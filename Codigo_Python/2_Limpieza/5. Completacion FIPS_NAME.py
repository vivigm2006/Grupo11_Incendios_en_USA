import os
import duckdb
import geopandas as gpd
import pandas as pd
from pathlib import Path

os.environ["SHAPE_RESTORE_SHX"] = "YES"

# Rutas de archivos
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
SHP_PATH = DATA_DIR / "datos_geoespaciales_condados_eeuu" / "cb_2025_us_county_500k.shp"
DB_PATH = DATA_DIR / "Incendios_TFCompu.duckdb"

# Leer archivo shapefile de condados de EE. UU. usando GeoPandas
counties = gpd.read_file(SHP_PATH)

# Seleccionar solo los códigos de estado, condado y el nombre oficial
df_mapeo_condados = pd.DataFrame(counties[['STATEFP', 'COUNTYFP', 'NAME']]).drop_duplicates()

# Asegurar formato de texto
df_mapeo_condados['STATEFP'] = df_mapeo_condados['STATEFP'].astype(str).str.zfill(2)
df_mapeo_condados['COUNTYFP'] = df_mapeo_condados['COUNTYFP'].astype(str).str.zfill(3)
df_mapeo_condados.rename(columns={'NAME': 'fips_name_oficial'}, inplace=True)

# actualizar tabla Fires en .duckdb
conn = duckdb.connect(str(DB_PATH))

# Registrar el dataframe de mapeo como una tabla temporal en DuckDB
conn.register('temp_mapeo_condados', df_mapeo_condados)

# Consulta SQL de actualización por coincidencia de estado y condado
query_update = """
    UPDATE fires
    SET FIPS_NAME = temp_mapeo_condados.fips_name_oficial
    FROM temp_mapeo_condados
    WHERE lpad(cast(fires.STATE_CODE as VARCHAR), 2, '0') = temp_mapeo_condados.STATEFP
      AND lpad(cast(fires.FIPS_CODE as VARCHAR), 3, '0') = temp_mapeo_condados.COUNTYFP
      AND (fires.FIPS_NAME IS NULL OR fires.FIPS_NAME = '')
"""

res = conn.execute(query_update).fetchone()
registros_actualizados = res[0] if res else 0

print(f"¡Éxito! Se asignó el nombre a {registros_actualizados:,} registros de condados.")

conn.close()
print("Proceso finalizado.")