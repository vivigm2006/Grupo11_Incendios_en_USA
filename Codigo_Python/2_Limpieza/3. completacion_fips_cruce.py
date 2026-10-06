import duckdb
import geopandas as gpd
import pandas as pd
from pathlib import Path

# Definir rutas relativas
RUTA_CODIGO = Path(__file__).resolve().parent
RAIZ_PROYECTO = RUTA_CODIGO.parent.parent
DATA = RAIZ_PROYECTO / "Data"
RUTA_SHP = DATA / "datos_geoespaciales_condados_eeuu" / "cb_2025_us_county_500k.shp"
RUTA_DUCKDB = DATA / "Incendios_TFCompu.duckdb"

# Cargar archivo de condados de EE. UU. (shapefile)
print("Cargando mapa de condados...")
counties = gpd.read_file(RUTA_SHP)

# Seleccionar columnas STATEFP, COUNTYFP y geometría
counties = counties[['STATEFP', 'COUNTYFP', 'geometry']]

# Conectar duckdb a base de datos
conn = duckdb.connect(str(RUTA_DUCKDB))

# Extraer registros con FIPS_CODE nulo pero con coordenadas válidas
df_faltantes = conn.sql("""
    SELECT 
        FOD_ID, 
        LATITUDE, 
        LONGITUDE
    FROM fires
    WHERE FIPS_CODE IS NULL 
      AND LATITUDE IS NOT NULL 
      AND LONGITUDE IS NOT NULL
""").df()

# Join espacial
if not df_faltantes.empty:
    gdf_faltantes = gpd.GeoDataFrame(
        df_faltantes,
        geometry=gpd.points_from_xy(df_faltantes['LONGITUDE'], df_faltantes['LATITUDE']),
        crs="EPSG:4326"
    )

    if gdf_faltantes.crs != counties.crs:
        gdf_faltantes = gdf_faltantes.to_crs(counties.crs)

    gdf_resueltos = gpd.sjoin(gdf_faltantes, counties, how="left", predicate="within")

# Actualización en la base de datos DuckDB
     # Filtrar valores válidos
    df_actualizar = gdf_resueltos[['FOD_ID', 'COUNTYFP']].dropna(subset=['COUNTYFP'])
    conn.register('temp_fips_recuperados', df_actualizar)

    # Actualizar mediante JOIN
    update_query = """
        UPDATE fires
        SET FIPS_CODE = temp_fips_recuperados.COUNTYFP
        FROM temp_fips_recuperados
        WHERE fires.FOD_ID = temp_fips_recuperados.FOD_ID
    """
    
    # conteo de filas afectadas
    res = conn.execute(update_query).fetchone()
    registros_actualizados = res[0] if res else len(df_actualizar)
    
    print(f"¡Éxito! Se actualizaron {registros_actualizados:,} registros en DuckDB.")

else:
    print("No se encontraron registros con FIPS_CODE faltante.")

conn.close()
print("Proceso finalizado.")