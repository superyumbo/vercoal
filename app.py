import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.data_loader import load_data_from_sheets 

# Configuración inicial
st.set_page_config(page_title="Verificación de Insumos Alimentarios", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS compactados
st.markdown("""<style>.main-header{font-size:2.5rem;color:#2C3E50;text-align:center;margin-bottom:1rem;}.sub-header{font-size:1.8rem;color:#34495E;margin-top:2rem;margin-bottom:1rem;}.metric-card{background-color:#F8F9FA;border-radius:5px;padding:1rem;box-shadow:0 0.15rem 1.75rem 0 rgba(58,59,69,0.15);}.metric-value{font-size:2rem;font-weight:bold;color:#1E88E5;}.metric-label{font-size:1rem;color:#34495E;}.highlight-text{background-color:#FFF9C4;padding:0.2rem 0.5rem;border-radius:3px;}.footer{text-align:center;margin-top:3rem;padding:1rem;font-size:0.8rem;color:#7F8C8D;}</style>""", unsafe_allow_html=True)

# Función para calcular porcentajes
def calcular_porcentaje(df, columna):
    if columna not in df.columns or df.empty: return 0.0
    if not pd.api.types.is_numeric_dtype(df[columna]):
        try:
            if df[columna].dtype == 'object': df[columna] = df[columna].str.upper().map({'SI': 1, 'NO': 0, 'S': 1, 'N': 0})
            df[columna] = pd.to_numeric(df[columna], errors='coerce').fillna(0)
        except Exception: return 0.0
    return round((df[columna].sum() / len(df)) * 100, 2)

# Filtros globales
def get_global_filters(df):
    st.sidebar.title("Filtros")
    df_filtrado = df.copy()

    # Filtro de fecha
    if 'fecha' in df_filtrado.columns and not df_filtrado['fecha'].dropna().empty:
        try:
            if not pd.api.types.is_datetime64_any_dtype(df_filtrado['fecha']):
                df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'], errors='coerce')
            df_filtrado_fechas_validas = df_filtrado.dropna(subset=['fecha'])
            if not df_filtrado_fechas_validas.empty:
                min_date, max_date = df_filtrado_fechas_validas['fecha'].min().date(), df_filtrado_fechas_validas['fecha'].max().date()
                date_range = st.sidebar.date_input("Rango de fechas", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="global_date_filter")
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    start_datetime, end_datetime = pd.to_datetime(start_date), pd.to_datetime(end_date) + pd.Timedelta(days=1)
                    df_filtrado = df_filtrado[(df_filtrado['fecha'] >= start_datetime) & (df_filtrado['fecha'] < end_datetime)]
            else: st.sidebar.warning("No hay fechas válidas para filtrar.")
        except Exception as e: st.sidebar.warning(f"Error al aplicar filtro de fechas: {e}")
    
    # Filtro de comuna
    if 'comuna' in df_filtrado.columns and not df_filtrado['comuna'].dropna().empty:
        comunas_validas = sorted(df_filtrado['comuna'].dropna().unique().tolist())
        if comunas_validas:
            comunas = ['Todas'] + comunas_validas
            comuna_seleccionada = st.sidebar.selectbox("Comuna", comunas, key="global_comuna_filter")
            if comuna_seleccionada != 'Todas': df_filtrado = df_filtrado[df_filtrado['comuna'] == comuna_seleccionada]
    
    # Filtro de ruta
    if 'ruta' in df_filtrado.columns and not df_filtrado['ruta'].dropna().empty:
        rutas_validas = sorted(df_filtrado['ruta'].dropna().unique().tolist())
        if rutas_validas:
            rutas = ['Todas'] + rutas_validas
            ruta_seleccionada = st.sidebar.selectbox("Ruta", rutas, key="global_ruta_filter")
            if ruta_seleccionada != 'Todas': df_filtrado = df_filtrado[df_filtrado['ruta'] == ruta_seleccionada]
    
    # Filtro de nodo
    if 'nodo' in df_filtrado.columns and not df_filtrado['nodo'].dropna().empty:
        nodos_validos = sorted(df_filtrado['nodo'].dropna().unique().tolist())
        if nodos_validos:
            nodos = ['Todos'] + nodos_validos
            nodo_seleccionado = st.sidebar.selectbox("Nodo", nodos, key="global_nodo_filter")
            if nodo_seleccionado != 'Todos': df_filtrado = df_filtrado[df_filtrado['nodo'] == nodo_seleccionado]
    
    return df_filtrado

# Página principal
def main():
    # Header
    st.markdown('<h1 class="main-header">Verificación de Transporte de Insumos Alimentarios</h1>', unsafe_allow_html=True)
    
    # Cargar y filtrar datos
    df_original = load_data_from_sheets() 
    if df_original is None or df_original.empty:
        st.error("No se pudieron cargar los datos. Por favor, verifique la fuente de datos o la conexión.")
        return
    filtered_df = get_global_filters(df_original.copy())
    st.session_state['filtered_df'] = filtered_df
    
    # KPIs principales
    st.markdown('<h2 class="sub-header">Indicadores Clave de Desempeño</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    # Indicadores de accesibilidad
    with col1:
        accesibilidad_cols = ['comedor_facil_Acceso', 'vehiculo_puede_llegar_a_sitio']
        valid_accesibilidad_cols = [col for col in accesibilidad_cols if col in filtered_df.columns]
        pct_accesibilidad = sum(calcular_porcentaje(filtered_df, col) for col in valid_accesibilidad_cols) / len(valid_accesibilidad_cols) if valid_accesibilidad_cols else 0.0
        st.markdown(f"""<div class="metric-card"><p class="metric-label">Accesibilidad</p><p class="metric-value">{pct_accesibilidad:.1f}%</p></div>""", unsafe_allow_html=True)
    
    # Indicadores de cumplimiento
    with col2:
        cumplimiento_cols = ['entrega_en_dia_programado', 'alimentos_debidamente_entregados']
        valid_cumplimiento_cols = [col for col in cumplimiento_cols if col in filtered_df.columns]
        pct_cumplimiento = sum(calcular_porcentaje(filtered_df, col) for col in valid_cumplimiento_cols) / len(valid_cumplimiento_cols) if valid_cumplimiento_cols else 0.0
        st.markdown(f"""<div class="metric-card"><p class="metric-label">Cumplimiento</p><p class="metric-value">{pct_cumplimiento:.1f}%</p></div>""", unsafe_allow_html=True)
    
    # Indicadores de calidad del vehículo
    with col3:
        vehiculo_cols = ['vehiculo_limpio_buen_estado', 'alimentos_de_calidad_cantidad', 'contenedores_para_cada_tipoalimento']
        valid_vehiculo_cols = [col for col in vehiculo_cols if col in filtered_df.columns]
        pct_vehiculo = sum(calcular_porcentaje(filtered_df, col) for col in valid_vehiculo_cols) / len(valid_vehiculo_cols) if valid_vehiculo_cols else 0.0
        st.markdown(f"""<div class="metric-card"><p class="metric-label">Calidad Vehículo</p><p class="metric-value">{pct_vehiculo:.1f}%</p></div>""", unsafe_allow_html=True)
    
    # Indicadores actitudinales
    with col4:
        actitud_cols = ['actitud_conductor_respetuosa_colaborativa', 'actitud_auxiliar_respetuosa_colaborativa', 'actitud_gestora_respetuosa_colaborativa', 'buena_disposicion_recibir_mercados', 'comunicacion_efectiva', 'resolucion_inconvenientes']
        valid_actitud_cols = [col for col in actitud_cols if col in filtered_df.columns]
        pct_actitud = sum(calcular_porcentaje(filtered_df, col) for col in valid_actitud_cols) / len(valid_actitud_cols) if valid_actitud_cols else 0.0
        st.markdown(f"""<div class="metric-card"><p class="metric-label">Actitud del Personal</p><p class="metric-value">{pct_actitud:.1f}%</p></div>""", unsafe_allow_html=True)
    
    # Descripción general
    st.markdown("""
    ## Bienvenido al Dashboard de Verificación de Insumos Alimentarios
    
    Este panel de control le permite analizar la información recopilada durante las verificaciones
    de transporte de insumos alimentarios a los comedores comunitarios.
    
    Utilice el **menú lateral izquierdo** para navegar entre las diferentes secciones de análisis:
    
    - **Inicio**: Resumen general y KPIs principales (esta página)
    - **Accesibilidad**: Análisis de accesibilidad a los comedores
    - **Cumplimiento**: Análisis del cumplimiento en la entrega
    - **Condiciones Vehículo**: Análisis de las condiciones del vehículo
    - **Actitudes**: Análisis de las condiciones actitudinales
    - **Análisis General**: Análisis integrado de todos los aspectos
    
    Utilice los **filtros** en la barra lateral para personalizar su análisis por fecha, 
    comuna, ruta o nodo.
    """)
    
    # Información adicional
    st.markdown("""
    ### Información del Proyecto
    
    Este dashboard permite visualizar y analizar los datos recopilados durante la verificación
    del transporte de insumos alimentarios a los comedores comunitarios.
    
    Los datos se actualizan automáticamente desde Google Sheets cada 10 minutos (si la conexión es exitosa).
    """)
    
    # Pie de página
    st.markdown('<div class="footer">Verificación de Insumos Alimentarios - v1.0 © 2025</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()