from pathlib import Path
import duckdb


# Ruta del proyecto
ROOT_DIR = Path(__file__).resolve().parents[2]

# Base de datos
DB_PATH = ROOT_DIR / "Data" / "Incendios_TFCompu.duckdb"


# Codigo FIPS de cada estado
state_codes = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "DC": "11",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
    "PR": "72"
}


# Conectar con la base de datos
con = duckdb.connect(str(DB_PATH))

# Nombre de la tabla
tabla = "Fires"


# Crear la columna si todavía no existe
columnas = con.execute(f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = '{tabla}'
""").fetchall()

columnas = [col[0].upper() for col in columnas]

if "STATE_CODE" not in columnas:
    con.execute(f"""
        ALTER TABLE {tabla}
        ADD COLUMN STATE_CODE VARCHAR
    """)


# Crear el CASE para asignar los códigos
case_statement = " ".join(
    f"WHEN '{estado}' THEN '{codigo}'"
    for estado, codigo in state_codes.items()
)


# Actualizar STATE_CODE
con.execute(f"""
    UPDATE {tabla}
    SET STATE_CODE = CASE UPPER(TRIM(STATE))
        {case_statement}
        ELSE NULL
    END
""")

con.close()

print("\nProceso terminado.")