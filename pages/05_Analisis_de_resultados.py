"""
Analisis de resultados 

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import os
import duckdb
import pandas as pd
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(
    page_title="Análisis de Resultados",
    page_icon="📊",
    layout="wide",
)

MOTHERDUCK_TOKEN = os.environ.get(
    "MOTHERDUCK_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNhcmxvc2hlcnJlcmFzZWdhcnJhQGdtYWlsLmNvbSIsIm1kUmVnaW9uIjoiYXdzLXVzLWVhc3QtMSIsInNlc3Npb24iOiJjYXJsb3NoZXJyZXJhc2VnYXJyYS5nbWFpbC5jb20iLCJwYXQiOiJCb2h2blVPeGY4TjU5MDY5bVJaSG9Hb0NnR2hTc3ViRXhqMWdhUXlsRjJ3IiwidXNlcklkIjoiZjBmZWZmM2EtYWUzMy00MGExLThmMTUtZDNjNTAzZmM3ODM0IiwiaXNzIjoibWRfcGF0IiwicmVhZE9ubHkiOmZhbHNlLCJ0b2tlblR5cGUiOiJyZWFkX3dyaXRlIiwiaWF0IjoxNzkzMjg1MDA2fQ.ZrcMtxyCK0RiInbm7DEYytfLfqvtwBStPS0LUrmcK3M"
)
os.environ["motherduck_token"] = MOTHERDUCK_TOKEN
pd.set_option("display.max_columns", 50)
print("DuckDB versión:", duckdb.__version__)

@st.cache_data
def cargar_datos():
    print("Conectando a MotherDuck y cargando datos...")
    con = duckdb.connect("md:")
    
    BASE = "incendios_usa"     
    ESQUEMA = "main"    
    TABLA = "vista_general_detallada"       

    REF = f'"{BASE}"."{ESQUEMA}"."{TABLA}"'
    query = f"SELECT * FROM {REF}"
    df = con.sql(query).df()
    
    con.close()
    return df

df = cargar_datos()
print("Datos listos en memoria ✅")

with st.sidebar:
    st.title("Filtro a aplicar")
    st.caption("seleccion de la parte de la investigacion a filtrar")

    select_region = st.multiselect(
        "Seleccione la región de interés",
        df["region_nifc"].unique(),
        default=df["region_nifc"].unique()
    )
    
    select_propietario = st.pills(
        "Seleccione el tipo de propietario",
        df['tipo_administracion'].unique(),
        default=df['tipo_administracion'].unique(),
        selection_mode="multi"
    )
    
    select_causa = st.segmented_control(
        "Seleccione la causa del incendio",
        df['origen_causa'].unique(),
        default=df['origen_causa'].unique(),
        selection_mode="multi"
    )
    anios_disponibles = sorted(df['anio'].dropna().unique())
    select_anio = st.select_slider(
        "Seleccione el rango de años",
        options= anios_disponibles,
        value=(anios_disponibles[0], anios_disponibles[-1])
    )
# el df filtrado para usarlo en la ventana y que si haga efecto los filtros
df_filtered = df[
    df["region_nifc"].isin(select_region) &
    df["tipo_administracion"].isin(select_propietario) &
    df["origen_causa"].isin(select_causa) &
    (df['anio'] >= select_anio[0]) &
    (df['anio'] <= select_anio[1])
]


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
        unsafe_allow_html=True
    )


tab1, tab2, tab3 = st.tabs(["🗺️ Impacto Territorial","📊 Causas y severidad" , "📈 Gestión y estacionalidad"])

#objetivo 1
with tab1:
    st.header("Distribución Regional de Superficie Afectada y Severidad del Fuego")
    st.markdown("""Evaluación comparativa de la magnitud del impacto territorial para la
      identificación de zonas de alta susceptibilidad y destrucción.""")
    col1, col2, col3 = st.columns(3)
    with col1:
        # total de superficie quemada
        total_acres = df_filtered['superficie_acres'].sum() if not df_filtered.empty else 0
        tarjeta_metrica(
        titulo="Total superficie quemada",
        valor=f"{total_acres:,.2f}",
        subtitulo="acres"
        )
    with col2:
        if not df_filtered.empty:
            # Encontramos la región mas afectada
            region_stats = df_filtered.groupby('region_nifc')['superficie_acres'].sum()
            region_max = region_stats.idxmax()
            label_región = f"{region_max}"
            acres_max = region_stats.max()
        else:
            label_región = "Sin datos"

        tarjeta_metrica(
            titulo="Región más afectada",
            valor=region_max,
            subtitulo=f"{acres_max:,.0f} acres"
        )
    with col3:
        #superficie media por incendio
        media_acres = df_filtered['superficie_acres'].mean() if not df_filtered.empty else 0
        tarjeta_metrica(
            titulo="Superficie media por incendio",
            valor=f"{media_acres:,.2f}",
            subtitulo="acres"
        )
        
    #Grafico objetivo 1
    ORDEN_CLASES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    COLORES_CLASE = dict(zip(ORDEN_CLASES, px.colors.sequential.YlOrRd[1:8]))
    COLORES_CLASE['(?)'] = '#333333'

    if not df_filtered.empty:
        resumen = (
            df_filtered.groupby(['region_nifc', 'clase'])['superficie_acres']
            .sum()
            .reset_index(name='acres')
        )
        acres_region = resumen.groupby('region_nifc')['acres'].sum()
        resumen['region_label'] = resumen['region_nifc'].map(
            lambda r: f"{r} ({acres_region[r] / 1e6:.1f}M ac)"
        )

        fig_treemap = px.treemap(
            resumen,
            path=[px.Constant('Total'), 'region_label', 'clase'],
            values='acres',
            color='clase',
            color_discrete_map=COLORES_CLASE,
            title='Superficie Quemada por Región y Clase de Incendio (Acres)',
            template='plotly_dark',
        )
        fig_treemap.update_traces(
            textinfo='label+percent parent',
            hovertemplate='%{label}<br>%{value:,.0f} acres<br>%{percentParent:.1%} de su grupo<extra></extra>',
        )
        fig_treemap.update_layout(
            height=600,
            uniformtext=dict(minsize=10, mode='hide'),
            margin=dict(t=60, l=10, r=10, b=10),
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.caption(
            "Clases por tamaño final: A ≤ 0.25 acres · B 0.26–9.9 · C 10–99.9 · "
            "D 100–299 · E 300–999 · F 1,000–4,999 · G ≥ 5,000."
        )
    else:
        st.warning("No hay registros para mostrar con los filtros seleccionados.")
        
#objetivo 2
with tab2:
    st.header("Patrones de Ignición y Fuentes de Causa por Región")
    st.markdown("""Análisis de la relación entre el origen del fuego (humano vs. natural) y la ubicación
      geográfica para determinar la dinámica de las fuentes de inicio.""")

    col4, col5 = st.columns(2)

    with col4:
         # Estado y region a la que pertenece con mas incendios
            if not df_filtered.empty:
                df_count = df_filtered.groupby(['estado', 'region_nifc'])['objectid'].count().reset_index()
                if not df_count.empty:
                    idx_max_count = df_count['objectid'].idxmax()
                    est_count = df_count.loc[idx_max_count, 'estado']
                    reg_count = df_count.loc[idx_max_count, 'region_nifc']
                    val_count = df_count.loc[idx_max_count, 'objectid']
                    txt_count = f"""{est_count} <span style='font-size: 14px; color: #261E1E;'>({reg_count})</span><br><span 
                    style='font-size: 16px; font-weight: normal; color: #261E1E;'>{val_count:,} incendios</span>"""
                else:
                    txt_count = "Sin datos"
            else:
                txt_count = "Sin datos"
                
            tarjeta_metrica(
                titulo="Mayor frecuencia de incendios",
                valor=txt_count,
                subtitulo="Estado y Región"
            )
    with col5:
        # porcentaje de causa de incendios
            if not df_filtered.empty and 'origen_causa' in df_filtered.columns:
                total_reg = len(df_filtered)
                if total_reg > 0:
                    # Contamos cuántos registros hay de cada valor de forma directa
                    conteo = df_filtered['origen_causa'].value_counts()
                    nat = conteo.get('Natural', 0)
                    hum = conteo.get('Humana', 0)
                    
                    pct_nat = (nat / total_reg) * 100
                    pct_hum = (hum / total_reg) * 100
        
                    val_causas = f"⚡ Natural: {pct_nat:.1f}%<br>👥 Humana: {pct_hum:.1f}%"
                else:
                    val_causas = "Sin datos"
            else:
                val_causas = "Sin datos"
                            
            tarjeta_metrica(
                titulo="Distribución por tipo de causa",
                valor=val_causas,
                subtitulo=f"Sobre {len(df_filtered):,} incendios"
            )

    #Grafico objetivo 2
    st.subheader("Proporción de Fuentes de Ignición por Región NIFC")

    if not df_filtered.empty and 'region_nifc' in df_filtered.columns and 'origen_causa' in df_filtered.columns:
        df_chart = df_filtered.groupby(['region_nifc', 'origen_causa'])['objectid'].count().reset_index()
        
        df_chart.rename(columns={'objectid': 'cantidad'}, inplace=True)
        
        # grafico
        fig = px.bar(
        df_chart,
        x='region_nifc',
        y='cantidad',
        color='origen_causa',
        title="Cantidad total de incendios por Región y su origen",
        labels={'region_nifc': 'Región NIFC', 'cantidad': 'Número de Incendios', 'origen_causa': 'Origen de la Causa'},
        barmode='stack', 
        color_discrete_map={'Humana': "#c7b422", 'Natural': "#d42d1b"}
        )
    
        fig.update_layout(
            xaxis_title="Región",
            yaxis_title="Cantidad de Incendios",
            legend_title="Origen",
            yaxis=dict(tickformat=","), 
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos filtrados para mostrar el gráfico de proporciones de causa.")

    st.markdown("---")
    
    #objetivo 3
    st.header("Concentración Territorial de Incendios de Alta Severidad y Mega-Incendios")
    st.markdown("""Cuantificación de eventos críticos a nivel nacional e identificación de las 
    regiones con mayor vulnerabilidad a eventos de gran magnitud.""")

    col6, col7, col8 = st.columns(3)

    with col6:
        # total de megaincendios (Solo clase G)
        if not df_filtered.empty and 'clase' in df_filtered.columns:
            n_megaincendios = len(df_filtered[df_filtered['clase'] == 'G'])
        else:
            n_megaincendios = 0
            
        tarjeta_metrica(
            titulo="Total de megaincendios",
            valor=f"{n_megaincendios:,}",
            subtitulo="Incendios clase G"
        )

    with col7:
        # 2. maxima extension registrada
        max_acres = df_filtered['superficie_acres'].max() if not df_filtered.empty else 0
        tarjeta_metrica(
            titulo="Máxima extensión registrada",
            valor=f"{max_acres:,.2f}",
            subtitulo="acres en un solo evento"
        )

    with col8:
        # Estado y region a la que pertenece con mas superficie quemada
            if not df_filtered.empty:
                df_sup = df_filtered.groupby(['estado', 'region_nifc'])['superficie_acres'].sum().reset_index()
                if not df_sup.empty:
                    idx_max_sup = df_sup['superficie_acres'].idxmax()
                    est_sup = df_sup.loc[idx_max_sup, 'estado']
                    reg_sup = df_sup.loc[idx_max_sup, 'region_nifc']
                    val_sup = df_sup.loc[idx_max_sup, 'superficie_acres']
                    # Formateamos el texto interno con saltos de línea limpios
                    txt_sup = f"""{est_sup} <span style='font-size: 14px; color: #261E1E;'>({reg_sup})</span><br><span 
                    style='font-size: 16px; font-weight: normal; color: #261E1E;'>{val_sup:,.0f} acres</span>"""
                else:
                    txt_sup = "Sin datos"
            else:
                txt_sup = "Sin datos"
                
            tarjeta_metrica(
                titulo="Mayor superficie quemada",
                valor=txt_sup,
                subtitulo="Estado y Región"
            )             

    #grafico objetivo 3
    st.subheader("Mega-Incendios por Región NIFC")
    st.markdown("Comparación entre el número de eventos y la superficie total quemada en cada región.")

    REGIONES_TODAS = sorted(df['region_nifc'].dropna().unique())

    COLOR_NARANJA = "#FF7F0E"  # También puedes usar "#F97316" o "orange"
    COLORE_REGION = {region: COLOR_NARANJA for region in REGIONES_TODAS}

    df_mega = df_filtered[df_filtered['es_megaincendio'] == 1]

    if not df_mega.empty:
        por_region = (
            df_mega.groupby('region_nifc')
            .agg(
                n_megaincendios=('superficie_acres', 'size'),
                acres_totales=('superficie_acres', 'sum'),
            )
            .reset_index()
            .sort_values('n_megaincendios', ascending=True)
        )
        orden_regiones = por_region['region_nifc'].tolist()

        df_largo = por_region.melt(
            id_vars='region_nifc',
            value_vars=['n_megaincendios', 'acres_totales'],
            var_name='metrica',
            value_name='valor',
        )
        df_largo['metrica'] = df_largo['metrica'].map({
            'n_megaincendios': 'Número de mega-incendios',
            'acres_totales': 'Superficie quemada (acres)',
        })

        fig_regiones = px.bar(
            df_largo,
            x='valor',
            y='region_nifc',
            facet_col='metrica',
            orientation='h',
            text_auto='.3~s',
            category_orders={
                'region_nifc': orden_regiones,
                'metrica': ['Número de mega-incendios', 'Superficie quemada (acres)'],
            },
            title='Mega-Incendios por Región NIFC: Eventos vs. Superficie Quemada',
            labels={'valor': '', 'region_nifc': 'Región NIFC'},
            template='plotly_dark',
        )
        fig_regiones.update_xaxes(matches=None, showticklabels=True)
        fig_regiones.update_xaxes(range=[0, por_region['n_megaincendios'].max() * 1.2], col=1)
        fig_regiones.update_xaxes(range=[0, por_region['acres_totales'].max() * 1.2], col=2)
        fig_regiones.update_traces(
            marker_color='#FF7F0E',
            textposition='outside',
            cliponaxis=False,
            hovertemplate='%{y}<br>%{x:,.0f}<extra></extra>',
        )
        fig_regiones.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_regiones.update_layout(
            showlegend=False,
            height=max(400, 55 * len(por_region) + 150),
        )
        st.plotly_chart(fig_regiones, use_container_width=True)
    else:
        st.warning("No hay mega-incendios para mostrar con los filtros seleccionados.")

with tab3: #objetivo 4
    st.header("Impacto y Tiempo de Contención según el propietario del Suelo")
    st.markdown("""Análisis comparativo de la severidad y respuesta operativa entre 
    terrenos bajo administración federal y tierras estatales o privadas.""")

    col9, col10, col11 = st.columns(3)

    with col9:
        #propietario con mas superficie quemada y mas cantidad de incendios
            if not df_filtered.empty and 'tipo_administracion' in df_filtered.columns:
                df_prop = df_filtered.groupby('tipo_administracion').agg(
                    total_incendios=('objectid', 'count'),
                    total_acres=('superficie_acres', 'sum')
                ).reset_index()
                
                if not df_prop.empty:
                    # Categoría con más incendios dentro de las 3
                    prop_incendios = df_prop.loc[df_prop['total_incendios'].idxmax()]
                    # Categoría con más acres dentro de las 3
                    prop_acres = df_prop.loc[df_prop['total_acres'].idxmax()]
                    
                    val_prop = f"""<b>Más frecuencia:</b> {prop_incendios['tipo_administracion']} 
                    ({prop_incendios['total_incendios']:,})<br> <b>Mayor superficie:</b> {prop_acres['tipo_administracion']} ({prop_acres['total_acres']:,.0f} ac)"""
                else:
                    val_prop = "Sin datos"
            else:
                val_prop = "Sin datos"
                
            tarjeta_metrica(
                titulo="Propietario dominante (3 categorías)",
                valor=val_prop,
                subtitulo="Basado en Federal, Estatal y Privado"
            )

    with col10:
        # Tiempo promedio de incendio (filtrando solo los que tienen contención == 1)
        if not df_filtered.empty and 'dias_contencion' in df_filtered.columns and 'tiene_contencion' in df_filtered.columns:
            # Filtramos solo los que tienen contención (1)
            df_contenidos = df_filtered[df_filtered['tiene_contencion'] == 1]
            prom_dias = df_contenidos['dias_contencion'].mean() if not df_contenidos.empty else 0
        else:
            prom_dias = 0
            
        tarjeta_metrica(
            titulo="Tiempo promedio de contencion",
            valor=f"{prom_dias:.1f} días",
            subtitulo="Duración media por evento"
        )

    with col11:
         # Tiempo máximo de contención registrado
        if not df_filtered.empty and 'dias_contencion' in df_filtered.columns and 'tiene_contencion' in df_filtered.columns:
            max_dias = df_contenidos['dias_contencion'].max() if not df_contenidos.empty else 0
                
            df_limpio = df_contenidos[df_contenidos['dias_contencion'] <= 365]
            
            max_dias = df_limpio['dias_contencion'].max() if not df_limpio.empty else 0  
        else:
            max_dias = 0
            
        tarjeta_metrica(
            titulo="Tiempo máximo de contención",
            valor=f"{max_dias:.0f} días",
            subtitulo="Mayor duración registrada"
        )

    #grafico objetivo 4
    st.subheader("Severidad y Rapidez de Contención por Tipo de Administración")
    ORDEN_ADMIN = ['Federal', 'Estatal/Local', 'Privada']
    ORDEN_CLASES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    RANGOS_CONTENCION = ['Mismo día', '1 día', '2-7 días', '8-30 días', 'Más de 30 días']


    def heatmap_porcentajes(df, columna, orden_columnas, titulo, etiqueta_x, pesos=None):
        if pesos:
            tabla = df.pivot_table(
                index='tipo_administracion', columns=columna,
                values=pesos, aggfunc='sum', fill_value=0, observed=False,
            )
        else:
            tabla = pd.crosstab(df['tipo_administracion'], df[columna])

        tabla = tabla.reindex(
            index=[a for a in ORDEN_ADMIN if a in tabla.index],
            columns=orden_columnas,
            fill_value=0,
        )
        pct = tabla.div(tabla.sum(axis=1), axis=0) * 100

        n_admin = df['tipo_administracion'].value_counts()
        pct.index = [f"{a}<br>n={n_admin.get(a, 0):,}" for a in pct.index]

        fig = px.imshow(
            pct,
            text_auto='.1f',
            aspect='auto',
            color_continuous_scale='YlOrRd',
            title=titulo,
            labels={'x': etiqueta_x, 'y': 'Tipo de administración', 'color': '%'},
            template='plotly_dark',
        )
        fig.update_layout(height=320)
        return fig


    if not df_filtered.empty:
        st.plotly_chart(
            heatmap_porcentajes(
                df_filtered, 'clase', ORDEN_CLASES,
                '% de Incendios por Clase y Tipo de Administración', 'Clase de incendio',
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            heatmap_porcentajes(
                df_filtered, 'clase', ORDEN_CLASES,
                '% de Superficie Quemada por Clase y Tipo de Administración', 'Clase de incendio',
                pesos='superficie_acres',
            ),
            use_container_width=True,
        )
        st.caption(
            "Clases por tamaño final: A ≤ 0.25 acres · B 0.26–9.9 · C 10–99.9 · "
            "D 100–299 · E 300–999 · F 1,000–4,999 · G ≥ 5,000. Cada fila suma 100 %."
        )

    if 'tiene_contencion' in df_filtered.columns:
        df_resp = df_filtered[df_filtered['tiene_contencion'] == 1]
    else:
        df_resp = df_filtered
    n_antes = len(df_resp)
    df_resp = df_resp[df_resp['dias_contencion'] <= 365].copy()

    if not df_resp.empty:
        df_resp['rango'] = pd.cut(
            df_resp['dias_contencion'],
            bins=[-1, 0, 1, 7, 30, 365],
            labels=RANGOS_CONTENCION,
        )
        st.plotly_chart(
            heatmap_porcentajes(
                df_resp, 'rango', RANGOS_CONTENCION,
                '% de Incendios por Tiempo de Contención y Tipo de Administración', 'Tiempo de contención',
            ),
            use_container_width=True,
        )
        st.caption(
            f"Solo incendios con contención registrada; se excluyeron {n_antes - len(df_resp):,} "
            "con más de 365 días (posibles errores de fecha)."
        )
    else:
        st.warning("No hay registros suficientes para mostrar el tiempo de contención con los filtros seleccionados.")


    st.markdown("---")

#objetivo 5   
    st.header("Dinámica Estacional de la Severidad y Respuesta Operativa")
    st.markdown("""Evaluación del comportamiento del tiempo de contención y la superficie afectada
      a lo largo de las estaciones del año por región.""")

    col12, col13, col14 = st.columns(3)

    with col12:
        if not df_filtered.empty and 'nombre_mes' in df_filtered.columns:
            mes_stats = df_filtered.groupby('nombre_mes')['superficie_acres'].sum()
            if not mes_stats.empty:
                mes_max = mes_stats.idxmax()
                acres_mes_max = mes_stats.max()
                val_mes = f"""{mes_max}<br><span style='font-size: 16px; font-weight: normal; 
                color: #261E1E;'>{acres_mes_max:,.0f} acres</span>"""
            else:
                val_mes = "Sin datos"
        else:
            val_mes = "Sin datos"
            
        tarjeta_metrica(
            titulo="Mes con más superficie quemada",
            valor=val_mes,
            subtitulo="Pico histórico estacional"
        )

    with col13: 
        if not df_filtered.empty and 'estacion' in df_filtered.columns:
            if not df_filtered['estacion'].mode().empty:
                pico_estacion = df_filtered['estacion'].mode()[0]
            else:
                pico_estacion = "Sin datos"
        else:
            pico_estacion = "Sin datos"
            
        tarjeta_metrica(
            titulo="Pico de temporada alta",
            valor=pico_estacion,
            subtitulo="Estación con mayor incidencia"
        )

    with col14:
        # promedio de superficie quemada por año
        if not df_filtered.empty:
            promedio_anual = df_filtered.groupby('anio')['superficie_acres'].sum().mean()
        else:
            promedio_anual = 0
            
        tarjeta_metrica(
            titulo="Promedio de superficie quemada por año",
            valor=f"{promedio_anual:,.2f}",
            subtitulo="acres/año"
        )

    MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    ORDEN_ESTACIONES = ['Primavera', 'Verano', 'Otoño', 'Invierno']
    COLORES_ESTACION = {
        'Invierno': '#FFF9E6',  
        'Primavera': '#FFD966',  
        'Verano': '#FF9933',  
        'Otoño': '#D94E00',  
    }

    if not df_filtered.empty:
        por_mes = (
            df_filtered.groupby(['mes', 'estacion'])
            .agg(incendios=('superficie_acres', 'size'),
                acres=('superficie_acres', 'sum'))
            .reset_index()
        )
        por_mes['mes_nombre'] = por_mes['mes'].map(lambda m: MESES_ES[int(m) - 1])

        largo_mes = por_mes.melt(
            id_vars=['mes', 'mes_nombre', 'estacion'],
            value_vars=['incendios', 'acres'],
            var_name='metrica',
            value_name='valor',
        )
        largo_mes['metrica'] = largo_mes['metrica'].map({
            'incendios': 'Número de incendios',
            'acres': 'Superficie quemada (acres)',
        })

        fig_meses = px.bar(
            largo_mes,
            x='mes_nombre',
            y='valor',
            color='estacion',
            facet_row='metrica',
            color_discrete_map=COLORES_ESTACION,
            category_orders={
                'mes_nombre': MESES_ES,
                'estacion': ORDEN_ESTACIONES,
                'metrica': ['Número de incendios', 'Superficie quemada (acres)'],
            },
            title='Incendios y Superficie Quemada por Mes',
            labels={'mes_nombre': 'Mes', 'valor': '', 'estacion': 'Estación'},
            template='plotly_dark',
        )
        fig_meses.update_yaxes(matches=None, showticklabels=True)
        fig_meses.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_meses.update_layout(height=600)
        st.plotly_chart(fig_meses, use_container_width=True)

        acres_region_mes = (
            df_filtered.pivot_table(
                index='region_nifc', columns='mes',
                values='superficie_acres', aggfunc='sum', fill_value=0,
            )
            .reindex(columns=range(1, 13), fill_value=0)
        )
        acres_region_mes = acres_region_mes.loc[
            acres_region_mes.sum(axis=1).sort_values(ascending=False).index
        ]
        perfil_mensual = acres_region_mes.div(acres_region_mes.sum(axis=1), axis=0) * 100

        fig_calor_mes = px.imshow(
            perfil_mensual,
            x=MESES_ES,
            y=perfil_mensual.index,
            text_auto='.0f',
            aspect='auto',
            color_continuous_scale='YlOrRd',
            title='¿Cuándo se Quema Cada Región? % de su Superficie Anual por Mes',
            labels={'x': 'Mes', 'y': 'Región NIFC', 'color': '% anual'},
            template='plotly_dark',
        )
        fig_calor_mes.update_layout(height=max(400, 50 * len(perfil_mensual) + 150))
        st.plotly_chart(fig_calor_mes, use_container_width=True)