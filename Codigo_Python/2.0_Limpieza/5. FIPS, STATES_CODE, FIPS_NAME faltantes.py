import os
import duckdb
import geopandas as gpd
import pandas as pd
from pathlib import Path

os.environ["SHAPE_RESTORE_SHX"] = "YES"

# Configuración de Rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
SHP_PATH = DATA_DIR / "datos_geoespaciales_condados_eeuu" / "cb_2025_us_county_500k.shp"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"

# conectar a la base de datos DuckDB
conn = duckdb.connect(str(DB_PATH))

# Cargar el archivo Shapefile
counties = gpd.read_file(SHP_PATH)





# Limpiar registros que tienen FIPS_CODE pero les falta FIPS_NAME
df_cat = pd.DataFrame(counties[['STATEFP', 'COUNTYFP', 'NAMELSAD']]).drop_duplicates()
df_cat['STATEFP'] = df_cat['STATEFP'].astype(str).str.zfill(2)
df_cat['COUNTYFP'] = df_cat['COUNTYFP'].astype(str).str.zfill(3)

conn.register('temp_catalogo', df_cat)

q_fase_a = """
    UPDATE fires
    SET FIPS_NAME = temp_catalogo.NAMELSAD
    FROM temp_catalogo
    WHERE lpad(cast(fires.STATE_CODE as VARCHAR), 2, '0') = temp_catalogo.STATEFP
      AND lpad(cast(fires.FIPS_CODE as VARCHAR), 3, '0') = temp_catalogo.COUNTYFP
      AND fires.FIPS_CODE IS NOT NULL 
      AND (fires.FIPS_NAME IS NULL OR fires.FIPS_NAME = '');
"""
res_a = conn.execute(q_fase_a).fetchone()
print(f"Fase A: Se asignó FIPS_NAME a {res_a[0] if res_a else 0:,} registros mediante catálogo.")





# Aumentar distancia de reconocimiento para los registros faltantes
df_faltantes = conn.execute("""
    SELECT FOD_ID, LATITUDE, LONGITUDE 
    FROM fires 
    WHERE (FIPS_CODE IS NULL OR FIPS_NAME IS NULL)
      AND LATITUDE IS NOT NULL 
      AND LONGITUDE IS NOT NULL
""").df()

if not df_faltantes.empty:
    print(f"Fase B: Procesando cruce espacial con vecino más cercano para {len(df_faltantes):,} registros...")
    
    gdf_faltantes = gpd.GeoDataFrame(
        df_faltantes,
        geometry=gpd.points_from_xy(df_faltantes['LONGITUDE'], df_faltantes['LATITUDE']),
        crs="EPSG:4326"
    )

    if gdf_faltantes.crs != counties.crs:
        gdf_faltantes = gdf_faltantes.to_crs(counties.crs)

    # Usar sjoin_nearest para encontrar el condado más cercano dentro de un radio de 0.05 grados
    gdf_resueltos = gpd.sjoin_nearest(
        gdf_faltantes,
        counties[['COUNTYFP', 'NAMELSAD', 'geometry']],
        how="left",
        max_distance=0.05
    )
    
    # Eliminar posibles duplicados si un punto está exactamente a la misma distancia de dos geometrías
    gdf_resueltos = gdf_resueltos.drop_duplicates(subset=['FOD_ID'])

    # Preparar datos para actualización
    df_actualizar = gdf_resueltos[['FOD_ID', 'COUNTYFP', 'NAMELSAD']].dropna(subset=['COUNTYFP'])
    df_actualizar['COUNTYFP'] = df_actualizar['COUNTYFP'].astype(int)
    
    conn.register('temp_espacial', df_actualizar)

    q_fase_b = """
        UPDATE fires
        SET FIPS_CODE = temp_espacial.COUNTYFP,
            FIPS_NAME = temp_espacial.NAMELSAD
        FROM temp_espacial
        WHERE fires.FOD_ID = temp_espacial.FOD_ID;
    """
    res_b = conn.execute(q_fase_b).fetchone()
    print(f"Fase B: Se actualizaron {res_b[0] if res_b else 0:,} registros mediante cruce espacial por proximidad.")

conn.close()
print("\n¡Limpieza de nulos finalizada con éxito!")