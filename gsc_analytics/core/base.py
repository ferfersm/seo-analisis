"""
Clase base abstracta para analizadores GSC.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import re

from ..contracts import IDimensionAnalyzer
from ..types import Dimension


class BaseAnalyzer(IDimensionAnalyzer, ABC):
    """
    Clase base para analizadores de dimensiones GSC.
    Implementa funcionalidad común para queries y páginas.
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        config,
        dimension: Dimension
    ):
        """
        Inicializa el analizador.
        
        Args:
            df: DataFrame con datos GSC
            config: Objeto de configuración
            dimension: Dimensión a analizar ('query' o 'page')
        """
        self.df = df.copy()
        self.config = config
        self.dimension = dimension
        self._preprocesar()
    
    def _preprocesar(self):
        """Preprocesa el dataframe."""
        # Convertir fechas
        fecha_col = self.config.columna_fecha
        if fecha_col in self.df.columns:
            self.df[fecha_col] = pd.to_datetime(self.df[fecha_col])
        
        # Preprocesar dimension
        if self.dimension in self.df.columns:
            if self.dimension == 'query':
                self.df[self.dimension] = self.df[self.dimension].str.lower()
            # Para 'page' mantener case sensitivity de URLs
    
    def filtrar_por_fecha(self, inicio: str, fin: str) -> pd.DataFrame:
        """
        Filtra el dataframe por rango de fechas.
        
        Args:
            inicio: Fecha inicio (YYYY-MM-DD)
            fin: Fecha fin (YYYY-MM-DD)
            
        Returns:
            DataFrame filtrado
        """
        fecha_col = self.config.columna_fecha
        mask = (
            (self.df[fecha_col] >= pd.to_datetime(inicio)) &
            (self.df[fecha_col] <= pd.to_datetime(fin))
        )
        return self.df.loc[mask].copy()
    
    def calcular_metricas(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula métricas agregadas.
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            Diccionario con métricas
        """
        from .metrics import calcular_metricas_base
        return calcular_metricas_base(df, self.config.columna_metricas)
    
    def _compilar_patron(self, palabras: List[str]) -> str:
        """Compila lista de palabras en patrón regex."""
        return '|'.join(map(re.escape, palabras))
    
    def _filtrar_por_marcas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra dataframe manteniendo solo filas que contienen marcas."""
        todas_marcas = self.config.todas_marcas
        if not todas_marcas:
            return df
        patron = self._compilar_patron(todas_marcas)
        return df[df[self.dimension].str.contains(patron, na=False, case=False)]
    
    def _excluir_marcas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra dataframe excluyendo filas que contienen marcas."""
        todas_marcas = self.config.todas_marcas
        if not todas_marcas:
            return df
        patron = self._compilar_patron(todas_marcas)
        return df[~df[self.dimension].str.contains(patron, na=False, case=False)]
    
    @abstractmethod
    def analizar_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str]
    ) -> pd.DataFrame:
        """Implementar en subclases."""
        pass
    
    @abstractmethod
    def top_n_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        metrica: str = 'clicks',
        n: int = 10
    ) -> pd.DataFrame:
        """Implementar en subclases."""
        pass
