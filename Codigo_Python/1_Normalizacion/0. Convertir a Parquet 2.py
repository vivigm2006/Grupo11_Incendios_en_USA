from pathlib import Path
import duckdb

# 1. Rutas predeterminadas relativas a la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DUCKDB = BASE_DIR / "Data" / "Incendios_TFCompu.duckdb"
DEFAULT_PARQUET_DIR = BASE_DIR / "Data" / "Originales Parquet"


def exportar_tablas_a_parquet(
    ruta_duckdb: Path = DEFAULT_DUCKDB,
    dir_salida_parquet: Path = DEFAULT_PARQUET_DIR,
    compresion: str = "SNAPPY",
) -> None:
    """Extrae todas las tablas de un archivo DuckDB y las exporta individualmente

    a archivos comprimidos en formato Parquet.
    """
    # Convertir a objetos Path por seguridad
    ruta_duckdb = Path(ruta_duckdb)
    dir_salida_parquet = Path(dir_salida_parquet)

    # Validar existencia de la base de datos origen
    if not ruta_duckdb.exists():
        raise FileNotFoundError(
            f"❌ No se encontró la base de datos DuckDB en: {ruta_duckdb.resolve()}"
        )

    # Crear la carpeta de salida específica para los archivos Parquet
    dir_salida_parquet.mkdir(parents=True, exist_ok=True)

    # Abrir la conexión y asegurar su cierre con 'with'
    with duckdb.connect(str(ruta_duckdb)) as db:
        tablas = db.execute(
            "SELECT table_name FROM duckdb_tables() WHERE schema_name = 'main'"
        ).fetchall()

        if not tablas:
            print("⚠️ No se encontraron tablas en el esquema 'main'.")
            return

        print(
            f"🔄 Exportando {len(tablas)} tabla(s) desde '{ruta_duckdb.name}'..."
        )

        for (nombre_tabla,) in tablas:
            ruta_salida = dir_salida_parquet / f"{nombre_tabla}.parquet"

            # COPY con formato Parquet y compresión
            sql = f"COPY {nombre_tabla} TO '{ruta_salida}' (FORMAT PARQUET, COMPRESSION '{compresion}')"
            db.execute(sql)
            print(f"  ✅ Tabla guardada: {ruta_salida.name}")

    print(
        f"✨ Exportación finalizada con éxito. Archivos guardados en: {dir_salida_parquet}"
    )


if __name__ == "__main__":
    exportar_tablas_a_parquet()