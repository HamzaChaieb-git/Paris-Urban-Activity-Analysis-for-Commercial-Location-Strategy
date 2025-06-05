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
                'zone_name': record.get('Nom_de_la_zone', ''),
                'arrondissement': record.get('Arrondissement', ''),
                'date_partition_bovp': record.get('Date_parution_BOVP', ''),
            }
            zones_data.append(zone_data)
        
        transformed_data['pedestrian_zones'] = pd.DataFrame(zones_data)
        print(f"   ✅ Transformed {len(zones_data)} pedestrian zones")
    

    if 'bike_counters' in raw_data:
        print("🚴 Transforming bike counters...")
        counters_data = []
        for record in raw_data['bike_counters']:
            # Debug: print first record to see actual structure
            if len(counters_data) == 0:
                print(f"   🔍 Sample record keys: {list(record.keys())}")
            
            counter_data = {
                'counter_name': record.get('Nom_du_site_de_comptage', ''),
                'installation_date': record.get('Date_d_installation_du_site_de_comptage', ''),
                'count_datetime': record.get('Date_et_heure_de_comptage', ''),
                'hourly_count': record.get('Comptage_horaire', 0),
                'coordinates': record.get('Coordonnées_géographiques', {}),
                'month_year': record.get('mois_annee_comptage', ''),
            }
            counters_data.append(counter_data)
        
        df_counters = pd.DataFrame(counters_data)
        # Convert datetime columns
        if 'count_datetime' in df_counters.columns:
            df_counters['count_datetime'] = pd.to_datetime(df_counters['count_datetime'], errors='coerce')
        if 'installation_date' in df_counters.columns:
            df_counters['installation_date'] = pd.to_datetime(df_counters['installation_date'], errors='coerce')
        
        # If arrondissement is empty, try to extract from counter name or coordinates
        if df_counters['arrondissement'].isna().all() or (df_counters['arrondissement'] == '').all():
            df_counters['arrondissement'] = df_counters['counter_name'].str.extract(r'(\d{2})', expand=False)
        
        transformed_data['bike_counters'] = df_counters
        print(f"   ✅ Transformed {len(counters_data)} bike counter records")
    
  
    if 'advertising_panels' in raw_data:
        print("📢 Transforming advertising panels...")
        panels_data = []
        for record in raw_data['advertising_panels']:
            # Debug: print first record to see actual structure
            if len(panels_data) == 0:
                print(f"   🔍 Sample record keys: {list(record.keys())}")
            
            panel_data = {
                'location': record.get('Localisation_des_panneaux_d_affichage', ''),
                'precision': record.get('Précision', ''),
                'arrondissement': record.get('Arrondissement', ''),
                'format_1m2': record.get('Format_1m2', 0),
                'format_2m2': record.get('Format_2m2', 0),
                'coordinates': record.get('coordonnees', {}),
                'geometry': record.get('Coordonnées', {})
            }
            panels_data.append(panel_data)
        
        transformed_data['advertising_panels'] = pd.DataFrame(panels_data)
        print(f"   ✅ Transformed {len(panels_data)} advertising panels")
    
    print(f"\n🎉 TRANSFORMATION COMPLETE! Processed {len(transformed_data)} datasets")
    return transformed_data