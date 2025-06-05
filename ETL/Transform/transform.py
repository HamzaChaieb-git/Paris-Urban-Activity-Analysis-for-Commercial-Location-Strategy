import pandas as pd
from typing import List, Dict

def transform_paris_data(raw_data: Dict[str, List[Dict]]) -> Dict[str, pd.DataFrame]:
    """Transform raw data into clean DataFrames"""
    print("\n🔧 STARTING TRANSFORMATION...")
    
    if not raw_data:
        print("❌ No raw data to transform.")
        return {}
    
    transformed_data = {}
    
    # Transform Pedestrian Zones
    if 'pedestrian_zones' in raw_data:
        print("🚶 Transforming pedestrian zones...")
        zones_data = []
        for record in raw_data['pedestrian_zones']:
            zone_data = {
                'zone_name': record.get('nom', ''),
                'arrondissement': record.get('arrondissement', ''),
                'date_partition_bovp': record.get('paru_bovp', ''),
                'geo_shape': str(record.get('geo_shape', {})),
                'geo_point_2d': str(record.get('geo_point_2d', {}))
            }
            zones_data.append(zone_data)
        
        transformed_data['pedestrian_zones'] = pd.DataFrame(zones_data)
        print(f"   ✅ Transformed {len(zones_data)} pedestrian zones")
    
    # Transform Bike Counters - TRAFFIC PROXY DATA
    if 'bike_counters' in raw_data:
        print("🚴 Transforming bike counters...")
        print("   ⚠️  Note: API doesn't provide actual hourly counts (all 0)")
        print("   📊 Using counter density as traffic proxy")
        
        counters_data = []
        for record in raw_data['bike_counters']:
            counter_data = {
                'counter_name': record.get('nom_compteur', ''),
                'installation_date': record.get('installation_date', ''),
                'count_datetime': record.get('date', ''),
                'hourly_count': record.get('sum_counts', 0),  # Will be 0, but keep for structure
                'coordinates': str(record.get('coordinates', {})),
                'month_year': record.get('mois_annee_comptage', ''),
                'id_compteur': record.get('id_compteur', ''),
                'counter': record.get('counter', ''),
                'name': record.get('name', ''),
                'id': record.get('id', '')
            }
            counters_data.append(counter_data)
        
        df_counters = pd.DataFrame(counters_data)
        
        if 'count_datetime' in df_counters.columns:
            df_counters['count_datetime'] = pd.to_datetime(df_counters['count_datetime'], errors='coerce')
        if 'installation_date' in df_counters.columns:
            df_counters['installation_date'] = pd.to_datetime(df_counters['installation_date'], errors='coerce')
        
        df_counters['arrondissement'] = df_counters['counter_name'].str.extract(r'(\d{2})', expand=False)
        
        transformed_data['bike_counters'] = df_counters
        print(f"   ✅ Transformed {len(counters_data)} bike counter records")
    
    # Transform Advertising Panels
    if 'advertising_panels' in raw_data:
        print("📢 Transforming advertising panels...")
        panels_data = []
        for record in raw_data['advertising_panels']:
            panel_data = {
                'location': record.get('localisation_des_panneaux_d_affichage', ''),
                'precision': record.get('precision', ''),
                'arrondissement': record.get('r', ''),
                'format_1m2': record.get('format_1m2', 0),
                'format_2m2': record.get('format_2m2', 0),
                'coordinates': str(record.get('coordonnees', {})),
                'geometry': str(record.get('coordonnees', {}))
            }
            panels_data.append(panel_data)
        
        transformed_data['advertising_panels'] = pd.DataFrame(panels_data)
        print(f"   ✅ Transformed {len(panels_data)} advertising panels")
    
    print(f"\n🎉 TRANSFORMATION COMPLETE! Processed {len(transformed_data)} datasets")
    print("📊 Ready for marketing analysis using counter density as traffic proxy")
    return transformed_data