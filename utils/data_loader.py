import pandas as pd
import numpy as np
import os
import streamlit as st
from datetime import datetime

# Importaciones para Google Sheets
try:
    from oauth2client.service_account import ServiceAccountCredentials
    import gspread
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# Decorador de cache para la función de carga de datos
@st.cache_data(ttl=600) # Cache por 10 minutos
def load_data_from_sheets(spreadsheet_name="VERCOAL", 
                          worksheet_name="VERCOAL",
                          spreadsheet_id="1NybdSsOvzcIt5m_jG34spuMKWQOOoYwstrhNM6Zwhfw", # NUEVO: ID de la hoja de cálculo
                          credentials_path=None):
    """
    Carga datos desde una hoja de Google Sheets.
    Intenta abrir por ID si se proporciona, de lo contrario por nombre.
    Prioriza credenciales en este orden:
    1. Variable de entorno GOOGLE_APPLICATION_CREDENTIALS.
    2. Argumento credentials_path.
    3. Archivo local 'credentials.json'.
    4. Streamlit Secrets (st.secrets).
    Si todo falla, devuelve un DataFrame vacío.
    
    Args:
        spreadsheet_name (str): Nombre de la hoja de cálculo (usado si spreadsheet_id no se proporciona o falla).
        worksheet_name (str): Nombre de la pestaña específica de la hoja.
        spreadsheet_id (str, optional): ID único de la hoja de cálculo de Google Sheets.
        credentials_path (str, optional): Ruta al archivo de credenciales JSON.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados o un DataFrame vacío si falla.
    """
    if not GSPREAD_AVAILABLE:
        st.sidebar.error("Bibliotecas de Google Sheets no disponibles. No se pueden cargar datos.")
        return pd.DataFrame()

    credentials = None
    creds_source = "ninguna fuente conocida"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Lógica de carga de credenciales (sin cambios respecto a la versión anterior)
    # 1. Intentar con la variable de entorno
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        try:
            credentials_file = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            if os.path.exists(credentials_file):
                credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
                creds_source = "Variables de Entorno (GOOGLE_APPLICATION_CREDENTIALS)"
            else:
                st.sidebar.warning(f"Archivo de credenciales de entorno no encontrado en: {credentials_file}")
        except Exception as e:
            st.sidebar.warning(f"Error al cargar credenciales desde variable de entorno: {e}")
            credentials = None

    # 2. Intentar con la ruta de credenciales proporcionada
    if not credentials and credentials_path:
        if os.path.exists(credentials_path):
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
                creds_source = f"Ruta de Archivo Proporcionada ({credentials_path})"
            except Exception as e:
                st.sidebar.warning(f"Error al cargar credenciales desde ruta '{credentials_path}': {e}")
                credentials = None
        else:
            st.sidebar.warning(f"Archivo de credenciales no encontrado en la ruta especificada: {credentials_path}")

    # 3. Intentar con el archivo local 'credentials.json'
    if not credentials:
        local_credentials_file = 'credentials.json'
        if os.path.exists(local_credentials_file):
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(local_credentials_file, scope)
                creds_source = f"Archivo Local ({local_credentials_file})"
            except Exception as e:
                st.sidebar.warning(f"Error al cargar credenciales desde '{local_credentials_file}' local: {e}")
                credentials = None

    # 4. Intentar con Streamlit Secrets (más útil para despliegues)
    if not credentials:
        try:
            gcp_creds_dict = st.secrets.get("gcp_service_account")
            if gcp_creds_dict: 
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds_dict, scope)
                creds_source = "Streamlit Secrets (gcp_service_account)"
        except Exception as e: 
            st.sidebar.warning(f"No se pudieron usar Streamlit Secrets o no están configurados: {e}")
            credentials = None

    if not credentials:
        st.sidebar.error("No se pudieron cargar las credenciales de Google Sheets desde ninguna fuente.")
        st.sidebar.warning("La aplicación no podrá mostrar datos.")
        return pd.DataFrame()

    try:
        st.sidebar.info(f"Usando credenciales de: {creds_source}")
        client = gspread.authorize(credentials)
        spreadsheet = None
        method_used = ""

        # Intentar abrir por ID primero si se proporciona
        if spreadsheet_id:
            try:
                spreadsheet = client.open_by_key(spreadsheet_id)
                method_used = f"ID ({spreadsheet_id})"
                st.sidebar.info(f"Intentando abrir hoja de cálculo por ID: {spreadsheet_id}")
            except gspread.exceptions.APIError as e_id:
                st.sidebar.warning(f"Error al abrir por ID '{spreadsheet_id}': {e_id}. Intentando por nombre...")
                spreadsheet = None # Asegurar que spreadsheet es None para intentar por nombre
            except Exception as e_id_other: # Capturar otras posibles excepciones
                st.sidebar.warning(f"Error inesperado al abrir por ID '{spreadsheet_id}': {e_id_other}. Intentando por nombre...")
                spreadsheet = None


        # Si falla abrir por ID o no se proporcionó ID, intentar por nombre
        if not spreadsheet and spreadsheet_name:
            try:
                st.sidebar.info(f"Intentando abrir hoja de cálculo por nombre: {spreadsheet_name}")
                spreadsheet = client.open(spreadsheet_name)
                method_used = f"nombre ({spreadsheet_name})"
            except gspread.exceptions.SpreadsheetNotFound as e_name:
                 st.sidebar.error(f"⚠️ Error: Hoja de cálculo no encontrada por nombre '{spreadsheet_name}'.")
                 st.sidebar.warning("La aplicación no podrá mostrar datos.")
                 return pd.DataFrame()
            except Exception as e_name_other:
                 st.sidebar.error(f"⚠️ Error al abrir por nombre '{spreadsheet_name}': {str(e_name_other)}")
                 st.sidebar.warning("La aplicación no podrá mostrar datos.")
                 return pd.DataFrame()


        if not spreadsheet:
            st.sidebar.error("No se pudo abrir la hoja de cálculo ni por ID ni por nombre.")
            return pd.DataFrame()

        st.sidebar.info(f"Hoja de cálculo abierta exitosamente usando: {method_used}")
        worksheet = spreadsheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()

        if not data:
            st.sidebar.warning(f"No se encontraron datos en la hoja '{worksheet_name}' del libro '{spreadsheet.title}'.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = preprocess_data(df)
        
        if df.empty and data:
            st.sidebar.warning("Los datos se cargaron pero resultaron vacíos después del preprocesamiento.")
        elif not df.empty:
            st.sidebar.success("✅ Datos cargados y preprocesados correctamente desde Google Sheets.")
        return df

    except gspread.exceptions.WorksheetNotFound:
        # Este error es específico de la pestaña/worksheet
        title_to_show = spreadsheet.title if spreadsheet else (spreadsheet_id or spreadsheet_name)
        st.sidebar.error(f"⚠️ Error: Pestaña '{worksheet_name}' no encontrada en la hoja de cálculo '{title_to_show}'.")
        st.sidebar.warning("La aplicación no podrá mostrar datos.")
        return pd.DataFrame()
    except Exception as e_general: 
        st.sidebar.error(f"⚠️ Error general al conectar/leer Google Sheets (usando {creds_source}): {str(e_general)}")
        st.sidebar.warning("La aplicación no podrá mostrar datos.")
        return pd.DataFrame()


def preprocess_data(df):
    """
    Preprocesa los datos para asegurar tipos correctos y transformaciones necesarias.
    Maneja un DataFrame vacío de entrada.
    
    Args:
        df (pandas.DataFrame): DataFrame a preprocesar.
    
    Returns:
        pandas.DataFrame: DataFrame preprocesado.
    """
    if df.empty:
        return df

    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    boolean_columns = [
        'comedor_facil_Acceso', 'vehiculo_puede_llegar_a_sitio', 
        'trasbordo', 'ingreso_apoyo_comunidad', 'demora_entregas',
        'inocuidad_comprometida', 'entrega_en_dia_programado',
        'alimentos_debidamente_entregados', 'vehiculo_limpio_buen_estado',
        'alimentos_de_calidad_cantidad', 'contenedores_para_cada_tipoalimento',
        'actitud_conductor_respetuosa_colaborativa', 'actitud_auxiliar_respetuosa_colaborativa',
        'actitud_gestora_respetuosa_colaborativa', 'buena_disposicion_recibir_mercados',
        'comunicacion_efectiva', 'resolucion_inconvenientes'
    ]
    
    for col in boolean_columns:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.upper().map({
                        'SI': 1, 'NO': 0, 'S': 1, 'N': 0, 
                        'TRUE': 1, 'FALSE': 0, 'VERDADERO': 1, 'FALSO': 0,
                        'NAN': 0, '': 0 
                    })
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    monetary_columns = ['valor_trasbordo', 'valor_apoyo']
    for col in monetary_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

# La función generate_sample_data() ha sido eliminada.
