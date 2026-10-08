import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from shapely.geometry import shape, Point, Polygon, MultiPolygon
from shapely.validation import make_valid
import geopandas as gpd
from sqlalchemy import create_engine, text
from .config import config

logger = logging.getLogger(__name__)

class GeospatialCorrelationEngine:
    """Performs spatial validation and topological joins with NPRI industrial emitters."""

    def __init__(self):
        self.engine = create_engine(config.db_connection_url)

    def load_npri_facilities(self, geojson_path: Path | str) -> int:
        gdf = gpd.read_file(geojson_path)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)

        # Standardize columns
        records = []
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom.geom_type != "Point":
                geom = geom.centroid
            records.append({
                "facility_id": str(row["facility_id"]),
                "facility_name": str(row["facility_name"]),
                "company_name": str(row.get("company_name", "")),
                "naics_code": str(row.get("naics_code", "000000")),
                "province": str(row.get("province", "QC")),
                "geom_wkt": geom.wkt
            })

        with self.engine.begin() as conn:
            for rec in records:
                conn.execute(
                    text("""
                        INSERT INTO emissions.npri_facilities 
                        (facility_id, facility_name, company_name, naics_code, province, geom)
                        VALUES (:facility_id, :facility_name, :company_name, :naics_code, :province, ST_GeomFromText(:geom_wkt, 4326))
                        ON CONFLICT (facility_id) DO UPDATE SET
                            facility_name = EXCLUDED.facility_name,
                            geom = EXCLUDED.geom;
                    """),
                    rec
                )
        logger.info("Loaded %d facilities into emissions.npri_facilities", len(records))
        return len(records)

    def validate_and_clean_geometry(self, geom_dict: Dict[str, Any]) -> Polygon | MultiPolygon:
        geom = shape(geom_dict)
        if not geom.is_valid:
            logger.warning("Invalid geometry detected, applying topological repairs")
            geom = make_valid(geom)
        return geom

    def ingest_plume_observations(self, plumes_geojson: Path | str, max_distance_meters: float = 5000.0) -> List[Dict[str, Any]]:
        with open(plumes_geojson) as f:
            data = json.load(f)

        features = data.get("features", [])
        correlated_results = []

        with self.engine.begin() as conn:
            for feat in features:
                props = feat.get("properties", {})
                raw_geom = feat.get("geometry", {})
                cleaned_geom = self.validate_and_clean_geometry(raw_geom)
                wkt = cleaned_geom.wkt

                plume_id = props.get("plume_id", f"plume_{int(time.time() * 1000)}")
                rate = float(props.get("emission_rate_kg_h", 0.0))
                uncertainty = float(props.get("uncertainty_kg_h", 0.0))
                sensor = props.get("source_sensor", "Sentinel-5P")
                timestamp = props.get("detection_timestamp", "2026-10-01T12:00:00Z")

                # PostGIS spatial correlation: Find nearest NPRI facility within buffer threshold
                query = text("""
                    SELECT facility_id, facility_name,
                           ST_Distance(geom::geography, ST_GeomFromText(:wkt, 4326)::geography) AS distance_m
                    FROM emissions.npri_facilities
                    WHERE ST_DWithin(geom::geography, ST_GeomFromText(:wkt, 4326)::geography, :max_dist)
                    ORDER BY distance_m ASC
                    LIMIT 1;
                """)

                res = conn.execute(query, {"wkt": wkt, "max_dist": max_distance_meters}).fetchone()
                assigned_facility = res[0] if res else None
                dist_m = float(res[2]) if res else None

                conn.execute(
                    text("""
                        INSERT INTO emissions.plume_detections 
                        (plume_id, detection_timestamp, emission_rate_kg_h, uncertainty_kg_h, source_sensor, geom, correlated_facility_id)
                        VALUES (:plume_id, :ts, :rate, :unc, :sensor, ST_GeomFromText(:wkt, 4326), :facility_id)
                        ON CONFLICT (plume_id) DO UPDATE SET
                            emission_rate_kg_h = EXCLUDED.emission_rate_kg_h,
                            correlated_facility_id = EXCLUDED.correlated_facility_id;
                    """),
                    {
                        "plume_id": plume_id,
                        "ts": timestamp,
                        "rate": rate,
                        "unc": uncertainty,
                        "sensor": sensor,
                        "wkt": wkt,
                        "facility_id": assigned_facility
                    }
                )

                correlated_results.append({
                    "plume_id": plume_id,
                    "emission_rate_kg_h": rate,
                    "facility_id": assigned_facility,
                    "distance_meters": dist_m
                })

        return correlated_results
