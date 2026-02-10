"""
Funciones auxiliares y utilidades.
"""
from typing import List, Dict, Union
import pandas as pd
from pathlib import Path


def cargar_csvs(
    ruta_carpeta: Union[str, Path],
    col_fecha: str = 'date',
    recursive: bool = False,
    **read_csv_kwargs
) -> pd.DataFrame:
    """
    Carga y concatena múltiples archivos CSV.
    
    Args:
        ruta_carpeta: Ruta a la carpeta con CSVs
        col_fecha: Nombre de la columna de fecha
        recursive: Buscar en subcarpetas
        **read_csv_kwargs: Argumentos adicionales para pd.read_csv
        
    Returns:
        DataFrame concatenado
    """
    carpeta = Path(ruta_carpeta).expanduser()
    
    if not carpeta.is_dir():
        raise NotADirectoryError(f'{carpeta} no es una carpeta válida')
    
    patron = '**/*.csv' if recursive else '*.csv'
    archivos = sorted(carpeta.glob(patron))
    
    if not archivos:
        raise FileNotFoundError('No se encontraron archivos .csv')
    
    dfs = []
    for csv in archivos:
        df = pd.read_csv(csv, **read_csv_kwargs)
        if col_fecha in df.columns:
            df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True)


def concatena_dataframes(
    dfs: List[pd.DataFrame],
    ignore_index: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Concatena dos o más DataFrames.
    
    Args:
        dfs: Lista de DataFrames
        ignore_index: Reiniciar índice
        **kwargs: Argumentos adicionales para pd.concat
        
    Returns:
        DataFrame concatenado
    """
    if len(dfs) < 2:
        raise ValueError("Se requieren al menos dos DataFrames")
    return pd.concat(dfs, ignore_index=ignore_index, **kwargs)


def filtra_df(
    df: pd.DataFrame,
    filtros: Dict[str, Dict[str, Union[str, List[str]]]]
) -> pd.DataFrame:
    """
    Filtra DataFrame con condiciones complejas.
    
    Args:
        df: DataFrame a filtrar
        filtros: Diccionario de filtros por columna
            {
                'columna': {
                    'include_or': ['patron1', 'patron2'],
                    'include_and': ['patronA', 'patronB'],
                    'exclude_or': ['patronX', 'patronY']
                }
            }
            
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    for col, conditions in filtros.items():
        if col not in df_filtrado.columns:
            print(f"Advertencia: La columna '{col}' no existe. Se omitirá.")
            continue
        
        if conditions.get('include_or'):
            import re
            regex = '|'.join(conditions['include_or'])
            df_filtrado = df_filtrado[df_filtrado[col].str.contains(regex, na=False, regex=True)]
        
        if conditions.get('include_and'):
            for pattern in conditions['include_and']:
                df_filtrado = df_filtrado[df_filtrado[col].str.contains(pattern, na=False, regex=True)]
        
        if conditions.get('exclude_or'):
            import re
            regex = '|'.join(conditions['exclude_or'])
            df_filtrado = df_filtrado[~df_filtrado[col].str.contains(regex, na=False, regex=True)]
    
    return df_filtrado.reset_index(drop=True)


def resumen_kw(
    df: pd.DataFrame,
    col: str = 'query',
    kw: Union[str, None] = None,
    periodo: str = 'month',
    rango: tuple = (None, None),
    exact_match: bool = True
) -> pd.DataFrame:
    """
    Resumen de métricas para una keyword específica o todas.
    
    Args:
        df: DataFrame con datos GSC
        col: Columna a filtrar
        kw: Keyword a buscar (None para todas)
        periodo: 'month' o 'day'
        rango: Tupla (fecha_inicio, fecha_fin) opcional
        exact_match: Coincidencia exacta o parcial
        
    Returns:
        DataFrame con resumen temporal
    """
    import re
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtro keyword
    if kw is not None:
        if exact_match:
            df_kw = df[df[col] == kw]
        else:
            df_kw = df[df[col].str.contains(re.escape(kw), case=False, na=False)]
    else:
        df_kw = df
    
    # Agregación temporal
    if periodo == 'month':
        df_kw['period'] = df_kw['date'].dt.to_period('M').dt.to_timestamp()
        freq = 'M'
    elif periodo == 'day':
        df_kw['period'] = df_kw['date'].dt.floor('D')
        freq = 'D'
    else:
        raise ValueError("periodo debe ser 'month' o 'day'")
    
    df_met = (
        df_kw.groupby('period')
        .agg(
            impressions=('impressions', 'sum'),
            clicks=('clicks', 'sum'),
            avg_position=('position', 'mean')
        )
        .assign(ctr=lambda d: (d['clicks'] / d['impressions']).round(2))
        .round({'avg_position': 2})
        .astype({'impressions': int, 'clicks': int})
    )
    
    # Completar rango
    start, end = rango
    if not df_met.empty and (start or end):
        idx = pd.date_range(
            start or df_met.index.min(),
            end or df_met.index.max(),
            freq=freq
        )
        df_met = df_met.reindex(idx, fill_value=0)
        df_met.index.name = 'period'
    
    # Variaciones
    df_met['variacion_clicks'] = df_met['clicks'].diff().fillna(0).astype(int)
    df_met['variacion_impr'] = df_met['impressions'].diff().fillna(0).astype(int)
    df_met['variacion_clicks_pct'] = df_met['clicks'].pct_change().round(2).fillna(0)
    df_met['variacion_impr_pct'] = df_met['impressions'].pct_change().round(2).fillna(0)
    
    return df_met.reset_index()
