import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask

from rasterio.warp import reproject, calculate_default_transform, Resampling
from shapely.geometry import mapping
import numpy as np
from osgeo import gdal, ogr, osr
from scipy.interpolate import griddata
import pandas as pd
from sklearn.model_selection import train_test_split
from scipy.ndimage import distance_transform_edt

from pathlib import Path

# Base
base = Path(r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25")

# Caminhos
file_path = base / "DadosBrutos" / "ALLDATA_onehot_clipped.csv"
dir_path = base / "4_Recortados"
out_path = base / "arrays padronizados"
raster_seabed = out_path / "SEABED.tif"
raster_biotipos = out_path / "BIOTIPOS.tif"
shapefile_plataforma = base / "DadosBrutos" /"PlataformaES.shp"

latitude_media = -21
resolucao_metros = 1000

column_names = {
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'HardRock': 'HardRock',
    'Coarse': 'Coarse',
    'Sand': 'Sand',
    'Mixed':'Mixed',
    'Mud': 'Sud',
    'Terrigenous': 'Terrigenous',
    'Biogenic': 'Biogenic',
    'Recifal': 'Recifal',
    'Rhodolite':'Rhodolite'
    }
columns_to_process = [
    'HardRock',
    'Coarse',
    'Sand',
    'Mixed',
    'Mud',
    'Terrigenous',
    'Biogenic',
    'Recifal',
    'Rhodolite',
]

seabed_rasters_names = [
    #"NaN" #0
    'Coarse_clipped.tif', #1
    'Mixed_clipped.tif', #2
    'Mud_clipped.tif', #3
    'Sand_clipped.tif', #4
    'HardRock_clipped.tif'#5
]
biogenic_rasters_names = [ 
    #"NaN" #0
    'Biogenic_clipped.tif', #1
    'Recifal_clipped.tif', #2
    'Rhodolite_clipped.tif', #3
    'Terrigenous_clipped.tif' #4
]

seabed_rasters = ['Coarse_clipped.tif', 'Mixed_clipped.tif', 'Mud_clipped.tif', 'Sand_clipped.tif', 'HardRock_clipped.tif']


def metros_para_graus(resolucao_metros, latitude_media):
    "CONVERTE METROS PARA GRAUS"
    metros_para_graus_latitude = 1 / 111000
    metros_para_graus_longitude = 1 / (111000 * np.cos(np.deg2rad(latitude_media)))
    largura_pixel_deg = resolucao_metros * metros_para_graus_longitude
    altura_pixel_deg = resolucao_metros * metros_para_graus_latitude
    return largura_pixel_deg, altura_pixel_deg

def split_train_test(df, test_size=0.3, gen_prefix='Gen'):
    """Divide o DataFrame em treinamento e teste"""
    train_indices, test_indices = train_test_split(df.index, test_size=test_size)
    gen_col = f'{gen_prefix}_{len([col for col in df.columns if gen_prefix in col]) + 1}'
    df[gen_col] = 'Teste'
    df.loc[train_indices, gen_col] = 'Treinamento'
    return df


class ProcessamentoDados:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.interpolate_folder = os.path.join(base_dir, '0_Interpolados')
        self.reclassified_folder = os.path.join(base_dir, '1_Reclassificados')
        # self.polygonized_folder = os.path.join(base_dir, '2_Poligonizados')
        # self.filtered_folder = os.path.join(base_dir, '3_Filtrados')
        self.clipped_folder = os.path.join(base_dir, '4_Recortados')
        self.raster_batimetria = os.path.join(base_dir, 'BATIMETRIA_ZEE_WGS84.tif')
        self.recorte_area_de_estudo = os.path.join(base_dir, 'DadosBrutos/PlataformaES.shp')      
        # self.hidroseabed = os.path.join(base_dir, '5_Hidroseabed')
        # self.Classe2 = os.path.join(base_dir, '5_Hidroseabed/Classe2')
        # self.Classe3 = os.path.join(base_dir, '5_Hidroseabed/Classe3')
        # self.Classe3Recortada = os.path.join(base_dir, '6_Classe3Recortada')

        
        self.threshold_value = 0.5
        self.hidroninamic_limits = {
            1: (-10, 0),         # LITTORAL LIMITES
            2: (-30, -11),       # CIRCALITTORAL LIMITES
            3: (-200, -31),      # OFFSHORE LIMITES
            4: (-2000, -201),    # LOWER BATHYAL LIMITES
            5: (-6000, -2001),   # BATHYAL LIMITES
            6: (-16000, -6001)   # ABYSSAL LIMITES
        }
    
    def interpolate_and_save_tiff(self, input_file, column_names):
        for column_name in columns_to_process:
            # data = pd.read_csv(input_file, sep=',', usecols=range(len(column_names)))
            # data=df[df['Gen_1'] == 'Treinamento']
            data=df

            x = data[column_names['Longitude']]
            y = data[column_names['Latitude']]
            z = data[column_name]
            xi = np.linspace(min(x), max(x), 6554)
            yi = np.linspace(min(y), max(y), 6217)
            xi, yi = np.meshgrid(xi, yi)
            zi = griddata((x, y), z, (xi, yi), method='linear')
            yi = np.flipud(yi)
            zi = np.flipud(zi)
            
            # Calcular a largura e altura dos pixels em graus
            
            largura_pixel_deg = 0.0005  # Largura do pixel em graus
            altura_pixel_deg = 0.0005 # Altura do pixel em graus
            
            # Salvar o arquivo TIFF interpolado
            transform = rasterio.transform.from_origin(xi.min(), yi.max(), largura_pixel_deg, altura_pixel_deg)
            output_file = os.path.join(self.interpolate_folder, f"{column_name}.tif")
            # print(output_file)
            print(f"Salvando {output_file} dim: {zi.shape[1]} x {zi.shape[0]}")

            with rasterio.open(output_file, 'w', driver='GTiff', height=zi.shape[0], width=zi.shape[1], count=1,
                                dtype=zi.dtype, transform=transform) as dst:
                dst.write(zi, 1)
            # break #REMOVER O BREAK

        print("CSV interpolado e Rasters Gerados")
    def reclassify_raster(self, input_path, output_dir):
        try:
            with rasterio.open(input_path) as src:
                raster_data = src.read(1)
                reclassified_data = np.where(raster_data > self.threshold_value, 1, 0)
                meta = src.meta.copy()
                meta.update(dtype=rasterio.uint8)
                output_path = os.path.join(output_dir, f"{os.path.basename(input_path)}")
                with rasterio.open(output_path, 'w', **meta) as dst:
                    dst.write(reclassified_data, 1)
                print(f"Raster reclassificado salvo em: {output_path} dim:{meta['width']} x {meta['height']}")

        except Exception as e:
            print(f"Erro ao reclassificar raster: {e}")

    def reclassify_all_rasters(self):
        try:
            os.makedirs(self.reclassified_folder, exist_ok=True)
            for filename in os.listdir(self.interpolate_folder):
                if filename.endswith(".tif"):
                    input_path = os.path.join(self.interpolate_folder, filename)
                    self.reclassify_raster(input_path, self.reclassified_folder)

        except Exception as e:
            print(f"Erro ao reclassificar todos os rasters: {e}")

    def raster_to_polygon(self, input_raster, output_polygon):
        try:
            raster_ds = gdal.Open(input_raster)
            raster_band = raster_ds.GetRasterBand(1)
            srs = osr.SpatialReference()
            srs.ImportFromWkt(raster_ds.GetProjection())
            driver = ogr.GetDriverByName("ESRI Shapefile")
            out_ds = driver.CreateDataSource(output_polygon)
            out_layer = out_ds.CreateLayer("polygonized", srs=srs)
            id_field = ogr.FieldDefn("id", ogr.OFTInteger)
            out_layer.CreateField(id_field)
            gdal.Polygonize(raster_band, None, out_layer, 0, [], callback=None)
            out_ds = None
            raster_ds = None
            

        except Exception as e:
            print(f"Erro ao converter raster para polígono: {e}")

    def all_rasters_to_polygons(self):
        try:
            os.makedirs(self.polygonized_folder, exist_ok=True)
            for filename in os.listdir(self.reclassified_folder):
                if filename.endswith(".tif"):
                    input_raster = os.path.join(self.reclassified_folder, filename)
                    output_polygon = os.path.join(self.polygonized_folder, f"{os.path.splitext(filename)[0]}P.shp")
                    self.raster_to_polygon(input_raster, output_polygon)
            print("Rasters Poligonizados")
        except Exception as e:
            print(f"Erro ao converter todos os rasters para polígonos: {e}")

    def all_shapefiles_filter_and_save(self):
        try:
            os.makedirs(self.filtered_folder, exist_ok=True)
            for filename in os.listdir(self.polygonized_folder):
                if filename.endswith('.shp'):
                    input_shapefile = os.path.join(self.polygonized_folder, filename)
                    pontos = gpd.read_file(input_shapefile, encoding='latin1')
                    pontos_id_1 = pontos[pontos['id'] == 1]
                    output_filename = os.path.splitext(filename)[0] + "F.shp"
                    output_path = os.path.join(self.filtered_folder, output_filename)
                    pontos_id_1.to_file(output_path)
            print("Poligonos filtrados")
        except Exception as e:
            print(f"Erro ao filtrar e salvar shapefiles: {e}")

    def recortar_e_salvar(self):
        try:
            os.makedirs(self.clipped_folder, exist_ok=True)
            mascara = gpd.read_file(self.recorte_area_de_estudo)
            for filename in os.listdir(self.filtered_folder):
                if filename.endswith('.shp'):
                    input_shapefile = os.path.join(self.filtered_folder, filename)
                    poligono = gpd.read_file(input_shapefile)
                    poligono_recortado = gpd.overlay(poligono, mascara, how='intersection')
                    output_filename = os.path.splitext(filename)[0] + "R.shp"
                    output_path = os.path.join(self.clipped_folder, output_filename)
                    poligono_recortado.to_file(output_path)
            print("Poligonos recortados e salvos")
        except Exception as e:
            print(f"Erro ao recortar e salvar: {e}")


    def recortar_e_salvar_rasters(self):
        try:
            os.makedirs(self.clipped_folder, exist_ok=True)
            # Ler a máscara como um GeoDataFrame
            mascara = gpd.read_file(self.recorte_area_de_estudo)
    
            for filename in os.listdir(self.reclassified_folder):
                if filename.endswith('.tif'):
                    input_raster = os.path.join(self.reclassified_folder, filename)
    
                    with rasterio.open(input_raster) as src:
                        # Convertendo o GeoDataFrame para o formato de máscara esperado pelo rasterio
                        geometries = [mapping(geom) for geom in mascara.geometry]
                        out_image, out_transform = rasterio.mask.mask(src, geometries, crop=True)
                        out_meta = src.meta.copy()
    
                        out_meta.update({"driver": "GTiff",
                                         "height": out_image.shape[1],
                                         "width": out_image.shape[2],
                                         "transform": out_transform})
    
                        # Print dimensions of the cropped array
                        print(f"Tamanho do array recortado ({filename}): {out_image.shape}")
    
                        output_filename = os.path.splitext(filename)[0] + "_clipped.tif"
                        output_path = os.path.join(self.clipped_folder, output_filename)
    
                        with rasterio.open(output_path, "w", **out_meta) as dest:
                            dest.write(out_image)
    
            print("Rasters recortados e salvos")
        except Exception as e:
            print(f"Erro ao recortar e salvar: {e}")

    def reclass_batimetria(self):
        try:
            with rasterio.open(self.raster_batimetria) as src:
                batimetria = src.read(1)
                profile = src.profile
                batimetria_reclassificada = np.zeros_like(batimetria, dtype=np.uint8)
                
                for classe, (limite_inferior, limite_superior) in self.hidroninamic_limits.items():
                    batimetria_reclassificada[(batimetria >= limite_inferior) & (batimetria <= limite_superior)] = classe
    
                # Calcular nova transformação com resolução de 0.001 graus
                transform, width, height = calculate_default_transform(
                    src.crs, src.crs, src.width, src.height, resolution=(0.001, 0.001),
                    left=src.bounds.left, bottom=src.bounds.bottom, right=src.bounds.right, top=src.bounds.top
                )
                
                profile.update({
                    'dtype': rasterio.uint8,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
    
                output_tif = os.path.join(out_path, 'Batimetria.tif')
                print(f"Salvando {output_tif} dim: {width} x {height}")

                # Reprojetar e reamostrar os dados
                with rasterio.open(output_tif, 'w', **profile) as dst:
                    reclassificada_reprojetada = np.empty((height, width), dtype=rasterio.uint8)
                    reproject(
                        source=batimetria_reclassificada,
                        destination=reclassificada_reprojetada,
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=src.crs,
                        resampling=Resampling.nearest
                    )
                    dst.write(reclassificada_reprojetada, 1)
                
    
            print(f"Batimetria Reclassificada salva em: {output_tif}")
        except Exception as e:
            print(f"Erro ao reclassificar batimetria: {e}")
    def segmentar_batimetria(self):
        try:
            pontos = gpd.read_file(os.path.join(self.polygonized_folder, 'BatimetriaP.shp'), encoding='latin1')
            os.makedirs(self.filtered_folder, exist_ok=True)
            for id_value in pontos['id'].unique():
                pontos_id = pontos[pontos['id'] == id_value]
                output_filename = f"{id_value+1}_hid_class.shp"
                output_path = os.path.join(self.filtered_folder, output_filename)
                pontos_id.to_file(output_path)
            print("Batimetria Segmentada")
        except Exception as e:
            print(f"Erro ao segmentar batimetria: {e}")
    def recortar_e_salvar_HidroSeaBed(self):
        os.makedirs(self.clipped_folder, exist_ok=True)
        for mask_filename in os.listdir(self.clipped_folder):
            if mask_filename.endswith('classR.shp'):
                mask_path = os.path.join(self.clipped_folder, mask_filename)
                mascara = gpd.read_file(mask_path)
                for filename in os.listdir(self.clipped_folder):
                    if filename.endswith('PFR.shp'):
                        input_shapefile = os.path.join(self.clipped_folder, filename)
                        poligono = gpd.read_file(input_shapefile)
                        poligono_recortado = gpd.overlay(poligono, mascara, how='intersection')
                        output_filename = os.path.splitext(filename)[0] + os.path.splitext(mask_filename)[0] + ".shp"
                        output_path = os.path.join(self.hidroseabed, output_filename)
                        poligono_recortado.to_file(output_path)
                        
    def recortar_classe3_com_mascaras_classe2(self):
        os.makedirs(self.Classe3, exist_ok=True)
        for mask_filename in os.listdir(self.Classe3):
            # print(mask_filename)
            if mask_filename.endswith('classR.shp'):
                # print(mask_filename)

                mask_path = os.path.join(self.Classe3, mask_filename)
                mascara = gpd.read_file(mask_path)
                for filename in os.listdir(self.Classe3):

                    if filename.endswith('PFR.shp'):
                        print(mask_filename,filename)

                        input_shapefile = os.path.join(self.Classe3, filename)
                        poligono = gpd.read_file(input_shapefile)
                        poligono_recortado = gpd.overlay(poligono, mascara, how='intersection')
                        output_filename = os.path.splitext(filename)[0] +'_'+ os.path.splitext(mask_filename)[0] + ".shp"
                        output_path = os.path.join(self.Classe3Recortada, output_filename)
                        poligono_recortado.to_file(output_path)
def somar_rasters_com_pesos(dir_path, out_path, raster_names, nome):
    pesos = list(range(1, len(raster_names) + 1))
    raster_paths = [os.path.join(dir_path, raster_name) for raster_name in raster_names]
    output_path = os.path.join(out_path, f'{nome}.tif')
    

    assert len(raster_paths) == len(pesos), "O número de pesos deve ser igual ao número de rasters."

    with rasterio.open(raster_paths[0]) as src:
        profile = src.profile
        data = src.read(1) * pesos[0]  # Multiplicando pelo peso correspondente

    for i in range(1, len(raster_paths)):
        with rasterio.open(raster_paths[i]) as src:
            data += src.read(1) * pesos[i]  # Multiplicando pelo peso correspondente
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data, 1)
    print(f'Raster {nome} gerado. dim: {profile["width"]} x {profile["height"]}')

def preencher_zeros_iterativamente(data, max_iter=30):
    """
    Preenche valores zero iterativamente com os valores mais próximos até que
    não reste nenhum zero ou atinja o número máximo de iterações.
    """
    for i in range(max_iter):
        mask_zeros = (data == 0)
        if not np.any(mask_zeros):
            print(f"✅ Todos os valores 0 foram preenchidos em {i} iterações.")
            break

        nearest_indices = distance_transform_edt(mask_zeros, return_distances=False, return_indices=True)
        data[mask_zeros] = data[tuple(nearest_indices[:, mask_zeros])]
        print(f"Iteração {i+1}: Restam {np.sum(data == 0)} valores 0")

    return data

def preencher_zeros_por_valor_mais_proximo(raster_paths, shapefile_path):
    """
    Preenche pixels com valor 0 nos rasters fornecidos usando o valor mais próximo,
    aplica recorte com a máscara ao final e salva por cima dos arquivos originais.
    """
    gdf = gpd.read_file(shapefile_path)
    shapes = [feature["geometry"] for feature in gdf.__geo_interface__["features"]]

    for raster_path in raster_paths:
        print(f"\n🔄 Processando: {raster_path}")
        with rasterio.open(raster_path, 'r+') as src:
            data = src.read(1)
            profile = src.profile

            # Aplica o recorte com a máscara para limitar o processamento
            data_crop, _ = mask(src, shapes, crop=False, filled=False, nodata=0)
            data_crop = data_crop[0]

            # Preencher zeros iterativamente
            data_preenchido = preencher_zeros_iterativamente(data_crop.copy(), max_iter=30)

            # Substitui os dados da área de máscara no raster original
            mask_valida = ~np.isnan(data_preenchido)
            data[mask_valida] = data_preenchido[mask_valida]

            # Escreve os dados no próprio raster
            src.write(data, 1)

            # Verificação final
            n_zeros = np.sum(data == 0)
            if n_zeros == 0:
                print(f"✅ Final: nenhum valor 0 remanescente em {raster_path}")
            else:
                print(f"⚠️ Final: ainda restam {n_zeros} pixels com valor 0 em {raster_path}")

            # Estatísticas finais
            unique, counts = np.unique(data, return_counts=True)
            print("📊 Valores únicos finais:")
            for val, count in zip(unique, counts):
                print(f"{val}: {count} pixels")
df = pd.read_csv(file_path)

df = split_train_test(df, test_size=0.3)
df_teste = df[df['Gen_1'] == 'Teste']

# Execução das operações
# largura_pixel_deg, altura_pixel_deg = metros_para_graus(resolucao_metros, latitude_media)

# Executa o preenchimento para ambos
# preencher_zeros_por_valor_mais_proximo(raster_seabed)
# preencher_zeros_por_valor_mais_proximo(raster_biotipos)

# try:
#     processamento = ProcessamentoDados(r'C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25')
#     processamento.interpolate_and_save_tiff(file_path, column_names)    #Interpola e salva os arquivos tiff para cada coluna binaria(onehotencoding)

    # processamento.reclass_batimetria()#Reclassifica a batimetria
    # processamento.reclassify_all_rasters()
#     # processamento.all_rasters_to_polygons() #nao utilizado
#     # processamento.all_shapefiles_filter_and_save()#nao utilizado
#     # processamento.segmentar_batimetria()#nao utilizado
#     # processamento.recortar_e_salvar()#nao utilizado
    # processamento.recortar_e_salvar_rasters()

#     # processamento.recortar_e_salvar_HidroSeaBed()#nao utilizado
    # processamento.recortar_classe3_com_mascaras_classe2()  # Nova função para recortar Classe 3 com máscaras da Classe 2 #nao utilizado
    # somar_rasters_com_pesos(dir_path,out_path, seabed_rasters_names, nome='SEABED')
    # somar_rasters_com_pesos(dir_path, out_path, biogenic_rasters_names, nome ='BIOTIPOS')
# except Exception as e:
#     print(f"Erro durante o processamento: {e}")
