# Load/load.py

import pandas as pd
import json

def load_all_datasets(cleaned_data):
    """
    cleaned_data : dict clef -> liste de dictionnaires
    - si key == "zti" → écriture en JSON (géométries), sinon CSV
    """
    for key, records in cleaned_data.items():
        if key == "zti":
            output_file = f"{key}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            print(f"✅ Chargé {len(records)} enregistrements dans {output_file}")
        else:
            df = pd.DataFrame(records)
            output_file = f"{key}.csv"
            df.to_csv(output_file, index=False)
            print(f"✅ Chargé {len(records)} enregistrements dans {output_file}")
