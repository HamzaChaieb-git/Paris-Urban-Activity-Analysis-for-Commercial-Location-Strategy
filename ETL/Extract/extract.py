# Extract/extract.py

import requests
from requests.exceptions import HTTPError

def extract_all_datasets():
    """
    Fetch every record for each of the five Paris Data datasets by paginating
    100 records at a time. Stop when the API returns an empty batch or HTTP 400.
    """
    datasets = {
        "panels":        "panneaux_d_affichage_associatifs",
        "bike_counters": "comptage-velo-donnees-compteurs",
        "commerces":     "commerces-eau-de-paris",
        "events":        "que-faire-a-paris-",
        "zti":           "zones-touristiques-internationales"
    }

    base_url = "https://opendata.paris.fr/api/records/1.0/search/"
    all_data = {}

    for key, dataset in datasets.items():
        print(f"[Extract] Starting '{key}'")
        records = []
        offset = 0
        limit = 100

        while True:
            params = {
                "dataset": dataset,
                "rows": limit,
                "start": offset
            }
            try:
                resp = requests.get(base_url, params=params)
                resp.raise_for_status()
            except HTTPError:
                # If offset is beyond what the API allows, stop paging
                print(f"[Extract] HTTP 400 at offset={offset} for '{key}', stopping pagination.")
                break

            batch = resp.json().get("records", [])
            if not batch:
                # No more data left
                break

            records.extend(batch)
            offset += limit

        print(f"[Extract] Retrieved {len(records)} records for '{key}'")
        all_data[key] = records

    return all_data


if __name__ == "__main__":
    data = extract_all_datasets()
    for k, v in data.items():
        print(f"{k}: {len(v)} records")
