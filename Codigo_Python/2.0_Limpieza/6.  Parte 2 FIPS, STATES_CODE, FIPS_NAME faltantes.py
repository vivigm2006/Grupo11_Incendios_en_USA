import os
import duckdb
import geopandas as gpd
import pandas as pd
from pathlib import Path

# Permitir la restauración automática de archivos de índice shx
os.environ["SHAPE_RESTORE_SHX"] = "YES"

# Configuración de rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"

SHP_PATH = DATA_DIR / "datos_geoespaciales_condados_eeuu" / "cb_2025_us_county_500k.shp"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"

print(f"Ruta DuckDB: {DB_PATH}")
print(f"Ruta Shapefile: {SHP_PATH}\n")

# conectar el archivo shapefile
print("Cargando capa espacial del Censo de EE. UU. ...")
counties = gpd.read_file(SHP_PATH)

# Seleccionar solo los campos necesarios del Shapefile
counties_sub = counties[['STATEFP', 'COUNTYFP', 'NAMELSAD', 'geometry']].copy()

# conectar a la base de datos DuckDB
conn = duckdb.connect(str(DB_PATH))


df_faltantes = conn.execute("""
    SELECT FOD_ID, STATE, LATITUDE, LONGITUDE
    FROM fires
    WHERE FIPS_CODE IS NULL OR FIPS_NAME IS NULL
""").df()

print(f"Se encontraron {len(df_faltantes)} registros a completar.\n")

if not df_faltantes.empty:
    # Convertir a GeoDataFrame usando las coordenadas GPS
    gdf_faltantes = gpd.GeoDataFrame(
        df_faltantes,
        geometry=gpd.points_from_xy(df_faltantes['LONGITUDE'], df_faltantes['LATITUDE']),
        crs="EPSG:4326"
    )

    # Reproyectar al CRS del Shapefile si difieren
    if gdf_faltantes.crs != counties.crs:
        gdf_faltantes = gdf_faltantes.to_crs(counties.crs)

# cruce con nearest neighbor
    gdf_resueltos = gpd.sjoin_nearest(
        gdf_faltantes,
        counties_sub,
        how="left"
    )

    # Evitar duplicados si una coordenada está exactamente a la misma distancia de dos polígonos
    gdf_resueltos = gdf_resueltos.drop_duplicates(subset=['FOD_ID'])

    # Preparar tabla para actualizar DuckDB
    df_actualizar = pd.DataFrame({
        'FOD_ID': gdf_resueltos['FOD_ID'],
        'STATE_CODE': gdf_resueltos['STATEFP'].astype(int),
        'FIPS_CODE': gdf_resueltos['COUNTYFP'].astype(int),
        'FIPS_NAME': gdf_resueltos['NAMELSAD']
    })

    print("\nResultados obtenidos para la actualización:")
    print(df_actualizar.to_string(index=False))

    # 5. ACTUALIZAR LA TABLA FIRES EN DUCKDB
    conn.register('temp_ultimos_5', df_actualizar)

    query_update = """
        UPDATE fires
        SET STATE_CODE = temp_ultimos_5.STATE_CODE,
            FIPS_CODE = temp_ultimos_5.FIPS_CODE,
            FIPS_NAME = temp_ultimos_5.FIPS_NAME
        FROM temp_ultimos_5
        WHERE fires.FOD_ID = temp_ultimos_5.FOD_ID;
    """

    res = conn.execute(query_update).fetchone()
    registros_actualizados = res[0] if res else len(df_actualizar)

    print(f"\n¡Éxito! Se actualizaron {registros_actualizados} registros en la base de datos DuckDB.")

conn.close()
print("Proceso finalizado correctamente.")