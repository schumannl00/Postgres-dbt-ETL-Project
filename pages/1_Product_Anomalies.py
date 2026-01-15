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
    df_final = filtered_df.merge(
        ml_ready[['product_id', 'Result']], on='product_id', how='left')
    df_final['Result'] = df_final['Result'].fillna('Single sale - No Analysis')
    assert len(df_final) == len(filtered_df), "Merge error: Row counts do not match after ML labeling."
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
  
    
    st.subheader("🎯 Pareto Category Analysis")

    # Since the math is in SQL, we just count
    total_products = len(filtered_df)
    top_80_df = filtered_df[filtered_df['is_revenue_workhorse'] == True]
    top_80_count = len(top_80_df)

    col1, col2 = st.columns(2)
    col1.metric("Products driving 80% Revenue", top_80_count)
    col2.metric("% of Inventory", f"{(top_80_count/total_products)*100:.1f}%")

    st.write(f"In your selected categories: {' , '.join(map(str, selected_cat))} , **{top_80_count}** products generate 80% of the total revenue.")
    
    # --- High Priority Audit Section ---
    st.markdown("---")
    st.subheader("🚩 High Priority Audit: Revenue Workhorses & Anomalies")

    # Filter logic: Let the user decide if they want to see everything or just the 'Big Fish'
    show_only_pareto = st.toggle("Filter for Revenue Workhorses (Top 80% Rev Only)", value=False)
    show_only_outliers = st.toggle("Show Only Anomalies", value=False)
    # Prepare the view
    audit_df = df_final.sort_values('product_revenue_share_pct', ascending=False).copy()
    if show_only_pareto:
        audit_df = audit_df[audit_df['is_revenue_workhorse'] == True]
    if show_only_outliers:
        audit_df = audit_df[audit_df['Result'] == 'Anomaly']

    

    # Render with improved formatting
    st.data_editor(
        audit_df[[
            "product_id", "category", "Result", "is_revenue_workhorse", 
            "product_revenue_share_pct", "avg_price", "total_cost_z_score", "sales_count", "is_price_rebalanced"
        ]],
        column_config={
            "Result": st.column_config.TextColumn("Audit Status"),
            "is_revenue_workhorse": st.column_config.CheckboxColumn("80/20 Workhorse", ),
            "product_revenue_share_pct": st.column_config.ProgressColumn(
                "Revenue Percentile",
                help="How much this specific product contributes to the category's total sales revenue.",
                format="%.2f",
                min_value=0,
                max_value=100,
            ),
            "avg_price": st.column_config.NumberColumn("Avg Price", format="$%.2f"),
            "total_cost_z_score": st.column_config.NumberColumn("Volatility (Z-Score)", format="%.2f"), 
            "is_price_rebalanced": st.column_config.CheckboxColumn("Price Rebalance Candidate", help="Flagged for potential price adjustment based on cost anomalies."),
        },
        disabled=True, # Keeps it as a view-only table
        width='stretch', hide_index=True
    )
else:
    st.info("Not enough data in the selected category to run Anomaly Detection. Minimum 10 products with more than one sale required.")    
    
    
    

