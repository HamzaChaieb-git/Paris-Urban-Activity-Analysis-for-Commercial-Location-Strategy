from Extract.fetch_panels import fetch_panels_data
from Transform.clean_panels import clean_panels
from Load.load_panels import load_panels

if __name__ == "__main__":
    print("Extracting panels...")
    raw = fetch_panels_data()
    

    print("Transforming panels...")
    gdf = clean_panels(raw)

    print("Loading panels into PostGIS...")
    load_panels(gdf)
