import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.data_loader import load_data_from_sheets

# Configuración de la página
st.set_page_config(page_title="Cumplimiento - Verificación de Insumos Alimentarios", page_icon="✅", layout="wide")

# Estilos CSS para la página (simplificados, sin estilos para análisis en HTML)
st.markdown("""
<style>
    .page-title {font-size: 2.3rem; font-weight: bold; color: #0F766E; text-align: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #E0E0E0;}
    .section-header {font-size: 1.5rem; color: #0D9488; margin: 2rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px solid #E0E0E0;}
    .metric-card {background-color: #F8FAFC; border-radius: 8px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; height: 100%; transition: transform 0.3s;}
    .metric-card:hover {transform: translateY(-5px);}
    .metric-title {font-size: 1.1rem; font-weight: 600; color: #334155; margin-bottom: 0.5rem;}
    .metric-value {font-size: 2.5rem; font-weight: bold;}
    .metric-good {color: #10B981;}
    .metric-warning {color: #F59E0B;}
    .metric-bad {color: #EF4444;}
    .metric-description {font-size: 0.9rem; color: #64748B; margin-top: 0.5rem;}
    .info-box {background-color: #ECFEFF; border-left: 4px solid #06B6D4; padding: 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0;}
    .alert-box {background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0;}
    .success-box {background-color: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0;}
    .chart-container {background-color: white; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-bottom: 1.5rem;}
    .comparison-title {font-size: 1.2rem; font-weight: 600; color: #334155; margin-top: 1rem; margin-bottom: 0.5rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# Funciones
def get_data():
    """Obtiene datos de la sesión o carga nuevos si no existen"""
    return st.session_state.get('filtered_df', load_data_from_sheets())

def calcular_porcentaje(df, columna):
    """Calcula el porcentaje de valores positivos (1) en una columna"""
    if columna not in df.columns or df.empty:
        return 0
    return round((df[columna].sum() / len(df)) * 100, 2)

def crear_metrica_html(titulo, valor, descripcion=None, umbral_bueno=90, umbral_medio=70):
    """Crea una métrica HTML con formato según el valor"""
    clase_color = "metric-good" if valor >= umbral_bueno else "metric-warning" if valor >= umbral_medio else "metric-bad"
    html = f"""<div class="metric-card"><div class="metric-title">{titulo}</div><div class="metric-value {clase_color}">{valor}%</div>"""
    if descripcion:
        html += f'<div class="metric-description">{descripcion}</div>'
    html += "</div>"
    return html

def crear_grafico_pastel(df, columna, titulo, color_si='#10B981', color_no='#EF4444'):
    """Crea un gráfico de pastel para visualizar distribución Sí/No"""
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    fig = px.pie(
        conteo, values='Conteo', names='Respuesta', title=titulo, hole=0.4,
        color='Respuesta', color_discrete_map={'Sí': color_si, 'No': color_no}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    return fig

def crear_grafico_barras_tiempo_entrega(df, column_tiempo, column_cumplimiento=None):
    """Crea un gráfico de barras para visualizar el tiempo de entrega"""
    if column_cumplimiento is not None and column_cumplimiento in df.columns:
        def categorizar_cumplimiento(row):
            if row['entrega_en_dia_programado'] == 1 and row['alimentos_debidamente_entregados'] == 1:
                return "Cumplimiento Total"
            elif row['entrega_en_dia_programado'] == 1 and row['alimentos_debidamente_entregados'] == 0:
                return "Solo Día Programado"
            elif row['entrega_en_dia_programado'] == 0 and row['alimentos_debidamente_entregados'] == 1:
                return "Solo Verificación"
            else:
                return "Incumplimiento Total"
        
        df_analisis = df.copy()
        df_analisis['cumplimiento'] = df_analisis.apply(categorizar_cumplimiento, axis=1)
        agrupado = df_analisis.groupby([column_tiempo, 'cumplimiento']).size().reset_index(name='conteo')
        
        orden_tiempo = ['Menos de media hora', 'Entre media y una hora', 'Más de una hora']
        if set(agrupado[column_tiempo]).issubset(set(orden_tiempo)):
            agrupado[column_tiempo] = pd.Categorical(agrupado[column_tiempo], categories=orden_tiempo, ordered=True)
            agrupado = agrupado.sort_values([column_tiempo, 'cumplimiento'])
        
        fig = px.bar(
            agrupado, x=column_tiempo, y='conteo', color='cumplimiento', barmode='group',
            title='Distribución del Tiempo de Entrega por Tipo de Cumplimiento',
            color_discrete_map={
                'Cumplimiento Total': '#10B981', 'Solo Día Programado': '#60A5FA',
                'Solo Verificación': '#FBBF24', 'Incumplimiento Total': '#F43F5E'
            }
        )
        fig.update_layout(xaxis_title='Tiempo de Entrega', yaxis_title='Número de Entregas', legend_title='Tipo de Cumplimiento')
        return fig
    else:
        conteo_tiempo = df[column_tiempo].value_counts().reset_index()
        conteo_tiempo.columns = ['Tiempo de Entrega', 'Conteo']
        
        orden_tiempo = ['Menos de media hora', 'Entre media y una hora', 'Más de una hora']
        if set(conteo_tiempo['Tiempo de Entrega']).issubset(set(orden_tiempo)):
            conteo_tiempo['Tiempo de Entrega'] = pd.Categorical(conteo_tiempo['Tiempo de Entrega'], categories=orden_tiempo, ordered=True)
            conteo_tiempo = conteo_tiempo.sort_values('Tiempo de Entrega')
        
        fig = px.bar(
            conteo_tiempo, x='Tiempo de Entrega', y='Conteo', color='Tiempo de Entrega',
            title='Distribución del Tiempo de Entrega', color_discrete_sequence=px.colors.sequential.Teal
        )
        fig.update_layout(xaxis_title='Tiempo de Entrega', yaxis_title='Número de Entregas', showlegend=False)
        return fig

def crear_analisis_dia_entrega(df):
    """Crea un análisis de distribución por día de entrega usando componentes nativos de Streamlit"""
    if 'dia_entrega' not in df.columns or df.empty:
        return "No hay información disponible sobre días de entrega."
        
    # Agrupar por día de entrega
    conteo_dias = df['dia_entrega'].value_counts().reset_index()
    conteo_dias.columns = ['Día', 'Conteo']
    conteo_dias['Porcentaje'] = round((conteo_dias['Conteo'] / conteo_dias['Conteo'].sum()) * 100, 1)
    
    # Ordenar días si es posible
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    if set(conteo_dias['Día']).issubset(set(orden_dias)):
        conteo_dias['Día'] = pd.Categorical(conteo_dias['Día'], categories=orden_dias, ordered=True)
        conteo_dias = conteo_dias.sort_values('Día')
    
    # Determinar días con mayor y menor entregas
    dia_max = conteo_dias.loc[conteo_dias['Conteo'].idxmax()]
    dia_min = conteo_dias.loc[conteo_dias['Conteo'].idxmin()]
    
    return conteo_dias, dia_max, dia_min

def main():
    # Título y descripción
    st.markdown('<h1 class="page-title">Análisis de Cumplimiento en la Entrega</h1>', unsafe_allow_html=True)
    
    df = get_data()
    
    st.markdown("""
        <div class="info-box">
            <p>Esta sección analiza el cumplimiento en la entrega de los insumos alimentarios a los comedores comunitarios. 
            Se evalúan aspectos como la puntualidad (entregas en día programado), tiempo de duración de la entrega y 
            la verificación adecuada de los alimentos entregados.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar datos
    if df.empty:
        st.error("No hay datos disponibles para analizar. Por favor, verifica la conexión con la fuente de datos.")
        return
    
    columnas_cumplimiento = ['entrega_en_dia_programado', 'alimentos_debidamente_entregados']
    columnas_existentes = [col for col in columnas_cumplimiento if col in df.columns]
    
    if not columnas_existentes:
        st.error("No se encontraron las columnas de cumplimiento en los datos.")
        return
    
    # Indicadores Clave
    st.markdown('<h2 class="section-header">Indicadores Clave de Cumplimiento</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    pct_dia_programado = calcular_porcentaje(df, 'entrega_en_dia_programado')
    pct_alimentos_verificados = calcular_porcentaje(df, 'alimentos_debidamente_entregados')
    
    with col1:
        st.markdown(crear_metrica_html(
            "Entregas en Día Programado", pct_dia_programado,
            "Porcentaje de entregas realizadas en el día programado"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(crear_metrica_html(
            "Alimentos Debidamente Verificados", pct_alimentos_verificados,
            "Porcentaje de entregas donde los alimentos son contados y pesados adecuadamente"
        ), unsafe_allow_html=True)
    
    # Análisis de Entregas en Día Programado
    st.markdown('<h2 class="section-header">Análisis de Entregas en Día Programado</h2>', unsafe_allow_html=True)
    
    if 'entrega_en_dia_programado' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_grafico_pastel(
                df, 'entrega_en_dia_programado', 'Entregas en Día Programado',
                color_si="#0D9488", color_no="#F43F5E"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Análisis del porcentaje de cumplimiento usando componentes nativos de Streamlit
            pct_si = calcular_porcentaje(df, 'entrega_en_dia_programado')
            pct_no = 100 - pct_si
            
            nivel_cumplimiento = "alto" if pct_si >= 90 else "medio" if pct_si >= 70 else "bajo"
            impacto = "positivo" if nivel_cumplimiento == "alto" else "potencialmente negativo" if nivel_cumplimiento == "bajo" else "moderado"
            
            st.subheader("Análisis del Cumplimiento")
            st.write(f"El **{pct_si}%** de las entregas se realizan en el día programado, lo que representa un nivel de cumplimiento **{nivel_cumplimiento}**.")
            
            st.write(f"El restante **{pct_no}%** de entregas que no se realizan en el día programado pueden generar:")
            st.markdown("- Dificultades en la planificación de los comedores comunitarios")
            st.markdown("- Posible desabastecimiento temporal de productos esenciales")
            st.markdown("- Alteraciones en la programación de actividades en los comedores")
            
            st.write(f"Este indicador tiene un impacto **{impacto}** en la eficiencia general del programa de alimentación comunitaria.")
    
    # Análisis de Verificación de Alimentos
    st.markdown('<h2 class="section-header">Análisis de Verificación de Alimentos</h2>', unsafe_allow_html=True)
    
    if 'alimentos_debidamente_entregados' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = crear_grafico_pastel(
                df, 'alimentos_debidamente_entregados', 'Alimentos Debidamente Verificados',
                color_si="#0D9488", color_no="#F43F5E"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Análisis de verificación de alimentos usando componentes nativos de Streamlit
            pct_verificados = calcular_porcentaje(df, 'alimentos_debidamente_entregados')
            pct_no_verificados = 100 - pct_verificados
            
            nivel_verificacion = "alto" if pct_verificados >= 95 else "medio" if pct_verificados >= 80 else "bajo"
            riesgo = "bajo" if nivel_verificacion == "alto" else "alto" if nivel_verificacion == "bajo" else "moderado"
            
            st.subheader("Análisis de la Verificación")
            st.write(f"El **{pct_verificados}%** de las entregas tienen una adecuada verificación de alimentos (conteo y pesaje), lo que representa un nivel **{nivel_verificacion}** de control.")
            
            st.write(f"El **{pct_no_verificados}%** de entregas sin verificación adecuada pueden resultar en:")
            st.markdown("- Posibles inconsistencias en el inventario de los comedores")
            st.markdown("- Riesgo de entregas incompletas o con cantidades incorrectas")
            st.markdown("- Dificultades para realizar seguimiento preciso a los insumos")
            
            st.write(f"Este indicador presenta un **riesgo {riesgo}** para la integridad del sistema de distribución de alimentos.")
    
    # Relación entre Indicadores
    st.markdown('<h2 class="section-header">Relación entre Indicadores</h2>', unsafe_allow_html=True)
    
    if 'entrega_en_dia_programado' in df.columns and 'alimentos_debidamente_entregados' in df.columns:
        col1, col2 = st.columns(2)
        
        cumplen_ambos = (df['entrega_en_dia_programado'] == 1) & (df['alimentos_debidamente_entregados'] == 1)
        pct_ambos = round((cumplen_ambos.sum() / len(df)) * 100, 2)
        
        no_cumplen_ninguno = (df['entrega_en_dia_programado'] == 0) & (df['alimentos_debidamente_entregados'] == 0)
        pct_ninguno = round((no_cumplen_ninguno.sum() / len(df)) * 100, 2)
        
        with col1:
            st.markdown(f"""
                <div class="success-box">
                    <h3 style="margin-top: 0;">Cumplimiento Total</h3>
                    <p>El <strong>{pct_ambos}%</strong> de las entregas cumplen con ambos criterios: se realizan en el día programado y los alimentos son debidamente verificados.</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="alert-box">
                    <h3 style="margin-top: 0;">Incumplimiento Total</h3>
                    <p>El <strong>{pct_ninguno}%</strong> de las entregas no cumplen con ninguno de los criterios: ni se realizan en el día programado ni los alimentos son debidamente verificados.</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Gráfico de barras para tiempo de entrega
    if 'tiempo_de _entrega_de_alimentos' in df.columns:
        st.markdown('<h3 class="comparison-title">Distribución del Tiempo de Entrega</h3>', unsafe_allow_html=True)
        
        fig = crear_grafico_barras_tiempo_entrega(
            df, 'tiempo_de _entrega_de_alimentos',
            'alimentos_debidamente_entregados' if 'alimentos_debidamente_entregados' in df.columns else None
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Agregar análisis por días de entrega con componentes nativos de Streamlit
        if 'dia_entrega' in df.columns:
            conteo_dias, dia_max, dia_min = crear_analisis_dia_entrega(df)
            
            st.subheader("Análisis por Día de Entrega")
            st.write(f"El día con mayor número de entregas es el **{dia_max['Día']}**, con un **{dia_max['Porcentaje']}%** del total de entregas.")
            st.write(f"El día con menor número de entregas es el **{dia_min['Día']}**, con un **{dia_min['Porcentaje']}%** del total.")
            
            st.write("La distribución de entregas por día de la semana es:")
            for _, row in conteo_dias.iterrows():
                st.markdown(f"- **{row['Día']}:** {row['Conteo']} entregas ({row['Porcentaje']}%)")
    
    # Conclusiones y Recomendaciones
    st.markdown('<h2 class="section-header">Conclusiones y Recomendaciones</h2>', unsafe_allow_html=True)
    
    # Generar conclusiones
    conclusiones = []
    
    if pct_dia_programado < 90:
        conclusiones.append(f"El {100-pct_dia_programado:.1f}% de las entregas no se realizan en el día programado, lo que podría afectar la planificación de los comedores comunitarios.")
    
    if pct_alimentos_verificados < 95:
        conclusiones.append(f"En el {100-pct_alimentos_verificados:.1f}% de las entregas, los alimentos no son debidamente verificados (contados y pesados), lo que podría ocasionar inconsistencias en el inventario.")
    
    if 'tiempo_de _entrega_de_alimentos' in df.columns:
        try:
            entregas_largas = df[df['tiempo_de _entrega_de_alimentos'] == 'Más de una hora'].shape[0]
            pct_entregas_largas = round((entregas_largas / len(df)) * 100, 2)
            
            if pct_entregas_largas > 10:
                conclusiones.append(f"El {pct_entregas_largas:.1f}% de las entregas toman más de una hora, lo que podría estar afectando la eficiencia logística.")
        except Exception:
            pass
    
    # Correlación entre día programado y verificación
    if 'entrega_en_dia_programado' in df.columns and 'alimentos_debidamente_entregados' in df.columns and pct_ninguno > 5:
        conclusiones.append(f"El {pct_ninguno:.1f}% de las entregas no cumplen con ninguno de los criterios (ni día programado ni verificación), lo que sugiere problemas sistemáticos en el proceso de entrega.")
    
    # Mostrar conclusiones con componentes nativos de Streamlit
    if conclusiones:
        st.subheader("Principales Hallazgos")
        for conclusion in conclusiones:
            st.markdown(f"- {conclusion}")
    
    # Generar recomendaciones
    recomendaciones = []
    
    if pct_dia_programado < 90:
        recomendaciones.append("Implementar un sistema de seguimiento en tiempo real para monitorear el cumplimiento de las rutas programadas.")
    
    if pct_alimentos_verificados < 95:
        recomendaciones.append("Fortalecer los protocolos de entrega y verificación, posiblemente con herramientas digitales que agilicen el conteo y pesaje.")
    
    if 'tiempo_de _entrega_de_alimentos' in df.columns:
        try:
            entregas_largas = df[df['tiempo_de _entrega_de_alimentos'] == 'Más de una hora'].shape[0]
            pct_entregas_largas = round((entregas_largas / len(df)) * 100, 2)
            
            if pct_entregas_largas > 10:
                recomendaciones.append("Analizar las causas de demora en las entregas y proponer mejoras en los procedimientos para reducir los tiempos.")
        except Exception:
            pass
    
    if pct_dia_programado < 85 and pct_alimentos_verificados < 85:
        recomendaciones.append("Desarrollar un programa integral de capacitación para el personal involucrado en el proceso de entrega y verificación de alimentos.")
    
    if 'entrega_en_dia_programado' in df.columns and 'alimentos_debidamente_entregados' in df.columns and pct_ninguno > 10:
        recomendaciones.append("Realizar auditorías periódicas de todo el proceso de entrega para identificar y corregir los puntos críticos que están generando incumplimientos.")
    
    # Mostrar recomendaciones con componentes nativos de Streamlit
    if recomendaciones:
        st.subheader("Recomendaciones")
        for recomendacion in recomendaciones:
            st.markdown(f"- {recomendacion}")
    
    # Mostrar información adicional
    st.markdown("""
        <div class="success-box">
            <p><strong>Nota:</strong> El análisis de cumplimiento es crucial para asegurar que los comedores comunitarios
            reciban los insumos de manera oportuna y en las condiciones adecuadas. Un alto nivel de cumplimiento
            contribuye directamente a la eficiencia del programa y a la satisfacción de los beneficiarios.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()