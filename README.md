# 📊 Olist E-Commerce Analytics Suite
### *An End-to-End ELT Pipeline: Python, PostgreSQL, dbt, & Streamlit*



## 🚀 Overview
This project provides a production-ready analytics environment for the Brazilian Olist E-Commerce dataset. It automates the entire lifecycle of data: from raw CSV ingestion to multi-layered dbt transformations, culminating in an interactive Streamlit dashboard featuring **Unsupervised Machine Learning** for anomaly detection and **Pareto (80/20) business analysis**.

## 🏗️ Architecture
The system is fully containerized using **Docker Compose**, ensuring a "one-click" deployment that handles networking between the application and the database.

1.  **Extraction & Load (Python):** Custom SQLAlchemy 2.0 scripts with dynamic chunking to handle high-volume relational data into a `raw` PostgreSQL schema.
2.  **Transformation (dbt):** A modular dbt project that converts raw data into a structured **Star Schema** within an `analytics` schema.
    * **Staging Layer:** Views for light cleaning and column casting.
    * **Mart Layer:** Persistent tables for business-ready logic (Fact & Dimension tables).
3.  **Analytics & Visualization (Streamlit):** An interactive dashboard that queries the `analytics` layer to provide:
    * **Product Anomaly Detection:** Identifying outliers in product dimensions using Unsupervised ML (Isolation Forest/Z-Score).
    * **Pareto Analysis:** Identifying the top 20% of products/categories driving 80% of revenue.
    * **Customer Insights:** Customer retention metrics and purchasing behavior



## 🛠️ Tech Stack
* **Database:** PostgreSQL 15
* **Transformation:** dbt-core & dbt-postgres
* **App/Dashboard:** Streamlit
* **Language:** Python 3.13 (3.11+ should work as well)
* **Containerization:** Docker & Docker Compose
* **Library Highlights:** SQLAlchemy 2.0, Psycopg2, Pandas, Scikit-Learn

---

## 🚦 Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* Python 3.11+ (for initial data setup).
* A Kaggle account (to download the dataset via the script).

### 1. Download the Data
Run the provided setup script to fetch the latest data from Kaggle and place it in the local `data/` directory:
```bash
python scripts/setup_data.py 
``` 

### 2. Configure Environment
Copy the example environment file and add your database credentials:


```
cp .env.example .env
``` 
Note: Ensure DB_HOST is set to db for Docker internal networking.

3. Launch the Suite
Execute the following command to build the containers, load the data, run dbt transforms, and launch the dashboard:


```
docker-compose up --build
```
Access the Dashboard: Once the logs indicate Streamlit is running, navigate to http://localhost:8501.

📈 Key Analytical Features
🤖 Unsupervised ML: Product Anomalies
The pipeline includes a specialized Mart that applies machine learning (Isolation Forest) to identify products with unusual price-to-shipping-cost ratios or pricing outliers. This helps businesses identify potential shipping cost errors or data entry mistakes.


🎯 Pareto (80/20) Logic
Automated SQL models calculate the cumulative revenue contribution of every product category, allowing stakeholders to instantly see which segments are the core drivers of the business.

🧑‍🦰 Customer Insights
Overall Retention rate of customers, how many where likely one-time customers and are lost, times till last puchase based on cutoff date, time between purchases (where purchases that are just one hour apart are lumped together).
