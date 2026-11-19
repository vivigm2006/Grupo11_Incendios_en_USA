"""
Cuestionario SQL - seis consultas

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analisis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
"""

import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

load_dotenv()

st.set_page_config(
    page_title="Cuestionario SQL", page_icon="🔨", layout="wide"
)

st.title("Cuestionario SQL")
st.markdown(
    "Seis querys analíticos con la data de incendios forestales EE.UU."
    " (1992-2005)"
)

DATABASE_URL = os.getenv("DATABASE_URL")


@st.cache_resource
def obtener_engine():
  if not DATABASE_URL:
    raise ValueError(
        "Falta DATABASE_URL. Configúrala en tu archivo .env o en variables de"
        " entorno."
    )
  return create_engine(DATABASE_URL)


def consultar_supabase(query_sql):
  engine = obtener_engine()
  with engine.connect() as conn:
    return pd.read_sql(query_sql, conn)
