"""
Interfaces y contratos para GSC Analytics.
Define los contratos que deben cumplir las clases del sistema.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd


class IConfigurable(ABC):
    """Interfaz para objetos configurables."""
    
    @abstractmethod
    def validar_config(self) -> bool:
        """Valida que la configuración sea correcta."""
        pass
    
    @abstractmethod
    def obtener_marcas(self) -> List[str]:
        """Retorna lista plana de todas las marcas."""
        pass
    
    @abstractmethod
    def es_marca(self, texto: str) -> bool:
        """Verifica si un texto contiene términos de marca."""
        pass


class IAnalyzer(ABC):
    """Interfaz base para analizadores de GSC."""
    
    @abstractmethod
    def filtrar_por_fecha(self, inicio: str, fin: str) -> pd.DataFrame:
        """Filtra el dataframe por rango de fechas."""
        pass
    
    @abstractmethod
    def calcular_metricas(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas agregadas para un dataframe."""
        pass


class IDimensionAnalyzer(IAnalyzer):
    """Interfaz para analizadores por dimensión."""
    
    @abstractmethod
    def analizar_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str]
    ) -> pd.DataFrame:
        """Analiza variación entre dos períodos."""
        pass
    
    @abstractmethod
    def top_n_variacion(
        self,
        periodo_1: Tuple[str, str],
        periodo_2: Tuple[str, str],
        metrica: str = 'clicks',
        n: int = 10
    ) -> pd.DataFrame:
        """Obtiene top N elementos con mayor variación."""
        pass
