import streamlit as st
import pandas as pd
from stress_detection import load_flight_data, analyze_csv
from baseline import get_baseline_for_location
#from gemini_report import generate_risk_report

st.set_page_config(page_title="Aquatic Stress Sentinel", page_icon="🌊", layout="wide")

st.title("Aquatic Stress Sentinel")
st.caption("Drone-based early warning system for aquatic ecosystem stress")

# ── Sidebar Controls ────────────────────────────────────────────────

with st.sidebar:
    st.header("Mission Settings")

    environment = st.radio(
        "Select Environment",
        options=["freshwater", "marine"],
        format_func=lambda x: "Freshwater" if x == "freshwater" else "Marine"
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if environment == "marine":
        st.subheader("Flight Location")
        st.caption("Enter the coordinates of where the drone flew so we can find the nearest NOAA station.")
        manual_lat = st.number_input("Latitude", value=24.71, format="%.4f")
        manual_lon = st.number_input("Longitude", value=-81.10, format="%.4f")

# ── Main Panel ──────────────────────────────────────────────────────

if uploaded_file is None:
    st.info("Upload a CSV file in the sidebar to begin analysis.")
    st.stop()

# initialize baseline variables
baseline_temp = None
station_name = None

# fetch NOAA baseline for marine mode using manually entered coordinates
if environment == "marine":
    with st.spinner("Fetching baseline from NOAA..."):
        station_name, baseline_temp = get_baseline_for_location(manual_lat, manual_lon)
    if baseline_temp:
        st.sidebar.success(f"Baseline: {baseline_temp}°C ({station_name})")
    else:
        st.sidebar.warning("Could not fetch baseline.")

# load and analyze
df = load_flight_data(uploaded_file)
df = analyze_csv(df, environment, baseline_temp)

st.success(f"✅ {len(df)} readings analyzed — {environment} environment")

# ── Results ─────────────────────────────────────────────────────────

if environment == "freshwater":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fish Kill Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                        "fish_kill_status"]])

    with col2:
        st.subheader("Algal Bloom Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "algal_bloom_status"]])

elif environment == "marine":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Coral Bleaching Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                        "coral_bleaching_status"]])

    with col2:
        st.subheader("Algal Bloom Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "algal_bloom_status"]])

# ── Gemini Report ────────────────────────────────────────────────────

#st.divider()
#t.subheader("AI Ecosystem Risk Report")

#with st.spinner("Generating report..."):
#    report = generate_risk_report(
#        df=df,
#        environment=environment,
#        station_name=station_name,
#        baseline_temp=baseline_temp
#    )

#st.markdown(report)