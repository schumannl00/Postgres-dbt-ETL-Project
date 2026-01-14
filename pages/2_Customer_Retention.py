import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()
safe_password = quote_plus(os.getenv('DB_PASS')) if os.getenv('DB_PASS') else ""
# Use the cached engine to keep it snappy
@st.cache_resource
def get_engine():
    conn_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{safe_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(conn_url)

@st.cache_data
def load_retention_data():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM analytics.customer_retention", engine)

st.set_page_config(page_title="Retention Analysis", layout="wide")
st.title("📈 Customer Lifecycle & Retention")

df = load_retention_data()


# --- Top Level Metrics ---
total_customers = df['customer_unique_id'].nunique()
repeat_rate = (len(df[df['order_sequence'] > 1]) / len(df)) * 100

m1, m2 = st.columns(2)
m1.metric("Total Unique Customers", f"{total_customers:,}")
m2.metric("Repeat Purchase Rate", f"{repeat_rate:.2f}%")

# --- Lifecycle Distribution ---
st.subheader("Customer Segments")
# This visualizes our 'Initial Purchase', 'Repeat Transaction', and 'Lapsed' logic
fig_pie = px.pie(df, names='lifecycle_stage', hole=0.5, 
                 color_discrete_sequence=px.colors.qualitative.Pastel, )
st.plotly_chart(fig_pie, width="stretch")

# --- Recency Analysis ---
st.subheader("Recency Distribution")
st.markdown("How many days since the customer's last activity?")
fig_recency = px.histogram(df, x="recency_days", nbins=50, 
                           title="Days Since Last Purchase (Dataset Cutoff)",
                           color_discrete_sequence=["#174C70"], )

fig_recency.update_traces(
    marker_line_width=1,        # The thickness of the border
    marker_line_color="white",  # The color of the border
    opacity=0.85                # Slight transparency for a modern look
)

fig_recency.update_layout(
    bargap=0.1,                 # This creates the "slight separation" between bars
    xaxis_title="Days Since Last Purchase",
    yaxis_title="Number of Customers"
)


st.plotly_chart(fig_recency, width="stretch")


st.subheader("Time between Purchases")
repeat_behavior_df = df[df['order_sequence'] > 1].copy()
repeat_behavior_df['days_between_orders'] = repeat_behavior_df['days_between_orders'].fillna(0)
threshold = 0.05  # Approximately 1h this filters out technical splits which are quite frequent in the data, so orders with a few seconds difference

# Filter out the "Technical Splits" for your Repeat Rate and Histogram
true_repeat_df = df[
    (df['order_sequence'] > 1) & 
    (df['days_between_orders'] > threshold)
].copy()

st.markdown("For repeat customers, how are the days between their purchases distributed?" \
            " (Excludes purchases made just 1h apart) ")
if not repeat_behavior_df.empty : 
    fig_time_between = px.histogram(true_repeat_df, x="days_between_orders", nbins=200, 
                           title="Days between Purchases (including same day but excluding technical splits)",
                           color_discrete_sequence=["#14530F"], template= "plotly_white") 

fig_time_between.update_traces(
    xbins = dict(start = 0 ), 
    marker_line_width=1,        # The thickness of the border
    marker_line_color="white",  # The color of the border
    opacity=0.85                # Slight transparency for a modern look
)

fig_time_between.update_layout(
    bargap=0.1,                 # This creates the "slight separation" between bars
    xaxis_title="Days between Purchases",
    yaxis_title="Number of Customers",
    xaxis=dict(range=[0, true_repeat_df['days_between_orders'].max() * 1.05])
    
)


st.plotly_chart(fig_time_between, width="stretch")
same_day_count = len(repeat_behavior_df[repeat_behavior_df['days_between_orders'] <1 ])
true_day_count = len(true_repeat_df[true_repeat_df["days_between_orders"] < 1])
st.write(f"📊 Note: **{same_day_count}** orders were placed on the same day as a previous purchase. From those only {true_day_count} should be seen as credible. The remaining {same_day_count - true_day_count} are likely technical splits.")