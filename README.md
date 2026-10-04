# GRUPO 11 
# Análisis y Visualización Interactiva de Incendios Forestales

<div align="justify">
El presente es un proyecto de procesamiento de datos masivos para el desarrollo de tableros interactivos y su documentacion teorica respectiva, a partir de la base de datos de incendios forestales de EE. UU. (<i>FPA FOD</i>).
</div>

## 📌 Descripción del Proyecto

<div align="justify">
Este repositorio es el resultado del trabajo realizado para completar el trabajo final de la materia <b>Computación II</b> de la Escuela de Estadistica y Ciencias Actuariales de la UCV.
</div>
<br>
<div align="justify">
El objetivo principal es construir un pipeline integral de datos que abarca desde la ingesta de datos brutos en formato SQLite, su transformación y optimización mediante <b>DuckDB</b> y <b>Python</b>, hasta el consumo en una aplicación interactiva en <b>Streamlit</b> y un panel de control corporativo en <b>Power BI</b>.
</div>

## 📊 Fuente de Datos

<div align="justify">
El dataset original utilizado corresponde a la base de datos de incendios forestales de EE. UU. (<b>FPA FOD</b>), la cual contiene aproximadamente 1.88 millones de registros que van desde 1992 hasta 2015.
</div>
<br>
<div align="justify">
Debido a restricciones de tamaño de archivos en GitHub (el archivo SQLite original pesa mas de 750 MB), la base de datos completa no se incluye directamente en este repositorio. Puede ser descargada desde Kaggle en el siguiente enlace:
</div>
<br>
<ul>
  <li><b>Dataset original en Kaggle:</b> <a href="https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires">1.88 Million US Wildfires</a></li>
</ul>
</div>
<br>
<div align="justify">
Para facilitar la ejecución rápida del proyecto, se incluyo en el repositorio la versión en formato .parquet de la tabla Fire, (dentro de la carpeta data/), la cual fue generada mediante DuckDB omitiendo la geometría pesada (Shape). Dicha tabla representa la base para el desarrollo del resto del trabajo.
</div>


## 🛠️ Tecnologías Utilizadas

- Lenguaje: Python 3.14+
- Motor SQL / Analítico: DuckDB
- Formatos de Almacenamiento: SQLite, .duckdb, Parquet
- Visualización Web: Streamlit
- Business Intelligence: Power BI
- Control de Versiones: Git / GitHub

## 👥 Autores
Grupo 11 Computacion II

- Fabiola Bocaney
- Victoria Gilson
- Diego Guerrero
- Carlos Herrera
- Mariangel Morales
- Valeria Ruza

<a href="https://github.com/vivigm2006/Grupo11_Incendios_en_USA/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=vivigm2006/Grupo11_Incendios_en_USA" />
</a>

</div>
