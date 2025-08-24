import os
import rasterio
import geopandas as gpd
from rasterio.features import shapes
from shapely.geometry import shape
# Exemplo de uso
raster_path = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\arrays padronizados\NovoRasterReclassificado_Concatenacao.tif"
# output_folder_categorias = r"C:\Users\campo\Desktop\mestrado\DADOS121223\Raster Reclassificados\Shapefiles_Classes_Categorias"
output_folder_subcategorias = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\arrays padronizados\Shapefiles_Classes"
arquivo_tif1 = "HIDRODINAMIC.tif"
arquivo_tif2 = "SEABED.tif"
arquivo_tif3 = "BIOTIPOS.tif"

# Dicionário de classes com seus valores no raster

hidro_map = {
    0: "",
    1: "littoral",
    2: "circalittoral",
    3: "offshore",
    4: "upper_bathyal"
}

seabed_map = {
    0: "",
    1: "coarse",
    2: "mixed",
    3: "mud",
    4: "sand",
    5: "hardrock"
}

biotipo_map = {
    0: "",
    1: "biogenic",
    2: "recifal",
    3: "rhodolite",
    4: "terrigeneous"
}

classes_dict = {}

import unicodedata

for r1 in range(5):  # hidro_map 
    for r2 in range(6):  # seabed_map
        for r3 in range(5):  # biotipo_map
            cod = int(f"{r1}{r2}{r3}")
            partes = [hidro_map[r1], seabed_map[r2], biotipo_map[r3]]
            partes_formatadas = []
            for p in partes:
                if p:
                    p = unicodedata.normalize("NFKD", p)
                    p = p.encode("ASCII", "ignore").decode("ASCII")
                    p = p.lower().replace(" ", "_")
                    partes_formatadas.append(p)
            if partes_formatadas:
                nome = "_".join(partes_formatadas)
                classes_dict[cod] = nome





# Dicionário de categorias gerais e as classes que pertencem a cada categoria
# categories_dict = {
#     'Coarse': ['Coarse Biogenic', 'Coarse Recifal', 'Coarse Rhodolite', 'Coarse Terrigenous'],
#     'Mixed': ['Mixed Biogenic', 'Mixed Recifal', 'Mixed Rhodolite', 'Mixed Terrigenous'],
#     'Mud': ['Mud Biogenic', 'Mud Recifal', 'Mud Rhodolite', 'Mud Terrigenous'],
#     'Sand': ['Sand Biogenic', 'Sand Recifal', 'Sand Rhodolite', 'Sand Terrigenous'],
#     'HardRock': ['HardRock Biogenic', 'HardRock Recifal', 'HardRock Rhodolite', 'HardRock Terrigenous']
# }

categories_dict = {
    'coarse': [
        'littoral_coarse_biogenic',
        'circalittoral_coarse_biogenic',
        'offshore_coarse_biogenic',
        'upper_bathyal_coarse_biogenic',
        'littoral_coarse_recifal',
        'circalittoral_coarse_recifal',
        'offshore_coarse_recifal',
        'upper_bathyal_coarse_recifal',
        'littoral_coarse_rhodolite',
        'circalittoral_coarse_rhodolite',
        'offshore_coarse_rhodolite',
        'upper_bathyal_coarse_rhodolite',
        'littoral_coarse_terrigeneous',
        'circalittoral_coarse_terrigeneous',
        'offshore_coarse_terrigeneous',
        'upper_bathyal_coarse_terrigeneous'
    ],

    'mixed': [
        'littoral_mixed_biogenic',
        'circalittoral_mixed_biogenic',
        'offshore_mixed_biogenic',
        'upper_bathyal_mixed_biogenic',
        'littoral_mixed_recifal',
        'circalittoral_mixed_recifal',
        'offshore_mixed_recifal',
        'upper_bathyal_mixed_recifal',
        'littoral_mixed_rhodolite',
        'circalittoral_mixed_rhodolite',
        'offshore_mixed_rhodolite',
        'upper_bathyal_mixed_rhodolite',
        'littoral_mixed_terrigeneous',
        'circalittoral_mixed_terrigeneous',
        'offshore_mixed_terrigeneous',
        'upper_bathyal_mixed_terrigeneous'
    ],

    'mud': [
        'littoral_mud_biogenic',
        'circalittoral_mud_biogenic',
        'offshore_mud_biogenic',
        'upper_bathyal_mud_biogenic',
        'littoral_mud_recifal',
        'circalittoral_mud_recifal',
        'offshore_mud_recifal',
        'upper_bathyal_mud_recifal',
        'littoral_mud_rhodolite',
        'circalittoral_mud_rhodolite',
        'offshore_mud_rhodolite',
        'upper_bathyal_mud_rhodolite',
        'littoral_mud_terrigeneous',
        'circalittoral_mud_terrigeneous',
        'offshore_mud_terrigeneous',
        'upper_bathyal_mud_terrigeneous'
    ],

    'sand': [
        'littoral_sand_biogenic',
        'circalittoral_sand_biogenic',
        'offshore_sand_biogenic',
        'upper_bathyal_sand_biogenic',
        'littoral_sand_recifal',
        'circalittoral_sand_recifal',
        'offshore_sand_recifal',
        'upper_bathyal_sand_recifal',
        'littoral_sand_rhodolite',
        'circalittoral_sand_rhodolite',
        'offshore_sand_rhodolite',
        'upper_bathyal_sand_rhodolite',
        'littoral_sand_terrigeneous',
        'circalittoral_sand_terrigeneous',
        'offshore_sand_terrigeneous',
        'upper_bathyal_sand_terrigeneous'
    ],

    'hardrock': [
        'littoral_hardrock_biogenic',
        'circalittoral_hardrock_biogenic',
        'offshore_hardrock_biogenic',
        'upper_bathyal_hardrock_biogenic',
        'littoral_hardrock_recifal',
        'circalittoral_hardrock_recifal',
        'offshore_hardrock_recifal',
        'upper_bathyal_hardrock_recifal',
        'littoral_hardrock_rhodolite',
        'circalittoral_hardrock_rhodolite',
        'offshore_hardrock_rhodolite',
        'upper_bathyal_hardrock_rhodolite',
        'littoral_hardrock_terrigeneous',
        'circalittoral_hardrock_terrigeneous',
        'offshore_hardrock_terrigeneous',
        'upper_bathyal_hardrock_terrigenous',
        ]
    }
def raster_to_shapefiles(raster_path, output_folder_subcategorias, classes_dict, categories_dict):
    
    """
    Converte um raster .tif em shapefiles tanto para as subclasses (ex: Coarse Biogenic) quanto para as categorias gerais (ex: Coarse).
    
    :param raster_path: Caminho do arquivo raster (.tif)
    :param output_folder_subcategorias: Pasta onde os shapefiles serão salvos
    :param classes_dict: Dicionário que mapeia valores do raster para classes específicas
    :param categories_dict: Dicionário que mapeia classes para suas categorias gerais (ex: Mixed, Mud, etc.)
    """
    # Criar pasta de saída se não existir
    os.makedirs(output_folder_subcategorias, exist_ok=True)

    # Abrir o raster
    with rasterio.open(raster_path) as src:
        image = src.read(1)  # Ler a primeira banda
        transform = src.transform  # Obter a transformação espacial
        crs = src.crs  # Obter o sistema de coordenadas
        if crs is None:
            # Definir manualmente, por exemplo, para WGS84
            from rasterio.crs import CRS
            crs="EPSG:4326"
            print("Aviso: CRS não encontrado no raster. Definido CRS como EPSG:4326.")
        print(crs)

    # Criar dicionários para armazenar polígonos
    polygons_by_class = {value: [] for value in classes_dict.values()}  # Para subclasses
    polygons_by_category = {category: [] for category in categories_dict.keys()}  # Para categorias gerais

    # Gerar polígonos a partir do raster
    for geom, value in shapes(image, transform=transform):
        if value in classes_dict:  # Verifica se o valor do pixel está no dicionário de classes
            # Recupera o nome da classe
            class_name = classes_dict[value]
            # Adiciona ao dicionário de subclasses
            polygons_by_class[class_name].append(shape(geom))

            # Para categorias gerais, verifica qual categoria corresponde à classe
            for category, classes in categories_dict.items():
                if class_name in classes:
                    polygons_by_category[category].append(shape(geom))
                    break

    # Criar e salvar shapefiles para as subclasses
    for class_name, polygons in polygons_by_class.items():
        if polygons:  # Verifica se há polígonos para essa classe
            shapefile_path = os.path.join(output_folder_subcategorias, f"{class_name.replace(' ', '_')}.shp")
            
            # Criar GeoDataFrame para a classe específica
            gdf = gpd.GeoDataFrame({'class': [class_name] * len(polygons), 'geometry': polygons}, crs=crs)
            
            # Salvar shapefile para a classe
            gdf.to_file(shapefile_path)
            print(f"Shapefile de classe salvo: {shapefile_path}")

    # # Criar e salvar shapefiles para as categorias gerais
    # for category, polygons in polygons_by_category.items():
    #     if polygons:  # Verifica se há polígonos para essa categoria
    #         shapefile_path = os.path.join(output_folder_categorias, f"{category}.shp")
            
    #         # Criar GeoDataFrame para a categoria geral
    #         gdf = gpd.GeoDataFrame({'category': [category] * len(polygons), 'geometry': polygons}, crs=crs)
            
    #         # Salvar shapefile para a categoria
    #         gdf.to_file(shapefile_path)
    #         print(f"Shapefile de categoria salvo: {shapefile_path}")
def raster_to_individual_shapefiles(raster_path, class_map):
    output_folder=output_folder_subcategorias
    import os
    import rasterio
    import geopandas as gpd
    from rasterio.features import shapes
    from shapely.geometry import shape

    os.makedirs(output_folder, exist_ok=True)

    with rasterio.open(raster_path) as src:
        image = src.read(1)
        transform = src.transform
        crs = src.crs
        if crs is None:
            crs = "EPSG:4326"
            print(f"CRS não encontrado em {raster_path}, usando EPSG:4326")

    # Separar os polígonos por classe
    polygons_by_class = {v: [] for k, v in class_map.items() if k != 0}

    for geom, value in shapes(image, transform=transform):
        if value in class_map and value != 0:
            class_name = class_map[value]
            polygons_by_class[class_name].append(shape(geom))

    # Salvar cada shapefile
    for class_name, polygons in polygons_by_class.items():
        if polygons:
            gdf = gpd.GeoDataFrame({'class': [class_name] * len(polygons), 'geometry': polygons}, crs=crs)
            filename = f"{class_name}.shp"
            output_path = os.path.join(output_folder, filename)
            gdf.to_file(output_path)
            print(f"Shapefile salvo: {output_path}")
def gerar_shp_individuais():            
    base_dir = r"C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25"
    raster_dir = os.path.join(base_dir, "arrays padronizados")
    
    raster_to_individual_shapefiles(
        raster_path=os.path.join(raster_dir, "HIDRODINAMIC.tif"),
        class_map=hidro_map
    )
    
    raster_to_individual_shapefiles(
        raster_path=os.path.join(raster_dir, "SEABED.tif"),
        class_map=seabed_map
    )
    
    raster_to_individual_shapefiles(
        raster_path=os.path.join(raster_dir, "BIOTIPOS.tif"),
        class_map=biotipo_map
    )


# raster_to_shapefiles(raster_path, output_folder_subcategorias, classes_dict, categories_dict)
# gerar_shp_individuais()            
