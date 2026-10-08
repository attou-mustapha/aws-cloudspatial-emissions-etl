import click
from pathlib import Path
from .spatial_engine import GeospatialCorrelationEngine
from .parquet_exporter import GeoParquetAnalyticalExporter
from .s3_client import S3StorageManager
from .config import config

@click.group()
def main():
    """Cloud-native geospatial emissions processing pipeline."""
    pass

@main.command()
@click.option("--facilities", default="data/sample_npri_facilities.geojson", help="Path to NPRI facilities GeoJSON")
@click.option("--plumes", default="data/sample_plumes.geojson", help="Path to plume detections GeoJSON")
@click.option("--output", default="local_data/emissions_analytical.parquet", help="Output GeoParquet file")
@click.option("--upload-s3/--no-upload-s3", default=False, help="Upload output to S3 bucket")
def run_all(facilities, plumes, output, upload_s3):
    """Run full end-to-end ingestion, spatial join, and parquet export."""
    click.echo("[1/4] Loading NPRI Industrial Facilities into PostGIS...")
    engine = GeospatialCorrelationEngine()
    loaded_fac = engine.load_npri_facilities(facilities)
    click.echo(f"  ✓ {loaded_fac} facilities loaded.")

    click.echo("[2/4] Processing plume detections & topological correlation...")
    results = engine.ingest_plume_observations(plumes)
    click.echo(f"  ✓ {len(results)} plumes processed.")

    click.echo("[3/4] Exporting analytical dataset to GeoParquet...")
    exporter = GeoParquetAnalyticalExporter()
    out_file = exporter.export_dataset(output)
    click.echo(f"  ✓ GeoParquet exported: {out_file}")

    if upload_s3:
        click.echo("[4/4] Syncing to S3...")
        s3 = S3StorageManager()
        s3_url = s3.upload_file(out_file, config.s3_bucket_processed, f"year=2026/{Path(out_file).name}")
        click.echo(f"  ✓ Object stored at: {s3_url}")

    click.echo("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
