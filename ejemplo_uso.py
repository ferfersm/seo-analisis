"""
Ejemplo de uso del módulo GSC Analytics.
Este archivo replica el flujo de trabajo de Transbank.
"""

# ==============================================================================
# 1. INSTALACIÓN EN GOOGLE COLAB
# ==============================================================================
"""
!pip install git+https://github.com/TU_USUARIO/gsc-analytics.git
!pip install git+https://github.com/joshcarty/google-searchconsole
"""

# ==============================================================================
# 2. IMPORTS
# ==============================================================================
import pandas as pd
import searchconsole
from gsc_analytics import (
    GSCAnalyzer,
    ConfigGSC,
    CONFIG_EJEMPLO_TRANSBANK,
    cargar_csvs,
    obtener_datos_mes,
    procesar_rango_meses
)

# ==============================================================================
# 3. CONFIGURACIÓN DEL CLIENTE
# ==============================================================================
# Usar configuración predefinida o crear una nueva
config = CONFIG_EJEMPLO_TRANSBANK

# O crear configuración personalizada:
config_personalizada = ConfigGSC(
    cliente='santa-maria',
    marcas={
        'principal': ['santa maria', 'santamaria'],
        'productos': ['vino', 'vinos', 'uvas'],
    },
    keywords_importantes=['comprar', 'precio', 'tienda'],
    dimensiones=['query', 'page']
)

# ==============================================================================
# 4. CARGA DE DATOS (Opción A: Desde CSVs)
# ==============================================================================
df = cargar_csvs(
    ruta_carpeta='/content/drive/Shareddrives/Clientes/Transbank/SEO/Data-historica-GSC',
    col_fecha='date'
)

# ==============================================================================
# 4. CARGA DE DATOS (Opción B: Desde API GSC)
# ==============================================================================
"""
# Autenticación
account = searchconsole.authenticate(
    flow="console",
    client_config='client_secrets.json',
    credentials='credentials.json'
)
propiedad = account['sc-domain:transbank.cl']

# Extraer datos de un mes
df_mes = obtener_datos_mes(propiedad, year=2026, mes=1)

# Extraer rango de meses
procesar_rango_meses(
    propiedad,
    nombre_propiedad='transbank',
    year=2025,
    mes_inicio=1,
    mes_fin=12,
    folder_destino='/content/drive/Shareddrives/Clientes/Transbank/SEO/Data-historica-GSC'
)
"""

# ==============================================================================
# 5. INICIALIZAR ANALIZADOR
# ==============================================================================
analyzer = GSCAnalyzer(df, config)

# ==============================================================================
# 6. GENERAR REPORTE COMPLETO (Equivalente a todo tu código anterior)
# ==============================================================================
reporte = analyzer.generar_reporte_completo(
    periodo_1=('2026-01-17', '2026-01-23'),  # Semana inicial
    periodo_2=('2026-01-24', '2026-01-30'),  # Semana final
    subdominios=[
        'tienda.transbank.cl',
        'publico.transbank.cl',
        'ayuda.transbank.cl',
        'privado.transbank.cl'
    ],
    top_n=15
)

# ==============================================================================
# 7. ACCEDER A RESULTADOS
# ==============================================================================

# Sección 1: Resumen General por período
print("=" * 60)
print("SECCIÓN 1: RESUMEN GENERAL")
print("=" * 60)
print("\nResumen por período:")
print(reporte['resumen_general'])

# Sección 2: Comparación por Marcas
print("\n" + "=" * 60)
print("SECCIÓN 2: COMPARACIÓN POR MARCAS")
print("=" * 60)
print("\nComparación por clics:")
print(reporte['comparacion_marcas_clics'])
print("\nComparación por impresiones:")
print(reporte['comparacion_marcas_impresiones'])

# Keywords importantes
print("\n" + "=" * 60)
print("COMPARACIÓN KWs IMPORTANTES")
print("=" * 60)
print(reporte['comparacion_kws_importantes'])

# Top 15 variaciones
print("\n" + "=" * 60)
print("TOP 15 VARIACIONES")
print("=" * 60)
print("\nTop queries variación clics:")
print(reporte['top_queries_clics'])
print("\nTop queries variación impresiones:")
print(reporte['top_queries_impresiones'])
print("\nTop URLs variación clics:")
print(reporte['top_urls_clics'])
print("\nTop URLs variación impresiones:")
print(reporte['top_urls_impresiones'])

# Subdominios
print("\n" + "=" * 60)
print("ANÁLISIS DE SUBDOMINIOS")
print("=" * 60)
print(reporte['subdominios'])

# Distribuciones
print("\n" + "=" * 60)
print("DISTRIBUCIONES")
print("=" * 60)
print("\nDistribución por categoría de keyword:")
print(reporte['distribucion_categorias'])
print("\nDistribución por subdominio:")
print(reporte['distribucion_subdominios'])

# ==============================================================================
# 8. EXPORTAR A CSV
# ==============================================================================
analyzer.exportar_reporte(
    reporte,
    ruta_destino='/content/drive/Shareddrives/Clientes/Transbank/SEO/Reportes',
    prefijo='2026-01-s4-'
)

# ==============================================================================
# 9. USO INDIVIDUAL DE MÉTODOS
# ==============================================================================

# Comparar períodos específicos
comparacion = analyzer.comparar_periodos(
    ('2026-01-01', '2026-01-15'),
    ('2026-01-16', '2026-01-31'),
    dimension='query'
)

# Obtener top N específico
top_queries = analyzer.top_n_variacion(
    ('2026-01-17', '2026-01-23'),
    ('2026-01-24', '2026-01-30'),
    dimension='query',
    metrica='clicks',
    n=1000,
    subdominio='publico.transbank.cl'
)

# Exportar solo top 1000
top_queries.to_csv('top-1000-queries.csv', index=False)

print("\n✅ Análisis completado exitosamente!")
