# 📊 GSC Analytics v2.0 - Documentación

## 🎯 Resumen

Módulo refactoreado para análisis de datos de Google Search Console con:
- ✅ Soporte para queries y URLs
- ✅ Variaciones numéricas y porcentuales automáticas
- ✅ Arquitectura SOLID y Clean Code
- ✅ Fácil instalación desde GitHub en Colab

## 📁 Estructura del Proyecto

```
gsc_analytics/
├── __init__.py              # Exports principales
├── analyzer.py              # Fachada GSCAnalyzer (API principal)
├── config.py                # ConfigGSC y ejemplos
├── contracts.py             # Interfaces (IAnalyzer, IDimensionAnalyzer)
├── types.py                 # Tipos y dataclasses
├── core/
│   ├── base.py             # BaseAnalyzer (clase abstracta)
│   ├── metrics.py          # Cálculo de métricas y variaciones
│   ├── query_analyzer.py   # Análisis de palabras clave
│   └── page_analyzer.py    # Análisis de URLs
├── extractors/
│   └── gsc_api.py          # Funciones de extracción GSC
└── utils/
    └── helpers.py          # Funciones auxiliares
```

## 🚀 Instalación en Google Colab

```python
# 1. Instalar desde GitHub (una vez que subas el repo)
!pip install git+https://github.com/TU_USUARIO/gsc-analytics.git

# 2. Importar
from gsc_analytics import GSCAnalyzer, ConfigGSC
```

## 💻 Uso Rápido

```python
import pandas as pd
from gsc_analytics import GSCAnalyzer, ConfigGSC

# 1. Cargar datos
df = pd.read_csv('datos_gsc.csv', parse_dates=['date'])

# 2. Configurar
config = ConfigGSC(
    cliente='transbank',
    marcas={
        'tbk': ['transbank', 'tbk', ...],
        'webpay': ['webpay', 'web pay', ...],
        'onepay': ['onepay', 'one pay', ...],
        'redcompra': ['redcompra', ...],
        'conversion': [...]
    },
    keywords_importantes=[...],
    dimensiones=['query', 'page']  # Analizar ambas
)

# 3. Analizar
analyzer = GSCAnalyzer(df, config)
reporte = analyzer.generar_reporte_completo(
    periodo_1=('2026-01-17', '2026-01-23'),
    periodo_2=('2026-01-24', '2026-01-30'),
    subdominios=['tienda.transbank.cl', 'publico.transbank.cl', ...],
    top_n=15
)

# 4. Usar resultados (mismo formato que tu código actual)
reporte['resumen_general']
reporte['comparacion_marcas_clics']
reporte['top_queries_clics']
reporte['top_urls_clics']
reporte['subdominios']
```

## 📊 Resultados Disponibles

El método `generar_reporte_completo()` retorna un diccionario con:

| Clave | Descripción | Equivalente código original |
|-------|-------------|---------------------------|
| `resumen_general` | Resumen comparativo por período | Sección 1: `summary_inicio` + `summary_fin` |
| `comparacion_marcas_clics` | Comparación por grupos (clics) | Sección 2: `comparison_df_clics` |
| `comparacion_marcas_impresiones` | Comparación por grupos (impresiones) | Sección 2: `comparison_df_impressions` |
| `comparacion_kws_importantes` | Comparación solo KWs importantes | Sección 2: `comparison_df_kwi_clics` |
| `top_queries_clics` | Top N queries variación clics | `top_15_clicks` |
| `top_queries_impresiones` | Top N queries variación impresiones | `top_15_impressions` |
| `top_urls_clics` | Top N URLs variación clics | **NUEVO** |
| `top_urls_impresiones` | Top N URLs variación impresiones | **NUEVO** |
| `subdominios` | Análisis de subdominios | `merged_subdomains` |
| `distribucion_categorias` | Distribución por categoría keyword | `traffic_kw_summary` |
| `distribucion_subdominios` | Distribución por subdominio | `traffic_subdomain_summary_all` |
| `distribucion_subdominios_p1` | Distribución período 1 | `traffic_subdomain_summary_inicial` |
| `distribucion_subdominios_p2` | Distribución período 2 | `traffic_subdomain_summary_actual` |

## 📈 Variaciones Automáticas

Todas las comparaciones incluyen automáticamente:

- **Variación absoluta**: `valor_fin - valor_ini`
- **Variación porcentual**: `((valor_fin - valor_ini) / valor_ini) * 100`
- **Share inicial**: `(valor_ini / total_ini) * 100`
- **Share final**: `(valor_fin / total_fin) * 100`
- **Variación de share**: `share_fin - share_ini`

## 🔧 Configuración Predefinida para Transbank

```python
from gsc_analytics import CONFIG_EJEMPLO_TRANSBANK

# Ya incluye todas las marcas y keywords de tu código original
config = CONFIG_EJEMPLO_TRANSBANK
```

## 📦 Próximos Pasos

1. **Subir a GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit v2.0"
   git remote add origin https://github.com/TU_USUARIO/gsc-analytics.git
   git push -u origin main
   ```

2. **Instalar en Colab**:
   ```python
   !pip install git+https://github.com/TU_USUARIO/gsc-analytics.git
   ```

3. **Probar con tus datos**:
   - Ver archivo `ejemplo_uso.py` para flujo completo

## 🎨 Arquitectura SOLID

- **S**ingle Responsibility: Cada clase tiene una responsabilidad única
- **O**pen/Closed: Extensible sin modificar código existente
- **L**iskov Substitution: Los analizadores son intercambiables
- **I**nterface Segregation: Interfaces pequeñas y específicas
- **D**ependency Inversion: Depende de abstracciones, no implementaciones

## 🔮 Extensiones Futuras

Para agregar análisis predictivo (Data Science):

```python
# En el futuro podrás hacer:
from gsc_analytics.ml import TrendPredictor

predictor = TrendPredictor(analyzer)
prediccion = predictor.predecir_mes_siguiente('query')
```

## 📞 Soporte

Para dudas o mejoras, revisar:
- `ejemplo_uso.py` - Ejemplo completo
- `README.md` - Documentación básica
- Cada archivo tiene docstrings detallados
