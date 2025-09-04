from owslib.wfs import WebFeatureService

url = "https://ide.geobases.es.gov.br/geoserver/ows"
wfs = WebFeatureService(url, version="1.1.0")

# Lista todas as camadas disponíveis
for layer in list(wfs.contents):
    print(layer)
