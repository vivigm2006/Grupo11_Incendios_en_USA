"""
Marco teorico de la investigacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marco Teórico", page_icon="🚨", layout="wide")

st.image("imagen.jpg", width="stretch")
st.title("Marco Teórico")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

st.subheader("1.Plantamiento del problema")

st.markdown("""
<div class="text-justify">
Los incendios forestales representan uno de los fenómenos ambientales de mayor 
impacto en la gestión territorial, la biodiversidad y la economía de los Estados Unidos.
Entre 1992 y 2015, se registraron cerca de 1.88 millones de eventos a nivel nacional; sin embargo, 
abordar esta problemática de manera única en todo el país oculta profundas diferencias ecológicas,
climáticas y antropogénicas. <br><br>

La diversidad geográfica de Estados Unidos genera dinámicas de fuego radicalmente distintas:
mientras que ciertas zonas experimentan una alta frecuencia de incendios de menor tamaño 
asociados a actividades humanas o manejo de tierras, otras regiones concentran la mayor parte
de la devastación territorial debido a condiciones climáticas extremas, sequías prolongadas e 
incendios de origen natural.<br><br>

Al no considerar estas características territoriales, las estrategias de gestión y mitigación
corren el riesgo de ser ineficaces. Por ello, surge la necesidad de segmentar el territorio
en 10 regiones, contrastando el comportamiento del fuego y comprender las causas estructurales 
que condicionan la severidad y frecuencia de los incendios en cada zona.<br><br>

Para abordar este problema la base de datos FPA FOD (Short, 2017) proporciona un registro
histórico continuo de incendios forestales en Estados Unidos para el período 1992–2015.
Al integrar la fecha de detección, la fecha de contención, la superficie final afectada, la 
causa de ignición (humana o natural) y el tipo de administración del suelo, esta fuente de información
permite desarrollar un análisis puramente descriptivo sobre la relación entre la ubicación geográfica
y las características de los eventos. Asimismo, al estructurar los datos según las áreas geográficas
del National Interagency Coordination Center (NICC), es posible caracterizar la distribución regional
de la severidad, identificar la concentración de mega-incendios, evaluar las variaciones estacionales
en la respuesta operativa y comparar el comportamiento del fuego según la titularidad del terreno. 
<div>
""", unsafe_allow_html=True)

# PREGUNTAS DE INVESTIGACION

st.markdown("""
""")
