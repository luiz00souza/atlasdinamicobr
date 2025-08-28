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

# =====================
# Carregar dados de teste
# =====================
df_teste = pd.read_csv("ALLDATA_onehot_clipped.csv")

# Pasta onde estão shapefiles
shapefiles_folder_subdivididos = "."
os.makedirs(shapefiles_folder_subdivididos, exist_ok=True)

# =====================
# Dicionários de camadas
# =====================
categories  = {
    "Litoral": [
        'littoral_coarse_biogenic.shp',
        'littoral_mixed_biogenic.shp',
        'littoral_mud_biogenic.shp',
        'littoral_sand_biogenic.shp',
        'littoral_hardrock_biogenic.shp'
    ],
    "Circalitoral": [
        'circalittoral_coarse_biogenic.shp',
        'circalittoral_mixed_biogenic.shp',
        'circalittoral_mud_biogenic.shp',
        'circalittoral_sand_biogenic.shp',
        'circalittoral_hardrock_biogenic.shp'
    ],
    "Offshore": [
        'offshore_coarse_biogenic.shp',
        'offshore_mixed_biogenic.shp',
        'offshore_mud_biogenic.shp',
        'offshore_sand_biogenic.shp',
        'offshore_hardrock_biogenic.shp'
    ],
    "Batial Superior": [
        'upper_bathyal_coarse_biogenic.shp',
        'upper_bathyal_mixed_biogenic.shp',
        'upper_bathyal_mud_biogenic.shp',
        'upper_bathyal_sand_biogenic.shp',
        'upper_bathyal_hardrock_biogenic.shp'
    ]
}

categories_individuais = {
    "Zona": [
        'littoral.shp',
        'circalittoral.shp',
        'offshore.shp',
        'upper_bathyal.shp'
    ],
    "Substrato": [
        'coarse.shp',
        'mixed.shp',
        'mud.shp',
        'sand.shp',
        'hardrock.shp'
    ],
    "Biogênico": [
        'terrigeneous.shp',
        'rhodolite.shp',
        'biogenic.shp',
        'recifal.shp'
    ]
}

# Tradução de nomes técnicos para amigáveis
nomes_amigaveis = {
    "littoral": "Zona Litoral",
    "circalittoral": "Zona Circalitoral",
    "offshore": "Zona Offshore",
    "upper_bathyal": "Zona Batial Superior",
    "sand": "Fundo Arenoso",
    "mud": "Fundo Lodoso",
    "coarse": "Fundo Cascalhoso",
    "mixed": "Fundo Misto",
    "hardrock": "Rocha Dura",
    "biogenic": "Origem Biológica",
    "rhodolite": "Rodólitos",
    "recifal": "Recifes",
    "terrigeneous": "Origem Terrígena"
}

# =====================
# Funções auxiliares
# =====================
def load_shapefiles(shapefiles_folder):
    return [f for f in os.listdir(shapefiles_folder) if f.endswith('.shp')]

shapefiles_subdivididos = load_shapefiles(shapefiles_folder_subdivididos)

def traduzir_nome(nome):
    nome_bonito = nome.replace(".shp", "")
    for chave, traduz in nomes_amigaveis.items():
        nome_bonito = nome_bonito.replace(chave, traduz)
    return nome_bonito

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

def create_map(shapefiles_folder, selected_layers):
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True)

    layer_colors = ['#1f78b4', '#33a02c', '#fb9a99', '#e31a1c', '#ff7f00']

    bounds = []
    legend_entries = []

    for idx, shp in enumerate(selected_layers):
        gdf = gpd.read_file(os.path.join(shapefiles_folder, shp))
        color = layer_colors[idx % len(layer_colors)]
        layer_name = traduzir_nome(shp)
        folium.GeoJson(
            gdf,
            name=layer_name,
            style_function=lambda feature, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            }
        ).add_to(m)
        bounds.append(gdf.total_bounds)
        legend_entries.append((layer_name, color))

    if bounds:
        min_lon = min([b[0] for b in bounds])
        min_lat = min([b[1] for b in bounds])
        max_lon = max([b[2] for b in bounds])
        max_lat = max([b[3] for b in bounds])
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    folium.LayerControl().add_to(m)

    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="position:absolute;bottom:10px;left:10px;z-index:9999;
                background-color:rgba(255,255,255,0.85);padding:6px 8px;
                border-radius:5px;font-size:11px;max-width:200px;">
        <b>Legenda</b><br>
    """
    for name, color in legend_entries:
        legend_html += f"<div><span style='display:inline-block;width:12px;height:12px;background:{color};margin-right:6px;border:1px solid #333;'></span>{name}</div>"
    legend_html += "</div>{% endmacro %}"

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)
    return m

# =====================
# Layout principal
# =====================
st.title("🌊 Atlas Interativo de Habitats Marinhos")
st.markdown("""
Este Atlas é baseado na classificação internacional **EUNIS**, adaptada às condições do Brasil. 

🔎 Explore o mapa interativo abaixo.  
Os dados enviados por usuários passam por **avaliação de qualidade** antes de eventual inclusão.  
O Atlas atualizado em tempo real **não está disponível publicamente**.
""")

# -------- MAPA (Tela inicial)
st.header("🗺️ Explorar o Mapa")

if "layer_type" not in st.session_state:
    st.session_state["layer_type"] = "Mesclados"

col1, col2 = st.columns(2)
with col1:
    if st.button("🔎 Ver categorias gerais (Zonas, Substratos, Biologia)"):
        st.session_state['layer_type'] = 'Mesclados'
with col2:
    if st.button("🧩 Ver subcategorias detalhadas"):
        st.session_state['layer_type'] = 'Subdivididos'

layer_type = st.session_state['layer_type']
st.write(f"📌 Você está vendo: **{layer_type}**")

selected_layers = []
category_dict = categories_individuais if layer_type == "Mesclados" else categories

for category, files in category_dict.items():
    with st.expander(f"{category}"):
        for shp in files:
            if shp in shapefiles_subdivididos:
                layer_name = traduzir_nome(shp)
                if st.checkbox(layer_name, value=True):
                    selected_layers.append(shp)

if selected_layers:
    map_obj = create_map(shapefiles_folder_subdivididos, selected_layers)
    st_folium(map_obj, width=900, height=600)
    zip_buffer = create_shapefile_zip(shapefiles_folder_subdivididos, selected_layers)
    st.download_button(
        label="⬇️ Baixar Shapefiles Selecionados (.zip)",
        data=zip_buffer,
        file_name="shapefiles_selecionados.zip",
        mime="application/zip"
    )
else:
    st.info("Selecione ao menos uma camada para visualizar o mapa.")

# -------- ABAS SECUNDÁRIAS
tab1, tab2, tab3 = st.tabs(["📤 Contribuir com Dados", "⚙️ Processar Dados", "ℹ️ Sobre o Atlas"])

with tab1:
    st.subheader("📤 Envio de Dados para Avaliação")
    st.markdown("""
    Os dados enviados serão **avaliados** antes de serem incorporados ao Atlas. 
    Você pode cadastrar manualmente ou carregar um arquivo CSV.
    """)

    if "dados" not in st.session_state:
        st.session_state.dados = []

    opcao = st.radio("Como deseja inserir os dados?", ("Inserir Manualmente", "Carregar Arquivo CSV"))

    if opcao == "Inserir Manualmente":
        with st.form("entrada_dados"):
            latitude = st.number_input("Latitude", format="%.6f", min_value=-90.0, max_value=90.0)
            longitude = st.number_input("Longitude", format="%.6f", min_value=-180.0, max_value=180.0)
            tipo_fundo = st.selectbox("Tipo de Fundo", ["Arenoso", "Lodoso", "Cascalhoso", "Misto", "Rocha Dura"])
            class_bio = st.selectbox("Classificação Biogênica", ["Terrígena", "Biogênica", "Rodólitos", "Recifes"])
            submitted = st.form_submit_button("Adicionar Ponto")
            if submitted:
                st.session_state.dados.append({"Latitude": latitude, "Longitude": longitude,
                                               "Tipo de Fundo": tipo_fundo, "Classificação Biogênica": class_bio})
                st.success("✅ Ponto cadastrado com sucesso!")

    else:
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file, encoding="utf-8")
            except Exception as e:
                st.error(f"❌ Erro ao carregar o arquivo: {e}")
                df_uploaded = None
            if df_uploaded is not None:
                st.dataframe(df_uploaded.head())
                colunas = df_uploaded.columns.tolist()
                col_lat = st.selectbox("Coluna de Latitude", colunas)
                col_lon = st.selectbox("Coluna de Longitude", colunas)
                col_fundo = st.selectbox("Coluna de Tipo de Fundo", colunas)
                col_bio = st.selectbox("Coluna de Classificação Biogênica", colunas)
                if st.button("Carregar Dados"):
                    df_mapeado = df_uploaded[[col_lat, col_lon, col_fundo, col_bio]].copy()
                    df_mapeado.columns = ["Latitude", "Longitude", "Tipo de Fundo", "Classificação Biogênica"]
                    st.session_state.dados.extend(df_mapeado.to_dict(orient="records"))
                    st.success("✅ Dados carregados com sucesso!")

    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Baixar CSV", csv, "dados_marinhos.csv", "text/csv")

with tab2:
    st.subheader("⚙️ Processamento de Dados")
    st.markdown("Os dados aqui são processados em rotinas internas para avaliação.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Executar Modelo"):
            with st.spinner("Rodando modelo..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    progress.progress(i + 1)
            st.success("✅ Execução concluída!")
    with col2:
        st.button("❓ Ajuda")

with tab3:
    st.subheader("ℹ️ Sobre o Atlas")
    st.markdown("""
    Este Atlas de Habitats Marinhos é baseado no **EUNIS (European Nature Information System)**, 
    adaptado para as condições brasileiras. Ele organiza habitats em níveis hierárquicos, considerando:

    - **Zona** (profundidade, como litoral ou batial superior)
    - **Substrato** (areia, lama, rocha, etc.)
    - **Componente Biogênico** (recifes, rodólitos, biogênicos, etc.)

    ⚠️ Os dados enviados por usuários não são incorporados automaticamente.  
    Eles passam por avaliação de qualidade e consistência antes de eventual integração ao modelo.
    """)
