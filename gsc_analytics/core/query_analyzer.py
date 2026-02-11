"""
Analizador de queries (palabras clave).
"""
from typing import Dict, List, Optional, Tuple
import re
import pandas as pd
import numpy as np

from .base import BaseAnalyzer
from .metrics import (
    calcular_metricas_base,
    calcular_variacion,
    calcular_share,
    agregar_por_dimension
)


class QueryAnalyzer(BaseAnalyzer):
    """
    Analizador especializado en queries (palabras clave).
    """
    
    def __init__(self, df: pd.DataFrame, config):
        """Inicializa analizador de queries."""
        super().__init__(df, config, 'query')
        self._aplicar_mapeo_marcas()
        self._identificar_kws_importantes()
    
    def _aplicar_mapeo_marcas(self):
        """Aplica mapeo de marcas a cada query (optimizado)."""
        brand_map = self.config.brand_map
        if brand_map:
            # Método optimizado: verificar cada query contra cada grupo
            # más rápido que un regex masivo con cientos de términos
            self.df['matched_brand'] = None
            
            for grupo, palabras in self.config.marcas.items():
                # Crear patrón solo para este grupo (más pequeño y rápido)
                patron = '|'.join(map(re.escape, palabras))
                mask = self.df['query'].str.contains(patron, case=False, na=False)
                self.df.loc[mask, 'matched_brand'] = grupo
            
            self.df['is_brand'] = self.df['matched_brand'].notna()
        else:
            self.df['matched_brand'] = None
            self.df['is_brand'] = False
    
    def _identificar_kws_importantes(self):
        """Identifica queries que contienen keywords importantes."""
        kws_importantes = self.config.keywords_importantes
        if kws_importantes:
            patron = '|'.join(map(re.escape, kws_importantes))
            self.df['kw_importante'] = self.df['query'].str.contains(
                patron, na=False, case=False
            )
        else:
            self.df['kw_importante'] = False
    
    def generar_subconjuntos(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Genera subconjuntos de datos según categorías de marca.
        
        Args:
            df: DataFrame a segmentar
            
        Returns:
            Diccionario de dataframes por categoría
        """
        subsets = {'totales': df}
        
        # Branded y non-branded
        subsets['branded'] = df[df['is_brand']].copy()
        subsets['non_branded'] = df[~df['is_brand']].copy()
        
        # Por cada grupo de marca
        for grupo, palabras in self.config.marcas.items():
            patron = '|'.join(map(re.escape, palabras))
            subsets[f'solo_{grupo}'] = df[
                df['query'].str.contains(patron, na=False, case=False)
            ].copy()
        
        return subsets
    
    def generar_subconjuntos_kwi(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Genera subconjuntos solo con keywords importantes.
        
        Args:
            df: DataFrame a segmentar
            
        Returns:
            Diccionario de dataframes filtrados
        """
        df_kwi = df[df['kw_importante']].copy()
        return self.generar_subconjuntos(df_kwi)
    
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
            periodo_1: (inicio, fin) período base
            periodo_2: (inicio, fin) período comparación
            
        Returns:
            DataFrame con comparación de métricas
        """
        # Filtrar períodos
        df_p1 = self.filtrar_por_fecha(*periodo_1)
        df_p2 = self.filtrar_por_fecha(*periodo_2)
        
        # Generar subconjuntos
        subsets_p1 = self.generar_subconjuntos(df_p1)
        subsets_p2 = self.generar_subconjuntos(df_p2)
        
        # Resumir
        resumen_p1 = self.resumir_dataframes(subsets_p1)
        resumen_p2 = self.resumir_dataframes(subsets_p2)
        
        # Merge y calcular variaciones
        resultado = resumen_p1.merge(
            resumen_p2,
            on='categoria',
            suffixes=('_ini', '_fin')
        )
        
        # Calcular variaciones para cada métrica
        for metrica in ['clics', 'impresiones']:
            col_ini = f'{metrica}_ini'
            col_fin = f'{metrica}_fin'
            
            resultado[f'var_{metrica}'] = resultado[col_fin] - resultado[col_ini]
            resultado[f'var_{metrica}_pct'] = np.where(
                resultado[col_ini] != 0,
                ((resultado[col_fin] - resultado[col_ini]) / resultado[col_ini]) * 100,
                np.nan
            ).round(2)
            
            # Variación en share
            resultado[f'var_share_{metrica}_pct'] = (
                resultado[f'share_pct_fin'] - resultado[f'share_pct_ini']
            ).round(2)
        
        return resultado
    
    def comparar_por_grupos(
        self,
        df_p2: pd.DataFrame,
        df_p1: pd.DataFrame,
        grupos: List[List[str]],
        nombres_grupos: Optional[List[str]] = None,
        metrica: str = 'clicks'
    ) -> pd.DataFrame:
        """
        Compara métricas por grupos de palabras clave.
        
        Args:
            df_p2: DataFrame período actual
            df_p1: DataFrame período anterior
            grupos: Lista de listas de palabras clave por grupo
            nombres_grupos: Nombres para cada grupo
            metrica: Métrica a comparar ('clicks', 'impressions')
            
        Returns:
            DataFrame con comparación
        """
        if nombres_grupos is None:
            nombres_grupos = [f'Grupo_{i+1}' for i in range(len(grupos))]
        
        col_metrica = self.config.columna_metricas.get(metrica, metrica)
        total_p2 = df_p2[col_metrica].sum()
        total_p1 = df_p1[col_metrica].sum()
        
        rows = []
        
        for nombre, palabras in zip(nombres_grupos, grupos):
            patron = '|'.join(map(re.escape, palabras))
            
            # Filtrar por grupo en cada período
            mask_p2 = df_p2['query'].str.contains(patron, na=False, case=False)
            mask_p1 = df_p1['query'].str.contains(patron, na=False, case=False)
            
            val_p2 = df_p2.loc[mask_p2, col_metrica].sum()
            val_p1 = df_p1.loc[mask_p1, col_metrica].sum()
            
            var_abs, var_pct = calcular_variacion(val_p1, val_p2)
            share_p2 = calcular_share(val_p2, total_p2)
            share_p1 = calcular_share(val_p1, total_p1)
            
            rows.append({
                'grupo': nombre,
                f'{metrica}_ini': val_p1,
                f'{metrica}_fin': val_p2,
                f'var_{metrica}': var_abs,
                f'var_{metrica}_pct': var_pct,
                f'share_{metrica}_ini_pct': share_p1,
                f'share_{metrica}_fin_pct': share_p2,
                f'var_share_{metrica}_pct': round(share_p2 - share_p1, 2)
            })
        
        return pd.DataFrame(rows)
    
    def top_n_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        metrica: str = 'clicks',
        n: int = 10,
        subdominio: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Obtiene top N queries con mayor variación.
        
        Args:
            periodo_1: Período base
            periodo_2: Período comparación
            metrica: Métrica a analizar
            n: Cantidad de resultados
            subdominio: Filtrar por subdominio específico
            
        Returns:
            DataFrame con queries de mayor variación
        """
        # Filtrar períodos
        df_p1 = self.filtrar_por_fecha(*periodo_1)
        df_p2 = self.filtrar_por_fecha(*periodo_2)
        
        # Filtrar por subdominio si se especifica
        if subdominio:
            patron = re.escape(subdominio) if isinstance(subdominio, str) else '|'.join(map(re.escape, subdominio))
            df_p1 = df_p1[df_p1['page'].str.contains(patron, na=False)]
            df_p2 = df_p2[df_p2['page'].str.contains(patron, na=False)]
        
        col_metrica = self.config.columna_metricas.get(metrica, metrica)
        
        # Agregar por query
        agg_p1 = df_p1.groupby('query').agg({
            col_metrica: 'sum',
            'matched_brand': 'first'
        }).reset_index()
        
        agg_p2 = df_p2.groupby('query').agg({
            col_metrica: 'sum',
            'matched_brand': 'first'
        }).reset_index()
        
        # Merge
        merged = agg_p1.merge(
            agg_p2,
            on='query',
            how='outer',
            suffixes=('_ini', '_fin')
        ).fillna(0)
        
        # Calcular variación
        merged['variacion'] = merged[f'{metrica}_fin'] - merged[f'{metrica}_ini']
        merged['variacion_abs'] = merged['variacion'].abs()
        
        # Top N
        top_n = merged.nlargest(n, 'variacion_abs').copy()
        top_n['grupo'] = top_n['matched_brand_fin'].fillna(top_n['matched_brand_ini'])
        
        return top_n[['query', 'grupo', f'{metrica}_ini', f'{metrica}_fin', 'variacion', 'variacion_abs']]
    
    def distribucion_por_categoria(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Calcula distribución de tráfico por categoría de keyword.
        
        Args:
            df: DataFrame a analizar (usa self.df si None)
            
        Returns:
            DataFrame con distribución
        """
        if df is None:
            df = self.df
        
        if df is None or df.empty:
            return pd.DataFrame(columns=['categoria', 'clicks', 'impressions', 'share_clicks_pct'])
        
        df = df.copy()
        df['categoria'] = df['matched_brand'].fillna('no_marca')
        
        resumen = df.groupby('categoria').agg({
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        total_clicks = resumen['clicks'].sum()
        resumen['share_clicks_pct'] = resumen['clicks'].apply(
            lambda x: calcular_share(x, total_clicks)
        )
        
        return resumen
