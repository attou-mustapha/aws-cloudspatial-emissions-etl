# AWS CloudSpatial Emissions ETL Pipeline

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostGIS 3.4](https://img.shields.io/badge/PostGIS-3.4-green.svg)](https://postgis.net/)
[![Apache Arrow / GeoParquet](https://img.shields.io/badge/Format-GeoParquet_1.0-orange.svg)](https://geoparquet.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A cloud-native geospatial data engineering pipeline designed to ingest satellite methane plume observations, perform topological validation, correlate plumes against the Canadian National Pollutant Release Inventory (NPRI) using PostGIS, and export analytical datasets to AWS S3 in GeoParquet format.

---

## 🏛 Architecture & Data Flow

```text
[ Satellite Observations ]          [ Canadian NPRI Registry ]
  (Sentinel-5P / GHGSat)             (Environment Canada Open Data)
          │                                     │
          ▼                                     ▼
   GeoJSON / NetCDF                      Point Geometry
          │                                     │
          └───────────────┬─────────────────────┘
                          ▼
            [ PostGIS Spatial Join Engine ]
           - Topological repairs (Shapely)
           - Geodetic distance: ST_DWithin (4326 geography)
           - GIST spatial indexing
                          │
                          ▼
            [ GeoParquet Columnar Exporter ]
           - Snappy compression
           - Native bounding box bbox metadata
                          │
                          ▼
             [ AWS S3 Object Storage ]
           - Partitioned by observation year/sensor
           - MinIO local testing emulator
```

---

## 🚀 Key Features

* **Cloud-Native Ingestion:** Interfacing with AWS S3 via `boto3` with automatic fallback to local S3-compatible endpoints (MinIO).
* **Strict Topology Validation:** Automatic detection and repair of non-simple, self-intersecting geometries using `shapely.validation.make_valid`.
* **Geodetic Spatial Joins:** High-precision distance queries on the WGS84 spheroid using PostGIS `geography` types (`ST_DWithin`, `ST_Distance`).
* **Modern Geospatial Analytics:** Columnar storage using **GeoParquet 1.0**, drastically reducing I/O and query overhead compared to legacy ESRI Shapefiles or CSVs.

---

## 🛠 Tech Stack

* **Language:** Python 3.11+
* **Geospatial Libraries:** Shapely, GeoPandas, PyArrow, GeoAlchemy2
* **Storage & Database:** PostgreSQL 16 + PostGIS 3.4, AWS S3 / MinIO
* **Testing:** Pytest, Moto (AWS mocking)
* **Packaging:** Docker, Docker Compose, PEP 621 (`pyproject.toml`)

---

## 📦 Getting Started

### 1. Start Infrastructure (PostGIS + MinIO)

```bash
docker compose up -d
```

### 2. Install Python Dependencies

```bash
pip install -e ".[dev]"
```

### 3. Run Pipeline via CLI

```bash
# Run complete pipeline: Load facilities, ingest plumes, correlate and export
emissions-etl run-all \
  --facilities data/sample_npri_facilities.geojson \
  --plumes data/sample_plumes.geojson \
  --output local_data/emissions_analytical.parquet \
  --upload-s3
```

---

## 🧪 Testing

Run test suite including geometry self-intersection repairs and mock S3 operations:

```bash
pytest -v
```

---

## 👨‍💻 Author & Competency Profile

**Mustapha ATTOU**  
Senior Software Engineer & Geospatial Specialist  
*Algiers, Algeria — Open to Relocation (Canada)*  
- GitHub: [@attou-mustapha](https://github.com/attou-mustapha)
- LinkedIn: [attou-mustapha](https://www.linkedin.com/in/attou-mustapha)
- Email: [attou.mustapha.pro@gmail.com](mailto:attou.mustapha.pro@gmail.com)
