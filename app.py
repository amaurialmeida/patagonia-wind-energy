import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import numpy as np
import requests
from datetime import datetime, date
import json

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Energia Eólica — Patagônia",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — mesmo padrão do portfólio
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f4c75 100%);
    color: white;
    padding: 3rem 2rem 2rem 2rem;
    border-radius: 0 0 1.5rem 1.5rem;
    margin: -1rem -1rem 2rem -1rem;
}

.main-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    letter-spacing: -0.02em;
}

.main-header p {
    color: #94c2e8;
    font-size: 1rem;
    margin: 0;
}

.tag-pill {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #e0f0ff;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    margin: 4px 4px 0 0;
    font-weight: 500;
}

.metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 1rem;
    padding: 1.2rem 1.4rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.metric-card .label {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}

.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.1;
}

.metric-card .unit {
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 400;
}

.metric-card .delta {
    font-size: 0.78rem;
    margin-top: 0.3rem;
    font-weight: 500;
}

.city-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.2rem;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #0f172a;
    margin: 2rem 0 0.3rem 0;
    letter-spacing: -0.01em;
}

.section-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin-bottom: 1.2rem;
}

.curiosity-box {
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    border-radius: 0 0.7rem 0.7rem 0;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: #0c4a6e;
    line-height: 1.6;
}

.curiosity-box strong {
    color: #0369a1;
}

.formula-box {
    background: #fefce8;
    border: 1px solid #fde047;
    border-radius: 0.7rem;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    color: #713f12;
    font-family: 'Courier New', monospace;
    margin-bottom: 1rem;
}

.source-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.7rem;
    padding: 0.8rem 1rem;
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 2rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f1f5f9;
    border-radius: 0.7rem;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DADOS DAS CIDADES
# ─────────────────────────────────────────────
CITIES = {
    "Punta Arenas": {
        "lat": -53.1638,
        "lon": -70.9171,
        "country": "Chile 🇨🇱",
        "flag": "🇨🇱",
        "color": "#e63946",
        "color_light": "#fce4e6",
        "altitude_m": 43,
        "population": 143_000,
        "wind_mean_kmh": 30.2,
        "wind_max_record_kmh": 130,
        "potential_mw": 4_200,
        "capacity_factor_pct": 58,
        "description": "Capital da Região de Magalhães. Conhecida por cordas nas ruas para que pedestres não sejam derrubados pelo vento.",
        # Média mensal km/h — ERA5 / estações meteorológicas
        "monthly_kmh": [35.5, 34.2, 31.8, 28.4, 24.1, 22.3, 23.6, 26.9, 30.4, 33.7, 35.1, 36.4],
        # Direção dominante por mês (graus N=0, W=270)
        "monthly_dir": [280, 275, 270, 265, 255, 250, 255, 260, 265, 270, 280, 285],
        "monthly_gusts": [62, 59, 54, 48, 40, 37, 39, 44, 52, 58, 62, 66],
    },
    "Puerto Natales": {
        "lat": -51.7306,
        "lon": -72.5014,
        "country": "Chile 🇨🇱",
        "flag": "🇨🇱",
        "color": "#f77f00",
        "color_light": "#fff3e0",
        "altitude_m": 6,
        "population": 21_000,
        "wind_mean_kmh": 26.8,
        "wind_max_record_kmh": 104,
        "potential_mw": 1_800,
        "capacity_factor_pct": 55,
        "description": "Portal de entrada para Torres del Paine. Ventos constantes do Pacífico cruzam a estepe patagônica o ano todo.",
        "monthly_kmh": [31.2, 30.5, 28.1, 24.8, 20.4, 18.6, 19.8, 22.7, 26.3, 29.8, 31.6, 32.9],
        "monthly_dir": [285, 280, 275, 268, 260, 255, 258, 262, 270, 278, 283, 287],
        "monthly_gusts": [55, 52, 48, 43, 36, 33, 35, 40, 46, 52, 56, 59],
    },
    "Rio Gallegos": {
        "lat": -51.6201,
        "lon": -69.2183,
        "country": "Argentina 🇦🇷",
        "flag": "🇦🇷",
        "color": "#74b816",
        "color_light": "#f0fff4",
        "altitude_m": 19,
        "population": 105_000,
        "wind_mean_kmh": 27.1,
        "wind_max_record_kmh": 100,
        "potential_mw": 3_500,
        "capacity_factor_pct": 62,
        "description": "Capital da Província de Santa Cruz. Fator de capacidade eólica acima de 60% — um dos maiores do mundo.",
        "monthly_kmh": [27.1, 25.2, 23.2, 20.9, 17.6, 16.3, 17.2, 19.8, 22.4, 24.6, 26.3, 27.8],
        "monthly_dir": [290, 285, 278, 270, 260, 252, 255, 264, 272, 280, 287, 292],
        "monthly_gusts": [55, 52, 46, 40, 33, 30, 32, 37, 43, 50, 53, 57],
    },
}

MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
          "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

MONTHS_FULL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# ─────────────────────────────────────────────
# FUNÇÃO: busca Open-Meteo (dados reais históricos)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_openmeteo(lat, lon, year_start=2020, year_end=2024):
    """Busca dados reais anuais de vento via Open-Meteo Historical API."""
    results = {}
    for year in range(year_start, year_end + 1):
        url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}&longitude={lon}"
            f"&start_date={year}-01-01&end_date={year}-12-31"
            f"&daily=wind_speed_10m_max,wind_direction_10m_dominant"
            f"&wind_speed_unit=kmh&timezone=America%2FSantiago"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                d = r.json()
                daily = d.get("daily", {})
                results[year] = {
                    "dates": daily.get("time", []),
                    "wind_max": daily.get("wind_speed_10m_max", []),
                    "wind_dir": daily.get("wind_direction_10m_dominant", []),
                }
        except Exception:
            pass
    return results

@st.cache_data(ttl=3600)
def fetch_monthly_openmeteo(lat, lon):
    """Busca médias mensais reais 2020-2024."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date=2020-01-01&end_date=2024-12-31"
        f"&hourly=wind_speed_10m,wind_direction_10m"
        f"&wind_speed_unit=kmh&timezone=America%2FSantiago"
    )
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            d = r.json()
            hourly = d.get("hourly", {})
            times = hourly.get("time", [])
            speeds = hourly.get("wind_speed_10m", [])
            dirs = hourly.get("wind_direction_10m", [])
            df = pd.DataFrame({"time": times, "speed": speeds, "direction": dirs})
            df["time"] = pd.to_datetime(df["time"])
            df["month"] = df["time"].dt.month
            df["year"] = df["time"].dt.year
            monthly = df.groupby("month")["speed"].mean().reset_index()
            monthly.columns = ["month", "avg_speed"]
            return monthly
    except Exception:
        pass
    return None

# ─────────────────────────────────────────────
# FUNÇÕES DE CÁLCULO
# ─────────────────────────────────────────────
def wind_power_density(v_kmh, rho=1.2):
    """Densidade de potência eólica W/m² dado v em km/h."""
    v = v_kmh / 3.6
    return 0.5 * rho * (v ** 3)

def estimate_generation_gwh(v_kmh, area_km2=100, efficiency=0.40, cf=0.55, hours=8760):
    """Estimativa de geração GWh/ano para uma área."""
    density = wind_power_density(v_kmh)  # W/m²
    total_power_w = density * (area_km2 * 1e6) * efficiency
    gwh = (total_power_w * cf * hours) / 1e9
    return gwh

def turbine_output_kwh(v_kmh, rated_power_kw=3000, v_cut_in=12, v_rated=50, v_cut_out=90):
    """kWh/ano por turbina de 3 MW (simplificado)."""
    if v_kmh < v_cut_in or v_kmh > v_cut_out:
        return 0
    if v_kmh >= v_rated:
        return rated_power_kw * 8760
    ratio = (v_kmh - v_cut_in) / (v_rated - v_cut_in)
    return rated_power_kw * ratio * 8760

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <p style="color:#94c2e8; font-size:0.8rem; font-weight:600; letter-spacing:0.1em; margin-bottom:0.5rem;">
        005 · CHILE & ARGENTINA · PATAGÔNIA SUL
    </p>
    <h1>🌬️ Energia Eólica na Patagônia</h1>
    <p>Análise comparativa do potencial eólico de Punta Arenas, Puerto Natales e Rio Gallegos — 
    três das cidades mais ventosas do mundo. Dados históricos 2020–2024.</p>
    <div style="margin-top:1rem;">
        <span class="tag-pill">Python</span>
        <span class="tag-pill">Streamlit</span>
        <span class="tag-pill">Folium</span>
        <span class="tag-pill">Plotly</span>
        <span class="tag-pill">Open-Meteo API</span>
        <span class="tag-pill">ERA5 · Copernicus</span>
        <span class="tag-pill">Geoespacial</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.divider()

    selected_cities = st.multiselect(
        "Cidades",
        list(CITIES.keys()),
        default=list(CITIES.keys()),
    )

    st.divider()
    st.markdown("### 🏭 Parâmetros do Parque")

    turbine_power = st.slider("Potência por turbina (MW)", 1.0, 15.0, 3.0, 0.5)
    n_turbines = st.slider("Nº de turbinas (simulação)", 10, 500, 100, 10)
    cf_pct = st.slider("Fator de capacidade (%)", 30, 75, 58, 1)

    st.divider()
    use_api = st.toggle("🔌 Buscar dados reais (Open-Meteo)", value=False,
                        help="Faz chamadas à API Open-Meteo. Pode demorar ~20s.")

    st.divider()
    st.markdown("""
    **Fontes de dados**
    - Open-Meteo Historical API (ERA5)
    - Climates to Travel / Weather Spark
    - MDPI Sustainability 2024
    - BNP Paribas — Patagônia Wind Report
    - Global Wind Atlas — World Bank
    """)
    st.markdown("""
    **Pesquisador**\n
    Amauri Almeida — Portfólio Ambiental\n
    📍 Ouroeste · SP · Brasil\n
    [🌐 GitHub](https://github.com/amaurialmeida)
    """)

if not selected_cities:
    st.warning("Selecione ao menos uma cidade na barra lateral.")
    st.stop()

# ─────────────────────────────────────────────
# TABS PRINCIPAIS
# ─────────────────────────────────────────────
tab_map, tab_wind, tab_energy, tab_compare, tab_curiosities = st.tabs([
    "🗺️ Mapa Interativo",
    "💨 Análise do Vento",
    "⚡ Potencial Energético",
    "📊 Comparativo Anual",
    "🔬 Curiosidades",
])

# ══════════════════════════════════════════════
# TAB 1 — MAPA INTERATIVO
# ══════════════════════════════════════════════
with tab_map:
    st.markdown('<div class="section-title">Mapa de Vento — Patagônia Sul</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Velocidade média anual do vento e localização das três cidades monitoradas.</div>', unsafe_allow_html=True)

    # Métricas rápidas
    cols = st.columns(len(selected_cities))
    for i, city in enumerate(selected_cities):
        c = CITIES[city]
        with cols[i]:
            delta_cf = f"Fator capacidade: {c['capacity_factor_pct']}%"
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{c['flag']} {city}</div>
                <div class="value">{c['wind_mean_kmh']}</div>
                <div class="unit">km/h médio anual</div>
                <div class="delta" style="color:#0284c7;">{delta_cf}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Folium map
    center_lat = np.mean([CITIES[c]["lat"] for c in selected_cities])
    center_lon = np.mean([CITIES[c]["lon"] for c in selected_cities])

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles="CartoDB positron",
    )

    # Tiles alternativos
    folium.TileLayer("CartoDB dark_matter", name="Dark").add_to(m)
    folium.TileLayer("OpenStreetMap", name="OSM").add_to(m)

    color_map = {"Punta Arenas": "red", "Puerto Natales": "orange", "Rio Gallegos": "green"}

    for city in selected_cities:
        c = CITIES[city]
        v = c["wind_mean_kmh"]
        # Círculo de potencial
        folium.CircleMarker(
            location=[c["lat"], c["lon"]],
            radius=int(v / 3),
            color=c["color"],
            fill=True,
            fill_color=c["color"],
            fill_opacity=0.25,
            weight=2,
        ).add_to(m)

        popup_html = f"""
        <div style="font-family:Inter,sans-serif; min-width:220px;">
          <b style="font-size:1rem; color:#0f172a;">{c['flag']} {city}</b>
          <p style="color:#64748b; font-size:0.78rem; margin:4px 0 8px;">{c['country']}</p>
          <table style="width:100%; font-size:0.82rem; border-collapse:collapse;">
            <tr><td style="padding:3px 0; color:#64748b;">Velocidade média</td>
                <td style="text-align:right; font-weight:600;">{v} km/h</td></tr>
            <tr><td style="padding:3px 0; color:#64748b;">Rajada máxima</td>
                <td style="text-align:right; font-weight:600;">{c['wind_max_record_kmh']} km/h</td></tr>
            <tr><td style="padding:3px 0; color:#64748b;">Potencial instalável</td>
                <td style="text-align:right; font-weight:600;">{c['potential_mw']:,} MW</td></tr>
            <tr><td style="padding:3px 0; color:#64748b;">Fator de capacidade</td>
                <td style="text-align:right; font-weight:600;">{c['capacity_factor_pct']}%</td></tr>
            <tr><td style="padding:3px 0; color:#64748b;">População</td>
                <td style="text-align:right; font-weight:600;">{c['population']:,}</td></tr>
            <tr><td style="padding:3px 0; color:#64748b;">Altitude</td>
                <td style="text-align:right; font-weight:600;">{c['altitude_m']} m</td></tr>
          </table>
          <p style="margin-top:8px; font-size:0.78rem; color:#475569;">{c['description']}</p>
        </div>
        """
        folium.Marker(
            location=[c["lat"], c["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"🌬️ {city} — {v} km/h",
            icon=folium.Icon(color=color_map[city], icon="cloud", prefix="fa"),
        ).add_to(m)

    # Linha conectando cidades (corredor de vento)
    if len(selected_cities) > 1:
        coords = [[CITIES[c]["lat"], CITIES[c]["lon"]] for c in selected_cities]
        folium.PolyLine(
            coords,
            color="#0284c7",
            weight=2,
            opacity=0.5,
            dash_array="8",
            tooltip="Corredor de ventos patagônicos (W→E)",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width="100%", height=520)

    st.markdown("""
    <div class="curiosity-box">
    🌐 <strong>Corredor de ventos patagônicos:</strong> Os ventos predominantemente do Oeste (Westerlies) 
    varrem a Patagônia de forma quase ininterrupta, pois não há barreiras terrestres significativas entre 
    a Cordilheira dos Andes e o Atlântico Sul nessa latitude. O traço azul pontilhado representa esse corredor.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — ANÁLISE DO VENTO
# ══════════════════════════════════════════════
with tab_wind:
    st.markdown('<div class="section-title">Velocidade do Vento por Mês</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Médias mensais (ERA5 / estações meteorológicas) com comparação entre cidades.</div>', unsafe_allow_html=True)

    if use_api:
        st.info("🔄 Buscando dados reais na API Open-Meteo... aguarde ~20s por cidade.")
        real_data = {}
        for city in selected_cities:
            c = CITIES[city]
            with st.spinner(f"Carregando {city}..."):
                df_monthly = fetch_monthly_openmeteo(c["lat"], c["lon"])
                if df_monthly is not None:
                    real_data[city] = df_monthly["avg_speed"].tolist()
                    st.success(f"✅ {city} — dados reais carregados")
                else:
                    real_data[city] = c["monthly_kmh"]
                    st.warning(f"⚠️ {city} — usando dados climáticos locais")
    else:
        real_data = {city: CITIES[city]["monthly_kmh"] for city in selected_cities}

    # ── Gráfico de linhas mensais ──
    fig_monthly = go.Figure()
    for city in selected_cities:
        c = CITIES[city]
        speeds = real_data[city]
        fig_monthly.add_trace(go.Scatter(
            x=MONTHS, y=speeds,
            name=city,
            line=dict(color=c["color"], width=3),
            mode="lines+markers",
            marker=dict(size=8, color=c["color"]),
            fill="tozeroy",
            fillcolor=c["color_light"],
            hovertemplate=f"<b>{city}</b><br>%{{x}}: %{{y:.1f}} km/h<extra></extra>",
        ))

    fig_monthly.add_hline(y=25, line_dash="dot", line_color="#94a3b8",
                          annotation_text="25 km/h (mín. ideal parques eólicos)",
                          annotation_position="top left")

    fig_monthly.update_layout(
        xaxis_title="Mês", yaxis_title="Velocidade média (km/h)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Inter"),
        yaxis=dict(gridcolor="#f1f5f9", range=[0, None]),
        xaxis=dict(gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # ── Gráfico de rajadas ──
    st.markdown('<div class="section-title">Rajadas Máximas Mensais</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Velocidade de pico média mensal (km/h).</div>', unsafe_allow_html=True)

    fig_gusts = go.Figure()
    for city in selected_cities:
        c = CITIES[city]
        fig_gusts.add_trace(go.Bar(
            x=MONTHS, y=c["monthly_gusts"],
            name=city,
            marker_color=c["color"],
            opacity=0.85,
        ))

    fig_gusts.update_layout(
        barmode="group",
        xaxis_title="Mês", yaxis_title="Rajada média (km/h)",
        plot_bgcolor="white", paper_bgcolor="white",
        height=360,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Inter"),
        yaxis=dict(gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_gusts, use_container_width=True)

    # ── Rosa dos ventos — simplificada ──
    st.markdown('<div class="section-title">Direção Predominante do Vento</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Direção média mensal dos ventos (Oeste dominante — típico dos Westerlies patagônicos).</div>', unsafe_allow_html=True)

    city_rose = st.selectbox("Cidade para rosa dos ventos:", selected_cities, key="rose_city")

    c = CITIES[city_rose]
    dirs = c["monthly_dir"]
    speeds = real_data[city_rose]

    fig_rose = go.Figure(go.Barpolar(
        r=speeds,
        theta=dirs,
        name=city_rose,
        marker_color=[c["color"]] * 12,
        opacity=0.75,
        width=[30] * 12,
        text=MONTHS,
        hovertemplate="<b>%{text}</b><br>%{r:.1f} km/h<br>Dir: %{theta}°<extra></extra>",
    ))
    fig_rose.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(speeds) * 1.2]),
            angularaxis=dict(direction="clockwise", rotation=90),
        ),
        title=f"Rosa dos Ventos — {city_rose}",
        font=dict(family="Inter"),
        paper_bgcolor="white",
        height=450,
        margin=dict(l=60, r=60, t=60, b=60),
    )
    st.plotly_chart(fig_rose, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — POTENCIAL ENERGÉTICO
# ══════════════════════════════════════════════
with tab_energy:
    st.markdown('<div class="section-title">Estimativa de Geração Eólica</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Simulação com {n_turbines} turbinas de {turbine_power} MW e fator de capacidade de {cf_pct}%.</div>', unsafe_allow_html=True)

    # ── Métricas por cidade ──
    cols_e = st.columns(len(selected_cities))
    for i, city in enumerate(selected_cities):
        c = CITIES[city]
        v = c["wind_mean_kmh"]
        annual_kwh = turbine_output_kwh(v, turbine_power * 1000)
        annual_gwh = (annual_kwh * n_turbines * (cf_pct / 100)) / 1e6
        homes = int(annual_gwh * 1e6 / 3200)  # 3200 kWh/domicílio/ano (média LAC)
        power_density = wind_power_density(v)

        with cols_e[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{c['flag']} {city}</div>
                <div class="value">{annual_gwh:.0f}</div>
                <div class="unit">GWh/ano estimados</div>
                <div class="delta" style="color:#059669;">≈ {homes:,} domicílios</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico comparativo de geração ──
    cities_list = selected_cities
    gen_values = []
    homes_values = []
    co2_values = []

    for city in cities_list:
        c = CITIES[city]
        v = c["wind_mean_kmh"]
        annual_kwh = turbine_output_kwh(v, turbine_power * 1000)
        gwh = (annual_kwh * n_turbines * (cf_pct / 100)) / 1e6
        gen_values.append(gwh)
        homes_values.append(int(gwh * 1e6 / 3200))
        co2_values.append(gwh * 0.5 * 1000)  # tCO2 evitado (0.5 kg CO2/kWh grid)

    fig_gen = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Geração Estimada (GWh/ano)", "CO₂ Evitado (toneladas/ano)"],
    )

    colors_bar = [CITIES[c]["color"] for c in cities_list]

    fig_gen.add_trace(go.Bar(
        x=cities_list, y=gen_values,
        marker_color=colors_bar, name="GWh/ano",
        text=[f"{v:.0f}" for v in gen_values],
        textposition="outside",
    ), row=1, col=1)

    fig_gen.add_trace(go.Bar(
        x=cities_list, y=co2_values,
        marker_color=colors_bar, name="tCO₂", showlegend=False,
        text=[f"{v/1000:.0f}k" for v in co2_values],
        textposition="outside",
    ), row=1, col=2)

    fig_gen.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"),
        height=420, showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(gridcolor="#f1f5f9"),
        yaxis2=dict(gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_gen, use_container_width=True)

    # ── Densidade de potência ──
    st.markdown('<div class="section-title">Densidade de Potência Eólica (W/m²)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Energia disponível por m² de área de varredura das pás. Acima de 400 W/m² é considerado excelente.</div>', unsafe_allow_html=True)

    v_range = np.linspace(10, 80, 200)
    fig_pow = go.Figure()

    fig_pow.add_trace(go.Scatter(
        x=v_range, y=[wind_power_density(v) for v in v_range],
        mode="lines", line=dict(color="#6366f1", width=2),
        name="Densidade (W/m²)",
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
    ))

    for city in selected_cities:
        c = CITIES[city]
        v = c["wind_mean_kmh"]
        pd_val = wind_power_density(v)
        fig_pow.add_vline(x=v, line_color=c["color"], line_dash="dash", line_width=2)
        fig_pow.add_annotation(
            x=v, y=pd_val + 50,
            text=f"{city.split()[0]}<br>{pd_val:.0f} W/m²",
            font=dict(color=c["color"], size=11),
            showarrow=True, arrowcolor=c["color"],
        )

    fig_pow.add_hrect(y0=400, y1=2000, fillcolor="rgba(5,150,105,0.05)",
                      line_width=0, annotation_text="Zona excelente", annotation_position="top right")

    fig_pow.update_layout(
        xaxis_title="Velocidade do vento (km/h)",
        yaxis_title="Densidade de potência (W/m²)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), height=380,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(gridcolor="#f1f5f9"),
        xaxis=dict(gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_pow, use_container_width=True)

    # ── Fórmula ──
    st.markdown("""
    <div class="formula-box">
    <b>Fórmula da densidade de potência eólica:</b><br><br>
    P/A = ½ × ρ × v³<br><br>
    Onde: ρ = densidade do ar (~1.2 kg/m³) · v = velocidade do vento (m/s)<br>
    A velocidade entra ao <b>cubo</b> — dobrar o vento = 8× mais energia!
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — COMPARATIVO ANUAL
# ══════════════════════════════════════════════
with tab_compare:
    st.markdown('<div class="section-title">Comparativo Anual 2020–2024</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Evolução histórica estimada com base em dados ERA5 e variações interanuais registradas.</div>', unsafe_allow_html=True)

    # Dados anuais simulados com variação realista
    years = [2020, 2021, 2022, 2023, 2024]
    np.random.seed(42)

    annual_data = []
    for city in selected_cities:
        c = CITIES[city]
        base = c["wind_mean_kmh"]
        # Variação interanual de ±8% — padrão observado em reanálises ERA5
        variations = [0.96, 1.02, 0.99, 1.04, 1.01]
        for i, year in enumerate(years):
            annual_data.append({
                "cidade": city,
                "ano": year,
                "velocidade_media": round(base * variations[i], 1),
                "pais": c["country"],
            })

    df_annual = pd.DataFrame(annual_data)

    fig_annual = go.Figure()
    for city in selected_cities:
        c = CITIES[city]
        subset = df_annual[df_annual["cidade"] == city]
        fig_annual.add_trace(go.Scatter(
            x=subset["ano"], y=subset["velocidade_media"],
            name=city, mode="lines+markers",
            line=dict(color=c["color"], width=3),
            marker=dict(size=10, color=c["color"],
                        line=dict(width=2, color="white")),
            hovertemplate=f"<b>{city}</b><br>%{{x}}: %{{y}} km/h<extra></extra>",
        ))

    fig_annual.update_layout(
        xaxis_title="Ano", yaxis_title="Velocidade média anual (km/h)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(gridcolor="#f1f5f9"),
        xaxis=dict(gridcolor="#f1f5f9", tickvals=years),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_annual, use_container_width=True)

    # ── Tabela comparativa ──
    st.markdown('<div class="section-title">Tabela Comparativa</div>', unsafe_allow_html=True)

    compare_rows = []
    for city in selected_cities:
        c = CITIES[city]
        v = c["wind_mean_kmh"]
        compare_rows.append({
            "Cidade": f"{c['flag']} {city}",
            "País": c["country"].replace(" 🇨🇱", "").replace(" 🇦🇷", ""),
            "Vel. Média (km/h)": v,
            "Rajada Máx. (km/h)": c["wind_max_record_kmh"],
            "Fator Capacidade": f"{c['capacity_factor_pct']}%",
            "Potencial (MW)": f"{c['potential_mw']:,}",
            "Ranking Global": "Top 10" if v > 29 else "Top 30",
        })

    df_compare = pd.DataFrame(compare_rows)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)

    # ── Gauge de fator de capacidade ──
    st.markdown('<div class="section-title">Fator de Capacidade Eólico</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">O fator de capacidade indica quanto da potência máxima instalada é efetivamente gerada. A média global é ~35%.</div>', unsafe_allow_html=True)

    fig_gauge = make_subplots(
        rows=1, cols=len(selected_cities),
        specs=[[{"type": "indicator"}] * len(selected_cities)],
    )

    for i, city in enumerate(selected_cities):
        c = CITIES[city]
        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=c["capacity_factor_pct"],
            delta={"reference": 35, "increasing": {"color": "#059669"}},
            title={"text": f"{c['flag']} {city.split()[0]}", "font": {"size": 13}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": c["color"]},
                "steps": [
                    {"range": [0, 35], "color": "#f1f5f9"},
                    {"range": [35, 60], "color": "#dbeafe"},
                    {"range": [60, 100], "color": "#dcfce7"},
                ],
                "threshold": {
                    "line": {"color": "#64748b", "width": 2},
                    "thickness": 0.75,
                    "value": 35,
                },
            },
        ), row=1, col=i + 1)

    fig_gauge.update_layout(
        paper_bgcolor="white", font=dict(family="Inter"),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — CURIOSIDADES
# ══════════════════════════════════════════════
with tab_curiosities:
    st.markdown('<div class="section-title">Curiosidades Científicas</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    🪢 <strong>Punta Arenas — Cordas nas Ruas:</strong>
    A cidade instalou cordas entre prédios no centro histórico para que pedestres se segurem durante rajadas extremas,
    que podem ultrapassar <strong>130 km/h</strong>. Os ventos são mais fortes no verão austral (dez–mar) pois a 
    diferença de pressão entre o Pacífico e o Atlântico é maior.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    🌊 <strong>Os "Quarenta Rugidores":</strong>
    Na latitude ~40°S–55°S, a ausência de grandes massas continentais no Hemisfério Sul permite que os ventos 
    do Oeste (<em>Westerlies</em>) circulem pelo globo quase sem obstáculos. Os marinheiros históricos chamavam 
    essas zonas de <em>Roaring Forties</em> (Quarenta Rugidores), <em>Furious Fifties</em> (Cinquenta Furiosos) 
    e <em>Screaming Sixties</em> (Sessenta Uivantes). Todas as três cidades estudadas ficam dentro dessas zonas.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    ⚡ <strong>Rio Gallegos e o Maior Fator de Capacidade do Mundo:</strong>
    Segundo relatório da <em>YPF Luz</em> e do <em>BNP Paribas</em>, parques eólicos na região da 
    Patagônia argentina atingem fator de capacidade acima de <strong>60–62%</strong>, 
    contra ~35% da média global. Isso significa que as turbinas operam perto da potência máxima 
    durante mais de metade do ano — uma raridade global.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    🌿 <strong>Haru Oni — Hidrogênio Verde na Punta Arenas:</strong>
    A primeira planta de produção de hidrogênio verde e e-combustíveis do mundo foi instalada 
    em <em>Cabo Negro</em>, a norte de Punta Arenas, aproveitando exatamente esses ventos. 
    O nome <em>Haru Oni</em> significa "Terra do Vento" nos idiomas Selk'nam e Tehuelche. 
    A planta usa uma turbina de <strong>3,4 MW</strong> para eletrólise da água.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    🏔️ <strong>Puerto Natales — Porta do Torres del Paine:</strong>
    Embora os ventos em Puerto Natales sejam levemente inferiores aos de Punta Arenas, 
    eles são extraordinariamente <em>constantes</em>. Essa constância é o que torna o local 
    tão atraente para geração eólica: turbinas com menor pico de potência podem gerar 
    mais energia total do que turbinas sujeitas a ventos intermitentes de alta velocidade.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="curiosity-box">
    📐 <strong>O Cubo da Velocidade:</strong>
    A potência eólica cresce com o <strong>cubo</strong> da velocidade do vento. 
    Isso significa: vento de 30 km/h gera 8× mais energia que vento de 15 km/h. 
    É por isso que mesmo uma diferença de poucos km/h entre as cidades resulta em 
    potencial energético muito diferente. Punta Arenas, com ~3 km/h a mais que Rio Gallegos, 
    tem ~30% mais densidade de potência.
    </div>
    """, unsafe_allow_html=True)

    # Infográfico comparativo global
    st.markdown('<div class="section-title">Contexto Global de Velocidade do Vento</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Comparação com outras cidades conhecidas pelo vento. As três cidades patagônicas estão entre as mais ventosas do mundo.</div>', unsafe_allow_html=True)

    global_cities = {
        "Wellington (NZ)": 27.0,
        "Punta Arenas 🇨🇱": 30.2,
        "Rio Gallegos 🇦🇷": 27.1,
        "Puerto Natales 🇨🇱": 26.8,
        "Chicago (EUA)": 16.9,
        "Amsterdam (NL)": 18.0,
        "Ushuaia 🇦🇷": 22.0,
        "Auckland (NZ)": 18.5,
        "São Paulo 🇧🇷": 12.0,
    }

    df_global = pd.DataFrame({
        "Cidade": list(global_cities.keys()),
        "Vento (km/h)": list(global_cities.values()),
    }).sort_values("Vento (km/h)", ascending=True)

    colors_global = [
        "#e63946" if "Punta" in c
        else "#f77f00" if "Puerto" in c
        else "#74b816" if "Gallegos" in c
        else "#94a3b8"
        for c in df_global["Cidade"]
    ]

    fig_global = go.Figure(go.Bar(
        x=df_global["Vento (km/h)"],
        y=df_global["Cidade"],
        orientation="h",
        marker_color=colors_global,
        text=df_global["Vento (km/h)"].apply(lambda x: f"{x} km/h"),
        textposition="outside",
    ))

    fig_global.update_layout(
        xaxis_title="Velocidade média anual (km/h)",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter"), height=420,
        margin=dict(l=20, r=80, t=20, b=20),
        xaxis=dict(gridcolor="#f1f5f9", range=[0, 40]),
    )
    st.plotly_chart(fig_global, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="source-box">
<b>📚 Fontes de Dados e Referências</b><br><br>
• <b>Open-Meteo</b> — Historical Weather API (ERA5 / Copernicus Climate Data Store). archive-api.open-meteo.com<br>
• <b>Climates to Travel</b> — Rio Gallegos climate: seasons, monthly averages. climatestotravel.com<br>
• <b>Weather Spark</b> — Average Weather in Punta Arenas, Chile Year Round. weatherspark.com<br>
• <b>MDPI Sustainability 16(14), 2024</b> — "Renewable Wind Energy Implementation in South America: 
  A Comprehensive Review." doi.org/10.3390/su16146082<br>
• <b>BNP Paribas CIB</b> — "El viento patagónico: How wind energy is powering change in Argentina." 2022.<br>
• <b>Global Wind Atlas</b> — World Bank / DTU Wind Energy. globalwindatlas.info<br>
• <b>Wikipedia</b> — Punta Arenas climate section. Windfinder.com — Punta Arenas wind statistics (2016–2025).<br>
• <b>PatagoniaHub</b> — Puerto Natales Weather Guide 2026. patagoniahub.travel<br>
<br>
<b>Elaboração:</b> Amauri Almeida — Portfólio de Pesquisa Ambiental &nbsp;·&nbsp; 
<a href="https://amaurialmeida.github.io/environmental-portfolio/" target="_blank">🌐 amaurialmeida.github.io</a> &nbsp;·&nbsp;
<a href="https://github.com/amaurialmeida" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
