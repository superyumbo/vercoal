import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data_from_sheets

# Configuración de la página
st.set_page_config(page_title="Condiciones del Vehículo", page_icon="🚚", layout="wide")

# Estilos CSS básicos para la página
st.markdown("""
<style>
    .page-title {font-size: 2.3rem; font-weight: bold; color: #4338CA; text-align: center; margin-bottom: 1.5rem; border-bottom: 2px solid #E0E0E0;}
    .section-header {font-size: 1.5rem; color: #6366F1; margin: 2rem 0 1rem 0; border-bottom: 1px solid #E0E0E0;}
    .comparison-title {font-size: 1.2rem; font-weight: 600; color: #4B5563; margin-top: 1rem; margin-bottom: 0.5rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# Función para obtener datos
def get_data():
    if 'filtered_df' in st.session_state:
        return st.session_state['filtered_df']
    return load_data_from_sheets()

# Función para calcular el porcentaje de valores positivos
def calcular_porcentaje(df, columna):
    if columna not in df.columns or df.empty:
        return 0
    return round((df[columna].sum() / len(df)) * 100, 2)

# Función para crear gráfico de barras
def crear_grafico_barras(df, columna, titulo):
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    fig = px.bar(
        conteo,
        x='Respuesta',
        y='Porcentaje',
        text=conteo['Porcentaje'].apply(lambda x: f'{x}%'),
        color='Respuesta',
        color_discrete_map={'Sí': '#6366F1', 'No': '#EF4444'},
        title=titulo
    )
    fig.update_layout(xaxis_title='', yaxis_title='Porcentaje (%)', yaxis_range=[0, 100])
    return fig

# Función para crear gráfico de pastel
def crear_grafico_pastel(df, columna, titulo):
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    fig = px.pie(
        conteo,
        values='Conteo',
        names='Respuesta',
        title=titulo,
        hole=0.4,
        color='Respuesta',
        color_discrete_map={'Sí': '#6366F1', 'No': '#EF4444'}
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    return fig

# Función para crear análisis por vehículo
def crear_analisis_por_vehiculo(df):
    if 'placa_vehiculo' not in df.columns or df.empty:
        return None
    
    columnas_vehiculo = [
        'vehiculo_limpio_buen_estado',
        'alimentos_de_calidad_cantidad',
        'contenedores_para_cada_tipoalimento'
    ]
    
    columnas_existentes = [col for col in columnas_vehiculo if col in df.columns]
    if not columnas_existentes:
        return None
    
    resultados = pd.DataFrame()
    for col in columnas_existentes:
        temp = df.groupby('placa_vehiculo')[col].mean().reset_index()
        temp[col] = temp[col] * 100
        if resultados.empty:
            resultados = temp
        else:
            resultados = resultados.merge(temp, on='placa_vehiculo')
    
    resultados['promedio_general'] = resultados[columnas_existentes].mean(axis=1)
    resultados = resultados.sort_values(by='promedio_general', ascending=False)
    
    if len(resultados) > 20:
        mejores = resultados.head(10)
        peores = resultados.tail(10)
        resultados = pd.concat([mejores, peores])
    
    fig = px.bar(
        resultados,
        x='placa_vehiculo',
        y='promedio_general',
        text=resultados['promedio_general'].apply(lambda x: f'{x:.1f}%'),
        title='Calificación General por Vehículo',
        color='promedio_general',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(xaxis_title='Placa del Vehículo', yaxis_title='Calificación Promedio (%)', yaxis_range=[0, 100])
    
    return fig, resultados

# Función para generar análisis con componentes nativos de Streamlit
def generar_analisis_streamlit(df, columna, titulo):
    if columna not in df.columns or df.empty:
        st.warning(f"No hay datos suficientes para analizar {titulo.lower()}.")
        return
    
    valor_positivo = calcular_porcentaje(df, columna)
    valor_negativo = 100 - valor_positivo
    
    # Categorizar el resultado y elegir el tipo de contenedor
    if valor_positivo >= 90:
        categoria = "excelente"
        recomendacion = "Mantener los altos estándares actuales."
        st.success(f"El indicador muestra un desempeño **{categoria}** con un **{valor_positivo}%** de cumplimiento.")
    elif valor_positivo >= 70:
        categoria = "aceptable"
        recomendacion = "Implementar mejoras puntuales para optimizar este indicador."
        st.info(f"El indicador muestra un desempeño **{categoria}** con un **{valor_positivo}%** de cumplimiento.")
    else:
        categoria = "preocupante"
        recomendacion = "Priorizar acciones correctivas inmediatas para elevar este indicador."
        st.warning(f"El indicador muestra un desempeño **{categoria}** con un **{valor_positivo}%** de cumplimiento.")
    
    # Mostrar métricas de Streamlit
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Cumplimiento", value=f"{valor_positivo}%", delta=f"{valor_positivo-70:.1f}%" if valor_positivo-70 != 0 else None)
    with col2:
        st.metric(label="No Cumplimiento", value=f"{valor_negativo}%", delta=f"-{valor_negativo:.1f}%", delta_color="inverse")
    
    # Análisis por ruta si existe
    if 'ruta' in df.columns:
        rutas = df.groupby('ruta')[columna].mean().reset_index()
        rutas[columna] = rutas[columna] * 100
        mejor_ruta = rutas.loc[rutas[columna].idxmax()]
        peor_ruta = rutas.loc[rutas[columna].idxmin()]
        
        st.markdown("#### Análisis por Ruta")
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Mejor ruta:** {mejor_ruta['ruta']} ({mejor_ruta[columna]:.1f}%)")
        with col2:
            st.warning(f"**Ruta con desafíos:** {peor_ruta['ruta']} ({peor_ruta[columna]:.1f}%)")
    
    # Recomendación
    st.info(f"**Recomendación:** {recomendacion}")

def main():
    # Título de la página
    st.markdown('<h1 class="page-title">Análisis de Condiciones del Vehículo</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    df = get_data()
    
    # Descripción del análisis
    st.info("Esta sección analiza las condiciones de los vehículos que realizan las entregas de insumos alimentarios. "
            "Se evalúan aspectos como la limpieza y estado del vehículo, la calidad de los alimentos entregados "
            "y el uso de contenedores adecuados para cada tipo de alimento.")
    
    # Verificar que hay datos para analizar
    if df.empty:
        st.error("No hay datos disponibles para analizar. Por favor, verifica la conexión con la fuente de datos.")
        return
    
    # Columnas de vehículo que vamos a analizar
    columnas_vehiculo = [
        'vehiculo_limpio_buen_estado',
        'alimentos_de_calidad_cantidad',
        'contenedores_para_cada_tipoalimento'
    ]
    
    # Verificar que existen las columnas necesarias
    columnas_existentes = [col for col in columnas_vehiculo if col in df.columns]
    
    if not columnas_existentes:
        st.error("No se encontraron las columnas de condiciones del vehículo en los datos.")
        return
    
    # Sección de Indicadores Clave
    st.markdown('<h2 class="section-header">Indicadores Clave de Condiciones del Vehículo</h2>', unsafe_allow_html=True)
    
    # Crear métricas para los indicadores principales
    col1, col2, col3 = st.columns(3)
    
    # Mostrar métricas con componente nativo de Streamlit
    with col1:
        if 'vehiculo_limpio_buen_estado' in df.columns:
            pct_vehiculo_limpio = calcular_porcentaje(df, 'vehiculo_limpio_buen_estado')
            st.metric(
                label="Vehículos Limpios y en Buen Estado",
                value=f"{pct_vehiculo_limpio}%",
                delta=f"{pct_vehiculo_limpio-85:.1f}%" if pct_vehiculo_limpio-85 != 0 else None,
                help="Porcentaje de vehículos que se encuentran limpios y en buen estado"
            )
        else:
            st.warning("No hay datos sobre limpieza y estado de vehículos")
    
    with col2:
        if 'alimentos_de_calidad_cantidad' in df.columns:
            pct_alimentos_calidad = calcular_porcentaje(df, 'alimentos_de_calidad_cantidad')
            st.metric(
                label="Alimentos de Calidad y Cantidad",
                value=f"{pct_alimentos_calidad}%",
                delta=f"{pct_alimentos_calidad-85:.1f}%" if pct_alimentos_calidad-85 != 0 else None,
                help="Porcentaje de entregas donde los alimentos llegan con calidad y en la cantidad programada"
            )
        else:
            st.warning("No hay datos sobre calidad y cantidad de alimentos")
    
    with col3:
        if 'contenedores_para_cada_tipoalimento' in df.columns:
            pct_contenedores = calcular_porcentaje(df, 'contenedores_para_cada_tipoalimento')
            st.metric(
                label="Uso de Contenedores Adecuados",
                value=f"{pct_contenedores}%",
                delta=f"{pct_contenedores-85:.1f}%" if pct_contenedores-85 != 0 else None,
                help="Porcentaje de entregas que utilizan contenedores adecuados para cada tipo de alimento"
            )
        else:
            st.warning("No hay datos sobre uso de contenedores adecuados")
    
    # Índice general de calidad del vehículo
    if columnas_existentes:
        valores_promedio = [calcular_porcentaje(df, col) for col in columnas_existentes]
        indice_general = round(sum(valores_promedio) / len(valores_promedio), 2)
        
        st.markdown("### Índice General de Calidad del Vehículo")
        
        # Usar Streamlit columns para centrar
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("🚚")
            # Usar el componente de métrica de Streamlit
            st.metric(
                label="",
                value=f"{indice_general}%",
                delta=f"{indice_general-85:.1f}%" if indice_general-85 != 0 else None,
            )
    
    # Análisis Detallado de Cada Indicador
    st.markdown('<h2 class="section-header">Análisis Detallado de Cada Indicador</h2>', unsafe_allow_html=True)
    
    # Limpieza y Estado del Vehículo
    if 'vehiculo_limpio_buen_estado' in df.columns:
        st.markdown('<h3 class="comparison-title">Limpieza y Estado del Vehículo</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_grafico_barras(
                df,
                'vehiculo_limpio_buen_estado',
                'Vehículos Limpios y en Buen Estado'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Usar componentes nativos de Streamlit para el análisis
            with st.container():
                st.subheader("Análisis")
                generar_analisis_streamlit(
                    df, 
                    'vehiculo_limpio_buen_estado',
                    'Limpieza y Estado del Vehículo'
                )
    
    # Calidad y Cantidad de Alimentos
    if 'alimentos_de_calidad_cantidad' in df.columns:
        st.markdown('<h3 class="comparison-title">Calidad y Cantidad de Alimentos</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_grafico_barras(
                df,
                'alimentos_de_calidad_cantidad',
                'Alimentos de Calidad y Cantidad Adecuada'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Usar componentes nativos de Streamlit para el análisis
            with st.container():
                st.subheader("Análisis")
                generar_analisis_streamlit(
                    df, 
                    'alimentos_de_calidad_cantidad',
                    'Calidad y Cantidad de Alimentos'
                )
    
    # Uso de Contenedores Adecuados
    if 'contenedores_para_cada_tipoalimento' in df.columns:
        st.markdown('<h3 class="comparison-title">Uso de Contenedores Adecuados</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_grafico_pastel(
                df,
                'contenedores_para_cada_tipoalimento',
                'Uso de Contenedores Adecuados'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Usar componentes nativos de Streamlit para el análisis
            with st.container():
                st.subheader("Análisis")
                generar_analisis_streamlit(
                    df, 
                    'contenedores_para_cada_tipoalimento',
                    'Uso de Contenedores Adecuados'
                )
    
    # Análisis por Vehículo
    if 'placa_vehiculo' in df.columns and columnas_existentes:
        st.markdown('<h2 class="section-header">Análisis por Vehículo</h2>', unsafe_allow_html=True)
        
        resultado_vehiculo = crear_analisis_por_vehiculo(df)
        
        if resultado_vehiculo:
            fig, df_vehiculos = resultado_vehiculo
            
            # Mostrar gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Identificar mejores y peores vehículos
            if len(df_vehiculos) > 1:
                mejor_vehiculo = df_vehiculos.iloc[0]
                peor_vehiculo = df_vehiculos.iloc[-1]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success(f"### Mejor Vehículo\n"
                               f"**Placa:** {mejor_vehiculo['placa_vehiculo']}\n\n"
                               f"**Calificación:** {mejor_vehiculo['promedio_general']:.2f}%")
                
                with col2:
                    st.warning(f"### Vehículo con Oportunidades de Mejora\n"
                               f"**Placa:** {peor_vehiculo['placa_vehiculo']}\n\n"
                               f"**Calificación:** {peor_vehiculo['promedio_general']:.2f}%")
        else:
            st.warning("No hay suficientes datos para realizar un análisis por vehículo.")
    
    # Conclusiones y Recomendaciones
    st.markdown('<h2 class="section-header">Conclusiones y Recomendaciones</h2>', unsafe_allow_html=True)
    
    # Calcular indicadores clave para conclusiones
    pct_vehiculo_limpio = calcular_porcentaje(df, 'vehiculo_limpio_buen_estado') if 'vehiculo_limpio_buen_estado' in df.columns else 0
    pct_alimentos_calidad = calcular_porcentaje(df, 'alimentos_de_calidad_cantidad') if 'alimentos_de_calidad_cantidad' in df.columns else 0
    pct_contenedores = calcular_porcentaje(df, 'contenedores_para_cada_tipoalimento') if 'contenedores_para_cada_tipoalimento' in df.columns else 0
    
    # Generar conclusiones basadas en los indicadores
    conclusiones = []
    
    if pct_vehiculo_limpio < 90 and 'vehiculo_limpio_buen_estado' in df.columns:
        conclusiones.append(f"El {100-pct_vehiculo_limpio:.1f}% de los vehículos no cumplen con los estándares de limpieza y buen estado, lo que podría afectar la inocuidad de los alimentos.")
    
    if pct_alimentos_calidad < 95 and 'alimentos_de_calidad_cantidad' in df.columns:
        conclusiones.append(f"En el {100-pct_alimentos_calidad:.1f}% de las entregas, los alimentos no llegan con la calidad o cantidad programada, lo que podría generar insatisfacción en los comedores comunitarios.")
    
    if pct_contenedores < 90 and 'contenedores_para_cada_tipoalimento' in df.columns:
        conclusiones.append(f"En el {100-pct_contenedores:.1f}% de las entregas no se utilizan contenedores adecuados para cada tipo de alimento, lo que podría comprometer la calidad e inocuidad de los mismos.")
    
    # Mostrar conclusiones
    st.subheader("Principales Hallazgos")
    
    if conclusiones:
        for conclusion in conclusiones:
            st.info(conclusion)
    else:
        st.success("No se han identificado problemas significativos en las condiciones de los vehículos. "
                 "¡Felicitaciones por mantener altos estándares de calidad!")
    
    # Generar recomendaciones
    recomendaciones = []
    
    if pct_vehiculo_limpio < 90 and 'vehiculo_limpio_buen_estado' in df.columns:
        recomendaciones.append("Implementar un protocolo de verificación de limpieza y estado del vehículo antes de cada jornada de entrega.")
    
    if pct_alimentos_calidad < 95 and 'alimentos_de_calidad_cantidad' in df.columns:
        recomendaciones.append("Reforzar los procesos de control de calidad de los alimentos antes de cargarlos en los vehículos.")
    
    if pct_contenedores < 90 and 'contenedores_para_cada_tipoalimento' in df.columns:
        recomendaciones.append("Estandarizar el uso de contenedores específicos para cada tipo de alimento, con un sistema de etiquetado claro.")
    
    # Mostrar recomendaciones con componentes nativos
    if recomendaciones:
        st.subheader("Recomendaciones")
        for i, recomendacion in enumerate(recomendaciones):
            st.write(f"{i+1}. {recomendacion}")
    
    # Información de mejores prácticas con componente nativo de Streamlit
    st.markdown('<h2 class="section-header">Mejores Prácticas Recomendadas</h2>', unsafe_allow_html=True)
    
    with st.expander("Ver mejores prácticas recomendadas", expanded=True):
        st.write("**Para garantizar las mejores condiciones del vehículo y alimentos, se recomienda:**")
        st.markdown("""
        * Realizar limpieza diaria de los vehículos, con especial atención al área de carga.
        * Utilizar contenedores específicos para cada tipo de alimento, evitando la contaminación cruzada.
        * Mantener la cadena de frío para alimentos perecederos durante todo el trayecto.
        * Verificar la calidad y cantidad de alimentos antes de iniciar cada ruta.
        * Implementar un sistema de registro y seguimiento de incidencias relacionadas con el vehículo.
        """)

if __name__ == "__main__":
    main()