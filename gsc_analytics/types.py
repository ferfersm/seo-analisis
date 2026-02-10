"""
Tipos y enumeraciones para GSC Analytics.
"""
from typing import Dict, List, Tuple, Optional, Union, Literal
from dataclasses import dataclass
import pandas as pd

# Tipos básicos
FechaStr = str
Periodo = Tuple[FechaStr, FechaStr]
Metricas = List[str]
Dimension = Literal['query', 'page']

# Configuración
MarcasConfig = Dict[str, List[str]]
ColumnasConfig = Dict[str, str]

# Resultados
ResultadoComparacion = Dict[str, pd.DataFrame]


@dataclass
class MetricasCalculadas:
    """Contenedor para métricas con sus variaciones."""
    valor_inicial: Union[int, float]
    valor_final: Union[int, float]
    variacion_absoluta: Union[int, float]
    variacion_porcentual: Optional[float]
    share_inicial: float
    share_final: float
    variacion_share: float
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para DataFrame."""
        return {
            'valor_ini': self.valor_inicial,
            'valor_fin': self.valor_final,
            'variacion': self.variacion_absoluta,
            'variacion_pct': self.variacion_porcentual,
            'share_ini_pct': self.share_inicial,
            'share_fin_pct': self.share_final,
            'variacion_share_pct': self.variacion_share
        }


@dataclass
class SubconjuntoGSC:
    """Representa un subconjunto de datos GSC filtrado."""
    nombre: str
    df: pd.DataFrame
    es_marca: bool = False
    grupo: Optional[str] = None
