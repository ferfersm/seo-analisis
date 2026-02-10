"""
Fachada principal GSCAnalyzer.
Proporciona interfaz unificada para análisis de GSC.
"""
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

from .config import ConfigGSC
from .core.query_analyzer import QueryAnalyzer
from .core.page_analyzer import PageAnalyzer
from .core.metrics import calcular_variacion, calcular_share


class GSCAnalyzer:
    """
    Fachada principal para análisis de datos GSC.
    
    Unifica el análisis de queries y páginas en una interfaz simple.
    
    Example:
        >>> config = ConfigGSC(cliente='transbank', marcas={...})
        >>> analyzer = GSCAnalyzer(df, config)
        >>> reporte = analyzer.generar_reporte_completo(
        ...     ('2026-01-17', '2026-01-23'),
        ...     ('2026-01-24', '2026-01-30')
        ... )
    """
    
    def __init__(self, df: pd.DataFrame, config: ConfigGSC):
        """
        Inicializa el analizador.
        
        Args:
            df: DataFrame con datos GSC
            config: Configuración del cliente
        """
        self.config = config
        self.df = df.copy()
        
        # Inicializar analizadores según dimensiones configuradas
        self._query_analyzer = None
        self._page_analyzer = None
        
        if 'query' in config.dimensiones:
            self._query_analyzer = QueryAnalyzer(df, config)
        
        if 'page' in config.dimensiones:
            self._page_analyzer = PageAnalyzer(df, config)
    
    def generar_reporte_completo(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        subdominios: Optional[List[str]] = None,
        top_n: int = 15
    ) -> Dict[str, pd.DataFrame]:
        """
        Genera reporte completo con todas las métricas.
        
        Replica la funcionalidad completa del código original de Transbank.
        
        Args:
            periodo_1: (inicio, fin) período base
            periodo_2: (inicio, fin) período comparación
            subdominios: Lista de subdominios a analizar
            top_n: Cantidad de queries/URLs top a retornar
            
        Returns:
            Diccionario con DataFrames:
                - resumen_general: Resumen por período (Sección 1)
                - comparacion_marcas: Comparación por grupos de marca (Sección 2)
                - comparacion_kws_importantes: Comparación solo KWs importantes
                - top_queries_clics: Top N queries variación clics
                - top_queries_impresiones: Top N queries variación impresiones
                - top_urls_clics: Top N URLs variación clics (si page en dimensiones)
                - top_urls_impresiones: Top N URLs variación impresiones
                - subdominios: Análisis de subdominios
                - distribucion_categorias: Distribución por categoría
                - distribucion_subdominios: Distribución por subdominio
        """
        resultados = {}
        
        # 1. Resumen General (Sección 1)
        if self._query_analyzer:
            resultados['resumen_general'] = self._query_analyzer.analizar_variacion(
                periodo_1, periodo_2
            )
        
        # 2. Comparación por marcas (Sección 2)
        if self._query_analyzer:
            df_p1 = self._query_analyzer.filtrar_por_fecha(*periodo_1)
            df_p2 = self._query_analyzer.filtrar_por_fecha(*periodo_2)
            
            grupos = list(self.config.marcas.values())
            nombres = list(self.config.marcas.keys())
            
            resultados['comparacion_marcas_clics'] = self._query_analyzer.comparar_por_grupos(
                df_p2, df_p1, grupos, nombres, metrica='clicks'
            )
            resultados['comparacion_marcas_impresiones'] = self._query_analyzer.comparar_por_grupos(
                df_p2, df_p1, grupos, nombres, metrica='impressions'
            )
        
        # 3. Comparación KWs importantes
        if self._query_analyzer and self.config.keywords_importantes:
            df_kwi_p1 = df_p1[df_p1['kw_importante']]
            df_kwi_p2 = df_p2[df_p2['kw_importante']]
            
            resultados['comparacion_kws_importantes'] = self._query_analyzer.comparar_por_grupos(
                df_kwi_p2, df_kwi_p1, grupos, nombres, metrica='clicks'
            )
        
        # 4. Top N variaciones
        if self._query_analyzer:
            resultados['top_queries_clics'] = self._query_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica='clicks', n=top_n,
                subdominio=subdominios
            )
            resultados['top_queries_impresiones'] = self._query_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica='impressions', n=top_n,
                subdominio=subdominios
            )
        
        if self._page_analyzer:
            resultados['top_urls_clics'] = self._page_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica='clicks', n=top_n,
                subdominio=subdominios
            )
            resultados['top_urls_impresiones'] = self._page_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica='impressions', n=top_n,
                subdominio=subdominios
            )
        
        # 5. Análisis de subdominios
        if subdominios and self._page_analyzer:
            sub_p1, sub_p2 = self._page_analyzer.analizar_subdominios(
                periodo_1, periodo_2, subdominios
            )
            
            # Merge para comparación
            merged = sub_p1.merge(
                sub_p2, on='subdominio', how='outer', suffixes=('_ini', '_fin')
            ).fillna(0)
            
            # Calcular variaciones
            for metrica in ['clics', 'impresiones']:
                merged[f'var_{metrica}'] = merged[f'{metrica}_fin'] - merged[f'{metrica}_ini']
                merged[f'var_{metrica}_pct'] = (
                    (merged[f'var_{metrica}'] / merged[f'{metrica}_ini']) * 100
                ).round(2)
            
            resultados['subdominios'] = merged
        
        # 6. Distribuciones
        if self._query_analyzer:
            resultados['distribucion_categorias'] = self._query_analyzer.distribucion_por_categoria()
        
        if self._page_analyzer:
            resultados['distribucion_subdominios'] = self._page_analyzer.distribucion_por_subdominio()
            
            # Distribución por período
            df_p1_page = self._page_analyzer.filtrar_por_fecha(*periodo_1)
            df_p2_page = self._page_analyzer.filtrar_por_fecha(*periodo_2)
            
            resultados['distribucion_subdominios_p1'] = (
                self._page_analyzer.distribucion_por_subdominio(df_p1_page)
            )
            resultados['distribucion_subdominios_p2'] = (
                self._page_analyzer.distribucion_por_subdominio(df_p2_page)
            )
        
        return resultados
    
    def comparar_periodos(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        dimension: str = 'query'
    ) -> pd.DataFrame:
        """
        Compara métricas entre dos períodos.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            dimension: 'query' o 'page'
            
        Returns:
            DataFrame con comparación
        """
        if dimension == 'query' and self._query_analyzer:
            return self._query_analyzer.analizar_variacion(periodo_1, periodo_2)
        elif dimension == 'page' and self._page_analyzer:
            return self._page_analyzer.analizar_variacion(periodo_1, periodo_2)
        else:
            raise ValueError(f"Dimensión '{dimension}' no disponible")
    
    def top_n_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        dimension: str = 'query',
        metrica: str = 'clicks',
        n: int = 10,
        subdominio: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Obtiene top N con mayor variación.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            dimension: 'query' o 'page'
            metrica: 'clicks' o 'impressions'
            n: Cantidad de resultados
            subdominio: Filtrar por subdominio
            
        Returns:
            DataFrame con top variaciones
        """
        if dimension == 'query' and self._query_analyzer:
            return self._query_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica, n, subdominio
            )
        elif dimension == 'page' and self._page_analyzer:
            return self._page_analyzer.top_n_variacion(
                periodo_1, periodo_2, metrica, n, subdominio
            )
        else:
            raise ValueError(f"Dimensión '{dimension}' no disponible")
    
    def exportar_reporte(
        self,
        resultados: Dict[str, pd.DataFrame],
        ruta_destino: str,
        prefijo: str = ''
    ) -> None:
        """
        Exporta todos los DataFrames del reporte a CSV.
        
        Args:
            resultados: Diccionario de DataFrames
            ruta_destino: Carpeta destino
            prefijo: Prefijo para nombres de archivo
        """
        import os
        os.makedirs(ruta_destino, exist_ok=True)
        
        for nombre, df in resultados.items():
            nombre_archivo = f"{prefijo}{nombre}.csv" if prefijo else f"{nombre}.csv"
            ruta = os.path.join(ruta_destino, nombre_archivo)
            df.to_csv(ruta, index=False)
            print(f"Exportado: {ruta}")
