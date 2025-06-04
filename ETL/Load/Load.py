# Load/load.py

import os
import pandas as pd
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------
# Replace these with your own credentials (or use environment variables)
PG_USER     = os.getenv("PG_USER", "your_pg_username")
PG_PASS     = os.getenv("PG_PASS", "your_pg_password")
PG_HOST     = os.getenv("PG_HOST", "localhost")
PG_PORT     = os.getenv("PG_PORT", "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "your_database_name")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

# Create the SQLAlchemy engine & base
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------
# TABLE DEFINITIONS (SQLAlchemy Models)
# -----------------------------
# For each dataset, we define a model class corresponding to the
# columns we want in PostgreSQL. We’ll drop the table if it exists,
# then create a fresh one.

class Panels(Base):
    __tablename__ = "panels"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    recordid      = Column(String, nullable=True)
    arrondissement = Column(String, nullable=True)
    adresse       = Column(Text, nullable=True)
    format        = Column(String, nullable=True)
    gratuit       = Column(String, nullable=True)  # stored as string 'True'/'False'
    type_field    = Column("type", String, nullable=True)
    lat           = Column(Float, nullable=True)
    lon           = Column(Float, nullable=True)
    geo_shape     = Column(Geometry("POINT"), nullable=True)  # PostGIS point


class BikeCounters(Base):
    __tablename__ = "bike_counters"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    recordid        = Column(String, nullable=True)
    id_compteur     = Column(Integer, nullable=True)
    nom_compteur    = Column(String, nullable=True)
    id_site         = Column(Integer, nullable=True)
    nom_site        = Column(String, nullable=True)
    comptage        = Column(Integer, nullable=True)
    date            = Column(String, nullable=True)
    heure           = Column(String, nullable=True)
    date_install    = Column(String, nullable=True)
    photo_lien      = Column(String, nullable=True)
    lat             = Column(Float, nullable=True)
    lon             = Column(Float, nullable=True)
    geo_shape       = Column(Geometry("POINT"), nullable=True)


class Commerces(Base):
    __tablename__ = "commerces"
    id                 = Column(Integer, primary_key=True, autoincrement=True)
    recordid           = Column(String, nullable=True)
    nom_du_commerce    = Column(String, nullable=True)
    adresse            = Column(Text, nullable=True)
    type_de_distribution = Column(String, nullable=True)
    horaires           = Column(String, nullable=True)
    contact            = Column(String, nullable=True)
    lat                = Column(Float, nullable=True)
    lon                = Column(Float, nullable=True)
    geo_shape          = Column(Geometry("POINT"), nullable=True)


class Events(Base):
    __tablename__ = "events"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    recordid    = Column(String, nullable=True)
    title       = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    date_start  = Column(String, nullable=True)
    date_end    = Column(String, nullable=True)
    tags        = Column(JSON, nullable=True)      # JSON array of strings
    placename   = Column(String, nullable=True)
    address     = Column(Text, nullable=True)
    price       = Column(String, nullable=True)
    url         = Column(String, nullable=True)
    lat         = Column(Float, nullable=True)
    lon         = Column(Float, nullable=True)
    geo_shape   = Column(Geometry("POINT"), nullable=True)


class ZTI(Base):
    __tablename__ = "zti"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    recordid   = Column(String, nullable=True)
    nom_zone   = Column(String, nullable=True)
    type_zone  = Column(String, nullable=True)
    # zone_geom is expected to be a POLYGON or MULTIPOLYGON GeoJSON
    zone_geom  = Column(Geometry("POLYGON"), nullable=True)


# -----------------------------
# LOAD FUNCTION
# -----------------------------
def load_all_datasets(cleaned_data):
    """
    cleaned_data: dict mapping each key to a list of cleaned dicts.
    This function will:
      1) Drop any existing tables for panels, bike_counters, etc.
      2) Create new tables with the correct schema.
      3) Bulk-insert all rows using pandas.to_sql (or raw SQL for geometry).
    """
    # 1) Drop & recreate tables
    Base.metadata.drop_all(bind=engine)   # drop if exists
    Base.metadata.create_all(bind=engine) # create fresh tables

    session = SessionLocal()

    # 2) Insert data into each table
    # We’ll rely on pandas.to_sql for most columns, but we need to
    # separately load geometry fields via ST_GeomFromText or GeoAlchemy2.

    # 2a) PANELS
    if "panels" in cleaned_data:
        df_panels = pd.DataFrame(cleaned_data["panels"])
        # Rename “type” to “type_field” so column name doesn’t conflict
        if "type" in df_panels.columns:
            df_panels = df_panels.rename(columns={"type": "type_field"})

        # Temporarily drop the geometry column (we’ll insert it manually)
        geom_df = None
        if "geo_shape" in df_panels.columns:
            geom_df = df_panels[["geo_shape"]].copy()
            df_panels = df_panels.drop(columns=["geo_shape"])

        # Insert all non-geometry columns via to_sql
        df_panels.to_sql(
            name="panels",
            con=engine,
            if_exists="append",
            index=False,
            dtype={
                "recordid": String,
                "arrondissement": String,
                "adresse": Text,
                "format": String,
                "gratuit": String,
                "type_field": String,
                "lat": Float,
                "lon": Float
            }
        )

        # Now update each row’s geometry using ST_GeomFromGeoJSON
        if geom_df is not None and not geom_df.empty:
            # Use raw SQL to set geometry from GeoJSON
            for idx, json_geom in enumerate(geom_df["geo_shape"]):
                # The table has an auto-incremented “id” column starting at 1,
                # but to be safe, we’ll match on recordid if available:
                recid = df_panels.iloc[idx]["recordid"]
                if recid is not None:
                    # Build and execute an UPDATE query:
                    session.execute(
                        f"""
                        UPDATE panels
                        SET geo_shape = ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                        WHERE recordid = :rid
                        """,
                        {"geojson": json.dumps(json_geom), "rid": recid}
                    )
            session.commit()

        print(f"[Load] Inserted {len(df_panels)} rows into panels")

    # 2b) BIKE_COUNTERS
    if "bike_counters" in cleaned_data:
        df_bike = pd.DataFrame(cleaned_data["bike_counters"])
        # Drop the geo_shape column temporarily
        geom_df = None
        if "geo_shape" in df_bike.columns:
            geom_df = df_bike[["geo_shape"]].copy()
            df_bike = df_bike.drop(columns=["geo_shape"])

        df_bike.to_sql(
            name="bike_counters",
            con=engine,
            if_exists="append",
            index=False,
            dtype={
                "recordid": String,
                "id_compteur": Integer,
                "nom_compteur": String,
                "id_site": Integer,
                "nom_site": String,
                "comptage": Integer,
                "date": String,
                "heure": String,
                "date_install": String,
                "photo_lien": String,
                "lat": Float,
                "lon": Float
            }
        )

        if geom_df is not None and not geom_df.empty:
            for idx, json_geom in enumerate(geom_df["geo_shape"]):
                recid = df_bike.iloc[idx]["recordid"]
                if recid is not None:
                    session.execute(
                        f"""
                        UPDATE bike_counters
                        SET geo_shape = ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                        WHERE recordid = :rid
                        """,
                        {"geojson": json.dumps(json_geom), "rid": recid}
                    )
            session.commit()

        print(f"[Load] Inserted {len(df_bike)} rows into bike_counters")

    # 2c) COMMERCES
    if "commerces" in cleaned_data:
        df_com = pd.DataFrame(cleaned_data["commerces"])
        geom_df = None
        if "geo_shape" in df_com.columns:
            geom_df = df_com[["geo_shape"]].copy()
            df_com = df_com.drop(columns=["geo_shape"])

        df_com.to_sql(
            name="commerces",
            con=engine,
            if_exists="append",
            index=False,
            dtype={
                "recordid": String,
                "nom_du_commerce": String,
                "adresse": Text,
                "type_de_distribution": String,
                "horaires": String,
                "contact": String,
                "lat": Float,
                "lon": Float
            }
        )

        if geom_df is not None and not geom_df.empty:
            for idx, json_geom in enumerate(geom_df["geo_shape"]):
                recid = df_com.iloc[idx]["recordid"]
                if recid is not None:
                    session.execute(
                        f"""
                        UPDATE commerces
                        SET geo_shape = ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                        WHERE recordid = :rid
                        """,
                        {"geojson": json.dumps(json_geom), "rid": recid}
                    )
            session.commit()

        print(f"[Load] Inserted {len(df_com)} rows into commerces")

    # 2d) EVENTS
    if "events" in cleaned_data:
        df_evt = pd.DataFrame(cleaned_data["events"])
        geom_df = None
        if "geo_shape" in df_evt.columns:
            geom_df = df_evt[["geo_shape"]].copy()
            df_evt = df_evt.drop(columns=["geo_shape"])

        # Ensure 'tags' is JSON-string if it’s a Python list
        if "tags" in df_evt.columns:
            df_evt["tags"] = df_evt["tags"].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

        df_evt.to_sql(
            name="events",
            con=engine,
            if_exists="append",
            index=False,
            dtype={
                "recordid": String,
                "title": String,
                "description": Text,
                "date_start": String,
                "date_end": String,
                "tags": JSON,
                "placename": String,
                "address": Text,
                "price": String,
                "url": String,
                "lat": Float,
                "lon": Float
            }
        )

        if geom_df is not None and not geom_df.empty:
            for idx, json_geom in enumerate(geom_df["geo_shape"]):
                recid = df_evt.iloc[idx]["recordid"]
                if recid is not None:
                    session.execute(
                        f"""
                        UPDATE events
                        SET geo_shape = ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                        WHERE recordid = :rid
                        """,
                        {"geojson": json.dumps(json_geom), "rid": recid}
                    )
            session.commit()

        print(f"[Load] Inserted {len(df_evt)} rows into events")

    # 2e) ZTI
    if "zti" in cleaned_data:
        df_z = pd.DataFrame(cleaned_data["zti"])
        geom_df = None
        if "zone_geom" in df_z.columns:
            geom_df = df_z[["zone_geom"]].copy()
            df_z = df_z.drop(columns=["zone_geom"])

        df_z.to_sql(
            name="zti",
            con=engine,
            if_exists="append",
            index=False,
            dtype={
                "recordid": String,
                "nom_zone": String,
                "type_zone": String
            }
        )

        if geom_df is not None and not geom_df.empty:
            for idx, json_geom in enumerate(geom_df["zone_geom"]):
                recid = df_z.iloc[idx]["recordid"]
                if recid is not None:
                    session.execute(
                        f"""
                        UPDATE zti
                        SET zone_geom = ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                        WHERE recordid = :rid
                        """,
                        {"geojson": json.dumps(json_geom), "rid": recid}
                    )
            session.commit()

        print(f"[Load] Inserted {len(df_z)} rows into zti")

    session.close()
