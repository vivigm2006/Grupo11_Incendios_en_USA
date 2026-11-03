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

st.header("2. Población y Fuentes de Información")
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
* **Población:** Comprende la **totalidad de los eventos de incendios forestales** registrados a nivel nacional en Estados Unidos dentro de la base de datos espacial. Al tratarse de un análisis que abarca el registro histórico completo y exhaustivo de todos los eventos verificados, clasificados y georreferenciados por las agencias interagenciales (federales, estatales y locales), **no se emplea una muestra**, sino el universo total de los datos disponibles.
* **Fuentes Primarias:** Se emplean las bases de datos abiertas del NIFC y del Servicio Forestal de los Estados Unidos (USFS), permitiendo evaluar la tendencia histórica global con una cobertura censal completa.
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

st.header("3. Técnicas e Instrumentos")
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

with st.expander("⚠️ Limitación de la fecha de contención", expanded=True):
    st.markdown("""
    Una limitación importante de la base de datos FPA FOD (Short, 2017) radica en la presencia de valores faltantes en la variable de fecha de contención. En el conjunto de datos analizado, **891 531 registros (correspondientes al 47,31 % del total)** no presentan la fecha de contención del incendio. 
    Por consiguiente, los análisis descriptivos vinculados al tiempo de respuesta y duración del evento se restringen únicamente al subconjunto de datos que dispone de dicha información de forma completa. No obstante, para los objetivos restantes se emplea la totalidad del registro histórico, garantizando la representatividad general del estudio.
    """)

with st.expander("🗺️ Justificación de la Agrupación Territorial", expanded=True):
    st.markdown("""
    Analizar individualmente los 50 estados genera una dispersión espacial excesiva de los datos y dificulta la extracción de patrones claros. En lugar de emplear divisiones político-administrativas tradicionales, la delimitación territorial de este estudio adopta la clasificación oficial de **Áreas Geográficas de Coordinación Interagencial (NIFC / NICC)**. 

    Esta estructura subdivide el territorio estadounidense en zonas delimitadas por la **homogeneidad de sus patrones eco-climáticos, tipos de vegetación (combustibles forestales) y regímenes históricos de fuego**. Esto dota a la investigación de alta validez práctica al evaluar los incendios bajo las mismas unidades geográficas donde las agencias operan.
    """)

st.markdown("---")

st.header("5. Stack Tecnológico")
st.markdown("""
Para el procesamiento eficiente del universo censal de registros históricos, se implementó una arquitectura analítica basada en **DuckDB** y almacenamiento intermedio en formato **`.parquet`**, omitiendo la geometría espacial pesada tipo *Shape*, optimizando la memoria RAM y ejecutando consultas SQL ultrarrápidas.
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

st.header("6. Fases de Análisis")
st.markdown("""
El procesamiento de la información se desarrolló en las siguientes fases estratégicas:
1. **Análisis descriptivo e inferencial:** Cálculo de frecuencias, promedios de área quemada y tiempos de respuesta por región, junto con evaluación estadística general.
2. **Análisis espacial y de distribución de severidad:** Identificación de patrones de concentración regional de incendios de mayor severidad y mapeo de fuentes de ignición predominantes.
3. **Síntesis e interpretación de resultados:** Evaluación integrada de las hipótesis planteadas para contrastar las diferencias eco-climáticas y de gestión territorial.
""")

st.markdown("---")

st.header("7. Vistas Analíticas")
st.markdown("""
Se estructuraron vistas analíticas dedicadas para facilitar la exploración interactiva y evitar cálculos complejos en tiempo real:
* **Vista Obj 1:** Agrupa incendios y superficie quemada por región.
* **Vista Obj 2:** Frecuencia de causas humanas vs. naturales por región.
* **Vista Obj 3:** Magnitud de los mega-incendios por región.
* **Vistas Obj 4 y 5:** Tiempos promedio de respuesta y superficie por tipo de terreno y estación.
* **Vista General Detallada:** Mantiene el detalle individual para gráficos de dispersión y mapas.
""")