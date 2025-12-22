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
df_teste = pd.read_csv("ALLDATA_onehot_clipped.csv", encoding="latin1")

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
def create_map(shapefiles_folder, selected_layers, grid_interval=2):
    import geopandas as gpd
    import folium
    from folium import GeoJson
    import os
    from branca.element import Template, MacroElement
    import numpy as np
    import streamlit as st

    # =========================
    # Mapa base
    # =========================
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True)

    # Datum fixo
    datum_html = """
    <div style="
        position: absolute; bottom: 40px; left: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 4px 6px;
        border-radius: 4px; font-size: 11px;
    ">Datum: WGS84</div>
    """
    m.get_root().html.add_child(folium.Element(datum_html))

    # =========================
    # Paleta de cores
    # =========================
    layer_colors = [
        '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f',
        '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928'
    ]

    bounds = []
    legend_entries = []

    # =========================
    # Loop das camadas
    # =========================
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
        layer_name = fmt_layer_name(shp.replace('.shp', ''))

        # -------------------------
        # Campos exibidos no hover
        # -------------------------
        tooltip_fields = [c for c in gdf.columns if c.lower() not in ["geometry"]][:6]

        # -------------------------
        # GeoJson com TOOLTIP + POPUP
        # -------------------------
        GeoJson(
            gdf,
            name=layer_name,
            style_function=lambda feature, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            },
            highlight_function=lambda feature: {
                'weight': 2,
                'color': 'yellow',
                'fillOpacity': 0.9
            },
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields,
                aliases=tooltip_fields,
                sticky=True,
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=tooltip_fields,
                aliases=tooltip_fields,
                localize=True
            )
        ).add_to(m)

        bounds.append(gdf.total_bounds)
        legend_entries.append((layer_name, color))

    # =========================
    # Ajuste de bounds
    # =========================
    if bounds:
        min_lon = min(b[0] for b in bounds)
        min_lat = min(b[1] for b in bounds)
        max_lon = max(b[2] for b in bounds)
        max_lat = max(b[3] for b in bounds)
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    else:
        min_lon, min_lat, max_lon, max_lat = -50, -20, -40, 0

    # =========================
    # Grid geográfico
    # =========================
    lat_lines = np.arange(np.floor(min_lat), np.ceil(max_lat) + grid_interval, grid_interval)
    lon_lines = np.arange(np.floor(min_lon), np.ceil(max_lon) + grid_interval, grid_interval)

    for lat in lat_lines:
        folium.PolyLine([(lat, min_lon), (lat, max_lon)],
                        color='gray', weight=0.5, opacity=0.5).add_to(m)
        folium.Marker(
            [lat, min_lon],
            icon=folium.DivIcon(html=f'<div style="font-size:10px">{lat:.1f}°</div>')
        ).add_to(m)

    for lon in lon_lines:
        folium.PolyLine([(min_lat, lon), (max_lat, lon)],
                        color='gray', weight=0.5, opacity=0.5).add_to(m)
        folium.Marker(
            [min_lat, lon],
            icon=folium.DivIcon(html=f'<div style="font-size:10px">{lon:.1f}°</div>')
        ).add_to(m)

    # =========================
    # Legenda
    # =========================
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: absolute; bottom: 10px; right: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 8px;
        border-radius: 6px; font-size: 11px;
    ">
    <b>Legenda</b><br>
    """
    for name, color in legend_entries:
        legend_html += f"""
        <div>
            <span style="display:inline-block;width:12px;height:12px;
            background:{color};margin-right:6px;border:1px solid #333;"></span>
            {name}
        </div>
        """
    legend_html += """
    </div>
    {% endmacro %}
    """

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)

    #folium.LayerControl(collapsed=False).add_to(m)

    return m


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

def fmt_layer_name(shp):
    return shp.replace(".shp","").replace("_"," ").title()

def get_layers_by_substrate():
    layers = []
    for zone_files in categories.values():
        for shp in zone_files:
            for substrato in categories_individuais["Substrato"]:
                if f"_{substrato}_" in shp:
                    layers.append(shp)
    return layers

def get_layers_by_biogenic():
    layers = []
    for zone_files in categories.values():
        for shp in zone_files:
            for bio in categories_individuais["Biogênico"]:
                if f"_{bio}." in shp:
                    layers.append(shp)
    return layers

# =========================
# CSS Multiselect fonte 11
# =========================
st.markdown("""
<style>
div.stMultiSelect > div > div > div { font-size: 11px; }
div.stMultiSelect > div > div > div > div[role="listbox"] > div { font-size: 11px; }
</style>
""", unsafe_allow_html=True)
# =========================
# TÍTULO + AVISOS
# =========================
st.title("🌊 Atlas Interativo do Fundo do Mar — Base EUNIS")
st.markdown(
    """
**Nota importante:** Este atlas **não é atualizado em tempo real**.  
Usuários podem **enviar dados** para que sejam **avaliados** por nossa equipe técnica; somente após essa avaliação os dados podem ser **incorporados ao modelo**.
"""
)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("Navegação")
view = st.sidebar.radio(
    "Ir para:",
    ["🗺️ Mapa Interativo", "📍 Cadastrar Pontos", "🧾 Consultar Dados", "ℹ️ Sobre o Atlas"],
    index=0,
    key="sidebar_view"
)

# =========================
# 1) VISUALIZAR MAPA
# =========================
if view == "🗺️ Mapa Interativo":
    st.subheader("🗺️ Mapa de Habitats (EUNIS)")

    st.sidebar.markdown("### Nível de detalhamento")
    level = st.sidebar.radio(
        "Escolha o nível:",
        ["Zonas", "Substratos", "Biogênico", "🧩 Subcategorias detalhadas"],
        index=0,
        key="sidebar_level"
    )

    # --------------------
    # Seleção de shapefiles por nível
    # --------------------
    selected_layers = []

    if level == "Zonas":
        category_dict = {"Zona": categories_individuais["Zona"]}
    elif level == "Substratos":
        # busca todos os shapefiles que correspondem aos substratos
        category_dict = {"Substrato": categories_individuais["Substrato"]}
    elif level == "Biogênico":
        # busca todos os shapefiles que correspondem ao biogênico
        category_dict = {"Biogênico":categories_individuais["Biogênico"]}
    else:
        # subcategorias detalhadas
        category_dict = categories

    st.sidebar.caption("Marque as camadas que deseja visualizar no mapa:")

    for category, files in category_dict.items():
        with st.sidebar.expander(f"{category}", expanded=True):
            col_btns = st.columns([1,1])
            if col_btns[0].button(f"Selecionar tudo ({category})", key=f"sel_all_{category}"):
                st.session_state[f"{category}_selected"] = [fmt_layer_name(shp) for shp in files]
            if col_btns[1].button(f"Limpar tudo ({category})", key=f"desel_all_{category}"):
                st.session_state[f"{category}_selected"] = []

            selected = st.multiselect(
                f"Camadas ({category})",
                options=[fmt_layer_name(shp) for shp in files],
                default=st.session_state.get(f"{category}_selected", [fmt_layer_name(shp) for shp in files]),
                key=f"multi_{category}"  # chave única
            )
            st.session_state[f"{category}_selected"] = selected

            for shp in files:
                if fmt_layer_name(shp) in selected:
                    selected_layers.append(shp)

    # --------------------
    # Exibe mapa e download
    # --------------------
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

# 2) CADASTRAR PONTOS
# =========================
elif view == "📍 Cadastrar Pontos":
    if "dados" not in st.session_state:
        st.session_state.dados = []

    # Opções de entrada de dados
    opcao = st.radio("Como deseja inserir os dados?", ("Inserir Manualmente", "Carregar Arquivo CSV"))

    if opcao == "Inserir Manualmente":
        with st.form("entrada_dados"):
            st.subheader("📌 Inserir Novo Ponto")

            latitude = st.number_input("Latitude", format="%.6f", min_value=-90.0, max_value=90.0)
            longitude = st.number_input("Longitude", format="%.6f", min_value=-180.0, max_value=180.0)

            tipo_fundo = st.selectbox("Tipo de Fundo", ["Sand", "Mud", "Coarse", "Mixed", "Hard/Rock"])
            classificacao_biogenica = st.selectbox("Classificação Biogênica", ["Terrigenous", "Biogenic", "Rhodolite", "Recifal"])

            submitted = st.form_submit_button("Adicionar Ponto")

            if submitted:
                novo_dado = {
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Tipo de Fundo": tipo_fundo,
                    "Classificação Biogênica": classificacao_biogenica
                }
                st.session_state.dados.append(novo_dado)
                st.success("✅ Ponto cadastrado com sucesso!")
    elif opcao == "Carregar Arquivo CSV":
        st.subheader("📂 Enviar Arquivo CSV")
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])

        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    df_uploaded = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
                except Exception as e:
                    st.error(f"❌ Erro ao carregar o arquivo: {e}")
                    df_uploaded = None

            if df_uploaded is not None:
                st.write("Pré-visualização dos dados carregados:")
                st.dataframe(df_uploaded.head())

                colunas_disponiveis = df_uploaded.columns.tolist()

                col_latitude = st.selectbox("Selecione a coluna para Latitude", colunas_disponiveis)
                col_longitude = st.selectbox("Selecione a coluna para Longitude", colunas_disponiveis)
                col_tipo_fundo = st.selectbox("Selecione a coluna para Tipo de Fundo", colunas_disponiveis)
                col_class_biogenica = st.selectbox("Selecione a coluna para Classificação Biogênica", colunas_disponiveis)

                if st.button("Carregar Dados"):
                    df_mapeado = df_uploaded[[col_latitude, col_longitude, col_tipo_fundo, col_class_biogenica]].copy()
                    df_mapeado.columns = ["Latitude", "Longitude", "Tipo de Fundo", "Classificação Biogênica"]
                    st.session_state.dados.extend(df_mapeado.to_dict(orient="records"))
                    st.success("✅ Dados carregados com sucesso!")

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
