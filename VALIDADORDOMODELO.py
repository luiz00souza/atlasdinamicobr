import numpy as np
import geopandas as gpd
import rasterio
from shapely.geometry import Point
from rasterio.windows import Window
from GERADORDEMODELO import *

# Caminhos dos arquivos
CAMINHO_RASTER = r'C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\arrays padronizados\NovoRasterReclassificado_Concatenacao.tif'
CAMINHO_CSV = r'C:\Users\campo\Desktop\mestrado\DADOS BRUTOS\merge_dhn_labogeo\merge classificado clipped.csv'
CAMINHO_SHAPEFILE = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\DadosBrutos\pontos.shp"







def amostrar_raster_por_pontos(raster, df):
    """Amostra o raster por pontos fornecidos em um DataFrame"""
    if 'Longitude' not in df.columns or 'Latitude' not in df.columns:
        raise ValueError("As colunas 'Longitude' e 'Latitude' não estão presentes no CSV.")
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    geo_df = gpd.GeoDataFrame(df, geometry=geometry)
    geo_df.set_crs(epsg=4326, inplace=True)
    geo_df.to_file(CAMINHO_SHAPEFILE, driver='ESRI Shapefile')
    pontos = gpd.read_file(CAMINHO_SHAPEFILE)
    valores_amostrados = []
    with rasterio.open(raster) as src:
        for i, geom in enumerate(pontos.geometry):
            coords = [(geom.x, geom.y)]
            for coord in coords:
                row, col = src.index(coord[0], coord[1])
                janela = Window(col, row, 1, 1)
                data = src.read(1, window=janela)
                if data.size > 0:
                    valores_amostrados.append(data[0][0])
                else:
                    valores_amostrados.append(None)
    return valores_amostrados


def verificar_valores_amostrados(valores_amostrados, valores_possiveis):
    """Verifica os valores amostrados e sua presença no raster"""
    valores_amostrados_unicos = np.unique([v for v in valores_amostrados if v is not None])
    valores_nao_presentes = np.setdiff1d(valores_amostrados_unicos, valores_possiveis)
    valores_presentes = np.intersect1d(valores_amostrados_unicos, valores_possiveis)
    return valores_presentes, valores_nao_presentes

def calcular_porcentagem_linhas_iguais(coluna1, coluna2):
    """Calcula a porcentagem de linhas iguais entre duas colunas"""
    linhas_coluna1 = set(coluna1)
    linhas_coluna2 = set(coluna2)
    linhas_comuns = linhas_coluna1 & linhas_coluna2
    num_linhas_comuns = len(linhas_comuns)
    total_linhas_coluna1 = len(linhas_coluna1)
    if total_linhas_coluna1 > 0:
        return (num_linhas_comuns / total_linhas_coluna1) * 100
    else:
        return 0.0

def processar_dados(caminho_raster):
    gen_col = df.columns[df.columns.str.startswith('Gen_')][-1]
    df_teste = df[df[gen_col] == 'Teste']
    valores_amostrados = amostrar_raster_por_pontos(caminho_raster, df_teste)
    df_teste['Valor_Amostrado'] = valores_amostrados
    with rasterio.open(caminho_raster) as src:
        data = src.read(1)
        valores_possiveis = np.unique(data)
    valores_presentes, valores_nao_presentes = verificar_valores_amostrados(valores_amostrados, valores_possiveis)
    porcentagem_linhas_iguais = calcular_porcentagem_linhas_iguais(df_teste['Valor_Amostrado'], df_teste['ID_CLASSIFICACAO_FINAL'])
    print(f"Porcentagem de linhas iguais entre modelo e dados brutos: {porcentagem_linhas_iguais:.5f}%")
    df_resultados=df_teste
    return {
        "df_resultados":df_resultados,
        "df_teste": df_teste,
        "valores_presentes": valores_presentes,
        "valores_nao_presentes": valores_nao_presentes,
        "porcentagem_linhas_iguais": porcentagem_linhas_iguais
    }

# resultados = processar_dados(CAMINHO_RASTER)

# Exibir os resultados
# print(f"Porcentagem de linhas iguais entre modelo e dados brutos: {resultados['porcentagem_linhas_iguais']:.5f}%")
# print(f"Valores amostrados que não estão presentes no raster: {resultados['valores_nao_presentes']}")
# print(f"Valores amostrados que estão presentes no raster: {resultados['valores_presentes']}")
