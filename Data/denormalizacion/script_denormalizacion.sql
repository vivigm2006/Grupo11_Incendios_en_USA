-- 1. CREAR LAS TABLAS DE DIMENSIÓN (Primero, porque no dependen de nadie)
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
    MAX(CAST(land_sq_mi AS DOUBLE)) AS land_sq_mi 
FROM fires
WHERE state_code IS NOT NULL AND EXTRACT(YEAR FROM discovery_date) BETWEEN 2000 AND 2015
GROUP BY state_code, fips_code;

