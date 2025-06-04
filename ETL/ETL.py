# ETL.py

import sys
import os

# Ajouter le dossier courant au PYTHONPATH pour que Python trouve Extract/, Transform/, Load/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Extract.extract import extract_all_datasets
from Transform.transform import transform_all_datasets
from Load.load import load_all_datasets

if __name__ == "__main__":
    print("🚀 Lancement du pipeline ETL")

    # 1. Extraction
    raw_data = extract_all_datasets()

    # 2. Transformation
    transformed_data = transform_all_datasets(raw_data)

    # 3. Chargement
    load_all_datasets(transformed_data)

    print("🎉 ETL terminé avec succès")
