"""
Marco teorico de la investigacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Marco Teórico", page_icon="🚨", layout="wide")

st.markdown(
    """
<style>
.text-justify {
    text-align: justify;
    font-size: 16px;
}
.caja-pregunta {
    background-color: #10161A;  /* Color de fondo */
    border-left: 10px solid #B30000;  /* Borde izquierdo */
    padding: 28px;              /* Espacio interno */
    border-radius: 8px;         /* Bordes redondeados */
    margin: 30px 0px;           /* Espacio externo */
    text-align: center;
    font-style: italic;            /* Estilo de letra */
    font-size: 20px;            /* Tamaño de letra */
}
.OJ {
    background-color: #10161A;
    padding: 28px;              
    border-radius: 10px;         
    margin: 30px 0px;          
    text-align: center;
    font-style: italic;            
    font-size: 22px;  
    border-top: 6px solid #C7910E; /*Borde superior*/       
    border-bottom: 6px solid #C7910E; /*Borde inferior*/  
}
.JT {
    background-color: #10161A;
    padding: 28px;              
    border-radius: 8px;         
    margin: 30px 0px; 
    height: 100%;          
}
</style>
""",
    unsafe_allow_html=True,
)


st.image("assets/imagen.jpg", width="stretch")
st.title("Marco Teórico")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

st.subheader("Plantamiento del problema")

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
</div>
""", unsafe_allow_html=True)

# PREGUNTAS DE INVESTIGACION

st.subheader("Preguntas de investigación")

tab_one, tab_two, tab_three, tab_four, tab_five = st.tabs(["1", "2", "3","4","5"])

with tab_one:
    st.markdown("""
    <div class="caja-pregunta">
    "¿Cómo variaron la frecuencia, la severidad (superficie quemada) y las causas
    de los incendios forestales en Estados Unidos durante el período 1992–2015 al comparar las 10 regiones?"
    <div>
    """, unsafe_allow_html=True)

with tab_two:
   
    st.markdown("""
    <div class="caja-pregunta">
    "¿Cómo varía la causa de origen de los incendios forestales según las regiones y cuáles son 
    las principales fuentes de ignición que predominan en cada territorio?" 
    </div>
        """, unsafe_allow_html=True)
    
with tab_three:
    
    st.markdown("""
    <div class="caja-pregunta">
    "¿De qué manera se distribuyen los incendios de mayor severidad en el territorio
    nacional y qué región concentra la mayor proporción de estos eventos?" 

    </div>
    """, unsafe_allow_html=True)

with tab_four:
    
    st.markdown("""
    <div class="caja-pregunta">
    "¿Existen diferencias significativas en el tiempo de contención y el tamaño final 
    del incendio según la entidad administradora del terreno, Federal, Estatal o Privada 
    dentro de cada región? "
    </div>
    """, unsafe_allow_html=True)

with tab_five:
    
    st.markdown("""
    <div class="caja-pregunta">
    "¿Cómo varían el tiempo de contención y la magnitud de los incendios forestales a
      lo largo de las cuatro estaciones del año en cada región? "
    </div>
    """, unsafe_allow_html=True)

# JUATIFICACION Y LIMITACIONES

st.subheader("Justificación y Limitación")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""  <div class="JT" style="border-left: 5px solid #225DA3;">
    <h4 style="color:#225DA3; margin-top:0;">Justificación territorial</h4>
    <p style="font-size:14px;">Analizar individualmente los 50 estados genera una dispersión
     espacial excesiva de los datos y dificulta la extracción de patrones claros. el ajuste
     de la reagrupación en lugar de emplear divisiones político-administrativas (como las regiones 
     censales tradicionales), la delimitación territorial de este estudio adopta la clasificación
     oficial de Áreas Geográficas de Coordinación Interagencial del Centro Nacional Interagencial 
     de Incendios (NIFC / NICC). Esta estructura subdivide el territorio estadounidense en zonas de
     respuesta operativa delimitadas no por fronteras estatales rígidas, sino por la homogeneidad
     de sus patrones eco-climáticos, tipos de vegetación (combustibles forestales) y regímenes 
     históricos de fuego.<br><br>
       
    Adoptar el marco del NIFC dota a la investigación de una alta validez práctica, al evaluar
     los incendios forestales bajo las mismas unidades geográficas donde las agencias federales
     y estatales coordinan la asignación de recursos, los despachos de contención y las estrategias.
     Siendo estas regiones Northwest, Northern California, Southern California, Northern Rockies, 
     Great Basin, Rocky Mountain, Southwest, Southern, Eastern, Alaska.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""  <div class="JT" style="border-left: 5px solid #327FA8;">
        <h4 style="color:#327FA8; margin-top:0;">Limitación </h4>
        <p style="font-size:14px;">Limitación importante de la base de datos FPA FOD (Short, 2017)
        radica en la presencia de valores faltantes en la variable de fecha de contención. En el 
        conjunto de datos analizado, 891 531 registros (correspondientes al 47,31 % del total) no
        presentan la fecha de contención del incendio. Por consiguiente, los análisis descriptivos 
        vinculados al tiempo de respuesta y duración del evento (Objetivos 4 y 5) se restringen únicamente
        al subconjunto de datos que dispone de dicha información de forma completa. No obstante, para
        los objetivos restantes se emplea la totalidad del registro histórico, garantizando la 
        representatividad general del estudio. <br><br>
        </div>
        """, unsafe_allow_html=True)



# OBJETIVOS DE INVESTIGACION

st.header("Objetivo General")
    
st.markdown("""
<div class="OJ">
Analizar la relación de la ubicación geográfica y las características 
de los incendios forestales en Estados Unidos durante el período 1992–2015.
</div>
""", unsafe_allow_html=True)

st.subheader("Objetivos Específicos")

st.markdown(""" <div style="text-align: left; 
padding: 4px; 
line-height: 1.0;
font-size: 16px;">

1. Comparar la distribución y severidad de la superficie afectada por los incendios
forestales entre las regiones, para identificar las zonas de mayor susceptibilidad
y destrucción territorial.<br><br>

2. Analizar la relación entre la causa de origen del incendio, humana o natural y la 
región de ocurrencia, para determinar los patrones de las fuentes de ignición  
predominantes en cada territorio.<br><br>

3. Identificar la proporción y magnitud de los incendios de alta severidad por región,
 para identificar los territorios con mayor concentración de mega-incendios a nivel nacional.<br><br>

4. Comparar el tiempo promedio de contención y la superficie afectada de los incendios
 entre terrenos bajo administración federal  y terrenos estatales o privados en cada región, 
 para identificar diferencias en la severidad e impacto según el tipo de propiedad del suelo.<br><br> 

5. Evaluar la variación del tiempo de contención y la superficie quemada a través de las 
estaciones del año en cada región, para caracterizar el comportamiento de la respuesta 
operativa y la severidad.<br><br>
</div>
""", unsafe_allow_html=True)

st.subheader("")
