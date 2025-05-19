import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def calcular_porcentaje(df, columna):
    """
    Calcula el porcentaje de valores positivos (1) en una columna.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a calcular.
    
    Returns:
        float: Porcentaje de valores positivos (1).
    """
    if columna not in df.columns or df.empty:
        return 0
    return round((df[columna].sum() / len(df)) * 100, 2)

def crear_grafico_barras(df, columna, titulo, color_positivo="#4CAF50", color_negativo="#EF4444"):
    """
    Crea un gráfico de barras para visualizar porcentajes Sí/No.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        color_positivo (str, optional): Color para los valores "Sí".
        color_negativo (str, optional): Color para los valores "No".
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de barras.
    """
    # Contar valores y calcular porcentajes
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    
    # Mapear 0/1 a No/Sí
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    # Crear gráfico
    fig = px.bar(
        conteo,
        x='Respuesta',
        y='Porcentaje',
        text=conteo['Porcentaje'].apply(lambda x: f'{x}%'),
        color='Respuesta',
        color_discrete_map={'Sí': color_positivo, 'No': color_negativo},
        title=titulo
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='Porcentaje (%)',
        yaxis_range=[0, 100]
    )
    
    return fig

def crear_grafico_pastel(df, columna, titulo, color_si='#4CAF50', color_no='#EF4444'):
    """
    Crea un gráfico de pastel para visualizar distribución Sí/No.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        color_si (str, optional): Color para los valores "Sí".
        color_no (str, optional): Color para los valores "No".
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de pastel.
    """
    # Contar valores y calcular porcentajes
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    
    # Mapear 0/1 a No/Sí
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    # Crear gráfico
    fig = px.pie(
        conteo,
        values='Conteo',
        names='Respuesta',
        title=titulo,
        hole=0.4,
        color='Respuesta',
        color_discrete_map={'Sí': color_si, 'No': color_no}
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    return fig

def crear_grafico_pastel_categorias(df, columna, titulo):
    """
    Crea un gráfico de pastel para visualizar distribución de categorías.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de pastel.
    """
    if columna not in df.columns or df.empty:
        return None
    
    # Contar valores y calcular porcentajes
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Categoría', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    
    # Crear gráfico
    fig = px.pie(
        conteo,
        values='Conteo',
        names='Categoría',
        title=titulo,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    return fig

def crear_grafico_barras_por_grupo(df, columna_grupo, columna_dato, titulo, color_scale='Blues'):
    """
    Crea un gráfico de barras agrupado por una columna.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna_grupo (str): Nombre de la columna por la que agrupar.
        columna_dato (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        color_scale (str, optional): Escala de color para las barras.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de barras.
    """
    if columna_grupo not in df.columns or df.empty or columna_dato not in df.columns:
        return None
    
    # Agrupar por la columna de grupo y calcular promedio
    resultados = df.groupby(columna_grupo)[columna_dato].mean().reset_index()
    resultados[columna_dato] = resultados[columna_dato] * 100  # Convertir a porcentaje
    
    # Ordenar por valor descendente
    resultados = resultados.sort_values(by=columna_dato, ascending=False)
    
    # Crear gráfico
    fig = px.bar(
        resultados,
        x=columna_grupo,
        y=columna_dato,
        text=resultados[columna_dato].apply(lambda x: f'{x:.1f}%'),
        title=titulo,
        color=columna_dato,
        color_continuous_scale=color_scale
    )
    
    fig.update_layout(
        xaxis_title=columna_grupo.capitalize(),
        yaxis_title='Porcentaje (%)',
        yaxis_range=[0, 100]
    )
    
    return fig

def crear_grafico_barras_multiple(df, columna_grupo, columnas_datos, titulo, color_scale='Blues'):
    """
    Crea un gráfico de barras con múltiples series por grupo.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna_grupo (str): Nombre de la columna por la que agrupar.
        columnas_datos (list): Lista de nombres de columnas a visualizar.
        titulo (str): Título del gráfico.
        color_scale (str, optional): Escala de color para las barras.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de barras múltiple.
    """
    if columna_grupo not in df.columns or df.empty:
        return None
    
    # Verificar que existen las columnas
    columnas_existentes = [col for col in columnas_datos if col in df.columns]
    
    if not columnas_existentes:
        return None
    
    # Crear DataFrame para resultados
    resultados = pd.DataFrame()
    
    # Para cada columna, calcular promedio por grupo
    for col in columnas_existentes:
        # Agrupar por la columna de grupo y calcular promedio
        temp = df.groupby(columna_grupo)[col].mean().reset_index()
        temp[col] = temp[col] * 100  # Convertir a porcentaje
        
        # Renombrar columna para mejor visualización
        temp.rename(columns={col: col.replace('_', ' ').title()}, inplace=True)
        
        # Iniciar o unir con resultados
        if resultados.empty:
            resultados = temp
        else:
            resultados = resultados.merge(temp, on=columna_grupo)
    
    # Convertir a formato largo para Plotly
    resultados_melted = pd.melt(
        resultados,
        id_vars=[columna_grupo],
        value_name='Porcentaje',
        var_name='Indicador'
    )
    
    # Crear gráfico
    fig = px.bar(
        resultados_melted,
        x=columna_grupo,
        y='Porcentaje',
        color='Indicador',
        title=titulo,
        barmode='group',
        text=resultados_melted['Porcentaje'].apply(lambda x: f'{x:.1f}%')
    )
    
    fig.update_layout(
        xaxis_title=columna_grupo.capitalize(),
        yaxis_title='Porcentaje (%)',
        yaxis_range=[0, 100],
        legend_title='Indicador'
    )
    
    return fig

def crear_grafico_linea_temporal(df, columna, titulo, color='#4CAF50'):
    """
    Crea un gráfico de línea que muestra la evolución temporal de un indicador.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        color (str, optional): Color de la línea.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de línea.
    """
    # Asegurarse que fecha es datetime
    if 'fecha' not in df.columns:
        return None
    
    # Convertir a datetime si no lo es ya
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Agrupar por mes
    df['mes'] = df['fecha'].dt.to_period('M')
    
    # Calcular promedio por mes
    datos_tiempo = df.groupby('mes')[columna].mean().reset_index()
    datos_tiempo['mes'] = datos_tiempo['mes'].dt.to_timestamp()
    datos_tiempo[columna] = datos_tiempo[columna] * 100  # Convertir a porcentaje
    
    # Crear gráfico
    fig = px.line(
        datos_tiempo,
        x='mes',
        y=columna,
        markers=True,
        title=titulo,
        line_shape='linear'
    )
    
    fig.update_traces(line_color=color)
    
    fig.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Porcentaje (%)',
        yaxis_range=[0, 100]
    )
    
    return fig

def crear_grafico_radar(df, columnas, labels=None, color='rgb(0, 153, 76)'):
    """
    Crea un gráfico de radar para múltiples indicadores.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columnas (list): Lista de nombres de columnas a visualizar.
        labels (list, optional): Lista de etiquetas para los indicadores.
        color (str, optional): Color del área del radar.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el gráfico de radar.
    """
    # Verificar que existen las columnas
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if len(columnas_existentes) < 3:  # Necesitamos al menos 3 columnas para un radar útil
        return None
    
    # Calcular porcentajes para cada columna
    valores = [calcular_porcentaje(df, col) for col in columnas_existentes]
    
    # Usar etiquetas proporcionadas o los nombres de columnas
    if not labels:
        labels = [col.replace('_', ' ').title() for col in columnas_existentes]
    
    # Crear figura
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=labels,
        fill='toself',
        line_color=color,
        fillcolor=color.replace('rgb', 'rgba').replace(')', ', 0.5)'),
        name='Indicadores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False
    )
    
    return fig

def crear_mapa_calor_comunas(df, columnas, titulo, color_scale='RdYlGn'):
    """
    Crea un mapa de calor por comunas para variables seleccionadas.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columnas (list): Lista de nombres de columnas a visualizar.
        titulo (str): Título del gráfico.
        color_scale (str, optional): Escala de color para el mapa de calor.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el mapa de calor.
    """
    # Verificar si hay comunas en el DataFrame
    if 'comuna' not in df.columns or df.empty:
        return None
    
    # Crear DataFrame para resultados
    resultados = pd.DataFrame()
    
    # Para cada columna, calcular promedio por comuna
    for col in columnas:
        if col in df.columns:
            # Agrupar por comuna y calcular promedio (0-1)
            temp = df.groupby('comuna')[col].mean().reset_index()
            # Convertir a porcentaje
            temp[col] = temp[col] * 100
            
            # Iniciar o unir con resultados
            if resultados.empty:
                resultados = temp
            else:
                resultados = resultados.merge(temp, on='comuna')
    
    # Si no hay resultados, retornar None
    if resultados.empty:
        return None
    
    # Preparar datos para mapa de calor
    resultados_pivot = resultados.set_index('comuna')
    
    # Mapear nombres de columnas a nombres más legibles
    column_mapping = {
        'comedor_facil_Acceso': 'Acceso Fácil',
        'vehiculo_puede_llegar_a_sitio': 'Vehículo Llega Directo',
        'trasbordo': 'Requiere Trasbordo',
        'ingreso_apoyo_comunidad': 'Requiere Apoyo Comunidad',
        'demora_entregas': 'Causa Demoras',
        'inocuidad_comprometida': 'Compromete Inocuidad',
        'entrega_en_dia_programado': 'Entrega en Día Programado',
        'alimentos_debidamente_entregados': 'Alimentos Verificados',
        'vehiculo_limpio_buen_estado': 'Vehículo Limpio',
        'alimentos_de_calidad_cantidad': 'Alimentos de Calidad',
        'contenedores_para_cada_tipoalimento': 'Contenedores Adecuados',
        'actitud_conductor_respetuosa_colaborativa': 'Actitud Conductor',
        'actitud_auxiliar_respetuosa_colaborativa': 'Actitud Auxiliar',
        'actitud_gestora_respetuosa_colaborativa': 'Actitud Gestora',
        'buena_disposicion_recibir_mercados': 'Disposición Recepción',
        'comunicacion_efectiva': 'Comunicación Efectiva',
        'resolucion_inconvenientes': 'Resolución Problemas'
    }
    
    # Renombrar columnas si existen en el mapping
    resultados_pivot.columns = [column_mapping.get(col, col) for col in resultados_pivot.columns]
    
    # Crear figura
    fig = px.imshow(
        resultados_pivot.T,
        text_auto='.1f',
        labels=dict(x='Comuna', y='Indicador', color='Porcentaje (%)'),
        title=titulo,
        color_continuous_scale=color_scale,
        aspect='auto'
    )
    
    fig.update_layout(
        xaxis_title='Comuna',
        yaxis_title='Indicador',
        coloraxis_colorbar=dict(title='%')
    )
    
    return fig

def crear_grafico_correlacion(df, columnas, titulo):
    """
    Crea un mapa de calor de correlación entre diferentes indicadores.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columnas (list): Lista de nombres de columnas a correlacionar.
        titulo (str): Título del gráfico.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el mapa de calor de correlación.
    """
    # Verificar que existen las columnas
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if len(columnas_existentes) < 2:  # Necesitamos al menos 2 columnas para correlación
        return None
    
    # Calcular matriz de correlación
    df_corr = df[columnas_existentes].corr()
    
    # Mapear nombres de columnas a nombres más legibles
    column_mapping = {
        'comedor_facil_Acceso': 'Acceso Fácil',
        'vehiculo_puede_llegar_a_sitio': 'Vehículo Llega',
        'trasbordo': 'Trasbordo',
        'ingreso_apoyo_comunidad': 'Apoyo Comunidad',
        'demora_entregas': 'Demora Entregas',
        'inocuidad_comprometida': 'Inocuidad Comprometida',
        'entrega_en_dia_programado': 'Entrega en Día',
        'alimentos_debidamente_entregados': 'Alimentos Verificados',
        'vehiculo_limpio_buen_estado': 'Vehículo Limpio',
        'alimentos_de_calidad_cantidad': 'Alimentos Calidad',
        'contenedores_para_cada_tipoalimento': 'Contenedores Adecuados',
        'actitud_conductor_respetuosa_colaborativa': 'Actitud Conductor',
        'actitud_auxiliar_respetuosa_colaborativa': 'Actitud Auxiliar',
        'actitud_gestora_respetuosa_colaborativa': 'Actitud Gestora',
        'buena_disposicion_recibir_mercados': 'Disposición Recepción',
        'comunicacion_efectiva': 'Comunicación',
        'resolucion_inconvenientes': 'Resolución Problemas'
    }
    
    # Renombrar índices y columnas
    df_corr.index = [column_mapping.get(col, col) for col in df_corr.index]
    df_corr.columns = [column_mapping.get(col, col) for col in df_corr.columns]
    
    # Crear figura
    fig = px.imshow(
        df_corr,
        text_auto='.2f',
        labels=dict(x='Indicador', y='Indicador', color='Correlación'),
        title=titulo,
        color_continuous_scale='RdBu_r',
        range_color=[-1, 1]
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        height=600,
        width=700
    )
    
    return fig

def crear_histograma(df, columna, titulo, n_bins=20, color='#4CAF50'):
    """
    Crea un histograma para analizar la distribución de valores.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        n_bins (int, optional): Número de bins para el histograma.
        color (str, optional): Color de las barras.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el histograma.
    """
    if columna not in df.columns or df.empty:
        return None
    
    # Filtrar filas donde la columna tiene valores mayores que 0
    df_filtrado = df[df[columna] > 0]
    
    if df_filtrado.empty:
        return None
    
    # Crear gráfico
    fig = px.histogram(
        df_filtrado,
        x=columna,
        nbins=n_bins,
        title=titulo,
        color_discrete_sequence=[color]
    )
    
    fig.update_layout(
        xaxis_title='Valor',
        yaxis_title='Frecuencia'
    )
    
    return fig

def crear_boxplot(df, columna, titulo, color='#4CAF50'):
    """
    Crea un boxplot para analizar la distribución de valores.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Nombre de la columna a visualizar.
        titulo (str): Título del gráfico.
        color (str, optional): Color del boxplot.
    
    Returns:
        plotly.graph_objects.Figure: Figura de Plotly con el boxplot.
    """
    if columna not in df.columns or df.empty:
        return None
    
    # Filtrar filas donde la columna tiene valores mayores que 0
    df_filtrado = df[df[columna] > 0]
    
    if df_filtrado.empty:
        return None
    
    # Crear gráfico
    fig = px.box(
        df_filtrado,
        y=columna,
        title=titulo
    )
    
    fig.update_traces(marker_color=color)
    
    fig.update_layout(
        yaxis_title='Valor'
    )
    
    return fig