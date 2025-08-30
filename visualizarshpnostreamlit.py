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
# (mantido exatamente como no seu código)
shapefiles_folder_subdivididos = "."
os.makedirs(shapefiles_folder_subdivididos, exist_ok=True)

# =========================
# ESTRUTURA DAS CATEGORIAS (mantida)
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
        'upper_bathyal_hardrock_terrigenous.shp'
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

# =========================
# UTILITÁRIOS
# =========================
def load_shapefiles(shapefiles_folder):
    return [f for f in os.listdir(shapefiles_folder) if f.lower().endswith('.shp')]

shapefiles_subdivididos = load_shapefiles(shapefiles_folder_subdivididos)

def fmt_layer_name(name: str) -> str:
    """Converte nomes técnicos em rótulos mais amigáveis."""
    label = name.replace('.shp', '').replace('_', ' ')
    label = (label
             .replace('littoral', 'Litoral')
             .replace('circalittoral', 'Circalitoral')
             .replace('offshore', 'Offshore')
             .replace('upper bathyal', 'Batial Superior')
             .replace('hardrock', 'Rocha/Hard Rock')
             .replace('coarse', 'Cascalho/Coarse')
             .replace('mixed', 'Misto/Mixed')
             .replace('mud', 'Lodoso/Mud')
             .replace('sand', 'Arenoso/Sand')
             .replace('biogenic', 'Biogênico')
             .replace('recifal', 'Recifal')
             .replace('rhodolite', 'Rodólitos')
             .replace('terrigeneous', 'Terrígeno'))
    # Capitaliza primeira letra de cada palavra
    return ' '.join([w.capitalize() if w.islower() else w for w in label.split()])

def create_shapefile_zip(shapefiles_folder, selected_layers):
    """
    Cria um arquivo ZIP com os shapefiles selecionados (incluindo .shp, .shx, .dbf, .prj, .cpg).
    """
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

def create_map(shapefiles_folder, selected_layers):
    import geopandas as gpd
    import folium
    from folium import LayerControl, GeoJson, Element
    import os
    from branca.element import Template, MacroElement

    # Mapa base com escala nativa (canto inferior esquerdo)
    m = folium.Map(location=[-15, -47], zoom_start=4, control_scale=True)

    # Datum fixo no canto inferior direito
    datum_html = """
    <div style="
        position: absolute; bottom: 10px; right: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 4px 6px;
        border-radius: 4px; font-size: 11px; box-shadow: 0 0 4px rgba(0,0,0,0.2);
    ">Datum: WGS84</div>
    """
    m.get_root().html.add_child(folium.Element(datum_html))

    # Definir cores e adicionar camadas
    layer_colors = [
        '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c', '#fdbf6f',
        '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99', '#b15928', '#ffffb3',
        '#bebada', '#fb8072', '#fdb462', '#b3de69', '#fccde5', '#bc80bd',
        '#ffed6f', '#d9bf77', '#a1dab4', '#f4a582', '#d6604d', '#b2182b',
        '#fddbc7', '#ef8a62', '#d9d9d9', '#bcbd22', '#ccebc5', '#fa9fb5',
        '#e78ac3', '#fdc086', '#ffffcc', '#b3cde3', '#decbe4', '#f2f2f2',
        '#fbb4ae', '#b4464b', '#7fc97f'
    ]

    shp_files = [f for f in os.listdir(shapefiles_folder) if f.lower().endswith('.shp')]
    num_layers = max(len(shp_files), len(selected_layers))
    if num_layers > len(layer_colors):
        times = (num_layers // len(layer_colors)) + 1
        layer_colors = (layer_colors * times)[:num_layers]

    bounds = []
    legend_entries = []

    for idx, shp in enumerate(selected_layers):
        gdf = gpd.read_file(os.path.join(shapefiles_folder, shp))
        color = layer_colors[idx % len(layer_colors)]
        layer_name = shp.replace('.shp', '')
        GeoJson(
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

    LayerControl(collapsed=False).add_to(m)

    # Legenda no canto inferior esquerdo
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="
        position: relative; width: 100%; height: 100%;
    ">
      <div style="
        position: absolute; bottom: 10px; left: 10px; z-index: 9999;
        background-color: rgba(255,255,255,0.9); padding: 8px 10px;
        border-radius: 6px; font-size: 12px; max-width: 260px;
        box-shadow: 0 0 6px rgba(0,0,0,0.25); line-height: 1.25;
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
# SIDEBAR (NAVEGAÇÃO)
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

    # Controles na sidebar
    st.sidebar.markdown("### Camadas")
    # Tipo de camada: Mesclados (individuais) ou Subdivididos (detalhe completo)
    if st.sidebar.radio(
        "Nível de detalhamento:",
        ["🔎 Categorias gerais (Zonas, Substratos, Biogênico)", "🧩 Subcategorias detalhadas"],
        index=0
    ) == "🔎 Categorias gerais (Zonas, Substratos, Biogênico)":
        st.session_state['layer_type'] = 'Mesclados'
    else:
        st.session_state['layer_type'] = 'Subdivididos'

    layer_type = st.session_state.get('layer_type', 'Mesclados')

    # Seleção de camadas (expanders na sidebar)
    selected_layers = []
    shapefiles = shapefiles_subdivididos
    shapefiles_folder = shapefiles_folder_subdivididos
    category_dict = categories_individuais if layer_type == 'Mesclados' else categories

    st.sidebar.caption("Marque as camadas que deseja visualizar no mapa:")
    for category, files in category_dict.items():
        with st.sidebar.expander(f"{category}"):
            # Inicializa estado dos checkboxes se não existir
            if "checkbox_states" not in st.session_state:
                st.session_state.checkbox_states = {}

            # Botões Selecionar tudo / Limpar tudo
            col_btns = st.columns([1, 1])
            select_all = col_btns[0].button(f"Selecionar tudo ({category})", key=f"sel_all_{category}")
            deselect_all = col_btns[1].button(f"Limpar tudo ({category})", key=f"desel_all_{category}")

            for shp in files:
                if shp in shapefiles:
                    label = fmt_layer_name(shp)

                    # Define valor inicial de acordo com botão clicado
                    if select_all:
                        st.session_state.checkbox_states[shp] = True
                    elif deselect_all:
                        st.session_state.checkbox_states[shp] = False

                    # Pega estado salvo ou define True por padrão
                    checked = st.session_state.checkbox_states.get(shp, True)
                    st.session_state.checkbox_states[shp] = st.checkbox(label, value=checked, key=f"{category}-{shp}")

                    if st.session_state.checkbox_states[shp]:
                        selected_layers.append(shp)


    # Área principal: mapa + botão de download
    if selected_layers:
        map_obj = create_map(shapefiles_folder, selected_layers)
        st_data = st_folium(map_obj, width=1100, height=640)
        st.divider()
        zip_buffer = create_shapefile_zip(shapefiles_folder, selected_layers)
        st.download_button(
            label="⬇️ Baixar Shapefiles Selecionados (.zip)",
            data=zip_buffer,
            file_name="shapefiles_selecionados.zip",
            mime="application/zip",
            help="Faz o download de todos os arquivos necessários (.shp, .shx, .dbf, .prj, .cpg) das camadas marcadas."
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

    # Inicializa sessão
    if "dados" not in st.session_state:
        st.session_state.dados = []

    modo = st.radio("Como deseja inserir os dados?", ("Inserir Manualmente", "Carregar Arquivo CSV"))

    if modo == "Inserir Manualmente":
        with st.form("entrada_dados"):
            st.markdown("#### 📌 Inserir Novo Ponto")
            col_a, col_b = st.columns(2)
            with col_a:
                latitude = st.number_input("Latitude", format="%.6f", min_value=-90.0, max_value=90.0)
                tipo_fundo = st.selectbox("Tipo de Fundo (Substrato)", ["Sand", "Mud", "Coarse", "Mixed", "Hard/Rock"])
            with col_b:
                longitude = st.number_input("Longitude", format="%.6f", min_value=-180.0, max_value=180.0)
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

    else:
        st.markdown("#### 📂 Enviar Arquivo CSV")
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])

        if uploaded_file is not None:
            # Tentativas de encoding
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
                col1, col2 = st.columns(2)
                with col1:
                    col_latitude = st.selectbox("Selecione a coluna para Latitude", colunas_disponiveis)
                    col_tipo_fundo = st.selectbox("Selecione a coluna para Tipo de Fundo", colunas_disponiveis)
                with col2:
                    col_longitude = st.selectbox("Selecione a coluna para Longitude", colunas_disponiveis)
                    col_class_biogenica = st.selectbox("Selecione a coluna para Classificação Biogênica", colunas_disponiveis)

                if st.button("Carregar Dados"):
                    df_mapeado = df_uploaded[[col_latitude, col_longitude, col_tipo_fundo, col_class_biogenica]].copy()
                    df_mapeado.columns = ["Latitude", "Longitude", "Tipo de Fundo", "Classificação Biogênica"]
                    st.session_state.dados.extend(df_mapeado.to_dict(orient="records"))
                    st.success("✅ Dados carregados com sucesso!")

    # Tabela + download CSV do que foi inserido
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        st.markdown("#### 📋 Dados Inseridos")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Baixar CSV dos Dados Inseridos",
            data=csv,
            file_name="dados_marinhos.csv",
            mime="text/csv"
        )

# =========================
# 3) PROCESSAR DADOS
# =========================
elif view == "🧾 Consultar Dados":
    st.subheader("⚙️ Processamento / Modelo")
    st.markdown(
        "Aqui você pode visualizar dados tabulares utilizados no processamento e acionar o modelo. "
        "Lembre-se: **os dados enviados pelo usuário passam por avaliação** antes de serem incorporados."
    )

    st.markdown("#### Tabela de referência (df_teste)")
    st.dataframe(df_teste, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Executar Modelo"):
            with st.spinner("Iniciando o modelo..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)  # Simulação visual
                    progress.progress(i + 1)
                # CHAMADA REAL: chama_modelo()
            st.success("✅ Execução concluída!")
    with col2:
        st.button("Ajuda")

# =========================
# 4) SOBRE O ATLAS
# =========================
elif view == "ℹ️ Sobre o Atlas":
    st.subheader("ℹ️ Sobre o Atlas")
    st.markdown(
        """
Este atlas segue a **classificação EUNIS** (European Nature Information System), **adaptada** para os ambientes marinhos brasileiros.

**Camadas/níveis principais:**
- **Zona** (ex.: Littoral, Circalittoral, Offshore, Upper Bathyal)
- **Substrato** (ex.: Hard Rock, Coarse, Sand, Mixed, Mud)
- **Biogênico** (ex.: Recifal, Rodólitos, Biogênico, Terrígeno)

🔒 **Transparência e qualidade dos dados**
- O atlas **não é atualizado em tempo real** para usuários finais.
- Contribuições de usuários são **avaliadas** tecnicamente antes de integrar ao modelo/base.
- O objetivo é garantir **consistência e confiabilidade** do mapeamento.
        """
    )

# =========================
# (Opcional) Redefinição da função duplicada no fim do seu código original — já não é necessária aqui.
# Mantida apenas se você quiser reutilizá-la em outro ponto.
# =========================
def load_shapefiles(shapefiles_folder):
    return [f for f in os.listdir(shapefiles_folder) if f.endswith('.shp')]
