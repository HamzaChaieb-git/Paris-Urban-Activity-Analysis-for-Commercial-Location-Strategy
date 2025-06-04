import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions
from Extract.fetch_panels import fetch_panels_data
from Transform.clean_panels import clean_panels
from Load.load_panels import load_panels

def main():
    print("🔄 Starting ETL Pipeline...")
    
    # Extract
    print("📥 Extracting panels data...")
    raw_data = fetch_panels_data()
    print(f"✅ Extracted {len(raw_data)} records")
    
    # Transform
    print("🔧 Transforming panels data...")
    gdf = clean_panels(raw_data)
    print(f"✅ Transformed {len(gdf)} records")
    
    # Load
    print("📤 Loading panels into database...")
    load_panels(gdf)
    print("✅ ETL Pipeline completed successfully!")

if __name__ == "__main__":
    main()