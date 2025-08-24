import os
import rasterio
import numpy as np
from rasterio.enums import Resampling
import os
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import rasterio
from scipy.ndimage import generic_filter
from collections import Counter
import os
input_tif = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\arrays padronizados\NovoRasterReclassificado_Concatenacao.tif"
output_tif = input_tif.replace(".tif", "_suavizado.tif")
diretorio = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\arrays padronizados"
batimetria= "Batimetria.tif"
arquivo_tif1 = "HIDRODINAMIC.tif"
arquivo_tif2 = "SEABED.tif"
arquivo_tif3 = "BIOTIPOS.tif"
shapefile_plataforma = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\DadosBrutos\PlataformaES.shp"

novo_raster_nome = "NovoRasterReclassificado_Concatenacao.tif"



def recortar_e_reamostrar_hidrodinamic(diretorio, arquivo_seabed, arquivo_hidrodinamic, arquivo_saida_reamostrado, arquivo_saida_recortado, shp_mascara):
    seabed_path = os.path.join(diretorio, arquivo_seabed)
    hidrodinamic_path = os.path.join(diretorio, arquivo_hidrodinamic)
    output_reamostrado = os.path.join(diretorio, arquivo_saida_reamostrado)
    output_recortado = os.path.join(diretorio, arquivo_saida_recortado)

    # Ler shapefile da máscara
    gdf_mask = gpd.read_file(shp_mascara)
    geometries = gdf_mask.geometry.values

    # Abrir raster SEABED
    with rasterio.open(seabed_path) as src_seabed:
        width_seabed = src_seabed.width
        height_seabed = src_seabed.height
        profile_seabed = src_seabed.profile

    # Abrir raster HIDRODINAMIC e recortar
    with rasterio.open(hidrodinamic_path) as src_hidrodinamic:
        data_recortada, transform_recortada = mask(src_hidrodinamic, geometries, crop=True)
        profile_recortado = src_hidrodinamic.profile.copy()
        profile_recortado.update({
            'height': data_recortada.shape[1],
            'width': data_recortada.shape[2],
            'transform': transform_recortada,
            'driver': 'GTiff'
        })

        # Salvar raster recortado
        with rasterio.open(output_recortado, 'w', **profile_recortado) as dst_rec:
            dst_rec.write(data_recortada)
        print(f'Arquivo recortado salvo: {output_recortado}')

    # Agora reamostrar o raster recortado para as dimensões do SEABED
    with rasterio.open(output_recortado) as src_recortado:
        data_reamostrada = src_recortado.read(
            1,
            out_shape=(1, height_seabed, width_seabed),
            resampling=Resampling.nearest
        )
        profile_reamostrado = profile_seabed.copy()
        profile_reamostrado.update({
            'count': 1,
            'dtype': data_recortada.dtype,
            'driver': 'GTiff'
        })

        # Salvar raster reamostrado
        with rasterio.open(output_reamostrado, 'w', **profile_reamostrado) as dst_ream:
            dst_ream.write(data_reamostrada, 1)

    print(f'Arquivo recortado e reamostrado salvo: {output_reamostrado}')
def combinar_rasters(diretorio, arquivo_tif1, arquivo_tif2, arquivo_tif3, novo_raster_nome):
    # Caminhos completos
    caminho1 = os.path.join(diretorio, arquivo_tif1)
    caminho2 = os.path.join(diretorio, arquivo_tif2)
    caminho3 = os.path.join(diretorio, arquivo_tif3)

    # Leitura dos rasters
    with rasterio.open(caminho1) as src1, \
         rasterio.open(caminho2) as src2, \
         rasterio.open(caminho3) as src3:

        r1 = src1.read(1)
        r2 = src2.read(1)
        r3 = src3.read(1)
        perfil = src1.profile

    print("Valores únicos em", arquivo_tif1 + ":", np.unique(r1))
    print("Valores únicos em", arquivo_tif2 + ":", np.unique(r2))
    print("Valores únicos em", arquivo_tif3 + ":", np.unique(r3))
    print("Tamanho dos arrays:", r1.shape)

    # Concatenação r2 + r3 como strings
    r2_str = r2.astype(int).astype(str)
    r3_str = r3.astype(int).astype(str)
    combinado_r2r3_str = np.char.add(r2_str, r3_str)
    combinado_r2r3 = combinado_r2r3_str.astype(int)

    # Salvar raster intermediário r2r3
    nome_intermediario = novo_raster_nome.replace('.tif', '_r2r3.tif')
    caminho_intermediario = os.path.join(diretorio, nome_intermediario)
    perfil.update(dtype=rasterio.int32, count=1)

    with rasterio.open(caminho_intermediario, 'w', **perfil) as dst:
        dst.write(combinado_r2r3, 1)

    print("Raster intermediário salvo:", caminho_intermediario)
    print("Valores únicos no raster intermediário (r2r3):", np.unique(combinado_r2r3))

    # Concatenação r1 + combinado_r2r3
    r1_str = r1.astype(int).astype(str)
    r2r3_str = combinado_r2r3.astype(int).astype(str)
    combinado_final_str = np.char.add(r1_str, r2r3_str)
    combinado_final = combinado_final_str.astype(int)

    # Salvar raster final r1r2r3
    caminho_saida = os.path.join(diretorio, novo_raster_nome)
    with rasterio.open(caminho_saida, 'w', **perfil) as dst:
        dst.write(combinado_final, 1)

    print("Novo raster final salvo:", caminho_saida)
    print("Valores únicos no raster final (r1r2r3):", np.unique(combinado_final))

def moda_3x3(values):
    valores_validos = values[~np.isnan(values)]
    if len(valores_validos) == 0:
        return np.nan
    contagem = Counter(valores_validos)
    return contagem.most_common(1)[0][0]

# Função para suavizar com filtro de moda
def suavizar_raster_moda(input_tif, output_tif, tamanho_janela=3):
    with rasterio.open(input_tif) as src:
        data = src.read(1)
        perfil = src.profile

    print(f"Lendo raster: {input_tif}")
    print(f"Aplicando filtro de moda {tamanho_janela}x{tamanho_janela}...")

    # Aplica o filtro
    raster_suavizado = generic_filter(data, moda_3x3, size=tamanho_janela, mode='nearest')

    print(f"Salvando raster suavizado em: {output_tif}")
    with rasterio.open(output_tif, 'w', **perfil) as dst:
        dst.write(raster_suavizado.astype(perfil['dtype']), 1)

    print("Processo finalizado.")

# Executa
# suavizar_raster_moda(input_tif, output_tif, tamanho_janela=5)

# recortar_e_reamostrar_hidrodinamic(
#     diretorio,
#     arquivo_tif2,  # seabed
#     arquivo_tif1,  # hidrodinamic
#     f'{arquivo_tif1}_reamostrado.tif',  # arquivo saída reamostrado
#     f'{arquivo_tif1}_recortado.tif',    # arquivo saída recortado
#     shapefile_plataforma
# )

# combinar_rasters(diretorio, arquivo_tif1, arquivo_tif2, arquivo_tif3, novo_raster_nome)
