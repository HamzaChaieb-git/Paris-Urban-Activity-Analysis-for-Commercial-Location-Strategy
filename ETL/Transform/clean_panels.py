import uuid
from shapely.geometry import Point
import geopandas as gpd
import json

def clean_panels(records):
    """
    Clean and transform panels data into GeoDataFrame
    """
    data = []
    skipped = 0
    
    print(f"🔧 Processing {len(records)} records...")
    
    for i, rec in enumerate(records):
        try:
            # Try different possible coordinate field names
            coords = None
            
            # Common field names for coordinates in Paris Open Data
            possible_coord_fields = [
                'coordonnees', 'coordinates', 'geo_point_2d', 
                'geometry', 'geom', 'location', 'position'
            ]
            
            for field in possible_coord_fields:
                if field in rec:
                    coords = rec[field]
                    if coords:
                        print(f"🎯 Found coordinates in field: {field}")
                        break
            
            # If no direct field, look in nested objects
            if not coords:
                for key, value in rec.items():
                    if isinstance(value, dict):
                        for coord_field in possible_coord_fields:
                            if coord_field in value:
                                coords = value[coord_field]
                                if coords:
                                    print(f"🎯 Found coordinates in nested field: {key}.{coord_field}")
                                    break
                        if coords:
                            break
            
            # Parse coordinates based on their format
            point = None
            if coords:
                if isinstance(coords, list) and len(coords) == 2:
                    # [lat, lon] or [lon, lat] format
                    try:
                        lat, lon = coords
                        point = Point(lon, lat)  # Point expects (lon, lat)
                    except:
                        lon, lat = coords
                        point = Point(lon, lat)
                        
                elif isinstance(coords, dict):
                    # GeoJSON-like format
                    if 'coordinates' in coords:
                        coord_list = coords['coordinates']
                        if isinstance(coord_list, list) and len(coord_list) == 2:
                            lon, lat = coord_list
                            point = Point(lon, lat)
                    elif 'lat' in coords and 'lon' in coords:
                        point = Point(coords['lon'], coords['lat'])
                        
                elif isinstance(coords, str):
                    # String format like "lat,lon"
                    try:
                        parts = coords.split(',')
                        if len(parts) == 2:
                            lat, lon = map(float, parts)
                            point = Point(lon, lat)
                    except:
                        pass
            
            if point:
                # Extract other fields
                row = {
                    "id": str(uuid.uuid4()),
                    "location_desc": rec.get("localisation_des_panneaux_d_affichage", ""),
                    "precision": rec.get("precision", ""),
                    "arrondissement": rec.get("arrondissement", ""),
                    "format_1m2": rec.get("format_1m2", False),
                    "format_2m2": rec.get("format_2m2", False),
                    "geometry": point
                }
                data.append(row)
            else:
                skipped += 1
                if i < 5:  # Show first few failures for debugging
                    print(f"Skipping record {i}: no valid coordinates found")
                    print(f"   Available fields: {list(rec.keys())}")
                
        except Exception as e:
            skipped += 1
            if i < 5:  # Show first few errors for debugging
                print(f"Error processing record {i}: {e}")

    print(f"Processed {len(data)} valid records")
    print(f"Skipped {skipped} records without valid geometry")
    
    if not data:
        print("No valid records found! Checking first record structure:")
        if records:
            print(json.dumps(records[0], indent=2, ensure_ascii=False))
        raise ValueError("No valid records with geometry found.")

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    print(f"🗺️ Created GeoDataFrame with {len(gdf)} records")
    
    return gdf