from pathlib import Path
import duckdb

# Rutas de archivos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_DIR = PROJECT_ROOT / "Data"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"
TABLE_NAME = "fires"


def corregir_inconsistencias_fuerza_bruta():
    con = duckdb.connect(str(DB_PATH))

    try:
        print("Iniciando reasignación forzada de Causa 1, Causa 2 y Causa 3...")

        # 1. PASO PREVIO: ASEGURAR ESTRUCTURA DE COLUMNAS
        con.execute(
            f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS STATE_NAME VARCHAR;"
        )
        con.execute(
            f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS GEO_AREA_NAME VARCHAR;"
        )

        # CAUSA 2: CORRECCIONES DE FORMATO Y FIPS OFICIALES

        # Connecticut (CT): Mapeo directo a FIPS oficiales de 3 dígitos (001, 003, ..., 015)
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE_NAME = 'Connecticut',
                GEO_AREA_NAME = 'Eastern Area',
                FIPS_CODE = LPAD(CAST(FIPS_CODE AS VARCHAR), 3, '0')
            WHERE STATE = 'CT';
        """)

        # Florida (FL): Dade -> Miami-Dade (FIPS 086)
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'FL', STATE_CODE = '12', FIPS_CODE = '086',
                FIPS_NAME = 'Miami-Dade', STATE_NAME = 'Florida', GEO_AREA_NAME = 'Southern Area'
            WHERE STATE = 'FL' AND CAST(FIPS_CODE AS INT) = 25;
        """)

        # Georgia (GA): Bryan South -> Bryan County (FIPS 029)
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'GA', STATE_CODE = '13', FIPS_CODE = '029',
                FIPS_NAME = 'Bryan', STATE_NAME = 'Georgia', GEO_AREA_NAME = 'Southern Area'
            WHERE STATE = 'GA' AND CAST(FIPS_CODE AS INT) = 30;
        """)

        # Oklahoma (OK): Ellis County (FIPS 045)
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'OK', STATE_CODE = '40', FIPS_CODE = '045',
                FIPS_NAME = 'Ellis', STATE_NAME = 'Oklahoma', GEO_AREA_NAME = 'Southern Area'
            WHERE STATE = 'OK' AND CAST(FIPS_CODE AS INT) = 40;
        """)

        # CAUSA 1: CRUCES DE ESTADOS LIMÍTROFES (FUERZA BRUTA)
        mapeos_limitrofes = [
            # Arizona (AZ) -> Condados reales
            ("AZ", 31, "NM", "35", "031", "McKinley", "New Mexico", "Southwest Area"),
            ("AZ", 37, "NM", "35", "045", "San Juan", "New Mexico", "Southwest Area"),
            ("AZ", 45, "NM", "35", "045", "San Juan", "New Mexico", "Southwest Area"),
            ("AZ", 65, "CA", "06", "065", "Riverside", "California", "Southwest Area"),
            ("AZ", 71, "CA", "06", "071", "San Bernardino", "California", "Southwest Area"),
            ("AZ", 83, "CO", "08", "083", "Montezuma", "Colorado", "Rocky Mountain Area"),
           
            # California (CA)
            ("CA", 12, "AZ", "04", "012", "La Paz", "Arizona", "Southwest Area"),
           
            # Delaware (DE)
            ("DE", 45, "MD", "24", "045", "Wicomico", "Maryland", "Eastern Area"),
           
            # Indiana (IN)
            ("IN", 223, "KY", "21", "223", "Trimble", "Kentucky", "Eastern Area"),
           
            # Louisiana (LA)
            ("LA", 139, "AR", "05", "139", "Union", "Arkansas", "Southern Area"),
            ("LA", 149, "MS", "28", "149", "Warren", "Mississippi", "Southern Area"),
            
            # Nebraska (NE)
            ("NE", 102, "SD", "46", "102", "Oglala Lakota", "South Dakota", "Rocky Mountain Area"),
            ("NE", 193, "IA", "19", "193", "Woodbury", "Iowa", "Rocky Mountain Area"),

            # Nevada (NV)
            ("NV", 35, "CA", "06", "035", "Lassen", "California", "Great Basin Area"),
            ("NV", 45, "UT", "49", "045", "Tooele", "Utah", "Great Basin Area"),
            ("NV", 51, "CA", "06", "051", "Mono", "California", "Great Basin Area"),
            ("NV", 53, "UT", "49", "053", "Washington", "Utah", "Great Basin Area"),
            ("NV", 73, "ID", "16", "073", "Owyhee", "Idaho", "Great Basin Area"),
            ("NV", 91, "CA", "06", "091", "Sierra", "California", "Great Basin Area"),

            # New Jersey (NJ)
            ("NJ", 89, "PA", "42", "089", "Monroe", "Pennsylvania", "Eastern Area"),
            
            # New Mexico (NM)
            ("NM", 67, "CO", "08", "067", "La Plata", "Colorado", "Rocky Mountain Area"),
            ("NM", 83, "CO", "08", "083", "Montezuma", "Colorado", "Southwest Area"),
            ("NM", 109, "TX", "48", "109", "Culberson", "Texas", "Southwest Area"),
            ("NM", 229, "TX", "48", "229", "Hudspeth", "Texas", "Southwest Area"),
            ("NC", 241, "GA", "13", "241", "Rabun", "Georgia", "Southern Area"),
            
            # Oklahoma (OK)
            ("OK", 191, "KS", "20", "191", "Sumner", "Kansas", "Southern Area"),
            ("OK",295,"TX","48","295","Lipscomb","Texas","Southern Area"),
            ("OK", 485, "TX", "48", "485", "Wichita", "Texas", "Southern Area"),

            # South Dakota (SD)
            ("SD", 1, "ND", "38", "001", "Adams", "North Dakota", "Rocky Mountain Area"),
            ("SD", 149, "IA", "19", "149", "Plymouth", "Iowa", "Rocky Mountain Area"),
            ("SD", 161, "NE", "31", "161", "Sheridan", "Nebraska", "Rocky Mountain Area"),
           
            # Tennessee (TN)
            ("TN", 295, "GA", "13", "295", "Walker", "Georgia", "Southern Area"),
            
            # Utah (UT)
            ("UT", 77, "CO", "08", "077", "Mesa", "Colorado", "Great Basin Area"),
            ("UT", 81, "CO", "08", "081", "Moffat", "Colorado", "Great Basin Area"),
            ("UT",85,"CO","08","085","Montrose", "Colorado", "Great Basin Area"),
            ("UT", 113, "CO", "08", "113", "San Miguel", "Colorado", "Great Basin Area"),
            
            # Washington (WA)
            ("WA", 89, "MT", "30", "089", "Sanders", "Montana", "Northern Rockies"),

            # Wyoming (WY)
            ("WY", 67, "MT", "30", "067", "Park", "Montana", "Northern Rockies"),
            ("WY", 81, "ID", "16", "081", "Teton", "Idaho", "Great Basin Area"),
        ]

        for (
            st_orig,
            fips_orig,
            st_dest,
            st_code_dest,
            fips_dest,
            fips_name_dest,
            st_name_dest,
            geo_name_dest,
        ) in mapeos_limitrofes:
            con.execute(f"""
                UPDATE {TABLE_NAME}
                SET 
                    STATE = '{st_dest}',
                    STATE_CODE = '{st_code_dest}',
                    FIPS_CODE = '{fips_dest}',
                    FIPS_NAME = '{fips_name_dest}',
                    STATE_NAME = '{st_name_dest}',
                    GEO_AREA_NAME = '{geo_name_dest}'
                WHERE STATE = '{st_orig}' AND CAST(FIPS_CODE AS INT) = {fips_orig};
            """)

        # Caso especial Wyoming (WY) FIPS 81 Moffat County -> Colorado
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET 
                STATE = 'CO', STATE_CODE = '08', FIPS_CODE = '081',
                FIPS_NAME = 'Moffat', STATE_NAME = 'Colorado', GEO_AREA_NAME = 'Rocky Mountain Area'
            WHERE STATE = 'WY' AND CAST(FIPS_CODE AS INT) = 81 AND FIPS_NAME LIKE '%Moffat%';
        """)

        # CAUSA 3: ALASKA (AK) - ENTIDADES HISTÓRICAS
        con.execute(f"""
            UPDATE {TABLE_NAME}
            SET STATE_NAME = 'Alaska', GEO_AREA_NAME = 'Alaska Area'
            WHERE STATE = 'AK' AND STATE_NAME IS NULL;
        """)

        print("Correcciones forzadas aplicadas a la base de datos.")

    finally:
        con.close()


if __name__ == "__main__":
    corregir_inconsistencias_fuerza_bruta()