import duckdb
from pathlib import Path

# Rutas de archivos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_ROOT / "Data" / "Incendios_TFCompu.duckdb"

# conectar con duckdb
conn = duckdb.connect(str(DB_PATH))

# Agregar columnas temporales de tipo DATE
conn.execute("ALTER TABLE fires ADD COLUMN discovery_date_temp DATE;")
conn.execute("ALTER TABLE fires ADD COLUMN cont_date_temp DATE;")

# Convertir los días Julianos (DOUBLE) a DATE
conn.execute("""
    UPDATE fires 
    SET discovery_date_temp = CAST(to_timestamp((DISCOVERY_DATE - 2440587.5) * 86400) AS DATE),
        cont_date_temp = CASE 
                            WHEN CONT_DATE IS NOT NULL THEN CAST(to_timestamp((CONT_DATE - 2440587.5) * 86400) AS DATE)
                            ELSE NULL 
                         END;
""")

# Eliminar las columnas originales en formato DOUBLE
conn.execute("ALTER TABLE fires DROP COLUMN DISCOVERY_DATE;")
conn.execute("ALTER TABLE fires DROP COLUMN CONT_DATE;")

# Renombrar las columnas temporales a los nombres definitivos
conn.execute("ALTER TABLE fires RENAME COLUMN discovery_date_temp TO DISCOVERY_DATE;")
conn.execute("ALTER TABLE fires RENAME COLUMN cont_date_temp TO CONT_DATE;")

# Verificar esquema actualizado
df_schema = conn.execute("DESCRIBE fires").df()
print("\nEstructura actualizada de las columnas de fecha:")
print(df_schema[df_schema['column_name'].isin(['DISCOVERY_DATE', 'CONT_DATE'])][['column_name', 'column_type']])

conn.close()