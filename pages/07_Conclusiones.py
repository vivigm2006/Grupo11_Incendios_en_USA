"""
Conclusiones de la investigacion

Investigacion: Incendios forestales y segmentacion territorial (1992-20015):
Analsis estadistico de la superficie, fuentes y tiempos de incendios en EE.UU.
 
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conclusiones", page_icon="🧯", layout="wide")

st.image("assets/imagen.jpg", width="stretch")
st.caption("Incendios forestales y segmentacion territorial (1992-20015)")

st.markdown(
    """
    <style>
        .hero-box {
            background: linear-gradient(135deg, #2b0909 0%, #5c1616 60%, #8f2418 100%);
            border-left: 6px solid #ff6b35;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 18px;
            color: #fff8f5;
        }
        .card-box {
            background-color: #18181b;
            border: 1px solid #2e2e36;
            border-left: 5px solid #f97316;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 14px;
            color: #f4f4f5;
        }
        .note-box {
            background-color: #1c1917;
            border: 1px dashed #eab308;
            border-radius: 10px;
            padding: 14px 18px;
            margin-top: 10px;
            margin-bottom: 14px;
            color: #fef9c3;
        }
        .badge {
            display: inline-block;
            background-color: rgba(249, 115, 22, 0.18);
            color: #fb923c;
            border: 1px solid rgba(249, 115, 22, 0.4);
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_card(badge: str, title: str, bullets: list[str], note: str | None = None):
    bullets_html = "".join([f"<li style='margin-bottom:6px;'>{b}</li>" for b in bullets])
    st.markdown(
        f"""
        <div class="card-box">
            <div class="badge">{badge}</div>
            <h4 style="margin: 2px 0 10px 0; color: #ffffff;">{title}</h4>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.55;">
                {bullets_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if note:
        st.markdown(
            f"""
            <div class="note-box">
                <strong>Observación metodológica:</strong> {note}
            </div>
            """,
            unsafe_allow_html=True,
        )


st.title("Conclusiones de la Investigación: Incendios Forestales en EE. UU. (1992–2015)")
st.caption("Base FPA FOD (Short, 2017) • 10 Áreas Geográficas NICC/NIFC")

st.markdown(
    """
    <div class="hero-box">
        <div class="badge">CONCLUSIÓN GENERAL</div>
        <h3 style="margin: 4px 0 10px 0; color: #ffffff;">Frecuencia y severidad territorial siguen dinámicas geográficas opuestas</h3>
        <p style="margin: 0; line-height: 1.6; font-size: 1.02rem;">
            El análisis de los <strong>1,880,336 incendios</strong> registrados entre 1992 y 2015 muestra que el este y el sur concentran
            la gran mayoría de los eventos —impulsados por causas humanas y contenidos rápidamente en fases iniciales—, mientras que el oeste
            y <strong>Alaska</strong> concentran la mayor devastación superficial debido a <strong>mega-incendios</strong>, mayor peso de causas
            naturales y estacionalidad estival extrema. En consecuencia, una estrategia nacional uniforme resulta insuficiente: las regiones
            orientales y del sur demandan estrategias enfocadas en prevención humana, mientras que el oeste y Alaska requieren mayor capacidad
            de supresión ante eventos de gran escala.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

render_card(
    badge="OBJETIVO 1 • DISTRIBUCIÓN Y SEVERIDAD",
    title="Concentración del daño territorial y dominio de la Clase G",
    bullets=[
        "<strong>Impacto nacional acumulado:</strong> A nivel nacional se quemaron <strong>140,131,045.06 acres</strong>, con una superficie media de <strong>74.52 acres por incendio</strong>.",
        "<strong>Regiones más afectadas:</strong> Destacan <strong>Alaska Area</strong> (32.2 millones de acres; 32,233,094 acres exactos), <strong>Great Basin Area</strong> (24.5M ac) y <strong>Southern Area</strong> (24.1M ac).",
        "<strong>Dominio de incendios Clase G (&ge; 5,000 acres):</strong> En casi todas las regiones occidentales y en Alaska, los eventos Clase G explican la mayor parte del área destruida —alcanzando el <strong>96 % en Alaska</strong>, <strong>85 % en Northwest</strong>, <strong>82 % en Great Basin</strong> y <strong>76 % en Northern Rockies y Northern California</strong>—.",
        "<strong>Perfil distinto en el sur:</strong> <strong>Southern Area</strong> presenta una estructura más distribuida entre incendios medianos y grandes (Clase G: 38 %, Clase C: 18 %, Clase F: 17 %, Clase E: 12 %, Clase D: 10 %).",
    ],
)

render_card(
    badge="OBJETIVO 2 • ORIGEN HUMANO VS. NATURAL",
    title="Predominio decausa humana nacional y contrastes regionales marcados",
    bullets=[
        "<strong>Panorama nacional:</strong> El <strong>85.2 %</strong> de todos los incendios en Estados Unidos tiene origen <strong>humano</strong> frente al <strong>14.8 %</strong> de origen <strong>natural</strong>.",
        "<strong>Frecuencia y dominio humano:</strong> <strong>Southern Area</strong> lidera ampliamente la frecuencia nacional (superando los 900,000 eventos, con <strong>Georgia</strong> como el estado de mayor incidencia con 168,847 incendios) y junto con <strong>Eastern Area</strong> y <strong>Southern California</strong> exhibe un dominio abrumador de igniciones humanas.",
        "<strong>Mayor peso natural en el interior oeste y Alaska:</strong> En regiones como <strong>Great Basin</strong>, <strong>Northern Rockies</strong>, <strong>Northwest</strong>, <strong>Southwest</strong> y <strong>Alaska</strong> la proporción de incendios de origen natural adquiere un peso mucho más equilibrado respecto a los humanos.",
    ],
)

render_card(
    badge="OBJETIVO 3 • EVENTOS DE ALTA SEVERIDAD",
    title="Más mega-incendios en Great Basin, mayor devastación en Alaska",
    bullets=[
        "<strong>Diferencia entre cantidad de eventos y superficie devastada:</strong> <strong>Great Basin Area</strong> registra el mayor número de mega-incendios (<strong>755 eventos</strong>, con 20.2M de acres quemados), pero <strong>Alaska Area</strong> lidera la destrucción territorial con <strong>30.9M de acres</strong> generados por <strong>650 eventos</strong> (un promedio de impacto por mega-incendio muy superior).",
        "<strong>Brecha este–oeste en eventos extremos:</strong> Después de Alaska y Great Basin, el mayor impacto superficial de mega-incendios se ubica en <strong>Northwest</strong> (11.2M ac; 408 eventos), <strong>Southwest</strong> (9.88M ac; 449 eventos) y <strong>Southern Area</strong> (9.17M ac; 462 eventos).",
        "<strong>Baja incidencia en el este:</strong> <strong>Eastern Area</strong> presenta una incidencia mínima tanto en frecuencia (<strong>39 eventos</strong>) como en extensión (<strong>623k acres</strong>).",
    ],
)

render_card(
    badge="OBJETIVO 4 • ADMINISTRACIÓN, SEVERIDAD Y CONTENCIÓN",
    title="Peso de la propiedad privada, eficacia inicial y asimetría en eventos extremos",
    bullets=[
        "<strong>Peso dominante de la propiedad privada:</strong> Los terrenos privados concentran tanto la mayor frecuencia de eventos (<strong>1,769,008 incendios</strong>) como la mayor superficie acumulada (<strong>122,274,100 acres</strong>), muy por encima de la administración estatal/local (102,670 eventos) y federal (8,658 eventos).",
        "<strong>Patrón de tamaño vs. impacto:</strong> En las tres categorías de propiedad, cerca del 85 % de los eventos son pequeños (Clases A y B: 85.5 % en terrenos federales, 83.5 % en estatales/locales y 85.5 % en privados), mientras que los pocos eventos Clase G explican la gran mayoría de la superficie quemada (<strong>81.2 % en federal</strong>, <strong>79.3 % en estatal/local</strong> y <strong>72.9 % en privada</strong>).",
        "<strong>Alta eficacia en contención inicial:</strong> El tiempo promedio general de contención es de <strong>0.6 días</strong> (con un máximo de 90 días), resolviéndose el mismo día en el <strong>76.7 %</strong> de los incendios federales, <strong>70.7 %</strong> de los privados y <strong>69.5 %</strong> de los estatales/locales. No obstante, los terrenos federales presentan una ligera mayor proporción de incendios de larga duración (2.1 % supera los 7 días frente a 1.5 % en estatal y 0.7 % en privado).",
    ],
)

render_card(
    badge="OBJETIVO 5 • COMPORTAMIENTO ESTACIONAL",
    title="Desfase entre frecuencia en primavera y severidad en verano",
    bullets=[
        "<strong>Desfase entre frecuencia y severidad estacional:</strong> Aunque la <strong>primavera</strong> (especialmente marzo y abril) registra el pico más alto de número de incendios, el <strong>verano</strong> (junio, julio y agosto) concentra la mayor destrucción territorial, alcanzando su máximo histórico en <strong>junio</strong> con <strong>35,068,342 acres</strong> quemados (frente a un promedio anual nacional de 5,838,793.54 acres).",
        "<strong>Verano extremo (junio–agosto):</strong> <strong>Alaska</strong> concentra el <strong>63 %</strong> de su área quemada anual solo en junio (y 23 % en julio); <strong>Northwest</strong> (43 % julio, 43 % agosto), <strong>Northern Rockies</strong> (37 % julio, 46 % agosto), <strong>Great Basin</strong> (39 % julio, 41 % agosto) y <strong>Northern California</strong> (38 % agosto) tienen su punto crítico en pleno verano.",
        "<strong>Primavera y transición temprana:</strong> <strong>Eastern Area</strong> concentra su mayor proporción en abril (<strong>34 %</strong>), <strong>Southern Area</strong> entre febrero y abril (<strong>12 %</strong>, <strong>20 %</strong> y <strong>19 %</strong>), y <strong>Southwest</strong> entre mayo (<strong>24 %</strong>) y junio (<strong>36 %</strong>).",
        "<strong>Otoño tardío:</strong> <strong>Southern California</strong> destaca por desplazar su pico máximo hacia <strong>octubre (25 %)</strong>, asociado a vientos secos estacionales.",
    ],
)

st.markdown(
    """
    <div class="card-box">
        <div class="badge">SÍNTESIS EJECUTIVA</div>
        <h4 style="margin: 2px 0 10px 0; color: #ffffff;">Resumen consolidado del estudio (1992–2015)</h4>
        <p style="margin: 0; line-height: 1.6;">
            Entre 1992 y 2015 (1,880,336 incendios y 140,131,045.06 acres quemados en EE. UU.), los incendios muestran un contraste
            territorial marcado: <strong>Southern Area</strong> concentra la mayor frecuencia de eventos con fuerte componente humano
            (85.2 % humano a nivel nacional), mientras que <strong>Alaska Area</strong> y <strong>Great Basin Area</strong> lideran la severidad
            y los mega-incendios (dominados por la Clase G). En propiedad del suelo, predomina la categoría privada en volumen y
            superficie, con tiempos medios de contención bajos (0.6 días) y alta resolución en el mismo día. Finalmente, la frecuencia
            máxima ocurre en primavera, pero la mayor devastación ocurre en verano (con junio como pico histórico y matices regionales
            como octubre en Southern California).
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)