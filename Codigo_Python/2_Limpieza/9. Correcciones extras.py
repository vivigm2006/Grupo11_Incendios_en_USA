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


def corregir_inconsistencias_db():

    con = duckdb.connect(str(DB_PATH))

    try:
        csv_path_str = str(CSV_PATH).replace("\\", "/")
        
        # 2. CARGAR VISTA TEMPORAL DEL CSV CON CODIGOS NORMALIZADOS
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW csv_oficial AS 
            SELECT 
                CAST(CODIGO_ZONA AS VARCHAR) AS CODIGO_ZONA,
                CAST(County AS VARCHAR) AS County_Oficial,
                LPAD(CAST("State Code" AS VARCHAR), 2, '0') AS STATE_CODE_PADDED,
                LPAD(CAST(FIPS_CODE AS VARCHAR), 3, '0') AS FIPS_CODE_PADDED
            FROM read_csv_auto('{csv_path_str}', header=True);
        """)

        # 3. VERIFICAR REGISTROS A AFECTAR
        count_check = f"""
            SELECT COUNT(*) 
            FROM {TABLE_NAME} AS db
            JOIN csv_oficial AS csv
              ON LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = csv.STATE_CODE_PADDED
             AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = csv.FIPS_CODE_PADDED;
        """
        coincidencias = con.execute(count_check).fetchone()[0]
        print(f"🔍 Total de registros coincidentes para actualizar: {coincidencias:,}")

        # 4. ACTUALIZACIÓN MASIVA EN LA BASE DE DATOS
        # Actualiza GeographicArea, FIPS_NAME y estandariza la columna FIPS_CODE a 3 dígitos en texto.
        update_query = f"""
            UPDATE {TABLE_NAME} AS db
            SET 
                GeographicArea = csv.CODIGO_ZONA,
                FIPS_NAME = csv.County_Oficial,
                FIPS_CODE = LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0')
            FROM csv_oficial AS csv
            WHERE LPAD(CAST(db.STATE_CODE AS VARCHAR), 2, '0') = csv.STATE_CODE_PADDED
              AND LPAD(CAST(db.FIPS_CODE AS VARCHAR), 3, '0') = csv.FIPS_CODE_PADDED;
        """

        print("Ejecutando actualización y corrección de inconsistencias...")
        con.execute(update_query)
        print("Actualización de GeographicArea, FIPS_NAME y formateo de FIPS_CODE completada exitosamente!")

        # 5. VERIFICACIÓN POSTERIOR DE VALORES ANÓMALOS DE GEOGRAPHIC AREA
        check_anomalias = f"""
            SELECT GeographicArea, COUNT(*) as cantidad
            FROM {TABLE_NAME}
            WHERE GeographicArea IN ('AK', 'CA')
            GROUP BY GeographicArea;
        """
        anomalias = con.execute(check_anomalias).fetchall()
        if anomalias:
            print(f"Atención: Aún quedan registros con GeographicArea anómala (AK/CA no estándar): {anomalias}")
        else:
            print("Confirmación: No quedan registros con GeographicArea anómala en la base de datos.")

    finally:
        con.close()


if __name__ == "__main__":
    corregir_inconsistencias_db()