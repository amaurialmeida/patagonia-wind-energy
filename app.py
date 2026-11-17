import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import math
from PIL import Image

# Importa as traduções do arquivo separado
from translations import TRANSLATIONS

st.set_page_config(
    page_title="Patagonia Wind Energy",
    page_icon="🌬️",
    layout="wide"
)

# ============================================================
# SISTEMA DE IDIOMAS (10 idiomas)
# ============================================================
LANGS = [
    ("pt", "🇧🇷", "PT"), ("en", "🇺🇸", "EN"), ("es", "🇪🇸", "ES"),
    ("it", "🇮🇹", "IT"), ("fr", "🇫🇷", "FR"), ("de", "🇩🇪", "DE"),
    ("zh", "🇨🇳", "ZH"), ("ar", "🇸🇦", "AR"), ("el", "🇬🇷", "EL"),
    ("af", "🇿🇦", "AF"),
]
CODES = [c for c, _, _ in LANGS]
FLAGS = {c: f"{flag} {label}" for c, flag, label in LANGS}

DECIMAL = {"pt": ",", "en": ".", "es": ",", "it": ",", "fr": ",", "de": ",", "zh": ".", "ar": ".", "el": ",", "af": ","}
PLOTLY_SEP = {"pt": ",.", "en": ".,", "es": ",.", "it": ",.", "fr": ", ", "de": ",.", "zh": ".,", "ar": ".,", "el": ",.", "af": ", "}

def _initial_lang():
    q = st.query_params.get("lang")
    if isinstance(q, list):
        q = q[0] if q else None
    return q if q in CODES else "pt"

if "lang" not in st.session_state:
    st.session_state.lang = _initial_lang()

def render_lang_selector():
    try:
        escolha = st.pills(
            "Language", CODES, selection_mode="single",
            default=st.session_state.lang, format_func=lambda c: FLAGS[c],
            key="lang_pick", label_visibility="collapsed",
        )
    except AttributeError:  # fallback para versões antigas do Streamlit
        escolha = st.radio(
            "Language", CODES, index=CODES.index(st.session_state.lang),
            format_func=lambda c: FLAGS[c], horizontal=True,
            key="lang_pick", label_visibility="collapsed",
        )
    if escolha and escolha != st.session_state.lang:
        st.session_state.lang = escolha
        st.query_params["lang"] = escolha
        st.rerun()

render_lang_selector()
LANG = st.session_state.lang
T = TRANSLATIONS[LANG]
RTL = LANG == "ar"

def fmt(x, nd=1):
    return f"{x:.{nd}f}".replace(".", DECIMAL[LANG])

def plot(fig):
    fig.update_layout(separators=PLOTLY_SEP[LANG])
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

# ── ESTILOS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&family=DM+Mono&family=Noto+Serif:wght@700&family=Noto+Sans:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Naskh+Arabic:wght@400;700&display=swap');
:root{
  --wind:#1A3A6E;--wind-mid:#2555A0;--wind-light:#3A7ACA;
  --sky:#56B3F0;--sky-light:#A8D8F0;
  --slate:#2D3A4A;--cream:#F4F6FA;--warm-gray:#6A7888;
  --green:#2D7A3A;--amber:#C47D0E;--danger:#8B2515;--black:#0D1117;
}
html,body,[class*="css"]{font-family:'DM Sans','Noto Sans','Noto Sans SC','Noto Naskh Arabic',sans-serif;background-color:var(--cream);color:var(--black);}
.hero-wrap{
  background:linear-gradient(135deg,var(--slate) 0%,var(--wind) 50%,#1E4A8A 100%);
  border-radius:20px;padding:3rem 2.5rem 2rem;margin-bottom:2rem;position:relative;overflow:hidden;
}
.hero-wrap::before{content:"🌬️";font-size:200px;position:absolute;right:-20px;top:-30px;opacity:0.05;}
.hero-tag{background:#A8D8F0;color:var(--wind);font-family:'DM Mono',monospace;font-size:0.7rem;font-weight:bold;letter-spacing:2px;padding:4px 12px;border-radius:4px;display:inline-block;margin-bottom:1rem;text-transform:uppercase;}
.hero-title{font-family:'Playfair Display','Noto Serif','Noto Sans SC','Noto Naskh Arabic',serif;font-size:2.8rem;font-weight:900;color:#fff;line-height:1.15;margin-bottom:0.8rem;white-space:pre-line;}
.hero-subtitle{font-size:1rem;color:rgba(255,255,255,0.78);max-width:680px;line-height:1.6;margin-bottom:1.5rem;}
.hero-badges{display:flex;gap:10px;flex-wrap:wrap;}
.badge{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.85);font-size:0.72rem;font-family:'DM Mono','Noto Sans','Noto Sans SC','Noto Naskh Arabic',monospace;padding:5px 12px;border-radius:20px;letter-spacing:0.5px;}
.badge-wind{background:rgba(168,216,240,0.2);border-color:#A8D8F0;color:#A8D8F0;}
.metric-box{background:white;border-radius:16px;padding:1.4rem 1.2rem;border-top:4px solid var(--wind-light);box-shadow:0 2px 12px rgba(0,0,0,0.06);text-align:center;}
.metric-box.sky{border-top-color:var(--sky);}
.metric-box.amber{border-top-color:var(--amber);}
.metric-box.green{border-top-color:var(--green);}
.metric-val{font-family:'Playfair Display','Noto Serif',serif;font-size:2.1rem;font-weight:900;color:var(--wind);line-height:1;margin-bottom:0.3rem;}
.metric-label{font-size:0.75rem;color:var(--warm-gray);text-transform:uppercase;letter-spacing:1px;}
.section-label{font-family:'DM Mono','Noto Sans','Noto Sans SC','Noto Naskh Arabic',monospace;font-size:0.65rem;color:var(--wind-mid);text-transform:uppercase;letter-spacing:3px;margin-bottom:0.3rem;}
.section-title{font-family:'Playfair Display','Noto Serif','Noto Sans SC','Noto Naskh Arabic',serif;font-size:1.9rem;font-weight:700;color:var(--wind);margin-bottom:1.2rem;line-height:1.2;}
.info-card{background:white;border-radius:16px;padding:1.5rem;box-shadow:0 2px 12px rgba(0,0,0,0.05);border-left:4px solid var(--wind-light);margin-bottom:1rem;}
.info-card.amber{border-left-color:var(--amber);}
.info-card.green{border-left-color:var(--green);}
.info-card.danger{border-left-color:var(--danger);}
.timeline-item{display:flex;gap:1rem;padding:1rem 0;border-bottom:1px solid #e0e8f0;}
.timeline-year{font-family:'Playfair Display','Noto Serif',serif;font-size:1rem;font-weight:700;color:var(--wind-mid);min-width:80px;}
.timeline-title{font-weight:500;color:var(--wind);margin-bottom:0.2rem;}
.timeline-desc{font-size:0.85rem;color:var(--warm-gray);}
.method-step{display:flex;align-items:flex-start;gap:1rem;padding:1rem;background:white;border-radius:12px;margin-bottom:0.8rem;box-shadow:0 1px 6px rgba(0,0,0,0.04);}
.step-num{background:var(--wind-mid);color:white;font-family:'Playfair Display','Noto Serif',serif;font-size:1.1rem;font-weight:700;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.step-title{font-weight:500;color:var(--wind);font-size:0.95rem;}
.step-desc{font-size:0.82rem;color:var(--warm-gray);margin-top:0.2rem;}
.discovery-box{background:linear-gradient(135deg,#EEF4FF,#D8EAF8);border:2px solid var(--wind-light);border-radius:16px;padding:1.8rem;margin:0.8rem 0;}
.discovery-title{font-family:'Playfair Display','Noto Serif','Noto Sans SC','Noto Naskh Arabic',serif;font-size:1.1rem;font-weight:700;color:var(--wind);margin-bottom:0.5rem;}
.source-badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:0.8rem;}
.source-badge{background:var(--wind);color:white;font-family:'DM Mono',monospace;font-size:0.65rem;padding:4px 10px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;}
.footer-wrap{background:var(--wind);border-radius:20px;padding:2rem;color:rgba(255,255,255,0.8);text-align:center;margin-top:3rem;}
.footer-title{font-family:'Playfair Display','Noto Serif',serif;color:#A8D8F0;font-size:1.2rem;margin-bottom:0.5rem;}
.city-card{background:white;border-radius:16px;padding:1.4rem;border-top:5px solid;box-shadow:0 3px 14px rgba(0,0,0,0.07);margin-bottom:0.5rem;transition:box-shadow .2s;}
.city-card:hover{box-shadow:0 6px 22px rgba(0,0,0,0.12);}
.city-card-title{font-family:'Playfair Display','Noto Serif',serif;font-size:1rem;font-weight:700;margin-bottom:0.4rem;}
.city-card-meta{font-size:0.78rem;font-family:'DM Mono','Noto Sans','Noto Sans SC','Noto Naskh Arabic',monospace;color:var(--warm-gray);line-height:1.8;}
.photo-placeholder{background:#EEF4FF;border:2px dashed var(--wind-light);border-radius:12px;padding:2rem;text-align:center;min-height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.photo-emoji{font-size:2.8rem;}
.photo-title{font-weight:600;color:var(--wind);margin:0.5rem 0 0.2rem;font-size:1rem;}
.photo-desc{font-size:0.80rem;color:var(--warm-gray);line-height:1.55;max-width:280px;}
.photo-path{font-size:0.65rem;color:var(--wind-mid);font-family:'DM Mono',monospace;margin-top:0.5rem;background:#D8EAF8;padding:3px 8px;border-radius:4px;direction:ltr;}
.photo-meta{font-size:0.7rem;font-family:'DM Mono',monospace;margin-top:0.4rem;line-height:1.7;}
.photo-legenda{font-size:0.72rem;color:var(--warm-gray);font-style:italic;padding:0.5rem 0.8rem;background:#f5f7fa;text-align:center;border-top:1px solid #d8e4f0;}
.photo-destaque{border:3px solid var(--wind-light);border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(26,58,110,0.15);}
</style>
""", unsafe_allow_html=True)

if RTL:
    st.markdown("""
<style>
[data-testid="stMain"], [data-testid="stAppViewContainer"] .main { direction: rtl; text-align: right; }
.hero-wrap, .info-card, .method-step, .discovery-box, .timeline-item, .sim-notice { direction: rtl; text-align: right; }
.hero-wrap::before { right: auto; left: -20px; }
.info-card, .info-card.amber, .info-card.green, .info-card.danger { border-left: none; border-right: 4px solid var(--wind-light); }
.js-plotly-plot, iframe { direction: ltr; }
body, html, [class*="css"] { font-family: 'Noto Naskh Arabic','DM Sans',sans-serif; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DADOS DAS CIDADES
# ============================================================
CITIES = {
    "Punta Arenas":  {"lat": -53.163, "lon": -70.917, "pais": "🇨🇱 Chile",  "v_media": 30.2, "rajada": 130, "pot_mw": 4200, "cap_factor": 0.63, "cor": "#1A3A6E"},
    "Puerto Natales": {"lat": -51.729, "lon": -72.494, "pais": "🇨🇱 Chile",  "v_media": 26.8, "rajada": 104, "pot_mw": 1800, "cap_factor": 0.55, "cor": "#1B3A1E"},
    "Rio Gallegos":   {"lat": -51.622, "lon": -69.218, "pais": "🇦🇷 Argentina", "v_media": 27.1, "rajada": 100, "pot_mw": 3500, "cap_factor": 0.61, "cor": "#5C3D1E"},
    "Puerto Williams":{"lat": -54.935, "lon": -67.616, "pais": "🇨🇱 Chile",  "v_media": 22.0, "rajada": 95,  "pot_mw": None,  "cap_factor": 0.52, "cor": "#8B2515"},
}

MONTHS = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
WIND_DATA = {
    "Punta Arenas":  [33.1,31.8,29.6,28.4,27.9,28.2,29.1,30.5,31.8,32.4,33.6,32.9],
    "Puerto Natales": [28.4,27.6,26.1,25.3,24.8,25.1,25.8,26.9,27.5,28.1,29.2,28.8],
    "Rio Gallegos":   [29.2,28.1,27.0,25.8,25.2,25.6,26.4,27.8,28.5,29.1,29.8,29.5],
    "Puerto Williams":[23.1,22.5,21.8,20.9,20.4,20.8,21.5,22.3,22.8,23.4,24.1,23.7],
}
ANNUAL = {
    "Punta Arenas":   [29.1,29.8,30.2,30.5,31.0],
    "Puerto Natales": [25.8,26.1,26.5,26.9,27.2],
    "Rio Gallegos":   [26.4,26.8,27.0,27.3,27.6],
    "Puerto Williams":[21.2,21.6,21.9,22.1,22.5],
}
YEARS = [2020, 2021, 2022, 2023, 2024]
CITY_COLORS = {"Punta Arenas": "#1A3A6E", "Puerto Natales": "#1B3A1E",
               "Rio Gallegos": "#5C3D1E", "Puerto Williams": "#8B2515"}

# ── HERO ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-tag">{T['hero_tag']}</div>
  <div class="hero-title">{T['hero_title']}</div>
  <div class="hero-subtitle">{T['hero_subtitle']}</div>
  <div class="hero-badges">
    <span class="badge badge-wind">{T['badge1']}</span>
    <span class="badge badge-wind">{T['badge2']}</span>
    <span class="badge">{T['badge3']}</span>
    <span class="badge">{T['badge4']}</span>
    <span class="badge">{T['badge5']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-box"><div class="metric-val">{fmt(30.2)} km/h</div><div class="metric-label">{T["m1"]}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box sky"><div class="metric-val">>60%</div><div class="metric-label">{T["m2"]}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-box amber"><div class="metric-val">{fmt(130)} km/h</div><div class="metric-label">{T["m3"]}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-box green"><div class="metric-val">{fmt(9500,0)} MW</div><div class="metric-label">{T["m4"]}</div></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── ABAS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([T['tab1'], T['tab2'], T['tab3'], T['tab4'], T['tab5']])

# ── TAB 1: MAPA & ANÁLISE ─────────────────────────────────────
with tab1:
    st.markdown(f'<div class="section-label">{T["map_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["map_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["map_hint"]}</div>', unsafe_allow_html=True)

    try:
        carto_key = st.secrets.get("CARTO_API_KEY", "")
    except Exception:
        carto_key = ""

    mapa = folium.Map(location=[-52.5, -70.0], zoom_start=5, tiles=None, control_scale=True)

    if carto_key:
        folium.TileLayer(
            tiles=("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?key=" + carto_key),
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name="CARTO Voyager", subdomains="abcd", max_zoom=20, overlay=False, control=True,
        ).add_to(mapa)
    else:
        folium.TileLayer(
            "OpenStreetMap", name="OpenStreetMap",
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            control=True,
        ).add_to(mapa)

    for city, d in CITIES.items():
        radius = d["v_media"] * 1200
        pot_str = f"{d['pot_mw']:,} MW" if d['pot_mw'] else "Ponto extremo"
        pop_html = f"""<div style='font-family:sans-serif;min-width:240px;padding:12px'>
            <h4 style='color:{d["cor"]};margin:0 0 8px'>{city}</h4>
            <p style='margin:3px 0;font-size:12px'>🌍 {d["pais"]}</p>
            <p style='margin:3px 0;font-size:12px'>💨 Vel. média: <b>{fmt(d["v_media"])} km/h</b></p>
            <p style='margin:3px 0;font-size:12px'>⚡ Rajada máx.: <b>{fmt(d["rajada"],0)} km/h</b></p>
            <p style='margin:3px 0;font-size:12px'>🔋 Potencial: <b>{pot_str}</b></p>
            <p style='margin:3px 0;font-size:12px'>📊 Cap. factor: <b>{fmt(d["cap_factor"]*100,0)}%</b></p>
            <hr style='margin:8px 0;border-color:#eee'>
            <p style='margin:0;font-size:10px;color:#999'>Lat: {fmt(d["lat"],3)} · Lon: {fmt(d["lon"],3)}</p>
        </div>"""
        folium.Circle(
            location=[d["lat"], d["lon"]], radius=radius,
            color=d["cor"], fill=True, fill_color=d["cor"], fill_opacity=0.15,
            weight=2, tooltip=f"💨 {city} · {fmt(d['v_media'])} km/h"
        ).add_to(mapa)
        folium.Marker(
            location=[d["lat"], d["lon"]],
            popup=folium.Popup(pop_html, max_width=270),
            tooltip=f"💨 {city} · {fmt(d['v_media'])} km/h média",
            icon=folium.Icon(color="blue" if "Chile" in d["pais"] else "red", icon="wind", prefix="fa")
        ).add_to(mapa)

    folium.PolyLine(
        locations=[[-40, -80],[-40,-65],[-45,-60],[-50,-60],[-55,-65],[-55,-68]],
        color="#56B3F0", weight=2, opacity=0.5, dash_array="8",
        tooltip="Corredor Westerlies (~40°S–55°S)"
    ).add_to(mapa)

    folium_static(mapa, width=1100, height=500)

    st.markdown("<br>", unsafe_allow_html=True)
    col_cards = st.columns(4)
    city_list = list(CITIES.items())
    for i, (city, d) in enumerate(city_list):
        pot_str = f"{d['pot_mw']:,} MW" if d['pot_mw'] else "Ref."
        with col_cards[i]:
            flag = "🇨🇱" if "Chile" in d["pais"] else "🇦🇷"
            st.markdown(f"""
            <div class="city-card" style="border-top-color:{d['cor']}">
              <div class="city-card-title" style="color:{d['cor']}">{flag} {city}</div>
              <div class="city-card-meta">
                💨 {fmt(d['v_media'])} km/h média<br>
                ⚡ Rajada: {fmt(d['rajada'],0)} km/h<br>
                🔋 Potencial: {pot_str}<br>
                📊 Cap. factor: {fmt(d['cap_factor']*100,0)}%
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"<br><div class='section-label'>{T['chart_label']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{T['wind_monthly_title']}</div>", unsafe_allow_html=True)

    fig_monthly = go.Figure()
    for city, vals in WIND_DATA.items():
        fig_monthly.add_trace(go.Scatter(
            x=MONTHS, y=vals, mode='lines+markers',
            name=city,
            line=dict(color=CITY_COLORS[city], width=2.5),
            marker=dict(size=7, color=CITY_COLORS[city]),
            hovertemplate=f'<b>{city}</b><br>%{{x}}: %{{y:.1f}} km/h<extra></extra>'
        ))
    fig_monthly.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(26,58,110,0.02)',
        font=dict(family='DM Sans'), height=380,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e0e8f0', title=T['wind_y'], range=[18, 38]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left'),
        margin=dict(t=20, b=20)
    )
    plot(fig_monthly)

    col_r, col_a = st.columns(2)
    with col_r:
        st.markdown(f"<div style='font-family:DM Mono;font-size:0.75rem;color:#2555A0;letter-spacing:1px'>{T['rose_title']}</div>", unsafe_allow_html=True)
        direcoes = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSO","SO","OSO","O","ONO","NO","NNO"]
        freqs_pa = [2,1.5,1.5,2,2.5,3,4,5,4,5,8,12,18,16,9,6]
        freqs_rg = [2,2,2,2.5,3,4,5,6,5,6,9,13,16,15,8,5]
        fig_rose = go.Figure()
        fig_rose.add_trace(go.Barpolar(r=freqs_pa, theta=direcoes, name="Punta Arenas", marker_color="#1A3A6E", opacity=0.75, hovertemplate='<b>Punta Arenas</b><br>%{theta}: %{r:.1f}%<extra></extra>'))
        fig_rose.add_trace(go.Barpolar(r=freqs_rg, theta=direcoes, name="Rio Gallegos", marker_color="#5C3D1E", opacity=0.75, hovertemplate='<b>Rio Gallegos</b><br>%{theta}: %{r:.1f}%<extra></extra>'))
        fig_rose.update_layout(paper_bgcolor='rgba(0,0,0,0)', polar=dict(radialaxis=dict(showticklabels=True, ticks='', range=[0, 20]), angularaxis=dict(direction="clockwise")), legend=dict(orientation='h', yanchor='top', y=-0.05), height=360, font=dict(family='DM Sans'), margin=dict(t=10, b=20))
        plot(fig_rose)

    with col_a:
        st.markdown(f"<div style='font-family:DM Mono;font-size:0.75rem;color:#2555A0;letter-spacing:1px'>{T['annual_title']}</div>", unsafe_allow_html=True)
        fig_annual = go.Figure()
        for city, vals in ANNUAL.items():
            fig_annual.add_trace(go.Bar(name=city, x=YEARS, y=vals, marker_color=CITY_COLORS[city], opacity=0.85, hovertemplate=f'<b>{city}</b><br>%{{x}}: %{{y:.1f}} km/h<extra></extra>'))
        fig_annual.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'), height=360, xaxis=dict(showgrid=False, tickmode='array', tickvals=YEARS, ticktext=[str(y) for y in YEARS]), yaxis=dict(showgrid=True, gridcolor='#e0e8f0', title=T['annual_y'], range=[18, 36]), legend=dict(orientation='h', yanchor='bottom', y=1.02), margin=dict(t=20, b=20))
        plot(fig_annual)

    st.markdown(f"<br><div class='section-label'>{T['simulator_label']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{T['simulator_title']}</div>", unsafe_allow_html=True)

    sim_col1, sim_col2, sim_col3 = st.columns([2, 1, 1])
    with sim_col1:
        city_sel = st.selectbox(T['select_city'], list(CITIES.keys()), key="sim_city")
    with sim_col2:
        n_turbines = st.slider(T['turbines_label'], 1, 500, 100, key="sim_turb")
    with sim_col3:
        power_mw = st.slider(T['power_label'], 2, 8, 4, key="sim_power")

    cf = CITIES[city_sel]["cap_factor"]
    gwh = round(power_mw * n_turbines * cf * 8760 / 1000, 1)
    homes = int(gwh * 1000 / 4.2)
    co2 = int(gwh * 1000 * 0.42)

    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:2.4rem;color:#1A3A6E">{fmt(gwh)}</div><div class="metric-label">{T["sim_result_gwh"]}</div></div>', unsafe_allow_html=True)
    with res_col2:
        st.markdown(f'<div class="metric-box sky"><div class="metric-val" style="font-size:2rem">{homes:,}</div><div class="metric-label">{T["sim_result_homes"]}</div></div>', unsafe_allow_html=True)
    with res_col3:
        st.markdown(f'<div class="metric-box green"><div class="metric-val" style="font-size:2rem">{co2:,}</div><div class="metric-label">{T["sim_result_co2"]}</div></div>', unsafe_allow_html=True)

    fig_gauges = go.Figure()
    for i, (city, d) in enumerate(CITIES.items()):
        fig_gauges.add_trace(go.Indicator(
            mode="gauge+number",
            value=d["cap_factor"] * 100,
            number={'suffix': "%", 'font': {'size': 18, 'family': 'Playfair Display', 'color': d["cor"]}},
            gauge={'axis': {'range': [0, 80], 'tickwidth': 1}, 'bar': {'color': d["cor"], 'thickness': 0.3}, 'bgcolor': "white", 'borderwidth': 0, 'steps': [{'range': [0, 35], 'color': '#f0f4f8'}, {'range': [35, 55], 'color': '#d8e8f5'}, {'range': [55, 80], 'color': '#A8D8F0'}], 'threshold': {'line': {'color': d["cor"], 'width': 3}, 'thickness': 0.75, 'value': d["cap_factor"] * 100}},
            title={'text': city, 'font': {'size': 11, 'family': 'DM Sans', 'color': d["cor"]}},
            domain={'row': 0, 'column': i}
        ))
    fig_gauges.update_layout(grid={'rows': 1, 'columns': 4, 'pattern': "independent"}, paper_bgcolor='rgba(0,0,0,0)', height=260, font=dict(family='DM Sans'), title=dict(text=T['capacity_title'], font=dict(size=13, family='Playfair Display'), x=0.5), margin=dict(t=50, b=10, l=10, r=10))
    plot(fig_gauges)

# ── TAB 2: METODOLOGIA ────────────────────────────────────────
with tab2:
    st.markdown(f'<div class="section-label">{T["method_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["method_title"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="discovery-box"><div class="discovery-title">{T["sci_question_title"]}</div><p style="font-size:1.05rem;color:#1A3A6E;line-height:1.7"><em>{T["sci_question"]}</em></p></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-label" style="margin-top:1.5rem">{T["pipeline_label"]}</div>', unsafe_allow_html=True)
    for num, title, desc in T['steps']:
        st.markdown(f'<div class="method-step"><div class="step-num">{num}</div><div style="flex:1"><div class="step-title">{title}</div><div class="step-desc">{desc}</div></div></div>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f'<div class="info-card"><strong>{T["physics_title"]}</strong><br><br><div style="font-size:0.88rem;line-height:2.1">{T["physics_text"]}</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="info-card amber"><strong>{T["westerlies_title"]}</strong><br><br><div style="font-size:0.88rem;line-height:2.1">{T["westerlies_text"]}</div></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="background:linear-gradient(135deg,#EEF4FF,#D8EAF8);margin-top:0.5rem">
      <strong style="color:#1A3A6E">📐 Fórmulas Fundamentais</strong><br><br>
      <div style="font-family:'DM Mono',monospace;font-size:0.85rem;line-height:2.4;color:#1A3A6E;direction:ltr">
        <b>Densidade de potência:</b> P/A = ½ × ρ × v³<br>
        <b>Geração anual:</b> GWh/ano = P_turb × N × FC × 8.760h<br>
        <b>FC Patagônia:</b> 55–63% (média global: ~35%)<br>
        <b>Dobrar velocidade</b> = 8× mais energia (lei cúbica)<br>
        <b>CO₂ evitado:</b> GWh × 420 kg/MWh (fator rede sul-americana)
      </div>
      <div style="font-size:0.75rem;color:#7A8A96;margin-top:0.5rem">MDPI Sustainability 2024 · BNP Paribas CIB · Global Wind Atlas · Open-Meteo ERA5</div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB 3: DESCOBERTAS ────────────────────────────────────────
with tab3:
    st.markdown(f'<div class="section-label">{T["discovery_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["discovery_title"]}</div>', unsafe_allow_html=True)

    for emoji, titulo, texto in T['discoveries']:
        st.markdown(f'<div class="discovery-box" style="margin-bottom:0.8rem"><div style="display:flex;align-items:flex-start;gap:1rem"><span style="font-size:1.5rem">{emoji}</span><div><div class="discovery-title">{titulo}</div><p style="color:#1A3A6E;line-height:1.65;font-size:0.93rem;margin:0">{texto}</p></div></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-label" style="margin-top:1.5rem">{T["conclusion_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card" style="border-left-color:#1A3A6E;background:linear-gradient(135deg,#EEF4FF,#D8EAF8)"><strong style="color:#1A3A6E;font-size:1rem">{T["conclusion_title"]}</strong><br><br><p style="color:#1A3A6E;line-height:1.7;font-size:0.93rem">{T["conclusion_text"]}</p><p style="color:#2555A0;font-size:0.82rem;margin-bottom:0"><em>{T["conclusion_author"]}</em></p></div>', unsafe_allow_html=True)

    fig_comp = go.Figure()
    for city, d in list(CITIES.items())[:3]:
        pot = d['pot_mw'] or 0
        fig_comp.add_trace(go.Bar(x=[city], y=[pot], marker_color=d["cor"], opacity=0.88, text=[f"{pot:,} MW"], textposition='outside', textfont=dict(size=11, color=d["cor"], family="DM Mono"), showlegend=False, hovertemplate=f'<b>{city}</b><br>{pot:,} MW<extra></extra>'))
    fig_comp.update_layout(title=dict(text="Potencial Instalável por Cidade (MW)", font=dict(size=14, family='Playfair Display')), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340, font=dict(family='DM Sans'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#e0e8f0', title="MW instaláveis (estimativa)"), margin=dict(t=50, b=20))
    plot(fig_comp)

# ── TAB 4: EM CAMPO ───────────────────────────────────────────
with tab4:
    st.markdown(f'<div class="section-label">{T["field_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["field_title"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-card amber" style="margin-bottom:1.5rem"><strong>{T["field_instructions_title"]}</strong><br><div style="font-size:0.88rem;color:#5C3D1E;margin-top:0.4rem">{T["field_instructions"]}</div></div>', unsafe_allow_html=True)

    photos = T['photos']
    foto_destaque = next((f for f in photos if f.get("destaque")), None)
    fotos_normais = [f for f in photos if not f.get("destaque")]

    row_cols = st.columns(3)
    for i, foto in enumerate(fotos_normais):
        with row_cols[i]:
            _img_ok = False
            if os.path.exists(foto['path']):
                try:
                    Image.open(foto['path']).verify()
                    _img_ok = True
                except Exception:
                    _img_ok = False
            if _img_ok:
                st.image(foto['path'], use_container_width=True)
            else:
                st.markdown(f"""
                <div class="photo-placeholder" style="border-color:{foto['cor']}">
                  <div class="photo-emoji">{foto['emoji']}</div>
                  <div class="photo-title" style="color:{foto['cor']}">{foto['titulo']}</div>
                  <div class="photo-desc">{foto['desc']}</div>
                  <div class="photo-meta" style="color:{foto['cor']}">
                    📍 {foto['coords']}<br>
                    💨 {foto['vento']}<br>
                    ⚡ {foto['pot']}<br>
                    📅 {foto['mes']}
                  </div>
                  <div class="photo-path">{foto['path']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f'<div class="photo-legenda">{foto["legenda"]}</div>', unsafe_allow_html=True)

    if foto_destaque:
        st.markdown("---")
        st.markdown(f'<div class="section-label" style="color:{foto_destaque["cor"]}">🏁 DESTAQUE FINAL — PUERTO WILLIAMS · FIM DA JORNADA</div>', unsafe_allow_html=True)
        _dest_ok = False
        if os.path.exists(foto_destaque['path']):
            try:
                Image.open(foto_destaque['path']).verify()
                _dest_ok = True
            except Exception:
                _dest_ok = False
        if _dest_ok:
            st.markdown('<div class="photo-destaque">', unsafe_allow_html=True)
            st.image(foto_destaque['path'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="photo-placeholder" style="min-height:300px;border-color:{foto_destaque['cor']}">
              <div class="photo-emoji" style="font-size:3rem">{foto_destaque['emoji']}</div>
              <div class="photo-title" style="font-size:1.2rem;color:{foto_destaque['cor']}">{foto_destaque['titulo']}</div>
              <div class="photo-desc" style="max-width:660px;text-align:center">{foto_destaque['desc']}</div>
              <div class="photo-meta" style="color:{foto_destaque['cor']}">
                📍 {foto_destaque['coords']} · 💨 {foto_destaque['vento']} · 📅 {foto_destaque['mes']}
              </div>
              <div class="photo-path">{foto_destaque['path']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f'<div class="photo-legenda" style="font-size:0.82rem;padding:0.7rem 1.2rem">{foto_destaque["legenda"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{T["timeline_field_label"]}</div>', unsafe_allow_html=True)
    for data, titulo, desc in T['timeline_field_items']:
        st.markdown(f'<div class="timeline-item"><div class="timeline-year">{data}</div><div style="flex:1"><div class="timeline-title">{titulo}</div><div class="timeline-desc">{desc}</div></div></div>', unsafe_allow_html=True)

# ── TAB 5: FONTES ─────────────────────────────────────────────
with tab5:
    st.markdown(f'<div class="section-label">{T["sources_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["sources_title"]}</div>', unsafe_allow_html=True)

    fontes = [
        ("OPEN-METEO", "Open-Meteo Historical API — Reanálise ERA5 (ECMWF)", "archive-api.open-meteo.com · Dados horários de velocidade e direção do vento 2020–2024 para Punta Arenas, Puerto Natales e Rio Gallegos.", "#1A3A6E"),
        ("GLOBAL WIND ATLAS", "Global Wind Atlas — DTU Wind Energy / World Bank", "globalwindatlas.info · Densidade de potência eólica, mapeamento de recursos, atlas global de vento com resolução 250 m.", "#2555A0"),
        ("MDPI 2024", "MDPI Sustainability — DOI: 10.3390/su16146082", "Potencial de geração eólica regional na Patagônia. Dados de fator de capacidade e estimativas instaláveis para cidades patagônicas.", "#3A7ACA"),
        ("BNP PARIBAS", "BNP Paribas CIB — Relatório Técnico Eólico Argentina", "cib.bnpparibas · Fator de capacidade eólica Argentina: acima de 60% vs. média global 35%. Referência para avaliação de projetos.", "#1B3A1E"),
        ("CLIMATES TRAVEL", "Climates to Travel — Rio Gallegos Climate Profile", "climatestotravel.com · Médias mensais de velocidade do vento, temperatura e precipitação para Rio Gallegos.", "#5C3D1E"),
        ("WEATHER SPARK", "Weather Spark — Punta Arenas Climate Summary", "weatherspark.com · Perfil climático detalhado de Punta Arenas com dados históricos de vento e rajadas máximas.", "#C47D0E"),
        ("CAMPO", "Observação Pessoal de Campo — Amauri Almeida (Nov 2024–Out 2025)", "11 meses percorrendo Punta Arenas, Puerto Natales, Rio Gallegos e Puerto Williams. Vivência direta dos Westerlies e registro dos fenômenos naturais.", "#8B2515"),
    ]

    for sigla, nome, desc, cor in fontes:
        st.markdown(f"""
        <div class="info-card" style="border-left-color:{cor}">
          <div style="display:flex;align-items:flex-start;gap:1rem">
            <div style="background:{cor};color:white;font-family:'DM Mono',monospace;font-size:0.6rem;
                 padding:4px 7px;border-radius:4px;white-space:nowrap;flex-shrink:0;margin-top:2px;
                 letter-spacing:0.5px;font-weight:bold;text-align:center;min-width:75px">{sigla}</div>
            <div>
              <div style="font-weight:500;font-size:0.9rem;color:#1A3A6E">{nome}</div>
              <div style="font-size:0.82rem;color:#6A7888;margin-top:0.2rem">{desc}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<br><div class='section-label'>{T['tech_label']}</div>", unsafe_allow_html=True)
    techs = ["Python 3.11", "Streamlit", "Plotly", "Folium", "Pandas", "NumPy", "Open-Meteo API", "ERA5/ECMWF", "Global Wind Atlas"]
    st.markdown(''.join([f'<span class="source-badge">{t}</span>' for t in techs]), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="footer-wrap" style="margin-top:2rem">
      <div class="footer-title">{T['footer_title']}</div>
      <p style="margin:0.5rem 0;font-size:0.9rem">{T['footer_desc']}</p>
      <p style="margin:1rem 0 0.5rem;font-size:0.85rem;opacity:0.7">
        {T['footer_links']} &nbsp;|&nbsp;
        🌐 <a href="https://amaurialmeida.github.io/environmental-portfolio/" style="color:#A8D8F0">Portfólio</a> &nbsp;|&nbsp;
        🐙 <a href="https://github.com/amaurialmeida" style="color:#A8D8F0">GitHub</a>
      </p>
      <p style="font-size:0.75rem;opacity:0.5;margin:0">© 2024–2026 · Potencial Eólico · Patagônia · Chile & Argentina</p>
    </div>
    """, unsafe_allow_html=True)
