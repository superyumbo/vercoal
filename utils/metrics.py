import pandas as pd
import numpy as np
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

def calcular_indice_grupo(df, columnas, pesos=None):
    """
    Calcula un índice compuesto para un grupo de columnas.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columnas (list): Lista de nombres de columnas a incluir en el índice.
        pesos (list, optional): Lista de pesos para cada columna. Si no se proporciona,
                               se asigna el mismo peso a todas las columnas.
    
    Returns:
        float: Índice compuesto (valor entre 0 y 100).
    """
    # Verificar que existen las columnas
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if not columnas_existentes:
        return 0
    
    # Si no se proporcionan pesos, asignar el mismo peso a todas las columnas
    if pesos is None:
        pesos = [1] * len(columnas_existentes)
    else:
        # Asegurar que hay un peso para cada columna existente
        pesos = pesos[:len(columnas_existentes)]
        if len(pesos) < len(columnas_existentes):
            pesos.extend([1] * (len(columnas_existentes) - len(pesos)))
    
    # Normalizar pesos para que sumen 1
    suma_pesos = sum(pesos)
    pesos_norm = [p / suma_pesos for p in pesos]
    
    # Calcular índice ponderado
    valores = [calcular_porcentaje(df, col) for col in columnas_existentes]
    indice = sum(v * p for v, p in zip(valores, pesos_norm))
    
    return round(indice, 2)

def calcular_indice_accesibilidad(df):
    """
    Calcula el índice de accesibilidad.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
    
    Returns:
        float: Índice de accesibilidad (valor entre 0 y 100).
    """
    columnas = [
        'comedor_facil_Acceso',
        'vehiculo_puede_llegar_a_sitio'
    ]
    
    # Columnas negativas (se invierte su valor)
    columnas_neg = [
        'trasbordo',
        'ingreso_apoyo_comunidad',
        'demora_entregas',
        'inocuidad_comprometida'
    ]
    
    # Verificar qué columnas existen
    columnas_pos_existentes = [col for col in columnas if col in df.columns]
    columnas_neg_existentes = [col for col in columnas_neg if col in df.columns]
    
    if not columnas_pos_existentes and not columnas_neg_existentes:
        return 0
    
    # Calcular indicadores positivos
    if columnas_pos_existentes:
        indice_pos = calcular_indice_grupo(df, columnas_pos_existentes)
    else:
        indice_pos = 0
    
    # Calcular indicadores negativos (invertidos)
    if columnas_neg_existentes:
        # Para los indicadores negativos, tomamos el complemento (100 - valor)
        df_neg_inv = df.copy()
        for col in columnas_neg_existentes:
            df_neg_inv[col] = 1 - df_neg_inv[col]  # Invertir 0/1
        
        indice_neg = calcular_indice_grupo(df_neg_inv, columnas_neg_existentes)
    else:
        indice_neg = 0
    
    # Calcular promedio ponderado (damos más peso a los indicadores positivos si ambos existen)
    if columnas_pos_existentes and columnas_neg_existentes:
        indice = (indice_pos * 0.6) + (indice_neg * 0.4)
    elif columnas_pos_existentes:
        indice = indice_pos
    else:
        indice = indice_neg
    
    return round(indice, 2)

def calcular_indice_cumplimiento(df):
    """
    Calcula el índice de cumplimiento en la entrega.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
    
    Returns:
        float: Índice de cumplimiento (valor entre 0 y 100).
    """
    columnas = [
        'entrega_en_dia_programado',
        'alimentos_debidamente_entregados'
    ]
    
    # Verificar qué columnas existen
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if not columnas_existentes:
        return 0
    
    # Pesos: damos más importancia a la entrega en día programado
    pesos = [0.6, 0.4]
    
    return calcular_indice_grupo(df, columnas_existentes, pesos)

def calcular_indice_vehiculo(df):
    """
    Calcula el índice de condiciones del vehículo.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
    
    Returns:
        float: Índice de condiciones del vehículo (valor entre 0 y 100).
    """
    columnas = [
        'vehiculo_limpio_buen_estado',
        'alimentos_de_calidad_cantidad',
        'contenedores_para_cada_tipoalimento'
    ]
    
    # Verificar qué columnas existen
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if not columnas_existentes:
        return 0
    
    # Pesos: damos más importancia a la calidad de los alimentos
    pesos = [0.3, 0.4, 0.3]
    
    return calcular_indice_grupo(df, columnas_existentes, pesos)

def calcular_indice_actitudes(df):
    """
    Calcula el índice de condiciones actitudinales.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
    
    Returns:
        float: Índice de condiciones actitudinales (valor entre 0 y 100).
    """
    columnas = [
        'actitud_conductor_respetuosa_colaborativa',
        'actitud_auxiliar_respetuosa_colaborativa',
        'actitud_gestora_respetuosa_colaborativa',
        'buena_disposicion_recibir_mercados',
        'comunicacion_efectiva',
        'resolucion_inconvenientes'
    ]
    
    # Verificar qué columnas existen
    columnas_existentes = [col for col in columnas if col in df.columns]
    
    if not columnas_existentes:
        return 0
    
    # Pesos: todos iguales por defecto
    return calcular_indice_grupo(df, columnas_existentes)

def calcular_indice_general(df):
    """
    Calcula el índice general de calidad del servicio.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
    
    Returns:
        float: Índice general (valor entre 0 y 100).
    """
    # Calcular índices por grupo
    indice_accesibilidad = calcular_indice_accesibilidad(df)
    indice_cumplimiento = calcular_indice_cumplimiento(df)
    indice_vehiculo = calcular_indice_vehiculo(df)
    indice_actitudes = calcular_indice_actitudes(df)
    
    # Contar índices con valor (para no afectar el promedio con ceros)
    indices = [indice_accesibilidad, indice_cumplimiento, indice_vehiculo, indice_actitudes]
    indices_validos = [ind for ind in indices if ind > 0]
    
    if not indices_validos:
        return 0
    
    # Calcular promedio de los índices válidos
    indice_general = sum(indices_validos) / len(indices_validos)
    
    return round(indice_general, 2)

def identificar_problemas(df, umbral_alerta=80, umbral_critico=70):
    """
    Identifica problemas en los indicadores.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        umbral_alerta (int, optional): Umbral para alertas (por debajo de este valor).
        umbral_critico (int, optional): Umbral para problemas críticos (por debajo de este valor).
    
    Returns:
        tuple: (problemas_criticos, alertas) Listas de diccionarios con los problemas identificados.
    """
    # Definir todas las columnas de interés por grupo
    columnas_por_grupo = {
        'Accesibilidad': [
            'comedor_facil_Acceso',
            'vehiculo_puede_llegar_a_sitio',
            'trasbordo',
            'ingreso_apoyo_comunidad',
            'demora_entregas',
            'inocuidad_comprometida'
        ],
        'Cumplimiento': [
            'entrega_en_dia_programado',
            'alimentos_debidamente_entregados'
        ],
        'Vehículo': [
            'vehiculo_limpio_buen_estado',
            'alimentos_de_calidad_cantidad',
            'contenedores_para_cada_tipoalimento'
        ],
        'Actitudes': [
            'actitud_conductor_respetuosa_colaborativa',
            'actitud_auxiliar_respetuosa_colaborativa',
            'actitud_gestora_respetuosa_colaborativa',
            'buena_disposicion_recibir_mercados',
            'comunicacion_efectiva',
            'resolucion_inconvenientes'
        ]
    }
    
    # Mapeo de nombres de columnas a nombres más legibles
    nombres_legibles = {
        'comedor_facil_Acceso': 'Acceso Fácil al Comedor',
        'vehiculo_puede_llegar_a_sitio': 'Vehículo Llega Directamente',
        'trasbordo': 'Necesidad de Trasbordo',
        'ingreso_apoyo_comunidad': 'Necesidad de Apoyo Comunitario',
        'demora_entregas': 'Demoras en Otras Entregas',
        'inocuidad_comprometida': 'Inocuidad Comprometida',
        'entrega_en_dia_programado': 'Entrega en Día Programado',
        'alimentos_debidamente_entregados': 'Verificación de Alimentos',
        'vehiculo_limpio_buen_estado': 'Vehículo Limpio y en Buen Estado',
        'alimentos_de_calidad_cantidad': 'Calidad y Cantidad de Alimentos',
        'contenedores_para_cada_tipoalimento': 'Contenedores Adecuados',
        'actitud_conductor_respetuosa_colaborativa': 'Actitud del Conductor',
        'actitud_auxiliar_respetuosa_colaborativa': 'Actitud del Auxiliar',
        'actitud_gestora_respetuosa_colaborativa': 'Actitud de la Gestora',
        'buena_disposicion_recibir_mercados': 'Disposición para Recibir',
        'comunicacion_efectiva': 'Comunicación Efectiva',
        'resolucion_inconvenientes': 'Resolución de Inconvenientes'
    }
    
    # Indicadores que deben invertirse (son negativos)
    indicadores_negativos = ['trasbordo', 'ingreso_apoyo_comunidad', 'demora_entregas', 'inocuidad_comprometida']
    
    problemas_criticos = []
    alertas = []
    
    # Analizar cada grupo de indicadores
    for grupo, columnas in columnas_por_grupo.items():
        # Verificar qué columnas existen
        columnas_existentes = [col for col in columnas if col in df.columns]
        
        # Analizar cada indicador
        for col in columnas_existentes:
            # Calcular valor
            valor = calcular_porcentaje(df, col)
            
            # Para indicadores negativos, invertir el valor
            if col in indicadores_negativos:
                valor = 100 - valor
                nombre = "Ausencia de " + nombres_legibles.get(col, col)
            else:
                nombre = nombres_legibles.get(col, col)
            
            # Evaluar si es un problema
            if valor < umbral_critico:
                problemas_criticos.append({
                    'grupo': grupo,
                    'indicador': nombre,
                    'valor': valor,
                    'columna': col
                })
            elif valor < umbral_alerta:
                alertas.append({
                    'grupo': grupo,
                    'indicador': nombre,
                    'valor': valor,
                    'columna': col
                })
    
    # Ordenar por valor ascendente (peores primero)
    problemas_criticos = sorted(problemas_criticos, key=lambda x: x['valor'])
    alertas = sorted(alertas, key=lambda x: x['valor'])
    
    return problemas_criticos, alertas

def generar_recomendaciones(problemas, alertas):
    """
    Genera recomendaciones basadas en los problemas identificados.
    
    Args:
        problemas (list): Lista de problemas críticos.
        alertas (list): Lista de alertas.
    
    Returns:
        dict: Diccionario con recomendaciones por categoría y horizonte temporal.
    """
    # Inicializar estructura para recomendaciones
    recomendaciones = {
        'corto_plazo': [],   # Acción inmediata (1-3 meses)
        'mediano_plazo': [], # Acción planeada (3-6 meses)
        'largo_plazo': []    # Mejora continua (6-12 meses)
    }
    
    # Recomendaciones específicas según el indicador
    if problemas or alertas:
        # Combinar problemas y alertas, priorizando problemas
        todos_problemas = problemas + alertas
        
        # Generar recomendaciones específicas por problema
        for problema in todos_problemas:
            categoria = problema['grupo']
            indicador = problema['columna']
            
            # Generar recomendación específica según el indicador
            recomendacion = ""
            
            # Accesibilidad
            if indicador == 'comedor_facil_Acceso' or indicador == 'vehiculo_puede_llegar_a_sitio':
                recomendacion = f"Realizar un estudio detallado de rutas y accesos para mejorar el acceso a los comedores con dificultades."
                recomendaciones['corto_plazo'].append(recomendacion) if indicador in [p['columna'] for p in problemas] else recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'trasbordo':
                recomendacion = f"Evaluar la posibilidad de utilizar vehículos más pequeños para zonas de difícil acceso."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'ingreso_apoyo_comunidad':
                recomendacion = f"Establecer acuerdos formales con líderes comunitarios para facilitar el apoyo en las entregas."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'demora_entregas':
                recomendacion = f"Optimizar la programación de rutas considerando los tiempos adicionales para comedores de difícil acceso."
                recomendaciones['corto_plazo'].append(recomendacion) if indicador in [p['columna'] for p in problemas] else recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'inocuidad_comprometida':
                recomendacion = f"Implementar protocolos específicos para preservar la inocuidad de los alimentos en condiciones de trasbordos."
                recomendaciones['corto_plazo'].append(recomendacion)
            
            # Cumplimiento
            elif indicador == 'entrega_en_dia_programado':
                recomendacion = f"Establecer un sistema de seguimiento en tiempo real para monitorear el cumplimiento de entregas."
                recomendaciones['corto_plazo'].append(recomendacion) if indicador in [p['columna'] for p in problemas] else recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'alimentos_debidamente_entregados':
                recomendacion = f"Implementar un sistema digital de verificación de alimentos con listas de chequeo electrónicas."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            # Vehículo
            elif indicador == 'vehiculo_limpio_buen_estado':
                recomendacion = f"Establecer un protocolo de verificación de limpieza y estado del vehículo antes de cada jornada."
                recomendaciones['corto_plazo'].append(recomendacion) if indicador in [p['columna'] for p in problemas] else recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'alimentos_de_calidad_cantidad':
                recomendacion = f"Reforzar los controles de calidad de alimentos antes de su carga en los vehículos."
                recomendaciones['corto_plazo'].append(recomendacion)
            
            elif indicador == 'contenedores_para_cada_tipoalimento':
                recomendacion = f"Estandarizar el uso de contenedores específicos para cada tipo de alimento con etiquetado claro."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            # Actitudes
            elif 'actitud' in indicador:
                recomendacion = f"Implementar talleres de sensibilización y capacitación en servicio al cliente y trabajo en equipo."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'buena_disposicion_recibir_mercados':
                recomendacion = f"Desarrollar protocolos claros para el proceso de recepción y establecer tiempos estimados para cada etapa."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'comunicacion_efectiva':
                recomendacion = f"Establecer canales de comunicación efectivos y un glosario común para todos los actores involucrados."
                recomendaciones['mediano_plazo'].append(recomendacion)
            
            elif indicador == 'resolucion_inconvenientes':
                recomendacion = f"Implementar un sistema de registro y seguimiento de incidencias para asegurar su resolución."
                recomendaciones['mediano_plazo'].append(recomendacion)
    
    # Recomendaciones generales de largo plazo (siempre se incluyen)
    recomendaciones['largo_plazo'] = [
        "Implementar un sistema integral de monitoreo y evaluación continua del proceso de entrega.",
        "Establecer un programa de capacitación permanente para todo el personal involucrado en el proceso.",
        "Desarrollar un plan de mejora continua con revisiones trimestrales de los indicadores clave."
    ]
    
    # Eliminar duplicados
    for plazo in recomendaciones:
        recomendaciones[plazo] = list(dict.fromkeys(recomendaciones[plazo]))
    
    return recomendaciones

def analizar_tendencia(df, columna, meses=3):
    """
    Analiza la tendencia de un indicador en los últimos meses.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna (str): Columna a analizar.
        meses (int, optional): Número de meses a considerar.
    
    Returns:
        dict: Diccionario con información de la tendencia.
    """
    # Verificar si existen las columnas necesarias
    if 'fecha' not in df.columns or columna not in df.columns or df.empty:
        return None
    
    # Convertir a datetime si no lo es ya
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Filtrar datos sin fecha válida
    df = df.dropna(subset=['fecha'])
    
    if df.empty:
        return None
    
    # Agrupar por mes
    df['mes'] = df['fecha'].dt.to_period('M')
    
    # Calcular promedio por mes
    datos_tiempo = df.groupby('mes')[columna].mean().reset_index()
    datos_tiempo['mes'] = datos_tiempo['mes'].dt.to_timestamp()
    datos_tiempo[columna] = datos_tiempo[columna] * 100  # Convertir a porcentaje
    
    # Ordenar por fecha
    datos_tiempo = datos_tiempo.sort_values('mes')
    
    # Si no hay suficientes datos para analizar tendencia
    if len(datos_tiempo) < 2:
        return {
            'tendencia': 'estable',
            'cambio': 0,
            'ultimo_valor': datos_tiempo[columna].iloc[-1] if not datos_tiempo.empty else 0
        }
    
    # Tomar los últimos N meses
    ultimos_meses = datos_tiempo.tail(min(meses, len(datos_tiempo)))
    
    # Calcular cambio absoluto y porcentual
    primer_valor = ultimos_meses[columna].iloc[0]
    ultimo_valor = ultimos_meses[columna].iloc[-1]
    
    cambio_absoluto = ultimo_valor - primer_valor
    cambio_porcentual = (cambio_absoluto / primer_valor) * 100 if primer_valor > 0 else 0
    
    # Determinar tendencia
    if abs(cambio_porcentual) < 5:
        tendencia = 'estable'
    elif cambio_porcentual > 0:
        tendencia = 'positiva'
    else:
        tendencia = 'negativa'
    
    return {
        'tendencia': tendencia,
        'cambio': round(cambio_porcentual, 2),
        'ultimo_valor': round(ultimo_valor, 2)
    }

def identificar_mejores_peores(df, columna_grupo, columnas_indicadores):
    """
    Identifica los mejores y peores elementos por grupo.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        columna_grupo (str): Nombre de la columna por la que agrupar.
        columnas_indicadores (list): Lista de columnas de indicadores a analizar.
    
    Returns:
        tuple: (mejores, peores) Listas con los mejores y peores elementos.
    """
    # Verificar si existen las columnas necesarias
    if columna_grupo not in df.columns or df.empty:
        return [], []
    
    # Verificar qué columnas de indicadores existen
    columnas_existentes = [col for col in columnas_indicadores if col in df.columns]
    
    if not columnas_existentes:
        return [], []
    
    # Crear DataFrame para resultados
    resultados = pd.DataFrame()
    
    # Para cada columna, calcular promedio por grupo
    for col in columnas_existentes:
        # Agrupar por la columna de grupo y calcular promedio
        temp = df.groupby(columna_grupo)[col].mean().reset_index()
        temp[col] = temp[col] * 100  # Convertir a porcentaje
        
        # Iniciar o unir con resultados
        if resultados.empty:
            resultados = temp
        else:
            resultados = resultados.merge(temp, on=columna_grupo)
    
    # Calcular promedio general
    resultados['promedio_general'] = resultados[columnas_existentes].mean(axis=1)
    
    # Ordenar por promedio general
    resultados = resultados.sort_values(by='promedio_general', ascending=False)
    
    # Obtener los 3 mejores y los 3 peores
    mejores = resultados.head(min(3, len(resultados))).to_dict('records')
    peores = resultados.tail(min(3, len(resultados))).to_dict('records')
    
    return mejores, peores