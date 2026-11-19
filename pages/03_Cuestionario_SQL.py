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

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
if not MOTHERDUCK_TOKEN:
    try:
        MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
    except Exception:
        MOTHERDUCK_TOKEN = None

if not MOTHERDUCK_TOKEN:
    st.error("No se encontró MOTHERDUCK_TOKEN en las variables de entorno ni en secrets.toml.")
    st.stop()

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
            """Se comparan dos periodos de doce años según el año del incendio (FIRE_YEAR): de 1992 a 2003 y de 2004 a 2015.
            Interesa saber en qué estados cambió la causa que más incendios provoca.

Excluye las causas Miscellaneous y Missing/Undefined, que no identifican un origen real. La causa dominante de un estado
en un periodo es la que tiene más incendios; en caso de empate, la primera en orden alfabético. Los porcentajes se calculan 
sobre los incendios del estado en ese periodo, ya sin las dos causas excluidas.

Lista los estados cuya causa dominante es distinta en los dos periodos. Muestra la causa dominante de cada periodo con su 
porcentaje, el porcentaje que conserva en el segundo periodo la causa que dominaba en el primero, y la suma de los incendios 
de ambas causas dominantes (cada una contada en su propio periodo). Ordena por estado.
"""
        ),
        "sql": """WITH BaseFires AS (
    -- Filtra los años y excluye las causas indicadas
    SELECT 
        STATE AS estado,
        STAT_CAUSE_DESCR AS causa,
        CASE 
            WHEN FIRE_YEAR BETWEEN 1992 AND 2003 THEN '1992-2003'
            WHEN FIRE_YEAR BETWEEN 2004 AND 2015 THEN '2004-2015'
        END AS periodo
    FROM Fires
    WHERE FIRE_YEAR BETWEEN 1992 AND 2015
      AND STAT_CAUSE_DESCR NOT IN ('Miscellaneous', 'Missing/Undefined')
      AND STATE IS NOT NULL
),
TotalEstadoPeriodo AS (
    -- Total de incendios válidos por estado y periodo (para calcular porcentajes reales)
    SELECT 
        estado,
        periodo,
        COUNT(*) AS total_estado
    FROM BaseFires
    GROUP BY estado, periodo
),
ConteoCausas AS (
    -- Conteo de incendios por causa, estado y periodo
    SELECT 
        bf.estado,
        bf.periodo,
        bf.causa,
        COUNT(*) AS cant_causa,
        tep.total_estado
    FROM BaseFires bf
    JOIN TotalEstadoPeriodo tep ON bf.estado = tep.estado AND bf.periodo = tep.periodo
    GROUP BY bf.estado, bf.periodo, bf.causa, tep.total_estado
),
CausasRankeadas AS (
    -- Función de ventana: Asigna un ranking ordenando por cantidad descendente y por orden alfabético en caso de empate
    SELECT 
        estado,
        periodo,
        causa,
        cant_causa,
        ROUND(CAST(cant_causa AS REAL) * 100.0 / total_estado, 2) AS porcentaje_causa,
        ROW_NUMBER() OVER (PARTITION BY estado, periodo ORDER BY cant_causa DESC, causa ASC) as rnk
    FROM ConteoCausas
),
Dominantes AS (
    -- Filtra únicamente la causa dominante (puesto 1) de cada estado y periodo
    SELECT 
        estado,
        periodo,
        causa,
        cant_causa,
        porcentaje_causa
    FROM CausasRankeadas
    WHERE rnk = 1
),
PorcentajesPeriodo2 AS (
    -- CTE auxiliar con los porcentajes de todas las causas en el periodo 2
    SELECT estado, causa, porcentaje_causa
    FROM CausasRankeadas
    WHERE periodo = '2004-2015'
),
PivoteEstados AS (
    -- SELF JOIN: Cruza la tabla de dominantes del periodo 1 con la del periodo 2 para el mismo estado
    SELECT 
        d1.estado,
        d1.causa AS causa_p1,
        d1.porcentaje_causa AS porc_p1,
        d1.cant_causa AS cant_p1,
        d2.causa AS causa_p2,
        d2.porcentaje_causa AS porc_p2,
        d2.cant_causa AS cant_p2,
        -- Subconsulta para obtener el porcentaje exacto que conserva en el periodo 2 la causa que dominaba en el periodo 1
        (SELECT COALESCE(p.porcentaje_causa, 0.0) 
         FROM PorcentajesPeriodo2 p 
         WHERE p.estado = d1.estado AND p.causa = d1.causa) AS porc_p1_en_p2
    FROM Dominantes d1
    JOIN Dominantes d2 ON d1.estado = d2.estado
    WHERE d1.periodo = '1992-2003' 
      AND d2.periodo = '2004-2015'
      AND d1.causa <> d2.causa -- Filtra solo los estados donde cambió la causa dominante
)
-- Consulta final con alias descriptivos en español ordenados por estado
SELECT 
    estado AS "Estado",
    causa_p1 AS "Causa Dominante Periodo 1 (1992-2003)",
    porc_p1 AS "Porcentaje Periodo 1 (%)",
    causa_p2 AS "Causa Dominante Periodo 2 (2004-2015)",
    porc_p2 AS "Porcentaje Periodo 2 (%)",
    porc_p1_en_p2 AS "Porcentaje de Causa 1 en Periodo 2 (%)",
    (cant_p1 + cant_p2) AS "Suma de Incendios de Ambas Causas Dominantes"
FROM PivoteEstados
ORDER BY estado ASC;
""",
        "interpretacion": (
            """ **Cambio dominante de Arson a Debris Burning:** De los 18 estados donde cambió la causa principal, 
            en la mayoría fueron en 10 estados (AR, CT, IL, KY, MA, MD, MS, OH, TN, WV) Arson lideraba entre 1992–2003, 
            pero entre 2004–2015 fue desplazado por Debris Burning, llegando a superar el 65% de los incendios en estados 
            como OH (70.69%) y KY (66.36%). 
            
            **Caídas drásticas vs. relevos reñidos:** En estados como FL Railroad pasó de 32.54% en 1992-2003 a 0.84% en 
            2004-2015 o DE Arson bajó de 43.18% en 1992-2003 a 3.51% en 1992-2003. Prácticamente la causa original no solo 
            perdió el liderazgo, sino que dejó de ser relevante. En cambio, en AL, MN o SD, ambas causas quedaron casi 
            empatadas en el segundo periodo. 

"""
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
            """Se quiere encontrar los estados cuya superficie quemada creció durante más años 
            seguidos.

Calcula la superficie quemada por estado y año (FIRE_YEAR). Un año es de aumento si su superficie supera 
estrictamente la del año anterior del mismo estado; esa comparación debe hacerse cruzando la serie 
consigo misma. Una racha es una secuencia de años de aumento consecutivos. Para cada estado toma su 
racha más larga y, si hay empate, la más antigua.

Considera solo los estados con datos en los 24 años. Muestra los diez estados con rachas más 
largas, con su puesto (los empates comparten puesto), el primer y el último año de aumento, la 
cantidad de años, la superficie del año anterior al inicio de la racha, la superficie del último 
año de la racha y el cociente entre ambas. Ordena por puesto y, en caso de empate, por estado.
"""
        ),
        "sql": """WITH SuperficieAnualEstado AS (
    
    SELECT 
        STATE AS estado,
        FIRE_YEAR AS anio,
        SUM(FIRE_SIZE) AS superficie_total
    FROM Fires
    WHERE STATE IS NOT NULL 
      AND FIRE_YEAR BETWEEN 1992 AND 2015
    GROUP BY STATE, FIRE_YEAR
),
Estados24Anios AS (
    
    SELECT estado
    FROM SuperficieAnualEstado
    GROUP BY estado
    HAVING COUNT(DISTINCT anio) = 24
),
ComparacionAnual AS (
    
    SELECT 
        curr.estado,
        curr.anio,
        curr.superficie_total AS sup_actual,
        prev.superficie_total AS sup_anterior,
        CASE WHEN curr.superficie_total > prev.superficie_total THEN 1 ELSE 0 END AS es_aumento
    FROM SuperficieAnualEstado curr
    JOIN SuperficieAnualEstado prev ON curr.estado = prev.estado AND curr.anio = prev.anio + 1
    WHERE curr.estado IN (SELECT estado FROM Estados24Anios)
),
AumentosPuros AS (
    
    SELECT 
        estado,
        anio,
        sup_actual,
        sup_anterior,
        -- Técnica de secuencia (Gaps and Islands): resta una fila de numeración para agrupar rachas consecutivas
        anio - ROW_NUMBER() OVER (PARTITION BY estado ORDER BY anio) AS grupo_racha
    FROM ComparacionAnual
    WHERE es_aumento = 1
),
RachasCalculadas AS (
    
    SELECT 
        estado,
        grupo_racha,
        MIN(anio) - 1 AS anio_previo_inicio, -- El año anterior al inicio de la racha es anio_inicio - 1
        MIN(anio) AS primer_anio_aumento,
        MAX(anio) AS ultimo_anio_aumento,
        COUNT(*) AS cantidad_anios
    FROM AumentosPuros
    GROUP BY estado, grupo_racha
),
RachasConSuperficies AS (
   
    SELECT 
        r.estado,
        r.primer_anio_aumento,
        r.ultimo_anio_aumento,
        r.cantidad_anios,
        s_ant.superficie_total AS superficie_anio_anterior_inicio,
        s_fin.superficie_total AS superficie_ultimo_anio
    FROM RachasCalculadas r
    JOIN SuperficieAnualEstado s_ant ON r.estado = s_ant.estado AND s_ant.anio = r.anio_previo_inicio
    JOIN SuperficieAnualEstado s_fin ON r.estado = s_fin.estado AND s_fin.anio = r.ultimo_anio_aumento
),
MejorRachaPorEstado AS (
   
    SELECT 
        estado,
        primer_anio_aumento,
        ultimo_anio_aumento,
        cantidad_anios,
        superficie_anio_anterior_inicio,
        superficie_ultimo_anio,
        ROUND(CAST(superficie_ultimo_anio AS REAL) / superficie_anio_anterior_inicio, 2) AS cociente_superficie,
        ROW_NUMBER() OVER (PARTITION BY estado ORDER BY cantidad_anios DESC, primer_anio_aumento ASC) AS rn_mejor
    FROM RachasConSuperficies
),
FiltradoMejores AS (
    SELECT 
        estado,
        primer_anio_aumento,
        ultimo_anio_aumento,
        cantidad_anios,
        superficie_anio_anterior_inicio,
        superficie_ultimo_anio,
        cociente_superficie
    FROM MejorRachaPorEstado
    WHERE rn_mejor = 1
),
RankingGlobalRachas AS (

    SELECT 
        estado,
        primer_anio_aumento,
        ultimo_anio_aumento,
        cantidad_anios,
        superficie_anio_anterior_inicio,
        superficie_ultimo_anio,
        cociente_superficie,
        DENSE_RANK() OVER (ORDER BY cantidad_anios DESC) AS puesto
    FROM FiltradoMejores
)

SELECT 
    puesto AS "Puesto",
    estado AS "Estado",
    primer_anio_aumento AS "Primer Año de Aumento",
    ultimo_anio_aumento AS "Último Año de Aumento",
    cantidad_anios AS "Cantidad de Años en Racha",
    superficie_anio_anterior_inicio AS "Superficie Año Anterior al Inicio",
    superficie_ultimo_anio AS "Superficie Último Año de la Racha",
    cociente_superficie AS "Cociente de Superficie",
    puesto AS "Puesto Compartido"
FROM RankingGlobalRachas
WHERE puesto <= 10
ORDER BY puesto ASC, estado ASC;
        """,
        "interpretacion": (
            """Interpretación de resultados
La consulta busca qué estados con datos completos de 1992 a 2015 tuvieron más años seguidos 
aumentando su superficie quemada y calcula cuánto creció al final de su mejor racha. En los 
resultados lidera AR con 8 años seguidos, seguido por LA con 6 y KY con 5, mientras que en los 
puestos siguientes se acumulan empates y casos como KS muestran cambios proporcionales enormes en 
rachas cortas. Esto sugiere que ir subiendo año tras año refleja condiciones que se van acumulando 
con el tiempo, mientras que los saltos bruscos en pocos años apuntan a momentos puntuales muy fuertes 
más que a una tendencia larga.
"""
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