"""
Streamlit Dashboard for Smart Log Analyzer
"""
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
API_URL = "http://localhost:10000"  # Your FastAPI endpoint

# --- Page Config ---
st.set_page_config(page_title="Log Analyzer", layout="wide")
st.title("📊 Smart Log Analyzer Dashboard")

# --- Sidebar Actions ---
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Ingest Sample Logs"):
        with st.spinner("Ingesting logs..."):
            try:
                response = requests.post(f"{API_URL}/ingest", json={"filepath": "/app/data/sample.log"})
                if response.status_code == 200:
                    st.success("✅ Logs ingested successfully!")
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")

    st.divider()
    st.caption("Built with Streamlit & FastAPI")

# --- Main Dashboard ---
st.markdown("### 📈 Key Metrics")

# Fetch Data
try:
    # 1. Top IPs
    top_ips_res = requests.get(f"{API_URL}/top-ips?limit=5")
    top_ips = top_ips_res.json().get("results", [])
    
    # 2. Hourly Volume
    hourly_res = requests.get(f"{API_URL}/hourly-volume")
    hourly_data = hourly_res.json().get("results", [])
    
    # 3. Error Rates (for metrics)
    error_res = requests.get(f"{API_URL}/error-rates")
    error_data = error_res.json().get("results", [])

except Exception as e:
    st.warning(f"Could not connect to API. Make sure the container is running. Error: {e}")
    top_ips, hourly_data, error_data = [], [], []

# --- Display Metrics ---
if top_ips or hourly_data:
    col1, col2, col3 = st.columns(3)
    
    # Total Logs (Roughly estimate from hourly data)
    total_logs = sum([d.get("request_count", 0) for d in hourly_data]) if hourly_data else 0
    col1.metric("📦 Total Logs", f"{total_logs:,}")
    
    # Unique IPs
    unique_ips = len(top_ips) if top_ips else 0
    col2.metric("🌐 Unique IPs", unique_ips)
    
    # Error Rate (Approx)
    total_errors = sum([d.get("error_count", 0) for d in error_data]) if error_data else 0
    total_requests = sum([d.get("total_requests", 0) for d in error_data]) if error_data else 1
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    col3.metric("⚠️ Error Rate", f"{error_rate:.1f}%")
else:
    st.info("No data found. Click 'Ingest Sample Logs' in the sidebar to load data.")

# --- Charts ---
st.divider()
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Top IPs")
    if top_ips:
        df_ips = pd.DataFrame(top_ips)
        st.dataframe(df_ips, width='stretch')
        
        # Bar Chart
        fig, ax = plt.subplots()
        sns.barplot(data=df_ips, x="ip", y="request_count", hue="ip", palette="viridis", legend=False)
        ax.set_xlabel("IP Address")
        ax.set_ylabel("Request Count")
        st.pyplot(fig)
    else:
        st.caption("No IP data available.")

with col_chart2:
    st.subheader("📈 Hourly Volume")
    if hourly_data:
        df_hourly = pd.DataFrame(hourly_data)
        # Convert hour string to datetime for better plotting
        df_hourly['hour'] = pd.to_datetime(df_hourly['hour'])
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_hourly['hour'], df_hourly['request_count'], marker='o')
        ax.set_xlabel("Time")
        ax.set_ylabel("Requests")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.caption("No hourly data available.")

st.divider()
st.caption("Data fetched from FastAPI backend.")
