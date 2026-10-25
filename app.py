"""
Vista principal de la aplicacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import pandas as pd


# CONFIGURACION DE LA PAGINA
st.set_page_config(
    page_title="Incendios forestales y segmentacion territorial (1992-20015)",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("Incendios forestales y segmentacion territorial (1992-20015)")

# CONEXCION DE LA DATA

# BARRA LATERAL

with st.sidebar:
    st.title("Ventana seleccionada")
    st.caption("seleccion de la parte de la investigacion a visualizar")

st.image("assets/imagen.jpg", caption="Incendios forestales en EE.UU. (1992-2015)")
