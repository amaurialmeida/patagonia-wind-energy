import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
import math
from PIL import Image
import io

st.set_page_config(
    page_title="Potencial Eólico · Patagônia",
    page_icon="🌬️",
    layout="wide"
)

# ============================================================
# SISTEMA DE IDIOMAS
# ============================================================
if "lang" not in st.session_state:
    st.session_state.lang = "pt"

TRANSLATIONS = {
    "pt": {
        "page_title": "Potencial Eólico · Patagônia",
        "hero_tag": "ANÁLISE CIENTÍFICA · PATAGÔNIA SUL · CHILE & ARGENTINA · NOV 2024–OUT 2025",
        "hero_title": "Potencial Eólico\nda Patagônia",
        "hero_subtitle": "Análise comparativa do potencial de geração de energia eólica em Punta Arenas, Puerto Natales, Rio Gallegos e Puerto Williams — quatro das cidades mais ventosas do planeta, percorridas pessoalmente entre novembro de 2024 e outubro de 2025.",
        "badge1": "💨 Westerlies · 40°S–60°S",
        "badge2": "⚡ 9.500+ MW potencial",
        "badge3": "Chile & Argentina",
        "badge4": "Nov 2024 — Out 2025",
        "badge5": "OPEN-METEO · ERA5 · GWA",
        "m1": "Vel. média Punta Arenas",
        "m2": "Fator de capacidade (PAT)",
        "m3": "Rajada máx. registrada",
        "m4": "Potencial total estimado",
        "tab1": "🗺️ Mapa & Análise",
        "tab2": "🔬 Metodologia & Pipeline",
        "tab3": "💡 O que Descobrimos",
        "tab4": "📷 Em Campo",
        "tab5": "📚 Fontes & Créditos",
        "map_label": "GEOLOCALIZAÇÃO — CORREDOR DE VENTOS",
        "map_title": "Mapa Interativo — Cidades & Potencial Eólico",
        "map_hint": "💨 <strong>Clique nos marcadores</strong> para ver dados de vento, potencial instalado e características de cada cidade. Os círculos são proporcionais à velocidade média do vento.",
        "chart_label": "ANÁLISE DO VENTO",
        "wind_monthly_title": "Velocidade Média Mensal do Vento — 2020–2024",
        "wind_y": "Velocidade (km/h)",
        "rose_title": "Rosa dos Ventos — Distribuição Direcional",
        "annual_title": "Evolução Anual da Velocidade Média (2020–2024)",
        "annual_y": "Velocidade média anual (km/h)",
        "simulator_label": "SIMULADOR DE GERAÇÃO EÓLICA",
        "simulator_title": "Calculadora de Potencial Energético",
        "sim_city": "Cidade",
        "sim_turbines": "Número de turbinas",
        "sim_power": "Potência por turbina (MW)",
        "sim_result_gwh": "GWh / ano estimados",
        "sim_result_homes": "domicílios atendidos",
        "sim_result_co2": "t CO₂ evitadas/ano",
        "capacity_title": "Fator de Capacidade por Cidade",
        "method_label": "CIÊNCIA DO VENTO",
        "method_title": "Pergunta & Metodologia",
        "sci_question_title": "❓ Pergunta Central",
        "sci_question": "\"Qual é o potencial real de geração de energia eólica nas cidades mais ventosas da Patagônia, e como a experiência direta de campo reforça os dados científicos sobre a força e consistência dos ventos Westerlies nessa região?\"",
        "pipeline_label": "PIPELINE DE ANÁLISE",
        "steps": [
            ("1", "Coleta de Dados — Open-Meteo ERA5 (2020–2024)",
             "Dados horários de velocidade e direção do vento para Punta Arenas, Puerto Natales e Rio Gallegos via Open-Meteo Historical API (reanálise ERA5 do ECMWF). Cobertura de 5 anos completos com resolução horária, processados para obter médias mensais, anuais e distribuições direcionais."),
            ("2", "Experiência de Campo — Patagônia (Nov 2024–Out 2025)",
             "11 meses percorrendo as quatro cidades estudadas: Punta Arenas (nov 2024), Puerto Natales (dez 2024), Rio Gallegos (mar 2025) e Puerto Williams (até out 2025). Vivência direta dos ventos Westerlies — incluindo rajadas que dificultam caminhar em linha reta e um terremoto M7+ registrado em Puerto Williams em 02 mai 2025."),
            ("3", "Física do Vento — Lei da Potência Cúbica",
             "A densidade de potência eólica segue P/A = ½ × ρ × v³, onde a velocidade entra ao cubo. Duplicar a velocidade do vento gera 8× mais energia. Com médias entre 26–30 km/h e rajadas de até 130 km/h, a Patagônia explora essa lei de forma exponencial. Fatores de capacidade acima de 60% vs. média global de 35%."),
            ("4", "Simulador de Turbinas",
             "Cálculo interativo de geração: GWh/ano = P_turbina × N_turbinas × Fator_Capacidade × 8.760h. O simulador permite configurar número de turbinas (1–500) e potência unitária (2–8 MW), calculando automaticamente domicílios atendidos e CO₂ evitado com base no fator de emissão da rede chilena/argentina."),
            ("5", "Rosa dos Ventos e Análise Direcional",
             "Distribuição direcional dos ventos para identificar os setores de maior frequência e intensidade. Na Patagônia, os Westerlies conferem dominância ao setor WSW-W-WNW com consistência ímpar — uma característica determinante para o posicionamento ótimo de turbinas eólicas e o projeto de parques eólicos offshore."),
            ("6", "Potencial Instalado e Impacto Ambiental",
             "Estimativa do potencial total instalável: Punta Arenas 4.200 MW, Puerto Natales 1.800 MW, Rio Gallegos 3.500 MW. A geração combinada substituiria ~2,3 GW de termelétricas a gás na Patagônia, evitando ~3,5 Mt de CO₂/ano — equivalente a retirar 750.000 veículos de circulação."),
        ],
        "physics_title": "⚙️ Física do Vento",
        "physics_text": "• <b>Lei cúbica:</b> P/A = ½ × ρ × v³ · (v³ = 8× mais energia ao dobrar v)<br>• <b>Densidade do ar:</b> ~1,20 kg/m³ ao nível do mar<br>• <b>Fator de capacidade PAT:</b> >60% vs. média global de 35%<br>• <b>Ventos Westerlies:</b> 40°S–60°S · quase sem obstáculos terrestres<br>• <b>Roaring Forties / Furious Fifties / Screaming Sixties</b>",
        "westerlies_title": "🌍 Por que a Patagônia?",
        "westerlies_text": "• <b>Zona dos Westerlies</b> — ventos do Oeste circulam sem obstáculos no HS<br>• <b>Topografia plana</b> nas estepes argentinas — sem barreiras orográficas<br>• <b>Rajadas extremas</b> até 130 km/h (Punta Arenas) documentadas<br>• <b>Consistência anual</b> — baixa sazonalidade vs. outras regiões<br>• <b>Infraestrutura</b> em desenvolvimento: parques eólicos já em operação",
        "discovery_label": "ANÁLISE E DESCOBERTAS",
        "discovery_title": "O que os Dados Revelaram",
        "discoveries": [
            ("💨", "Punta Arenas — a mais ventosa das quatro cidades",
             "Com velocidade média de 30,2 km/h e rajadas de até 130 km/h, Punta Arenas lidera o ranking de potencial eólico entre as cidades estudadas. O potencial instalável estimado de 4.200 MW tornaria a cidade capaz de exportar energia limpa para toda a região."),
            ("⚡", "Fator de capacidade >60% — padrão mundial excepcional",
             "A Patagônia argentina registra fatores de capacidade eólica acima de 60%, mais que o dobro da média global (~35%). Isso significa que cada MW instalado gera quase o dobro de energia que em regiões convencionais, tornando o custo por MWh gerado extraordinariamente competitivo."),
            ("🌊", "Os Westerlies — vento que move navios há séculos",
             "Os ventos Westerlies, que historicamente guiaram as rotas dos veleiros entre os Roaring Forties e os Screaming Sixties, são a fonte do potencial eólico patagônico. Sem obstáculos terrestres entre o Pacífico e o Atlântico Sul, esses ventos chegam às cidades patagônicas com energia cinética extraordinária."),
            ("🏙️", "Puerto Williams — o vento no fim do mundo",
             "A experiência em Puerto Williams (out 2025) confirmou que mesmo na cidade mais austral do mundo os ventos Westerlies chegam com força notável. Acrescente-se o terremoto M7+ de 02 mai 2025 e fica evidente a intensidade das forças naturais atuando nesta região extrema."),
            ("📊", "9.500+ MW de potencial combinado — o gigante adormecido",
             "A soma dos potenciais de Punta Arenas (4.200 MW), Puerto Natales (1.800 MW) e Rio Gallegos (3.500 MW) ultrapassa 9.500 MW. Para referência, o Brasil inteiro tinha ~30 GW de capacidade eólica instalada em 2024 — a Patagônia, com três cidades, já tem potencial para 30% disso."),
            ("🌱", "CO₂ evitado — o argumento climático decisivo",
             "Se apenas 20% do potencial combinado fosse aproveitado (~1.900 MW instalados), a geração anual evitaria cerca de 700.000 toneladas de CO₂ — equivalente ao plantio de 50 milhões de árvores ou à retirada de 150.000 veículos das ruas da Patagônia."),
        ],
        "conclusion_label": "CONCLUSÃO",
        "conclusion_title": "A Patagônia como Solução Climática Global",
        "conclusion_text": "Percorrer Punta Arenas, Puerto Natales, Rio Gallegos e Puerto Williams entre novembro de 2024 e outubro de 2025 não foi apenas uma experiência geográfica — foi uma constatação física dos dados. O vento que dificulta caminhar em linha reta em Punta Arenas é o mesmo que, canalizado por turbinas, pode alimentar cidades inteiras com energia 100% limpa. A Patagônia é um recurso renovável global aguardando escala.",
        "conclusion_author": "Amauri Almeida · Pesquisa & Observação de Campo · Patagônia · Nov 2024–Out 2025",
        "field_label": "OBSERVAÇÃO PESSOAL DE CAMPO",
        "field_title": "11 Meses Percorrendo a Patagônia",
        "field_instructions_title": "📁 Como adicionar suas fotos",
        "field_instructions": "Coloque suas fotos na pasta <code>assets/campo/</code> com os nomes exatos abaixo. O sistema detecta e exibe automaticamente.",
        "photos": [
            {
                "emoji": "🌬️",
                "cidade": "Punta Arenas",
                "titulo": "Punta Arenas — Novembro 2024",
                "desc": "Punta Arenas, Chile — Estreito de Magalhães. Velocidade média do vento: 30,2 km/h · Rajadas de até 130 km/h documentadas. A cidade mais ventosa do estudo, localizada na zona dos Westerlies (Furious Fifties, ~53°S). Potencial instalável estimado: 4.200 MW — o que tornaria Punta Arenas um hub exportador de energia limpa para toda a Patagônia.",
                "path": "assets/campo/01_punta_arenas_nov2024.JPG",
                "legenda": "Punta Arenas · Chile · Novembro 2024 · Westerlies ~53°S",
                "coords": "53.1°S · 70.9°O",
                "vento": "30,2 km/h média",
                "pot": "4.200 MW",
                "mes": "Nov/2024",
                "cor": "#1A3A6E"
            },
            {
                "emoji": "🏔️",
                "cidade": "Puerto Natales",
                "titulo": "Puerto Natales — Dezembro 2024",
                "desc": "Puerto Natales, Chile — porta de entrada da Torres del Paine. Velocidade média: 26,8 km/h · Rajadas de até 104 km/h. A menor das cidades estudadas em potencial (~1.800 MW) mas com ventos notavelmente consistentes, reforçados pelos canais e braços de mar da Patagônia chilena que canalizam os Westerlies.",
                "path": "assets/campo/02_puerto_natales_dez2024.JPG",
                "legenda": "Puerto Natales · Chile · Dezembro 2024 · Canais Patagônicos ~51°S",
                "coords": "51.7°S · 72.5°O",
                "vento": "26,8 km/h média",
                "pot": "1.800 MW",
                "mes": "Dez/2024",
                "cor": "#1B3A1E"
            },
            {
                "emoji": "🌪️",
                "cidade": "Rio Gallegos",
                "titulo": "Rio Gallegos — Março 2025",
                "desc": "Rio Gallegos, Argentina — na margem norte do Estreito de Magalhães. Velocidade média: 27,1 km/h · Rajadas de até 100 km/h. Segunda maior cidade da Patagônia argentina com 3.500 MW de potencial eólico. A estepe plana e sem obstáculos amplifica o efeito dos Westerlies, conferindo à região um dos melhores fatores de capacidade eólica do mundo.",
                "path": "assets/campo/03_rio_gallegos_mar2025.jpg",
                "legenda": "Rio Gallegos · Argentina · Março 2025 · Estepe Patagônica ~51°S",
                "coords": "51.6°S · 69.2°O",
                "vento": "27,1 km/h média",
                "pot": "3.500 MW",
                "mes": "Mar/2025",
                "cor": "#5C3D1E"
            },
            {
                "emoji": "🏁",
                "cidade": "Puerto Williams",
                "titulo": "Puerto Williams — Outubro 2025",
                "desc": "Puerto Williams, Chile — Isla Navarino — o assentamento humano permanente mais austral do mundo (~55°S). Base dos Screaming Sixties, os ventos mais intensos do planeta. Em 02 de maio de 2025, a cidade registrou um terremoto de magnitude M7+. Encerramento da jornada patagônica com a confirmação de que forças naturais extremas coexistem nessa região única do planeta.",
                "path": "assets/campo/04_puerto_williams_out2025.jpg",
                "legenda": "Puerto Williams · Chile · Outubro 2025 · Screaming Sixties ~55°S",
                "coords": "54.9°S · 67.6°O",
                "vento": "Screaming Sixties",
                "pot": "Ponto extremo",
                "mes": "Out/2025",
                "cor": "#8B2515",
                "destaque": True
            },
        ],
        "timeline_field_label": "ROTEIRO DE CAMPO — PATAGÔNIA",
        "timeline_field_items": [
            ("Nov 2024", "Punta Arenas — Chile", "Estreito de Magalhães · Cidade mais ventosa do estudo · 30,2 km/h média · Potencial de 4.200 MW"),
            ("Dez 2024", "Puerto Natales — Chile", "Torres del Paine · Ventos dos canais patagônicos · 26,8 km/h média · 1.800 MW de potencial"),
            ("Mar 2025", "Rio Gallegos — Argentina", "Estepe plana · Westerlies sem obstáculos · 27,1 km/h · 3.500 MW de potencial instalável"),
            ("Mai 2025", "Terremoto M7+ · Puerto Williams", "02 de maio de 2025 · Magnitude 7+ · Isla Navarino · Forças naturais extremas da Patagônia"),
            ("Mai–Set 2025", "Residência em Puerto Williams", "Meses de convivência com os Westerlies no extremo sul · Screaming Sixties em campo"),
            ("Out 2025", "Encerramento · Puerto Williams", "11 meses de observação patagônica concluídos · Dados e registros consolidados"),
        ],
        "sources_label": "FONTES DE DADOS",
        "sources_title": "Fontes Científicas & Dados",
        "tech_label": "TECNOLOGIAS UTILIZADAS",
        "footer_title": "🌬️ Amauri Almeida",
        "footer_desc": "Tecnólogo em Gestão Ambiental · FATEC Jundiaí (3º ENADE)<br>Pós-Graduação em IA, Machine Learning & Data Science · Ciência de Dados & Big Data<br>Análise e Desenvolvimento de Sistemas · FACINT Maringá",
        "footer_links": "📍 Patagônia · Chile & Argentina (Nov 2024–Out 2025) | Fernandópolis · SP · Brasil",
        "select_city": "Selecione a cidade",
        "turbines_label": "Número de turbinas",
        "power_label": "Potência por turbina (MW)",
        "year_label": "Selecione o ano",
    },
    "es": {
        "page_title": "Potencial Eólico · Patagonia",
        "hero_tag": "ANÁLISIS CIENTÍFICO · PATAGONIA SUR · CHILE & ARGENTINA · NOV 2024–OCT 2025",
        "hero_title": "Potencial Eólico\nde la Patagonia",
        "hero_subtitle": "Análisis comparativo del potencial de generación de energía eólica en Punta Arenas, Puerto Natales, Río Gallegos y Puerto Williams — cuatro de las ciudades más ventosas del planeta, recorridas personalmente entre noviembre de 2024 y octubre de 2025.",
        "badge1": "💨 Westerlies · 40°S–60°S",
        "badge2": "⚡ 9.500+ MW potencial",
        "badge3": "Chile & Argentina",
        "badge4": "Nov 2024 — Oct 2025",
        "badge5": "OPEN-METEO · ERA5 · GWA",
        "m1": "Vel. media Punta Arenas",
        "m2": "Factor de capacidad (PAT)",
        "m3": "Ráfaga máx. registrada",
        "m4": "Potencial total estimado",
        "tab1": "🗺️ Mapa & Análisis",
        "tab2": "🔬 Metodología & Pipeline",
        "tab3": "💡 Lo que Descubrimos",
        "tab4": "📷 En Campo",
        "tab5": "📚 Fuentes & Créditos",
        "map_label": "GEOLOCALIZACIÓN — CORREDOR DE VIENTOS",
        "map_title": "Mapa Interactivo — Ciudades & Potencial Eólico",
        "map_hint": "💨 <strong>Haga clic en los marcadores</strong> para ver datos de viento, potencial instalado y características de cada ciudad. Los círculos son proporcionales a la velocidad media del viento.",
        "chart_label": "ANÁLISIS DEL VIENTO",
        "wind_monthly_title": "Velocidad Media Mensual del Viento — 2020–2024",
        "wind_y": "Velocidad (km/h)",
        "rose_title": "Rosa de los Vientos — Distribución Direccional",
        "annual_title": "Evolución Anual de la Velocidad Media (2020–2024)",
        "annual_y": "Velocidad media anual (km/h)",
        "simulator_label": "SIMULADOR DE GENERACIÓN EÓLICA",
        "simulator_title": "Calculadora de Potencial Energético",
        "sim_city": "Ciudad",
        "sim_turbines": "Número de turbinas",
        "sim_power": "Potencia por turbina (MW)",
        "sim_result_gwh": "GWh / año estimados",
        "sim_result_homes": "hogares atendidos",
        "sim_result_co2": "t CO₂ evitadas/año",
        "capacity_title": "Factor de Capacidad por Ciudad",
        "method_label": "CIENCIA DEL VIENTO",
        "method_title": "Pregunta & Metodología",
        "sci_question_title": "❓ Pregunta Central",
        "sci_question": "\"¿Cuál es el potencial real de generación de energía eólica en las ciudades más ventosas de la Patagonia, y cómo la experiencia directa de campo refuerza los datos científicos sobre la fuerza y consistencia de los vientos Westerlies en esta región?\"",
        "pipeline_label": "PIPELINE DE ANÁLISIS",
        "steps": [
            ("1", "Recolección de Datos — Open-Meteo ERA5 (2020–2024)", "Datos horarios de velocidad y dirección del viento para las tres ciudades vía Open-Meteo Historical API (reanálisis ERA5 de ECMWF). 5 años completos con resolución horaria."),
            ("2", "Experiencia de Campo — Patagonia (Nov 2024–Oct 2025)", "11 meses recorriendo las cuatro ciudades estudiadas. Vivencia directa de los vientos Westerlies — incluyendo el terremoto M7+ en Puerto Williams el 02 may 2025."),
            ("3", "Física del Viento — Ley de la Potencia Cúbica", "La densidad de potencia eólica sigue P/A = ½ × ρ × v³, donde la velocidad entra al cubo. Duplicar la velocidad genera 8× más energía. Factores de capacidad superiores al 60% vs. media global del 35%."),
            ("4", "Simulador de Turbinas", "Cálculo interactivo: GWh/año = P_turbina × N_turbinas × Factor_Capacidad × 8.760h. Configuración de turbinas y potencia unitaria con cálculo automático de CO₂ evitado."),
            ("5", "Rosa de los Vientos y Análisis Direccional", "Distribución direccional de los vientos. En la Patagonia, los Westerlies confieren dominancia al sector WSW-W-WNW con consistencia excepcional."),
            ("6", "Potencial Instalado e Impacto Ambiental", "Punta Arenas 4.200 MW · Puerto Natales 1.800 MW · Río Gallegos 3.500 MW. La generación combinada evitaría ~3,5 Mt CO₂/año."),
        ],
        "physics_title": "⚙️ Física del Viento",
        "physics_text": "• <b>Ley cúbica:</b> P/A = ½ × ρ × v³ · (v³ = 8× más energía al doblar v)<br>• <b>Densidad del aire:</b> ~1,20 kg/m³ al nivel del mar<br>• <b>Factor de capacidad PAT:</b> >60% vs. media global 35%<br>• <b>Vientos Westerlies:</b> 40°S–60°S · sin obstáculos terrestres<br>• <b>Roaring Forties / Furious Fifties / Screaming Sixties</b>",
        "westerlies_title": "🌍 ¿Por qué la Patagonia?",
        "westerlies_text": "• <b>Zona Westerlies</b> — vientos del Oeste sin obstáculos en el HS<br>• <b>Topografía plana</b> en las estepas argentinas<br>• <b>Ráfagas extremas</b> hasta 130 km/h (Punta Arenas)<br>• <b>Consistencia anual</b> — baja estacionalidad<br>• <b>Infraestructura</b> en desarrollo: parques eólicos ya en operación",
        "discovery_label": "ANÁLISIS Y HALLAZGOS",
        "discovery_title": "Lo que los Datos Revelaron",
        "discoveries": [
            ("💨", "Punta Arenas — la más ventosa de las cuatro ciudades", "Con velocidad media de 30,2 km/h y ráfagas de hasta 130 km/h, Punta Arenas lidera el potencial eólico. El potencial instalable estimado de 4.200 MW la haría exportadora de energía limpia."),
            ("⚡", "Factor de capacidad >60% — estándar mundial excepcional", "La Patagonia argentina registra factores de capacidad superiores al 60%, más del doble de la media global (~35%). Cada MW instalado genera casi el doble de energía que en regiones convencionales."),
            ("🌊", "Los Westerlies — viento que movió navíos por siglos", "Los vientos Westerlies, que históricamente guiaron rutas de veleros entre los Roaring Forties y los Screaming Sixties, son la fuente del potencial eólico patagónico."),
            ("🏙️", "Puerto Williams — el viento en el fin del mundo", "La experiencia en Puerto Williams (oct 2025) confirmó que incluso en la ciudad más austral del mundo los vientos Westerlies llegan con notable fuerza."),
            ("📊", "9.500+ MW de potencial combinado — el gigante dormido", "La suma de los potenciales de las tres ciudades supera los 9.500 MW — equivalente al 30% de la capacidad eólica instalada de Brasil en 2024."),
            ("🌱", "CO₂ evitado — el argumento climático decisivo", "Aprovechando solo el 20% del potencial (~1.900 MW), se evitarían ~700.000 t CO₂/año — equivalente a 50 millones de árboles plantados."),
        ],
        "conclusion_label": "CONCLUSIÓN",
        "conclusion_title": "La Patagonia como Solución Climática Global",
        "conclusion_text": "Recorrer Punta Arenas, Puerto Natales, Río Gallegos y Puerto Williams entre noviembre de 2024 y octubre de 2025 fue una constatación física de los datos. El viento que dificulta caminar en línea recta en Punta Arenas es el mismo que, canalizado por turbinas, puede alimentar ciudades enteras con energía 100% limpia.",
        "conclusion_author": "Amauri Almeida · Investigación & Observación de Campo · Patagonia · Nov 2024–Oct 2025",
        "field_label": "OBSERVACIÓN PERSONAL DE CAMPO",
        "field_title": "11 Meses Recorriendo la Patagonia",
        "field_instructions_title": "📁 Cómo agregar sus fotos",
        "field_instructions": "Coloque sus fotos en la carpeta <code>assets/campo/</code> con los nombres exactos indicados.",
        "photos": [
            {"emoji": "🌬️", "cidade": "Punta Arenas", "titulo": "Punta Arenas — Noviembre 2024", "desc": "Punta Arenas, Chile — Estrecho de Magallanes. Velocidad media: 30,2 km/h · Ráfagas hasta 130 km/h. Ciudad más ventosa del estudio · Potencial: 4.200 MW.", "path": "assets/campo/01_punta_arenas_nov2024.JPG", "legenda": "Punta Arenas · Chile · Noviembre 2024 · Westerlies ~53°S", "coords": "53.1°S · 70.9°O", "vento": "30,2 km/h media", "pot": "4.200 MW", "mes": "Nov/2024", "cor": "#1A3A6E"},
            {"emoji": "🏔️", "cidade": "Puerto Natales", "titulo": "Puerto Natales — Diciembre 2024", "desc": "Puerto Natales, Chile — puerta de Torres del Paine. Velocidad media: 26,8 km/h · Ráfagas hasta 104 km/h. Potencial: 1.800 MW.", "path": "assets/campo/02_puerto_natales_dez2024.JPG", "legenda": "Puerto Natales · Chile · Diciembre 2024 · Canales Patagónicos ~51°S", "coords": "51.7°S · 72.5°O", "vento": "26,8 km/h media", "pot": "1.800 MW", "mes": "Dic/2024", "cor": "#1B3A1E"},
            {"emoji": "🌪️", "cidade": "Rio Gallegos", "titulo": "Río Gallegos — Marzo 2025", "desc": "Río Gallegos, Argentina — estepa patagónica. Velocidad media: 27,1 km/h · Ráfagas hasta 100 km/h. Potencial: 3.500 MW.", "path": "assets/campo/03_rio_gallegos_mar2025.jpg", "legenda": "Río Gallegos · Argentina · Marzo 2025 · Estepa Patagónica ~51°S", "coords": "51.6°S · 69.2°O", "vento": "27,1 km/h media", "pot": "3.500 MW", "mes": "Mar/2025", "cor": "#5C3D1E"},
            {"emoji": "🏁", "cidade": "Puerto Williams", "titulo": "Puerto Williams — Octubre 2025", "desc": "Puerto Williams, Chile — Isla Navarino — el asentamiento permanente más austral del mundo (~55°S). Screaming Sixties · Terremoto M7+ en 02 may 2025.", "path": "assets/campo/04_puerto_williams_out2025.jpg", "legenda": "Puerto Williams · Chile · Octubre 2025 · Screaming Sixties ~55°S", "coords": "54.9°S · 67.6°O", "vento": "Screaming Sixties", "pot": "Punto extremo", "mes": "Oct/2025", "cor": "#8B2515", "destaque": True},
        ],
        "timeline_field_label": "ITINERARIO DE CAMPO — PATAGONIA",
        "timeline_field_items": [
            ("Nov 2024", "Punta Arenas — Chile", "Estrecho de Magallanes · Ciudad más ventosa · 30,2 km/h · 4.200 MW"),
            ("Dic 2024", "Puerto Natales — Chile", "Torres del Paine · Vientos de canales patagónicos · 26,8 km/h · 1.800 MW"),
            ("Mar 2025", "Río Gallegos — Argentina", "Estepa plana · Westerlies sin obstáculos · 27,1 km/h · 3.500 MW"),
            ("May 2025", "Terremoto M7+ · Puerto Williams", "02 de mayo de 2025 · Isla Navarino · Fuerzas naturales extremas"),
            ("May–Sep 2025", "Residencia en Puerto Williams", "Meses de convivencia con los Westerlies en el extremo sur"),
            ("Oct 2025", "Cierre · Puerto Williams", "11 meses de observación patagónica completados"),
        ],
        "sources_label": "FUENTES DE DATOS",
        "sources_title": "Fuentes Científicas & Datos",
        "tech_label": "TECNOLOGÍAS UTILIZADAS",
        "footer_title": "🌬️ Amauri Almeida",
        "footer_desc": "Tecnólogo en Gestión Ambiental · FATEC Jundiaí<br>Posgrado en IA, Machine Learning & Data Science · Ciencia de Datos & Big Data<br>Análisis y Desarrollo de Sistemas · FACINT Maringá",
        "footer_links": "📍 Patagonia · Chile & Argentina (Nov 2024–Oct 2025) | Fernandópolis · SP · Brasil",
        "select_city": "Seleccione la ciudad",
        "turbines_label": "Número de turbinas",
        "power_label": "Potencia por turbina (MW)",
        "year_label": "Seleccione el año",
    },
    "en": {
        "page_title": "Wind Energy Potential · Patagonia",
        "hero_tag": "SCIENTIFIC ANALYSIS · SOUTHERN PATAGONIA · CHILE & ARGENTINA · NOV 2024–OCT 2025",
        "hero_title": "Wind Energy Potential\nof Patagonia",
        "hero_subtitle": "Comparative analysis of wind energy generation potential in Punta Arenas, Puerto Natales, Río Gallegos and Puerto Williams — four of the windiest cities on the planet, personally visited between November 2024 and October 2025.",
        "badge1": "💨 Westerlies · 40°S–60°S",
        "badge2": "⚡ 9,500+ MW potential",
        "badge3": "Chile & Argentina",
        "badge4": "Nov 2024 — Oct 2025",
        "badge5": "OPEN-METEO · ERA5 · GWA",
        "m1": "Avg. wind · Punta Arenas",
        "m2": "Capacity factor (PAT)",
        "m3": "Max. recorded gust",
        "m4": "Total estimated potential",
        "tab1": "🗺️ Map & Analysis",
        "tab2": "🔬 Methodology & Pipeline",
        "tab3": "💡 What We Found",
        "tab4": "📷 Field Research",
        "tab5": "📚 Sources & Credits",
        "map_label": "GEOLOCATION — WIND CORRIDOR",
        "map_title": "Interactive Map — Cities & Wind Potential",
        "map_hint": "💨 <strong>Click the markers</strong> to view wind data, installed potential and characteristics of each city. Circles are proportional to mean wind speed.",
        "chart_label": "WIND ANALYSIS",
        "wind_monthly_title": "Monthly Mean Wind Speed — 2020–2024",
        "wind_y": "Speed (km/h)",
        "rose_title": "Wind Rose — Directional Distribution",
        "annual_title": "Annual Mean Wind Speed Evolution (2020–2024)",
        "annual_y": "Annual mean speed (km/h)",
        "simulator_label": "WIND GENERATION SIMULATOR",
        "simulator_title": "Energy Potential Calculator",
        "sim_city": "City",
        "sim_turbines": "Number of turbines",
        "sim_power": "Power per turbine (MW)",
        "sim_result_gwh": "Estimated GWh / year",
        "sim_result_homes": "households supplied",
        "sim_result_co2": "t CO₂ avoided/year",
        "capacity_title": "Capacity Factor by City",
        "method_label": "WIND SCIENCE",
        "method_title": "Research Question & Methodology",
        "sci_question_title": "❓ Central Question",
        "sci_question": "\"What is the real wind energy generation potential of the windiest cities in Patagonia, and how does direct field experience reinforce scientific data on the strength and consistency of Westerly winds in this region?\"",
        "pipeline_label": "ANALYSIS PIPELINE",
        "steps": [
            ("1", "Data Collection — Open-Meteo ERA5 (2020–2024)", "Hourly wind speed and direction data for three cities via Open-Meteo Historical API (ERA5 reanalysis from ECMWF). 5 complete years at hourly resolution, processed for monthly/annual means and directional distributions."),
            ("2", "Field Experience — Patagonia (Nov 2024–Oct 2025)", "11 months across four cities: Punta Arenas (Nov 2024), Puerto Natales (Dec 2024), Río Gallegos (Mar 2025) and Puerto Williams (through Oct 2025). Direct experience of the Westerlies — including the M7+ earthquake in Puerto Williams on May 2, 2025."),
            ("3", "Wind Physics — Cubic Power Law", "Wind power density follows P/A = ½ × ρ × v³, where speed enters as a cube. Doubling wind speed = 8× more energy. Patagonia's capacity factors above 60% vs. global average of 35%."),
            ("4", "Turbine Simulator", "Interactive calculation: GWh/yr = P_turbine × N_turbines × Capacity_Factor × 8,760h. Configurable turbine count and unit power with automatic CO₂ avoided calculation."),
            ("5", "Wind Rose and Directional Analysis", "Directional wind distribution. In Patagonia, the Westerlies give WSW-W-WNW dominance with exceptional consistency — key for optimal turbine positioning."),
            ("6", "Installed Potential and Environmental Impact", "Punta Arenas 4,200 MW · Puerto Natales 1,800 MW · Río Gallegos 3,500 MW. Combined generation would avoid ~3.5 Mt CO₂/year."),
        ],
        "physics_title": "⚙️ Wind Physics",
        "physics_text": "• <b>Cubic law:</b> P/A = ½ × ρ × v³ · (v³ = 8× more energy by doubling v)<br>• <b>Air density:</b> ~1.20 kg/m³ at sea level<br>• <b>PAT capacity factor:</b> >60% vs. global average 35%<br>• <b>Westerly winds:</b> 40°S–60°S · almost no terrestrial obstacles<br>• <b>Roaring Forties / Furious Fifties / Screaming Sixties</b>",
        "westerlies_title": "🌍 Why Patagonia?",
        "westerlies_text": "• <b>Westerlies zone</b> — westerly winds circulate unobstructed in SH<br>• <b>Flat topography</b> on Argentine steppes<br>• <b>Extreme gusts</b> up to 130 km/h (Punta Arenas)<br>• <b>Annual consistency</b> — low seasonality vs. other regions<br>• <b>Infrastructure</b> developing: wind farms already operational",
        "discovery_label": "ANALYSIS & FINDINGS",
        "discovery_title": "What the Data Revealed",
        "discoveries": [
            ("💨", "Punta Arenas — windiest of the four cities", "With a mean speed of 30.2 km/h and gusts up to 130 km/h, Punta Arenas leads wind potential. The estimated 4,200 MW installable would make it a clean energy export hub."),
            ("⚡", "Capacity factor >60% — exceptional global standard", "Patagonia registers capacity factors above 60%, more than double the global average (~35%). Each installed MW generates nearly twice the energy of conventional regions."),
            ("🌊", "The Westerlies — wind that moved ships for centuries", "The Westerly winds that historically guided sailing routes between the Roaring Forties and Screaming Sixties are the source of Patagonia's wind potential."),
            ("🏙️", "Puerto Williams — wind at the end of the world", "The experience in Puerto Williams (Oct 2025) confirmed that even in the world's southernmost city the Westerlies arrive with remarkable force."),
            ("📊", "9,500+ MW combined potential — the sleeping giant", "The sum of potentials of the three cities exceeds 9,500 MW — equivalent to 30% of Brazil's entire installed wind capacity in 2024."),
            ("🌱", "CO₂ avoided — the decisive climate argument", "Using just 20% of the potential (~1,900 MW) would avoid ~700,000 t CO₂/year — equivalent to planting 50 million trees."),
        ],
        "conclusion_label": "CONCLUSION",
        "conclusion_title": "Patagonia as a Global Climate Solution",
        "conclusion_text": "Travelling through Punta Arenas, Puerto Natales, Río Gallegos and Puerto Williams between November 2024 and October 2025 was a physical confirmation of the data. The wind that makes walking in a straight line difficult in Punta Arenas is the same that, channelled through turbines, can power entire cities with 100% clean energy.",
        "conclusion_author": "Amauri Almeida · Research & Field Observation · Patagonia · Nov 2024–Oct 2025",
        "field_label": "PERSONAL FIELD OBSERVATION",
        "field_title": "11 Months Across Patagonia",
        "field_instructions_title": "📁 How to add your photos",
        "field_instructions": "Place your photos in the <code>assets/campo/</code> folder with the exact file names shown.",
        "photos": [
            {"emoji": "🌬️", "cidade": "Punta Arenas", "titulo": "Punta Arenas — November 2024", "desc": "Punta Arenas, Chile — Strait of Magellan. Mean speed: 30.2 km/h · Gusts up to 130 km/h. Windiest city in the study · Potential: 4,200 MW.", "path": "assets/campo/01_punta_arenas_nov2024.jpg", "legenda": "Punta Arenas · Chile · November 2024 · Westerlies ~53°S", "coords": "53.1°S · 70.9°W", "vento": "30.2 km/h mean", "pot": "4,200 MW", "mes": "Nov/2024", "cor": "#1A3A6E"},
            {"emoji": "🏔️", "cidade": "Puerto Natales", "titulo": "Puerto Natales — December 2024", "desc": "Puerto Natales, Chile — gateway to Torres del Paine. Mean speed: 26.8 km/h · Gusts up to 104 km/h. Potential: 1,800 MW.", "path": "assets/campo/02_puerto_natales_dez2024.JPG", "legenda": "Puerto Natales · Chile · December 2024 · Patagonian Channels ~51°S", "coords": "51.7°S · 72.5°W", "vento": "26.8 km/h mean", "pot": "1,800 MW", "mes": "Dec/2024", "cor": "#1B3A1E"},
            {"emoji": "🌪️", "cidade": "Rio Gallegos", "titulo": "Río Gallegos — March 2025", "desc": "Río Gallegos, Argentina — Patagonian steppe. Mean speed: 27.1 km/h · Gusts up to 100 km/h. Potential: 3,500 MW.", "path": "assets/campo/03_rio_gallegos_mar2025.jpg", "legenda": "Río Gallegos · Argentina · March 2025 · Patagonian Steppe ~51°S", "coords": "51.6°S · 69.2°W", "vento": "27.1 km/h mean", "pot": "3,500 MW", "mes": "Mar/2025", "cor": "#5C3D1E"},
            {"emoji": "🏁", "cidade": "Puerto Williams", "titulo": "Puerto Williams — October 2025", "desc": "Puerto Williams, Chile — Isla Navarino — world's southernmost permanent settlement (~55°S). Screaming Sixties · M7+ earthquake on May 2, 2025.", "path": "assets/campo/04_puerto_williams_out2025.jpg", "legenda": "Puerto Williams · Chile · October 2025 · Screaming Sixties ~55°S", "coords": "54.9°S · 67.6°W", "vento": "Screaming Sixties", "pot": "Extreme point", "mes": "Oct/2025", "cor": "#8B2515", "destaque": True},
        ],
        "timeline_field_label": "FIELD ITINERARY — PATAGONIA",
        "timeline_field_items": [
            ("Nov 2024", "Punta Arenas — Chile", "Strait of Magellan · Windiest city · 30.2 km/h · 4,200 MW"),
            ("Dec 2024", "Puerto Natales — Chile", "Torres del Paine · Patagonian channel winds · 26.8 km/h · 1,800 MW"),
            ("Mar 2025", "Río Gallegos — Argentina", "Flat steppe · Unobstructed Westerlies · 27.1 km/h · 3,500 MW"),
            ("May 2025", "M7+ Earthquake · Puerto Williams", "May 2, 2025 · Isla Navarino · Extreme natural forces of Patagonia"),
            ("May–Sep 2025", "Residence in Puerto Williams", "Months living with the Westerlies at the far south"),
            ("Oct 2025", "Closure · Puerto Williams", "11 months of Patagonian observation completed"),
        ],
        "sources_label": "DATA SOURCES",
        "sources_title": "Scientific Sources & Data",
        "tech_label": "TECHNOLOGIES USED",
        "footer_title": "🌬️ Amauri Almeida",
        "footer_desc": "Environmental Management Technologist · FATEC Jundiaí<br>Post-Grad in AI, Machine Learning & Data Science · Data Science & Big Data<br>Systems Analysis and Development · FACINT Maringá",
        "footer_links": "📍 Patagonia · Chile & Argentina (Nov 2024–Oct 2025) | Fernandópolis · SP · Brazil",
        "select_city": "Select city",
        "turbines_label": "Number of turbines",
        "power_label": "Power per turbine (MW)",
        "year_label": "Select year",
    },
}

# ── SELETOR ──────────────────────────────────────────────────
def render_lang_selector():
    c0, c1, c2, c3 = st.columns([8, 1, 1, 1])
    with c1:
        if st.button("🇧🇷 PT", use_container_width=True,
                     type="primary" if st.session_state.lang == "pt" else "secondary"):
            st.session_state.lang = "pt"; st.rerun()
    with c2:
        if st.button("🇪🇸 ES", use_container_width=True,
                     type="primary" if st.session_state.lang == "es" else "secondary"):
            st.session_state.lang = "es"; st.rerun()
    with c3:
        if st.button("🇺🇸 EN", use_container_width=True,
                     type="primary" if st.session_state.lang == "en" else "secondary"):
            st.session_state.lang = "en"; st.rerun()

render_lang_selector()
T = TRANSLATIONS[st.session_state.lang]

# ── ESTILOS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');
:root{
  --wind:#1A3A6E;--wind-mid:#2555A0;--wind-light:#3A7ACA;
  --sky:#56B3F0;--sky-light:#A8D8F0;
  --slate:#2D3A4A;--cream:#F4F6FA;--warm-gray:#6A7888;
  --green:#2D7A3A;--amber:#C47D0E;--danger:#8B2515;--black:#0D1117;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--cream);color:var(--black);}
.hero-wrap{
  background:linear-gradient(135deg,var(--slate) 0%,var(--wind) 50%,#1E4A8A 100%);
  border-radius:20px;padding:3rem 2.5rem 2rem;margin-bottom:2rem;position:relative;overflow:hidden;
}
.hero-wrap::before{content:"🌬️";font-size:200px;position:absolute;right:-20px;top:-30px;opacity:0.05;}
.hero-tag{background:#A8D8F0;color:var(--wind);font-family:'DM Mono',monospace;font-size:0.7rem;font-weight:bold;letter-spacing:2px;padding:4px 12px;border-radius:4px;display:inline-block;margin-bottom:1rem;text-transform:uppercase;}
.hero-title{font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:900;color:#fff;line-height:1.15;margin-bottom:0.8rem;white-space:pre-line;}
.hero-subtitle{font-size:1rem;color:rgba(255,255,255,0.78);max-width:680px;line-height:1.6;margin-bottom:1.5rem;}
.hero-badges{display:flex;gap:10px;flex-wrap:wrap;}
.badge{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);color:rgba(255,255,255,0.85);font-size:0.72rem;font-family:'DM Mono',monospace;padding:5px 12px;border-radius:20px;letter-spacing:0.5px;}
.badge-wind{background:rgba(168,216,240,0.2);border-color:#A8D8F0;color:#A8D8F0;}
.metric-box{background:white;border-radius:16px;padding:1.4rem 1.2rem;border-top:4px solid var(--wind-light);box-shadow:0 2px 12px rgba(0,0,0,0.06);text-align:center;}
.metric-box.sky{border-top-color:var(--sky);}
.metric-box.amber{border-top-color:var(--amber);}
.metric-box.green{border-top-color:var(--green);}
.metric-val{font-family:'Playfair Display',serif;font-size:2.1rem;font-weight:900;color:var(--wind);line-height:1;margin-bottom:0.3rem;}
.metric-label{font-size:0.75rem;color:var(--warm-gray);text-transform:uppercase;letter-spacing:1px;}
.section-label{font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--wind-mid);text-transform:uppercase;letter-spacing:3px;margin-bottom:0.3rem;}
.section-title{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:700;color:var(--wind);margin-bottom:1.2rem;line-height:1.2;}
.info-card{background:white;border-radius:16px;padding:1.5rem;box-shadow:0 2px 12px rgba(0,0,0,0.05);border-left:4px solid var(--wind-light);margin-bottom:1rem;}
.info-card.amber{border-left-color:var(--amber);}
.info-card.green{border-left-color:var(--green);}
.info-card.danger{border-left-color:var(--danger);}
.timeline-item{display:flex;gap:1rem;padding:1rem 0;border-bottom:1px solid #e0e8f0;}
.timeline-year{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:var(--wind-mid);min-width:80px;}
.timeline-title{font-weight:500;color:var(--wind);margin-bottom:0.2rem;}
.timeline-desc{font-size:0.85rem;color:var(--warm-gray);}
.method-step{display:flex;align-items:flex-start;gap:1rem;padding:1rem;background:white;border-radius:12px;margin-bottom:0.8rem;box-shadow:0 1px 6px rgba(0,0,0,0.04);}
.step-num{background:var(--wind-mid);color:white;font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.step-title{font-weight:500;color:var(--wind);font-size:0.95rem;}
.step-desc{font-size:0.82rem;color:var(--warm-gray);margin-top:0.2rem;}
.discovery-box{background:linear-gradient(135deg,#EEF4FF,#D8EAF8);border:2px solid var(--wind-light);border-radius:16px;padding:1.8rem;margin:0.8rem 0;}
.discovery-title{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:var(--wind);margin-bottom:0.5rem;}
.source-badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:0.8rem;}
.source-badge{background:var(--wind);color:white;font-family:'DM Mono',monospace;font-size:0.65rem;padding:4px 10px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;}
.footer-wrap{background:var(--wind);border-radius:20px;padding:2rem;color:rgba(255,255,255,0.8);text-align:center;margin-top:3rem;}
.footer-title{font-family:'Playfair Display',serif;color:#A8D8F0;font-size:1.2rem;margin-bottom:0.5rem;}
.city-card{background:white;border-radius:16px;padding:1.4rem;border-top:5px solid;box-shadow:0 3px 14px rgba(0,0,0,0.07);margin-bottom:0.5rem;transition:box-shadow .2s;}
.city-card:hover{box-shadow:0 6px 22px rgba(0,0,0,0.12);}
.city-card-title{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;margin-bottom:0.4rem;}
.city-card-meta{font-size:0.78rem;font-family:'DM Mono',monospace;color:var(--warm-gray);line-height:1.8;}
.photo-placeholder{background:#EEF4FF;border:2px dashed var(--wind-light);border-radius:12px;padding:2rem;text-align:center;min-height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.photo-emoji{font-size:2.8rem;}
.photo-title{font-weight:600;color:var(--wind);margin:0.5rem 0 0.2rem;font-size:1rem;}
.photo-desc{font-size:0.80rem;color:var(--warm-gray);line-height:1.55;max-width:280px;}
.photo-path{font-size:0.65rem;color:var(--wind-mid);font-family:'DM Mono',monospace;margin-top:0.5rem;background:#D8EAF8;padding:3px 8px;border-radius:4px;}
.photo-meta{font-size:0.7rem;font-family:'DM Mono',monospace;margin-top:0.4rem;line-height:1.7;}
.photo-legenda{font-size:0.72rem;color:var(--warm-gray);font-style:italic;padding:0.5rem 0.8rem;background:#f5f7fa;text-align:center;border-top:1px solid #d8e4f0;}
.photo-destaque{border:3px solid var(--wind-light);border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(26,58,110,0.15);}
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

# Dados mensais simulados (baseados em ERA5 + Open-Meteo)
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
with c1: st.markdown(f'<div class="metric-box"><div class="metric-val">30,2 km/h</div><div class="metric-label">{T["m1"]}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-box sky"><div class="metric-val">>60%</div><div class="metric-label">{T["m2"]}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-box amber"><div class="metric-val">130 km/h</div><div class="metric-label">{T["m3"]}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="metric-box green"><div class="metric-val">9.500 MW</div><div class="metric-label">{T["m4"]}</div></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── ABAS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([T['tab1'], T['tab2'], T['tab3'], T['tab4'], T['tab5']])

# ── TAB 1: MAPA & ANÁLISE ─────────────────────────────────────
with tab1:
    st.markdown(f'<div class="section-label">{T["map_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["map_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-card">{T["map_hint"]}</div>', unsafe_allow_html=True)

    # A chave fica no Streamlit Secrets, nunca no código público.
    try:
        carto_key = st.secrets.get("CARTO_API_KEY", "")
    except Exception:
        carto_key = ""

    # tiles=None impede o Folium de adicionar uma camada base automaticamente.
    mapa = folium.Map(
        location=[-52.5, -70.0],
        zoom_start=5,
        tiles=None,
        control_scale=True,
    )

    if carto_key:
        folium.TileLayer(
            tiles=(
                "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/"
                "{z}/{x}/{y}{r}.png?key=" + carto_key
            ),
            attr=(
                '&copy; <a href="https://www.openstreetmap.org/copyright">'
                "OpenStreetMap</a> contributors &copy; "
                '<a href="https://carto.com/attributions">CARTO</a>'
            ),
            name="CARTO Voyager",
            subdomains="abcd",
            max_zoom=20,
            overlay=False,
            control=True,
        ).add_to(mapa)
    else:
        # Fallback: o app continua funcional sem o Secret configurado.
        folium.TileLayer(
            "OpenStreetMap",
            name="OpenStreetMap",
            attr=(
                '&copy; <a href="https://www.openstreetmap.org/copyright">'
                "OpenStreetMap</a> contributors"
            ),
            control=True,
        ).add_to(mapa)

    for city, d in CITIES.items():
        radius = d["v_media"] * 1200
        pot_str = f"{d['pot_mw']:,} MW" if d['pot_mw'] else "Ponto extremo"
        pop_html = f"""<div style='font-family:sans-serif;min-width:240px;padding:12px'>
            <h4 style='color:{d["cor"]};margin:0 0 8px'>{city}</h4>
            <p style='margin:3px 0;font-size:12px'>🌍 {d["pais"]}</p>
            <p style='margin:3px 0;font-size:12px'>💨 Vel. média: <b>{d["v_media"]} km/h</b></p>
            <p style='margin:3px 0;font-size:12px'>⚡ Rajada máx.: <b>{d["rajada"]} km/h</b></p>
            <p style='margin:3px 0;font-size:12px'>🔋 Potencial: <b>{pot_str}</b></p>
            <p style='margin:3px 0;font-size:12px'>📊 Cap. factor: <b>{d["cap_factor"]*100:.0f}%</b></p>
            <hr style='margin:8px 0;border-color:#eee'>
            <p style='margin:0;font-size:10px;color:#999'>Lat: {d["lat"]:.3f} · Lon: {d["lon"]:.3f}</p>
        </div>"""
        folium.Circle(
            location=[d["lat"], d["lon"]], radius=radius,
            color=d["cor"], fill=True, fill_color=d["cor"], fill_opacity=0.15,
            weight=2, tooltip=f"💨 {city} · {d['v_media']} km/h"
        ).add_to(mapa)
        folium.Marker(
            location=[d["lat"], d["lon"]],
            popup=folium.Popup(pop_html, max_width=270),
            tooltip=f"💨 {city} · {d['v_media']} km/h média",
            icon=folium.Icon(color="blue" if "Chile" in d["pais"] else "red",
                             icon="wind", prefix="fa")
        ).add_to(mapa)

    # Corredor dos Westerlies
    folium.PolyLine(
        locations=[[-40, -80],[-40,-65],[-45,-60],[-50,-60],[-55,-65],[-55,-68]],
        color="#56B3F0", weight=2, opacity=0.5, dash_array="8",
        tooltip="Corredor Westerlies (~40°S–55°S)"
    ).add_to(mapa)

    folium_static(mapa, width=1100, height=500)

    # ─ Cards das cidades ─
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
                💨 {d['v_media']} km/h média<br>
                ⚡ Rajada: {d['rajada']} km/h<br>
                🔋 Potencial: {pot_str}<br>
                📊 Cap. factor: {d['cap_factor']*100:.0f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ─ GRÁFICOS INTERATIVOS ─
    st.markdown(f"<br><div class='section-label'>{T['chart_label']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{T['wind_monthly_title']}</div>", unsafe_allow_html=True)

    # 1. Velocidade Mensal
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
    st.plotly_chart(fig_monthly, use_container_width=True)

    col_r, col_a = st.columns(2)
    with col_r:
        # 2. Rosa dos Ventos
        st.markdown(f"<div style='font-family:DM Mono;font-size:0.75rem;color:#2555A0;letter-spacing:1px'>{T['rose_title']}</div>", unsafe_allow_html=True)
        direcoes = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSO","SO","OSO","O","ONO","NO","NNO"]
        # Distribuição realista Westerlies: pico em O/ONO/OSO
        freqs_pa = [2,1.5,1.5,2,2.5,3,4,5,4,5,8,12,18,16,9,6]
        freqs_rg = [2,2,2,2.5,3,4,5,6,5,6,9,13,16,15,8,5]
        fig_rose = go.Figure()
        fig_rose.add_trace(go.Barpolar(
            r=freqs_pa, theta=direcoes, name="Punta Arenas",
            marker_color="#1A3A6E", opacity=0.75,
            hovertemplate='<b>Punta Arenas</b><br>%{theta}: %{r:.1f}%<extra></extra>'
        ))
        fig_rose.add_trace(go.Barpolar(
            r=freqs_rg, theta=direcoes, name="Rio Gallegos",
            marker_color="#5C3D1E", opacity=0.75,
            hovertemplate='<b>Rio Gallegos</b><br>%{theta}: %{r:.1f}%<extra></extra>'
        ))
        fig_rose.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            polar=dict(
                radialaxis=dict(showticklabels=True, ticks='', range=[0, 20]),
                angularaxis=dict(direction="clockwise")
            ),
            legend=dict(orientation='h', yanchor='top', y=-0.05),
            height=360, font=dict(family='DM Sans'),
            margin=dict(t=10, b=20)
        )
        st.plotly_chart(fig_rose, use_container_width=True)

    with col_a:
        # 3. Evolução Anual
        st.markdown(f"<div style='font-family:DM Mono;font-size:0.75rem;color:#2555A0;letter-spacing:1px'>{T['annual_title']}</div>", unsafe_allow_html=True)
        fig_annual = go.Figure()
        for city, vals in ANNUAL.items():
            fig_annual.add_trace(go.Bar(
                name=city, x=YEARS, y=vals,
                marker_color=CITY_COLORS[city], opacity=0.85,
                hovertemplate=f'<b>{city}</b><br>%{{x}}: %{{y:.1f}} km/h<extra></extra>'
            ))
        fig_annual.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans'), height=360,
            xaxis=dict(showgrid=False, tickmode='array', tickvals=YEARS, ticktext=[str(y) for y in YEARS]),
            yaxis=dict(showgrid=True, gridcolor='#e0e8f0', title=T['annual_y'], range=[18, 36]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_annual, use_container_width=True)

    # ─ SIMULADOR INTERATIVO ─
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
    homes = int(gwh * 1000 / 4.2)  # 4.2 MWh/domicílio/ano Chile/Argentina
    co2 = int(gwh * 1000 * 0.42)    # 0.42 kg CO₂/kWh rede sul-americana

    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.markdown(f"""
        <div class="metric-box">
          <div class="metric-val" style="font-size:2.4rem;color:#1A3A6E">{gwh:,.1f}</div>
          <div class="metric-label">{T['sim_result_gwh']}</div>
        </div>""", unsafe_allow_html=True)
    with res_col2:
        st.markdown(f"""
        <div class="metric-box sky">
          <div class="metric-val" style="font-size:2rem">{homes:,}</div>
          <div class="metric-label">{T['sim_result_homes']}</div>
        </div>""", unsafe_allow_html=True)
    with res_col3:
        st.markdown(f"""
        <div class="metric-box green">
          <div class="metric-val" style="font-size:2rem">{co2:,}</div>
          <div class="metric-label">{T['sim_result_co2']}</div>
        </div>""", unsafe_allow_html=True)

    # Gauge de fator de capacidade
    fig_gauges = go.Figure()
    for i, (city, d) in enumerate(CITIES.items()):
        fig_gauges.add_trace(go.Indicator(
            mode="gauge+number",
            value=d["cap_factor"] * 100,
            number={'suffix': "%", 'font': {'size': 18, 'family': 'Playfair Display', 'color': d["cor"]}},
            gauge={
                'axis': {'range': [0, 80], 'tickwidth': 1},
                'bar': {'color': d["cor"], 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 35], 'color': '#f0f4f8'},
                    {'range': [35, 55], 'color': '#d8e8f5'},
                    {'range': [55, 80], 'color': '#A8D8F0'},
                ],
                'threshold': {'line': {'color': d["cor"], 'width': 3}, 'thickness': 0.75, 'value': d["cap_factor"] * 100}
            },
            title={'text': city, 'font': {'size': 11, 'family': 'DM Sans', 'color': d["cor"]}},
            domain={'row': 0, 'column': i}
        ))
    fig_gauges.update_layout(
        grid={'rows': 1, 'columns': 4, 'pattern': "independent"},
        paper_bgcolor='rgba(0,0,0,0)', height=260,
        font=dict(family='DM Sans'),
        title=dict(text=T['capacity_title'], font=dict(size=13, family='Playfair Display'), x=0.5),
        margin=dict(t=50, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_gauges, use_container_width=True)

# ── TAB 2: METODOLOGIA ────────────────────────────────────────
with tab2:
    st.markdown(f'<div class="section-label">{T["method_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["method_title"]}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="discovery-box">
      <div class="discovery-title">{T['sci_question_title']}</div>
      <p style="font-size:1.05rem;color:#1A3A6E;line-height:1.7"><em>{T['sci_question']}</em></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-label" style="margin-top:1.5rem">{T["pipeline_label"]}</div>', unsafe_allow_html=True)
    for num, title, desc in T['steps']:
        st.markdown(f"""
        <div class="method-step">
          <div class="step-num">{num}</div>
          <div style="flex:1">
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="info-card">
          <strong>{T['physics_title']}</strong><br><br>
          <div style="font-size:0.88rem;line-height:2.1">{T['physics_text']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="info-card amber">
          <strong>{T['westerlies_title']}</strong><br><br>
          <div style="font-size:0.88rem;line-height:2.1">{T['westerlies_text']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="background:linear-gradient(135deg,#EEF4FF,#D8EAF8);margin-top:0.5rem">
      <strong style="color:#1A3A6E">📐 Fórmulas Fundamentais</strong><br><br>
      <div style="font-family:'DM Mono',monospace;font-size:0.85rem;line-height:2.4;color:#1A3A6E">
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
        st.markdown(f"""
        <div class="discovery-box" style="margin-bottom:0.8rem">
          <div style="display:flex;align-items:flex-start;gap:1rem">
            <span style="font-size:1.5rem">{emoji}</span>
            <div>
              <div class="discovery-title">{titulo}</div>
              <p style="color:#1A3A6E;line-height:1.65;font-size:0.93rem;margin:0">{texto}</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="section-label" style="margin-top:1.5rem">{T["conclusion_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-card" style="border-left-color:#1A3A6E;background:linear-gradient(135deg,#EEF4FF,#D8EAF8)">
      <strong style="color:#1A3A6E;font-size:1rem">{T['conclusion_title']}</strong><br><br>
      <p style="color:#1A3A6E;line-height:1.7;font-size:0.93rem">{T['conclusion_text']}</p>
      <p style="color:#2555A0;font-size:0.82rem;margin-bottom:0"><em>{T['conclusion_author']}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Comparativo final
    fig_comp = go.Figure()
    for city, d in list(CITIES.items())[:3]:
        pot = d['pot_mw'] or 0
        fig_comp.add_trace(go.Bar(
            x=[city], y=[pot],
            marker_color=d["cor"], opacity=0.88,
            text=[f"{pot:,} MW"],
            textposition='outside',
            textfont=dict(size=11, color=d["cor"], family="DM Mono"),
            showlegend=False,
            hovertemplate=f'<b>{city}</b><br>{pot:,} MW<extra></extra>'
        ))
    fig_comp.update_layout(
        title=dict(text="Potencial Instalável por Cidade (MW)", font=dict(size=14, family='Playfair Display')),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=340, font=dict(family='DM Sans'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e0e8f0', title="MW instaláveis (estimativa)"),
        margin=dict(t=50, b=20)
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# ── TAB 4: EM CAMPO ───────────────────────────────────────────
with tab4:
    st.markdown(f'<div class="section-label">{T["field_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["field_title"]}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-card amber" style="margin-bottom:1.5rem">
      <strong>{T['field_instructions_title']}</strong><br>
      <div style="font-size:0.88rem;color:#5C3D1E;margin-top:0.4rem">{T['field_instructions']}</div>
    </div>
    """, unsafe_allow_html=True)

    photos = T['photos']
    foto_destaque = next((f for f in photos if f.get("destaque")), None)
    fotos_normais = [f for f in photos if not f.get("destaque")]

    # 3 fotos normais em grade
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

    # Foto destaque — largura total
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

    # Timeline
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{T["timeline_field_label"]}</div>', unsafe_allow_html=True)
    for data, titulo, desc in T['timeline_field_items']:
        st.markdown(f"""
        <div class="timeline-item">
          <div class="timeline-year">{data}</div>
          <div style="flex:1">
            <div class="timeline-title">{titulo}</div>
            <div class="timeline-desc">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 5: FONTES ─────────────────────────────────────────────
with tab5:
    st.markdown(f'<div class="section-label">{T["sources_label"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{T["sources_title"]}</div>', unsafe_allow_html=True)

    fontes = [
        ("OPEN-METEO", "Open-Meteo Historical API — Reanálise ERA5 (ECMWF)",
         "archive-api.open-meteo.com · Dados horários de velocidade e direção do vento 2020–2024 para Punta Arenas, Puerto Natales e Rio Gallegos.", "#1A3A6E"),
        ("GLOBAL WIND ATLAS", "Global Wind Atlas — DTU Wind Energy / World Bank",
         "globalwindatlas.info · Densidade de potência eólica, mapeamento de recursos, atlas global de vento com resolução 250 m.", "#2555A0"),
        ("MDPI 2024", "MDPI Sustainability — DOI: 10.3390/su16146082",
         "Potencial de geração eólica regional na Patagônia. Dados de fator de capacidade e estimativas instaláveis para cidades patagônicas.", "#3A7ACA"),
        ("BNP PARIBAS", "BNP Paribas CIB — Relatório Técnico Eólico Argentina",
         "cib.bnpparibas · Fator de capacidade eólica Argentina: acima de 60% vs. média global 35%. Referência para avaliação de projetos.", "#1B3A1E"),
        ("CLIMATES TRAVEL", "Climates to Travel — Rio Gallegos Climate Profile",
         "climatestotravel.com · Médias mensais de velocidade do vento, temperatura e precipitação para Rio Gallegos.", "#5C3D1E"),
        ("WEATHER SPARK", "Weather Spark — Punta Arenas Climate Summary",
         "weatherspark.com · Perfil climático detalhado de Punta Arenas com dados históricos de vento e rajadas máximas.", "#C47D0E"),
        ("CAMPO", "Observação Pessoal de Campo — Amauri Almeida (Nov 2024–Out 2025)",
         "11 meses percorrendo Punta Arenas, Puerto Natales, Rio Gallegos e Puerto Williams. Vivência direta dos Westerlies e registro dos fenômenos naturais.", "#8B2515"),
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
