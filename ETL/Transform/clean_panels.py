import uuid
from shapely.geometry import Point
import geopandas as gpd

def clean_panels(records):
    data = []

    for rec in records:
        try:
            coords = rec.get("coordonnees")
            if coords and isinstance(coords, list) and len(coords) == 2:
                data.append({
                    "id": str(uuid.uuid4()),  # Generate new UUID since API doesn't provide one
                    "location_desc": rec.get("localisation_des_panneaux_d_affichage"),
                    "precision": rec.get("precision"),
                    "format_1m2": rec.get("format_1m2", False),
                    "format_2m2": rec.get("format_2m2", False),
                    "geometry": Point(coords[1], coords[0])  # lon, lat
                })
        except Exception as e:
            print(f"Skipping record: {e}")

    if not data:
        raise ValueError("No valid records with geometry found.")

    gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    return gdf
