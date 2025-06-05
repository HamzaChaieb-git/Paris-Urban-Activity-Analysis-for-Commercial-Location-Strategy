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
                'zone_name': record.get('nom_de_la_zone', ''),
                'arrondissement': record.get('arrondissement', ''),
                'date_partition_bovp': record.get('date_partition_bovp', ''),
                'geometry': record.get('geometry', {})
            }
            zones_data.append(zone_data)
        
        transformed_data['pedestrian_zones'] = pd.DataFrame(zones_data)
        print(f"   ✅ Transformed {len(zones_data)} pedestrian zones")
    
    # Transform Bike Counters
    if 'bike_counters' in raw_data:
        print("🚴 Transforming bike counters...")
        counters_data = []
        for record in raw_data['bike_counters']:
            counter_data = {
                'counter_name': record.get('nom_du_site_de_comptage', ''),
                'installation_date': record.get('date_d_installation_du_site_de_comptage', ''),
                'count_datetime': record.get('date_et_heure_de_comptage', ''),
                'hourly_count': record.get('comptage_horaire', 0),
                'coordinates': record.get('coordonnees_geographiques', {}),
                'month_year': record.get('mois_annee_comptage', '')
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
    
    # Transform Advertising Panels
    if 'advertising_panels' in raw_data:
        print("📢 Transforming advertising panels...")
        panels_data = []
        for record in raw_data['advertising_panels']:
            panel_data = {
                'location': record.get('localisation_des_panneaux_d_affichage', ''),
                'precision': record.get('precision', ''),
                'arrondissement': record.get('arrondissement', ''),
                'format_1m2': record.get('format_1m2', 0),
                'format_2m2': record.get('format_2m2', 0),
                'coordinates': record.get('coordonnees', {}),
                'geometry': record.get('geometry', {})
            }
            panels_data.append(panel_data)
        
        transformed_data['advertising_panels'] = pd.DataFrame(panels_data)
        print(f"   ✅ Transformed {len(panels_data)} advertising panels")
    
    print(f"\n🎉 TRANSFORMATION COMPLETE! Processed {len(transformed_data)} datasets")
    return transformed_data