"""
Streamlit Dashboard for Smart Log Analyzer
"""

# --- Configuration ---
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:10000")

# --- Page Config ---
st.set_page_config(page_title="Log Analyzer", layout="wide")
st.title("📊 Smart Log Analyzer Dashboard")

# --- Sidebar Actions ---
with st.sidebar:
    st.header("⚙️ Controls")

    st.markdown("**Upload a log file:**")
    uploaded_file = st.file_uploader("Choose a .log file", type=["log", "txt"])

    if uploaded_file is not None:
        if st.button("📤 Upload & Analyze"):
            with st.spinner("Uploading and ingesting..."):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "text/plain",
                        )
                    }
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("✅ Logs ingested successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {e}")
    st.divider()
    st.caption("Built with Streamlit & FastAPI")


# --- Main Dashboard ---
st.markdown("### 📈 Key Metrics")

# Add this too, near the top of your dashboard
import socket

try:
    ip = socket.gethostbyname("smart-log-analyzer-gl1x.onrender.com")
    st.write(f"DEBUG - DNS resolved to: {ip}")
except Exception as e:
    st.write(f"DEBUG - DNS failed: {e}")


def fetch_from_api(path, timeout=90):
    """
    Fetch data from the API with retry and parse-safety.
    Handles Render cold starts and non-JSON responses gracefully.
    """
    import time

    for attempt in range(3):
        try:
            response = requests.get(f"{API_URL}{path}", timeout=timeout)

            # TEMP DEBUG: Print what the API actually returned
            st.write(f"DEBUG - Status: {response.status_code}")
            st.write(
                f"DEBUG - Content-Type: {response.headers.get('Content-Type', 'NONE')}"
            )
            st.write(f"DEBUG - Body (first 500 chars):")
            st.code(response.text[:500])

            # Check if response is valid JSON
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                # Not JSON — likely a cold-start HTML page from Render
                if attempt < 2:
                    time.sleep(10)  # Wait for API to wake up
                    continue
                else:
                    return None

            if response.status_code == 200:
                return response.json()
            else:
                if attempt < 2:
                    time.sleep(5)
                    continue
                return None

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 2:
                time.sleep(10)
                continue
            return None
        except Exception:
            return None

    return None


# --- Fetch Data ---
top_ips_data = fetch_from_api("/top-ips?limit=5")
hourly_data_raw = fetch_from_api("/hourly-volume")
error_data_raw = fetch_from_api("/error-rates")

if top_ips_data is None or hourly_data_raw is None or error_data_raw is None:
    st.warning(
        "⚠️ **API is waking up.** Render's free tier sleeps after 15 minutes of "
        "inactivity. This first request can take up to 60 seconds. "
        "Please **refresh this page** in a moment to try again."
    )
    top_ips = []
    hourly_data = []
    error_data = []
else:
    top_ips = top_ips_data.get("results", [])
    hourly_data = hourly_data_raw.get("results", [])
    error_data = error_data_raw.get("results", [])


# --- Display Metrics ---
if top_ips or hourly_data:
    col1, col2, col3 = st.columns(3)

    # Total Logs (Roughly estimate from hourly data)
    total_logs = (
        sum([d.get("request_count", 0) for d in hourly_data]) if hourly_data else 0
    )
    col1.metric("📦 Total Logs", f"{total_logs:,}")

    # Unique IPs
    unique_ips = len(top_ips) if top_ips else 0
    col2.metric("🌐 Unique IPs", unique_ips)

    # Error Rate (Approx)
    total_errors = (
        sum([d.get("error_count", 0) for d in error_data]) if error_data else 0
    )
    total_requests = (
        sum([d.get("total_requests", 0) for d in error_data]) if error_data else 1
    )
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
        st.dataframe(df_ips, width="stretch")

        # Bar Chart
        fig, ax = plt.subplots()
        sns.barplot(
            data=df_ips,
            x="ip",
            y="request_count",
            hue="ip",
            palette="viridis",
            legend=False,
        )
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
        df_hourly["hour"] = pd.to_datetime(df_hourly["hour"])

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_hourly["hour"], df_hourly["request_count"], marker="o")
        ax.set_xlabel("Time")
        ax.set_ylabel("Requests")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.caption("No hourly data available.")

st.divider()
st.caption("Data fetched from FastAPI backend.")
