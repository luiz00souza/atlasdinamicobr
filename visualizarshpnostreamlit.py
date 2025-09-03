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
    'littoral': [
        'littoral_coarse_biogenic.shp',
        'littoral_coarse_recifal.shp',
        'littoral_coarse_rhodolite.shp',
        'littoral_coarse_terrigeneous.shp',
        'littoral_mixed_biogenic.shp',
        'littoral_mixed_recifal.shp',
        'littoral_mixed_rhodolite.shp',
        'littoral_mixed_terrigeneous.shp',
        'littoral_mud_biogenic.shp',
        'littoral_mud_recifal.shp',
        'littoral_mud_rhodolite.shp',
        'littoral_mud_terrigeneous.shp',
        'littoral_sand_biogenic.shp',
        'littoral_sand_recifal.shp',
        'littoral_sand_rhodolite.shp',
        'littoral_sand_terrigeneous.shp',
        'littoral_hardrock_biogenic.shp',
        'littoral_hardrock_recifal.shp',
        'littoral_hardrock_rhodolite.shp',
        'littoral_hardrock_terrigeneous.shp'
    ],
    'circalittoral': [
        'circalittoral_coarse_biogenic.shp',
        'circalittoral_coarse_recifal.shp',
        'circalittoral_coarse_rhodolite.shp',
        'circalittoral_coarse_terrigeneous.shp',
        'circalittoral_mixed_biogenic.shp',
        'circalittoral_mixed_recifal.shp',
        'circalittoral_mixed_rhodolite.shp',
        'circalittoral_mixed_terrigeneous.shp',
        'circalittoral_mud_biogenic.shp',
        'circalittoral_mud_recifal.shp',
        'circalittoral_mud_rhodolite.shp',
        'circalittoral_mud_terrigeneous.shp',
        'circalittoral_sand_biogenic.shp',
        'circalittoral_sand_recifal.shp',
        'circalittoral_sand_rhodolite.shp',
        'circalittoral_sand_terrigeneous.shp',
        'circalittoral_hardrock_biogenic.shp',
        'circalittoral_hardrock_recifal.shp',
        'circalittoral_hardrock_rhodolite.shp',
        'circalittoral_hardrock_terrigeneous.shp'
    ],
    'offshore': [
        'offshore_coarse_biogenic.shp',
        'offshore_coarse_recifal.shp',
        'offshore_coarse_rhodolite.shp',
        'offshore_coarse_terrigeneous.shp',
        'offshore_mixed_biogenic.shp',
        'offshore_mixed_recifal.shp',
        'offshore_mixed_rhodolite.shp',
        'offshore_mixed_terrigeneous.shp',
        'offshore_mud_biogenic.shp',
        'offshore_mud_recifal.shp',
        'offshore_mud_rhodolite.shp',
        'offshore_mud_terrigeneous.shp',
        'offshore_sand_biogenic.shp',
        'offshore_sand_recifal.shp',
        'offshore_sand_rhodolite.shp',
        'offshore_sand_terrigeneous.shp',
        'offshore_hardrock_biogenic.shp',
        'offshore_hardrock_recifal.shp',
        'offshore_hardrock_rhodolite.shp',
        'offshore_hardrock_terrigeneous.shp'
    ],
    'upper_bathyal': [
        'upper_bathyal_coarse_biogenic.shp',
        'upper_bathyal_coarse_recifal.shp',
        'upper_bathyal_coarse_rhodolite.shp',
        'upper_bathyal_coarse_terrigeneous.shp',
        'upper_bathyal_mixed_biogenic.shp',
        'upper_bathyal_mixed_recifal.shp',
        'upper_bathyal_mixed_rhodolite.shp',
        'upper_bathyal_mixed_terrigeneous.shp',
        'upper_bathyal_mud_biogenic.shp',
        'upper_bathyal_mud_recifal.shp',
        'upper_bathyal_mud_rhodolite.shp',
        'upper_bathyal_mud_terrigeneous.shp',
        'upper_bathyal_sand_biogenic.shp',
        'upper_bathyal_sand_recifal.shp',
        'upper_bathyal_sand_rhodolite.shp',
        'upper_bathyal_sand_terrigeneous.shp',
        'upper_bathyal_hardrock_biogenic.shp',
        'upper_bathyal_hardrock_recifal.shp',
        'upper_bathyal_hardrock_rhodolite.shp',
        'upper_bathyal_hardrock_terrigeneous.shp'
    ]
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

# ... aqui mantém a função create_map intacta (não cortei nada)

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
    """ **Nota importante:** Este atlas **não é atualizado em tempo real**.  
Usuários podem **enviar dados** para que sejam **avaliados** por nossa equipe técnica; somente após essa avaliação os dados podem ser **incorporados ao modelo**. """
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

    st.sidebar.markdown("### Camadas")
    layer_type = st.sidebar.radio(
        "Nível de detalhamento:",
        ["🔎 Categorias gerais (Zonas, Substratos, Biogênico)", "🧩 Subcategorias detalhadas"],
        index=0
    )
    layer_type = 'Mesclados' if layer_type.startswith("🔎") else 'Subdivididos'

    selected_layers = []
    category_dict = categories_individuais if layer_type == 'Mesclados' else categories

    # --------------------
    # Botões globais
    # --------------------
    st.sidebar.caption("Ações rápidas:")
    col_btns = st.sidebar.columns([1,1])
    if col_btns[0].button("✅ Selecionar tudo"):
        for category, files in category_dict.items():
            st.session_state[f"{category}_selected"] = [fmt_layer_name(shp) for shp in files]
    if col_btns[1].button("❌ Limpar tudo"):
        for category in category_dict.keys():
            st.session_state[f"{category}_selected"] = []

    # --------------------
    # Expanders com multiselects
    # --------------------
    st.sidebar.caption("Marque as camadas que deseja visualizar no mapa:")
    for category, files in category_dict.items():
        with st.sidebar.expander(f"{category}"):
            selected = st.multiselect(
                f"Camadas ({category})",
                options=[fmt_layer_name(shp) for shp in files],
                default=st.session_state.get(f"{category}_selected", [fmt_layer_name(shp) for shp in files])
            )
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
    # ... mantém exatamente como estava
    pass

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
    # ... mantém exatamente como estava
    pass
