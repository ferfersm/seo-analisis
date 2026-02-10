"""
Analizador de páginas (URLs).
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from urllib.parse import urlparse

from .base import BaseAnalyzer
from .metrics import calcular_variacion, calcular_share


class PageAnalyzer(BaseAnalyzer):
    """
    Analizador especializado en páginas (URLs).
    """
    
    def __init__(self, df: pd.DataFrame, config):
        """Inicializa analizador de páginas."""
        super().__init__(df, config, 'page')
    
    def extraer_subdominio(self, url: str) -> Optional[str]:
        """
        Extrae el subdominio de una URL.
        
        Args:
            url: URL completa
            
        Returns:
            Subdominio o None
        """
        try:
            parsed = urlparse(url)
            return parsed.hostname
        except:
            return None
    
    def extraer_ruta(self, url: str) -> str:
        """
        Extrae la ruta de una URL.
        
        Args:
            url: URL completa
            
        Returns:
            Ruta de la URL
        """
        try:
            parsed = urlparse(url)
            return parsed.path
        except:
            return ''
    
    def generar_subconjuntos(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Genera subconjuntos de datos según subdominios.
        
        Args:
            df: DataFrame a segmentar
            
        Returns:
            Diccionario de dataframes por subdominio
        """
        subsets = {'totales': df}
        
        # Extraer subdominios
        df = df.copy()
        df['subdominio'] = df['page'].apply(self.extraer_subdominio)
        
        # Agrupar por subdominio
        for subdominio in df['subdominio'].dropna().unique():
            if subdominio:
                subsets[f'subdominio_{subdominio}'] = df[
                    df['subdominio'] == subdominio
                ].copy()
        
        return subsets
    
    def resumir_dataframes(self, dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Resume métricas de múltiples dataframes.
        
        Args:
            dfs: Diccionario {nombre: dataframe}
            
        Returns:
            DataFrame con resumen
        """
        total_clicks = sum(
            d[self.config.columna_metricas['clicks']].sum() 
            for d in dfs.values()
        )
        
        rows = []
        for nombre, df in dfs.items():
            metricas = self.calcular_metricas(df)
            share = calcular_share(metricas['clicks'], total_clicks)
            
            rows.append({
                'categoria': nombre,
                'clics': metricas['clicks'],
                'impresiones': metricas['impressions'],
                'ctr': metricas['ctr'],
                'posicion': metricas['position'],
                'share_pct': share
            })
        
        return pd.DataFrame(rows)
    
    def analizar_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str]
    ) -> pd.DataFrame:
        """
        Analiza variación entre dos períodos.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            
        Returns:
            DataFrame con comparación
        """
        df_p1 = self.filtrar_por_fecha(*periodo_1)
        df_p2 = self.filtrar_por_fecha(*periodo_2)
        
        subsets_p1 = self.generar_subconjuntos(df_p1)
        subsets_p2 = self.generar_subconjuntos(df_p2)
        
        resumen_p1 = self.resumir_dataframes(subsets_p1)
        resumen_p2 = self.resumir_dataframes(subsets_p2)
        
        resultado = resumen_p1.merge(
            resumen_p2,
            on='categoria',
            suffixes=('_ini', '_fin')
        )
        
        for metrica in ['clics', 'impresiones']:
            col_ini = f'{metrica}_ini'
            col_fin = f'{metrica}_fin'
            
            resultado[f'var_{metrica}'] = resultado[col_fin] - resultado[col_ini]
            resultado[f'var_{metrica}_pct'] = np.where(
                resultado[col_ini] != 0,
                ((resultado[col_fin] - resultado[col_ini]) / resultado[col_ini]) * 100,
                np.nan
            ).round(2)
        
        return resultado
    
    def top_n_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        metrica: str = 'clicks',
        n: int = 10,
        subdominio: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Obtiene top N URLs con mayor variación.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            metrica: Métrica a analizar
            n: Cantidad de resultados
            subdominio: Filtrar por subdominio
            
        Returns:
            DataFrame con URLs de mayor variación
        """
        df_p1 = self.filtrar_por_fecha(*periodo_1)
        df_p2 = self.filtrar_por_fecha(*periodo_2)
        
        if subdominio:
            import re
            patron = re.escape(subdominio) if isinstance(subdominio, str) else '|'.join(map(re.escape, subdominio))
            df_p1 = df_p1[df_p1['page'].str.contains(patron, na=False)]
            df_p2 = df_p2[df_p2['page'].str.contains(patron, na=False)]
        
        col_metrica = self.config.columna_metricas.get(metrica, metrica)
        
        # Agregar por página
        agg_p1 = df_p1.groupby('page').agg({
            col_metrica: 'sum'
        }).reset_index()
        
        agg_p2 = df_p2.groupby('page').agg({
            col_metrica: 'sum'
        }).reset_index()
        
        merged = agg_p1.merge(
            agg_p2,
            on='page',
            how='outer',
            suffixes=('_ini', '_fin')
        ).fillna(0)
        
        merged['variacion'] = merged[f'{metrica}_fin'] - merged[f'{metrica}_ini']
        merged['variacion_abs'] = merged['variacion'].abs()
        
        top_n = merged.nlargest(n, 'variacion_abs').copy()
        top_n['subdominio'] = top_n['page'].apply(self.extraer_subdominio)
        
        return top_n[['page', 'subdominio', f'{metrica}_ini', f'{metrica}_fin', 'variacion', 'variacion_abs']]
    
    def distribucion_por_subdominio(
        self,
        df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Calcula distribución de tráfico por subdominio.
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            DataFrame con distribución
        """
        if df is None:
            df = self.df
        
        df = df.copy()
        df['subdominio'] = df['page'].apply(self.extraer_subdominio)
        df = df.dropna(subset=['subdominio'])
        
        resumen = df.groupby('subdominio').agg({
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index().sort_values('clicks', ascending=False)
        
        total_clicks = resumen['clicks'].sum()
        resumen['share_clicks_pct'] = resumen['clicks'].apply(
            lambda x: calcular_share(x, total_clicks)
        )
        
        return resumen
    
    def analizar_subdominios(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        patrones: List[str]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Analiza métricas por subdominios específicos.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            patrones: Lista de patrones de subdominio a buscar
            
        Returns:
            Tupla de DataFrames (período_1, período_2)
        """
        df_p1 = self.filtrar_por_fecha(*periodo_1)
        df_p2 = self.filtrar_por_fecha(*periodo_2)
        
        rows_p1 = []
        rows_p2 = []
        
        import re
        for patron in patrones:
            regex = re.escape(patron)
            
            # Período 1
            df_sub_p1 = df_p1[df_p1['page'].str.contains(regex, na=False)]
            if not df_sub_p1.empty:
                metricas = self.calcular_metricas(df_sub_p1)
                rows_p1.append({
                    'subdominio': patron,
                    'clics': metricas['clicks'],
                    'impresiones': metricas['impressions']
                })
            
            # Período 2
            df_sub_p2 = df_p2[df_p2['page'].str.contains(regex, na=False)]
            if not df_sub_p2.empty:
                metricas = self.calcular_metricas(df_sub_p2)
                rows_p2.append({
                    'subdominio': patron,
                    'clics': metricas['clicks'],
                    'impresiones': metricas['impressions']
                })
        
        return pd.DataFrame(rows_p1), pd.DataFrame(rows_p2)
