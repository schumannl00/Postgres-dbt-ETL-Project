#!/bin/bash
set -e

# 1. Wait for Postgres
echo "⏳ Waiting for Postgres..."
until pg_isready -h "$DB_HOST" -p 5432 -U "$DB_USER"; do
  sleep 2
done

# 2. Run the Load Script (CSV -> Postgres)
python scripts/extract_load.py

# 3. Run dbt
cd olist_transform
dbt deps --profiles-dir .
dbt seed --profiles-dir .
dbt build --profiles-dir .

# 4. Start App
cd ..
streamlit run Dashboards.py --server.port=8501 --server.address=0.0.0.0