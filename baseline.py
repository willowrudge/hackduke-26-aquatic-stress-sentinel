import requests

def get_nearest_noaa_station(lat, lon):
    """
    Finds the nearest NOAA CO-OPS station to a given lat/lon.
    Uses the NOAA metadata API to search by location.
    """
    url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    params = {
        "type": "waterlevels",
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        stations = response.json().get("stations", [])

        nearest = None
        min_distance = float("inf")

        for station in stations:
            s_lat = float(station["lat"])
            s_lon = float(station["lng"])

            # simple distance calculation
            distance = ((lat - s_lat) ** 2 + (lon - s_lon) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                nearest = station

        if nearest:
            print(f"📍 Nearest station: {nearest['name']} (ID: {nearest['id']})")
            return nearest["id"], nearest["name"]

        return None, None

    except Exception as e:
        print(f"❌ Station lookup failed: {e}")
        return None, None


def get_noaa_baseline(station_id):
    """
    Pulls recent sea surface temperature from a NOAA CO-OPS station.
    Returns average temp as baseline for coral bleaching comparison.
    """
    url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "station": station_id,
        "product": "water_temperature",
        "date": "recent",
        "units": "metric",
        "time_zone": "gmt",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "data" not in data:
            return None

        readings = data["data"]
        temps = [float(r["v"]) for r in readings if r["v"] not in ("", None)]

        if not temps:
            return None

        return round(sum(temps) / len(temps), 2)

    except Exception:
        return None
def get_baseline_for_location(lat, lon):
    """
    Master function — finds baseline temp for any location on earth.
    Tries NOAA first, falls back to Open-Meteo for non-US locations.
    """
    # try NOAA first
    station_id, station_name = get_nearest_noaa_station(lat, lon)

    if station_id:
        baseline = get_noaa_baseline(station_id)
        if baseline is not None:
            print(f"Baseline from {station_name}: {baseline}°C")
            return station_name, baseline

    # fallback to Open-Meteo for global coverage
    print("NOAA unavailable for this location — trying Open-Meteo...")
    baseline = get_open_meteo_baseline(lat, lon)

    if baseline is not None:
        return "Open-Meteo Marine API", baseline

    print("All baseline sources failed.")
    return None, None
def get_open_meteo_baseline(lat, lon):
    """
    Fallback for locations outside NOAA coverage (e.g. Great Barrier Reef).
    Uses Open-Meteo marine API — free, no API key, global coverage.
    Returns average sea surface temperature for the past 7 days.
    """
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "sea_surface_temperature",
        "past_days": 7,
        "timezone": "GMT"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        temps = [t for t in data["hourly"]["sea_surface_temperature"]
                 if t is not None]

        if not temps:
            return None

        baseline = round(sum(temps) / len(temps), 2)
        print(f"Baseline from Open-Meteo marine API: {baseline}°C")
        return baseline

    except Exception as e:
        print(f"Open-Meteo fallback failed: {e}")
        return None