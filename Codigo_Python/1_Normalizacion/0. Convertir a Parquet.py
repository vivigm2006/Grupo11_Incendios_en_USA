import os
from pathlib import Path
import duckdb

# Definir la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas de los archivos SQLite y DuckDB
RUTA_DUCKDB = BASE_DIR / "Data" / "Incendios_TFCompu.duckdb"
RUTA_PARQUET = BASE_DIR / "Data" / "Originales Parquet"

RUTA_PARQUET.parent.mkdir(parents=True, exist_ok=True)

db = con = duckdb.connect(str(RUTA_DUCKDB))

#Extraer nombres de tablas
tablas = db.execute(
    "SELECT table_name FROM duckdb_tables() WHERE schema_name = 'main'"
).fetchall()

# Copiar tablas a formato Parquet
for t in tablas:
    nombre_tabla = t[0]
    ruta_salida = RUTA_PARQUET / (nombre_tabla + ".parquet")

    sql = f"COPY {nombre_tabla} TO '{ruta_salida}' (FORMAT PARQUET)"
    db.execute(sql)
    print("tabla guardada:", nombre_tabla)

db.close()
print("listo")