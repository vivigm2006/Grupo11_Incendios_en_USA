import duckdb
from pathlib import Path

# Definir rutas dinámicas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
TABLE_NAME = "fires"


def corregir_tres_casos_especificos():
    con = duckdb.connect(str(DB_PATH))

    try:
        # Caso 1: Carson City está en Nevada (NV - STATE_CODE 32), no en California (CA - STATE_CODE 6)
        query_1 = f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'NV',
                STATE_CODE = '32',
                GeographicArea = 'GB',
                FIPS_NAME = 'Carson'
            WHERE (CAST(STATE_CODE AS INT) = 6 OR STATE = 'CA')
              AND CAST(FIPS_CODE AS INT) = 510;
        """
        con.execute(query_1)

        # Caso 2: Modoc County está en California (CA - STATE_CODE 6, FIPS 049), no en Nevada (NV - STATE_CODE 32)
        query_2 = f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'CA',
                STATE_CODE = '06',
                GeographicArea = 'ON',
                FIPS_NAME = 'Modoc'
            WHERE (CAST(STATE_CODE AS INT) = 32 OR STATE = 'NV')
              AND CAST(FIPS_CODE AS INT) = 49
              AND FIPS_NAME LIKE '%Modoc%';
        """
        con.execute(query_2)

        # Caso 3: Siskiyou County está en California (CA - STATE_CODE 6, FIPS 093), no en Oregon (OR - STATE_CODE 41)
        query_3 = f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'CA',
                STATE_CODE = '06',
                GeographicArea = 'ON',
                FIPS_NAME = 'Siskiyou'
            WHERE (CAST(STATE_CODE AS INT) = 41 OR STATE = 'OR')
              AND CAST(FIPS_CODE AS INT) = 93
              AND FIPS_NAME LIKE '%Siskiyou%';
        """
        con.execute(query_3)

        print("Listo")
    finally:
        con.close()


if __name__ == "__main__":
    corregir_tres_casos_especificos()