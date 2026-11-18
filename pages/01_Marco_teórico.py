"""
Marco teorico de la investigacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st

st.set_page_config(page_title="Marco Teórico", page_icon="🚨", layout="wide")

st.image("assets/imagen.jpg", width="stretch")
st.title("Marco Teórico")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

import pandas as pd

st.markdown("---")
st.header("1. Antecedentes de la investigación")
st.subheader("1.1. Fuente de Datos  FPA FOD ")

st.markdown("""
El análisis desarrollado en esta investigación se fundamenta en la utilización del conjunto de datos oficial denominado FPA FOD 
(Fire Program Analysis Fire-Occurrence Database), un registro histórico exhaustivo de incendios forestales ocurridos en los Estados Unidos.
Esta base de datos pública es recopilada y mantenida por el Servicio Forestal del Departamento de Agricultura de los Estados Unidos (USDA Forest Service),
bajo la dirección de investigadores principales como Karen C. Short, quienes han estandarizado y consolidado los reportes de múltiples agencias federales, estatales y locales
""")

st.markdown("""
El conjunto de datos abarca un período de 24 años, comprendiendo los registros desde 1992 hasta 2015. Durante este proceso de extracción y
unificación, se recopilaron aproximadamente 1.88 millones de registros georreferenciados, integrando información proveniente de diversas fuentes
institucionales clave en la gestión de emergencias, tales como: El Servicio Forestal (USDA Forest Service), El Departamento del Interior 
(U.S. Department of the Interior) y las agencias de protección contra incendios de nivel estatal y local
""")

st.subheader("1.2. Antecedente Directo: Short (2015) ")
st.markdown("""
Como antecedente directo para esta investigación, se destaca el trabajo de Short (2015), titulado _"Spatial and temporal patterns of wildfire ignitions 
in the UnitedStates"_, publicado en el _International Journal of Wildland Fire_, *realizado por Karen C. Short* la investigadora principal del Servicio Forestal de EE. UU. que estructuró y publicó 
originalmente la base de datos FPA FOD.

En este estudio, la autora analiza los patrones espaciales y temporales de más de 1.5 millones de registros de incendios forestales comprendidos entre 1992 y 2011,
utilizando el repositorio oficial FPA FOD. La investigación detalla cómo varían las tasas de ignición según la entidad administradora y la región geográfica, 
estableciendo metodologías clave para comprender la concentración espacial del fuego. Este antecedente respalda conceptualmente el presente proyecto al validar 
la importancia de procesar y visualizar grandes volúmenes de datos históricos para identificar tendencias regionales y temporales de riesgo.
""")

st.header("2. Regionalización Operativa Oficial de Estados Unidos del NIFC y NICC")
st.markdown("""Para la gestión integral, el monitoreo y el combate de incendios forestales en los Estados Unidos, el National Interagency Fire Center (NIFC)
y su centro operativo principal, el National Interagency Coordination Center (NICC), estructuran y dividen el territorio nacional en 10 Áreas Geográficas 
(conocidas formalmente como Geographic Area Coordination Centers o GACCs). Esta regionalización no responde únicamente a límites políticos o estatales, 
sino a criterios ecológicos, meteorológicos, de topografía y de comportamiento del fuego similares.
""")

st.subheader("Tabla de las 10 Áreas Geográficas Oficiales (NIFC / NICC)")
    
gacc_data = {
    "N.°": list(range(1, 11)),
    "Área Geográfica (GACC)": [
        "Alaska",
        "California del Norte",
        "California del Sur",
        "Noroeste",
        "Gran Cuenca",
        "Montañas Rocosas",
        "Suroeste",
        "Montañas Rocosas del Norte",
        "Área Este",
        "Área Sur",
    ],
    "Cobertura Territorial Principal": [
        "Estado de Alaska",
        "Norte de California y Hawái",
        "Sur de California",
        "Oregón y Washington",
        "Nevada, Utah, Idaho (sur), Wyoming (oeste) y partes de Oregón/California",
        "Colorado, Kansas, Nebraska, Dakota del Sur y Wyoming",
        "Arizona y Nuevo México",
        "Montana, Idaho (norte), Dakota del Norte y este de Washington",
        "20 estados del noreste y medio oeste de EE. UU.",
        "13 estados del sur y sureste, más Puerto Rico",
    ],
}

df_gacc = pd.DataFrame(gacc_data)

st.dataframe(df_gacc, use_container_width=True, hide_index=True)