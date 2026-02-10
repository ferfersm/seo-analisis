"""
Cálculo de métricas con variaciones absolutas y porcentuales.
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


def calcular_metricas_base(
    df: pd.DataFrame,
    columna_metricas: Dict[str, str]
) -> Dict[str, float]:
    """
    Calcula métricas base para un dataframe.
    
    Args:
        df: DataFrame con datos GSC
        columna_metricas: Mapeo de nombres estándar a columnas del df
        
    Returns:
        Diccionario con métricas calculadas
    """
    if df.empty:
        return {
            'clicks': 0,
            'impressions': 0,
            'ctr': 0.0,
            'position': 0.0
        }
    
    clicks_col = columna_metricas.get('clicks', 'clicks')
    imp_col = columna_metricas.get('impressions', 'impressions')
    ctr_col = columna_metricas.get('ctr', 'ctr')
    pos_col = columna_metricas.get('position', 'position')
    
    clicks = df[clicks_col].sum()
    impressions = df[imp_col].sum()
    
    # CTR ponderado por impresiones
    if impressions > 0:
        ctr = np.average(df[ctr_col], weights=df[imp_col])
    else:
        ctr = 0.0
    
    # Posición ponderada por impresiones
    if impressions > 0:
        position = np.average(df[pos_col], weights=df[imp_col])
    else:
        position = 0.0
    
    return {
        'clicks': clicks,
        'impressions': impressions,
        'ctr': round(ctr, 2),
        'position': round(position, 1)
    }


def calcular_variacion(
    valor_ini: float,
    valor_fin: float,
    redondeo: int = 2
) -> Tuple[float, Optional[float]]:
    """
    Calcula variación absoluta y porcentual.
    
    Args:
        valor_ini: Valor inicial
        valor_fin: Valor final
        redondeo: Decimales para porcentaje
        
    Returns:
        Tupla (variacion_absoluta, variacion_porcentual)
    """
    var_abs = valor_fin - valor_ini
    
    if valor_ini != 0:
        var_pct = (var_abs / valor_ini) * 100
        var_pct = round(var_pct, redondeo)
    else:
        var_pct = None
    
    return var_abs, var_pct


def calcular_share(
    valor: float,
    total: float,
    redondeo: int = 2
) -> float:
    """
    Calcula el share (participación porcentual).
    
    Args:
        valor: Valor individual
        total: Valor total
        redondeo: Decimales
        
    Returns:
        Share porcentual
    """
    if total > 0:
        return round((valor / total) * 100, redondeo)
    return 0.0


def agregar_por_dimension(
    df: pd.DataFrame,
    dimension: str,
    columna_metricas: Dict[str, str]
) -> pd.DataFrame:
    """
    Agrega métricas por una dimensión (query o page).
    
    Args:
        df: DataFrame con datos GSC
        dimension: Columna para agrupar ('query' o 'page')
        columna_metricas: Mapeo de nombres estándar a columnas
        
    Returns:
        DataFrame agregado
    """
    if df.empty:
        return pd.DataFrame()
    
    clicks_col = columna_metricas.get('clicks', 'clicks')
    imp_col = columna_metricas.get('impressions', 'impressions')
    ctr_col = columna_metricas.get('ctr', 'ctr')
    pos_col = columna_metricas.get('position', 'position')
    
    grouped = df.groupby(dimension).agg({
        clicks_col: 'sum',
        imp_col: 'sum',
        ctr_col: lambda x: np.average(x, weights=df.loc[x.index, imp_col]),
        pos_col: lambda x: np.average(x, weights=df.loc[x.index, imp_col])
    }).reset_index()
    
    grouped.columns = [dimension, 'clicks', 'impressions', 'ctr', 'position']
    grouped['ctr'] = grouped['ctr'].round(2)
    grouped['position'] = grouped['position'].round(1)
    
    return grouped
