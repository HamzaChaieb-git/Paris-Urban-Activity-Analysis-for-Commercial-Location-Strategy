import pandas as pd
import json
from sqlalchemy import create_engine, text
from typing import Dict

def load_paris_data(transformed_data: Dict[str, pd.DataFrame], db_config: Dict = None) -> None:
    """Load transformed data to PostgreSQL database"""
    print("\n💾 STARTING LOAD TO POSTGRESQL...")
    if not transformed_data:
        print("❌ No transformed data to load.")
        return

    # Default DB config
    if db_config is None:
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'city_marketing',
            'user': 'postgres',
            'password': '1234'
        }

    conn_str = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    engine = create_engine(conn_str)

    try:
        with engine.connect() as conn:
            print("✅ Connected to PostgreSQL database")

            for dataset_name, df in transformed_data.items():
                print(f"\n📊 Loading {dataset_name}...")

                # JSON-ify any geo/geometry columns
                df_clean = df.copy()
                for col in df_clean.columns:
                    if 'geo' in col.lower() or 'geometry' in col.lower():
                        df_clean[col] = df_clean[col].apply(
                            lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x)
                        )
                df_clean = df_clean.fillna('')

                # Use dataset name as table name
                df_clean.to_sql(
                    dataset_name,
                    engine,
                    if_exists='replace',
                    index=False,
                    method='multi',
                    chunksize=1000
                )
                print(f"   ✅ Loaded {len(df_clean)} rows to table: {dataset_name}")

                _create_indexes(conn, dataset_name, dataset_name)

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure your PostgreSQL container is running: docker-compose up -d")
        raise

    print("\n🎉 LOAD COMPLETE! All data loaded to PostgreSQL database")


def _create_indexes(conn, table_name: str, dataset_name: str):
    """Create indexes for better query performance"""
    try:
        if dataset_name == 'vehicle_counters':
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arr ON {table_name} (arrondissement)"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_ts ON {table_name} (timestamp)"))
        elif dataset_name == 'associative_panels':
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arr ON {table_name} (arrondissement)"))
        elif dataset_name == 'pedestrian_zones':
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_arr ON {table_name} (arrondissement)"))
        conn.commit()
        print(f"   📈 Created indexes for {table_name}")
    except Exception as e:
        print(f"   ⚠️ Warning: could not create indexes for {table_name}: {e}")
