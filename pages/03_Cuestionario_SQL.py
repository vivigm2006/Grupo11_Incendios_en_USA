"""
Cuestionario SQL - seis consultas

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analisis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
"""
import os
import time
import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Consultas SQL — MotherDuck",
    page_icon="🪓",
    layout="wide",
)

MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
os.environ["MOTHERDUCK_TOKEN"] = MOTHERDUCK_TOKEN

# Ajusta aquí la base si tu tabla Fires está en otra en MotherDuck (p. ej. "Consultasbbdd")
BASE_DATOS = "incendios_usa"


@st.cache_resource
def get_connection():
  con = duckdb.connect(f"md:{BASE_DATOS}?motherduck_token={MOTHERDUCK_TOKEN}")
  con.sql(f"USE {BASE_DATOS};")
  return con


@st.cache_data(show_spinner="Ejecutando consulta en MotherDuck...")
def ejecutar_consulta_cacheada(query: str, _nonce: int = 0) -> pd.DataFrame:
  con = get_connection()
  for intento in range(3):
    try:
      return con.sql(query).df()
    except duckdb.Error as e:
      if "DEADLINE_EXCEEDED" in str(e) and intento < 2:
        time.sleep(2 * (intento + 1))
      else:
        raise


PREGUNTAS = [
    {
        "id": "q1",
        "titulo": "Pregunta 1: Peso de Cada Causa en Dos Periodos",
        "enunciado": (
            "Se comparan dos periodos de doce años según el año del incendio"
            " (FIRE_YEAR): de 1992 a 2003 y de 2004 a 2015."
        ),
        "sql": """
        """,
        "interpretacion": (
            "**Interpretación:** Aquí puedes redactar el análisis del cambio en"
            " puntos porcentuales de cada causa entre 1992–2003 y 2004–2015."
        ),
    },
    {
        "id": "q2",
        "titulo": "Pregunta 2: Mayores Aumentos Interanuales por Mes",
        "enunciado": (
            """Para eliminar el efecto de la estacionalidad, cada mes se compara con el mismo mes del año anterior.

Cuenta los incendios por año y mes de la fecha de descubrimiento, y compara cada mes con el mismo mes del año anterior cruzando 
la serie consigo misma. Considera solo los meses cuya cantidad de incendios sea mayor o igual que la media mensual de toda la serie.

Muestra los diez meses con mayor aumento porcentual, con su puesto, el año, el mes, los incendios, los incendios del mismo mes del año anterior,
 la variación porcentual y el puesto que ocupa ese mes, por cantidad de incendios, entre los meses considerados del mismo mes calendario. Ordena 
 por puesto.
"""
        ),
        "sql": """
        WITH IncendiosMensuales AS (
    -- Cuenta los incendios por año y mes a partir de la fecha de descubrimiento (día juliano en SQLite)
    SELECT 
        CAST(strftime('%Y', DISCOVERY_DATE) AS INTEGER) AS anio,
        CAST(strftime('%m', DISCOVERY_DATE) AS INTEGER) AS mes,
        COUNT(*) AS total_incendios
    FROM Fires
    WHERE DISCOVERY_DATE IS NOT NULL
    GROUP BY anio, mes
),
MediaMensualGlobal AS (
    -- Subconsulta / cálculo de la media mensual de toda la serie para filtrar
    SELECT AVG(total_incendios) AS media_general 
    FROM IncendiosMensuales
),
MesesFiltrados AS (
    -- Considera solo los meses cuya cantidad de incendios sea mayor o igual que la media mensual de toda la serie
    SELECT 
        im.anio,
        im.mes,
        im.total_incendios
    FROM IncendiosMensuales im
    WHERE im.total_incendios >= (SELECT media_general FROM MediaMensualGlobal)
),
ComparacionInteranual AS (
    -- SELF JOIN: Cruza la serie consigo misma para comparar cada mes con el mismo mes del año anterior (anio - 1)
    SELECT 
        curr.anio AS anio_actual,
        curr.mes AS mes_actual,
        curr.total_incendios AS incendios_actual,
        prev.total_incendios AS incendios_anio_anterior,
        ROUND(CAST((curr.total_incendios - prev.total_incendios) AS REAL) * 100.0 / prev.total_incendios, 2) AS variacion_porcentual
    FROM MesesFiltrados curr
    JOIN MesesFiltrados prev ON curr.mes = prev.mes AND curr.anio = prev.anio + 1
),
RankingPorMesCalendario AS (
    -- Función de ventana para calcular el puesto que ocupa ese mes por cantidad de incendios entre los meses del mismo mes calendario
    SELECT 
        anio_actual,
        mes_actual,
        incendios_actual,
        incendios_anio_anterior,
        variacion_porcentual,
        RANK() OVER (PARTITION BY mes_actual ORDER BY incendios_actual DESC) AS puesto_mes_calendario
    FROM ComparacionInteranual
),
RankingGlobalAumento AS (
    -- Función de ventana para ordenar los 10 mayores aumentos porcentuales generales
    SELECT 
        anio_actual,
        mes_actual,
        incendios_actual,
        incendios_anio_anterior,
        variacion_porcentual,
        puesto_mes_calendario,
        RANK() OVER (ORDER BY variacion_porcentual DESC) AS puesto_global
    FROM RankingPorMesCalendario
)
-- Consulta final que muestra los diez meses con mayor aumento porcentual
SELECT 
    puesto_global AS "Puesto General",
    anio_actual AS "Año",
    mes_actual AS "Mes",
    incendios_actual AS "Incendios",
    incendios_anio_anterior AS "Incendios Año Anterior",
    variacion_porcentual AS "Variación Porcentual (%)",
    puesto_mes_calendario AS "Puesto en su Mes Calendario"
FROM RankingGlobalAumento
WHERE puesto_global <= 10
ORDER BY puesto_global ASC;""",
        "interpretacion": (
            """Los resultados muestran los diez meses con mayor crecimiento interanual de
              incendios por encima de la media histórica, eliminando el efecto estacional al 
              comparar cada mes con el mismo mes del año anterior. Destaca marzo de 2006 como el caso más
              crítico tanto por su salto porcentual (+79.76%, pasando de 10,313 a 18,539 incendios) como 
              por ocupar el primer lugar histórico entre los meses de marzo considerados, acompañado por otros
              picos relevantes en sus respectivos calendarios como febrero de 2000 (+62.35%) y julio de 2006 (+52.97%). 
              Asimismo, la tabla evidencia que un gran aumento porcentual no siempre implica un récord absoluto en ese mes 
              como ocurre en marzo de 1999 (+58.25%, puesto 7 en su mes) o abril de 1999 (+40.36%, puesto 8)
              y que los mayores repuntes se concentran principalmente en febrero, marzo, julio y agosto durante los 
              periodos 1999–2002 y 2004–2006."""
        ),
    },
    {
        "id": "q3",
        "titulo": "Pregunta 3: Control en el Mismo Día por Estado",
        "enunciado": (
            "Un incendio se controla en el mismo día cuando su fecha de control"
            " (CONT_DATE) coincide con la de descubrimiento."
        ),
        "sql": """
        """,
        "interpretacion": (
            "**Interpretación:** Aquí puedes sintetizar qué estados mejoraron"
            " más su contención en el mismo día y su brecha frente a la media"
            " nacional del segundo periodo."
        ),
    },
    {
        "id": "q4",
        "titulo": "Pregunta 4: Cambio de Causa Dominante",
        "enunciado": (
            "Se comparan dos periodos de doce años según el año del incendio"
            " (FIRE_YEAR): de 1992 a 2003 y de 2004 a 2015."
        ),
        "sql": """
""",
        "interpretacion": (
            "**Interpretación:** Aquí puedes resumir en qué estados cambió la"
            " causa dominante y cuánto peso conservó la causa anterior en"
            " 2004–2015."
        ),
    },
    {
        "id": "q5",
        "titulo": "Pregunta 5: Franja Horaria de Descubrimiento según la Causa",
        "enunciado": (
            "La hora en que se descubre un incendio (DISCOVERY_TIME, texto con"
            " formato HHMM) revela patrones distintos según su causa."
        ),
        "sql": """
""",
        "interpretacion": (
            "**Interpretación:** Aquí puedes destacar las horas pico y las"
            " franjas de 6 horas con mayor concentración según el origen del"
            " incendio."
        ),
    },
    {
        "id": "q6",
        "titulo": "Pregunta 6: Rachas de Años de Aumento",
        "enunciado": (
            "Se quiere encontrar los estados cuya superficie quemada creció"
            " durante más años seguidos."
        ),
        "sql": """
        """,
        "interpretacion": (
            "**Interpretación:** Aquí puedes comentar los estados con rachas"
            " más largas de crecimiento anual en superficie quemada y el"
            " multiplicador acumulado."
        ),
    },
]

if "nonces_sql" not in st.session_state:
  st.session_state["nonces_sql"] = {item["id"]: 0 for item in PREGUNTAS}

st.title("🦆 Consultas SQL en MotherDuck")
st.caption(f"Base activa: `{BASE_DATOS}`")

for item in PREGUNTAS:
  qid = item["id"]
  with st.container(border=True):
    st.subheader(item["titulo"])
    st.markdown(item["enunciado"])

    with st.expander("📄 Ver código SQL", expanded=False):
      st.code(item["sql"], language="sql")

    col_btn, col_info = st.columns([1.2, 4.8])
    with col_btn:
      if st.button("🔄 Re-ejecutar SQL", key=f"btn_{qid}"):
        st.session_state["nonces_sql"][qid] += 1

    try:
      df_res = ejecutar_consulta_cacheada(
          item["sql"], _nonce=st.session_state["nonces_sql"][qid]
      )
      with col_info:
        st.caption(f"✅ {len(df_res)} filas")
      st.dataframe(df_res, use_container_width=True, hide_index=True)
      st.success(item["interpretacion"])
    except Exception as e:
      st.error(f"Error al ejecutar: {e}")