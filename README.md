# GSC Analytics

Módulo avanzado para análisis de datos de Google Search Console (GSC).

## Características

- **Análisis de Queries y URLs**: Soporta análisis de palabras clave y páginas
- **Comparación de Períodos**: Compara cualquier par de períodos (no necesitan ser iguales)
- **Variaciones Automáticas**: Calcula variaciones absolutas y porcentuales
- **Configuración Flexible**: Define marcas, grupos y métricas por cliente
- **Exportación Simple**: Exporta resultados a CSV
- **Integración GSC API**: Incluye funciones para extracción de datos

## Instalación

```bash
pip install git+https://github.com/TU_USUARIO/gsc-analytics.git
```

## Uso Rápido

```python
import pandas as pd
from gsc_analytics import GSCAnalyzer, ConfigGSC

# Cargar datos
df = pd.read_csv('datos_gsc.csv', parse_dates=['date'])

# Configurar
config = ConfigGSC(
    cliente='mi_cliente',
    marcas={
        'marca1': ['keyword1', 'keyword2'],
        'marca2': ['keyword3', 'keyword4'],
    },
    keywords_importantes=['importante1', 'importante2'],
    dimensiones=['query', 'page']
)

# Analizar
analyzer = GSCAnalyzer(df, config)
reporte = analyzer.generar_reporte_completo(
    ('2025-01-01', '2025-01-31'),
    ('2025-02-01', '2025-02-28')
)

# Usar resultados
print(reporte['resumen_general'])
print(reporte['top_queries_clics'])
```

## Estructura del Reporte

El método `generar_reporte_completo()` retorna un diccionario con:

- `resumen_general`: Resumen comparativo por período
- `comparacion_marcas_clics`: Comparación por grupos (clics)
- `comparacion_marcas_impresiones`: Comparación por grupos (impresiones)
- `comparacion_kws_importantes`: Comparación de keywords importantes
- `top_queries_clics`: Top queries con mayor variación en clics
- `top_queries_impresiones`: Top queries con mayor variación en impresiones
- `top_urls_clics`: Top URLs con mayor variación en clics
- `top_urls_impresiones`: Top URLs con mayor variación en impresiones
- `subdominios`: Análisis por subdominios
- `distribucion_categorias`: Distribución por categoría de keyword
- `distribucion_subdominios`: Distribución por subdominio

## Licencia

MIT
