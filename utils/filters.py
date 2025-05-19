import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

def apply_date_filter(df, start_date=None, end_date=None):
    """
    Aplica filtros de fecha al DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a filtrar.
        start_date (datetime, optional): Fecha de inicio para filtrar.
        end_date (datetime, optional): Fecha de fin para filtrar.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado por fecha.
    """
    # Verificar que la columna de fecha existe
    if 'fecha' not in df.columns or df.empty:
        return df
    
    # Asegurar que la columna de fecha es datetime
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Eliminar filas sin fecha válida
    df = df.dropna(subset=['fecha'])
    
    # Si no hay fechas para filtrar o no hay datos, retornar df original
    if df.empty:
        return df
    
    # Aplicar filtro de fecha
    if start_date and end_date:
        # Convertir a datetime si es necesario
        if not isinstance(start_date, datetime):
            start_date = pd.to_datetime(start_date)
        if not isinstance(end_date, datetime):
            end_date = pd.to_datetime(end_date)
        
        # Asegurar que end_date incluye todo el día
        end_date = end_date + timedelta(days=1) - timedelta(seconds=1)
        
        # Aplicar filtro
        df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]
    
    return df

def apply_category_filter(df, column, values):
    """
    Aplica filtros de categoría al DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a filtrar.
        column (str): Nombre de la columna a filtrar.
        values (list): Lista de valores a incluir.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado por categoría.
    """
    # Verificar que la columna existe
    if column not in df.columns or df.empty:
        return df
    
    # Si no hay valores para filtrar o 'Todos' está en los valores, retornar df original
    if not values or 'Todos' in values or 'Todas' in values:
        return df
    
    # Aplicar filtro
    df = df[df[column].isin(values)]
    
    return df

def apply_range_filter(df, column, min_val=None, max_val=None):
    """
    Aplica filtros de rango al DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a filtrar.
        column (str): Nombre de la columna a filtrar.
        min_val (numeric, optional): Valor mínimo a incluir.
        max_val (numeric, optional): Valor máximo a incluir.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado por rango.
    """
    # Verificar que la columna existe
    if column not in df.columns or df.empty:
        return df
    
    # Asegurar que la columna es numérica
    if not pd.api.types.is_numeric_dtype(df[column]):
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except:
            return df
    
    # Aplicar filtro de rango
    if min_val is not None:
        df = df[df[column] >= min_val]
    
    if max_val is not None:
        df = df[df[column] <= max_val]
    
    return df

def apply_boolean_filter(df, column, value=None):
    """
    Aplica filtros booleanos al DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a filtrar.
        column (str): Nombre de la columna a filtrar.
        value (bool, optional): Valor a filtrar (True, False o None para ambos).
    
    Returns:
        pandas.DataFrame: DataFrame filtrado por valor booleano.
    """
    # Verificar que la columna existe
    if column not in df.columns or df.empty:
        return df
    
    # Si no hay valor para filtrar, retornar df original
    if value is None:
        return df
    
    # Aplicar filtro
    df = df[df[column] == value]
    
    return df

def create_date_filter_widget(df, key_prefix="date"):
    """
    Crea un widget de filtro de fecha para Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame para obtener el rango de fechas.
        key_prefix (str, optional): Prefijo para las claves de los widgets.
    
    Returns:
        tuple: (start_date, end_date) Fechas seleccionadas.
    """
    # Verificar que la columna de fecha existe
    if 'fecha' not in df.columns or df.empty:
        return None, None
    
    # Asegurar que la columna de fecha es datetime
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Eliminar filas sin fecha válida
    df = df.dropna(subset=['fecha'])
    
    # Si no hay fechas válidas, retornar None
    if df.empty:
        return None, None
    
    # Obtener rango de fechas
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    # Crear widget de filtro de fecha
    date_range = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}_date_range"
    )
    
    # Extraer fechas seleccionadas
    if len(date_range) == 2:
        start_date, end_date = date_range
        return start_date, end_date
    else:
        return None, None

def create_category_filter_widget(df, column, label=None, key_prefix="cat", multiselect=True):
    """
    Crea un widget de filtro de categoría para Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame para obtener las categorías.
        column (str): Nombre de la columna a filtrar.
        label (str, optional): Etiqueta para el widget.
        key_prefix (str, optional): Prefijo para las claves de los widgets.
        multiselect (bool, optional): Si es True, permite selección múltiple.
    
    Returns:
        list or str: Valores seleccionados.
    """
    # Verificar que la columna existe
    if column not in df.columns or df.empty:
        return None
    
    # Obtener categorías únicas
    categories = sorted(df[column].unique().tolist())
    
    # Si no hay categorías, retornar None
    if not categories:
        return None
    
    # Establecer etiqueta
    if label is None:
        label = column.capitalize()
    
    # Crear widget de filtro de categoría
    if multiselect:
        selected = st.sidebar.multiselect(
            label,
            options=['Todos'] + categories,
            default='Todos',
            key=f"{key_prefix}_{column}"
        )
        
        # Si 'Todos' está seleccionado, retornar None (sin filtro)
        if 'Todos' in selected:
            return None
        
        return selected
    else:
        selected = st.sidebar.selectbox(
            label,
            options=['Todos'] + categories,
            index=0,
            key=f"{key_prefix}_{column}"
        )
        
        # Si 'Todos' está seleccionado, retornar None (sin filtro)
        if selected == 'Todos':
            return None
        
        return selected

def create_range_filter_widget(df, column, label=None, key_prefix="range"):
    """
    Crea un widget de filtro de rango para Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame para obtener el rango.
        column (str): Nombre de la columna a filtrar.
        label (str, optional): Etiqueta para el widget.
        key_prefix (str, optional): Prefijo para las claves de los widgets.
    
    Returns:
        tuple: (min_val, max_val) Valores mínimo y máximo seleccionados.
    """
    # Verificar que la columna existe
    if column not in df.columns or df.empty:
        return None, None
    
    # Asegurar que la columna es numérica
    if not pd.api.types.is_numeric_dtype(df[column]):
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except:
            return None, None
    
    # Obtener rango de valores
    min_val = float(df[column].min())
    max_val = float(df[column].max())
    
    # Si min_val es igual a max_val, no tiene sentido mostrar el filtro
    if min_val == max_val:
        return min_val, max_val
    
    # Establecer etiqueta
    if label is None:
        label = column.replace('_', ' ').capitalize()
    
    # Crear widget de filtro de rango
    values = st.sidebar.slider(
        label,
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val),
        key=f"{key_prefix}_{column}"
    )
    
    # Extraer valores seleccionados
    min_selected, max_selected = values
    
    # Si se seleccionó todo el rango, retornar None (sin filtro)
    if min_selected == min_val and max_selected == max_val:
        return None, None
    
    return min_selected, max_selected

def create_boolean_filter_widget(df, column, label=None, key_prefix="bool"):
    """
    Crea un widget de filtro booleano para Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame (no usado, pero mantenido por consistencia).
        column (str): Nombre de la columna a filtrar.
        label (str, optional): Etiqueta para el widget.
        key_prefix (str, optional): Prefijo para las claves de los widgets.
    
    Returns:
        bool or None: Valor seleccionado o None para ambos.
    """
    # Establecer etiqueta
    if label is None:
        label = column.replace('_', ' ').capitalize()
    
    # Crear widget de filtro booleano
    options = ['Todos', 'Sí', 'No']
    selected = st.sidebar.radio(
        label,
        options=options,
        index=0,
        key=f"{key_prefix}_{column}"
    )
    
    # Mapear selección a valor booleano
    if selected == 'Sí':
        return True
    elif selected == 'No':
        return False
    else:
        return None

def create_all_filters(df):
    """
    Crea todos los filtros relevantes para el DataFrame en Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame para filtrar.
    
    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    st.sidebar.title("Filtros")
    
    filtered_df = df.copy()
    
    # Filtro de fecha
    start_date, end_date = create_date_filter_widget(filtered_df)
    if start_date and end_date:
        filtered_df = apply_date_filter(filtered_df, start_date, end_date)
    
    # Filtro de comuna
    if 'comuna' in df.columns:
        comuna_selected = create_category_filter_widget(filtered_df, 'comuna', 'Comuna')
        if comuna_selected:
            filtered_df = apply_category_filter(filtered_df, 'comuna', comuna_selected)
    
    # Filtro de ruta
    if 'ruta' in df.columns:
        ruta_selected = create_category_filter_widget(filtered_df, 'ruta', 'Ruta')
        if ruta_selected:
            filtered_df = apply_category_filter(filtered_df, 'ruta', ruta_selected)
    
    # Filtro de nodo
    if 'nodo' in df.columns:
        nodo_selected = create_category_filter_widget(filtered_df, 'nodo', 'Nodo')
        if nodo_selected:
            filtered_df = apply_category_filter(filtered_df, 'nodo', nodo_selected)
    
    # Filtro de día de entrega
    if 'dia_entrega' in df.columns:
        dia_selected = create_category_filter_widget(filtered_df, 'dia_entrega', 'Día de Entrega')
        if dia_selected:
            filtered_df = apply_category_filter(filtered_df, 'dia_entrega', dia_selected)
    
    # Filtro de conductor
    if 'conductor_auxiliar' in df.columns:
        conductor_selected = create_category_filter_widget(filtered_df, 'conductor_auxiliar', 'Conductor/Auxiliar')
        if conductor_selected:
            filtered_df = apply_category_filter(filtered_df, 'conductor_auxiliar', conductor_selected)
    
    # Filtro de tiempo de entrega
    if 'tiempo_de_entrega_de_alimentos' in df.columns:
        tiempo_selected = create_category_filter_widget(filtered_df, 'tiempo_de_entrega_de_alimentos', 'Tiempo de Entrega')
        if tiempo_selected:
            filtered_df = apply_category_filter(filtered_df, 'tiempo_de_entrega_de_alimentos', tiempo_selected)
    
    # Agregar botón para restablecer filtros
    if st.sidebar.button("Restablecer Filtros"):
        return df
    
    # Mostrar conteo de registros
    st.sidebar.markdown(f"**Registros filtrados:** {len(filtered_df)}")
    
    return filtered_df