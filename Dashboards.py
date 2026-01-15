import streamlit as st

st.set_page_config(
    page_title="Olist Business Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("🚀 Olist Executive Dashboard")

st.markdown("""
### Welcome to the Olist BI Suite
Use the sidebar on the left to navigate between different analytical views:

* **🕵️ Product Pricing Auditor**: Detect pricing anomalies using Unsupervised ML and analyze category revenue concentration (80/20 Rule).
* **📈 Customer Lifecycle**: Analyze customer retention, recency, and purchase frequency.
""")

# Optional: Add a high-level KPI summary here that pulls from both Marts
st.info("👈 Select a page from the sidebar to begin your analysis.")