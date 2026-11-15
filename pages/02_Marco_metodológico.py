"""
Marco metodologico de la investigacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st

st.set_page_config(page_title="Marco Metodológico", page_icon="🚒", layout="wide")

st.image("assets/imagen.jpg", width="stretch")
st.title("Marco Metodológico")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

import pandas as pd

st.markdown("---")

st.header("1. Tipo y Diseño de la Investigación")
st.markdown("""
La presente investigación se enmarca en un **enfoque cuantitativo** de nivel **descriptivo-comparativo** y de **corte longitudinal**:
* **Descriptiva:** Busca caracterizar las variables fundamentales de los incendios forestales (frecuencia, severidad o superficie quemada, causas de origen, propiedad del terreno y estacionalidad) en el territorio estadounidense.
* **Comparativa:** Contrasta de manera sistemática estas dinámicas entre las 10 regiones geográficas de coordinación reagrupadas según el marco del Centro Nacional Interagencial de Incendios (**NIFC/NICC**).
* **No experimental y longitudinal:** Analiza la evolución temporal y espacial de los registros históricos de fuego sin manipular deliberadamente las variables de estudio.
""")

st.markdown("---")

st.header("2. Población y Fuente de Información")
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
* **Población:** Comprende la **totalidad de los eventos de incendios forestales** registrados a nivel nacional en Estados Unidos dentro de la base de datos espacial. Al tratarse de un análisis que abarca el registro histórico completo y exhaustivo de todos los eventos verificados, clasificados y georreferenciados por las agencias interagenciales (federales, estatales y locales), **no se emplea una muestra**, sino el universo total de los datos disponibles.
* **Fuente:** Se emplean las bases de datos abiertas del NIFC y del Servicio Forestal de los Estados Unidos (USFS), permitiendo evaluar la tendencia histórica global con una cobertura censal completa.
""")

with col2:
    st.metric(
        label="Universo Analizado",
        value="Censal (100%)",
        delta="Sin muestreo"
    )
    st.metric(
        label="Fuente Principal",
        value="FPA FOD (Short)",
        delta="1992 - 2015"
    )

st.markdown("---")

st.header("3. Enfoque de fuentes y herramientas analíticas")
st.markdown("""
La técnica principal utilizada es la **observación indirecta y el análisis documental** de registros cuantitativos secundarios. Para ello, se estructuró una ficha de extracción que captura las siguientes variables clave de cada incendio:

* **Ubicación geográfica y asignación regional:** Clasificación del evento dentro de una de las 10 regiones del NIFC (*Northwest, Northern California, Southern California, Northern Rockies, Great Basin, Rocky Mountain, Southwest, Southern, Eastern, Alaska*).
* **Causa de origen e ignición:** Diferenciación entre causas humanas (accidentales o intencionadas) y naturales (principalmente rayos).
* **Magnitud y severidad:** Superficie total afectada (hectáreas/acres) e identificación de mega-incendios de alta severidad.
* **Administración del terreno:** Tipo de propiedad de la tierra donde se originó o expandió el fuego (*Federal, Estatal o Privada*).
* **Temporalidad y respuesta:** Fecha de inicio, estación del año y tiempo de contención del incendio.
""")

st.markdown("---")

st.header("4. Justificaciones Metodológicas")

with st.expander("Justificación de la fecha de contención", expanded=True):
    st.markdown("""
    Una limitación importante de la base de datos FPA FOD (Short, 2017) radica en la presencia de valores faltantes en la variable de fecha de contención. En el conjunto de datos analizado, **891 531 registros (correspondientes al 47,31 % del total)** no presentan la fecha de contención del incendio. 
    Por consiguiente, los análisis descriptivos vinculados al tiempo de respuesta y duración del evento se restringen únicamente al subconjunto de datos que dispone de dicha información de forma completa. No obstante, para los objetivos restantes se emplea la totalidad del registro histórico, garantizando la representatividad general del estudio.
    """)

with st.expander("Justificación de la Agrupación Territorial", expanded=True):
    st.markdown("""
    Analizar individualmente los 50 estados genera una dispersión espacial excesiva de los datos y dificulta la extracción de patrones claros. En lugar de emplear divisiones político-administrativas tradicionales, la delimitación territorial de este estudio adopta la clasificación oficial de **Áreas Geográficas de Coordinación Interagencial (NIFC / NICC)**. 

    Esta estructura subdivide el territorio estadounidense en zonas delimitadas por la **homogeneidad de sus patrones eco-climáticos, tipos de vegetación (combustibles forestales) y regímenes históricos de fuego**. Esto dota a la investigación de alta validez práctica al evaluar los incendios bajo las mismas unidades geográficas donde las agencias operan.
    """)

st.markdown("---")

st.header("5. Stack Tecnológico")
st.markdown("""
Para el procesamiento eficiente del universo censal de registros históricos, se implementó una arquitectura analítica basada en **DuckDB** y almacenamiento intermedio en formato **`.parquet`**, optimizando la memoria RAM y ejecutando consultas SQL ultrarrápidas.
""")

tech_data = {
    "Categoría": [
        "Lenguaje de Programación",
        "Motor Analítico / SQL",
        "Formatos de Datos",
        "Visualización e Interfaz",
        "Control de Versiones",
    ],
    "Tecnología": [
        "Python 3.14+",
        "DuckDB",
        "SQLite, DuckDB, Parquet",
        "Streamlit y Power BI",
        "Git / GitHub",
    ],
}
st.dataframe(pd.DataFrame(tech_data), use_container_width=True, hide_index=True)

st.markdown("---")

st.header("6. Procedimiento y Fases de Análisis")

tab1, tab2, tab3, tab4 = st.tabs([
    "Fases de Análisis", 
    "Limpieza y Normalización", 
    "Denormalización", 
    "Modelo Dimensional"
])

with tab1:
    st.markdown("""
    El procesamiento de la información se desarrolló en cuatro fases consecutivas:
    1. **Depuración y normalización de datos:** Filtrado de inconsistencias, estandarización de registros históricos y asignación espacial de coordenadas a las 10 regiones operativas del NIFC.
    2. **Análisis descriptivo e inferencial:** Cálculo de frecuencias, promedios de área quemada y tiempos de contención por región, junto con pruebas estadísticas de comparación de grupos.
    3. **Análisis espacial y de distribución de severidad:** Identificación de patrones de concentración regional de incendios de mayor severidad y mapeo de fuentes de ignición predominantes.
    4. **Síntesis e interpretación de resultados:** Evaluación integrada de las hipótesis planteadas para contrastar las diferencias eco-climáticas y de gestión territorial.
    """)

with tab2:
    st.markdown("""
    ### Estrategia de Normalización
    * **Paso 1 (Completación de condados y estados):** El 36% de los registros tenían este campo vacío. Se usaron longitud y latitud cruzándolas con un archivo *ShapeFile* del censo de EE. UU. para ubicar el punto exacto de cada incendio de forma automatizada y asignar los códigos FIPS y estados.
    * **Paso 2 (Asignación de Región NIFC):** Se cruzó la base de datos con el archivo CSV que contiene el campo de Área Geográfica utilizando el Código de Estado + Código FIPS.
    * **Paso 3 (Estandarización temporal):** Se cambió el formato de los campos de fecha de Juliano a formato nativo `DATE`.
    """)
    st.image(
        "assets/Diagrama_Normalizacion.png",
        caption="Diagrama de Normalizacion",
        width="stretch"
        )

with tab3:
    st.markdown("""
    ### Estrategia de Denormalizacion
    Para garantizar un rendimiento óptimo en la interfaz interactiva y analítica, se aplicaron tácticas clave de denormalización sobre el esquema:
    * **Reducción de operaciones JOIN:** Se consolidaron atributos descriptivos clave dentro de estructuras optimizadas para evitar cruces relacionales excesivos en tiempo de ejecución.
    * **Duplicación controlada:** Se precomputaron y replicaron ciertos campos categóricos para agilizar el filtrado dinámico en los componentes de Streamlit.
    * **Enfoque OLAP:** La transición desde esquemas altamente normalizados hacia un entorno analítico denormalizado permite procesar millones de registros sin latencia perceptible.
    """)
    st.image(
        "assets/Diagrama_Denormalizacion.png",
        caption="Diagrama de Denormalizacion",
        width="stretch"
        )

with tab4:
    st.markdown("""
    ### Transición del Modelo Relacional al Dimensional (Estrella)
    Se construyó una capa analítica optimizada en **Modelo Estrella** aplicando conceptos de denormalización para garantizar consultas de alta velocidad en Streamlit sin ralentizaciones por cruces masivos en tiempo real.
    """)

    dim_data = {
        "Tabla / Dimensión": [
            "fact_incendio",
            "dim_fecha",
            "dim_region",
            "dim_causa",
            "dim_administracion",
            "dim_ubicacion",
            "dim_tamano",
        ],
        "Tipo": [
            "Tabla de Hechos",
            "Dimensión",
            "Dimensión",
            "Dimensión",
            "Dimensión",
            "Dimensión",
            "Dimensión",
        ],
        "Descripción Detallada": [
            "Granularidad de un registro por incendio detectado. Almacena superficie en acres, tiempo de contención en días y claves foráneas.",
            "Para el análisis temporal y la clasificación de las cuatro estaciones del año.",
            "Para la comparación entre las 10 áreas geográficas operativas del NIFC/NICC.",
            "Aplica regla de negocio para agrupar causas en 'Humana' o 'Natural'.",
            "Clasifica la titularidad del suelo en Federal, Estatal/Local o Privada.",
            "Conserva información del estado, condado y extensión en millas cuadradas para análisis espacial.",
            "Tabla estática basada en escala A-G que incorpora el indicador booleano `es_megaincendio` (Clase G >= 5,000 acres).",
        ],
    }
    st.table(pd.DataFrame(dim_data))

st.markdown("---")

st.header("7. Optimización, Manejo de Nulos y Vistas Analíticas")

col_op1, col_op2 = st.columns(2)

with col_op1:
    with st.expander("Tratamiento de Valores Faltantes (Contención)", expanded=True):
        st.markdown("""
        * Para maximizar el rendimiento se usaron claves subrogadas con `DENSE_RANK()` para compactar la tabla de hechos.
        * Atendiendo a que el **47.31% de los registros carecen de fecha de contención**, se incorporó una variable dicotómica denominada **`tiene_contencion`** (1 si posee fecha de control, 0 si no).
        * Esto permite calcular promedios de tiempo de respuesta filtrando exclusivamente los registros válidos, evitando sesgos o divisiones por nulos.
        """)

with col_op2:
    with st.expander("Vistas Analíticas Materializadas", expanded=True):
        st.markdown("""
        Se materializaron cinco vistas analíticas para evitar cálculos complejos en tiempo real:
        * **Vista Obj 1:** Agrupa incendios y superficie quemada por región.
        * **Vista Obj 2:** Frecuencia de causas humanas vs. naturales por región.
        * **Vista Obj 3:** Magnitud de los mega-incendios por región.
        * **Vistas Obj 4 y 5:** Tiempos promedio de contención y superficie por tipo de terreno y estación.
        * **Vista General Detallada:** Mantiene el detalle individual para gráficos de dispersión y mapas.
        """)
    
#diciconario de datos
def mostrar_diccionario_datos():
    st.title("Diccionario de Datos")
    
    st.markdown("### Normalización")
    st.markdown(
        "El objetivo de esta capa es estructurar la información en un modelo relacional "
        "para eliminar la redundancia de datos, garantizar la integridad referencial y optimizar "
        "el almacenamiento de la información de incendios forestales en EE. UU."
    )
    
    #tabla de estados
    st.subheader("1. Tabla de Estados (`tabla_estado`)")
    st.markdown("Almacena la información oficial de los estados de EE. UU.")
    df_estado = pd.DataFrame([
        {"Campo": "state_code", "Tipo": "VARCHAR(2)", "Descripción": "Llave Primaria. Código único de dos caracteres del estado (ISO/ANSI)."},
        {"Campo": "state_name", "Tipo": "VARCHAR", "Descripción": "Nombre completo oficial del estado."},
        {"Campo": "state_abbr", "Tipo": "VARCHAR(2)", "Descripción": "Abreviatura o sigla estándar del estado."}
    ])
    st.dataframe(df_estado, use_container_width=True, hide_index=True)
    
    #tabla de Condados
    st.subheader("2. Tabla de Condados (`tabla_condado`)")
    st.markdown("Contiene la segmentación territorial a nivel de condados y su relación con cada estado.")
    df_condado = pd.DataFrame([
        {"Campo": "state_code", "Tipo": "VARCHAR(2)", "Descripción": "Llave Foránea (hacia `tabla_estado`). Código del estado al que pertenece el condado."},
        {"Campo": "fips_code", "Tipo": "VARCHAR(3)", "Descripción": "Llave Primaria compuesta (junto a `state_code`). Código FIPS de 3 dígitos del condado."},
        {"Campo": "fips_name", "Tipo": "VARCHAR", "Descripción": "Nombre oficial del condado."},
        {"Campo": "land_sq_mi", "Tipo": "DOUBLE", "Descripción": "Superficie territorial del condado medida en millas cuadradas."}
    ])
    st.dataframe(df_condado, use_container_width=True, hide_index=True)
    
    #tabla de Causa de Incendio
    st.subheader("3. Tabla de Causa de Incendio (`tabla_causa_incendio`)")
    st.markdown("Catálogo de los motivos o causas principales que originaron los incendios.")
    df_causa = pd.DataFrame([
        {"Campo": "cause_code", "Tipo": "SMALLINT", "Descripción": "Llave Primaria. Identificador numérico único de la causa."},
        {"Campo": "cause_descr", "Tipo": "VARCHAR", "Descripción": "Descripción detallada del origen del fuego (ej. Rayos, Humano, etc.)."}
    ])
    st.dataframe(df_causa, use_container_width=True, hide_index=True)
    
#tabla de Propietario del Terreno
    st.subheader("4. Tabla de Propietario del Terreno (`tabla_propietario`)")
    st.markdown("Catálogo que clasifica la entidad o tipo de administración del terreno afectado.")
    df_propietario = pd.DataFrame([
        {"Campo": "owner_code", "Tipo": "SMALLINT", "Descripción": "Llave Primaria. Identificador numérico del tipo de propietario."},
        {"Campo": "owner_descr", "Tipo": "VARCHAR", "Descripción": "Descripción de la entidad administradora (ej. Federal, Estatal, Privada)."}
    ])
    st.dataframe(df_propietario, use_container_width=True, hide_index=True)
    
#tabla de Clase de Tamaño
    st.subheader("5. Tabla de Clase de Tamaño (`tabla_clase_tamano`)")
    st.markdown("Rangos oficiales de clasificación según la superficie quemada.")
    df_tamano = pd.DataFrame([
        {"Campo": "fire_size_class", "Tipo": "VARCHAR(1)", "Descripción": "Llave Primaria. Letra distintiva de la clase de tamaño (rango de A a G)."},
        {"Campo": "min_acres", "Tipo": "DOUBLE", "Descripción": "Límite inferior de superficie afectada en acres."},
        {"Campo": "max_acres", "Tipo": "DOUBLE", "Descripción": "Límite superior de superficie afectada en acres."}
    ])
    st.dataframe(df_tamano, use_container_width=True, hide_index=True)
    
#tabla de Área Geográfica
    st.subheader("6. Tabla de Área Geográfica (`tabla_geographic_area`)")
    st.markdown("Clasificación por áreas geográficas de gestión operativa de incendios en EE. UU.")
    df_area = pd.DataFrame([
        {"Campo": "geographic_area_code", "Tipo": "VARCHAR(2)", "Descripción": "Llave Primaria. Código identificador del área geográfica operativa."},
        {"Campo": "geographic_area_name", "Tipo": "VARCHAR", "Descripción": "Nombre oficial del área geográfica de respuesta."}
    ])
    st.dataframe(df_area, use_container_width=True, hide_index=True)
    
#tabla de Incendios
    st.subheader("7. Tabla Principal de Incendios (`tabla_incendios`)")
    st.markdown("Registro central y transaccional de cada evento de incendio forestal detectado.")
    df_incendios = pd.DataFrame([
        {"Campo": "objectid", "Tipo": "INTEGER", "Descripción": "Llave Primaria. Identificador único y correlativo del evento de incendio."},
        {"Campo": "discovery_date", "Tipo": "DATE", "Descripción": "Fecha en la que se descubrió o reportó el inicio del incendio."},
        {"Campo": "cont_date", "Tipo": "DATE", "Descripción": "Fecha en la que el incendio fue contenido o controlado."},
        {"Campo": "fire_size_class", "Tipo": "VARCHAR(1)", "Descripción": "Llave Foránea hacia `tabla_clase_tamano`. Rango de tamaño del incendio."},
        {"Campo": "fire_size", "Tipo": "DOUBLE", "Descripción": "Superficie total quemada medida en acres."},
        {"Campo": "latitude", "Tipo": "DOUBLE", "Descripción": "Coordenada geográfica de latitud del punto de origen."},
        {"Campo": "longitude", "Tipo": "DOUBLE", "Descripción": "Coordenada geográfica de longitud del punto de origen."},
        {"Campo": "cause_code", "Tipo": "SMALLINT", "Descripción": "Llave Foránea hacia `tabla_causa_incendio`. Motivo del origen del fuego."},
        {"Campo": "owner_code", "Tipo": "SMALLINT", "Descripción": "Llave Foránea hacia `tabla_propietario`. Tipo de propiedad del suelo afectado."},
        {"Campo": "state_code", "Tipo": "VARCHAR(2)", "Descripción": "Llave Foránea hacia `tabla_condado` (y `tabla_estado`). Estado donde ocurrió el incendio."},
        {"Campo": "fips_code", "Tipo": "VARCHAR(3)", "Descripción": "Llave Foránea hacia `tabla_condado`. Condado específico de ocurrencia."},
        {"Campo": "geographic_area_code", "Tipo": "VARCHAR(2)", "Descripción": "Llave Foránea hacia `tabla_geographic_area`. Área operativa asignada."}
    ])
    st.dataframe(df_incendios, use_container_width=True, hide_index=True)

mostrar_diccionario_datos()
    