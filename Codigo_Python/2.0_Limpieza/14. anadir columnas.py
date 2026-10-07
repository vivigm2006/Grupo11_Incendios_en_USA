import os
from pathlib import Path
import duckdb

# Rutas de archivos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
CSV_PATH = DATA_DIR / "datos_areas_geografica_condados" / "area_geografica_segun_condados.csv"

TABLE_NAME = "fires"

def agregar_nombres_estado_y_zona():
    con = duckdb.connect(str(DB_PATH))

    try:
        csv_path_str = str(CSV_PATH).replace("\\", "/")
        
        # Vista temporal para los datos del CSV
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW csv_nombres AS 
            SELECT DISTINCT
                LPAD(CAST("State Code" AS VARCHAR), 2, '0') AS STATE_CODE_PADDED,
                LPAD(CAST(FIPS_CODE AS VARCHAR), 3, '0') AS FIPS_CODE_PADDED,
                CAST(State AS VARCHAR) AS STATE_NAME,
                CAST("Nombre Zona" AS VARCHAR) AS GEO_AREA_NAME
            FROM read_csv_auto('{csv_path_str}', header=True);
        """)

        # Agregar columnas si no existen
        con.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS STATE_NAME VARCHAR;")
        con.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS GEO_AREA_NAME VARCHAR;")

        # Actualizar las columnas STATE_NAME y GEO_AREA_NAME en la tabla principal usando los datos del CSV
        query_update = f"""
        UPDATE {TABLE_NAME} AS db
            SET 
                STATE_NAME = COALESCE(csv.STATE_NAME, db.STATE),
                GEO_AREA_NAME = COALESCE(csv.GEO_AREA_NAME, db.GeographicArea)
            FROM csv_nombres AS csv
            WHERE LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = csv.STATE_CODE_PADDED
                AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = csv.FIPS_CODE_PADDED;;
        """
        con.execute(query_update)
        print("Columnas agregadas")
   
    finally:
        con.close()


if __name__ == "__main__":
    agregar_nombres_estado_y_zona()