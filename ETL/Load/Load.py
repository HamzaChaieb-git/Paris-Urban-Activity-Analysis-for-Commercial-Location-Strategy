# Load/load.py

import os
import pandas as pd
import json
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID

# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------
# Match your docker-compose.yml settings
PG_USER     = os.getenv("PG_USER", "postgres")
PG_PASS     = os.getenv("PG_PASS", "1234")
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "city_marketing")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# Create the SQLAlchemy engine & base
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------
# TABLE DEFINITIONS - Match init.sql schema
# -----------------------------

class Panels(Base):
    __tablename__ = "panels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=True)
    installation_date = Column(DateTime, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    
    # Additional fields from the API data
    recordid = Column(String, nullable=True)
    arrondissement = Column(String, nullable=True)
    adresse = Column(Text, nullable=True)
    format = Column(String, nullable=True)
    gratuit = Column(String, nullable=True)


class BikeCounters(Base):
    __tablename__ = "bike_counts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counter_name = Column(String, nullable=True)
    date_time = Column(DateTime, nullable=True)
    count = Column(Integer, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    
    # Additional fields from API - adjusted data types based on actual data
    recordid = Column(String, nullable=True)
    id_compteur = Column(String, nullable=True)  # Changed to String (contains dashes)
    id_site = Column(String, nullable=True)      # Changed to String to be safe
    nom_site = Column(String, nullable=True)
    date_install = Column(String, nullable=True)
    photo_lien = Column(String, nullable=True)


class Commerces(Base):
    __tablename__ = "commerces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    
    # Additional fields from API
    recordid = Column(String, nullable=True)
    horaires = Column(String, nullable=True)
    contact = Column(String, nullable=True)


class Events(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=True)
    
    # Additional fields from API
    recordid = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # Store as JSON string
    placename = Column(String, nullable=True)
    price = Column(String, nullable=True)
    url = Column(String, nullable=True)


class ZTIZones(Base):
    __tablename__ = "zti_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    geom = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    
    # Additional fields from API
    recordid = Column(String, nullable=True)
    type_zone = Column(String, nullable=True)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def parse_date_string(date_str):
    """Parse various date formats from the API"""
    if not date_str:
        return None
    
    # Common formats in Paris Open Data
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    
    print(f"Warning: Could not parse date '{date_str}'")
    return None


def create_point_from_coords(lat, lon):
    """Create a PostGIS POINT from lat/lon coordinates"""
    if lat is None or lon is None:
        return None
    return f"POINT({lon} {lat})"


def create_geometry_from_geojson(geojson_obj):
    """Convert GeoJSON to WKT for PostGIS"""
    if not geojson_obj:
        return None
    
    try:
        if geojson_obj.get("type") == "Point":
            coords = geojson_obj["coordinates"]
            return f"POINT({coords[0]} {coords[1]})"
        elif geojson_obj.get("type") == "Polygon":
            coords = geojson_obj["coordinates"][0]  # First ring
            coord_pairs = [f"{c[0]} {c[1]}" for c in coords]
            return f"POLYGON(({', '.join(coord_pairs)}))"
        elif geojson_obj.get("type") == "MultiPolygon":
            polygons = []
            for poly in geojson_obj["coordinates"]:
                coords = poly[0]  # First ring of each polygon
                coord_pairs = [f"{c[0]} {c[1]}" for c in coords]
                polygons.append(f"(({', '.join(coord_pairs)}))")
            return f"MULTIPOLYGON({', '.join(polygons)})"
    except (KeyError, IndexError, TypeError) as e:
        print(f"Warning: Could not convert GeoJSON to WKT: {e}")
        return None


def safe_int_convert(value):
    """Safely convert a value to integer, return None if conversion fails"""
    if value is None:
        return None
    try:
        # Handle string values that might be numeric
        if isinstance(value, str):
            # Remove any non-numeric characters except decimal point
            clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
            if clean_value:
                return int(float(clean_value))
        return int(value)
    except (ValueError, TypeError):
        return None


def debug_sample_data(data_dict, dataset_name, sample_size=3):
    """Print sample data for debugging"""
    if dataset_name in data_dict and data_dict[dataset_name]:
        print(f"\n[DEBUG] Sample {dataset_name} data:")
        for i, record in enumerate(data_dict[dataset_name][:sample_size]):
            print(f"  Record {i}: {record}")
        print(f"  Total records: {len(data_dict[dataset_name])}")
    else:
        print(f"\n[DEBUG] No data found for {dataset_name}")


# -----------------------------
# LOAD FUNCTION
# -----------------------------

def load_all_datasets(cleaned_data):
    """
    Load cleaned data into PostgreSQL tables matching init.sql schema
    """
    
    # Debug: Print sample data to see what we're working with
    for dataset in ["panels", "bike_counters", "commerces", "events", "zti"]:
        debug_sample_data(cleaned_data, dataset)
    
    # Recreate tables to ensure clean state
    print("\n[Load] Dropping and recreating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        # Load Panels
        if "panels" in cleaned_data and cleaned_data["panels"]:
            print(f"\n[Load] Loading {len(cleaned_data['panels'])} panels...")
            
            for i, record in enumerate(cleaned_data["panels"]):
                if i == 0:  # Debug first record
                    print(f"[DEBUG] First panel record: {record}")
                
                panel = Panels(
                    recordid=record.get("recordid"),
                    type=record.get("type"),
                    installation_date=parse_date_string(record.get("date_install")),
                    arrondissement=record.get("arrondissement"),
                    adresse=record.get("adresse"),
                    format=record.get("format"),
                    gratuit=record.get("gratuit")
                )
                
                # Handle geometry
                if record.get("geo_shape"):
                    wkt = create_geometry_from_geojson(record["geo_shape"])
                    if wkt:
                        panel.geom = f"SRID=4326;{wkt}"
                elif record.get("lat") and record.get("lon"):
                    wkt = create_point_from_coords(record["lat"], record["lon"])
                    if wkt:
                        panel.geom = f"SRID=4326;{wkt}"
                
                session.add(panel)
            
            session.commit()
            print(f"[Load] ✅ Loaded {len(cleaned_data['panels'])} panels")

        # Load Bike Counters
        if "bike_counters" in cleaned_data and cleaned_data["bike_counters"]:
            print(f"\n[Load] Loading {len(cleaned_data['bike_counters'])} bike counter records...")
            
            loaded_count = 0
            for i, record in enumerate(cleaned_data["bike_counters"]):
                if i == 0:  # Debug first record
                    print(f"[DEBUG] First bike counter record: {record}")
                
                # Combine date and hour for datetime
                date_time = None
                if record.get("date") and record.get("heure"):
                    try:
                        date_time = datetime.strptime(f"{record['date']} {record['heure']}", "%Y-%m-%d %H:%M:%S")
                    except:
                        date_time = parse_date_string(record.get("date"))
                
                bike_count = BikeCounters(
                    recordid=record.get("recordid"),
                    counter_name=record.get("nom_compteur"),
                    date_time=date_time,
                    count=safe_int_convert(record.get("comptage")),
                    id_compteur=str(record.get("id_compteur")) if record.get("id_compteur") else None,
                    id_site=str(record.get("id_site")) if record.get("id_site") else None,
                    nom_site=record.get("nom_site"),
                    date_install=record.get("date_install"),
                    photo_lien=record.get("photo_lien")
                )
                
                # Handle geometry
                if record.get("geo_shape"):
                    wkt = create_geometry_from_geojson(record["geo_shape"])
                    if wkt:
                        bike_count.geom = f"SRID=4326;{wkt}"
                elif record.get("lat") and record.get("lon"):
                    wkt = create_point_from_coords(record["lat"], record["lon"])
                    if wkt:
                        bike_count.geom = f"SRID=4326;{wkt}"
                
                session.add(bike_count)
                loaded_count += 1
                
                # Commit in batches to avoid memory issues
                if loaded_count % 1000 == 0:
                    session.commit()
                    print(f"[Load] ✅ Committed batch: {loaded_count} bike counter records")
            
            session.commit()
            print(f"[Load] ✅ Loaded {loaded_count} bike counter records")

        # Load Commerces
        if "commerces" in cleaned_data:
            print(f"[Load] Loading {len(cleaned_data['commerces'])} commerces...")
            
            for record in cleaned_data["commerces"]:
                commerce = Commerces(
                    recordid=record.get("recordid"),
                    name=record.get("nom_du_commerce"),
                    activity=record.get("type_de_distribution"),
                    address=record.get("adresse"),
                    horaires=record.get("horaires"),
                    contact=record.get("contact")
                )
                
                # Handle geometry
                if record.get("geo_shape"):
                    wkt = create_geometry_from_geojson(record["geo_shape"])
                    if wkt:
                        commerce.geom = f"SRID=4326;{wkt}"
                elif record.get("lat") and record.get("lon"):
                    wkt = create_point_from_coords(record["lat"], record["lon"])
                    if wkt:
                        commerce.geom = f"SRID=4326;{wkt}"
                
                session.add(commerce)
            
            session.commit()
            print(f"[Load] ✅ Loaded {len(cleaned_data['commerces'])} commerces")

        # Load Events
        if "events" in cleaned_data:
            print(f"[Load] Loading {len(cleaned_data['events'])} events...")
            
            for record in cleaned_data["events"]:
                event = Events(
                    recordid=record.get("recordid"),
                    title=record.get("title"),
                    description=record.get("description"),
                    start_time=parse_date_string(record.get("date_start")),
                    end_time=parse_date_string(record.get("date_end")),
                    tags=json.dumps(record.get("tags")) if record.get("tags") else None,
                    placename=record.get("placename"),
                    price=record.get("price"),
                    url=record.get("url")
                )
                
                # Handle geometry
                if record.get("lat") and record.get("lon"):
                    wkt = create_point_from_coords(record["lat"], record["lon"])
                    if wkt:
                        event.geom = f"SRID=4326;{wkt}"
                
                session.add(event)
            
            session.commit()
            print(f"[Load] ✅ Loaded {len(cleaned_data['events'])} events")

        # Load ZTI Zones
        if "zti" in cleaned_data:
            print(f"[Load] Loading {len(cleaned_data['zti'])} ZTI zones...")
            
            for record in cleaned_data["zti"]:
                zti_zone = ZTIZones(
                    recordid=record.get("recordid"),
                    name=record.get("nom_zone"),
                    type_zone=record.get("type_zone")
                )
                
                # Handle geometry
                if record.get("zone_geom"):
                    wkt = create_geometry_from_geojson(record["zone_geom"])
                    if wkt:
                        zti_zone.geom = f"SRID=4326;{wkt}"
                
                session.add(zti_zone)
            
            session.commit()
            print(f"[Load] ✅ Loaded {len(cleaned_data['zti'])} ZTI zones")

        print("\n🎉 All data loaded successfully into PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # Test database connection
    try:
        connection = engine.connect()
        result = connection.execute("SELECT version();")
        print(f"✅ Connected to PostgreSQL: {result.fetchone()[0]}")
        connection.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")