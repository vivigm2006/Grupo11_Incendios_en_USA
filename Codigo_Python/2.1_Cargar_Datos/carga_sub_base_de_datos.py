from pathlib import Path
import duckdb


def obtener_rutas():
    ruta_script = Path(__file__).resolve()
    raiz_proyecto = ruta_script
    while raiz_proyecto.name != "Grupo11_Incendios_en_USA" and raiz_proyecto.parent != raiz_proyecto:
        raiz_proyecto = raiz_proyecto.parent
    if raiz_proyecto.name != "Grupo11_Incendios_en_USA":
        raiz_proyecto = ruta_script.parent.parent.parent
    db_destino = raiz_proyecto / "Data" / "Datos_Normalizados" / "sub_base_de_datos.duckdb"
    db_origen = raiz_proyecto / "Data" / "Incendios_TFCompu.duckdb"
    return raiz_proyecto, db_origen, db_destino


def poblar_sub_base_datos():
    _, db_origen_path, db_destino_path = obtener_rutas()

    con = duckdb.connect(str(db_destino_path))

    try:

        con.execute(f"ATTACH '{db_origen_path}' AS db_origen (READ_ONLY);")

        tablas_origen = con.execute("SHOW TABLES FROM db_origen;").fetchall()
        if not tablas_origen:
            raise ValueError("No se encontraron tablas en la base de datos origen.")

        tabla_origen_nombre = tablas_origen[0][0]
        print(f"Cargando datos desde la tabla origen: '{tabla_origen_nombre}'...")

        # 1. Poblar tabla_estado
        print("Poblando 'tabla_estado'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_estado (state_code, state_name, state_abbr)
            SELECT 
                STATE_CODE,
                MAX(STATE_NAME) AS state_name,
                MAX(STATE) AS state_abbr
            FROM db_origen.{tabla_origen_nombre}
            WHERE STATE_CODE IS NOT NULL
            GROUP BY STATE_CODE;
        """)

        # 2. Poblar tabla_condado
        print("Poblando 'tabla_condado'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_condado (state_code, fips_code, fips_name, land_sq_mi)
            SELECT 
                TRIM(CAST(STATE_CODE AS VARCHAR)) AS state_code,
                TRIM(CAST(FIPS_CODE AS VARCHAR)) AS fips_code,
                MAX(TRIM(FIPS_NAME)) AS fips_name,
                AVG(CAST(LAND_SQ_MI AS DOUBLE)) AS land_sq_mi
            FROM db_origen.{tabla_origen_nombre}
            WHERE STATE_CODE IS NOT NULL 
            AND FIPS_CODE IS NOT NULL 
            AND FIPS_NAME IS NOT NULL
             GROUP BY 
            TRIM(CAST(STATE_CODE AS VARCHAR)),
            TRIM(CAST(FIPS_CODE AS VARCHAR));
        """)

        # 3. Poblar tabla_causa_incendio
        print("Poblando 'tabla_causa_incendio'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_causa_incendio (cause_code, cause_descr)
            SELECT DISTINCT
                CAST(STAT_CAUSE_CODE AS SMALLINT) AS cause_code,
                STAT_CAUSE_DESCR
            FROM db_origen.{tabla_origen_nombre}
            WHERE STAT_CAUSE_CODE IS NOT NULL 
              AND STAT_CAUSE_DESCR IS NOT NULL;
        """)

        # 4. Poblar tabla_propietario
        print("Poblando 'tabla_propietario'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_propietario (owner_code, owner_descr)
            SELECT DISTINCT
                TRIM(CAST(OWNER_CODE AS VARCHAR)) AS owner_code,
                MAX(TRIM(OWNER_DESCR)) AS owner_descr
            FROM db_origen.{tabla_origen_nombre}
            WHERE OWNER_CODE IS NOT NULL 
              AND OWNER_DESCR IS NOT NULL
              GROUP BY TRIM(CAST(OWNER_CODE AS VARCHAR));
        """)

        # 5. Poblar tabla_clase_tamano
        print("Poblando 'tabla_clase_tamano'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_clase_tamano (fire_size_class, min_acres, max_acres)
            SELECT 
                FIRE_SIZE_CLASS,
                MIN(FIRE_SIZE) AS min_acres,
                MAX(FIRE_SIZE) AS max_acres
            FROM db_origen.{tabla_origen_nombre}
            WHERE FIRE_SIZE_CLASS IS NOT NULL
            GROUP BY FIRE_SIZE_CLASS;
        """)

        # 6. Poblar tabla_geographic_area
        print("Poblando 'tabla_geographic_area'...")
        con.execute(f"""
            INSERT OR IGNORE INTO tabla_geographic_area (geographic_area_code, geographic_area_name)
            SELECT 
                TRIM(CAST(GeographicArea AS VARCHAR)) AS geographic_area_code,
                MAX(TRIM(GEO_AREA_NAME)) AS geographic_area_name
            FROM db_origen.{tabla_origen_nombre}
            WHERE GeographicArea IS NOT NULL 
              AND GEO_AREA_NAME IS NOT NULL
            GROUP BY TRIM(CAST(GeographicArea AS VARCHAR));
        """)

        # 7. Poblar tabla_incendios
        print("Poblando 'tabla_incendios'...")
        con.execute(f"""
            INSERT INTO tabla_incendios (
                objectid,
                discovery_date,
                cont_date,
                fire_size_class,
                fire_size,
                latitude,
                longitude,
                cause_code,
                owner_code,
                state_code,
                fips_code,
                geographic_area_code
            )
            SELECT DISTINCT
                CAST(OBJECTID AS INTEGER) AS objectid,
                CAST(DISCOVERY_DATE AS DATE) AS discovery_date,
                CAST(CONT_DATE AS DATE) AS cont_date,
                FIRE_SIZE_CLASS,
                CAST(FIRE_SIZE AS DOUBLE) AS fire_size,
                CAST(LATITUDE AS DOUBLE) AS latitude,
                CAST(LONGITUDE AS DOUBLE) AS longitude,
                CAST(STAT_CAUSE_CODE AS SMALLINT) AS cause_code,
                CAST(OWNER_CODE AS SMALLINT) AS owner_code,
                STATE_CODE,
                LPAD(CAST(FIPS_CODE AS VARCHAR), 3, '0') AS fips_code,
                GeographicArea AS geographic_area_code
            FROM db_origen.{tabla_origen_nombre}
            WHERE OBJECTID IS NOT NULL
              AND STATE_CODE IS NOT NULL
              AND GeographicArea IS NOT NULL
              AND STAT_CAUSE_CODE IS NOT NULL
              AND OWNER_CODE IS NOT NULL;
        """)

        print("Carga de datos finalizada exitosamente")

    finally:
        con.execute("DETACH db_origen;")
        con.close()


if __name__ == "__main__":
    poblar_sub_base_datos()