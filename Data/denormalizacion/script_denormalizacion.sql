-- CREACION DE LAS TABLAS DE DIMENSIÓN 

CREATE OR REPLACE TABLE dim_tamano AS
SELECT * FROM (VALUES 
    ('A', '<= 0.25 acres', 1, 0), ('B', '0.26 - 9.9 acres', 2, 0),
    ('C', '10 - 99.9 acres', 3, 0), ('D', '100 - 299.9 acres', 4, 0),
    ('E', '300 - 999.9 acres', 5, 0), ('F', '1,000 - 4,999.9 acres', 6, 0),
    ('G', '>= 5,000 acres', 7, 1)
) AS t(clase, rango, orden, es_megaincendio);

CREATE OR REPLACE TABLE dim_fecha AS
SELECT DISTINCT 
    CAST(STRFTIME(discovery_date, '%Y%m%d') AS INTEGER) AS fecha_key,
    discovery_date AS fecha,
    EXTRACT(YEAR FROM discovery_date) AS anio,
    EXTRACT(QUARTER FROM discovery_date) AS trimestre,
    EXTRACT(MONTH FROM discovery_date) AS mes,
    STRFTIME(discovery_date, '%B') AS nombre_mes,
    CASE WHEN EXTRACT(MONTH FROM discovery_date) IN (12,1,2) THEN 'Invierno'
         WHEN EXTRACT(MONTH FROM discovery_date) IN (3,4,5) THEN 'Primavera'
         WHEN EXTRACT(MONTH FROM discovery_date) IN (6,7,8) THEN 'Verano'
         ELSE 'Otoño' END AS estacion
FROM fires WHERE EXTRACT(YEAR FROM discovery_date) BETWEEN 2000 AND 2015;

CREATE OR REPLACE TABLE dim_region AS
SELECT DISTINCT DENSE_RANK() OVER (ORDER BY geo_area_name) AS region_key,
       geo_area_name AS region_name, geo_area_name AS region_code
FROM fires WHERE geo_area_name IS NOT NULL;

CREATE OR REPLACE TABLE dim_causa AS
SELECT DISTINCT stat_cause_code AS causa_key, stat_cause_descr AS causa_especifica,
       CASE WHEN LOWER(stat_cause_descr) = 'lightning' THEN 'Natural' ELSE 'Humana' END AS origen_causa
FROM fires;

CREATE OR REPLACE TABLE dim_administracion AS
SELECT DISTINCT owner_code + 1 AS administracion_key, owner_descr AS propietario,
       CASE WHEN LOWER(owner_descr) LIKE '%federal%' THEN 'Federal'
            WHEN LOWER(owner_descr) LIKE '%state%' THEN 'Estatal/Local'
            ELSE 'Privada' END AS tipo_administracion
FROM fires;

CREATE OR REPLACE TABLE dim_ubicacion AS
SELECT 
    DENSE_RANK() OVER (ORDER BY state_code, fips_code) AS ubicacion_key,
    state_code,
    MAX(state_name) AS state_name,
    CAST(state_code AS VARCHAR) || LPAD(CAST(fips_code AS VARCHAR), 3, '0') AS fips_5,
    MAX(COALESCE(fips_name, 'Desconocido')) AS county_name,
    MAX(CAST(land_sq_mi AS DOUBLE)) AS land_sq_mi,
    MAX(latitude) AS latitude,    
    MAX(longitude) AS longitude   
FROM fires 
WHERE state_code IS NOT NULL AND EXTRACT(YEAR FROM discovery_date) BETWEEN 1992 AND 2015
GROUP BY state_code, fips_code;

-- CREACION DE LA TABLA DE HECHOS

CREATE OR REPLACE TABLE fact_incendio AS
SELECT 
    f.fod_id,
    CAST(STRFTIME(f.discovery_date, '%Y%m%d') AS INTEGER) AS fecha_key,
    dr.region_key,
    f.stat_cause_code AS causa_key,
    f.owner_code + 1 AS administracion_key,
    f.fire_size_class AS clase,
    du.ubicacion_key,
    f.nwcg_reporting_unit_id AS nwcg_unit_id,
    1 AS incendios,
    f.fire_size AS acres,
    CASE WHEN f.cont_date IS NOT NULL THEN 1 ELSE 0 END AS tiene_contencion,
    CAST(DATE_DIFF('day', f.discovery_date, f.cont_date) AS INTEGER) AS dias_contencion
FROM fires f
LEFT JOIN dim_region dr ON f.geo_area_name = dr.region_name
LEFT JOIN dim_ubicacion du ON f.state_code = du.state_code AND CAST(f.fips_code AS VARCHAR) = RIGHT(du.fips_5, 3)
WHERE EXTRACT(YEAR FROM f.discovery_date) BETWEEN 1992 AND 2015;

-- CREACION DE LAS VISTAS POR OBJETIVO ESPECÍFICO

-- vista 1: sirve para comparar que regiones tuvieron mas incendios y caules se quemaron mas
CREATE OR REPLACE VIEW vista_obj1_distribucion_regional AS
SELECT r.region_name, COUNT(f.fod_id) AS total_incendios, SUM(f.acres) AS total_acres_quemados, AVG(f.acres) AS promedio_acres_por_incendio
FROM fact_incendio f JOIN dim_region r ON f.region_key = r.region_key GROUP BY r.region_name;

-- vista 2: sirve para saber que porcentaje de los incendios en cada region fueron causados por humanos y caules por la naturaleza
CREATE OR REPLACE VIEW vista_obj2_causas_region AS
SELECT r.region_name, c.origen_causa, COUNT(f.fod_id) AS frecuencia
FROM fact_incendio f JOIN dim_region r ON f.region_key = r.region_key JOIN dim_causa c ON f.causa_key = c.causa_key
GROUP BY r.region_name, c.origen_causa;

-- vista 3: sirve para saber en que regiones se concentran los mega-incendios. la parte de t.es_megainecndio=1 esto es
-- un filtro clave: le dice a la base de datos "ignora todos los incendios pequeños, solo cuéntame los de clase G (mayores a 5,000 acres)"
-- y luego suma sus acres y los agrupa por región.
CREATE OR REPLACE VIEW vista_obj3_megaincendios AS
SELECT r.region_name, COUNT(f.fod_id) AS total_megaincendios, SUM(f.acres) AS acres_totales_mega
FROM fact_incendio f JOIN dim_region r ON f.region_key = r.region_key JOIN dim_tamano t ON f.clase = t.clase
WHERE t.es_megaincendio = 1 GROUP BY r.region_name;

-- vista 4: sirve para saber si el tiempo que tardan en apagar un incendio cambia dependiendo de si el terreno es federal, estatal o privado
-- la parte de f.tiene_contencion = 1 es porque como casi la mitad de los datos no tienen fecha de fin
-- al poner = 1 solo promediamos los incendios que si sabemos cuánto tardaron en apagarse
CREATE OR REPLACE VIEW vista_obj4_administracion_terreno AS
SELECT r.region_name, a.tipo_administracion, AVG(f.dias_contencion) AS promedio_dias_contencion, SUM(f.acres) AS total_acres_afectados, COUNT(f.fod_id) AS conteo_incendios
FROM fact_incendio f JOIN dim_region r ON f.region_key = r.region_key JOIN dim_administracion a ON f.administracion_key = a.administracion_key
WHERE f.tiene_contencion = 1 GROUP BY r.region_name, a.tipo_administracion;

-- vista 5: sirev mo cambia la superficie quemada y los días de contención según la estación del año (invierno, primavera, verano, otoño)
CREATE OR REPLACE VIEW vista_obj5_estacionalidad AS
SELECT r.region_name, d.estacion, AVG(f.dias_contencion) AS promedio_dias_contencion, SUM(f.acres) AS total_acres_quemados, COUNT(f.fod_id) AS conteo_incendios
FROM fact_incendio f JOIN dim_region r ON f.region_key = r.region_key JOIN dim_fecha d ON f.fecha_key = d.fecha_key
WHERE f.tiene_contencion = 1 GROUP BY r.region_name, d.estacion;
