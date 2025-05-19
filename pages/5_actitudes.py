import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data_from_sheets

# Configuración de la página
st.set_page_config(page_title="Condiciones Actitudinales", page_icon="😊", layout="wide")

# Estilos CSS mínimos
st.markdown("""
<style>
    .page-title {font-size: 2.3rem; font-weight: bold; color: #2E7D32; text-align: center; margin-bottom: 1.5rem; border-bottom: 2px solid #E0E0E0;}
    .section-header {font-size: 1.5rem; color: #388E3C; margin: 2rem 0 1rem 0; border-bottom: 1px solid #E0E0E0;}
    .metric-card {background-color: #F9FAFB; border-radius: 8px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; height: 100%;}
    .metric-title {font-size: 1.1rem; font-weight: 600; color: #4B5563; margin-bottom: 0.5rem;}
    .metric-value {font-size: 2.5rem; font-weight: bold;}
    .metric-good {color: #10B981;} .metric-warning {color: #F59E0B;} .metric-bad {color: #EF4444;}
    .metric-description {font-size: 0.9rem; color: #6B7280; margin-top: 0.5rem;}
    .info-box {background-color: #F0FDF4; border-left: 4px solid #10B981; padding: 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0;}
    .alert-box {background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0;}
    .tip-box {background-color: #ECFDF5; border-radius: 8px; padding: 1rem; margin: 1rem 0; border: 1px solid #D1FAE5;}
    .comparison-title {font-size: 1.2rem; font-weight: 600; color: #4B5563; margin-top: 1rem; margin-bottom: 0.5rem; text-align: center;}
    .person-emoji {font-size: 2rem; text-align: center; margin-bottom: 0.5rem;}
</style>
""", unsafe_allow_html=True)

# Obtener datos
def get_data():
    return st.session_state.get('filtered_df', load_data_from_sheets())

# Calcular porcentaje positivo
def calcular_porcentaje(df, columna):
    if columna not in df.columns or df.empty: return 0
    return round((df[columna].sum() / len(df)) * 100, 2)

# Crear métrica con formato
def crear_metrica_html(titulo, valor, descripcion=None, umbral_bueno=90, umbral_medio=70, icono=None):
    clase_color = "metric-good" if valor >= umbral_bueno else "metric-warning" if valor >= umbral_medio else "metric-bad"
    html = f"""<div class="metric-card">{f'<div class="person-emoji">{icono}</div>' if icono else ''}
        <div class="metric-title">{titulo}</div><div class="metric-value {clase_color}">{valor}%</div>
        {f'<div class="metric-description">{descripcion}</div>' if descripcion else ''}</div>"""
    return html

# Crear gráfico de barras
def crear_grafico_barras(df, columna, titulo, color_positivo="#4CAF50", color_negativo="#EF4444"):
    conteo = df[columna].value_counts().reset_index()
    conteo.columns = ['Valor', 'Conteo']
    conteo['Porcentaje'] = round(conteo['Conteo'] / conteo['Conteo'].sum() * 100, 2)
    conteo['Respuesta'] = conteo['Valor'].map({1: 'Sí', 0: 'No'})
    
    fig = px.bar(conteo, x='Respuesta', y='Porcentaje', text=conteo['Porcentaje'].apply(lambda x: f'{x}%'),
        color='Respuesta', color_discrete_map={'Sí': color_positivo, 'No': color_negativo}, title=titulo)
    fig.update_layout(xaxis_title='', yaxis_title='Porcentaje (%)', yaxis_range=[0, 100])
    return fig

# Crear gráfico de radar
def crear_grafico_radar(df, columnas, labels=None):
    if not all(col in df.columns for col in columnas): return None
    valores = [calcular_porcentaje(df, col) for col in columnas]
    if not labels: labels = [col.replace('_', ' ').title() for col in columnas]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=valores, theta=labels, fill='toself', 
        line_color='rgb(0, 153, 76)', fillcolor='rgba(0, 153, 76, 0.5)', name='Indicadores Actitudinales'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    return fig

# Crear análisis por gestor
def crear_comparativa_gestores(df, columnas):
    if 'Gestor_principal' not in df.columns or df.empty: return None
    columnas_existentes = [col for col in columnas if col in df.columns]
    if not columnas_existentes: return None
    
    resultados = pd.DataFrame()
    for col in columnas_existentes:
        temp = df.groupby('Gestor_principal')[col].mean().reset_index()
        temp[col] = temp[col] * 100
        if resultados.empty: resultados = temp
        else: resultados = resultados.merge(temp, on='Gestor_principal')
    
    resultados['promedio_general'] = resultados[columnas_existentes].mean(axis=1)
    resultados = resultados.sort_values(by='promedio_general', ascending=False)
    
    if len(resultados) > 20:
        resultados = pd.concat([resultados.head(10), resultados.tail(10)])
    
    fig = px.bar(resultados, x='Gestor_principal', y='promedio_general',
        text=resultados['promedio_general'].apply(lambda x: f'{x:.1f}%'),
        title='Valoración Actitudinal por Gestor Principal',
        color='promedio_general', color_continuous_scale='RdYlGn')
    fig.update_layout(xaxis_title='Gestor Principal', yaxis_title='Valoración Promedio (%)', yaxis_range=[0, 100])
    
    return fig, resultados

def main():
    # Título y descripción
    st.markdown('<h1 class="page-title">Análisis de Condiciones Actitudinales</h1>', unsafe_allow_html=True)
    
    # Cargar datos
    df = get_data()
    
    # Descripción
    st.markdown("""<div class="info-box"><p>Esta sección analiza las condiciones actitudinales de las personas involucradas en el proceso
        de entrega y recepción de insumos alimentarios. Se evalúa la actitud del conductor, auxiliar y
        gestora del comedor, así como la disposición para recibir los mercados, la comunicación efectiva
        y la resolución de inconvenientes.</p></div>""", unsafe_allow_html=True)
    
    # Verificar datos
    if df.empty:
        st.error("No hay datos disponibles para analizar. Por favor, verifica la conexión con la fuente de datos.")
        return
    
    # Columnas a analizar
    columnas_actitudinales = [
        'actitud_conductor_respetuosa_colaborativa',
        'actitud_auxiliar_respetuosa_colaborativa',
        'actitud_gestora_respetuosa_colaborativa',
        'buena_disposicion_recibir_mercados',
        'comunicacion_efectiva',
        'resolucion_inconvenientes'
    ]
    
    # Verificar columnas
    columnas_existentes = [col for col in columnas_actitudinales if col in df.columns]
    if not columnas_existentes:
        st.error("No se encontraron las columnas de condiciones actitudinales en los datos.")
        return
    
    # Sección de Indicadores Clave
    st.markdown('<h2 class="section-header">Indicadores Clave de Condiciones Actitudinales</h2>', unsafe_allow_html=True)
    
    # Personal que realiza la entrega
    st.markdown('<h3 class="comparison-title">Personal que Realiza la Entrega</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if 'actitud_conductor_respetuosa_colaborativa' in df.columns:
            pct_actitud_conductor = calcular_porcentaje(df, 'actitud_conductor_respetuosa_colaborativa')
            st.markdown(crear_metrica_html("Actitud del Conductor", pct_actitud_conductor,
                "Porcentaje de entregas donde el conductor muestra actitud respetuosa y colaborativa", icono="🚚"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre la actitud del conductor")
    
    with col2:
        if 'actitud_auxiliar_respetuosa_colaborativa' in df.columns:
            pct_actitud_auxiliar = calcular_porcentaje(df, 'actitud_auxiliar_respetuosa_colaborativa')
            st.markdown(crear_metrica_html("Actitud del Auxiliar", pct_actitud_auxiliar,
                "Porcentaje de entregas donde el auxiliar muestra actitud respetuosa y colaborativa", icono="👷"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre la actitud del auxiliar")
    
    # Personal que recibe
    st.markdown('<h3 class="comparison-title">Personal que Recibe los Insumos</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if 'actitud_gestora_respetuosa_colaborativa' in df.columns:
            pct_actitud_gestora = calcular_porcentaje(df, 'actitud_gestora_respetuosa_colaborativa')
            st.markdown(crear_metrica_html("Actitud de la Gestora", pct_actitud_gestora,
                "Porcentaje de entregas donde la gestora muestra actitud respetuosa y colaborativa", icono="👩"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre la actitud de la gestora")
    
    with col2:
        if 'buena_disposicion_recibir_mercados' in df.columns:
            pct_disposicion_mercados = calcular_porcentaje(df, 'buena_disposicion_recibir_mercados')
            st.markdown(crear_metrica_html("Disposición para Recibir", pct_disposicion_mercados,
                "Porcentaje de entregas donde hay buena disposición para recibir, revisar y firmar", icono="📋"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre la disposición para recibir mercados")
    
    # Relación entre actores
    st.markdown('<h3 class="comparison-title">Relación entre Actores</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if 'comunicacion_efectiva' in df.columns:
            pct_comunicacion = calcular_porcentaje(df, 'comunicacion_efectiva')
            st.markdown(crear_metrica_html("Comunicación Efectiva", pct_comunicacion,
                "Porcentaje de entregas con comunicación efectiva entre el personal", icono="🗣️"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre comunicación efectiva")
    
    with col2:
        if 'resolucion_inconvenientes' in df.columns:
            pct_resolucion = calcular_porcentaje(df, 'resolucion_inconvenientes')
            st.markdown(crear_metrica_html("Resolución de Inconvenientes", pct_resolucion,
                "Porcentaje de entregas donde se resuelven adecuadamente los inconvenientes", icono="🔧"), 
                unsafe_allow_html=True)
        else:
            st.warning("No hay datos sobre resolución de inconvenientes")
    
    # Índice general
    if columnas_existentes:
        valores_promedio = [calcular_porcentaje(df, col) for col in columnas_existentes]
        indice_general = round(sum(valores_promedio) / len(valores_promedio), 2)
        color = "#10B981" if indice_general >= 90 else "#F59E0B" if indice_general >= 70 else "#EF4444"
        
        st.markdown(f"""<div style="text-align: center; margin: 2rem 0;">
            <h3>Índice General de Condiciones Actitudinales</h3>
            <div style="font-size: 3.5rem; font-weight: bold; color: {color};">{indice_general}%</div>
        </div>""", unsafe_allow_html=True)
    
    # Visualización de Radar
    st.markdown('<h2 class="section-header">Análisis Comparativo de Indicadores Actitudinales</h2>', unsafe_allow_html=True)
    
    if len(columnas_existentes) >= 3:
        labels_mapping = {
            'actitud_conductor_respetuosa_colaborativa': 'Conductor',
            'actitud_auxiliar_respetuosa_colaborativa': 'Auxiliar',
            'actitud_gestora_respetuosa_colaborativa': 'Gestora',
            'buena_disposicion_recibir_mercados': 'Disposición Recepción',
            'comunicacion_efectiva': 'Comunicación',
            'resolucion_inconvenientes': 'Resolución Problemas'
        }
        labels = [labels_mapping.get(col, col) for col in columnas_existentes]
        fig = crear_grafico_radar(df, columnas_existentes, labels)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No se pudo crear el gráfico radar con los datos disponibles.")
    
    # Análisis Detallado por Indicador
    st.markdown('<h2 class="section-header">Análisis Detallado por Indicador</h2>', unsafe_allow_html=True)
    
    # Actitud del Personal de Entrega
    if 'actitud_conductor_respetuosa_colaborativa' in df.columns or 'actitud_auxiliar_respetuosa_colaborativa' in df.columns:
        st.markdown('<h3 class="comparison-title">Actitud del Personal de Entrega</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if 'actitud_conductor_respetuosa_colaborativa' in df.columns:
                fig = crear_grafico_barras(df, 'actitud_conductor_respetuosa_colaborativa', 
                    'Actitud Respetuosa y Colaborativa del Conductor')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'actitud_auxiliar_respetuosa_colaborativa' in df.columns:
                fig = crear_grafico_barras(df, 'actitud_auxiliar_respetuosa_colaborativa', 
                    'Actitud Respetuosa y Colaborativa del Auxiliar')
                st.plotly_chart(fig, use_container_width=True)
    
    # Actitud del Personal de Recepción
    if 'actitud_gestora_respetuosa_colaborativa' in df.columns or 'buena_disposicion_recibir_mercados' in df.columns:
        st.markdown('<h3 class="comparison-title">Actitud del Personal de Recepción</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if 'actitud_gestora_respetuosa_colaborativa' in df.columns:
                fig = crear_grafico_barras(df, 'actitud_gestora_respetuosa_colaborativa', 
                    'Actitud Respetuosa y Colaborativa de la Gestora')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'buena_disposicion_recibir_mercados' in df.columns:
                fig = crear_grafico_barras(df, 'buena_disposicion_recibir_mercados', 
                    'Buena Disposición para Recibir Mercados')
                st.plotly_chart(fig, use_container_width=True)
    
    # Relación entre Actores
    if 'comunicacion_efectiva' in df.columns or 'resolucion_inconvenientes' in df.columns:
        st.markdown('<h3 class="comparison-title">Relación entre Actores</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            if 'comunicacion_efectiva' in df.columns:
                fig = crear_grafico_barras(df, 'comunicacion_efectiva', 
                    'Comunicación Efectiva entre los Actores')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'resolucion_inconvenientes' in df.columns:
                fig = crear_grafico_barras(df, 'resolucion_inconvenientes', 
                    'Resolución Adecuada de Inconvenientes')
                st.plotly_chart(fig, use_container_width=True)
    
    # Análisis por Gestor Principal
    if 'Gestor_principal' in df.columns and columnas_existentes:
        st.markdown('<h2 class="section-header">Análisis por Gestor Principal</h2>', unsafe_allow_html=True)
        resultado_gestores = crear_comparativa_gestores(df, columnas_existentes)
        
        if resultado_gestores:
            fig, df_gestores = resultado_gestores
            st.plotly_chart(fig, use_container_width=True)
            
            if len(df_gestores) > 1:
                mejor_gestor = df_gestores.iloc[0]
                peor_gestor = df_gestores.iloc[-1]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<div class="info-box">
                        <h3 style="margin-top: 0;">Gestor con Mejor Valoración</h3>
                        <p><strong>Nombre:</strong> {mejor_gestor['Gestor_principal']}</p>
                        <p><strong>Valoración:</strong> {mejor_gestor['promedio_general']:.2f}%</p>
                    </div>""", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""<div class="alert-box">
                        <h3 style="margin-top: 0;">Gestor con Oportunidades de Mejora</h3>
                        <p><strong>Nombre:</strong> {peor_gestor['Gestor_principal']}</p>
                        <p><strong>Valoración:</strong> {peor_gestor['promedio_general']:.2f}%</p>
                    </div>""", unsafe_allow_html=True)
        else:
            st.warning("No hay suficientes datos para realizar un análisis por gestor.")
    
    # Conclusiones y Recomendaciones
    st.markdown('<h2 class="section-header">Conclusiones y Recomendaciones</h2>', unsafe_allow_html=True)
    
    # Calcular indicadores clave para conclusiones
    pct_actitud_conductor = calcular_porcentaje(df, 'actitud_conductor_respetuosa_colaborativa') if 'actitud_conductor_respetuosa_colaborativa' in df.columns else 0
    pct_actitud_auxiliar = calcular_porcentaje(df, 'actitud_auxiliar_respetuosa_colaborativa') if 'actitud_auxiliar_respetuosa_colaborativa' in df.columns else 0
    pct_actitud_gestora = calcular_porcentaje(df, 'actitud_gestora_respetuosa_colaborativa') if 'actitud_gestora_respetuosa_colaborativa' in df.columns else 0
    pct_disposicion = calcular_porcentaje(df, 'buena_disposicion_recibir_mercados') if 'buena_disposicion_recibir_mercados' in df.columns else 0
    pct_comunicacion = calcular_porcentaje(df, 'comunicacion_efectiva') if 'comunicacion_efectiva' in df.columns else 0
    pct_resolucion = calcular_porcentaje(df, 'resolucion_inconvenientes') if 'resolucion_inconvenientes' in df.columns else 0
    
    # Generar conclusiones
    conclusiones = []
    if pct_actitud_conductor < 95 and 'actitud_conductor_respetuosa_colaborativa' in df.columns:
        conclusiones.append(f"En el {100-pct_actitud_conductor:.1f}% de las entregas, la actitud del conductor no es completamente respetuosa y colaborativa, lo que podría afectar la calidad del servicio.")
    if pct_actitud_auxiliar < 95 and 'actitud_auxiliar_respetuosa_colaborativa' in df.columns:
        conclusiones.append(f"En el {100-pct_actitud_auxiliar:.1f}% de las entregas, la actitud del auxiliar no es completamente respetuosa y colaborativa, lo que podría afectar la manipulación de los alimentos.")
    if pct_actitud_gestora < 95 and 'actitud_gestora_respetuosa_colaborativa' in df.columns:
        conclusiones.append(f"En el {100-pct_actitud_gestora:.1f}% de las entregas, la actitud de la gestora no es completamente respetuosa y colaborativa, lo que podría generar un ambiente de trabajo no ideal.")
    if pct_disposicion < 90 and 'buena_disposicion_recibir_mercados' in df.columns:
        conclusiones.append(f"En el {100-pct_disposicion:.1f}% de las entregas, no hay una buena disposición para recibir, revisar y firmar, lo que podría generar demoras y errores en el proceso.")
    if pct_comunicacion < 90 and 'comunicacion_efectiva' in df.columns:
        conclusiones.append(f"En el {100-pct_comunicacion:.1f}% de las entregas, la comunicación no es completamente efectiva entre los actores, lo que podría dificultar el proceso de entrega.")
    if pct_resolucion < 85 and 'resolucion_inconvenientes' in df.columns:
        conclusiones.append(f"En el {100-pct_resolucion:.1f}% de las entregas, no se resuelven adecuadamente los inconvenientes, lo que podría generar problemas recurrentes.")
    
    # Análisis por gestor
    if 'Gestor_principal' in df.columns and columnas_existentes:
        resultado_gestores = crear_comparativa_gestores(df, columnas_existentes)
        if resultado_gestores:
            _, df_gestores = resultado_gestores
            umbral_bajo = 80
            gestores_bajos = df_gestores[df_gestores['promedio_general'] < umbral_bajo]
            if not gestores_bajos.empty:
                pct_gestores_bajos = round((len(gestores_bajos) / len(df_gestores)) * 100, 2)
                conclusiones.append(f"El {pct_gestores_bajos:.1f}% de los gestores tiene una valoración actitudinal por debajo del {umbral_bajo}%, lo que sugiere la necesidad de intervención y capacitación.")
    
    # Mostrar conclusiones
    if conclusiones:
        st.markdown("<h3>Principales Hallazgos</h3>", unsafe_allow_html=True)
        for conclusion in conclusiones:
            st.markdown(f"- {conclusion}")
    else:
        st.markdown("""<div class="info-box">
            <h3 style="margin-top: 0;">Excelente Desempeño Actitudinal</h3>
            <p>No se han identificado problemas significativos en las condiciones actitudinales. 
            ¡Felicitaciones por mantener altos estándares de servicio y colaboración!</p>
        </div>""", unsafe_allow_html=True)
    
    # Generar recomendaciones
    recomendaciones = []
    if pct_actitud_conductor < 95 or pct_actitud_auxiliar < 95:
        recomendaciones.append("Implementar capacitaciones periódicas para el personal de entrega sobre servicio al cliente y trabajo en equipo.")
    if pct_actitud_gestora < 95 or pct_disposicion < 90:
        recomendaciones.append("Realizar talleres de sensibilización para las gestoras sobre la importancia de una actitud positiva y colaborativa en el proceso de recepción.")
    if pct_comunicacion < 90:
        recomendaciones.append("Desarrollar protocolos claros de comunicación entre el personal de entrega y recepción, incluyendo un glosario de términos comunes.")
    if pct_resolucion < 85:
        recomendaciones.append("Implementar un sistema de registro y seguimiento de inconvenientes para asegurar su adecuada resolución y prevenir su recurrencia.")
    
    # Recomendaciones específicas por gestor
    if 'Gestor_principal' in df.columns and columnas_existentes:
        resultado_gestores = crear_comparativa_gestores(df, columnas_existentes)
        if resultado_gestores:
            _, df_gestores = resultado_gestores
            umbral_bajo = 80
            gestores_bajos = df_gestores[df_gestores['promedio_general'] < umbral_bajo]
            if not gestores_bajos.empty and len(gestores_bajos) <= 3:
                nombres_bajos = ", ".join(gestores_bajos['Gestor_principal'].tolist())
                recomendaciones.append(f"Proporcionar coaching personalizado a los gestores: {nombres_bajos}, para mejorar sus habilidades interpersonales y de servicio.")
            elif not gestores_bajos.empty:
                recomendaciones.append(f"Diseñar un programa de mejora para los {len(gestores_bajos)} gestores con valoraciones por debajo del {umbral_bajo}%.")
    
    # Recomendaciones generales
    if indice_general < 90 and columnas_existentes:
        recomendaciones.append("Organizar eventos de integración entre personal de entrega y personal de recepción para fortalecer relaciones y mejorar la comunicación.")
        recomendaciones.append("Implementar un sistema de reconocimiento para destacar actitudes positivas y ejemplares en el proceso de entrega y recepción.")
    
    # Mostrar recomendaciones
    if recomendaciones:
        st.markdown("<h3>Recomendaciones</h3>", unsafe_allow_html=True)
        for recomendacion in recomendaciones:
            st.markdown(f"- {recomendacion}")
   
   
if __name__ == "__main__":
    main()