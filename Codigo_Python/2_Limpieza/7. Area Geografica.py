import os
from pathlib import Path
import duckdb

#Configuración de rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]  # Apunta a Grupo11_Incendios_en_USA
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
CSV_PATH = DATA_DIR / "datos_areas_geografica_condados" / "area_geografica_segun_condados.csv"
TABLE_NAME = "Fires"


def actualizar_area_geografica():
    print(f"Leyendo CSV: {CSV_PATH}")


    con = duckdb.connect(str(DB_PATH))

    try:
        csv_path_str = str(CSV_PATH).replace("\\", "/")
        
        # Registrar el CSV como vista temporal
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW csv_zonas AS 
            SELECT * FROM read_csv_auto('{csv_path_str}', header=True);
        """)

        query_update = f"""
            UPDATE {TABLE_NAME} AS db
            SET GeographicArea = csv.CODIGO_ZONA
            FROM csv_zonas AS csv
            WHERE LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = LPAD(CAST(csv."State Code" AS VARCHAR), 2, '0')
              AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = LPAD(CAST(csv.FIPS_CODE AS VARCHAR), 3, '0');
        """

        print("actualizando GeographicArea...")
        con.execute(query_update)
        
        print("Exito")

    finally:
        con.close()


if __name__ == "__main__":
    actualizar_area_geografica()