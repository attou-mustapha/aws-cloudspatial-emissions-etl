-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Schema for national pollutant reporting and plume detections
CREATE SCHEMA IF NOT EXISTS emissions;

-- Canadian National Pollutant Release Inventory (NPRI) emitters
CREATE TABLE IF NOT EXISTS emissions.npri_facilities (
    facility_id VARCHAR(50) PRIMARY KEY,
    facility_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    naics_code VARCHAR(10),
    province VARCHAR(10) NOT NULL,
    geom geometry(Point, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_npri_facilities_geom 
ON emissions.npri_facilities USING GIST (geom);

-- Satellite detected emission plumes
CREATE TABLE IF NOT EXISTS emissions.plume_detections (
    plume_id VARCHAR(64) PRIMARY KEY,
    detection_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    emission_rate_kg_h DOUBLE PRECISION,
    uncertainty_kg_h DOUBLE PRECISION,
    source_sensor VARCHAR(50) DEFAULT 'Sentinel-5P',
    geom geometry(Polygon, 4326) NOT NULL,
    correlated_facility_id VARCHAR(50) REFERENCES emissions.npri_facilities(facility_id)
);

CREATE INDEX IF NOT EXISTS idx_plume_detections_geom 
ON emissions.plume_detections USING GIST (geom);
