import streamlit as st
import geopandas as gpd
import requests
import geojson
from owslib.wfs import WebFeatureService

# 1. Captura dos dados WFS
url = 'https://ide.geobases.es.gov.br/geoserver/ows'
wfs = WebFeatureService(url, version='1.1.0')
layer = 'NOME_DA_CAMADA_AQUI'
response = wfs.getfeature(typename=layer, outputFormat='application/json')
gdf = gpd.GeoDataFrame.from_features(geojson.loads(response.read()))

# 2. Converter para colunas lat/lon
gdf['latitude'] = gdf.geometry.y
gdf['longitude'] = gdf.geometry.x

# 3. Exibir mapa simples
st.title("Visualização de WFS com Streamlit")
st.map(gdf[['latitude', 'longitude']])
