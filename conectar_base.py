import os
import duckdb
from dotenv import load_dotenv

#cargamos el token del archivo .env
load_dotenv()
token = os.getenv("MOTHERDUCK_TOKEN")

if not token:
    print("No se encontró el token")
else:
    print("Token detectado. Conectando a MotherDuck...")
    
    #la conexion a la base de datos 
    con = duckdb.connect(f"md:incendios_usa?motherduck_token={token}")
    
    #y consultamos las tablas 
    tablas = con.sql("SHOW TABLES;").fetchall()
    print("CONEXIÓN EXITOSA")
    print("Tablas disponibles en incendios_usa:", tablas)