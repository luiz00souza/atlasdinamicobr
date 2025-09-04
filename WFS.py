from owslib.wfs import WebFeatureService
import geopandas as gpd
import json

url = "https://ide.geobases.es.gov.br/geoserver/ows"
wfs = WebFeatureService(url, version="1.1.0")

# Veja todas as camadas disponíveis
print(list(wfs.contents))

# Escolha uma camada real do servidor
layer = "geobases:limite_municipal"  # exemplo, troque pelo nome certo

# Testar formatos alternativos
response = wfs.getfeature(
    typename=layer,
    outputFormat="json"   # tente também "GEOJSON" ou "application/json"
)

gdf = gpd.GeoDataFrame.from_features(json.loads(response.read()))
print(gdf.head())
