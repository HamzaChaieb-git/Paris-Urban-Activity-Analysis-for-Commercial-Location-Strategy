# Extract/extract.py

import requests

def extract_all_datasets():
    """
    Récupère tous les enregistrements pour chacun des 5 jeux de données Paris Data,
    en paginant par 100 enregistrements max par requête, sans générer d'erreur 400.
    """
    datasets = {
        "panels": "panneaux_d_affichage_associatifs",
        "bike_counters": "comptage-velo-donnees-compteurs",
        "commerces": "commerces-eau-de-paris",
        "events": "que-faire-a-paris-",
        "zti": "zones-touristiques-internationales"
    }

    all_data = {}
    base_url = "https://opendata.paris.fr/api/records/1.0/search/"

    for key, dataset in datasets.items():
        print(f"📥 Extracting {key}...")
        records = []

        # 1) On fait d'abord une requête pour obtenir nhits (nombre total d'enregistrements)
        params_count = {
            "dataset": dataset,
            "rows": 0  # on ne veut pas de données, seulement nhits
        }
        response_count = requests.get(base_url, params=params_count)
        response_count.raise_for_status()
        total_hits = response_count.json().get("nhits", 0)
        print(f"   • {total_hits} enregistrements au total pour '{key}'")

        # 2) On boucle ensuite par blocs de size=limit jusqu'à total_hits
        offset = 0
        limit = 100
        while offset < total_hits:
            params = {
                "dataset": dataset,
                "rows": limit,
                "start": offset
            }
            resp = requests.get(base_url, params=params)
            resp.raise_for_status()
            batch = resp.json().get("records", [])
            if not batch:
                # plus rien à récupérer
                break

            records.extend(batch)
            offset += limit

        # Sécurité : parfois last batch peut avoir moins ou plus (selon modifs)
        print(f"   • Récupéré {len(records)} enregistrements pour '{key}' (attendu: {total_hits})")
        all_data[key] = records

    return all_data

if __name__ == "__main__":
    # Pour tester l’extraction seule
    data = extract_all_datasets()
    for k, v in data.items():
        print(f"{k}: {len(v)} records")
