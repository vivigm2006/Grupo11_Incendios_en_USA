"""
Analisis de resultados 

Investigacion: Incendios forestales y segmentacion territorial (1992-2015):
Analisis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
"""
import os
import time
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Análisis de Resultados",
    page_icon="📊",
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

REF = '"incendios_usa"."main"."vista_general_detallada"'


@st.cache_resource
def get_connection():
    return duckdb.connect(f"md:?motherduck_token={MOTHERDUCK_TOKEN}")


def ejecutar_sql(query: str, params=None) -> pd.DataFrame:
    con = get_connection()
    for intento in range(3):
        try:
            if params is not None:
                return con.execute(query, params).df()
            return con.sql(query).df()
        except duckdb.Error as e:
            if "DEADLINE_EXCEEDED" in str(e) and intento < 2:
                time.sleep(2 * (intento + 1))
            else:
                raise


@st.cache_data(ttl=3600)
def cargar_catalogos():
    regiones = ejecutar_sql(
        f"SELECT DISTINCT region_nifc FROM {REF} WHERE region_nifc IS NOT NULL ORDER BY 1"
    )["region_nifc"].tolist()
    propietarios = ejecutar_sql(
        f"SELECT DISTINCT tipo_administracion FROM {REF} WHERE tipo_administracion IS NOT NULL ORDER BY 1"
    )["tipo_administracion"].tolist()
    causas = ejecutar_sql(
        f"SELECT DISTINCT origen_causa FROM {REF} WHERE origen_causa IS NOT NULL ORDER BY 1"
    )["origen_causa"].tolist()
    anios = ejecutar_sql(
        f"SELECT DISTINCT anio FROM {REF} WHERE anio IS NOT NULL ORDER BY 1"
    )["anio"].tolist()
    return regiones, propietarios, causas, anios


def construir_where(regiones, propietarios, causas, rango_anios):
    if not regiones or not propietarios or not causas:
        return "WHERE 1=0", []

    clauses = [
        f"region_nifc IN ({','.join(['?'] * len(regiones))})",
        f"tipo_administracion IN ({','.join(['?'] * len(propietarios))})",
        f"origen_causa IN ({','.join(['?'] * len(causas))})",
        "anio BETWEEN ? AND ?",
    ]
    params = list(regiones) + list(propietarios) + list(causas) + [rango_anios[0], rango_anios[1]]
    return "WHERE " + " AND ".join(clauses), params


@st.cache_data(ttl=3600)
def obtener_metricas_generales(regiones, propietarios, causas, rango_anios):
    where_sql, params = construir_where(regiones, propietarios, causas, rango_anios)
    q_general = f"""
        SELECT
            COUNT(*) AS total_incendios,
            COALESCE(SUM(superficie_acres), 0) AS total_acres,
            COALESCE(AVG(superficie_acres), 0) AS media_acres,
            COALESCE(MAX(superficie_acres), 0) AS max_acres,
            SUM(CASE WHEN origen_causa = 'Natural' THEN 1 ELSE 0 END) AS n_natural,
            SUM(CASE WHEN origen_causa = 'Humana' THEN 1 ELSE 0 END) AS n_humana,
            SUM(CASE WHEN clase = 'G' THEN 1 ELSE 0 END) AS n_megaincendios,
            AVG(CASE WHEN tiene_contencion = 1 THEN dias_contencion END) AS prom_dias_contencion,
            MAX(CASE WHEN tiene_contencion = 1 AND dias_contencion <= 365 THEN dias_contencion END) AS max_dias_contencion
        FROM {REF}
        {where_sql}
    """
    general = ejecutar_sql(q_general, params).iloc[0].to_dict()

    q_region_max = f"""
        SELECT region_nifc, SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY region_nifc
        ORDER BY acres DESC
        LIMIT 1
    """
    df_reg = ejecutar_sql(q_region_max, params)

    q_est_count = f"""
        SELECT estado, region_nifc, COUNT(objectid) AS total
        FROM {REF}
        {where_sql}
        GROUP BY estado, region_nifc
        ORDER BY total DESC
        LIMIT 1
    """
    df_est_cnt = ejecutar_sql(q_est_count, params)

    q_est_sup = f"""
        SELECT estado, region_nifc, SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY estado, region_nifc
        ORDER BY acres DESC
        LIMIT 1
    """
    df_est_sup = ejecutar_sql(q_est_sup, params)

    q_mes_max = f"""
        SELECT nombre_mes, SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY nombre_mes
        ORDER BY acres DESC
        LIMIT 1
    """
    df_mes_max = ejecutar_sql(q_mes_max, params)

    q_estacion_pico = f"""
        SELECT estacion, COUNT(*) AS total
        FROM {REF}
        {where_sql}
        GROUP BY estacion
        ORDER BY total DESC
        LIMIT 1
    """
    df_estacion = ejecutar_sql(q_estacion_pico, params)

    q_prom_anual = f"""
        SELECT COALESCE(AVG(acres_anio), 0) AS promedio_anual
        FROM (
            SELECT anio, SUM(superficie_acres) AS acres_anio
            FROM {REF}
            {where_sql}
            GROUP BY anio
        )
    """
    prom_anual = float(ejecutar_sql(q_prom_anual, params).iloc[0]["promedio_anual"])

    return {
        "general": general,
        "region_max": df_reg.iloc[0].to_dict() if not df_reg.empty else None,
        "est_count": df_est_cnt.iloc[0].to_dict() if not df_est_cnt.empty else None,
        "est_sup": df_est_sup.iloc[0].to_dict() if not df_est_sup.empty else None,
        "mes_max": df_mes_max.iloc[0].to_dict() if not df_mes_max.empty else None,
        "estacion_pico": df_estacion.iloc[0].to_dict() if not df_estacion.empty else None,
        "promedio_anual": prom_anual,
    }


@st.cache_data(ttl=3600)
def obtener_datos_graficos(regiones, propietarios, causas, rango_anios):
    where_sql, params = construir_where(regiones, propietarios, causas, rango_anios)

    # Objetivo 1: Treemap
    df_treemap = ejecutar_sql(
        f"""
        SELECT region_nifc, clase, SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY region_nifc, clase
        """,
        params,
    )

    # Objetivo 2: Causas por región
    df_causas = ejecutar_sql(
        f"""
        SELECT region_nifc, origen_causa, COUNT(objectid) AS cantidad
        FROM {REF}
        {where_sql}
        GROUP BY region_nifc, origen_causa
        """,
        params,
    )

    # Objetivo 3: Megaincendios por región
    df_mega = ejecutar_sql(
        f"""
        SELECT
            region_nifc,
            COUNT(*) AS n_megaincendios,
            SUM(superficie_acres) AS acres_totales
        FROM {REF}
        {where_sql} AND es_megaincendio = 1
        GROUP BY region_nifc
        ORDER BY n_megaincendios ASC
        """,
        params,
    )

    # Objetivo 4: Propietario / administración
    df_admin_clase = ejecutar_sql(
        f"""
        SELECT
            tipo_administracion,
            clase,
            COUNT(objectid) AS total_incendios,
            SUM(superficie_acres) AS total_acres
        FROM {REF}
        {where_sql}
        GROUP BY tipo_administracion, clase
        """,
        params,
    )

    df_contencion = ejecutar_sql(
        f"""
        SELECT
            tipo_administracion,
            CASE
                WHEN dias_contencion <= 0 THEN 'Mismo día'
                WHEN dias_contencion <= 1 THEN '1 día'
                WHEN dias_contencion <= 7 THEN '2-7 días'
                WHEN dias_contencion <= 30 THEN '8-30 días'
                ELSE 'Más de 30 días'
            END AS rango,
            COUNT(*) AS total
        FROM {REF}
        {where_sql} AND tiene_contencion = 1 AND dias_contencion <= 365
        GROUP BY tipo_administracion, rango
        """,
        params,
    )

    df_excluidos = ejecutar_sql(
        f"""
        SELECT COUNT(*) AS excluidos
        FROM {REF}
        {where_sql} AND tiene_contencion = 1 AND dias_contencion > 365
        """,
        params,
    )
    n_excluidos = int(df_excluidos.iloc[0]["excluidos"])

    # Objetivo 5: Estacionalidad
    df_meses = ejecutar_sql(
        f"""
        SELECT
            mes,
            estacion,
            COUNT(*) AS incendios,
            SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY mes, estacion
        """,
        params,
    )

    df_region_mes = ejecutar_sql(
        f"""
        SELECT
            region_nifc,
            mes,
            SUM(superficie_acres) AS acres
        FROM {REF}
        {where_sql}
        GROUP BY region_nifc, mes
        """,
        params,
    )

    return {
        "treemap": df_treemap,
        "causas": df_causas,
        "mega": df_mega,
        "admin_clase": df_admin_clase,
        "contencion": df_contencion,
        "n_excluidos": n_excluidos,
        "meses": df_meses,
        "region_mes": df_region_mes,
    }


regiones_disp, propietarios_disp, causas_disp, anios_disponibles = cargar_catalogos()

with st.sidebar:
    st.title("Filtro a aplicar")
    st.caption("Selección de la parte de la investigación a filtrar")

    select_region = st.multiselect(
        "Seleccione la región de interés",
        regiones_disp,
        default=regiones_disp,
    )

    select_propietario = st.pills(
        "Seleccione el tipo de propietario",
        propietarios_disp,
        default=propietarios_disp,
        selection_mode="multi",
    )

    select_causa = st.segmented_control(
        "Seleccione la causa del incendio",
        causas_disp,
        default=causas_disp,
        selection_mode="multi",
    )

    select_anio = st.select_slider(
        "Seleccione el rango de años",
        options=anios_disponibles,
        value=(anios_disponibles[0], anios_disponibles[-1]),
    )


def tarjeta_metrica(titulo, valor, subtitulo=""):
    st.markdown(
        f"""
        <div style="
            padding: 16px; 
            border-radius: 8px; 
            background-color: #962323; 
            border: 1px solid #CC1D1D;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            height: 100%;">
            <p style="margin: 0; font-size: 13px; color: #000000; font-weight: 600;">{titulo}</p>
            <p style="margin: 6px 0 0 0; font-size: 20px; font-weight: bold; color: #000000;">{valor}</p>
            {"<p style='margin: 4px 0 0 0; font-size: 12px; color: #000000;'>" + subtitulo + "</p>" if subtitulo else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


metricas = obtener_metricas_generales(
    tuple(select_region),
    tuple(select_propietario),
    tuple(select_causa),
    tuple(select_anio),
)
datos = obtener_datos_graficos(
    tuple(select_region),
    tuple(select_propietario),
    tuple(select_causa),
    tuple(select_anio),
)

gen = metricas["general"]
total_incendios = int(gen["total_incendios"] or 0)

tab1, tab2, tab3 = st.tabs(["🗺️ Impacto Territorial", "📊 Causas y severidad", "📈 Gestión y estacionalidad"])

# ==================== OBJETIVO 1 ====================
with tab1:
    st.header("Distribución Regional de Superficie Afectada y Severidad del Fuego")
    st.markdown(
        """Evaluación comparativa de la magnitud del impacto territorial para la
        identificación de zonas de alta susceptibilidad y destrucción."""
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        total_acres = float(gen["total_acres"] or 0)
        tarjeta_metrica(
            titulo="Total superficie quemada",
            valor=f"{total_acres:,.2f}",
            subtitulo="acres",
        )
    with col2:
        if metricas["region_max"] is not None:
            region_max = metricas["region_max"]["region_nifc"]
            acres_max = float(metricas["region_max"]["acres"] or 0)
            sub_region = f"{acres_max:,.0f} acres"
        else:
            region_max = "Sin datos"
            sub_region = ""

        tarjeta_metrica(
            titulo="Región más afectada",
            valor=region_max,
            subtitulo=sub_region,
        )
    with col3:
        media_acres = float(gen["media_acres"] or 0)
        tarjeta_metrica(
            titulo="Superficie media por incendio",
            valor=f"{media_acres:,.2f}",
            subtitulo="acres",
        )

    ORDEN_CLASES = ["A", "B", "C", "D", "E", "F", "G"]
    COLORES_CLASE = dict(zip(ORDEN_CLASES, px.colors.sequential.YlOrRd[1:8]))
    COLORES_CLASE["(?)"] = "#333333"

    resumen = datos["treemap"].copy()
    if not resumen.empty:
        acres_region = resumen.groupby("region_nifc")["acres"].sum()
        resumen["region_label"] = resumen["region_nifc"].map(
            lambda r: f"{r} ({acres_region[r] / 1e6:.1f}M ac)"
        )

        fig_treemap = px.treemap(
            resumen,
            path=[px.Constant("Total"), "region_label", "clase"],
            values="acres",
            color="clase",
            color_discrete_map=COLORES_CLASE,
            title="Superficie Quemada por Región y Clase de Incendio (Acres)",
            template="plotly_dark",
        )
        fig_treemap.update_traces(
            textinfo="label+percent parent",
            hovertemplate="%{label}<br>%{value:,.0f} acres<br>%{percentParent:.1%} de su grupo<extra></extra>",
        )
        fig_treemap.update_layout(
            height=600,
            uniformtext=dict(minsize=10, mode="hide"),
            margin=dict(t=60, l=10, r=10, b=10),
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.caption(
            "Clases por tamaño final: A ≤ 0.25 acres · B 0.26–9.9 · C 10–99.9 · "
            "D 100–299 · E 300–999 · F 1,000–4,999 · G ≥ 5,000."
        )
    else:
        st.warning("No hay registros para mostrar con los filtros seleccionados.")

# ==================== OBJETIVO 2 Y 3 ====================
with tab2:
    st.header("Patrones de Ignición y Fuentes de Causa por Región")
    st.markdown(
        """Análisis de la relación entre el origen del fuego (humano vs. natural) y la ubicación
        geográfica para determinar la dinámica de las fuentes de inicio."""
    )

    col4, col5 = st.columns(2)

    with col4:
        if metricas["est_count"] is not None:
            est_count = metricas["est_count"]["estado"]
            reg_count = metricas["est_count"]["region_nifc"]
            val_count = int(metricas["est_count"]["total"])
            txt_count = (
                f"{est_count} <span style='font-size: 14px; color: #261E1E;'>({reg_count})</span><br>"
                f"<span style='font-size: 16px; font-weight: normal; color: #261E1E;'>{val_count:,} incendios</span>"
            )
        else:
            txt_count = "Sin datos"

        tarjeta_metrica(
            titulo="Mayor frecuencia de incendios",
            valor=txt_count,
            subtitulo="Estado y Región",
        )

    with col5:
        if total_incendios > 0:
            nat = int(gen["n_natural"] or 0)
            hum = int(gen["n_humana"] or 0)
            pct_nat = (nat / total_incendios) * 100
            pct_hum = (hum / total_incendios) * 100
            val_causas = f"⚡ Natural: {pct_nat:.1f}%<br>👥 Humana: {pct_hum:.1f}%"
        else:
            val_causas = "Sin datos"

        tarjeta_metrica(
            titulo="Distribución por tipo de causa",
            valor=val_causas,
            subtitulo=f"Sobre {total_incendios:,} incendios",
        )

    st.subheader("Proporción de Fuentes de Ignición por Región NIFC")
    df_chart = datos["causas"]

    if not df_chart.empty:
        fig = px.bar(
            df_chart,
            x="region_nifc",
            y="cantidad",
            color="origen_causa",
            title="Cantidad total de incendios por Región y su origen",
            labels={
                "region_nifc": "Región NIFC",
                "cantidad": "Número de Incendios",
                "origen_causa": "Origen de la Causa",
            },
            barmode="stack",
            color_discrete_map={"Humana": "#c7b422", "Natural": "#d42d1b"},
        )
        fig.update_layout(
            xaxis_title="Región",
            yaxis_title="Cantidad de Incendios",
            legend_title="Origen",
            yaxis=dict(tickformat=","),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos filtrados para mostrar el gráfico de proporciones de causa.")

    st.markdown("---")

    # Objetivo 3
    st.header("Concentración Territorial de Incendios de Alta Severidad y Mega-Incendios")
    st.markdown(
        """Cuantificación de eventos críticos a nivel nacional e identificación de las 
        regiones con mayor vulnerabilidad a eventos de gran magnitud."""
    )

    col6, col7, col8 = st.columns(3)

    with col6:
        n_megaincendios = int(gen["n_megaincendios"] or 0)
        tarjeta_metrica(
            titulo="Total de megaincendios",
            valor=f"{n_megaincendios:,}",
            subtitulo="Incendios clase G",
        )

    with col7:
        max_acres = float(gen["max_acres"] or 0)
        tarjeta_metrica(
            titulo="Máxima extensión registrada",
            valor=f"{max_acres:,.2f}",
            subtitulo="acres en un solo evento",
        )

    with col8:
        if metricas["est_sup"] is not None:
            est_sup = metricas["est_sup"]["estado"]
            reg_sup = metricas["est_sup"]["region_nifc"]
            val_sup = float(metricas["est_sup"]["acres"] or 0)
            txt_sup = (
                f"{est_sup} <span style='font-size: 14px; color: #261E1E;'>({reg_sup})</span><br>"
                f"<span style='font-size: 16px; font-weight: normal; color: #261E1E;'>{val_sup:,.0f} acres</span>"
            )
        else:
            txt_sup = "Sin datos"

        tarjeta_metrica(
            titulo="Mayor superficie quemada",
            valor=txt_sup,
            subtitulo="Estado y Región",
        )

    st.subheader("Mega-Incendios por Región NIFC")
    st.markdown("Comparación entre el número de eventos y la superficie total quemada en cada región.")

    por_region = datos["mega"]

    if not por_region.empty:
        orden_regiones = por_region["region_nifc"].tolist()

        df_largo = por_region.melt(
            id_vars="region_nifc",
            value_vars=["n_megaincendios", "acres_totales"],
            var_name="metrica",
            value_name="valor",
        )
        df_largo["metrica"] = df_largo["metrica"].map(
            {
                "n_megaincendios": "Número de mega-incendios",
                "acres_totales": "Superficie quemada (acres)",
            }
        )

        fig_regiones = px.bar(
            df_largo,
            x="valor",
            y="region_nifc",
            facet_col="metrica",
            orientation="h",
            text_auto=".3~s",
            category_orders={
                "region_nifc": orden_regiones,
                "metrica": ["Número de mega-incendios", "Superficie quemada (acres)"],
            },
            title="Mega-Incendios por Región NIFC: Eventos vs. Superficie Quemada",
            labels={"valor": "", "region_nifc": "Región NIFC"},
            template="plotly_dark",
        )
        fig_regiones.update_xaxes(matches=None, showticklabels=True)
        fig_regiones.update_xaxes(range=[0, por_region["n_megaincendios"].max() * 1.2], col=1)
        fig_regiones.update_xaxes(range=[0, por_region["acres_totales"].max() * 1.2], col=2)
        fig_regiones.update_traces(
            marker_color="#FF7F0E",
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>",
        )
        fig_regiones.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_regiones.update_layout(
            showlegend=False,
            height=max(400, 55 * len(por_region) + 150),
        )
        st.plotly_chart(fig_regiones, use_container_width=True)
    else:
        st.warning("No hay mega-incendios para mostrar con los filtros seleccionados.")

# ==================== OBJETIVO 4 Y 5 ====================
with tab3:
    st.header("Impacto y Tiempo de Contención según el propietario del Suelo")
    st.markdown(
        """Análisis comparativo de la severidad y respuesta operativa entre 
        terrenos bajo administración federal y tierras estatales o privadas."""
    )

    col9, col10, col11 = st.columns(3)
    df_admin_clase = datos["admin_clase"]

    with col9:
        if not df_admin_clase.empty:
            df_prop = (
                df_admin_clase.groupby("tipo_administracion")
                .agg(
                    total_incendios=("total_incendios", "sum"),
                    total_acres=("total_acres", "sum"),
                )
                .reset_index()
            )
            prop_incendios = df_prop.loc[df_prop["total_incendios"].idxmax()]
            prop_acres = df_prop.loc[df_prop["total_acres"].idxmax()]

            val_prop = (
                f"<b>Más frecuencia:</b> {prop_incendios['tipo_administracion']} "
                f"({int(prop_incendios['total_incendios']):,})<br>"
                f"<b>Mayor superficie:</b> {prop_acres['tipo_administracion']} ({prop_acres['total_acres']:,.0f} ac)"
            )
        else:
            val_prop = "Sin datos"

        tarjeta_metrica(
            titulo="Propietario dominante (3 categorías)",
            valor=val_prop,
            subtitulo="Basado en Federal, Estatal y Privado",
        )

    with col10:
        prom_dias = float(gen["prom_dias_contencion"] or 0)
        tarjeta_metrica(
            titulo="Tiempo promedio de contencion",
            valor=f"{prom_dias:.1f} días",
            subtitulo="Duración media por evento",
        )

    with col11:
        max_dias = float(gen["max_dias_contencion"] or 0)
        tarjeta_metrica(
            titulo="Tiempo máximo de contención",
            valor=f"{max_dias:.0f} días",
            subtitulo="Mayor duración registrada",
        )

    st.subheader("Severidad y Rapidez de Contención por Tipo de Administración")
    ORDEN_ADMIN = ["Federal", "Estatal/Local", "Privada"]
    ORDEN_CLASES = ["A", "B", "C", "D", "E", "F", "G"]
    RANGOS_CONTENCION = ["Mismo día", "1 día", "2-7 días", "8-30 días", "Más de 30 días"]

    def heatmap_desde_agregado(df_agg, col_x, col_val, orden_columnas, titulo, etiqueta_x, n_por_admin):
        tabla = df_agg.pivot_table(
            index="tipo_administracion",
            columns=col_x,
            values=col_val,
            aggfunc="sum",
            fill_value=0,
            observed=False,
        )
        tabla = tabla.reindex(
            index=[a for a in ORDEN_ADMIN if a in tabla.index],
            columns=orden_columnas,
            fill_value=0,
        )
        pct = tabla.div(tabla.sum(axis=1), axis=0) * 100
        pct.index = [f"{a}<br>n={int(n_por_admin.get(a, 0)):,}" for a in pct.index]

        fig = px.imshow(
            pct,
            text_auto=".1f",
            aspect="auto",
            color_continuous_scale="YlOrRd",
            title=titulo,
            labels={"x": etiqueta_x, "y": "Tipo de administración", "color": "%"},
            template="plotly_dark",
        )
        fig.update_layout(height=320)
        return fig

    if not df_admin_clase.empty:
        n_admin_total = df_admin_clase.groupby("tipo_administracion")["total_incendios"].sum()

        st.plotly_chart(
            heatmap_desde_agregado(
                df_admin_clase,
                "clase",
                "total_incendios",
                ORDEN_CLASES,
                "% de Incendios por Clase y Tipo de Administración",
                "Clase de incendio",
                n_admin_total,
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            heatmap_desde_agregado(
                df_admin_clase,
                "clase",
                "total_acres",
                ORDEN_CLASES,
                "% de Superficie Quemada por Clase y Tipo de Administración",
                "Clase de incendio",
                n_admin_total,
            ),
            use_container_width=True,
        )
        st.caption(
            "Clases por tamaño final: A ≤ 0.25 acres · B 0.26–9.9 · C 10–99.9 · "
            "D 100–299 · E 300–999 · F 1,000–4,999 · G ≥ 5,000. Cada fila suma 100 %."
        )

    df_cont = datos["contencion"]
    if not df_cont.empty:
        n_admin_cont = df_cont.groupby("tipo_administracion")["total"].sum()
        st.plotly_chart(
            heatmap_desde_agregado(
                df_cont,
                "rango",
                "total",
                RANGOS_CONTENCION,
                "% de Incendios por Tiempo de Contención y Tipo de Administración",
                "Tiempo de contención",
                n_admin_cont,
            ),
            use_container_width=True,
        )
        st.caption(
            f"Solo incendios con contención registrada; se excluyeron {datos['n_excluidos']:,} "
            "con más de 365 días (posibles errores de fecha)."
        )
    else:
        st.warning("No hay registros suficientes para mostrar el tiempo de contención con los filtros seleccionados.")

    st.markdown("---")

    # Objetivo 5
    st.header("Dinámica Estacional de la Severidad y Respuesta Operativa")
    st.markdown(
        """Evaluación del comportamiento del tiempo de contención y la superficie afectada
        a lo largo de las estaciones del año por región."""
    )

    col12, col13, col14 = st.columns(3)

    with col12:
        if metricas["mes_max"] is not None:
            mes_max = metricas["mes_max"]["nombre_mes"]
            acres_mes_max = float(metricas["mes_max"]["acres"] or 0)
            val_mes = (
                f"{mes_max}<br><span style='font-size: 16px; font-weight: normal; "
                f"color: #261E1E;'>{acres_mes_max:,.0f} acres</span>"
            )
        else:
            val_mes = "Sin datos"

        tarjeta_metrica(
            titulo="Mes con más superficie quemada",
            valor=val_mes,
            subtitulo="Pico histórico estacional",
        )

    with col13:
        if metricas["estacion_pico"] is not None:
            pico_estacion = metricas["estacion_pico"]["estacion"]
        else:
            pico_estacion = "Sin datos"

        tarjeta_metrica(
            titulo="Pico de temporada alta",
            valor=pico_estacion,
            subtitulo="Estación con mayor incidencia",
        )

    with col14:
        promedio_anual = metricas["promedio_anual"]
        tarjeta_metrica(
            titulo="Promedio de superficie quemada por año",
            valor=f"{promedio_anual:,.2f}",
            subtitulo="acres/año",
        )

    MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    ORDEN_ESTACIONES = ["Primavera", "Verano", "Otoño", "Invierno"]
    COLORES_ESTACION = {
        "Invierno": "#FFF9E6",
        "Primavera": "#FFD966",
        "Verano": "#FF9933",
        "Otoño": "#D94E00",
    }

    por_mes = datos["meses"].copy()
    if not por_mes.empty:
        por_mes["mes_nombre"] = por_mes["mes"].map(lambda m: MESES_ES[int(m) - 1])

        largo_mes = por_mes.melt(
            id_vars=["mes", "mes_nombre", "estacion"],
            value_vars=["incendios", "acres"],
            var_name="metrica",
            value_name="valor",
        )
        largo_mes["metrica"] = largo_mes["metrica"].map(
            {
                "incendios": "Número de incendios",
                "acres": "Superficie quemada (acres)",
            }
        )

        fig_meses = px.bar(
            largo_mes,
            x="mes_nombre",
            y="valor",
            color="estacion",
            facet_row="metrica",
            color_discrete_map=COLORES_ESTACION,
            category_orders={
                "mes_nombre": MESES_ES,
                "estacion": ORDEN_ESTACIONES,
                "metrica": ["Número de incendios", "Superficie quemada (acres)"],
            },
            title="Incendios y Superficie Quemada por Mes",
            labels={"mes_nombre": "Mes", "valor": "", "estacion": "Estación"},
            template="plotly_dark",
        )
        fig_meses.update_yaxes(matches=None, showticklabels=True)
        fig_meses.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_meses.update_layout(height=600)
        st.plotly_chart(fig_meses, use_container_width=True)

        df_reg_mes = datos["region_mes"]
        if not df_reg_mes.empty:
            acres_region_mes = df_reg_mes.pivot_table(
                index="region_nifc",
                columns="mes",
                values="acres",
                aggfunc="sum",
                fill_value=0,
            ).reindex(columns=range(1, 13), fill_value=0)

            acres_region_mes = acres_region_mes.loc[
                acres_region_mes.sum(axis=1).sort_values(ascending=False).index
            ]
            perfil_mensual = acres_region_mes.div(acres_region_mes.sum(axis=1), axis=0) * 100

            fig_calor_mes = px.imshow(
                perfil_mensual,
                x=MESES_ES,
                y=perfil_mensual.index,
                text_auto=".0f",
                aspect="auto",
                color_continuous_scale="YlOrRd",
                title="¿Cuándo se Quema Cada Región? % de su Superficie Anual por Mes",
                labels={"x": "Mes", "y": "Región NIFC", "color": "% anual"},
                template="plotly_dark",
            )
            fig_calor_mes.update_layout(height=max(400, 50 * len(perfil_mensual) + 150))
            st.plotly_chart(fig_calor_mes, use_container_width=True)