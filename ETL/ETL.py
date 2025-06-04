# ETL.py

import sys
import os

# Make sure the ETL folders are on Python’s path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Extract.extract import extract_all_datasets
from Transform.transform import transform_all_datasets
from Load.load import load_all_datasets

if __name__ == "__main__":
    print("🚀 Starting ETL pipeline")

    # 1. Extraction
    raw_data = extract_all_datasets()

    # 2. Transformation
    transformed_data = transform_all_datasets(raw_data)

    # 3. Loading
    load_all_datasets(transformed_data)

    print("🎉 ETL pipeline complete")
