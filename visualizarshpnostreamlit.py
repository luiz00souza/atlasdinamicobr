import sys
import streamlit as st
import time
import os
import geopandas as gpd
import folium 
from branca.element import Template, MacroElement
from streamlit_folium import st_folium
import pandas as pd
df_teste = pd.read_csv("ALLDATA_onehot_clipped.csv")

# modulo_diretorio = r'C:\Users\campo\Desktop\mestrado\DADOS121223\Raster Reclassificados\88_rotinas_python'
#import CHAMAMODELO
#shapefiles_folder_subdivididos = r"C:\Users\campo\Desktop\mestrado\DADOS121223\Raster Reclassificados\arrays padronizados\Shapefiles_Classes"
shapefiles_folder_subdivididos = "."

os.makedirs(shapefiles_folder_subdivididos, exist_ok=True)

#sys.path.append(modulo_diretorio)
# Diretórios das pastas

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
        'upper_bathyal_hardrock_terrigenous.shp'  # corrigido conforme original
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


# Função para carregar shapefiles de uma pasta
def load_shapefiles(shapefiles_folder):
    shapefiles = [f for f in os.listdir(shapefiles_folder) if f.endswith('.shp')]
    return shapefiles
# Carregar shapefiles
# shapefiles_mesclados = load_shapefiles(shapefiles_folder_mesclados)
shapefiles_subdivididos = load_shapefiles(shapefiles_folder_subdivididos)
# Função para criar o mapa com folium

def create_map(shapefiles_folder, selected_layers):
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True)

    layer_colors = [
    '#1f78b4',  # azul escuro
    '#b2df8a',  # verde claro
    '#33a02c',  # verde médio
    '#fb9a99',  # rosa claro
    '#e31a1c',  # vermelho escuro
    '#fdbf6f',  # pêssego claro
    '#ff7f00',  # laranja queimado
    '#cab2d6',  # lilás claro
    '#6a3d9a',  # roxo escuro
    '#ffff99',  # amarelo claro pastel
    '#b15928',  # marrom escuro
    '#ffffb3',  # amarelo pastel suave
    '#bebada',  # roxo pastel
    '#fb8072',  # coral suave
    '#fdb462',  # laranja suave
    '#b3de69',  # verde limão claro
    '#fccde5',  # rosa pastel
    '#bc80bd',  # lilás médio
    '#ffed6f',  # amarelo pálido
    '#d9bf77',  # dourado claro
    '#a1dab4',  # verde menta (mais opaco, ainda visível)
    '#f4a582',  # salmão claro
    '#d6604d',  # vermelho suave queimado
    '#b2182b',  # bordô
    '#fddbc7',  # bege rosado
    '#ef8a62',  # coral queimado
    '#d9d9d9',  # cinza claro
    '#bcbd22',  # verde musgo pálido
    '#ccebc5',  # verde bem claro (não ciano)
    '#fa9fb5',  # rosa médio
    '#e78ac3',  # rosa violeta
    '#fdc086',  # laranja claro pastel
    '#ffffcc',  # amarelo quase branco
    '#b3cde3',  # azul acinzentado mais neutro
    '#decbe4',  # lilás pálido
    '#f2f2f2',  # branco sujo (para contorno leve)
    '#fbb4ae',  # rosa alaranjado claro
    '#b4464b',  # vermelho terroso
    '#7fc97f',  # verde limão mais forte
]

    
    # Listar arquivos terminados em .shp
    shp_files = [f for f in os.listdir(shapefiles_folder_subdivididos) if f.lower().endswith('.shp')]
    num_layers = len(shp_files)
    if num_layers > len(layer_colors):
        vezes = (num_layers // len(layer_colors)) + 1
        layer_colors = (layer_colors * vezes)[:num_layers]
    bounds = []
    legend_entries = []  # Armazena pares (nome, cor)

    for idx, shp in enumerate(selected_layers):
        gdf = gpd.read_file(os.path.join(shapefiles_folder, shp))
        color = layer_colors[idx % len(layer_colors)]
        layer_name = shp.replace('.shp', '')
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

    # Ajusta os limites
    if bounds:
        min_lon = min([b[0] for b in bounds])
        min_lat = min([b[1] for b in bounds])
        max_lon = max([b[2] for b in bounds])
        max_lat = max([b[3] for b in bounds])
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    folium.LayerControl().add_to(m)

    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: relative;
        width: 100%;
        height: 100%;
    ">
        <div style="
            position: absolute;
            bottom: 10px;
            left: 10px;
            z-index: 9999;
            background-color: rgba(255, 255, 255, 0.85);
            padding: 6px 8px;
            border-radius: 5px;
            font-size: 11px;
            max-width: 200px;
            box-shadow: 0 0 5px rgba(0,0,0,0.3);
            line-height: 1.2;
        ">
        <b>Legenda</b><br>
    """
    for name, color in legend_entries:
        legend_html += (
            f"<div style='margin: 2px 0;'>"
            f"<span style='display:inline-block;width:12px;height:12px;"
            f"background:{color};margin-right:6px;border:1px solid #333;'></span>{name}</div>"
        )
    
    legend_html += """
        </div>
    </div>
    {% endmacro %}
    """


    


    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)

    return m



st.title("Visualização de Shapefiles com Folium")

tab1, tab2, tab3 = st.tabs(["Dados marinhos","Escolha de Camada", "Mapa e Seleção de Camadas"])

with tab1:
    st.header("📌 Aba 1 - Cadastro de Dados Marinhos")

    # Inicializa a sessão de dados (se ainda não inicializada)
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

    # Exibir tabela com os dados inseridos
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        st.subheader("📋 Dados Inseridos")
        st.dataframe(df)

        # Botão para baixar os dados como CSV
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv,
            file_name="dados_marinhos.csv",
            mime="text/csv"
        )
with tab2:
    st.write("Escolha o tipo de camada desejada:")
    st.dataframe(df_teste)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Executa o modelo"):
            with st.spinner("Iniciando o modelo..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.05)  # Simula um delay visual
                    progress.progress(i + 1)
                #chama_modelo()
            st.success("Execução concluída!")


    with col2:
        st.button("Help")  # Botão vazio

with tab3:
    # Se não houver escolha ainda, definir padrão
    st.write("Escolha o tipo de camada desejada:")
    # Dois botões para escolher camada mesclada ou subdivididadi
    if st.button("Camadas Individuais"):
        st.session_state['layer_type'] = 'Mesclados'
    if st.button("Camadas Subdivididas"):
        st.session_state['layer_type'] = 'Subdivididos'
    if 'layer_type' not in st.session_state:
        st.session_state['layer_type'] = 'Mesclados'
    
    layer_type = st.session_state['layer_type']

    st.write(f"Tipo de camada selecionado: **{layer_type}**")

    shapefiles = shapefiles_subdivididos
    shapefiles_folder = shapefiles_folder_subdivididos

    selected_layers = []
    if layer_type == 'Mesclados':
        category_dict = categories_individuais
    else:
        category_dict = categories
    
    for category, files in category_dict.items():    
        with st.expander(f"{category} (Clique para expandir)"):
            for shp in files:
                if shp in shapefiles:
                    layer_name = shp.replace('.shp', '')
                    if st.checkbox(layer_name, value=True):
                        selected_layers.append(shp)

    if selected_layers:
        map_obj = create_map(shapefiles_folder, selected_layers)
        st_data = st_folium(map_obj, width=900, height=600)

    else:
        st.info("Selecione ao menos uma camada para visualizar o mapa.")
def load_shapefiles(shapefiles_folder):
    shapefiles = [f for f in os.listdir(shapefiles_folder) if f.endswith('.shp')]
    return shapefiles

# shapefiles_mesclados = load_shapefiles(shapefiles_folder_mesclados)










