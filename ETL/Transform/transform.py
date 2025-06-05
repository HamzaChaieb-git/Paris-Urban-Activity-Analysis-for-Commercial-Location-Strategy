import pandas as pd
from typing import List, Dict

def transform_paris_data(raw_data: Dict[str, List[Dict]]) -> Dict[str, pd.DataFrame]:
    """Transform raw data into clean DataFrames"""
    print("\n🔧 STARTING TRANSFORMATION...")
    
    if not raw_data:
        print("❌ No raw data to transform.")
        return {}
    
    transformed_data = {}
    
    # Transform Pedestrian Zones - CORRECTED API FIELD NAMES
    if 'pedestrian_zones' in raw_data:
        print("🚶 Transforming pedestrian zones...")
        zones_data = []
        for record in raw_data['pedestrian_zones']:
            zone_data = {
                'zone_name': record.get('nom', ''),                    # FIXED: API uses 'nom'
                'arrondissement': record.get('arrondissement', ''),    # CORRECT
                'date_partition_bovp': record.get('paru_bovp', ''),    # FIXED: API uses 'paru_bovp'
                'geo_shape': record.get('geo_shape', {}),              # Additional field
                'geo_point_2d': record.get('geo_point_2d', {})         # Additional field
            }
            zones_data.append(zone_data)
        
        transformed_data['pedestrian_zones'] = pd.DataFrame(zones_data)
        print(f"   ✅ Transformed {len(zones_data)} pedestrian zones")
    
    # Transform Bike Counters - CORRECTED HOURLY_COUNT FIELD
    if 'bike_counters' in raw_data:
        print("🚴 Transforming bike counters...")
        counters_data = []
        for record in raw_data['bike_counters']:
            counter_data = {
                'counter_name': record.get('nom_compteur', ''),
                'installation_date': record.get('installation_date', ''),
                'count_datetime': record.get('date', ''),
                'hourly_count': record.get('sum_counts', 0),           # FIXED: API uses 'sum_counts'
                'coordinates': record.get('coordinates', {}),
                'month_year': record.get('mois_annee_comptage', ''),
                'id_compteur': record.get('id_compteur', ''),
                'counter': record.get('counter', ''),
                'name': record.get('name', ''),
                'id': record.get('id', '')
            }
            counters_data.append(counter_data)
        
        df_counters = pd.DataFrame(counters_data)
        
        # Convert datetime columns
        if 'count_datetime' in df_counters.columns:
            df_counters['count_datetime'] = pd.to_datetime(df_counters['count_datetime'], errors='coerce')
        if 'installation_date' in df_counters.columns:
            df_counters['installation_date'] = pd.to_datetime(df_counters['installation_date'], errors='coerce')
        
        # Extract arrondissement from counter name
        df_counters['arrondissement'] = df_counters['counter_name'].str.extract(r'(\d{2})', expand=False)
        
        transformed_data['bike_counters'] = df_counters
        print(f"   ✅ Transformed {len(counters_data)} bike counter records")
    
    # Transform Advertising Panels - CORRECTED API FIELD NAMES
    if 'advertising_panels' in raw_data:
        print("📢 Transforming advertising panels...")
        panels_data = []
        for record in raw_data['advertising_panels']:
            panel_data = {
                'location': record.get('localisation_des_panneaux_d_affichage', ''),  # CORRECT
                'precision': record.get('precision', ''),                             # CORRECT
                'arrondissement': record.get('r', ''),                                # FIXED: API uses 'r'
                'format_1m2': record.get('format_1m2', 0),                           # CORRECT
                'format_2m2': record.get('format_2m2', 0),                           # CORRECT
                'coordinates': record.get('coordonnees', {}),                        # CORRECT
                'geometry': record.get('coordonnees', {})                            # SAME AS coordinates
            }
            panels_data.append(panel_data)
        
        transformed_data['advertising_panels'] = pd.DataFrame(panels_data)
        print(f"   ✅ Transformed {len(panels_data)} advertising panels")
    
    print(f"\n🎉 TRANSFORMATION COMPLETE! Processed {len(transformed_data)} datasets")
    return transformed_data