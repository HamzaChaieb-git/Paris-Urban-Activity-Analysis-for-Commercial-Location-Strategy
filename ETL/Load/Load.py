import pandas as pd
import json
import psycopg2
from sqlalchemy import create_engine, text
from datetime import datetime
from typing import Dict
import ast

def load_paris_data(transformed_data: Dict[str, pd.DataFrame], db_config: Dict = None) -> None:
    """Load transformed data to PostgreSQL database"""
    print(f"\n💾 STARTING LOAD TO POSTGRESQL...")
    
    if not transformed_data:
        print("❌ No transformed data to load.")
        return
    
    # Default database configuration from docker-compose
    if db_config is None:
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'city_marketing',
            'user': 'postgres',
            'password': '1234'
        }
    
    # Create SQLAlchemy engine
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(connection_string)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        with engine.connect() as conn:
            print("✅ Connected to PostgreSQL database")
            
            # Load each dataset
            for dataset_name, df in transformed_data.items():
                print(f"\n📊 Loading {dataset_name}...")
                
                # Prepare DataFrame for PostgreSQL
                df_clean = prepare_dataframe_for_postgres(df, dataset_name)
                
                # Create table name
                table_name = f"{dataset_name}_{timestamp}"
                
                # Load to PostgreSQL
                df_clean.to_sql(
                    table_name, 
                    engine, 
                    if_exists='replace', 
                    index=False,
                    method='multi',
                    chunksize=1000
                )
                
                print(f"   ✅ Loaded {len(df_clean)} rows to table: {table_name}")
                
                # Create indexes for performance
                create_indexes(conn, table_name, dataset_name)
            
            # Create summary table
            create_summary_table(conn, transformed_data, timestamp)
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure your PostgreSQL container is running: docker-compose up -d")
        raise
    
    print(f"\n🎉 LOAD COMPLETE! All data loaded to PostgreSQL database")

def prepare_dataframe_for_postgres(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Prepare DataFrame for PostgreSQL insertion"""
    df_clean = df.copy()
    
    # Handle coordinates and geometry columns
    for col in df_clean.columns:
        if 'coordinates' in col.lower() or 'geometry' in col.lower():
            # Convert dict/object columns to JSON strings
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x))
    
    # Handle datetime columns
    for col in df_clean.columns:
        if df_clean[col].dtype == 'datetime64[ns]':
            # Keep as datetime - PostgreSQL will handle it
            pass
    
    # Handle null values
    df_clean = df_clean.fillna('')
    
    return df_clean

def create_indexes(conn, table_name: str, dataset_name: str) -> None:
    """Create indexes for better query performance"""
    try:
        if dataset_name == 'bike_counters':
            # Index on arrondissement and datetime for bike counters
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arrondissement ON {table_name} (arrondissement)"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_datetime ON {table_name} (count_datetime)"))
            conn.commit()
            
        elif dataset_name == 'advertising_panels':
            # Index on arrondissement for panels
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arrondissement ON {table_name} (arrondissement)"))
            conn.commit()
            
        elif dataset_name == 'pedestrian_zones':
            # Index on arrondissement for zones
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arrondissement ON {table_name} (arrondissement)"))
            conn.commit()
            
        print(f"   📈 Created indexes for {table_name}")
        
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create indexes for {table_name}: {e}")

def create_summary_table(conn, transformed_data: Dict[str, pd.DataFrame], timestamp: str) -> None:
    """Create a summary table with ETL metadata"""
    try:
        summary_data = []
        for dataset_name, df in transformed_data.items():
            summary_data.append({
                'dataset_name': dataset_name,
                'table_name': f"{dataset_name}_{timestamp}",
                'record_count': len(df),
                'columns': ', '.join(df.columns),
                'load_timestamp': datetime.now()
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_sql(
            f'etl_summary_{timestamp}',
            conn,
            if_exists='replace',
            index=False
        )
        
        print(f"   📋 Created summary table: etl_summary_{timestamp}")
        
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create summary table: {e}")