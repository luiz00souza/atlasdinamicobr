import sys
modulo_diretorio = r'C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25\88_rotinas_python'
proc_dir=r'C:\Users\campo\Desktop\mestrado\Raster Reclassificados_clean_08_25'
sys.path.append(modulo_diretorio)
from GERADORDEMODELO import *
from COMPILADORDEMODELO import *
from VALIDADORDOMODELO import *
from separartiffemshp import *
#GERADOR DO MODELO
largura_pixel_deg, altura_pixel_deg = metros_para_graus(resolucao_metros, latitude_media)
def chama_modelo():
    try:
    #GERADOR DO MODELO
        processamento = ProcessamentoDados(proc_dir)
        print("Processamento Iniciado")
        processamento.interpolate_and_save_tiff(file_path, column_names)
        print("-"*20)
        processamento.reclass_batimetria()
        print("-"*20)
        processamento.reclassify_all_rasters()
        print("-"*20)
        processamento.recortar_e_salvar_rasters()
        print("-"*20)
        somar_rasters_com_pesos(dir_path, diretorio, seabed_rasters_names, nome='SEABED')
        somar_rasters_com_pesos(dir_path, diretorio, biogenic_rasters_names, nome ='BIOTIPOS')
        print("-"*20)
        preencher_zeros_por_valor_mais_proximo([raster_seabed, raster_biotipos], shapefile_plataforma)
        #COMPILADOR DO MODELO
        recortar_e_reamostrar_hidrodinamic(
            diretorio,
            arquivo_tif2,  # seabed
            batimetria,  # hidrodinamic
            arquivo_tif1,  # arquivo saída reamostrado
            f'{batimetria}_recortado.tif',    # arquivo saída recortado
            shapefile_plataforma
        )
        combinar_rasters(diretorio, arquivo_tif1, arquivo_tif2, arquivo_tif3, novo_raster_nome)
        print("-"*20)
        raster_to_shapefiles(raster_path, output_folder_subcategorias, classes_dict, categories_dict)
        gerar_shp_individuais()
        #VALIDADOR DO MODELO
        # resultados = processar_dados(CAMINHO_RASTER)
    except Exception as e: 
        print(f"Erro durante o processamento: {e}")
    # df_resultados=resultados['df_resultados']
    # lat=df_resultados[['Latitude','Longitude','Valor_Amostrado','ID_CLASSIFICACAO_FINAL']]
# chama_modelo()