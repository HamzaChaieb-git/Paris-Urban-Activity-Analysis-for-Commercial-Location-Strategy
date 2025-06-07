import requests
import time
from typing import List, Dict

def extract_paris_data() -> Dict[str, List[Dict]]:
    """Extract data from Paris Open Data API with pagination (API limits: 100 per fetch, 10k total)"""
    print("🔍 STARTING EXTRACTION...")
    print("⚠️  API Limits: 100 records per fetch, 10,000 records max per dataset")
    
    base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets"
    datasets = {
        'pedestrian_zones': 'aires-pietonnes',
        'vehicule_counters': 'comptage-multimodal-comptages', 
        'associative_panels': 'panneaux_d_affichage_associatifs'
    }
    limit = 100  
    max_total_records = 10000 
    raw_data = {}
    
    for dataset_key, dataset_name in datasets.items():
        print(f"\n📊 Extracting {dataset_key} ({dataset_name})...")
        
        all_records = []
        offset = 0
        total_count = None
        
        while len(all_records) < max_total_records:
            url = f"{base_url}/{dataset_name}/records"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if total_count is None:
                    total_count = data.get('total_count', 0)
                    actual_max = min(total_count, max_total_records)
                    print(f"   Dataset has {total_count} records (extracting max {actual_max})")
                
                records = data.get('results', [])
                if not records:
                    print(f"   No more records available at offset {offset}")
                    break
                    
                all_records.extend(records)
                offset += limit
                
                # Show progress with API limits
                current_count = len(all_records)
                target_count = min(total_count or max_total_records, max_total_records)
                print(f"   Progress: {current_count}/{target_count} records (API limit: {max_total_records})")
                
                # Stop if we hit API total limit
                if len(all_records) >= max_total_records:
                    print(f"   ⚠️  Reached API limit of {max_total_records} records")
                    break
                
                # Stop if we've got all available records
                if total_count and len(all_records) >= total_count:
                    print(f"   ✅ Extracted all available records")
                    break
                    
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Error fetching {dataset_key}: {e}")
                break
        
        raw_data[dataset_key] = all_records
        final_count = len(all_records)
        
        if final_count >= max_total_records:
            print(f"   ⚠️  Extracted {final_count} records (hit API limit)")
        else:
            print(f"   ✅ Extracted {final_count} records for {dataset_key}")
        
    print(f"\n🎉 EXTRACTION COMPLETE! Total datasets: {len(raw_data)}")
    total_extracted = sum(len(records) for records in raw_data.values())
    print(f"📊 Total records extracted: {total_extracted}")
    return raw_data