from pathlib import Path
import duckdb


# Definir rutas y crear carpetas
def obtener_ruta_db():
    ruta_codigo = Path(__file__).resolve()
    raiz_proyecto = ruta_codigo.parent.parent.parent
    carpeta_destino = raiz_proyecto / "Data" / "Datos_Normalizados"
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    return carpeta_destino / "sub_base_de_datos.duckdb"


def crear_esquema():
    db_path = obtener_ruta_db()
    print(f"Conectando a la base de datos en: {db_path}")

    con = duckdb.connect(str(db_path))

    ddl_script = """
    CREATE TABLE IF NOT EXISTS tabla_estado (
      state_code VARCHAR(2) PRIMARY KEY,
      state_name VARCHAR NOT NULL,
      state_abbr VARCHAR(2)
    );

    CREATE TABLE IF NOT EXISTS tabla_condado (
      state_code VARCHAR(2) NOT NULL,
      fips_code VARCHAR(3) NOT NULL,
      fips_name VARCHAR NOT NULL,
      PRIMARY KEY (state_code, fips_code),
      FOREIGN KEY (state_code) REFERENCES tabla_estado (state_code)
    );

    CREATE TABLE IF NOT EXISTS tabla_causa_incendio (
      cause_code SMALLINT PRIMARY KEY,
      cause_descr VARCHAR UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tabla_propietario (
      owner_code SMALLINT PRIMARY KEY,
      owner_descr VARCHAR UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tabla_clase_tamano (
      fire_size_class VARCHAR(1) PRIMARY KEY,
      min_acres DOUBLE NOT NULL,
      max_acres DOUBLE
    );

    CREATE TABLE IF NOT EXISTS tabla_geographic_area (
      geographic_area_code VARCHAR(2) PRIMARY KEY,
      geographic_area_name VARCHAR
    );

    CREATE TABLE IF NOT EXISTS tabla_incendios (
      objectid INTEGER PRIMARY KEY NOT NULL,
      discovery_date DATE NOT NULL,
      cont_date DATE,
      fire_size_class VARCHAR(1),
      fire_size DOUBLE NOT NULL,
      latitude DOUBLE NOT NULL,
      longitude DOUBLE NOT NULL,
      cause_code SMALLINT NOT NULL,
      owner_code SMALLINT NOT NULL,
      state_code VARCHAR(2) NOT NULL,
      fips_code VARCHAR(3),
      geographic_area_code VARCHAR(2) NOT NULL,
      FOREIGN KEY (fire_size_class) REFERENCES tabla_clase_tamano (fire_size_class),
      FOREIGN KEY (cause_code) REFERENCES tabla_causa_incendio (cause_code),
      FOREIGN KEY (owner_code) REFERENCES tabla_propietario (owner_code),
      FOREIGN KEY (geographic_area_code) REFERENCES tabla_geographic_area (geographic_area_code),
      FOREIGN KEY (state_code, fips_code) REFERENCES tabla_condado (state_code, fips_code)
    );
    """
    try:
        con.execute(ddl_script)
        print("Sub base de datos y tablas creadas exitosamente.")
    finally:
        con.close()


if __name__ == "__main__":
    crear_esquema()