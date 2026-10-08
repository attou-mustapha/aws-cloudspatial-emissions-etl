from emissions_pipeline.spatial_engine import GeospatialCorrelationEngine

def test_invalid_bowtie_polygon_repair():
    engine = GeospatialCorrelationEngine.__new__(GeospatialCorrelationEngine)
    # Self-intersecting 'bowtie' polygon
    invalid_bowtie = {
        "type": "Polygon",
        "coordinates": [
            [[0, 0], [0, 2], [2, 0], [2, 2], [0, 0]]
        ]
    }
    cleaned = engine.validate_and_clean_geometry(invalid_bowtie)
    assert cleaned.is_valid
    assert cleaned.geom_type in ["MultiPolygon", "GeometryCollection"]
