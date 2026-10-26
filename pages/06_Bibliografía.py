"""
Referencias bibliograficas y fuentes consultadas

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st

st.set_page_config(page_title="Bibliografía", page_icon="📚", layout="wide")


st.title("Bibliografía")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

st.subheader("Fuente de datos")
st.markdown("""
- Short, K. C. (2017). *Spatial wildfire occurrence data for the United States,
  1992-2015 [FPA_FOD_20170508]* (4.ª ed.). Fort Collins, CO: Forest Service Research
  Data Archive. https://doi.org/10.2737/RDS-2013-0009.4

- Tatman, R. (2020). *1.88 Million US Wildfires* [Conjunto de datos]. Kaggle.
  https://www.kaggle.com/datasets/rtatman/188-million-us-wildfires
""")

st.warning("""Licencia y cita obligatoria. El conjunto de datos se distribuye bajo licencia
CC0 (dominio publico). Fue producido con financiamiento del Gobierno de Estados Unidos y puede
 utilizarse sin permisos ni tarifas adicionales. La documentacion de la fuente exige, no obstante,
   citar el trabajo de Short (2017) en toda publicacion, presentacion o producto de investigacion que 
   lo emplee. Esta investigacion cumple dicho requisito.""")

st.subheader("Referencias sobre el fenómeno")

st.markdown("""
-Balch, J. K., Bradley, B. A., Abatzoglou, J. T., Nagy, R. C., Fusco, E. J., y Mahood, A. L. (2017).
 Human-started wildfires expand the fire niche across the United States. Proceedings of the National 
 Academy of Sciences, 114(11), 2946-2951. https://doi.org/10.1073/pnas.1617394114

-Abatzoglou, J. T., & Williams, A. P. (2016). Impact of anthropogenic climate change on wildfire
 across US western forests. Proceedings of the National Academy of Sciences (PNAS), 113(42), 11770-11775.
 https://doi.org/10.1073/pnas.1607171113

-Westerling, A. L., Hidalgo, H. G., Cayan, D. R., & Swetnam, T. W. (2006). Warming and earlier spring
 increase western US forest wildfire activity. Science, 313(5789), 940-943. 
 https://doi.org/10.1126/science.1128834

-Calkin, D. E., Gebert, K. M., Jones, J. G., y Neilson, R. P. (2005). Forest Service large fire
 area burned and suppression expenditure trends, 1970-2002. Journal of Forestry, 103(4), 179-183.
 https://doi.org/10.1093/jof/103.4.179
""")

st.subheader("Documentación")

st.markdown("""
- National Interagency Fire Center. Geographic Area Coordination Centers. https://www.nifc.gov/nicc/geographic-areas

- Shapefile de los condados de EE.UU. https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2025
""")

st.subheader("Herramientas")

st.markdown("""
-Snowflake Inc. Streamlit Documentation. https://docs.streamlit.io/

-DuckDB Foundation. DuckDB Documentation. https://duckdb.org/docs/

-Apache Software Foundation. Apache Parquet Documentation. https://parquet.apache.org/docs/

-Plotly Technologies Inc. Plotly Python Open Source Graphing Library. https://plotly.com/python/

-Microsof. Power BI Documentation https://learn.microsoft.com/en-us/power-bi/

""")