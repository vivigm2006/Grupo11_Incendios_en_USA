import os
from pathlib import Path
import duckdb

# Configuración de rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
TABLE_NAME = "fires"


def estandarizar_fips_code_3_digitos():
    con = duckdb.connect(str(DB_PATH))

    try:
        # Forzar la conversión de FIPS_CODE a VARCHAR para evitar problemas de tipo
        con.execute(f"ALTER TABLE {TABLE_NAME} ALTER FIPS_CODE TYPE VARCHAR;")

        query_update = f"""
            UPDATE {TABLE_NAME}
            SET FIPS_CODE = LPAD(CAST(FIPS_CODE AS VARCHAR), 3, '0')
            WHERE FIPS_CODE IS NOT NULL;
        """
        con.execute(query_update)
        print("Estandarización completada exitosamente")

    finally:
        con.close()


if __name__ == "__main__":
    estandarizar_fips_code_3_digitos()