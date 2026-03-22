import google.generativeai as genai
import streamlit as st


def generate_risk_report(df, environment, station_name=None, baseline_temp=None):
    """
    Takes the analyzed dataframe and generates a plain-language
    ecosys risk report using the Gemini API.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    # summarize the data to keep the prompt concise
    total_readings = len(df)
    avg_temp = round(df["water_surface_temp_c"].mean(), 2)
    max_temp = round(df["water_surface_temp_c"].max(), 2)
    min_temp = round(df["water_surface_temp_c"].min(), 2)

    if environment == "freshwater":
        fish_kill_counts = df["fish_kill_status"].value_counts().to_dict()
        algal_bloom_counts = df["algal_bloom_status"].value_counts().to_dict()
        stressor_summary = f"""
        - Fish Kill Risk readings: {fish_kill_counts}
        - Algal Bloom Risk readings: {algal_bloom_counts}
        """
    else:
        coral_counts = df["coral_bleaching_status"].value_counts().to_dict()
        algal_bloom_counts = df["algal_bloom_status"].value_counts().to_dict()
        baseline_info = f"Baseline sea surface temp: {baseline_temp}°C (from {station_name})" if baseline_temp else ""
        stressor_summary = f"""
        - Coral Bleaching Risk readings: {coral_counts}
        - Algal Bloom Risk readings: {algal_bloom_counts}
        - {baseline_info}
        """

    prompt = f"""
    You are a marine and freshwater ecosystem scientist reviewing drone-collected 
    water surface temperature data. Write a concise, plain-language ecosystem 
    health report (3-4 paragraphs) based on the following flight data summary.
    
    Environment type: {environment}
    Total readings: {total_readings}
    Temperature range: {min_temp}°C to {max_temp}°C
    Average temperature: {avg_temp}°C
    
    Stressor analysis:
    {stressor_summary}
    
    Your report should:
    1. Summarize the overall ecosystem health based on the data
    2. Explain what the detected risk levels mean for aquatic life and the ecosystem as a whole
    3. Suggest specific recommended actions for conservationists or local agencies
    4. Note any climate change context that is relevant
    
    Write in clear language that a non-scientist could understand.
    Do not use bullet points — write in short, flowing paragraphs.
    """

    response = model.generate_content(prompt)
    return response.text