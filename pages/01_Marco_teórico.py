"""
Planteamiento del problema y Marco Teórico de la Investigacción

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Incendios forestales y segmentacion territorial (1992-20015)",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded")


# BARRA LATERAL

with st.sidebar:
    st.audio("assets/mixfuego.mp3", format="audio/mp3", start_time=0)

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

st.set_page_config(page_title="Marco Teórico", page_icon="🚨", layout="wide")

st.image("assets/imagen.jpg", width="stretch")
st.title("Marco Teórico")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")



st.markdown("---")
st.header("1. Planteamiento del problema")

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

st.header("2 Preguntas de investigación")

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
    
st.markdown("---")

# JUATIFICACION Y LIMITACIONES

st.header("3. Justificación y Limitación")

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

st.markdown("---")

# OBJETIVOS DE INVESTIGACION
st.header("4. Objetivos de investigación")

st.subheader("Objetivo General")
    
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

st.markdown("---")

st.header("5. Antecedentes de la investigación")
st.subheader("Fuente de Datos  FPA FOD ")

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

st.subheader("Antecedente Directo: Short (2015) ")
st.markdown("""
Como antecedente directo para esta investigación, se destaca el trabajo de Short (2015), titulado _"Spatial and temporal patterns of wildfire ignitions 
in the UnitedStates"_, publicado en el _International Journal of Wildland Fire_, *realizado por Karen C. Short* la investigadora principal del Servicio Forestal de EE. UU. que estructuró y publicó 
originalmente la base de datos FPA FOD.

En este estudio, la autora analiza los patrones espaciales y temporales de más de 1.5 millones de registros de incendios forestales comprendidos entre 1992 y 2011,
utilizando el repositorio oficial FPA FOD. La investigación detalla cómo varían las tasas de ignición según la entidad administradora y la región geográfica, 
estableciendo metodologías clave para comprender la concentración espacial del fuego. Este antecedente respalda conceptualmente el presente proyecto al validar 
la importancia de procesar y visualizar grandes volúmenes de datos históricos para identificar tendencias regionales y temporales de riesgo.
""")

st.markdown("---")

st.header("6. Regionalización Operativa Oficial de Estados Unidos del NIFC y NICC")
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

st.markdown("---")

st.header("7.Bases Teóricas")

col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("Severidad y Magnitud de los Incendios ")
    st.markdown("""
    <div class="justificado">
    La severidad y magnitud de un evento se cuantifican principalmente a través de la superficie final afectada (medida en acres).
    Conforme a los estándares del National Wildfire Coordinating Group (NWCG) integrados en la base de datos, los incendios se estructuran en clases de 
    tamaño (de la A a la G), donde las categorías de mayor rango (Clases F y G, que superan los 1,000 y 5,000 acres respectivamente) representan los 
    eventos de extrema severidad o mega-incendios. 
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Estacionalidad")
    st.markdown("""
    <div class="justificado">
     La estacionalidad en la dinámica de incendios forestales se define como el comportamiento cíclico y temporal en la concentración de eventos a lo largo del año.
    Según los reportes operativos del National Interagency Coordination Center (NICC), este fenómeno está condicionado por la interacción entre 
    las condiciones meteorológicas estacionales y la desecación de los combustibles vegetales. La identificación de los meses o estaciones de mayor
    riesgo permite caracterizar los períodos críticos de respuesta operativa para cada Área Geográfica .
     </div>
     """, unsafe_allow_html=True)
    
    

    
with col_der:
    
    st.subheader("Causas de Ignición")
    st.markdown("""
    <div class="justificado">
    La base de datos FPA FOD clasifica las causas de ignición en dos categorías principales: humanas y naturales. 
    Las causas humanas incluyen actividades como quema controlada, negligencia, maquinaria y vandalismo, mientras que
    las causas naturales se atribuyen principalmente a rayos. Esta distinción es crucial para comprender los patrones de riesgo de cada región.
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Administración del Suelo")
    st.markdown("""
    <div class="justificado">
     Bajo los marcos interagenciales del NIFC y NWCG, la administración del territorio se divide en tres categorías principales: terrenos bajo administración federal, estatal y privado. 
     En los registros del FPA FOD se encuentran, terrenos bajo administración federal ,gestionados por agencias como el USDA Forest Service, el Bureau of Land Management (BLM) o el National
     Park Service (NPS), terrenos estatales o locales, se identifican bajo etiquetas como: State/Local , y terrenos de propiedad privada. Esta distinción es clave para el análisis, ya que los diferentes tipos
     de propiedad operan bajo distintas políticas de manejo de combustibles, presupuestos de supresión y protocolos de respuesta, lo que puede influir
     en los tiempos de contención y en la severidad final del impacto.   
    </div>
    """, unsafe_allow_html=True)
    