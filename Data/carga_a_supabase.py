import os
import sqlite3
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

#cargar desde el archivo .env
load_dotenv()

#la conexión a supabase desde .env
SUPABASE_URL = os.getenv("DATABASE_URL")

if not SUPABASE_URL:
  raise ValueError(
      "Falta DATABASE_URL. Configúrala en tu archivo .env antes de ejecutar el"
      " script."
  )

engine = create_engine(SUPABASE_URL)

print("Conectando con Supabase...")

#conexion al archivo sqlite local 
sqlite_path = "Data/FPA_FOD_20170508.sqlite"
conn = sqlite3.connect(sqlite_path)

print(
    "Leyendo la tabla de incendios desde el archivo SQLite local (esto puede tardar unos segundos)..."
)

df_incendios = pd.read_sql("SELECT * FROM Fires", conn)

conn.close()
print(f"Datos leídos con éxito. Total de filas: {len(df_incendios)}")

print("Subiendo la data a Supabase (esto subirá la tabla a la nube)...")
#se sube la data a una tabla en supabase
df_incendios.to_sql("fact_incendio", engine, if_exists="replace", index=False)

print(
    "¡Éxito total! La data ya está en Supabase"
)