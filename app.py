"""
Vista principal de la aplicacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import pandas as pd
import plotly.express as px


# CONFIGURACION DE LA PAGINA
st.set_page_config(
    page_title="Incendios forestales y segmentacion territorial (1992-20015)",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded")

st.image("assets/imagen.jpg", width="stretch")
