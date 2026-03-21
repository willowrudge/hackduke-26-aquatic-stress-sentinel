## 🌊 Aquatic Stress Sentinel
Aquatic Stress Sentinel, a drone-based microclimate sensing system for early detection of aquatic ecosystem stress.

## Description
Aquatic Stress Sentinel is a low-altitude drone system that collects real-time temperature and humidity readings at the air-water interface, geotags each reading, and compares it against USGS and NOAA baseline data to generate a tiered stress risk score for any body of water.
Water surface temperature is an important variable in identify stressors in aquatic ecosystems. When it shifts, even by a single degree, it can have large impacts on the ecosystem as a whole. Current monitoring infrastructure relies on satellites (low resolution, infrequent passes) or expensive fixed buoys. Neither can provide the hyperlocal, on-demand data that conservationists and regulators need to act before damage is done.

Detected stressors include:
| Stressor | Ecosystem | Threshold |
|---|---|---|
| Fish Kill Risk | Freshwater | >29°C Warning, >32°C Critical |
| Harmful Algal Bloom | Freshwater, Marine | >24°C |
| Coral Bleaching | Marine | >1°C above seasonal baseline |

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
**Requirements:**
- Python 3.10+
- pip

**Steps:**

1. Clone the repository:
```bash
git clone https://coursework.cs.duke.edu/wjr20/hackduke-2026.git
cd hackduke-2026
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run webapp.py
```

**Dependencies:**

pandas
requests
streamlit
folium
streamlit-folium

## Usage
1. Place your drone's CSV flight log in the project folder. It should follow this format:
```csv
timestamp,lat,lon,temperature_c,humidity_pct,altitude_m
2026-03-22T09:15:01Z,36.0014,-78.9382,21.8,68.4,1.0
2026-03-22T09:15:06Z,36.0018,-78.9379,22.1,69.2,1.0
```

2. Run the Streamlit dashboard:
```bash
streamlit run webapp.py
```

3. In the sidebar:
   - Select **Freshwater** or **Marine** depending on where the drone flew
   - Upload your drone CSV file

4. The dashboard will automatically:
   - Apply a boundary layer thermal correction to estimate water surface temperature from air temperature readings
   - Pull NOAA baseline sea surface temperature for marine mode
   - Run stressor analysis on every reading
   - Display risk status tables

## Roadmap
- **Live telemetry** — stream CSV data in real-time via MQTT during flight
- **Interactive map** — plot flight path with color-coded risk overlays using Folium
- **Mobile companion app** — view stress map live from a phone during flight
- **Multi-flight comparison** — overlay historical flights to track ecosystem change over time
- **Expanded sensor suite** — pH, turbidity, and chlorophyll sensors for deeper water quality analysis
- **Calibrated thermal correction** — refine the boundary layer correction against a submerged reference sensor

## Contributing
This project was built as a hackathon prototype and we welcome contributions. If you'd like to contribute:

Fork the repository
Create a feature branch (git checkout -b feature/your-feature)
Commit your changes and open a pull request

Please open an issue first to discuss major changes.

## Team
Built at HackDuke: Code For Good 2026

- **Willow Rudge** — Software, data pipeline, dashboard
- **Niko Weaver** — Hardware, drone build, firmware

## Authors and acknowledgment
Big thank you to HackDuke for organizing and to NOAA and USGS for providing free public APIs that made the baseline comparison system possible.

## License
MIT License — free to use, modify, and build on.

## Project status
Actively developed as a hackathon prototype. Core functionality is complete: stressor detection, NOAA baseline comparison, and boundary layer thermal correction are all working.