import os
from pathlib import Path
import duckdb

# Configuración de rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
TABLE_NAME = "Fires"


def corregir_zonas_alaska():
    con = duckdb.connect(str(DB_PATH))

    try:
        # Actualización de registros para corregir la zona geográfica
        query_update = f"""
            UPDATE {TABLE_NAME}
            SET GeographicArea = 'AC'
            WHERE (STATE = 'AK' OR CAST(STATE_CODE AS INT) = 2)
              AND GeographicArea = 'AK';
        """
        con.execute(query_update)
        print("Listo")
    finally:
        con.close()


if __name__ == "__main__":
    corregir_zonas_alaska()