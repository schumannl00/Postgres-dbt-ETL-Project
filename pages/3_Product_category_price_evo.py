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
    query = "SELECT * FROM analytics.monthly_revenue_by_cat"
    return pd.read_sql(query, engine)

st.set_page_config(page_title="Monthly Revenue by Category", layout="wide")
st.title("Monthly Revenue by Product Category")
st.markdown("TTBA")

with st.spinner("Loading Marts from Warehouse..."):
    df = load_product_data()
    
 
st.sidebar.header("Select categoty and year")
    
categories = sorted(df['product_category'].unique().tolist())
years_float = df["revenue_year"].unique().tolist()
years = sorted(list(map(int, years_float)))
selected_cat = st.sidebar.multiselect("Select Product Categories", categories, default=None)
selected_year = st.sidebar.multiselect("Select Year", years, default=None)


    
filtered_df = df[
    (df['product_category'].isin(selected_cat)) & 
    (df['revenue_year'].isin(selected_year))
].copy()
if filtered_df.empty:
    st.warning("Please select at least one category and a year.")
    st.stop()

max_cols = 2
n_years = len(selected_year)
n_cat = len(selected_cat)


n_rows = (n_cat + max_cols - 1) // max_cols  # Ceiling division

# Create grid
for row in range(n_rows):
    cols = st.columns(max_cols)
    
    for col_idx in range(max_cols):
        cat_idx = row * max_cols + col_idx
        
        # Check if we still have categories to display
        if cat_idx < n_cat:
            cat = selected_cat[cat_idx]
            
            with cols[col_idx]:
                st.subheader(str(cat))
                cat_df = filtered_df[filtered_df['product_category'] == cat]
                avg_monthly_by_year = cat_df.groupby('revenue_year')['monthly_revenue'].mean().round(2).reset_index()
                avg_monthly_by_year.columns = ['revenue_year', 'avg_monthly_revenue']
                fig = px.line(
                    cat_df,
                    x='revenue_month_num',
                    y='monthly_revenue',
                    color= "revenue_year",
                    height=400,
                    labels= {"revenue_month_num" : "Month (Number)", 
                            "monthly_revenue" : "Revenue", "revenue_year" : "Year", "product_sold" : "Products sold this month"}, 
                    hover_data = ['revenue_month_num', 'revenue_year', 'monthly_revenue', 'product_sold']
                )
                fig.update_xaxes(dtick="M1", tickformat="%b")
                fig.update_yaxes(matches=None)
                st.plotly_chart(fig, width="stretch", key=f"chart_{cat}")
                st.dataframe(avg_monthly_by_year)


    
    

