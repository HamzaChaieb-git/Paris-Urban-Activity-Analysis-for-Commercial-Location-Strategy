import pandas as pd
from typing import List, Dict

def transform_paris_data(raw_data: Dict[str, List[Dict]]) -> Dict[str, pd.DataFrame]:
    """
    Take raw JSON records from the Paris API and turn them into
    cleaned pandas DataFrames keyed by:
      - pedestrian_zones
      - vehicle_counters
      - associative_panels
    """
    print("\n🔧 STARTING TRANSFORMATION...")
    if not raw_data:
        print("❌ No raw data to transform.")
        return {}

    transformed_data: Dict[str, pd.DataFrame] = {}

    # 1) Pedestrian Zones (split out lon/lat)
    if 'pedestrian_zones' in raw_data:
        print("🚶 Transforming pedestrian zones...")
        zones = []
        for record in raw_data['pedestrian_zones']:
            # if your extractor wrapped fields in record['fields'], switch to:
            # fields = record.get('fields', {})
            # pt = fields.get('geo_point_2d') or {}
            pt = record.get('geo_point_2d') or {}
            zones.append({
                'zone_name':           record.get('nom', ''),
                'arrondissement':      record.get('arrondissement', ''),
                'date_partition_bovp': record.get('paru_bovp', ''),
                'longitude':           pt.get('lon'),
                'latitude':            pt.get('lat'),
                'geo_shape':           str(record.get('geo_shape', {}))
            })
        transformed_data['pedestrian_zones'] = pd.DataFrame(zones)
        print(f"   ✅ Transformed {len(zones)} pedestrian zones")

    # 2) Vehicle Counters
    vc_key = 'vehicule_counters'
    if vc_key in raw_data:
        print("🚗 Transforming vehicle counters...")
        rows = []
        for record in raw_data[vc_key]:
            coord = record.get('coordonnees_geo') or {}
            rows.append({
                'trajectory_id': record.get('id_trajectoire', ''),
                'site_id':       record.get('id_site', ''),
                'site_label':    record.get('label', ''),
                'mode':          record.get('mode', ''),
                'count':         record.get('nb_usagers', 0),
                'direction':     record.get('sens', ''),
                'lane':          record.get('voie', ''),
                'timestamp':     pd.to_datetime(record.get('t', None)),
                'longitude':     coord.get('lon'),
                'latitude':      coord.get('lat'),
            })
        transformed_data['vehicle_counters'] = pd.DataFrame(rows)
        print(f"   ✅ Transformed {len(rows)} vehicle counter records")

    # 3) Associative Panels
    if 'associative_panels' in raw_data:
        print("📢 Transforming associative panels...")
        panels = []
        for record in raw_data['associative_panels']:
            coords = record.get('coordonnees') or {}
            panels.append({
                'location':       record.get('localisation_des_panneaux_d_affichage', ''),
                'precision':      record.get('precision', ''),
                'arrondissement': record.get('r', ''),
                'format_1m2':     record.get('format_1m2', 0),
                'format_2m2':     record.get('format_2m2', 0),
                'longitude':      coords.get('lon'),
                'latitude':       coords.get('lat'),
            })
        transformed_data['associative_panels'] = pd.DataFrame(panels)
        print(f"   ✅ Transformed {len(panels)} associative panels")

    print(f"\n🎉 TRANSFORMATION COMPLETE! Processed {len(transformed_data)} datasets")
    return transformed_data
