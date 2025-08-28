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

# -----------------------------
# Configurações iniciais
# -----------------------------
df_teste = pd.read_csv("ALLDATA_onehot_clipped.csv")
shapefiles_folder_subdivididos = "."
os.makedirs(shapefiles_folder_subdivididos, exist_ok=True)

categories  = {
    'littoral': [
        'littoral_coarse_biogenic.shp','littoral_coarse_recifal.shp','littoral_coarse_rhodolite.shp','littoral_coarse_terrigeneous.shp',
        'littoral_mixed_biogenic.shp','littoral_mixed_recifal.shp','littoral_mixed_rhodolite.shp','littoral_mixed_terrigeneous.shp',
        'littoral_mud_biogenic.shp','littoral_mud_recifal.shp','littoral_mud_rhodolite.shp','littoral_mud_terrigeneous.shp',
        'littoral_sand_biogenic.shp','littoral_sand_recifal.shp','littoral_sand_rhodolite.shp','littoral_sand_terrigeneous.shp',
        'littoral_hardrock_biogenic.shp','littoral_hardrock_recifal.shp','littoral_hardrock_rhodolite.shp','littoral_hardrock_terrigeneous.shp'
    ],
    'circalittoral': [
        'circalittoral_coarse_biogenic.shp','circalittoral_coarse_recifal.shp','circalittoral_coarse_rhodolite.shp','circalittoral_coarse_terrigeneous.shp',
        'circalittoral_mixed_biogenic.shp','circalittoral_mixed_recifal.shp','circalittoral_mixed_rhodolite.shp','circalittoral_mixed_terrigeneous.shp',
        'circalittoral_mud_biogenic.shp','circalittoral_mud_recifal.shp','circalittoral_mud_rhodolite.shp','circalittoral_mud_terrigeneous.shp',
        'circalittoral_sand_biogenic.shp','circalittoral_sand_recifal.shp','circalittoral_sand_rhodolite.shp','circalittoral_sand_terrigeneous.shp',
        'circalittoral_hardrock_biogenic.shp','circalittoral_hardrock_recifal.shp','circalittoral_hardrock_rhodolite.shp','circalittoral_hardrock_terrigeneous.shp'
    ],
    'offshore': [
        'offshore_coarse_biogenic.shp','offshore_coarse_recifal.shp','offshore_coarse_rhodolite.shp','offshore_coarse_terrigeneous.shp',
        'offshore_mixed_biogenic.shp','offshore_mixed_recifal.shp','offshore_mixed_rhodolite.shp','offshore_mixed_terrigeneous.shp',
        'offshore_mud_biogenic.shp','offshore_mud_recifal.shp','offshore_mud_rhodolite.shp','offshore_mud_terrigeneous.shp',
        'offshore_sand_biogenic.shp','offshore_sand_recifal.shp','offshore_sand_rhodolite.shp','offshore_sand_terrigeneous.shp',
        'offshore_hardrock_biogenic.shp','offshore_hardrock_recifal.shp','offshore_hardrock_rhodolite.shp','offshore_hardrock_terrigeneous.shp'
    ],
    'upper_bathyal': [
        'upper_bathyal_coarse_biogenic.shp','upper_bathyal_coarse_recifal.shp','upper_bathyal_coarse_rhodolite.shp','upper_bathyal_coarse_terrigeneous.shp',
        'upper_bathyal_mixed_biogenic.shp','upper_bathyal_mixed_recifal.shp','upper_bathyal_mixed_rhodolite.shp','upper_bathyal_mixed_terrigeneous.shp',
        'upper_bathyal_mud_biogenic.shp','upper_bathyal_mud_recifal.shp','upper_bathyal_mud_rhodolite.shp','upper_bathyal_mud_terrigeneous.shp',
        'upper_bathyal_sand_biogenic.shp','upper_bathyal_sand_recifal.shp','upper_bathyal_sand_rhodolite.shp','upper_bathyal_sand_terrigeneous.shp',
        'upper_bathyal_hardrock_biogenic.shp','upper_bathyal_hardrock_recifal.shp','upper_bathyal_hardrock_rhodolite.shp','upper_bathyal_hardrock_terrigenous.shp'
    ]
}

categories_individuais = {
    "Zona": ['littoral.shp','circalittoral.shp','offshore.shp','upper_bathyal.shp'],
    "Substrato": ['coarse.shp','mixed.shp','mud.shp','sand.shp','hardrock.shp'],
    "Biogênico": ['terrigeneous.shp','rhodolite.shp','biogenic.shp','recifal.shp']
}

# -----------------------------
# Funções
# -----------------------------
def load_shapefiles(shapefiles_folder):
    return [f for f in os.listdir(shapefiles_folder) if f.endswith('.shp')]

def create_shapefile_zip(shapefiles_folder, selected_layers):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for shp in selected_layers:
            base = os.path.splitext(shp)[0]
            for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                file_path = os.path.join(shapefiles_folder, base + ext)
                if os.path.exists(file_path):
                    zf.write(file_path, arcname=os.path.basename(file_path))
    buffer.seek(0)
    return buffer

def create_map(shapefiles_folder, selected_layers, basemap="OpenStreetMap"):
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True, tiles=basemap)

    # cores básicas
    layer_colors = ['#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6',
                    '#6a3d9a','#ffff99','#b15928','#ffffb3','#bebada','#fb8072','#fdb462','#b3de69',
                    '#fccde5','#bc80bd','#ffed6f','#d9bf77','#a1dab4','#f4a582','#d6604d','#b2182b',
                    '#fddbc7','#ef8a62','#d9d9d9','#bcbd22','#ccebc5','#fa9fb5','#e78ac3','#fdc086',
                    '#ffffcc','#b3cde3','#decbe4','#f2f2f2','#fbb4ae','#b4464b','#7fc97f']

    num_layers = len(selected_layers)
    if num_layers > len(layer_colors):
        layer_colors = (layer_colors * ((num_layers // len(layer_colors)) + 1))[:num_layers]

    bounds = []
    legend_entries = []

    for idx, shp in enumerate(selected_layers):
        gdf = gpd.read_file(os.path.join(shapefiles_folder, shp))
        color = layer_colors[idx]
        layer_name = shp.replace('.shp','')
        folium.GeoJson(
            gdf,
            name=layer_name,
            style_function=lambda feature, color=color: {'fillColor': color,'color':'black','weight':0.5,'fillOpacity':0.7}
        ).add_to(m)
        bounds.append(gdf.total_bounds)
        legend_entries.append((layer_name, color))

    if bounds:
        min_lon = min([b[0] for b in bounds])
        min_lat = min([b[1] for b in bounds])
        max_lon = max([b[2] for b in bounds])
        max_lat = max([b[3] for b in bounds])
        m.fit_bounds([[min_lat,min_lon],[max_lat,max_lon]])

    folium.LayerControl().add_to(m)

    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="position: relative;width: 100%;height: 100%;">
        <div style="position: absolute;bottom: 10px;left: 10px;z-index:9999;background-color:rgba(255,255,255,0.85);
                    padding:6px 8px;border-radius:5px;font-size:11px;max-width:200px;box-shadow:0 0 5px rgba(0,0,0,0.3);line-height:1.2;">
        <b>Legenda</b><br>
    """
    for name, color in legend_entries:
        legend_html += f"<div style='margin:2px 0;'><span style='display:inline-block;width:12px;height:12px;background:{color};margin-right:6px;border:1px solid #333;'></span>{name}</div>"
    legend_html += "</div></div>{% endmacro %}"

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)
    return m

# -----------------------------
# Carregar shapefiles
# -----------------------------
shapefiles_subdivididos = load_shapefiles(shapefiles_folder_subdivididos)

# -----------------------------
# Interface Streamlit
# -----------------------------
st.title("Atlas Interativo do Fundo do Mar")

tab1, tab2, tab3 = st.tabs(["📍 Cadastro de Pontos","Processar Dados", "🗺️ Visualizar Mapa"])

# -----------------------------
# TAB 1 - Cadastro de Pontos
# -----------------------------
with tab1:
    st.header("📍 Cadastro de Pontos")
    if "dados" not in st.session_state: st.session_state.dados = []

    opcao = st.radio("Como deseja inserir os dados?", ("Inserir Manualmente","Carregar Arquivo CSV"))

    if opcao == "Inserir Manualmente":
        with st.form("entrada_dados"):
            latitude = st.number_input("Latitude", format="%.6f", min_value=-90.0, max_value=90.0)
            longitude = st.number_input("Longitude", format="%.6f", min_value=-180.0, max_value=180.0)
            tipo_fundo = st.selectbox("Tipo de Fundo", ["Sand", "Mud", "Coarse", "Mixed", "Hard/Rock"])
            classificacao_biogenica = st.selectbox("Classificação Biogênica", ["Terrigenous","Biogenic","Rhodolite","Recifal"])
            submitted = st.form_submit_button("Adicionar Ponto")
            if submitted:
                st.session_state.dados.append({"Latitude": latitude,"Longitude": longitude,"Tipo de Fundo": tipo_fundo,"Classificação Biogênica": classificacao_biogenica})
                st.success("✅ Ponto cadastrado com sucesso!")

    elif opcao == "Carregar Arquivo CSV":
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                df_uploaded = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
            st.dataframe(df_uploaded.head())
            colunas_disponiveis = df_uploaded.columns.tolist()
            col_latitude = st.selectbox("Coluna Latitude", colunas_disponiveis)
            col_longitude = st.selectbox("Coluna Longitude", colunas_disponiveis)
            col_tipo_fundo = st.selectbox("Coluna Tipo de Fundo", colunas_disponiveis)
            col_class_biogenica = st.selectbox("Coluna Classificação Biogênica", colunas_disponiveis)
            if st.button("Carregar Dados"):
                df_mapeado = df_uploaded[[col_latitude,col_longitude,col_tipo_fundo,col_class_biogenica]].copy()
                df_mapeado.columns = ["Latitude","Longitude","Tipo de Fundo","Classificação Biogênica"]
                st.session_state.dados.extend(df_mapeado.to_dict(orient="records"))
                st.success("✅ Dados carregados com sucesso!")

    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        st.subheader("📋 Dados Inseridos")
        st.dataframe(df)
        st.download_button("⬇️ Baixar CSV", df.to_csv(index=False).encode("utf-8-sig"), "dados_marinhos.csv", "text/csv")

# -----------------------------
# TAB 2 - Processar Dados
# -----------------------------
with tab2:
    st.dataframe(df_teste)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Executa o modelo"):
            with st.spinner("Iniciando o modelo..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)
                    progress.progress(i+1)
            st.success("Execução concluída!")
    with col2:
        st.button("Help")

# -----------------------------
# TAB 3 - Visualizar Mapa
# -----------------------------
with tab3:
    st.sidebar.header("Configurações do Mapa")
    layer_type = st.sidebar.radio("Tipo de Camada", ["Mesclados","Subdivididos"])
    basemap = st.sidebar.selectbox("Basemap", ["OpenStreetMap","Stamen Terrain","Stamen Toner","CartoDB positron","CartoDB dark_matter"])

    st.write(f"Tipo de camada selecionado: **{layer_type}**")

    shapefiles = shapefiles_subdivididos
    shapefiles_folder = shapefiles_folder_subdivididos
    selected_layers = []

    category_dict = categories_individuais if layer_type=="Mesclados" else categories

    st.sidebar.subheader("Camadas Disponíveis")
    if st.sidebar.button("Selecionar Tudo"):
        st.session_state['select_all'] = True
    if st.sidebar.button("Limpar Seleção"):
        st.session_state['select_all'] = False

    if 'select_all' not in st.session_state:
        st.session_state['select_all'] = True

    for category, files in category_dict.items():
        with st.sidebar.expander(category, expanded=True):
            for shp in files:
                if shp in shapefiles:
                    layer_name = shp.replace(".shp","")
                    default_value = st.session_state['select_all']
                    if st.checkbox(layer_name, value=default_value, key=layer_name):
                        selected_layers.append(shp)

    if selected_layers:
        map_obj = create_map(shapefiles_folder, selected_layers, basemap=basemap)
        st_folium(map_obj, width=900, height=600)
        zip_buffer = create_shapefile_zip(shapefiles_folder, selected_layers)
        st.download_button("⬇️ Baixar Shapefiles Selecionados (.zip)", zip_buffer, "shapefiles_selecionados.zip", "application/zip")
    else:
        st.info("Selecione ao menos uma camada para visualizar o mapa.")
