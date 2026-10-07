import os
from pathlib import Path
import duckdb

# Configuración de rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
CSV_PATH = DATA_DIR / "datos_areas_geografica_condados" / "area_geografica_segun_condados.csv"
TABLE_NAME = "Fires"


def actualizar_fips_name():

    con = duckdb.connect(str(DB_PATH))

    try:
        # Normalizar la ruta del CSV para DuckDB (usar / en lugar de \)
        csv_path_str = str(CSV_PATH).replace("\\", "/")
        
        # Registramos el CSV como una vista temporal
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW csv_zonas AS 
            SELECT * FROM read_csv_auto('{csv_path_str}', header=True);
        """)

        # Contar registros que coinciden antes de ejecutar el UPDATE
        count_query = f"""
            SELECT COUNT(*) 
            FROM {TABLE_NAME} AS db
            JOIN csv_zonas AS csv
              ON LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = LPAD(CAST(csv."State Code" AS VARCHAR), 2, '0')
             AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = LPAD(CAST(csv.FIPS_CODE AS VARCHAR), 3, '0');
        """
        coincidencias = con.execute(count_query).fetchone()[0]
        print(f"Registros coincidentes a actualizar: {coincidencias:,}")
        
        # actualizar FIPS_NAME en la tabla Fires usando los datos del CSV
        query_update = f"""
            UPDATE {TABLE_NAME} AS db
            SET FIPS_NAME = csv.County
            FROM csv_zonas AS csv
            WHERE LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = LPAD(CAST(csv."State Code" AS VARCHAR), 2, '0')
              AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = LPAD(CAST(csv.FIPS_CODE AS VARCHAR), 3, '0');
        """

        print("actualizando FIPS_NAME...")
        con.execute(query_update)
        print("Listo")

    finally:
        con.close()


if __name__ == "__main__":
    actualizar_fips_name()