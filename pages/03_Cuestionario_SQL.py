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
           '''Se comparan dos periodos de doce años según el año del incendio (FIRE_YEAR):
           de 1992 a 2003 y de 2004 a 2015.

Para cada causa y periodo calcula la cantidad de incendios y el porcentaje que representa sobre 
todos los incendios de ese periodo, contando todas las causas. Obtén los dos periodos en una misma 
fila cruzando ese resultado consigo mismo.

Muestra solo las causas cuyos incendios, sumando ambos periodos, alcancen al menos el 1 % de todos 
los incendios de la base. Para cada una indica los incendios y el porcentaje de cada periodo, el cambio 
en puntos porcentuales y su puesto según ese cambio, de mayor a menor. Ordena por puesto.
'''
        ),
        "sql": """WITH TotalesPeriodo AS (
    SELECT 
        CASE 
            WHEN FIRE_YEAR BETWEEN 1992 AND 2003 THEN '1992-2003'
            WHEN FIRE_YEAR BETWEEN 2004 AND 2015 THEN '2004-2015'
        END AS periodo,
        COUNT(*) AS total_periodo
    FROM Fires
    WHERE FIRE_YEAR BETWEEN 1992 AND 2015
    GROUP BY periodo
),
CausaPeriodo AS (
    SELECT 
        STAT_CAUSE_DESCR AS causa,
        CASE 
            WHEN FIRE_YEAR BETWEEN 1992 AND 2003 THEN '1992-2003'
            WHEN FIRE_YEAR BETWEEN 2004 AND 2015 THEN '2004-2015'
        END AS periodo,
        COUNT(*) AS cant_incendios
    FROM Fires
    WHERE FIRE_YEAR BETWEEN 1992 AND 2015
    GROUP BY STAT_CAUSE_DESCR, periodo
),
CausasValidas AS (
    SELECT STAT_CAUSE_DESCR AS causa
    FROM Fires
    WHERE FIRE_YEAR BETWEEN 1992 AND 2015
    GROUP BY STAT_CAUSE_DESCR
    HAVING COUNT(*) >= 0.01 * (SELECT COUNT(*) FROM Fires)
),
CausasConPorcentaje AS (
    SELECT 
        cp.causa,
        cp.periodo,
        cp.cant_incendios,
        ROUND(CAST(cp.cant_incendios AS REAL) * 100.0 / tp.total_periodo, 2) AS porcentaje
    FROM CausaPeriodo cp
    JOIN TotalesPeriodo tp ON cp.periodo = tp.periodo
    WHERE cp.causa IN (SELECT causa FROM CausasValidas)
),
PivotePeriodos AS (
    SELECT 
        p1.causa AS causa,
        p1.cant_incendios AS incendios_p1,
        p1.porcentaje AS porcentaje_p1,
        p2.cant_incendios AS incendios_p2,
        p2.porcentaje AS porcentaje_p2,
        (p2.porcentaje - p1.porcentaje) AS cambio_pp
    FROM CausasConPorcentaje p1
    JOIN CausasConPorcentaje p2 ON p1.causa = p2.causa
    WHERE p1.periodo = '1992-2003' AND p2.periodo = '2004-2015'
)
SELECT 
    causa AS "Causa del Incendio",
    incendios_p1 AS "Incendios Periodo 1992-2003",
    porcentaje_p1 AS "Porcentaje Periodo 1 (%)",
    incendios_p2 AS "Incendios Periodo 2004-2015",
    porcentaje_p2 AS "Porcentaje Periodo 2 (%)",
    cambio_pp AS "Cambio en Puntos Porcentuales",
    RANK() OVER (ORDER BY cambio_pp DESC) AS "Puesto"
FROM PivotePeriodos
ORDER BY "Puesto" ASC;
        """,
        "interpretacion": (
            '''-Más incendios sin causa clara. Miscellaneous y Missing/Undefined pasaron juntas de ~20.8 % a ~30.9 % del total, 
            casi una de cada tres ocurrencias. Probablemente refleja cambios en cómo se registra la causa y no un cambio real 
            en el comportamiento de los incendios, así que conviene decirlo con cautela en las conclusiones.

-Las causas específicas pierden peso. Arson, Lightning, Railroad, Children y Smoking cayeron. 
Parte de esa caída puede deberse a que más casos se clasifican como “Miscellaneous” o “Missing”.

-Cambio de ranking. En el periodo 1 el orden era Debris Burning, Arson, Lightning, Miscellaneous. 
En el periodo 2 es Debris Burning, Miscellaneous, Lightning, Arson.'''
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
            """Un incendio se controla en el mismo día cuando su fecha de control (CONT_DATE) coincide con la de descubrimiento.
              Se quiere saber si esa proporción mejoró con el tiempo.
Trabaja solo con los incendios que tienen fecha de control y compara dos periodos según FIRE_YEAR: de 1992 a 2003 y de 2004 a 2015. 
Calcula por estado y periodo el porcentaje controlado en el mismo día y obtén ambos periodos en una misma fila cruzando ese resultado consigo mismo.
Muestra los estados con al menos 5.000 incendios con fecha de control en cada periodo. 
Para cada uno indica esos incendios y el porcentaje de cada periodo, el cambio en puntos porcentuales, la diferencia entre su porcentaje del segundo periodo y 
el de todo el país en ese periodo (calculado con todos los estados) y su puesto según el cambio, de mayor a menor. Ordena por puesto.
"""
        ),
        "sql": """ WITH IncendiosConControl AS (
    SELECT 
        STATE AS estado,
        FIRE_YEAR AS anio,
        CASE 
            WHEN FIRE_YEAR BETWEEN 1992 AND 2003 THEN '1992-2003'
            WHEN FIRE_YEAR BETWEEN 2004 AND 2015 THEN '2004-2015'
        END AS periodo,
        -- En SQLite, CONT_DATE y DISCOVERY_DATE son días julianos; la igualdad numérica indica el mismo día
        CASE WHEN CONT_DATE = DISCOVERY_DATE THEN 1 ELSE 0 END AS mismo_dia
    FROM Fires
    WHERE CONT_DATE IS NOT NULL 
      AND DISCOVERY_DATE IS NOT NULL 
      AND FIRE_YEAR BETWEEN 1992 AND 2015
),
NacionalPeriodo AS (
    SELECT 
        periodo,
        ROUND(CAST(SUM(mismo_dia) AS REAL) * 100.0 / COUNT(*), 2) AS porcentaje_nacional
    FROM IncendiosConControl
    GROUP BY periodo
),
EstadisticasEstadoPeriodo AS (
    -- Calcula totales y porcentajes por estado y periodo
    SELECT 
        estado,
        periodo,
        COUNT(*) AS total_incendios,
        ROUND(CAST(SUM(mismo_dia) AS REAL) * 100.0 / COUNT(*), 2) AS porcentaje_mismo_dia
    FROM IncendiosConControl
    GROUP BY estado, periodo
),
EstadosValidos AS (
    SELECT estado
    FROM EstadisticasEstadoPeriodo
    WHERE total_incendios >= 5000
    GROUP BY estado
    HAVING COUNT(DISTINCT periodo) = 2
),
PivotePeriodos AS (
    SELECT 
        e1.estado,
        e1.total_incendios AS incendios_p1,
        e1.porcentaje_mismo_dia AS porcentaje_p1,
        e2.total_incendios AS incendios_p2,
        e2.porcentaje_mismo_dia AS porcentaje_p2,
        (e2.porcentaje_mismo_dia - e1.porcentaje_mismo_dia) AS cambio_pp,
        e2.porcentaje_mismo_dia - (SELECT porcentaje_nacional FROM NacionalPeriodo np WHERE np.periodo = '2004-2015') AS dif_nacional_p2
    FROM EstadisticasEstadoPeriodo e1
    JOIN EstadisticasEstadoPeriodo e2 ON e1.estado = e2.estado
    WHERE e1.periodo = '1992-2003' 
      AND e2.periodo = '2004-2015'
      AND e1.estado IN (SELECT estado FROM EstadosValidos)
)
SELECT 
    estado AS "Estado",
    incendios_p1 AS "Incendios en Periodo 1992-2003",
    porcentaje_p1 AS "Porcentaje Mismo Día Periodo 1 (%)",
    incendios_p2 AS "Incendios en Periodo 2004-2015",
    porcentaje_p2 AS "Porcentaje Mismo Día Periodo 2 (%)",
    cambio_pp AS "Cambio en Puntos Porcentuales",
    dif_nacional_p2 AS "Diferencia con la Media Nacional Periodo 2 (pp)",
    RANK() OVER (ORDER BY cambio_pp DESC) AS "Puesto"
FROM PivotePeriodos
ORDER BY "Puesto" ASC;
        """,
        "interpretacion": (
"""Se puede observar que la proporción de incendios controlados en un mismo dia, disminuyo desde el primer periodo de estudio (1992 - 2003) al segundo periodo (2004 - 2015)

De los 20 estados que cumplen con las condiciones, solo 4 lograron aumentar la proporción de incendios controlados en un mismo dia.

Se observan estados que tienen un alto porcentaje de incendios controlados el mismo dia y otros como Idaho que tienen un porcentaje muy bajo"""
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
    SELECT 
        estado,
        periodo,
        COUNT(*) AS total_estado
    FROM BaseFires
    GROUP BY estado, periodo
),
ConteoCausas AS (
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
    SELECT estado, causa, porcentaje_causa
    FROM CausasRankeadas
    WHERE periodo = '2004-2015'
),
PivoteEstados AS (
    SELECT 
        d1.estado,
        d1.causa AS causa_p1,
        d1.porcentaje_causa AS porc_p1,
        d1.cant_causa AS cant_p1,
        d2.causa AS causa_p2,
        d2.porcentaje_causa AS porc_p2,
        d2.cant_causa AS cant_p2,
        (SELECT COALESCE(p.porcentaje_causa, 0.0) 
         FROM PorcentajesPeriodo2 p 
         WHERE p.estado = d1.estado AND p.causa = d1.causa) AS porc_p1_en_p2
    FROM Dominantes d1
    JOIN Dominantes d2 ON d1.estado = d2.estado
    WHERE d1.periodo = '1992-2003' 
      AND d2.periodo = '2004-2015'
      AND d1.causa <> d2.causa -- Filtra solo los estados donde cambió la causa dominante
)
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
                    """ La hora en que se descubre un incendio (DISCOVERY_TIME, texto con formato HHMM) 
                    revela patrones distintos según su causa.
         
        Usa solo los incendios con hora informada y excluye las causas Miscellaneous y Missing/Undefined. 
        Agrupa por causa y hora del día (de 0 a 23). Considera el día como circular: una franja de seis 
        horas consecutivas puede empezar a las 22 y terminar a las 3. Para cada causa determina la hora 
        con más descubrimientos (si hay empate, la menor) y la franja de seis horas consecutivas que 
        concentra más descubrimientos (si hay empate, la de menor hora de inicio).
         
        Incluye solo las causas con descubrimientos en las 24 horas. Muestra la cantidad de incendios con 
        hora, el porcentaje que representan sobre todos los incendios de la causa, la hora pico y el 
        porcentaje que concentra, la hora de inicio y la de fin de la franja, el porcentaje que concentra 
        la franja (estos dos porcentajes, sobre los incendios con hora) y si la franja cruza la medianoche
         ('si' o 'no'). Agrega el puesto de la causa según la concentración de su franja, de mayor a 
         menor, y ordena por ese puesto.
        """
                ),
                "sql": """ WITH FiresValidos AS (
    
    SELECT 
        STAT_CAUSE_DESCR AS causa,
        CAST(DISCOVERY_TIME AS INTEGER) // 100 AS hora
    FROM Fires
    WHERE DISCOVERY_TIME IS NOT NULL 
      AND STAT_CAUSE_DESCR NOT IN ('Miscellaneous', 'Missing/Undefined')
      AND STAT_CAUSE_DESCR IS NOT NULL
),
ConteoCausaHora AS (
    
    SELECT 
        causa,
        hora,
        COUNT(*) AS incendios_hora
    FROM FiresValidos
    WHERE hora BETWEEN 0 AND 23
    GROUP BY causa, hora
),
Causas24H AS (
    
    SELECT causa
    FROM ConteoCausaHora
    GROUP BY causa
    HAVING COUNT(DISTINCT hora) = 24
),
TotalCausaHora AS (
    
    SELECT 
        causa,
        SUM(incendios_hora) AS total_incendios_con_hora
    FROM ConteoCausaHora
    WHERE causa IN (SELECT causa FROM Causas24H)
    GROUP BY causa
),
HoraPicoCausa AS (
    
    SELECT 
        c.causa,
        c.hora AS hora_pico,
        c.incendios_hora AS incendios_pico,
        ROW_NUMBER() OVER (PARTITION BY c.causa ORDER BY c.incendios_hora DESC, c.hora ASC) AS rn_pico
    FROM ConteoCausaHora c
    WHERE c.causa IN (SELECT causa FROM Causas24H)
),
PicoFiltrado AS (
    SELECT causa, hora_pico, incendios_pico
    FROM HoraPicoCausa
    WHERE rn_pico = 1
),
Ventanas6Horas AS (
    
    SELECT 
        t0.causa,
        t0.hora AS hora_inicio,
        ((t0.hora + 5) % 24) AS hora_fin,
        (t0.incendios_hora + t1.incendios_hora + t2.incendios_hora + t3.incendios_hora + t4.incendios_hora + t5.incendios_hora) AS incendios_ventana,
        CASE WHEN t0.hora > (t0.hora + 5) % 24 THEN 'si' ELSE 'no' END AS cruza_medianoche
    FROM ConteoCausaHora t0
    JOIN ConteoCausaHora t1 ON t0.causa = t1.causa AND t1.hora = (t0.hora + 1) % 24
    JOIN ConteoCausaHora t2 ON t0.causa = t2.causa AND t2.hora = (t0.hora + 2) % 24
    JOIN ConteoCausaHora t3 ON t0.causa = t3.causa AND t3.hora = (t0.hora + 3) % 24
    JOIN ConteoCausaHora t4 ON t0.causa = t4.causa AND t4.hora = (t0.hora + 4) % 24
    JOIN ConteoCausaHora t5 ON t0.causa = t5.causa AND t5.hora = (t0.hora + 5) % 24
    WHERE t0.causa IN (SELECT causa FROM Causas24H)
),
MejorVentanaRank AS (
    
    SELECT 
        causa,
        hora_inicio,
        hora_fin,
        incendios_ventana,
        cruza_medianoche,
        ROW_NUMBER() OVER (PARTITION BY causa ORDER BY incendios_ventana DESC, hora_inicio ASC) AS rn_ventana
    FROM Ventanas6Horas
),
MejorVentana AS (
    SELECT causa, hora_inicio, hora_fin, incendios_ventana, cruza_medianoche
    FROM MejorVentanaRank
    WHERE rn_ventana = 1
),
ConsolidadoCausa AS (
    
    SELECT 
        tc.causa,
        tc.total_incendios_con_hora,
        pf.hora_pico,
        ROUND(CAST(pf.incendios_pico AS DOUBLE) * 100.0 / tc.total_incendios_con_hora, 2) AS porcentaje_pico,
        mv.hora_inicio,
        mv.hora_fin,
        ROUND(CAST(mv.incendios_ventana AS DOUBLE) * 100.0 / tc.total_incendios_con_hora, 2) AS porcentaje_ventana,
        mv.cruza_medianoche
    FROM TotalCausaHora tc
    JOIN PicoFiltrado pf ON tc.causa = pf.causa
    JOIN MejorVentana mv ON tc.causa = mv.causa
),
RankingFinal AS (
    
    SELECT 
        causa,
        total_incendios_con_hora,
        hora_pico,
        porcentaje_pico,
        hora_inicio,
        hora_fin,
        porcentaje_ventana,
        cruza_medianoche,
        RANK() OVER (ORDER BY porcentaje_ventana DESC) AS puesto_causa
    FROM ConsolidadoCausa
)

SELECT 
    puesto_causa AS "Puesto",
    causa AS "Causa del Incendio",
    total_incendios_con_hora AS "Incendios con Hora",
    hora_pico AS "Hora Pico",
    porcentaje_pico AS "Porcentaje Hora Pico (%)",
    hora_inicio AS "Hora de Inicio Franja",
    hora_fin AS "Hora de Fin Franja",
    porcentaje_ventana AS "Porcentaje Franja 6 Horas (%)",
    cruza_medianoche AS "Cruza Medianoche"
FROM RankingFinal
ORDER BY puesto_causa ASC;
        """,
                "interpretacion": (
                    """ Según lo pedido, se excluyen Miscellaneous y Missing/Undefined, quedan 11
                    causas, ninguna franja cruza la medianoche y se usan solo incendios con hora
                    de 0 a 23. Las agrupaciones por hora de inicio y fin se distribuyen en 
                    jornadas diurnas y vespertinas (se concentran entre las 11:00 y las 18:00,
                    esto indica mayor calor, menor humedad y más actividad al aire libre de
                    la población), estas son de 11 a 16 (Equipment Use y Campfire), 12 a 17
                    (Debris Burning, Railroad, Smoking, Powerline, Arson y Structure), 13
                    a 18 (Children, Lightning y Fireworks). Las horas pico son las 14 
                    (Debris Burning, Railroad, Equipment Use, Smoking, Powerline, Campfire, 
                    Arson, Structure), las 16 (Children, Lightning) y las 22 (Fireworks, única 
                    excepción nocturna). Por concentración, el primero es Debris Burning con 73,46%  
                    y 16,29% en hora pico (de 198.098 incendios), en el puesto medio está Children con 
                    62,46% en franja y 12,43% en hora pico (29.349 de incendios), y en el último 
                    puesto Fireworks con 47,78% en franja y 9,43 % en hora pico (10.505 de incendios), 
                    evidenciando mayor dispersión entre el día y la noche. Para concluir, Powerline 
                    queda en el puesto 5 por debajo de Smoking (63,91% vs. 65,32% en franja), a pesar
                     de tener mayor pico (13,51% vs. 13,42%). 
        """
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