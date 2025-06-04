import requests
import time

def fetch_panels_data():
    base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/panneaux_d_affichage_associatifs/records"
    all_results = []
    limit = 100
    offset = 0

    while True:
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "select": "*"  # Explicitly request all fields
            }
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" not in data:
                print("Warning: No 'results' field in API response")
                print("Response:", data)
                break
                
            results = data["results"]
            if not results:
                break

            all_results.extend(results)
            offset += limit

            print(f"⬇️ Fetched {len(results)} records (offset={offset})")
            
            # Add a small delay to be nice to the API
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break

    print(f"✅ Total records fetched: {len(all_results)}")
    return all_results
