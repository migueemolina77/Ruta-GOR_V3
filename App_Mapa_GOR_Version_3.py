import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import re
import requests
import math
import os
from folium.features import DivIcon
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


# ======================================================
# CONFIGURACION GENERAL
# ======================================================

st.set_page_config(
    page_title="MAPA GOR",
    layout="wide",
    page_icon="🦎"
)


# ======================================================
# ESTILO GENERAL - PALETA Y TIPOGRAFIA
# ======================================================

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>

    :root {
        --gor-bg: #FFFFFF;
        --gor-panel: #F3F6F4;
        --gor-panel-2: #EAF3EE;
        --gor-border: #DCE3DF;
        --gor-accent: #1F8A4C;
        --gor-accent-soft: rgba(31, 138, 76, 0.10);
        --gor-gold: #B8860B;
        --gor-gold-soft: rgba(184, 134, 11, 0.12);
        --gor-text: #1B1F24;
        --gor-text-muted: #5B6570;
        --gor-danger: #C0392B;
        --gor-danger-soft: rgba(192, 57, 43, 0.10);
        --gor-warning: #B7791F;
        --gor-warning-soft: rgba(183, 121, 31, 0.12);
        --gor-info: #1B5FA6;
        --gor-info-soft: rgba(27, 95, 166, 0.10);
        --gor-success: #2E7D32;
        --gor-success-soft: rgba(46, 125, 50, 0.10);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: var(--gor-bg);
    }

    /* --------------------------------------------------
       ENCABEZADO
       -------------------------------------------------- */

    .gor-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 4px 0 18px 0;
        border-bottom: 1px solid var(--gor-border);
        margin-bottom: 18px;
    }

    .gor-header-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: var(--gor-accent-soft);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }

    .gor-header-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--gor-text);
        margin: 0;
        letter-spacing: -0.3px;
    }

    .gor-header-subtitle {
        font-size: 13px;
        color: var(--gor-text-muted);
        margin: 2px 0 0 0;
    }

    /* --------------------------------------------------
       TABS
       -------------------------------------------------- */

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid var(--gor-border);
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        color: var(--gor-text-muted);
        font-weight: 600;
        font-size: 14px;
        border-radius: 8px 8px 0 0;
    }

    .stTabs [aria-selected="true"] {
        color: var(--gor-accent) !important;
        border-bottom: 2px solid var(--gor-accent) !important;
    }

    /* --------------------------------------------------
       INPUTS
       -------------------------------------------------- */

    .stTextArea label, .stNumberInput label, .stRadio label, .stCheckbox label {
        color: var(--gor-text) !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    .stTextArea textarea, .stNumberInput input {
        background-color: var(--gor-panel) !important;
        border: 1px solid var(--gor-border) !important;
        border-radius: 8px !important;
        color: var(--gor-text) !important;
    }

    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--gor-accent) !important;
    }

    .stButton button {
        background-color: var(--gor-accent) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
    }

    .stButton button:hover {
        opacity: 0.88;
    }

    /* --------------------------------------------------
       CONTENEDORES CON BORDE (tarjetas nativas de Streamlit)
       -------------------------------------------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--gor-panel) !important;
        border: 1px solid var(--gor-border) !important;
        border-radius: 12px !important;
    }

    /* --------------------------------------------------
       ALERTAS NATIVAS (success / error / warning / info)
       -------------------------------------------------- */

    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 13px !important;
    }

    /* --------------------------------------------------
       DIVISORES Y TEXTO
       -------------------------------------------------- */

    hr {
        border-color: var(--gor-border) !important;
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--gor-text-muted) !important;
    }

    /* --------------------------------------------------
       TARJETAS KPI PERSONALIZADAS (Tab de Analisis)
       -------------------------------------------------- */

    .gor-kpi-card {
        background: var(--gor-panel-2);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }

    .gor-kpi-label {
        font-size: 12px;
        color: var(--gor-text-muted);
        margin: 0 0 4px 0;
        font-weight: 500;
    }

    .gor-kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--gor-text);
        margin: 0;
    }

    .gor-kpi-delta {
        font-size: 12px;
        font-weight: 600;
        margin: 4px 0 0 0;
    }

    .gor-kpi-delta.up { color: var(--gor-danger); }
    .gor-kpi-delta.down { color: var(--gor-success); }
    .gor-kpi-delta.neutral { color: var(--gor-text-muted); }

    .gor-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    .gor-badge.accent { background: var(--gor-accent-soft); color: var(--gor-accent); }
    .gor-badge.gold { background: var(--gor-gold-soft); color: var(--gor-gold); }
    .gor-badge.neutral { background: rgba(139,148,158,0.15); color: var(--gor-text-muted); }

</style>
""", unsafe_allow_html=True)


def tarjeta_kpi(label, valor, delta_texto=None, delta_tono="neutral"):
    """
    Renderiza una tarjeta KPI personalizada (reemplazo de st.metric)
    con el lenguaje visual de la V3: etiqueta pequeña arriba, valor
    grande abajo, y un delta opcional con color semantico.

    delta_tono: "up" (aumento, en este contexto es negativo -> rojo),
                "down" (disminucion, en este contexto es positivo -> verde),
                "neutral" (sin color, gris)
    """

    delta_html = ""

    if delta_texto is not None:
        delta_html = f'<p class="gor-kpi-delta {delta_tono}">{delta_texto}</p>'

    html = f"""
    <div class="gor-kpi-card">
        <p class="gor-kpi-label">{label}</p>
        <p class="gor-kpi-value">{valor}</p>
        {delta_html}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# ======================================================
# ENCABEZADO PRINCIPAL
# ======================================================

st.markdown("""
<div class="gor-header">
    <div class="gor-header-icon">🦎</div>
    <div>
        <p class="gor-header-title">Mapa GOR</p>
        <p class="gor-header-subtitle">Vista operativa + análisis y optimización de rutas</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ======================================================
# ARCHIVO MAESTRO LOCAL
# ======================================================

ARCHIVO_COORDENADAS = "COORDENADAS_GOR_V2.xlsx"


# ======================================================
# PUNTOS CRITICOS VALIDADOS
# ======================================================

PUNTOS_CRITICOS_VALIDACION = {
    # ==================================================
    # COMUNIDADES
    # ==================================================

    "OASIS": {
        "lat": 3.775392,
        "lon": -71.658505,
        "tipo": "COMUNIDAD",
        "alerta": "RESTRICCION NOCTURNA FIJA",
        "radio_km": 1.0
    },
    "SANTA HELENA": {
        "lat": 3.899376,
        "lon": -71.490427,
        "tipo": "COMUNIDAD",
        "alerta": "RESTRICCION NOCTURNA PROBABLE",
        "radio_km": 1.0
    },
    "BUENOS AIRES - RUBIALITO": {
        "lat": 3.793411,
        "lon": -71.384503,
        "tipo": "COMUNIDAD",
        "alerta": "RESTRICCION NOCTURNA PROBABLE",
        "radio_km": 1.0
    },
    "EL PORVENIR": {
        "lat": 3.765052,
        "lon": -71.363584,
        "tipo": "COMUNIDAD",
        "alerta": "RESTRICCION NOCTURNA PROBABLE",
        "radio_km": 1.0
    },

    # ==================================================
    # PUENTES / CAÑOS - PUNTOS DE DESPINE
    # ==================================================
    "PUENTE CPF 1": {
        "lat": 3.813599,
        "lon": -71.433355,
        "tipo": "PUENTE",
        "alerta": "DESPINADO",
        "radio_km": 1.0
    },
    "PUENTE CAÑO MASIFERIANO": {
        "lat": 3.799900,
        "lon": -71.472938,
        "tipo": "PUENTE",
        "alerta": "DESPINADO",
        "radio_km": 1.0
    },
    "CAÑO FELICIANO": {
        "lat": 3.852608,
        "lon": -71.420776,
        "tipo": "PUENTE",
        "alerta": "DESPINADO",
        "radio_km": 1.0
    },

    # ==================================================
    # FINCAS / RELACIONAMIENTO
    # ==================================================
    "LA PALOMA": {
        "lat": 3.726750,
        "lon": -71.421637,
        "tipo": "FINCA",
        "alerta": "RELACIONAMIENTO ENTORNO / TIERRAS",
        "radio_km": 1.0
    },
    "LINCON": {
        "lat": 3.723330,
        "lon": -71.530597,
        "tipo": "FINCA",
        "alerta": "RELACIONAMIENTO ENTORNO / TIERRAS",
        "radio_km": 1.0
    },
    "TIYABA": {
        "lat": 3.809906,
        "lon": -71.595794,
        "tipo": "FINCA",
        "alerta": "RELACIONAMIENTO ENTORNO / TIERRAS",
        "radio_km": 1.0
    }
}

# ======================================================
# AEROPUERTO MORELIA
# ======================================================
# Se maneja por separado porque tiene dos radios:
# 2 km = alerta critica
# 5 km = alerta preventiva

AEROPUERTO_MORELIA = {
    "nombre": "AEROPUERTO MORELIA",
    "lat": 3.750656,
    "lon": -71.455936,
    "radio_critico_km": 2.0,
    "radio_preventivo_km": 5.0
}

def evaluar_alertas_aeropuerto(geom):
    """
    Evalua si la ruta pasa dentro de los radios del Aeropuerto Morelia.
    Radio 2 km = alerta critica.
    Radio 5 km = alerta preventiva.
    """

    alertas_aeropuerto = []

    distancia_min = distancia_minima_a_ruta_km(
        AEROPUERTO_MORELIA["lat"],
        AEROPUERTO_MORELIA["lon"],
        geom
    )

    if distancia_min is None:
        return alertas_aeropuerto

    if distancia_min <= AEROPUERTO_MORELIA["radio_critico_km"]:
        alertas_aeropuerto.append({
            "tipo": "AEROPUERTO_CRITICO",
            "nombre": AEROPUERTO_MORELIA["nombre"],
            "mensaje": (
                f"✈️ ALERTA CRITICA AEROPUERTO MORELIA: "
                f"ruta dentro del radio de 2 km "
                f"({distancia_min:.2f} km)"
            ),
            "distancia_km": distancia_min,
            "radio_km": AEROPUERTO_MORELIA["radio_critico_km"]
        })

    elif distancia_min <= AEROPUERTO_MORELIA["radio_preventivo_km"]:
        alertas_aeropuerto.append({
            "tipo": "AEROPUERTO_PREVENTIVO",
            "nombre": AEROPUERTO_MORELIA["nombre"],
            "mensaje": (
                f"✈️ PRECAUCION AEROPUERTO MORELIA: "
                f"ruta dentro del radio de 5 km "
                f"({distancia_min:.2f} km)"
            ),
            "distancia_km": distancia_min,
            "radio_km": AEROPUERTO_MORELIA["radio_preventivo_km"]
        })

    return alertas_aeropuerto

# ======================================================
# FUNCIONES TECNICAS
# ======================================================

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula distancia aproximada entre dos coordenadas geograficas en kilometros.
    """

    R = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distancia_punto_a_segmento_km(p_lat, p_lon, a_lat, a_lon, b_lat, b_lon):
    """
    Calcula la distancia minima aproximada entre un punto critico y un segmento de ruta.
    Usa proyeccion local en km, suficiente para distancias cortas dentro del campo.
    """

    lat_ref = math.radians(p_lat)

    km_por_grado_lat = 110.574
    km_por_grado_lon = 111.320 * math.cos(lat_ref)

    ax = (a_lon - p_lon) * km_por_grado_lon
    ay = (a_lat - p_lat) * km_por_grado_lat

    bx = (b_lon - p_lon) * km_por_grado_lon
    by = (b_lat - p_lat) * km_por_grado_lat

    dx = bx - ax
    dy = by - ay

    if dx == 0 and dy == 0:
        return math.sqrt(ax ** 2 + ay ** 2)

    t = -((ax * dx) + (ay * dy)) / (dx ** 2 + dy ** 2)
    t = max(0, min(1, t))

    punto_cercano_x = ax + t * dx
    punto_cercano_y = ay + t * dy

    distancia = math.sqrt(
        punto_cercano_x ** 2 +
        punto_cercano_y ** 2
    )

    return distancia


def distancia_minima_a_ruta_km(lat, lon, geom):
    """
    Calcula la distancia minima entre un punto critico y toda la geometria de la ruta.
    geom debe venir como lista: [[lat, lon], [lat, lon], ...]
    """

    if not geom or len(geom) == 0:
        return None

    if len(geom) == 1:
        return haversine(lat, lon, geom[0][0], geom[0][1])

    distancias = []

    for i in range(len(geom) - 1):
        a_lat, a_lon = geom[i]
        b_lat, b_lon = geom[i + 1]

        d = distancia_punto_a_segmento_km(
            lat,
            lon,
            a_lat,
            a_lon,
            b_lat,
            b_lon
        )

        distancias.append(d)

    return min(distancias)


def evaluar_alertas_puntos_criticos(geom):
    """
    Evalua si la ruta pasa dentro del radio de algun punto critico:
    - Comunidad
    - Puente / Caño
    - Finca
    """

    alertas_detectadas = []

    for nombre, punto in PUNTOS_CRITICOS_VALIDACION.items():

        tipo = punto["tipo"]
        radio_km = punto.get("radio_km", 1.0)

        distancia_min = distancia_minima_a_ruta_km(
            punto["lat"],
            punto["lon"],
            geom
        )

        if distancia_min is None:
            continue

        if distancia_min <= radio_km:

            if tipo == "COMUNIDAD":
                mensaje = (
                    f"⚠️ {punto['alerta']}: ruta cercana a {nombre} "
                    f"({distancia_min:.2f} km | radio {radio_km:.1f} km)"
                )

            elif tipo == "PUENTE":
                mensaje = (
                    f"🚧 DESPINAR TORRE: cruce cercano a {nombre} "
                    f"({distancia_min:.2f} km | radio {radio_km:.1f} km)"
                )

            elif tipo == "FINCA":
                mensaje = (
                    f"🤝 {punto['alerta']}: ruta cercana a {nombre} "
                    f"({distancia_min:.2f} km | radio {radio_km:.1f} km)"
                )

            else:
                mensaje = (
                    f"ℹ️ Punto critico cercano: {nombre} "
                    f"({distancia_min:.2f} km | radio {radio_km:.1f} km)"
                )

            alertas_detectadas.append({
                "tipo": tipo,
                "nombre": nombre,
                "mensaje": mensaje,
                "distancia_km": distancia_min,
                "radio_km": radio_km
            })

    return alertas_detectadas


def proyectadas_a_latlon_colombia(este, norte):
    """
    Convierte coordenadas proyectadas a latitud/longitud.
    Mantiene la logica original del aplicativo funcional.
    """

    try:
        este = float(este)
        norte = float(norte)

        a = 6378137.0
        f = 1 / 298.257222101
        b = a * (1 - f)
        e2 = (a ** 2 - b ** 2) / a ** 2

        if este > 4000000:
            lat0_deg = 4.0
            lon0_deg = -73.0
            k0 = 0.9992
            FE = 5000000.0
            FN = 2000000.0
        else:
            lat0_deg = 4.596200417
            lon0_deg = -71.077507917
            k0 = 1.0
            FE = 1000000.0
            FN = 1000000.0

        lat0 = math.radians(lat0_deg)
        lon0 = math.radians(lon0_deg)

        M0 = a * (
            (1 - e2 / 4 - 3 * e2 ** 2 / 64) * lat0
            - (3 * e2 / 8 + 3 * e2 ** 2 / 32) * math.sin(2 * lat0)
            + (15 * e2 ** 2 / 256) * math.sin(4 * lat0)
        )

        M = M0 + (norte - FN) / k0
        mu = M / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64))

        e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))

        phi1 = (
            mu
            + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
            + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
        )

        N1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)

        R1 = (
            a * (1 - e2)
            / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
        )

        D = (este - FE) / (N1 * k0)

        lat = phi1 - (N1 * math.tan(phi1) / R1) * (
            D ** 2 / 2
            - (5 + 3 * math.tan(phi1) ** 2) * D ** 4 / 24
        )

        lon = lon0 + (
            D
            - (1 + 2 * math.tan(phi1) ** 2) * D ** 3 / 6
        ) / math.cos(phi1)

        return math.degrees(lat), math.degrees(lon)

    except Exception:
        return None, None


def obtener_ruta_osrm(p1, p2):
    """
    Consulta OSRM para obtener geometria y distancia de ruta.
    Si OSRM falla, retorna linea recta entre los dos puntos.
    """

    url = (
        "http://router.project-osrm.org/route/v1/driving/"
        f"{p1['lon']},{p1['lat']};{p2['lon']},{p2['lat']}"
        "?overview=full&geometries=geojson"
    )

    try:
        respuesta = requests.get(url, timeout=8)
        data = respuesta.json()

        if data.get("code") == "Ok":
            coords = [
                [lat, lon]
                for lon, lat in data["routes"][0]["geometry"]["coordinates"]
            ]

            distancia = data["routes"][0]["distance"] / 1000

            return coords, distancia

    except Exception:
        pass

    return [[p1["lat"], p1["lon"]], [p2["lat"], p2["lon"]]], 0


@st.cache_data
def cargar_maestro(ruta_archivo):
    """
    Carga el archivo maestro de coordenadas desde archivo local.
    El archivo debe estar en la misma carpeta del App.py.
    """

    try:
        if not os.path.exists(ruta_archivo):
            return pd.DataFrame()

        if ruta_archivo.lower().endswith(".xlsx"):
            df = pd.read_excel(ruta_archivo)
        else:
            df = pd.read_csv(
                ruta_archivo,
                encoding="latin-1",
                sep=None,
                engine="python"
            )

        df.columns = [
            re.sub(r"[^a-zA-Z]", "", str(c)).upper()
            for c in df.columns
        ]

        c_n = next(
            c for c in df.columns
            if any(k in c for k in ["POZO", "NAME", "CLUSTER"])
        )

        c_e = next(c for c in df.columns if "ESTE" in c)
        c_nt = next(c for c in df.columns if "NORTE" in c)

        df_f = df[[c_n, c_e, c_nt]].copy()
        df_f = df_f.dropna()

        df_f.columns = ["NAME", "E", "N"]

        coords = df_f.apply(
            lambda r: proyectadas_a_latlon_colombia(r["E"], r["N"]),
            axis=1
        )

        df_f["lat"] = [c[0] for c in coords]
        df_f["lon"] = [c[1] for c in coords]

        df_f["KEY"] = (
            df_f["NAME"]
            .astype(str)
            .str.replace(r"[^a-zA-Z0-9]", "", regex=True)
            .str.upper()
        )

        df_f = df_f.dropna(subset=["lat", "lon"])

        return df_f

    except Exception as e:
        st.error(f"Error cargando archivo maestro: {e}")
        return pd.DataFrame()


def buscar_punto(db, nombre):
    """
    Busca un pozo o cluster dentro del maestro.
    Usa coincidencia exacta primero y luego coincidencia parcial.
    """

    key = re.sub(r"[^a-zA-Z0-9]", "", nombre).upper()

    if key == "":
        return None

    match_exacto = db[db["KEY"] == key]

    if not match_exacto.empty:
        return match_exacto.iloc[0]

    match_contiene = db[
        db["KEY"].str.contains(
            key,
            case=False,
            na=False,
            regex=False
        )
    ]

    if not match_contiene.empty:
        return match_contiene.iloc[0]

    return None


# ======================================================
# MODULO DE OPTIMIZACION DE RUTAS (V3)
# ======================================================
# Resuelve el problema de "camino mas corto" (TSP de ruta abierta,
# con inicio y fin libres) entre los pozos seleccionados, usando
# como costo una combinacion de: km recorridos, tiempo de
# movilizacion y penalizacion por despines de torre detectados
# en la geometria real de cada tramo.
# ======================================================

@st.cache_data(show_spinner=False)
def construir_matriz_costos(
    puntos,
    costo_por_km,
    costo_por_hora,
    velocidad_kmh,
    costo_por_despine
):
    """
    Construye la matriz NxN de costos entre todos los pares de puntos
    seleccionados. Para cada par consulta OSRM (geometria + km reales),
    detecta cuantos puntos criticos tipo PUENTE cruza esa geometria
    (despines) y calcula el costo combinado del tramo.

    Retorna:
        matriz_costo: lista NxN de enteros (costo * 100, requerido por OR-Tools)
        detalle: dict {(i, j): {"km", "horas", "despines", "geom", "alertas"}}
    """

    n = len(puntos)
    matriz_costo = [[0] * n for _ in range(n)]
    detalle = {}

    for i in range(n):
        for j in range(n):

            if i == j:
                continue

            geom, km = obtener_ruta_osrm(puntos[i], puntos[j])

            horas = km / velocidad_kmh if velocidad_kmh > 0 else 0

            alertas = evaluar_alertas_puntos_criticos(geom)

            # ------------------------------------------------------
            # PREMISA 2: DESPINE POR DISTANCIA MAYOR A 30 KM
            # (misma regla que la pestaña Vista Operativa)
            # ------------------------------------------------------

            if km > 30:
                alertas.append({
                    "tipo": "DISTANCIA",
                    "nombre": "DISTANCIA MAYOR A 30 KM",
                    "mensaje": "🚚 DESPINAR TORRE POR DISTANCIA MAYOR A 30 KM",
                    "distancia_km": km,
                    "radio_km": None
                })

            # PREMISA 1 (puentes) + PREMISA 2 (distancia > 30 km) cuentan como despine
            n_despines = sum(
                1 for a in alertas if a["tipo"] in ("PUENTE", "DISTANCIA")
            )

            costo = (
                (km * costo_por_km)
                + (horas * costo_por_hora)
                + (n_despines * costo_por_despine)
            )

            matriz_costo[i][j] = int(round(costo * 100))

            detalle[(i, j)] = {
                "km": km,
                "horas": horas,
                "despines": n_despines,
                "geom": geom,
                "alertas": alertas
            }

    return matriz_costo, detalle


def resolver_tsp_abierto(matriz_costo, indice_inicio_fijo=None, tiempo_limite_seg=5):
    """
    Resuelve el TSP de camino abierto (fin siempre libre) usando OR-Tools.

    Tecnica: se agrega un nodo ficticio (dummy) que actua como deposito.

    - Si indice_inicio_fijo es None: el dummy se conecta con costo 0
      hacia TODOS los nodos reales -> el optimizador elige libremente
      por donde empezar.
    - Si indice_inicio_fijo tiene un valor: el dummy solo se conecta
      con costo 0 hacia ESE nodo, y con un costo altisimo hacia el
      resto -> el recorrido queda obligado a iniciar ahi.

    En ambos casos, todos los nodos reales se conectan con costo 0
    de vuelta al dummy, por lo que el final del recorrido siempre
    es libre (no hay regreso obligado al punto de partida).

    Retorna una lista con el orden optimo de indices (0-based) sobre
    los puntos originales, o None si no encuentra solucion.
    """

    n = len(matriz_costo)

    if n < 2:
        return list(range(n))

    n_total = n + 1
    dummy = n
    COSTO_PROHIBITIVO = 10 ** 12

    matriz_amp = [[0] * n_total for _ in range(n_total)]

    for i in range(n):
        for j in range(n):
            matriz_amp[i][j] = matriz_costo[i][j]

    # Salida del recorrido (nodo real -> dummy) siempre libre, costo 0
    for i in range(n):
        matriz_amp[i][dummy] = 0

    # Entrada al recorrido (dummy -> nodo real): libre o fija segun el caso
    for i in range(n):
        if indice_inicio_fijo is None:
            matriz_amp[dummy][i] = 0
        elif i == indice_inicio_fijo:
            matriz_amp[dummy][i] = 0
        else:
            matriz_amp[dummy][i] = COSTO_PROHIBITIVO

    manager = pywrapcp.RoutingIndexManager(n_total, 1, dummy)
    routing = pywrapcp.RoutingModel(manager)

    def costo_callback(from_index, to_index):
        from_nodo = manager.IndexToNode(from_index)
        to_nodo = manager.IndexToNode(to_index)
        return matriz_amp[from_nodo][to_nodo]

    transit_callback_index = routing.RegisterTransitCallback(costo_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    parametros = pywrapcp.DefaultRoutingSearchParameters()
    parametros.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    parametros.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    parametros.time_limit.FromSeconds(tiempo_limite_seg)

    solucion = routing.SolveWithParameters(parametros)

    if not solucion:
        return None

    orden = []
    index = routing.Start(0)

    while not routing.IsEnd(index):
        nodo = manager.IndexToNode(index)
        if nodo != dummy:
            orden.append(nodo)
        index = solucion.Value(routing.NextVar(index))

    return orden


def resumen_ruta(orden_indices, puntos, detalle):
    """
    Dado un orden de indices sobre 'puntos', calcula el resumen total:
    km, horas, despines y costo, recorriendo la 'detalle' ya calculada
    por construir_matriz_costos (no vuelve a llamar OSRM).
    """

    km_total = 0.0
    horas_total = 0.0
    despines_total = 0
    tramos = []

    for k in range(len(orden_indices) - 1):

        i = orden_indices[k]
        j = orden_indices[k + 1]

        d = detalle[(i, j)]

        km_total += d["km"]
        horas_total += d["horas"]
        despines_total += d["despines"]

        tramos.append({
            "origen": puntos[i],
            "destino": puntos[j],
            "km": d["km"],
            "horas": d["horas"],
            "despines": d["despines"],
            "geom": d["geom"],
            "alertas": d["alertas"]
        })

    return {
        "km_total": km_total,
        "horas_total": horas_total,
        "despines_total": despines_total,
        "tramos": tramos
    }


# ======================================================
# INTERFAZ PRINCIPAL
# ======================================================


# ======================================================
# CARGA INTERNA DEL ARCHIVO
# ======================================================

db = cargar_maestro(ARCHIVO_COORDENADAS)

if db.empty:
    st.error(
        f"❌ No se pudo cargar el archivo maestro interno: `{ARCHIVO_COORDENADAS}`"
    )

    st.warning(
        "Verifica que el archivo esté en la misma carpeta donde está `App.py`."
    )

    st.stop()


# ======================================================
# PESTAÑAS PRINCIPALES
# ======================================================

tab_operativa, tab_analisis = st.tabs([
    "🗺️ Vista Operativa",
    "📊 Análisis y Optimización de Rutas"
])


# ======================================================
# TAB 1 - VISTA OPERATIVA (logica original, sin cambios)
# ======================================================

with tab_operativa:

    # --------------------------------------------------
    # LAYOUT
    # --------------------------------------------------

    col_ui, col_map = st.columns([1.1, 3])

    # --------------------------------------------------
    # PANEL IZQUIERDO
    # --------------------------------------------------

    with col_ui:

        st.subheader("Plan de Ruta")

        entrada = st.text_area(
            "Lista de Pozos:",
            placeholder="Ejemplo:\nRB-91\nRB-158\nCASE-023",
            height=150
        )

        nombres = [
            n.strip().upper()
            for n in re.split(r"[\n,]+", entrada)
            if n.strip()
        ]

        puntos_validos = []
        nombres_no_encontrados = []

        for nombre in nombres:

            fila = buscar_punto(db, nombre)

            if fila is not None:
                puntos_validos.append({
                    "id": len(puntos_validos) + 1,
                    "buscado": nombre,
                    "n": fila["NAME"],
                    "lat": float(fila["lat"]),
                    "lon": float(fila["lon"])
                })
            else:
                nombres_no_encontrados.append(nombre)

        if nombres_no_encontrados:
            st.warning(
                "No encontrados: "
                + ", ".join(nombres_no_encontrados)
            )

        rutas_calculadas = []
        all_coords = []
        colores = ["#00FFCC", "#FF007F", "#FFD700", "#00BFFF", "#7CFC00"]

        if len(nombres) == 0:
            st.info("Ingrese mínimo dos pozos o clusters para calcular la ruta.")

        elif len(puntos_validos) < 2:
            st.info("Ingrese mínimo dos pozos o clusters válidos para calcular la ruta.")

        else:
            st.divider()

            km_totales = 0

            for i in range(len(puntos_validos) - 1):

                p_orig = puntos_validos[i]
                p_dest = puntos_validos[i + 1]

                geom, km = obtener_ruta_osrm(p_orig, p_dest)

                c = colores[i % len(colores)]

                rutas_calculadas.append({
                    "tramo": i + 1,
                    "origen": p_orig,
                    "destino": p_dest,
                    "geom": geom,
                    "km": km,
                    "color": c
                })

                km_totales += km
                all_coords.extend(geom)

                # --------------------------------------------------
                # ALERTAS AUTOMATICAS POR PUNTOS CRITICOS
                # --------------------------------------------------

                alertas = []

                alertas_puntos = evaluar_alertas_puntos_criticos(geom)
                alertas.extend(alertas_puntos)

                # --------------------------------------------------
                # ALERTA POR DISTANCIA MAYOR A 30 KM
                # --------------------------------------------------

                if km > 30:
                    alertas.append({
                        "tipo": "DISTANCIA",
                        "nombre": "DISTANCIA MAYOR A 30 KM",
                        "mensaje": "🚚 DESPINAR TORRE POR DISTANCIA MAYOR A 30 KM",
                        "distancia_km": km,
                        "radio_km": None
                    })

                # --------------------------------------------------
                # TARJETA NATIVA STREAMLIT
                # --------------------------------------------------

                with st.container(border=True):

                    st.caption(f"TRAMO {i + 1} ➜ {i + 2}")

                    st.markdown(
                        f"**{p_orig['n']} ➜ {p_dest['n']}**"
                    )

                    distancia_html = (
                        f"<h3 style='color:{c}; margin-top:0px; margin-bottom:8px;'>"
                        f"{km:.2f} KM"
                        f"</h3>"
                    )

                    st.markdown(distancia_html, unsafe_allow_html=True)

                    if len(alertas) == 0:
                        st.success("✅ Sin alertas críticas detectadas en este tramo.")

                    for alerta in alertas:

                        if alerta["tipo"] in ["PUENTE", "DISTANCIA"]:
                            st.error(alerta["mensaje"])

                        elif alerta["tipo"] == "COMUNIDAD":
                            st.warning(alerta["mensaje"])

                        elif alerta["tipo"] == "FINCA":
                            st.info(alerta["mensaje"])

                        else:
                            st.info(alerta["mensaje"])

            tarjeta_kpi("DISTANCIA TOTAL", f"{km_totales:.2f} KM")


    # ======================================================
    # MAPA DERECHO
    # ======================================================

    with col_map:

        if len(puntos_validos) >= 2 and len(rutas_calculadas) > 0:

            m = folium.Map(
                tiles=None,
                zoom_control=True
            )

            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr="Google",
                name="Satélite"
            ).add_to(m)

            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                attr="Google",
                name="Calles / GPS"
            ).add_to(m)

            folium.LayerControl(position="topright", collapsed=True).add_to(m)

            # --------------------------------------------------
            # RUTAS
            # --------------------------------------------------

            for ruta in rutas_calculadas:

                folium.PolyLine(
                    ruta["geom"],
                    color=ruta["color"],
                    weight=5,
                    opacity=0.85,
                    tooltip=(
                        f"Tramo {ruta['tramo']}: "
                        f"{ruta['origen']['n']} ➜ {ruta['destino']['n']} "
                        f"({ruta['km']:.2f} KM)"
                    )
                ).add_to(m)

            # --------------------------------------------------
            # MARCADORES DE POZOS / CLUSTERS
            # --------------------------------------------------

            for p in puntos_validos:

                c = colores[(p["id"] - 1) % len(colores)]

                label_html = f"""
                <div style="text-align:center;">
                    <div style="
                        background:{c};
                        color:black;
                        border-radius:50%;
                        width:24px;
                        height:24px;
                        line-height:24px;
                        font-weight:bold;
                        border:2px solid white;
                        font-size:9pt;">
                        {p["id"]}
                    </div>

                    <div style="
                        background:rgba(14,17,23,0.90);
                        color:white;
                        padding:3px 8px;
                        border-radius:5px;
                        font-size:9pt;
                        margin-top:4px;
                        border:1px solid {c};
                        white-space:nowrap;">
                        {p["n"]}
                    </div>
                </div>
                """

                folium.Marker(
                    [p["lat"], p["lon"]],
                    icon=DivIcon(
                        html=label_html,
                        icon_anchor=(12, 12)
                    ),
                    tooltip=p["n"]
                ).add_to(m)

            # --------------------------------------------------
            # PUNTOS CRITICOS EN MAPA
            # --------------------------------------------------

            for nombre, punto in PUNTOS_CRITICOS_VALIDACION.items():

                tipo = punto["tipo"]
                radio_km = punto.get("radio_km", 1.0)

                if tipo == "COMUNIDAD":
                    color = "orange"
                    icono = "users"
                elif tipo == "PUENTE":
                    color = "red"
                    icono = "road"
                elif tipo == "FINCA":
                    color = "blue"
                    icono = "home"
                else:
                    color = "gray"
                    icono = "info-sign"

                folium.Marker(
                    [punto["lat"], punto["lon"]],
                    icon=folium.Icon(
                        color=color,
                        icon=icono,
                        prefix="fa"
                    ),
                    tooltip=f"{tipo}: {nombre} - {punto['alerta']}"
                ).add_to(m)

                folium.Circle(
                    [punto["lat"], punto["lon"]],
                    radius=radio_km * 1000,
                    color=color,
                    weight=2,
                    fill=True,
                    fill_opacity=0.10,
                    opacity=0.50,
                    tooltip=f"{nombre} | Radio {radio_km} km | {punto['alerta']}"
                ).add_to(m)

            # --------------------------------------------------
            # AJUSTE DE ZOOM
            # --------------------------------------------------

            if all_coords:

                sw = [
                    min(p[0] for p in all_coords),
                    min(p[1] for p in all_coords)
                ]

                ne = [
                    max(p[0] for p in all_coords),
                    max(p[1] for p in all_coords)
                ]

                m.fit_bounds([sw, ne])

            st_folium(
                m,
                width="100%",
                height=700
            )

        else:
            st.info("Ingrese una ruta válida para visualizar el mapa.")


# ======================================================
# FUNCION AUXILIAR - MAPA NUMERADO (reutilizable en TAB 2)
# ======================================================

def construir_mapa_numerado(orden_indices, puntos, tramos, color_ruta):
    """
    Construye un mapa folium con:
    - La polilinea de la ruta (en el orden dado)
    - Marcadores numerados (1, 2, 3...) segun la posicion de cada
      pozo DENTRO de ese orden especifico (igual estilo que la
      pestaña Vista Operativa)
    """

    mapa = folium.Map(tiles=None, zoom_control=True)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Satélite"
    ).add_to(mapa)

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
        name="Calles / GPS"
    ).add_to(mapa)

    folium.LayerControl(position="topright", collapsed=True).add_to(mapa)

    all_coords_local = []
    despines_marcados = set()
    despines_por_distancia = []

    for tramo in tramos:
        folium.PolyLine(
            tramo["geom"],
            color=color_ruta,
            weight=5,
            opacity=0.85,
            tooltip=(
                f"{tramo['origen']['n']} ➜ {tramo['destino']['n']} "
                f"({tramo['km']:.2f} KM)"
            )
        ).add_to(mapa)
        all_coords_local.extend(tramo["geom"])

        # ----------------------------------------------
        # MARCAR PUENTES/DESPINES QUE CRUZA ESTE TRAMO
        # ----------------------------------------------

        for alerta in tramo.get("alertas", []):

            if alerta["tipo"] == "DISTANCIA":
                despines_por_distancia.append(
                    f"{tramo['origen']['n']} ➜ {tramo['destino']['n']} "
                    f"({tramo['km']:.1f} km)"
                )
                continue

            if alerta["tipo"] != "PUENTE":
                continue

            nombre_puente = alerta["nombre"]

            if nombre_puente in despines_marcados:
                continue

            despines_marcados.add(nombre_puente)

            punto_critico = PUNTOS_CRITICOS_VALIDACION.get(nombre_puente)

            if punto_critico is None:
                continue

            folium.Marker(
                [punto_critico["lat"], punto_critico["lon"]],
                icon=folium.Icon(color="red", icon="road", prefix="fa"),
                tooltip=(
                    f"🚧 DESPINE: {nombre_puente} "
                    f"({alerta['distancia_km']:.2f} km de la ruta)"
                )
            ).add_to(mapa)

            folium.Circle(
                [punto_critico["lat"], punto_critico["lon"]],
                radius=punto_critico.get("radio_km", 1.0) * 1000,
                color="red",
                weight=2,
                fill=True,
                fill_opacity=0.12,
                opacity=0.6,
                tooltip=f"{nombre_puente} | Radio {punto_critico.get('radio_km', 1.0)} km"
            ).add_to(mapa)

    if despines_marcados or despines_por_distancia:

        partes = []

        if despines_marcados:
            partes.append(
                f"🚧 Puentes cruzados: " + ", ".join(sorted(despines_marcados))
            )

        if despines_por_distancia:
            partes.append(
                f"🚚 Tramos > 30 km: " + " | ".join(despines_por_distancia)
            )

        st.caption(" — ".join(partes))

    else:
        st.caption("✅ Sin puentes ni tramos mayores a 30 km en esta ruta.")

    for pos, idx in enumerate(orden_indices):

        p = puntos[idx]
        numero = pos + 1

        label_html = f"""
        <div style="text-align:center;">
            <div style="
                background:{color_ruta};
                color:black;
                border-radius:50%;
                width:24px;
                height:24px;
                line-height:24px;
                font-weight:bold;
                border:2px solid white;
                font-size:9pt;">
                {numero}
            </div>
            <div style="
                background:rgba(14,17,23,0.90);
                color:white;
                padding:3px 8px;
                border-radius:5px;
                font-size:9pt;
                margin-top:4px;
                border:1px solid {color_ruta};
                white-space:nowrap;">
                {p["n"]}
            </div>
        </div>
        """

        folium.Marker(
            [p["lat"], p["lon"]],
            icon=DivIcon(html=label_html, icon_anchor=(12, 12)),
            tooltip=f"{numero}. {p['n']}"
        ).add_to(mapa)

    if all_coords_local:
        sw = [min(c[0] for c in all_coords_local), min(c[1] for c in all_coords_local)]
        ne = [max(c[0] for c in all_coords_local), max(c[1] for c in all_coords_local)]
        mapa.fit_bounds([sw, ne])
    elif orden_indices:
        p0 = puntos[orden_indices[0]]
        mapa.fit_bounds([[p0["lat"], p0["lon"]], [p0["lat"], p0["lon"]]])

    return mapa


# ======================================================
# TAB 2 - ANALISIS Y OPTIMIZACION DE RUTAS
# ======================================================

with tab_analisis:

    st.subheader("Análisis y Optimización de Rutas")

    st.caption(
        "Espacio independiente para analizar cualquier lista de pozos: "
        "compara el orden ingresado contra el orden sugerido por el "
        "optimizador (menor costo combinado de km, tiempo y despines)."
    )

    st.divider()

    # --------------------------------------------------
    # ENTRADA INDEPENDIENTE DE POZOS (propia de esta pestaña)
    # --------------------------------------------------

    entrada_analisis = st.text_area(
        "Lista de Pozos a analizar:",
        placeholder="Ejemplo:\nRB-91\nRB-158\nCASE-023",
        height=150,
        key="entrada_analisis_tab2"
    )

    nombres_analisis = [
        n.strip().upper()
        for n in re.split(r"[\n,]+", entrada_analisis)
        if n.strip()
    ]

    puntos_analisis = []
    no_encontrados_analisis = []

    for nombre in nombres_analisis:

        fila = buscar_punto(db, nombre)

        if fila is not None:
            puntos_analisis.append({
                "id": len(puntos_analisis) + 1,
                "buscado": nombre,
                "n": fila["NAME"],
                "lat": float(fila["lat"]),
                "lon": float(fila["lon"])
            })
        else:
            no_encontrados_analisis.append(nombre)

    if no_encontrados_analisis:
        st.warning("No encontrados: " + ", ".join(no_encontrados_analisis))

    if len(nombres_analisis) == 0:

        st.info("Ingrese mínimo dos pozos para habilitar el análisis.")

    elif len(puntos_analisis) < 2:

        st.info("Ingrese mínimo dos pozos válidos para habilitar el análisis.")

    else:

        st.divider()

        # --------------------------------------------------
        # PARAMETROS DE COSTO (editables por el usuario)
        # --------------------------------------------------

        st.markdown("**Parámetros de costo para la simulación**")

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            costo_por_km = st.number_input(
                "Costo por KM ($)",
                min_value=0.0,
                value=8000.0,
                step=500.0,
                help="Costo asociado a combustible y desgaste por km recorrido."
            )

        with col_p2:
            costo_por_hora = st.number_input(
                "Costo por hora ($)",
                min_value=0.0,
                value=150000.0,
                step=10000.0,
                help="Costo del vehiculo/cuadrilla por hora de movilizacion."
            )

        with col_p3:
            velocidad_kmh = st.number_input(
                "Velocidad promedio (km/h)",
                min_value=1.0,
                value=35.0,
                step=1.0,
                help="Velocidad promedio estimada en vias del campo."
            )

        with col_p4:
            costo_por_despine = st.number_input(
                "Costo por despine ($)",
                min_value=0.0,
                value=2000000.0,
                step=100000.0,
                help="Costo estimado (tiempo + dinero) por cada evento de despine de torre."
            )

        incluir_costo_tiempo = st.checkbox(
            "Incluir costo por tiempo en el cálculo",
            value=False,
            help=(
                "Actívalo solo si tu contrato de transporte cobra por hora. "
                "Por defecto queda apagado porque el tiempo real depende de "
                "factores muy variables (clima, derrumbes, estado de la vía) "
                "y en la mayoría de contratos el costo se factura por KM. "
                "El tiempo estimado siempre se muestra como referencia, "
                "se incluya o no en el costo."
            )
        )

        modo_inicio = st.radio(
            "Punto de partida de la ruta optimizada",
            options=["Libre (el optimizador elige el mejor inicio)", "Fijo (iniciar en el primer pozo de la lista)"],
            horizontal=False,
            help=(
                "'Libre' deja que el optimizador escoja el mejor punto de "
                "partida entre todos los pozos. 'Fijo' obliga a que la ruta "
                "sugerida siempre inicie en el primer pozo que escribiste en "
                "la lista de arriba — util cuando ya sabes desde donde va a "
                "salir la cuadrilla en la próxima campaña."
            )
        )

        st.divider()

        boton_optimizar = st.button(
            "🚀 Calcular ruta optimizada",
            type="primary",
            use_container_width=False
        )

        if boton_optimizar:
            st.session_state["analisis_calculado"] = True

        if st.session_state.get("analisis_calculado", False):

            with st.spinner("Consultando rutas reales y calculando matriz de costos..."):

                matriz_costo, detalle = construir_matriz_costos(
                    puntos_analisis,
                    costo_por_km,
                    costo_por_hora,
                    velocidad_kmh,
                    costo_por_despine
                )

                inicio_fijo = 0 if modo_inicio.startswith("Fijo") else None

                orden_actual = list(range(len(puntos_analisis)))
                orden_optimo = resolver_tsp_abierto(
                    matriz_costo,
                    indice_inicio_fijo=inicio_fijo
                )

                if orden_optimo is None:
                    st.error(
                        "No fue posible calcular una ruta optimizada. "
                        "Intente nuevamente o reduzca el numero de pozos."
                    )

                else:

                    resumen_actual = resumen_ruta(orden_actual, puntos_analisis, detalle)
                    resumen_optimo = resumen_ruta(orden_optimo, puntos_analisis, detalle)

                    def costo_total(resumen):
                        costo = (
                            (resumen["km_total"] * costo_por_km)
                            + (resumen["despines_total"] * costo_por_despine)
                        )
                        if incluir_costo_tiempo:
                            costo += resumen["horas_total"] * costo_por_hora
                        return costo

                    costo_actual_val = costo_total(resumen_actual)
                    costo_optimo_val = costo_total(resumen_optimo)

                    ahorro_costo = costo_actual_val - costo_optimo_val
                    ahorro_pct = (
                        (ahorro_costo / costo_actual_val * 100)
                        if costo_actual_val > 0 else 0
                    )

                    nota_tiempo = (
                        "(incluido en el costo)" if incluir_costo_tiempo
                        else "(solo referencial, no incluido en el costo)"
                    )

                    # ----------------------------------------------
                    # COMPARATIVO ORDEN ACTUAL VS SUGERIDO
                    # ----------------------------------------------

                    col_actual, col_optimo = st.columns(2)

                    with col_actual:
                        with st.container(border=True):
                            st.markdown("### 📋 Orden Actual (ingresado)")
                            secuencia_actual = " ➜ ".join(
                                puntos_analisis[i]["n"] for i in orden_actual
                            )
                            st.caption(secuencia_actual)
                            tarjeta_kpi("Distancia total", f"{resumen_actual['km_total']:.2f} KM")
                            tarjeta_kpi(
                                f"Tiempo estimado {nota_tiempo}",
                                f"{resumen_actual['horas_total']:.2f} horas"
                            )
                            tarjeta_kpi("Despines detectados", resumen_actual["despines_total"])
                            tarjeta_kpi("Costo estimado", f"$ {costo_actual_val:,.0f}")

                    with col_optimo:
                        with st.container(border=True):
                            st.markdown("### ✅ Orden Sugerido (optimizado)")
                            st.markdown(
                                '<span class="gor-badge gold">🔒 Inicio fijo</span>'
                                if inicio_fijo is not None
                                else '<span class="gor-badge neutral">🔓 Inicio libre</span>',
                                unsafe_allow_html=True
                            )
                            secuencia_optima = " ➜ ".join(
                                puntos_analisis[i]["n"] for i in orden_optimo
                            )
                            st.caption(secuencia_optima)

                            delta_km = resumen_optimo['km_total'] - resumen_actual['km_total']
                            tarjeta_kpi(
                                "Distancia total",
                                f"{resumen_optimo['km_total']:.2f} KM",
                                f"{delta_km:+.2f} KM",
                                "up" if delta_km > 0 else "down" if delta_km < 0 else "neutral"
                            )

                            delta_horas = resumen_optimo['horas_total'] - resumen_actual['horas_total']
                            tarjeta_kpi(
                                f"Tiempo estimado {nota_tiempo}",
                                f"{resumen_optimo['horas_total']:.2f} horas",
                                f"{delta_horas:+.2f} horas",
                                "up" if delta_horas > 0 else "down" if delta_horas < 0 else "neutral"
                            )

                            delta_desp = resumen_optimo["despines_total"] - resumen_actual["despines_total"]
                            tarjeta_kpi(
                                "Despines detectados",
                                resumen_optimo["despines_total"],
                                f"{delta_desp:+d}",
                                "up" if delta_desp > 0 else "down" if delta_desp < 0 else "neutral"
                            )

                            delta_costo = costo_optimo_val - costo_actual_val
                            tarjeta_kpi(
                                "Costo estimado",
                                f"$ {costo_optimo_val:,.0f}",
                                f"$ {delta_costo:,.0f}",
                                "up" if delta_costo > 0 else "down" if delta_costo < 0 else "neutral"
                            )

                    st.divider()

                    # ----------------------------------------------
                    # CONSOLIDADO DE AHORRO
                    # ----------------------------------------------

                    st.markdown("### 💰 Consolidado de Optimización")

                    col_r1, col_r2, col_r3 = st.columns(3)

                    with col_r1:
                        tarjeta_kpi(
                            "Ahorro en KM",
                            f"{resumen_actual['km_total'] - resumen_optimo['km_total']:.2f} KM"
                        )
                    with col_r2:
                        tarjeta_kpi(
                            "Ahorro en tiempo",
                            f"{resumen_actual['horas_total'] - resumen_optimo['horas_total']:.2f} horas"
                        )
                    with col_r3:
                        tarjeta_kpi(
                            "Ahorro estimado en costo",
                            f"$ {ahorro_costo:,.0f}",
                            f"{ahorro_pct:.1f}%",
                            "down" if ahorro_costo > 0 else "up" if ahorro_costo < 0 else "neutral"
                        )

                    if ahorro_costo <= 0:
                        st.info(
                            "El orden actual ya es igual o mejor que la mejor "
                            "alternativa encontrada para los parametros dados."
                        )

                    st.divider()

                    # ----------------------------------------------
                    # DOS MAPAS INDEPENDIENTES: ACTUAL vs SUGERIDO
                    # ----------------------------------------------

                    st.markdown("### 🗺️ Mapas: Orden Actual vs Orden Sugerido")

                    col_mapa_actual, col_mapa_optimo = st.columns(2)

                    with col_mapa_actual:
                        st.caption("📋 Orden Actual — pines numerados según secuencia ingresada")
                        mapa_actual = construir_mapa_numerado(
                            orden_actual,
                            puntos_analisis,
                            resumen_actual["tramos"],
                            "#8b949e"
                        )
                        st_folium(
                            mapa_actual,
                            width="100%",
                            height=550,
                            key="mapa_tab2_actual"
                        )

                    with col_mapa_optimo:
                        st.caption("✅ Orden Sugerido — pines numerados según secuencia optimizada")
                        mapa_optimo = construir_mapa_numerado(
                            orden_optimo,
                            puntos_analisis,
                            resumen_optimo["tramos"],
                            "#00FFCC"
                        )
                        st_folium(
                            mapa_optimo,
                            width="100%",
                            height=550,
                            key="mapa_tab2_optimo"
                        )
