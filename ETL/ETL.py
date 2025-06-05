import time
import pandas as pd
from typing import Dict

from Extract.extract import extract_paris_data
from Transform.transform import transform_paris_data
from Load.load import load_paris_data

def run_etl(db_config: Dict = None) -> Dict[str, pd.DataFrame]:
    """Run the complete ETL pipeline"""
    print("🚀 STARTING COMPLETE ETL PIPELINE")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Extract
        raw_data = extract_paris_data()
        
        # Transform  
        transformed_data = transform_paris_data(raw_data)
        
        # Load
        load_paris_data(transformed_data, db_config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 50)
        print(f"🎉 ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"📊 Datasets processed: {len(transformed_data)}")
        print(f"🗄️  Data loaded to PostgreSQL database")
        
        return transformed_data
        
    except Exception as e:
        print(f"\n❌ ETL PIPELINE FAILED: {e}")
        raise

if __name__ == "__main__":
    # Database configuration (uses defaults from docker-compose)
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'city_marketing',
        'user': 'postgres',
        'password': '1234'
    }
    
    # Run complete ETL process
    data = run_etl(db_config)
    
    # Access individual datasets
    bike_counters = data.get('bike_counters')
    advertising_panels = data.get('advertising_panels')
    pedestrian_zones = data.get('pedestrian_zones')
    
    print("\n📈 Data ready for marketing panel analysis!")
    
    # Optional: Print basic stats
    if bike_counters is not None:
        print(f"🚴 Bike counter records: {len(bike_counters)}")
    if advertising_panels is not None:
        print(f"📢 Advertising panels: {len(advertising_panels)}")
    if pedestrian_zones is not None:
        print(f"🚶 Pedestrian zones: {len(pedestrian_zones)}")