import duckdb
from pathlib import Path

# Definir rutas y crear carpetas
def obtener_ruta_db():
    ruta_codigo = Path(__file__).resolve()
    raiz_proyecto = ruta_codigo.parent.parent
    carpeta_destino = raiz_proyecto / "Data" / "Datos_Normalizados"
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    return carpeta_destino / "incendios_normalizados.duckdb"


def crear_esquema():
    db_path = obtener_ruta_db()
    print(f"Conectando a la base de datos en: {db_path}")

    con = duckdb.connect(str(db_path))

    ddl_script = """
    CREATE TABLE IF NOT EXISTS tabla_estado (
      state_code VARCHAR(2) PRIMARY KEY,
      state_name VARCHAR NOT NULL
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

    CREATE TABLE IF NOT EXISTS tabla_agencia_nwcg (
      agency_code VARCHAR PRIMARY KEY,
      agency_name VARCHAR NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tabla_unidades_nwcg (
      unit_id VARCHAR PRIMARY KEY,
      unit_name VARCHAR NOT NULL,
      agency_code VARCHAR NOT NULL,
      FOREIGN KEY (agency_code) REFERENCES tabla_agencia_nwcg (agency_code)
    );

    CREATE TABLE IF NOT EXISTS tabla_tipo_sistema (
      source_system_type VARCHAR PRIMARY KEY
    );

    CREATE TABLE IF NOT EXISTS tabla_sistema_origen (
      source_system VARCHAR PRIMARY KEY,
      source_system_type VARCHAR NOT NULL,
      FOREIGN KEY (source_system_type) REFERENCES tabla_tipo_sistema (source_system_type)
    );

    CREATE TABLE IF NOT EXISTS tabla_unidad_origen (
      unidad_origen_id INTEGER PRIMARY KEY,
      source_system VARCHAR NOT NULL,
      source_reporting_unit VARCHAR NOT NULL,
      source_reporting_unit_name VARCHAR,
      FOREIGN KEY (source_system) REFERENCES tabla_sistema_origen (source_system)
    );

    CREATE TABLE IF NOT EXISTS tabla_mtbs (
      mtbs_id VARCHAR PRIMARY KEY,
      mtbs_fire_name VARCHAR
    );

    CREATE TABLE IF NOT EXISTS tabla_clase_tamano (
      fire_size_class VARCHAR(1) PRIMARY KEY,
      min_acres DOUBLE NOT NULL,
      max_acres DOUBLE
    );

    CREATE TABLE IF NOT EXISTS tabla_ics_209 (
      ics_209_incident_number VARCHAR PRIMARY KEY,
      ics_209_name VARCHAR
    );

    CREATE TABLE IF NOT EXISTS tabla_incendios (
      fod_id INTEGER PRIMARY KEY,
      objectid INTEGER UNIQUE NOT NULL,
      fpa_id VARCHAR NOT NULL,
      fire_code VARCHAR(10),
      fire_name VARCHAR,
      complex_name VARCHAR,
      local_fire_report_id VARCHAR,
      local_incident_id VARCHAR,
      ics_209_incident_number VARCHAR,
      mtbs_id VARCHAR,
      discovery_date DATE NOT NULL,
      discovery_time TIME,
      cont_date DATE,
      cont_time TIME,
      fire_size_class VARCHAR(1),
      fire_size DOUBLE NOT NULL,
      latitude DOUBLE NOT NULL,
      longitude DOUBLE NOT NULL,
      cause_code SMALLINT NOT NULL,
      owner_code SMALLINT NOT NULL,
      nwcg_unit_id VARCHAR NOT NULL,
      unidad_origen_id INTEGER NOT NULL,
      state_code VARCHAR(2) NOT NULL,
      fips_code VARCHAR(3),
      FOREIGN KEY (ics_209_incident_number) REFERENCES tabla_ics_209 (ics_209_incident_number),
      FOREIGN KEY (mtbs_id) REFERENCES tabla_mtbs (mtbs_id),
      FOREIGN KEY (fire_size_class) REFERENCES tabla_clase_tamano (fire_size_class),
      FOREIGN KEY (cause_code) REFERENCES tabla_causa_incendio (cause_code),
      FOREIGN KEY (owner_code) REFERENCES tabla_propietario (owner_code),
      FOREIGN KEY (nwcg_unit_id) REFERENCES tabla_unidades_nwcg (unit_id),
      FOREIGN KEY (unidad_origen_id) REFERENCES tabla_unidad_origen (unidad_origen_id),
      FOREIGN KEY (state_code) REFERENCES tabla_estado (state_code),
      FOREIGN KEY (state_code, fips_code) REFERENCES tabla_condado (state_code, fips_code)
    );
    """
# Probar si el esquema se crea correctamente
    try:
        con.execute(ddl_script)
        print(" Base de datos y tablas creadas exitosamente.")
    except Exception as e:
        print(f" Error al crear la base de datos: {e}")
    finally:
        con.close()


if __name__ == "__main__":
    crear_esquema()