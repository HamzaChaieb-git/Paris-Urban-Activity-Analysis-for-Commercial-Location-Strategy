import requests
import time
import json

def fetch_panels_data():
    """
    Fetch all panels data from Paris Open Data API
    Returns list of records
    """
    base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/panneaux_d_affichage_associatifs/records"
    all_results = []
    limit = 100
    offset = 0
    
    print(f"🌐 Fetching from: {base_url}")
    
    while True:
        try:
            params = {
                "limit": limit,
                "offset": offset
            }
            
            print(f"📡 Requesting {limit} records at offset {offset}...")
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Debug: print first response structure
            if offset == 0:
                print(f"🔍 API Response keys: {list(data.keys())}")
                if 'results' in data and data['results']:
                    print(f"🔍 First record keys: {list(data['results'][0].keys())}")
            
            if "results" not in data:
                print(f"❌ No 'results' field in response: {data}")
                break
                
            results = data["results"]
            if not results:
                print(f"✅ No more records to fetch")
                break

            all_results.extend(results)
            print(f"✅ Fetched {len(results)} records (total: {len(all_results)})")
            
            offset += limit
            
            # Be nice to the API
            time.sleep(0.1)
            
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout at offset {offset}, retrying...")
            time.sleep(1)
            continue
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data at offset {offset}: {e}")
            break
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

    print(f"🎉 Total records fetched: {len(all_results)}")
    
    # Debug: Save a sample for inspection
    if all_results:
        sample_file = "sample_response.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(all_results[0], f, indent=2, ensure_ascii=False)
        print(f"💾 Sample record saved to {sample_file}")
    
    return all_results