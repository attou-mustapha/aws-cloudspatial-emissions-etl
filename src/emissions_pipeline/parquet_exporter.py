import logging
from pathlib import Path
import geopandas as gpd
from sqlalchemy import create_engine
from .config import config

logger = logging.getLogger(__name__)

class GeoParquetAnalyticalExporter:
    """Extracts correlated observations and exports to columnar GeoParquet for analytics."""

    def __init__(self):
        self.engine = create_engine(config.db_connection_url)

    def export_dataset(self, output_filepath: Path | str) -> Path:
        output_path = Path(output_filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        query = """
            SELECT 
                p.plume_id,
                p.detection_timestamp,
                p.emission_rate_kg_h,
                p.uncertainty_kg_h,
                p.source_sensor,
                p.correlated_facility_id,
                f.facility_name,
                f.company_name,
                f.province,
                p.geom
            FROM emissions.plume_detections p
            LEFT JOIN emissions.npri_facilities f ON p.correlated_facility_id = f.facility_id
        """

        gdf = gpd.read_postgis(query, self.engine, geom_col="geom", crs="EPSG:4326")
        
        # Write to Apache Parquet with native GeoParquet metadata specification
        gdf.to_parquet(output_path, compression="snappy", schema_version="1.0.0")
        logger.info("Successfully exported %d records to %s", len(gdf), output_path)
        return output_path
