import streamlit as st
import pandas as pd
from stress_detection import load_flight_data, analyze_csv
from baseline import get_baseline_for_location
#from gemini_report import generate_risk_report

st.set_page_config(page_title="Aquatic Stress Sentinel", layout="wide")

# ── Custom Styling ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1 {
    font-size: 2rem !important;
    font-weight: 300 !important;
    letter-spacing: -0.5px !important;
    color: #0a2540 !important;
}

.stCaption {
    color: #6b7c93 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.3px !important;
}

section[data-testid="stSidebar"] {
    background-color: #f7f9fc !important;
    border-right: 1px solid #e3e8ef !important;
}

.stDataFrame {
    border: 1px solid #e3e8ef !important;
    border-radius: 8px !important;
}

div[data-testid="stMetric"] {
    background-color: #f7f9fc;
    border: 1px solid #e3e8ef;
    border-radius: 8px;
    padding: 1rem;
}

.stAlert {
    border-radius: 8px !important;
}

h2, h3 {
    font-weight: 400 !important;
    color: #0a2540 !important;
    letter-spacing: -0.3px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Aquatic Stress Sentinel")
st.caption("Drone-based early warning system for aquatic ecosystem stress")

# ── Sidebar Controls ────────────────────────────────────────────────

with st.sidebar:
    st.header("Mission Settings")

    environment = st.radio(
        "Environment",
        options=["freshwater", "marine"],
        format_func=lambda x: "Freshwater" if x == "freshwater" else "Marine"
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if environment == "marine":
        st.markdown("---")
        st.markdown("**Flight Location**")
        st.caption("Enter coordinates to find the nearest NOAA baseline station.")
        manual_lat = st.number_input("Latitude", value=24.71, format="%.4f")
        manual_lon = st.number_input("Longitude", value=-81.10, format="%.4f")

# ── Main Panel ──────────────────────────────────────────────────────

if uploaded_file is None:
    st.info("Upload a drone CSV file in the sidebar to begin analysis.")
    st.stop()

baseline_temp = None
station_name = None

if environment == "marine":
    with st.spinner("Fetching baseline from NOAA..."):
        station_name, baseline_temp = get_baseline_for_location(manual_lat, manual_lon)
    if baseline_temp:
        st.sidebar.success(f"Baseline: {baseline_temp}°C — {station_name}")
    else:
        st.sidebar.warning("Could not fetch NOAA baseline.")

df = load_flight_data(uploaded_file)
df = analyze_csv(df, environment, baseline_temp)

# ── Summary Metrics ──────────────────────────────────────────────────
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Readings", len(df))
m2.metric("Avg Surface Temp", f"{df['water_surface_temp_c'].mean():.1f} °C")
m3.metric("Max Surface Temp", f"{df['water_surface_temp_c'].max():.1f} °C")
m4.metric("Environment", environment.capitalize())
st.markdown("---")

# ── Results ──────────────────────────────────────────────────────────

if environment == "freshwater":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fish Kill Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "fish_kill_status"]], use_container_width=True)
    with col2:
        st.subheader("Algal Bloom Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "algal_bloom_status"]], use_container_width=True)

elif environment == "marine":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Coral Bleaching Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "coral_bleaching_status"]], use_container_width=True)
    with col2:
        st.subheader("Algal Bloom Risk")
        st.dataframe(df[["timestamp", "temperature_c", "water_surface_temp_c",
                          "algal_bloom_status"]], use_container_width=True)

# ── Gemini Report ─────────────────────────────────────────────────────
# st.markdown("---")
# st.subheader("AI Ecosystem Risk Report")
# with st.spinner("Generating report..."):
#     report = generate_risk_report(df=df, environment=environment,
#                                   station_name=station_name, baseline_temp=baseline_temp)
# st.markdown(report)