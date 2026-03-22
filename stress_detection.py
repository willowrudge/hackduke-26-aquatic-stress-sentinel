import pandas as pd

# ── Stressor Functions ──────────────────────────────────────────────
def estimate_water_surface_temp(air_temp_c, altitude_m):
    """
    Estimates water surface temperature from air temperature
    readings taken at low altitude above the water surface.
    
    Based on atmospheric boundary layer thermal gradient.
    Correction factor: approximately 1.5°C per meter altitude.
    """
    correction = altitude_m * 1.5
    estimated_water_temp = air_temp_c + correction
    return round(estimated_water_temp, 2)

def fish_kill_risk(temp_c):
    """
    Freshwater
    Detects fish kill risk based on water surface temperature.
    Above 25c dissolved oxygen begins dropping for warmwater species.
    Above 29c dangerous for most freshwater fish.
    Above 32c mass fish kill territory.
    """
    if temp_c >= 32:
        return ("CRITICAL")
    elif temp_c >= 29:
        return ("WARNING")
    elif temp_c >= 25:
        return ("WATCH")
    else:
        return ("NORMAL")


def algal_bloom_risk(temp_c):
    """
    Freshwater + Marine
    Detects harmful algal bloom conditions.
    Uses temperature data to determine if the system is at risk of a harmful algal bloom.
    Conditions of 25c or above are at high risk of a bloom.
    """
    temp_risk = temp_c >= 25

    if temp_c >= 29:
        return ("CRITICAL")
    elif temp_c >= 25:
        return ("WARNING")
    elif temp_c >= 22:
        return ("WATCH")
    else:
        return ("NORMAL")


def coral_bleaching_risk(temp_c, baseline_temp):
    """
    Marine 
    Detects coral bleaching warnings.
    Coral bleaches when temps exceed seasonal baseline by 1c or more.
    """
    delta = temp_c - baseline_temp

    if delta >= 2:
        return ("CRITICAL")
    elif delta >= 1:
        return ("WARNING")
    elif delta >= 0.5:
        return ("WATCH")
    else:
        return ("NORMAL")


# ── Environment Router ──────────────────────────────────────────────

def analyze_csv(df, environment, baseline_temp=None):
    """
    Takes a cleaned dataframe and environment type.
    Returns the same dataframe with stressor columns added.

    environment: "freshwater" or "marine"
    baseline_temp: required for marine (pulled from NOAA API)
    """

    if environment == "freshwater":
        df["fish_kill_status"] = df["water_surface_temp_c"].apply(fish_kill_risk)
        df["algal_bloom_status"] = df["water_surface_temp_c"].apply(algal_bloom_risk)

    elif environment == "marine":
        if baseline_temp is None:
            raise ValueError("baseline_temp is required for marine environment.")

        df["coral_bleaching_status"] = df["water_surface_temp_c"].apply(
            lambda t: coral_bleaching_risk(t, baseline_temp))
        df["algal_bloom_status"] = df["water_surface_temp_c"].apply(algal_bloom_risk)

    return df


# ── CSV Ingestion ───────────────────────────────────────────────────
def normalize_columns(df):
    """
    Automatically renames columns to match expected names
    by detecting keywords in whatever column names the CSV has.
    Works for any dataset regardless of naming convention.
    """
    renamed = {}

    for col in df.columns:
        col_lower = col.lower().strip()

        if "temp" in col_lower or "air temperature" in col_lower:
            if "temperature_c" not in df.columns:
                renamed[col] = "temperature_c"

        elif any(x in col_lower for x in ["alt", "height", "elev"]) and "altitude_m" not in df.columns:
            renamed[col] = "altitude_m"

        elif any(x in col_lower for x in ["time", "date", "stamp"]) and "timestamp" not in df.columns:
            renamed[col] = "timestamp"

    if renamed:
        print(f"Auto-renamed columns: {renamed}")
        df = df.rename(columns=renamed)

    return df

def load_flight_data(csv_path):
    df = pd.read_csv(csv_path, comment="%")

    df = normalize_columns(df)

    if "altitude_m" not in df.columns:
        df["altitude_m"] = 1.0

    required_columns = {"timestamp", "temperature_c"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df = df.dropna(subset=["temperature_c"])

    df["water_surface_temp_c"] = df.apply(
        lambda row: estimate_water_surface_temp(
            row["temperature_c"], row["altitude_m"]), axis=1
    )

    return df

