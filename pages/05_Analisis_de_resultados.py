"""
Analisis de resultados 

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import os
import duckdb
import pandas as pd

MOTHERDUCK_TOKEN = os.environ.get(
    "MOTHERDUCK_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImNhcmxvc2hlcnJlcmFzZWdhcnJhQGdtYWlsLmNvbSIsIm1kUmVnaW9uIjoiYXdzLXVzLWVhc3QtMSIsInNlc3Npb24iOiJjYXJsb3NoZXJyZXJhc2VnYXJyYS5nbWFpbC5jb20iLCJwYXQiOiJCb2h2blVPeGY4TjU5MDY5bVJaSG9Hb0NnR2hTc3ViRXhqMWdhUXlsRjJ3IiwidXNlcklkIjoiZjBmZWZmM2EtYWUzMy00MGExLThmMTUtZDNjNTAzZmM3ODM0IiwiaXNzIjoibWRfcGF0IiwicmVhZE9ubHkiOmZhbHNlLCJ0b2tlblR5cGUiOiJyZWFkX3dyaXRlIiwiaWF0IjoxNzkzMjg1MDA2fQ.ZrcMtxyCK0RiInbm7DEYytfLfqvtwBStPS0LUrmcK3M"
)


os.environ["motherduck_token"] = MOTHERDUCK_TOKEN

pd.set_option("display.max_columns", 50)
print("DuckDB versión:", duckdb.__version__)

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
TABLA = "tabla_incendios"       

REF = f'"{BASE}"."{ESQUEMA}"."{TABLA}"'
print("Tabla seleccionada:", REF)

def consultar(sql: str) -> pd.DataFrame:
    """Ejecuta una consulta en MotherDuck y devuelve un DataFrame."""
    return con.sql(sql).df()