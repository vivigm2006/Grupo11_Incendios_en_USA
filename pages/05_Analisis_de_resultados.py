"""
Analisis de resultados 

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import os
import duckdb
import pandas as pd
import streamlit as st

MOTHERDUCK_TOKEN = os.environ.get(
    "MOTHERDUCK_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNhcmxvc2hlcnJlcmFzZWdhcnJhQGdtYWlsLmNvbSIsIm1kUmVnaW9uIjoiYXdzLXVzLWVhc3QtMSIsInNlc3Npb24iOiJjYXJsb3NoZXJyZXJhc2VnYXJyYS5nbWFpbC5jb20iLCJwYXQiOiJCb2h2blVPeGY4TjU5MDY5bVJaSG9Hb0NnR2hTc3ViRXhqMWdhUXlsRjJ3IiwidXNlcklkIjoiZjBmZWZmM2EtYWUzMy00MGExLThmMTUtZDNjNTAzZmM3ODM0IiwiaXNzIjoibWRfcGF0IiwicmVhZE9ubHkiOmZhbHNlLCJ0b2tlblR5cGUiOiJyZWFkX3dyaXRlIiwiaWF0IjoxNzkzMjg1MDA2fQ.ZrcMtxyCK0RiInbm7DEYytfLfqvtwBStPS0LUrmcK3M"
)


os.environ["motherduck_token"] = MOTHERDUCK_TOKEN

pd.set_option("display.max_columns", 50)
print("DuckDB versión:", duckdb.__version__)

# Verificación: MotherDuck solo funciona con DuckDB 1.x por ahora
if not duckdb.__version__.startswith("1."):
    raise RuntimeError(
        )
con = duckdb.connect("md:")
print("Conectado ✅")

bases = con.sql("SHOW DATABASES").df()
tablas = con.sql("""
    SELECT database_name, schema_name, table_name, estimated_size AS filas_estimadas, column_count
    FROM duckdb_tables()
    WHERE database_name NOT IN ('system', 'temp')
    ORDER BY database_name, schema_name, table_name
""").df()
if tablas.empty:
    raise ValueError("No se encontraron tablas en tu cuenta de MotherDuck.")

BASE = "incendios_usa"     
ESQUEMA = "main"    
TABLA = "vista_general_detallada"       

REF = f'"{BASE}"."{ESQUEMA}"."{TABLA}"'
print("Tabla seleccionada:", REF)


query = f"SELECT * FROM {REF}"
df = con.sql(query).df()

st.set_page_config(
    page_title="Análisis de Resultados",
    page_icon="📊",
    layout="wide",
)

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
