"""
Cuestionario SQL - seis consultas

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import plotly.express as px


st.set_page_config(page_title="Cuestionario SQL", page_icon="🪓", layout="wide")


st.title("Cuestionario SQL")
st.markdown("Seis querys analíticos con la data de incendios forestales EE.UU. (1992-20015)")
