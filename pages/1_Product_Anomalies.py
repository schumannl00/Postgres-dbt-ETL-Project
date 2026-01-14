import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
import plotly.express as px
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
safe_password = quote_plus(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else ""

@st.cache_resource
def get_engine():
    conn_url = f"postgresql://{os.getenv('DB_USER')}:{safe_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(conn_url)

@st.cache_data
def load_product_data():
    engine = get_engine()
    # Pull the Mart we built in dbt
    query = "SELECT * FROM analytics.product_cost_decomposition"
    return pd.read_sql(query, engine)

st.set_page_config(page_title="Product Auditor", layout="wide")
st.title("🕵️ Product Pricing Auditor")
st.markdown("This tool identifies listings where **Freight** or **Price** deviate significantly from category norms.")

with st.spinner("Loading Marts from Warehouse..."):
    df = load_product_data()
    
 
st.sidebar.header("Filter Controls")
    
categories = sorted(df['category'].unique().tolist())
selected_cat = st.sidebar.multiselect("Select Product Categories", categories, default=None)
    
contamination = st.sidebar.slider("Anomaly Sensitivity (Contamination)", 0.01, 0.20, 0.05)
    
    
filtered_df = df[df['category'].isin(selected_cat)].copy()

if filtered_df.empty:
    st.warning("Please select at least one category.")
    st.stop()

# 4. ML Logic (Isolation Forest)
# We only train on items that have enough sales history to be "reliable"
ml_ready = filtered_df[filtered_df['reliability_score'] != 'Single Sale'].copy()

if len(ml_ready) > 10:
    features = ['total_cost_z_score', 'total_cost_cv', 'freight_share_pct']
    model = IsolationForest(contamination=contamination, random_state=42)
    ml_ready['anomaly_score'] = model.fit_predict(ml_ready[features].fillna(0))
    ml_ready['Result'] = ml_ready['anomaly_score'].map({1: 'Normal', -1: 'Anomaly'})
    
    # --- UI LAYOUT ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Statistical Outlier Map")
        fig = px.scatter(
            ml_ready, 
            x="avg_price", 
            y="avg_freight",
            labels={
                "avg_price": "Average Product Price",
                "avg_freight": "Average Freight Cost"
            },
            color="Result",
            size="sales_count",
            hover_data=["product_id", "category", "total_cost_z_score", "total_cost_cv", "freight_share_pct"],
            color_discrete_map={'Normal': '#636EFA', 'Anomaly': '#EF553B'},
            template="plotly_white",
            height=600
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Key Metrics")
        total_items = len(ml_ready)
        anomaly_count = len(ml_ready[ml_ready['Result'] == 'Anomaly'])
        
        st.metric("Total Items Analyzed", total_items)
        st.metric("Anomalies Detected", anomaly_count, delta=f"{round(anomaly_count/total_items*100, 1)}%", delta_color="inverse")
        
        with st.expander("What is an Anomaly?"):
            st.write("""
            Anomalies are detected using an **Isolation Forest** model looking at:
            - **Z-Score**: Distance from category mean price.
            - **CV**: Price volatility over time.
            - **Freight Share**: High shipping vs product cost.
            """)

    # 5. Detail Table
    st.markdown("---")
    st.subheader("🚩 High Priority Items for Review")
    st.dataframe(
        ml_ready[ml_ready['Result'] == 'Anomaly'].sort_values('total_cost_z_score', ascending=False),
        width='stretch'
    )
else:
    st.info("Not enough data in the selected category to run Anomaly Detection.")    
    
    
    

