from sqlalchemy import create_engine, text

def ensure_panels_table_exists(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE EXTENSION IF NOT EXISTS postgis;

            CREATE TABLE IF NOT EXISTS panels (
                id UUID PRIMARY KEY,
                location_desc TEXT,
                precision TEXT,
                arrondissement TEXT,
                format_1m2 BOOLEAN,
                format_2m2 BOOLEAN,
                geom GEOMETRY(Point, 4326)
            );
        """))
        print("Ensured 'panels' table exists.")

def load_panels(gdf):
    engine = create_engine("postgresql://postgres:1234@localhost:5432/city_marketing")
    ensure_panels_table_exists(engine)
    gdf.to_postgis("panels", con=engine, if_exists="append", index=False)
    print("Panels data loaded into PostGIS.")
