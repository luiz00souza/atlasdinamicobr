# -*- coding: utf-8 -*-
"""
Sistema de Atlas de Habitats Marinhos (Baseado em EUNIS)
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ==============================
# CONFIGURAÇÃO GERAL
# ==============================
st.set_page_config(
    page_title="Atlas de Habitats Marinhos",
    page_icon="🌊",
    layout="wide"
)

# ==============================
# TÍTULO PRINCIPAL
# ==============================
st.title("🌍 Atlas de Habitats Marinhos")
st.markdown(
    """
    Bem-vindo ao **Atlas de Habitats Marinhos**.  
    Este sistema mostra os habitats classificados com base no padrão internacional **EUNIS**, 
    adaptado para o Brasil.  

    📌 Você pode:
    - Explorar o **mapa interativo**.  
    - **Enviar novos dados** para avaliação.  
    - Consultar **informações sobre a metodologia**.  
    """
)

# ==============================
# SIDEBAR (BARRA LATERAL)
# ==============================
st.sidebar.title("⚙️ Opções")

menu = st.sidebar.radio(
    "Escolha o que deseja visualizar:",
    ["🌍 Mapa Interativo", "📤 Enviar Dados", "ℹ️ Informações"]
)

# ==============================
# 1. MAPA INTERATIVO
# ==============================
if menu == "🌍 Mapa Interativo":
    st.subheader("Mapa Interativo dos Habitats")

    st.sidebar.markdown("### 🗺️ Camadas do Mapa")
    mostrar_littoral = st.sidebar.checkbox("Littoral", True)
    mostrar_circalittoral = st.sidebar.checkbox("Circalittoral", True)
    mostrar_offshore = st.sidebar.checkbox("Offshore", False)
    mostrar_bathyal = st.sidebar.checkbox("Bathyal", False)
    mostrar_abissal = st.sidebar.checkbox("Abissal", False)

    # Criar mapa base
    mapa = folium.Map(location=[-15, -40], zoom_start=4, tiles="CartoDB positron")

    # Adiciona camadas simuladas
    if mostrar_littoral:
        folium.Marker([-22.9, -43.1], popup="Habitat Littoral", tooltip="Littoral").add_to(mapa)
    if mostrar_circalittoral:
        folium.Marker([-8.0, -34.9], popup="Habitat Circalittoral", tooltip="Circalittoral").add_to(mapa)
    if mostrar_offshore:
        folium.Marker([-3.7, -38.5], popup="Habitat Offshore", tooltip="Offshore").add_to(mapa)
    if mostrar_bathyal:
        folium.Marker([-1.4, -48.5], popup="Habitat Bathyal", tooltip="Bathyal").add_to(mapa)
    if mostrar_abissal:
        folium.Marker([-20.3, -40.3], popup="Habitat Abissal", tooltip="Abissal").add_to(mapa)

    # Exibir mapa
    st_data = st_folium(mapa, width=900, height=600)

# ==============================
# 2. ENVIAR DADOS
# ==============================
elif menu == "📤 Enviar Dados":
    st.subheader("📤 Enviar Novos Dados")

    st.markdown(
        """
        Aqui você pode enviar novos pontos de dados (CSV).  
        ⚠️ **Atenção**: Seu envio **não será incorporado automaticamente** ao Atlas.  
        Todos os dados passam por **avaliação técnica** antes de serem integrados.  
        """
    )

    uploaded_file = st.file_uploader("Selecione seu arquivo CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("✅ Arquivo carregado com sucesso!")
            st.dataframe(df.head())
            st.info("Seus dados foram recebidos e serão avaliados pela equipe.")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

# ==============================
# 3. INFORMAÇÕES
# ==============================
elif menu == "ℹ️ Informações":
    st.subheader("ℹ️ Sobre o Sistema")

    st.markdown(
        """
        Este **Atlas de Habitats Marinhos** é baseado na classificação **EUNIS**,
        adaptada às condições brasileiras.  

        ### Estrutura da Classificação:
        - **Nível Hidronímico**: Littoral, Circalittoral, Offshore, Bathyal, Abissal.  
        - **Nível de Substrato**: Hard Rock, Coarse, Sand, Mixed, Mud.  
        - **Nível Biogênico**: Recifal, Rhodolite, Biogenic not specified, Terrigenous.  

        O **mapa é atualizado continuamente** pela equipe técnica,
        mas os usuários podem **enviar novos dados** para avaliação.  

        📌 Dessa forma, garantimos que o atlas seja sempre confiável e atualizado.  
        """
    )
