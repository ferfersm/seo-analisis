"""
Funciones de extracción de datos desde GSC API.
"""
from typing import Optional
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import os
import shutil


def obtener_datos_mes(
    propiedad,
    year: int,
    mes: int,
    search_type: str = 'web'
) -> pd.DataFrame:
    """
    Obtiene datos de GSC para un mes específico.
    
    Args:
        propiedad: Objeto de propiedad de Search Console
        year: Año
        mes: Mes (1-12)
        search_type: Tipo de búsqueda ('web', 'news', 'video', 'image', 'discover')
        
    Returns:
        DataFrame con datos del mes
    """
    ultimo_dia = calendar.monthrange(year, mes)[1]
    
    inicio = f"{year}-{mes:02d}-01"
    fin = f"{year}-{mes:02d}-{ultimo_dia}"
    
    query = propiedad.query
    
    if search_type != 'web':
        query = query.search_type(search_type)
    
    report = query.range(inicio, fin).dimension(['query', 'page', 'date', 'device', 'country']).get()
    
    return report.to_dataframe()


def procesar_rango_meses(
    propiedad,
    nombre_propiedad: str,
    year: int,
    mes_inicio: int,
    mes_fin: int,
    folder_destino: str
) -> None:
    """
    Procesa un rango de meses y guarda en CSV.
    
    Args:
        propiedad: Objeto de propiedad de Search Console
        nombre_propiedad: Nombre corto para identificar archivos
        year: Año
        mes_inicio: Mes inicial
        mes_fin: Mes final
        folder_destino: Carpeta destino
    """
    os.makedirs(folder_destino, exist_ok=True)
    
    # Fecha límite (16 meses atrás)
    fecha_limite = datetime.now() - relativedelta(months=16)
    
    for mes in range(mes_inicio, mes_fin + 1):
        fecha_del_mes = datetime(year, mes, 1)
        
        if fecha_del_mes < fecha_limite:
            print(f"--- OMITIENDO mes {mes}/{year} por estar fuera del rango de 16 meses. ---\n")
            continue
        
        print(f"--- Procesando mes {mes}/{year} para '{nombre_propiedad}' ---")
        
        try:
            df_mensual = obtener_datos_mes(propiedad, year, mes)
            
            if df_mensual.empty:
                print(f"No se generó CSV para {mes}/{year} porque no se encontraron datos.\n")
                continue
            
            nombre_csv = f"{year}-{mes:02d}-{nombre_propiedad}.csv"
            ruta_origen = f"/content/{nombre_csv}"
            
            df_mensual.to_csv(ruta_origen, index=False)
            print(f"Archivo '{nombre_csv}' creado exitosamente.")
            
            try:
                shutil.move(ruta_origen, folder_destino)
                print(f"Archivo movido a '{folder_destino}'.\n")
            except Exception as e:
                print(f"Error al mover archivo: {e}\n")
                
        except Exception as e:
            print(f"Error al procesar mes {mes}: {e}\n")
