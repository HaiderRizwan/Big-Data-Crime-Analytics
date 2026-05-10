import streamlit as st
import pandas as pd
import psycopg2
import yaml
import os
from pymongo import MongoClient
import plotly.express as px

# Set page config for a premium look
st.set_page_config(page_title="Chicago Crime Analytics", layout="wide")

# Load configuration
@st.cache_resource
def load_config():
    config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# Database connections
def get_pg_connection():
    pg = config['databases']['postgres']
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", pg['host']),
        port=int(os.getenv("POSTGRES_PORT", pg['port'])),
        user=os.getenv("POSTGRES_USER", pg['user']),
        password=os.getenv("POSTGRES_PASSWORD", pg['password']),
        dbname=os.getenv("POSTGRES_DB", pg['dbname'])
    )

def get_mg_collection():
    mg = config['databases']['mongodb']
    mongo_host = os.getenv("MONGO_HOST", mg['host'])
    mongo_port = int(os.getenv("MONGO_PORT", mg['port']))
    mongo_db = os.getenv("MONGO_DB", mg['dbname'])
    mongo_collection = os.getenv("MONGO_COLLECTION", mg['collection'])
    client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")
    return client[mongo_db][mongo_collection]

# Dashboard Layout
st.title("🚨 Real-Time Crime Analytics & Intelligent Alert System")
st.markdown("---")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)

# Main layout columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 Crime Hotspots (K-Means Clustering)")
    try:
        conn = get_pg_connection()
        hotspots_df = pd.read_sql("SELECT * FROM hotspots", conn)
        if not hotspots_df.empty:
            map_kwargs = dict(
                lat="latitude",
                lon="longitude",
                color="cluster_id",
                zoom=10,
                height=500,
                mapbox_style="carto-darkmatter",
            )
            if "incident_count" in hotspots_df.columns:
                map_kwargs["size"] = "incident_count"
                map_kwargs["size_max"] = 40
            fig_map = px.scatter_mapbox(hotspots_df, **map_kwargs)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No hotspot data available yet. Run the Spark ML job.")
        conn.close()
    except Exception as e:
        st.error(f"Postgres Error: {e}")

with col2:
    st.subheader("⚠️ Real-Time Anomaly Alerts")
    try:
        collection = get_mg_collection()
        alerts = list(collection.find().sort("timestamp", -1).limit(10))
        if alerts:
            for alert in alerts:
                st.warning(f"**District {alert['district']}**: {alert['count']} incidents (Threshold: {alert['threshold']})")
        else:
            st.success("No active anomalies detected.")
    except Exception as e:
        st.error(f"MongoDB Error: {e}")

st.markdown("---")

# Trends Section
st.subheader("📈 Historical Crime Trends")
try:
    conn = get_pg_connection()
    trends_df = pd.read_sql("SELECT * FROM crime_trends ORDER BY year, month", conn)
    if not trends_df.empty:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            fig_trend = px.line(trends_df, x="month", y="crime_count", color="year", title="Crimes by Month")
            st.plotly_chart(fig_trend, use_container_width=True)
        with t_col2:
            day_trends = trends_df.groupby("day_of_week")["crime_count"].sum().reset_index()
            fig_day = px.bar(day_trends, x="day_of_week", y="crime_count", title="Crimes by Day of Week")
            st.plotly_chart(fig_day, use_container_width=True)
    conn.close()
except Exception as e:
    st.info("Trend data will appear here after running the Spark Batch job.")

st.markdown("---")

# Arrest rates + latest alerts
a_col1, a_col2 = st.columns(2)

with a_col1:
    st.subheader("🏆 Top Arrest Rates")
    try:
        conn = get_pg_connection()
        arrest_rates_df = pd.read_sql(
            """
            SELECT primary_type, district, arrest_rate, total_crimes, total_arrests
            FROM arrest_rates
            WHERE total_crimes > 0
            ORDER BY arrest_rate DESC, total_arrests DESC
            LIMIT 10
            """,
            conn,
        )
        conn.close()

        if not arrest_rates_df.empty:
            arrest_rates_df["arrest_rate_pct"] = (arrest_rates_df["arrest_rate"] * 100).round(2)
            display_df = arrest_rates_df[
                ["primary_type", "district", "arrest_rate_pct", "total_crimes", "total_arrests"]
            ].rename(columns={"arrest_rate_pct": "arrest_rate_%"}).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No arrest rate data available yet. Run the Spark Batch job.")
    except Exception as e:
        st.error(f"Arrest Rates Error: {e}")

with a_col2:
    st.subheader("🕒 Latest Alerts")
    try:
        conn = get_pg_connection()
        latest_alerts_df = pd.read_sql(
            """
            SELECT district_id, crime_count, threshold, severity, alert_timestamp
            FROM alerts
            ORDER BY alert_timestamp DESC
            LIMIT 10
            """,
            conn,
        )
        conn.close()

        if not latest_alerts_df.empty:
            st.dataframe(latest_alerts_df.reset_index(drop=True), use_container_width=True, hide_index=True)
        else:
            st.info("No alerts in PostgreSQL yet. Start Kafka producer + Storm topology.")
    except Exception as e:
        st.error(f"Latest Alerts Error: {e}")

# Auto-refresh
if st.sidebar.button("Manual Refresh"):
    st.rerun()
