import os
import time
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from functools import wraps
from urllib.parse import quote_plus
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent
env_path = base_path / ".env"



load_dotenv(dotenv_path=env_path)
safe_password = quote_plus(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else ""

DATA_DIR = "./data"
DB_URL = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
print(f"Connecting to database at: {DB_URL}")

engine = create_engine(DB_URL)

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Finished in {end - start:.2f} seconds\n")
        return result
    return wrapper

@timer
def load_all_data():
    """Loops through data directory and loads all CSVs into Postgres 'raw' schema."""
    
    if not os.path.exists(DATA_DIR):
        print(f"Error: Directory {DATA_DIR} not found.")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    if not files:
        print("No CSV files found to load.")
        return

    print(f"Found {len(files)} files. Starting load...")

    for file in files:
        # 1. Generate table name from filename (e.g., 'olist_orders_dataset.csv' -> 'orders')
        # Custom logic: removing 'olist_' prefix and '_dataset' suffix for cleaner DB names
        table_name = file.replace('olist_', '').replace('_dataset.csv', '').replace('.csv', '')
        
        file_path = os.path.join(DATA_DIR, file)
        
        print(f"Processing: {file} -> raw.{table_name}")
        
        # 2. Extract
        df = pd.read_csv(file_path)
        
        # 3. Transform (Basic cleaning for SQL compatibility)
        df.columns = [c.lower().replace(' ', '_').replace('.', '_') for c in df.columns]
        safe_chunksize = 60000 // len(df.columns)
        # 4. Load (SQLAlchemy 2.0 transaction)
        with engine.begin() as conn:
            df.to_sql(
                name=table_name,
                con=conn,
                schema='raw',
                if_exists='replace',
                index=False,
                chunksize=safe_chunksize,
                method='multi'
            )
        print(f"Loaded {len(df)} rows.")

if __name__ == "__main__":
    load_all_data()