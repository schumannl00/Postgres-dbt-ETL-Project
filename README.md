# 🇧🇷 Olist E-Commerce ETL & Analytics Pipeline

### 🚧 Project Status: Active Development
*This is a home/learning project focused on modern data engineering practices. I am currently committing updates several times a week. The project will be considered "v1.0" once fully containerized with Docker.*

## 🎯 Project Overview
The goal of this project is to transform raw e-commerce data from Olist (9+ relational tables) into a structured **Star Schema** for analytical reporting. 

### Current Tech Stack
- **Language:** Python 3.13 
- **Database:** PostgreSQL (Relational Modeling)
- **Extraction:** SQLAlchemy 2.0 & Psycopg3 (Batch loading with dynamic chunking)
- **Transformation:** dbt (Data Build Tool) - *[In Progress]*
- **Orchestration:** TBD (Planned: Docker)

## 🏗️ Architecture
1. **Raw Layer:** Python scripts extract CSV data and load them into a `raw` schema in Postgres using high-performance batch inserts.
2. **Analytics Layer (dbt):** Transforming raw data into cleaned Fact and Dimension tables (SCD Type 2 logic where applicable).
3. **Visualization:** Streamlit dashboard for interactive EDA.

## 📈 Roadmap
- [x] Initial ETL pipeline from CSV to Postgres
- [x] Dynamic parameter-limit handling for wide tables
- [ ] dbt transformation models (Fact/Dimension tables)
- [ ] Streamlit integration for Business Intelligence
- [ ] Dockerization for one-click deployment