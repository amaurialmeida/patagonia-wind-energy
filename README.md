# 🌬️ Patagonia Wind Energy Potential — Chile & Argentina

[![Streamlit App](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?logo=streamlit&logoColor=white)](https://patagonia-wind-energy.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: Academic](https://img.shields.io/badge/License-Academic-blue.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

🌐 **Languages:** English | [Português](README.pt-BR.md) | [Español](README.es.md)

**Independent Field Research — Wind Energy Potential Analysis**
Punta Arenas · Puerto Natales · Río Gallegos · Puerto Williams · Nov 2024–Oct 2025
**Author:** Amauri Almeida de Souza Junior

---

## ❓ Research Question

> "What is the real wind energy generation potential in the windiest cities of Patagonia, and how does direct field experience reinforce the scientific data on the strength and consistency of the region's Westerlies?"

**Answer:** The four cities studied show a combined installable wind potential exceeding 9,500 MW, driven by the uninterrupted Southern Hemisphere Westerlies — with capacity factors above 60%, nearly double the global average of ~35%. Eleven months living through those winds firsthand — gusts strong enough to make walking a straight line difficult, and a magnitude 7+ earthquake in Puerto Williams — turned the ERA5 reanalysis data from an abstraction into a lived, physical confirmation.

---

## 📊 Data Summary

| City | Country | Avg. Wind Speed | Max Gust | Installable Potential |
|---|---|---|---|---|
| Punta Arenas | 🇨🇱 Chile | 30.2 km/h | 130 km/h | 4,200 MW |
| Puerto Natales | 🇨🇱 Chile | 26.8 km/h | 104 km/h | 1,800 MW |
| Río Gallegos | 🇦🇷 Argentina | 27.1 km/h | 100 km/h | 3,500 MW |
| Puerto Williams | 🇨🇱 Chile | Screaming Sixties zone | — | Extreme wind reference point |

| Indicator | Value |
|---|---|
| Combined installable potential | 9,500+ MW |
| Typical Patagonian capacity factor | >60% (vs. ~35% global average) |
| Field research period | Nov 2024 – Oct 2025 (11 months) |
| Data source | Open-Meteo Historical API (ECMWF ERA5 reanalysis, 2020–2024) |
| Estimated CO₂ avoided at 20% buildout | ~700,000 t/year |

---

## 🔵 Key Findings

- **Punta Arenas — the windiest of the four cities** — average speed of 30.2 km/h and gusts up to 130 km/h give it the region's highest single-city potential (4,200 MW), positioning it as a possible clean-energy export hub.
- **Capacity factor above 60% — an exceptional global standard** — Argentine/Chilean Patagonia's wind capacity factor is more than double the global average, meaning each installed MW generates nearly twice the energy of a conventional wind region, making cost-per-MWh extraordinarily competitive.
- **The Westerlies — winds that have moved ships for centuries** — the Roaring Forties, Furious Fifties, and Screaming Sixties reach Patagonian cities with exceptional kinetic energy, unobstructed by land between the Pacific and South Atlantic.
- **Puerto Williams — wind at the end of the world** — field observation (Oct 2025) confirmed forceful Westerlies even in the world's southernmost permanent settlement; a magnitude 7+ earthquake on May 2, 2025 underscored the intensity of natural forces at play in this extreme region.
- **9,500+ MW combined — a sleeping giant** — for reference, all of Brazil had ~30 GW of installed wind capacity in 2024; three Patagonian cities alone already represent roughly 30% of that.
- **CO₂ avoidance as the decisive climate argument** — capturing just 20% of the combined potential (~1,900 MW installed) would avoid an estimated 700,000 t of CO₂ per year — equivalent to planting 50 million trees or removing 150,000 vehicles from Patagonian roads.

---

## ⚙️ The Physics of Wind

```
Power law        →  P/A = ½ × ρ × v³  (wind power density)
                     Velocity enters as a cube — doubling wind speed
                     yields 8× more energy

Air density       →  ~1.20 kg/m³ at sea level

Capacity factor   →  Patagonia: >60%  |  Global average: ~35%

Westerlies        →  40°S–60°S · virtually unobstructed over open ocean
                     "Roaring Forties," "Furious Fifties," "Screaming Sixties"
```

---

## 🔬 Methodology

```
Data collection   →  Hourly wind speed/direction for Punta Arenas, Puerto
                      Natales, and Río Gallegos via the Open-Meteo Historical
                      API (ECMWF ERA5 reanalysis) — 5 full years, processed
                      into monthly/annual averages and directional
                      distributions

Field experience   →  11 months across the four cities studied: Punta Arenas
                      (Nov 2024), Puerto Natales (Dec 2024), Río Gallegos
                      (Mar 2025), Puerto Williams (through Oct 2025) — direct
                      exposure to Westerlies gusts and a documented M7+
                      earthquake in Puerto Williams (May 2, 2025)

Wind physics       →  Cubic power law (P/A = ½ρv³) applied to observed speed
                      distributions to estimate energy density

Turbine simulator   →  GWh/year = P_turbine × N_turbines × Capacity_Factor ×
                      8,760h; interactive controls for turbine count (1–500)
                      and unit power (2–8 MW), auto-calculating households
                      served and CO₂ avoided using regional grid emission
                      factors

Directional analysis →  Wind rose distribution to identify dominant sectors
                      (WSW–W–WNW) for optimal turbine placement and offshore
                      wind farm design

Impact estimation   →  Installable potential aggregated per city; combined
                      generation modeled against regional gas-thermal
                      displacement and CO₂ avoidance
```

---

## 🖥️ Dashboard Overview

The Streamlit app is organized into five tabs:

1. **🗺️ Map & Analysis** — interactive map with city markers sized by wind speed, monthly/annual wind speed trends (2020–2024), and a directional wind rose.
2. **🔬 Methodology & Pipeline** — the six-step research pipeline, wind physics reference, and an interactive turbine generation simulator with real-time GWh/CO₂/households-served calculations.
3. **💡 What We Found** — the six key findings above, plus the project's conclusion.
4. **📷 In the Field** — first-hand field photos and notes from each of the four cities, including exact coordinates, measured wind speed, and installable potential per location.
5. **📚 Sources & Credits** — data sources (Open-Meteo, ERA5, Global Wind Atlas) and author credentials.

The full interface — labels, chart titles, and narrative text — is natively trilingual (PT/EN/ES), switchable from the sidebar.

---

## 🛠️ Tech Stack

| Technology | Use |
|---|---|
| Python 3.11 | Core language |
| Streamlit | Dashboard framework |
| Folium + streamlit-folium | Interactive geospatial city mapping |
| Plotly (Express & Graph Objects) | Wind trend, wind rose, and capacity-factor charts |
| Pandas / NumPy | Data processing and physics calculations |
| Pillow (PIL) | Field photo handling |
| Open-Meteo API (ERA5) | Historical wind reanalysis data |

---

## 📁 Repository Structure

```
patagonia-wind-energy/
├── app.py                    # Main dashboard (5 tabs, PT/EN/ES, turbine simulator)
├── requirements.txt          # Python dependencies
├── README.md                   # This file (English)
├── README.pt-BR.md             # Portuguese version
├── README.es.md                # Spanish version
└── assets/
    └── campo/                 # Field photos
        ├── 01_punta_arenas_nov2024.JPG
        ├── 02_puerto_natales_dez2024.JPG
        ├── 03_rio_gallegos_mar2025.jpg
        └── 04_puerto_williams_out2025.jpg
```

---

## 🚀 Run Locally

```bash
# Clone the repository
git clone https://github.com/amaurialmeida/patagonia-wind-energy.git
cd patagonia-wind-energy

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

---

## 🌐 Live App

🔗 **[patagonia-wind-energy.streamlit.app](https://patagonia-wind-energy.streamlit.app/)**

Available in 🇧🇷 Portuguese, 🇺🇸 English, and 🇪🇸 Spanish.

---

## 📚 References

- Open-Meteo Historical Weather API — ECMWF ERA5 reanalysis dataset.
- Global Wind Atlas (GWA) — regional wind resource benchmarking.

---

## 🔗 Academic / Professional Links

| Platform | Link |
|---|---|
| Lattes | http://lattes.cnpq.br/9545242042800090 |
| Escavador | https://www.escavador.com/sobre/8577779/amauri-almeida-de-souza-junior |

---

## 🌿 Environmental Portfolio

This project is part of the author's environmental research and data science portfolio.
🔗 [amaurialmeida.github.io/environmental-portfolio](https://amaurialmeida.github.io/environmental-portfolio)

---

© 2024–2026 · Amauri Almeida de Souza Junior · Independent Field Research · Portfolio Project
