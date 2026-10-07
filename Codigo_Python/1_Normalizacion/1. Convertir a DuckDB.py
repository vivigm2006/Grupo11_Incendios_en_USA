from pathlib import Path
import duckdb

# Definir la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Rutas de los archivos SQLite y DuckDB
RUTA_SQLITE = BASE_DIR / "Data" / "FPA_FOD_20170508.sqlite"
RUTA_DUCKDB = BASE_DIR / "Data" / "Incendios_TFCompu.duckdb"

# Asegurar que la carpeta de destino exista antes de conectar
RUTA_DUCKDB.parent.mkdir(parents=True, exist_ok=True)


def ejecutar_etl():
    if not RUTA_SQLITE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo SQLite original en: {RUTA_SQLITE}\n"
            "Por favor, descarga el dataset y colócalo en la carpeta 'data/'."
        )

    # Conectar duckdb usando la ruta dinámica
    con = duckdb.connect(str(RUTA_DUCKDB))

    try:
        # Cargar extensión SQLite
        con.execute("INSTALL sqlite;")
        con.execute("LOAD sqlite;")

        # Adjuntar base de datos usando la ruta dinámica
        con.execute(f"ATTACH '{RUTA_SQLITE}' AS sqlite_db (TYPE SQLITE);")

        # Crear la tabla nueva tabla omitiendo la geometría pesada y agregando el área geográfica
        query = """
        CREATE OR REPLACE TABLE Fires AS 
        SELECT 
            f.* EXCLUDE (Shape),
            u.GeographicArea
        FROM sqlite_db.Fires f
        LEFT JOIN sqlite_db.NWCG_UnitIDActive_20170109 u
            ON f.NWCG_REPORTING_UNIT_ID = u.UnitId;
        """
        
        con.execute(query)

        print(
            f"Conversión completada exitosamente.\nBase de datos guardada en: {RUTA_DUCKDB}"
        )

    finally:
        con.close()


if __name__ == "__main__":
    ejecutar_etl()