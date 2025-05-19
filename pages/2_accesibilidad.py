import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_data_from_sheets

# Configuración de la página
st.set_page_config(
    page_title="Accesibilidad - Verificación de Insumos Alimentarios",
    page_icon="🚚",
    layout="wide"
)

# Estilos CSS para la página
st.markdown("""
<style>
    .page-title {font-size:2.3rem;font-weight:bold;color:#1E3A8A;text-align:center;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:2px solid #E0E0E0;}
    .section-header {font-size:1.5rem;color:#2563EB;margin:2rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:1px solid #E0E0E0;}
    .metric-card {background-color:#F9FAFB;border-radius:8px;padding:1.2rem;box-shadow:0 4px 6px rgba(0,0,0,0.1);text-align:center;height:100%;}
    .metric-title {font-size:1.1rem;font-weight:600;color:#4B5563;margin-bottom:0.5rem;}
    .metric-value {font-size:2.5rem;font-weight:bold;}
    .metric-good {color:#10B981;}
    .metric-warning {color:#F59E0B;}
    .metric-bad {color:#EF4444;}
    .info-box {background-color:#EFF6FF;border-left:4px solid #3B82F6;padding:1rem;margin:1rem 0;border-radius:0 4px 4px 0;}
    .alert-box {background-color:#FEF2F2;border-left:4px solid #EF4444;padding:1rem;margin:1rem 0;border-radius:0 4px 4px 0;}
    .insight-box {background-color:#ECFDF5;border-left:4px solid #10B981;padding:1rem;margin:1rem 0;border-radius:0 4px 4px 0;}
    .chart-container {background-color:white;border-radius:8px;padding:1rem;box-shadow:0 4px 6px rgba(0,0,0,0.05);margin-bottom:1.5rem;}
</style>
""", unsafe_allow_html=True)

# Función para obtener datos
def get_data():
    if 'filtered_df' in st.session_state:
        return st.session_state['filtered_df']
    else:
        return load_data_from_sheets()

# Función para calcular el porcentaje de Sí (1) en una columna
def calcular_porcentaje(df, columna):
    if columna not in df.columns or df.empty:
        return 0
    return round((df[columna].sum() / len(df)) * 100, 2)

def crear_metrica_html(titulo, valor, descripcion=None, umbral_bueno=90, umbral_medio=70):
    clase_color = "metric-good" if valor >= umbral_bueno else "metric-warning" if valor >= umbral_medio else "metric-bad"
    html = f"""
    <div class="metric-card">
        <div class="metric-title">{titulo}</div>
        <div class="metric-value {clase_color}">{valor}%</div>
    """
    if descripcion:
        html += f'<div style="font-size:0.9rem;color:#6B7280;margin-top:0.5rem;">{descripcion}</div>'
    html += "</div>"
    return html

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
        color_discrete_map={'Sí': '#10B981', 'No': '#EF4444'},
        title=titulo
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='Porcentaje (%)',
        yaxis_range=[0, 100]
    )
    
    return fig

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
        color_discrete_map={'Sí': '#10B981', 'No': '#EF4444'},
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    return fig

def crear_histograma(df, columna, titulo, n_bins=20):
    if columna not in df.columns or df.empty:
        return None
    
    df_filtrado = df[df[columna] > 0]
    
    if df_filtrado.empty:
        return None
    
    fig = px.histogram(
        df_filtrado,
        x=columna,
        nbins=n_bins,
        title=titulo,
        color_discrete_sequence=['#3B82F6']
    )
    
    fig.update_layout(
        xaxis_title='Valor ($)',
        yaxis_title='Frecuencia'
    )
    
    return fig

def main():
    # Título de la página
    st.markdown('<h1 class="page-title">Análisis de Accesibilidad al Comedor Comunitario</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    df = get_data()
    
    # Descripción del análisis
    st.markdown("""
        <div class="info-box">
            <p>Esta sección analiza las condiciones de accesibilidad de los comedores comunitarios. Se evalúan aspectos como
            la facilidad de acceso, la posibilidad de que el vehículo llegue directamente, la necesidad de trasbordos
            y el apoyo de la comunidad para el acceso, así como su impacto en otras entregas y en la inocuidad de los alimentos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar que hay datos para analizar
    if df.empty:
        st.error("No hay datos disponibles para analizar. Por favor, verifica la conexión con la fuente de datos.")
        return
    
    # Columnas de accesibilidad que vamos a analizar
    columnas_accesibilidad = [
        'comedor_facil_Acceso',
        'vehiculo_puede_llegar_a_sitio',
        'trasbordo',
        'ingreso_apoyo_comunidad',
        'demora_entregas',
        'inocuidad_comprometida'
    ]
    
    # Verificar que existen las columnas necesarias
    columnas_existentes = [col for col in columnas_accesibilidad if col in df.columns]
    
    if not columnas_existentes:
        st.error("No se encontraron las columnas de accesibilidad en los datos.")
        return
    
    # Sección de Indicadores Clave
    st.markdown('<h2 class="section-header">Indicadores Clave de Accesibilidad</h2>', unsafe_allow_html=True)
    
    # Crear métricas para los indicadores principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pct_facil_acceso = calcular_porcentaje(df, 'comedor_facil_Acceso')
        st.markdown(crear_metrica_html(
            "Comedores con Fácil Acceso",
            pct_facil_acceso,
            "Porcentaje de comedores donde el acceso es fácil"
        ), unsafe_allow_html=True)
    
    with col2:
        pct_vehiculo_llega = calcular_porcentaje(df, 'vehiculo_puede_llegar_a_sitio')
        st.markdown(crear_metrica_html(
            "Vehículo Llega Directamente",
            pct_vehiculo_llega,
            "Porcentaje de comedores donde el vehículo puede llegar directamente"
        ), unsafe_allow_html=True)
    
    with col3:
        pct_trasbordo = calcular_porcentaje(df, 'trasbordo')
        st.markdown(crear_metrica_html(
            "Requieren Trasbordo",
            pct_trasbordo,
            "Porcentaje de entregas que requieren trasbordo",
            umbral_bueno=10,
            umbral_medio=30
        ), unsafe_allow_html=True)
    
    # Análisis de Acceso
    st.markdown('<h2 class="section-header">Análisis de Acceso al Comedor</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'comedor_facil_Acceso' in df.columns:
            fig = crear_grafico_barras(df, 'comedor_facil_Acceso', 'Comedores con Fácil Acceso')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'vehiculo_puede_llegar_a_sitio' in df.columns:
            fig = crear_grafico_barras(df, 'vehiculo_puede_llegar_a_sitio', 'Vehículo Puede Llegar Directamente')
            st.plotly_chart(fig, use_container_width=True)
    
    # Análisis de Trasbordos
    st.markdown('<h2 class="section-header">Análisis de Trasbordos</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'trasbordo' in df.columns:
            fig = crear_grafico_pastel(df, 'trasbordo', 'Necesidad de Trasbordo')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'valor_trasbordo' in df.columns:
            df_trasbordo = df[df['trasbordo'] == 1].copy()
            
            if not df_trasbordo.empty:
                trasbordo_min = df_trasbordo['valor_trasbordo'].min()
                trasbordo_max = df_trasbordo['valor_trasbordo'].max()
                trasbordo_avg = df_trasbordo['valor_trasbordo'].mean()
                
                st.markdown(f"""
                    <div class="info-box">
                        <h3>Estadísticas de Costos de Trasbordo</h3>
                        <p><strong>Mínimo:</strong> ${trasbordo_min:,.0f}</p>
                        <p><strong>Máximo:</strong> ${trasbordo_max:,.0f}</p>
                        <p><strong>Promedio:</strong> ${trasbordo_avg:,.0f}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                fig = crear_histograma(df, 'valor_trasbordo', 'Distribución de Costos de Trasbordo')
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay registros con trasbordo en el período seleccionado.")
    
    # Análisis de Apoyo Comunitario
    st.markdown('<h2 class="section-header">Análisis de Apoyo Comunitario</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'ingreso_apoyo_comunidad' in df.columns:
            fig = crear_grafico_pastel(df, 'ingreso_apoyo_comunidad', 'Necesidad de Apoyo Comunitario')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'valor_apoyo' in df.columns:
            df_apoyo = df[df['ingreso_apoyo_comunidad'] == 1].copy()
            
            if not df_apoyo.empty:
                apoyo_min = df_apoyo['valor_apoyo'].min()
                apoyo_max = df_apoyo['valor_apoyo'].max()
                apoyo_avg = df_apoyo['valor_apoyo'].mean()
                
                st.markdown(f"""
                    <div class="info-box">
                        <h3>Estadísticas de Costos de Apoyo Comunitario</h3>
                        <p><strong>Mínimo:</strong> ${apoyo_min:,.0f}</p>
                        <p><strong>Máximo:</strong> ${apoyo_max:,.0f}</p>
                        <p><strong>Promedio:</strong> ${apoyo_avg:,.0f}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                fig = crear_histograma(df, 'valor_apoyo', 'Distribución de Costos de Apoyo Comunitario')
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay registros con apoyo comunitario en el período seleccionado.")
    
    # Impacto en Entregas y Calidad
    st.markdown('<h2 class="section-header">Impacto en Entregas y Calidad</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'demora_entregas' in df.columns:
            fig = crear_grafico_barras(df, 'demora_entregas', 'Demora en Otras Entregas')
            st.plotly_chart(fig, use_container_width=True)
            
            pct_demora = calcular_porcentaje(df, 'demora_entregas')
            
            if pct_demora > 15:
                st.markdown(f"""
                    <div class="alert-box">
                        <p><strong>Alerta:</strong> El {pct_demora}% de las entregas presentan demoras debido a dificultades de acceso.
                        Esto podría estar afectando las rutas de entrega y la eficiencia logística general.</p>
                    </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if 'inocuidad_comprometida' in df.columns:
            fig = crear_grafico_barras(df, 'inocuidad_comprometida', 'Inocuidad Comprometida')
            st.plotly_chart(fig, use_container_width=True)
            
            pct_inocuidad = calcular_porcentaje(df, 'inocuidad_comprometida')
            
            if pct_inocuidad > 5:
                st.markdown(f"""
                    <div class="alert-box">
                        <p><strong>Alerta crítica:</strong> El {pct_inocuidad}% de las entregas presentan riesgos de inocuidad
                        debido a las condiciones de acceso. Esta situación requiere atención inmediata para garantizar
                        la seguridad alimentaria.</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Análisis de Costos Totales
    st.markdown('<h2 class="section-header">Análisis de Costos Adicionales</h2>', unsafe_allow_html=True)
    
    if 'valor_trasbordo' in df.columns and 'valor_apoyo' in df.columns:
        total_trasbordo = df['valor_trasbordo'].sum()
        total_apoyo = df['valor_apoyo'].sum()
        total_costos = total_trasbordo + total_apoyo
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Costos Trasbordo", f"${total_trasbordo:,.0f}")
        
        with col2:
            st.metric("Total Costos Apoyo", f"${total_apoyo:,.0f}")
        
        with col3:
            st.metric("Total Costos Adicionales", f"${total_costos:,.0f}")
        
        costos_df = pd.DataFrame({
            'Categoría': ['Trasbordos', 'Apoyo Comunitario'],
            'Valor': [total_trasbordo, total_apoyo]
        })
        
        fig = px.pie(
            costos_df,
            values='Valor',
            names='Categoría',
            title='Distribución de Costos Adicionales',
            hole=0.4,
            color_discrete_sequence=['#3B82F6', '#8B5CF6']
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Conclusiones y Recomendaciones
    st.markdown('<h2 class="section-header">Conclusiones y Recomendaciones</h2>', unsafe_allow_html=True)
    
    pct_acceso_facil = calcular_porcentaje(df, 'comedor_facil_Acceso')
    pct_vehiculo_llega = calcular_porcentaje(df, 'vehiculo_puede_llegar_a_sitio')
    pct_trasbordo = calcular_porcentaje(df, 'trasbordo')
    pct_apoyo = calcular_porcentaje(df, 'ingreso_apoyo_comunidad')
    pct_demora = calcular_porcentaje(df, 'demora_entregas')
    pct_inocuidad = calcular_porcentaje(df, 'inocuidad_comprometida')
    
    conclusiones = []
    
    if pct_acceso_facil < 70:
        conclusiones.append(f"El {100-pct_acceso_facil:.1f}% de los comedores presentan dificultades de acceso, lo que podría estar impactando la eficiencia de las entregas.")
    
    if pct_trasbordo > 15:
        conclusiones.append(f"Un significativo {pct_trasbordo:.1f}% de las entregas requieren trasbordo, lo que incrementa costos operativos y tiempos de entrega.")
    
    if pct_demora > 10:
        conclusiones.append(f"Las dificultades de acceso están causando demoras en el {pct_demora:.1f}% de las entregas, afectando la programación de rutas.")
    
    if pct_inocuidad > 5:
        conclusiones.append(f"Preocupante: el {pct_inocuidad:.1f}% de las entregas presentan riesgos para la inocuidad de los alimentos debido a las condiciones de acceso.")
    
    if conclusiones:
        st.markdown("<h3>Principales Hallazgos</h3>", unsafe_allow_html=True)
        for conclusion in conclusiones:
            st.markdown(f"- {conclusion}")
    
    recomendaciones = []
    
    if pct_acceso_facil < 80 or pct_vehiculo_llega < 80:
        recomendaciones.append("Realizar un estudio detallado de rutas alternativas para mejorar el acceso a los comedores con dificultades.")
    
    if pct_trasbordo > 15:
        recomendaciones.append("Evaluar la posibilidad de utilizar vehículos más pequeños para acceder a zonas de difícil acceso.")
    
    if pct_inocuidad > 5:
        recomendaciones.append("Implementar protocolos especiales para trasbordos que garanticen la inocuidad de los alimentos.")
    
    if pct_demora > 10:
        recomendaciones.append("Optimizar la programación de rutas considerando los tiempos adicionales necesarios para comedores con acceso difícil.")
    
    if 'valor_trasbordo' in df.columns and 'valor_apoyo' in df.columns:
        total_costos = df['valor_trasbordo'].sum() + df['valor_apoyo'].sum()
        if total_costos > 0:
            recomendaciones.append(f"Evaluar el costo-beneficio de las mejoras en accesibilidad frente a los ${total_costos:,.0f} en costos adicionales por trasbordos y apoyo comunitario.")
    
    if recomendaciones:
        st.markdown("<h3>Recomendaciones</h3>", unsafe_allow_html=True)
        for recomendacion in recomendaciones:
            st.markdown(f"- {recomendacion}")
    
    st.markdown("""
        <div class="insight-box">
            <p><strong>Nota:</strong> El análisis de accesibilidad es fundamental para optimizar las rutas
            y garantizar la calidad de las entregas. Considere implementar un programa específico de mejoras
            de accesibilidad para los comedores con mayores dificultades.</p>
        </div>
    """, unsafe_allow_html=True)
    
if __name__ == "__main__":
    main()