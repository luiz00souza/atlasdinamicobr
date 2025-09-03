# -*- coding: utf-8 -*-
import sys
import streamlit as st
import time
import os
import geopandas as gpd
import folium
from branca.element import Template, MacroElement
from streamlit_folium import st_folium
import pandas as pd
import zipfile
import io
import numpy as np

# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(
    page_title="Atlas Interativo do Fundo do Mar (EUNIS)",
    page_icon="🌊",
    layout="wide"
)

# =========================
# DADOS / ARQUIVOS
# =========================
df_teste = pd.read_csv("ALLDATA_onehot_clipped.csv")

# Diretório dos shapefiles subdivididos
shapefiles_folder_subdivididos = "."
os.makedirs(shapefiles_folder_subdivididos, exist_ok=True)

# =========================
# ESTRUTURA DAS CATEGORIAS
# =========================
categories  = {
    'littoral': [ ... ],  # mantém todos os shapefiles como no seu código original
    'circalittoral': [ ... ],
    'offshore': [ ... ],
    'upper_bathyal': [ ... ]
}

categories_individuais = {
    "Zona": ['littoral.shp','circalittoral.shp','offshore.shp','upper_bathyal.shp'],
    "Substrato": ['coarse.shp','mixed.shp','mud.shp','sand.shp','hardrock.shp'],
    "Biogênico": ['terrigeneous.shp','rhodolite.shp','biogenic.shp','recifal.shp']
}

# =========================
# UTILITÁRIOS
# =========================
def load_shapefiles(shapefiles_folder):
    return [f for f in os.listdir(shapefiles_folder) if f.lower().endswith('.shp')]

shapefiles_subdivididos = load_shapefiles(shapefiles_folder_subdivididos)

def fmt_layer_name(name: str) -> str:
    label = name.replace('.shp', '').replace('_', ' ')
    label = (label
             .replace('littoral', 'Litoral')
             .replace('circalittoral', 'Circalitoral')
             .replace('offshore', 'Offshore')
             .replace('upper bathyal', 'Batial Superior')
             .replace('hardrock', 'Rocha/Hard Rock')
             .replace('coarse', 'Cascalho/Coarse')
             .replace('mixed', 'Misto/Mixed')
             .replace('mud', 'Lama/Mud')
             .replace('sand', 'Arenoso/Sand')
             .replace('biogenic', 'Biogênico')
             .replace('recifal', 'Recifal')
             .replace('rhodolite', 'Rodolitos')
             .replace('terrigeneous', 'Terrígeno'))
    return ' '.join([w.capitalize() if w.islower() else w for w in label.split()])

def create_shapefile_zip(shapefiles_folder, selected_layers):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for shp in selected_layers:
            base = os.path.splitext(shp)[0]
            for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                file_path = os.path.join(shapefiles_folder, base + ext)
                if os.path.exists(file_path):
                    zf.write(file_path, arcname=os.path.basename(file_path))
    buffer.seek(0)
    return buffer

def create_map(shapefiles_folder, selected_layers, grid_interval=2):
    # Mapa base
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True)

    # Datum fixo no canto inferior direito
    datum_html = """
    <div style="
        position: absolute; bottom: 40px; left: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 4px 6px;
        border-radius: 4px; font-size: 11px; box-shadow: 0 0 4px rgba(0,0,0,0.2);
    ">Datum: WGS84</div>
    """
    m.get_root().html.add_child(folium.Element(datum_html))

    # Definir cores
    layer_colors = [ ... ]  # mantém as cores originais

    bounds = []
    legend_entries = []

    for idx, shp in enumerate(selected_layers):
        filepath = os.path.join(shapefiles_folder, shp)
        if not os.path.exists(filepath):
            continue
        try:
            gdf = gpd.read_file(filepath)
        except Exception as e:
            st.warning(f"❌ Erro ao carregar {shp}: {e}")
            continue

        color = layer_colors[idx % len(layer_colors)]
        layer_name = shp.replace('.shp', '')

        folium.GeoJson(
            gdf,
            name=fmt_layer_name(layer_name),
            style_function=lambda feature, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            }
        ).add_to(m)

        bounds.append(gdf.total_bounds)
        legend_entries.append((fmt_layer_name(layer_name), color))

    # Ajusta limites
    if bounds:
        min_lon = min([b[0] for b in bounds])
        min_lat = min([b[1] for b in bounds])
        max_lon = max([b[2] for b in bounds])
        max_lat = max([b[3] for b in bounds])
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    else:
        min_lon, min_lat, max_lon, max_lat = -50, -20, -40, 0

    # Grid
    lat_lines = np.arange(np.floor(min_lat), np.ceil(max_lat) + grid_interval, grid_interval)
    lon_lines = np.arange(np.floor(min_lon), np.ceil(max_lon) + grid_interval, grid_interval)
    for lat in lat_lines:
        folium.PolyLine([(lat, min_lon), (lat, max_lon)], color='gray', weight=0.5, opacity=0.5).add_to(m)
        folium.map.Marker([lat, min_lon], icon=folium.DivIcon(html=f'<div style="font-size:10px">{lat:.1f}°</div>')).add_to(m)
    for lon in lon_lines:
        folium.PolyLine([(min_lat, lon), (max_lat, lon)], color='gray', weight=0.5, opacity=0.5).add_to(m)
        folium.map.Marker([min_lat, lon], icon=folium.DivIcon(html=f'<div style="font-size:10px">{lon:.1f}°</div>')).add_to(m)

    # Legenda
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: absolute; bottom: 10px; right: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 8px 10px;
        border-radius: 6px; font-size: 11px; max-width: 260px;
        box-shadow: 0 0 6px rgba(0,0,0,0.25); line-height: 1.25;
    ">
        <b>Legenda</b><br>
    """
    for name, color in legend_entries:
        legend_html += f"<div style='margin: 2px 0;'><span style='display:inline-block;width:12px;height:12px;background:{color};margin-right:6px;border:1px solid #333;'></span>{name}</div>"
    legend_html += "</div>{% endmacro %}"

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)

    return m

# =========================
# CSS Multiselect fonte 11
# =========================
st.markdown(
    """
    <style>
    div.stMultiSelect > div > div > div {
        font-size: 11px;
    }
    div.stMultiSelect > div > div > div > div[role="listbox"] > div {
        font-size: 11px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# TÍTULO + AVISOS
# =========================
st.title("🌊 Atlas Interativo do Fundo do Mar — Base EUNIS")
st.markdown(
    """**Nota importante:** Este atlas **não é atualizado em tempo real**.
    Usuários podem **enviar dados** para avaliação antes de incorporar ao modelo."""
)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Navegação")
view = st.sidebar.radio(
    "Ir para:",
    ["🗺️ Mapa Interativo", "📍 Cadastrar Pontos", "🧾 Consultar Dados", "ℹ️ Sobre o Atlas"],
    index=0
)

# =========================
# 1) VISUALIZAR MAPA
# =========================
if view == "🗺️ Mapa Interativo":
    st.subheader("🗺️ Mapa de Habitats (EUNIS)")

    # Botões globais
    col_sel, col_limpar = st.sidebar.columns([1,1])
    if col_sel.button("Selecionar Todas"):
        for category, files in categories_individuais.items():
            st.session_state[f"{category}_selected"] = [fmt_layer_name(shp) for shp in files]
    if col_limpar.button("Limpar Todas"):
        for category in categories_individuais.keys():
            st.session_state[f"{category}_selected"] = []

    # Multiselect por categoria
    selected_layers = []
    for category, files in categories_individuais.items():
        st.sidebar.markdown(f"### {category}")
        options = [fmt_layer_name(shp) for shp in files]
        default = st.session_state.get(f"{category}_selected", options)
        selected = st.sidebar.multiselect(f"Camadas ({category})", options=options, default=default)
        st.session_state[f"{category}_selected"] = selected
        for shp in files:
            if fmt_layer_name(shp) in selected:
                selected_layers.append(shp)

    if selected_layers:
        map_obj = create_map(shapefiles_folder_subdivididos, selected_layers)
        st_data = st_folium(map_obj, width=1100, height=640)
        st.divider()
        zip_buffer = create_shapefile_zip(shapefiles_folder_subdivididos, selected_layers)
        st.download_button(
            label="⬇️ Baixar Shapefiles Selecionados (.zip)",
            data=zip_buffer,
            file_name="shapefiles_selecionados.zip",
            mime="application/zip",
            help="Faz o download de todos os arquivos necessários (.shp, .shx, .dbf, .prj, .cpg)."
        )
    else:
        st.info("Selecione ao menos uma camada na barra lateral para visualizar o mapa.")

# =========================
# 2) CADASTRAR PONTOS
# =========================
elif view == "📍 Cadastrar Pontos":
    st.subheader("📍 Cadastro de Pontos de Observação")
    st.markdown(
        "Preencha o formulário abaixo ou envie um arquivo CSV. "
        "**Observação:** Os dados enviados serão avaliados antes de integrar ao atlas."
    )

    with st.form("form_cadastro_pontos"):
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
        with col2:
            substrato = st.selectbox("Substrato", ["Sand", "Mixed", "Mud", "Coarse", "Hard Rock", "Não identificado"])
            biogenico = st.selectbox("Biogênico", ["Recifal", "Rodolitos", "Biogenic not specified", "Terrigenous"])
            profundidade = st.selectbox("Zona Hidronímica", ["Littoral", "Circalittoral", "Offshore", "Bathyal Superior"])
        enviado = st.form_submit_button("📤 Enviar Ponto")
        if enviado:
            st.success(f"Ponto enviado: ({lat}, {lon}) - Substrato: {substrato}, Biogênico: {biogenico}, Zona: {profundidade}")

    st.markdown("---")
    st.subheader("📄 Upload de CSV")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV com colunas: Latitude, Longitude, Substrato, Biogênico, Zona")
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        st.dataframe(df_upload.head())
        st.success(f"{len(df_upload)} pontos carregados com sucesso!")

# =========================
# 3) CONSULTAR DADOS
# =========================
elif view == "🧾 Consultar Dados":
    st.subheader("🧾 Consulta de Dados do Atlas")
    st.dataframe(df_teste.head(2000))

# =========================
# 4) SOBRE O ATLAS
# =========================
elif view == "ℹ️ Sobre o Atlas":
    st.subheader("ℹ️ Sobre o Atlas Interativo do Fundo do Mar")
    st.markdown(
        """O **Atlas Interativo do Fundo do Mar** apresenta a distribuição de habitats marinhos no Brasil,
        utilizando a classificação **EUNIS adaptada para condições locais**.
        ... (mantém todo o texto original sobre classificação, substrato e biogênico) ...
        """
    )
