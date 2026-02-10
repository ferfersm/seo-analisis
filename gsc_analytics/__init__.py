"""
GSC Analytics Module v2.0
==========================
Módulo para análisis de datos de Google Search Console.
Soporta análisis de queries y URLs con configuración flexible.

Uso básico en Google Colab:
    !pip install git+https://github.com/TU_USUARIO/gsc-analytics.git
    
    from gsc_analytics import GSCAnalyzer, ConfigGSC
    
    config = ConfigGSC(
        cliente='transbank',
        marcas={
            'tbk': ['transbank', 'tbk', ...],
            'webpay': ['webpay', 'web pay', ...],
        },
        keywords_importantes=['...'],
        dimensiones=['query', 'page']
    )
    
    analyzer = GSCAnalyzer(df, config)
    resultados = analyzer.generar_reporte_completo(
        ('2026-01-17', '2026-01-23'),
        ('2026-01-24', '2026-01-30')
    )
"""

__version__ = '2.0.0'
__author__ = 'Fernando Sanhueza'

from .analyzer import GSCAnalyzer
from .config import ConfigGSC, CONFIG_EJEMPLO_TRANSBANK
from .extractors.gsc_api import obtener_datos_mes, procesar_rango_meses
from .utils.helpers import cargar_csvs, filtra_df, resumen_kw, concatena_dataframes

__all__ = [
    'GSCAnalyzer',
    'ConfigGSC',
    'CONFIG_EJEMPLO_TRANSBANK',
    'obtener_datos_mes',
    'procesar_rango_meses',
    'cargar_csvs',
    'filtra_df',
    'resumen_kw',
    'concatena_dataframes'
]
