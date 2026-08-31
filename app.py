import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import json
from supabase import create_client

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent / "data_parquet"
FICHAS_DIR = Path(__file__).parent / "fichas"
OUT_FILE  = Path(__file__).parent / "respuestas.csv"

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

st.set_page_config(
    page_title="UIA – Internacionalización",
    page_icon="🇦🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0a1f44 !important; }
html, body, p, span, label, div, li, [class*="css"], [data-testid] { color: #ffffff !important; }
[data-testid="stSidebar"] { background-color: #071633 !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebarCollapsedControl"], button[aria-label="Open sidebar"],
button[aria-label="Close sidebar"], [data-testid="collapsedControl"] {
    background-color: #1565c0 !important; border: none !important; border-radius: 0 6px 6px 0 !important;
}
[data-testid="stSidebarCollapsedControl"] svg, [data-testid="collapsedControl"] svg {
    fill: #ffffff !important; color: #ffffff !important;
}
[data-testid="stSelectbox"] > div > div, [data-testid="stSelectbox"] > div > div > div {
    background-color: #1a3a6b !important; color: #ffffff !important;
    border: 1px solid #3a6bc4 !important; border-radius: 6px !important;
}
[data-testid="stSelectbox"] span, [data-testid="stSelectbox"] p,
[data-testid="stSelectbox"] svg { color: #ffffff !important; fill: #ffffff !important; }
[data-baseweb="popover"], [data-baseweb="popover"] ul, [data-baseweb="popover"] li,
[data-baseweb="menu"], [data-baseweb="menu"] ul, [data-baseweb="menu"] li,
[data-baseweb="select"] ul, [data-baseweb="select"] li,
ul[role="listbox"], ul[role="listbox"] li,
div[role="listbox"], div[role="listbox"] li,
div[data-baseweb="popover"] > div, div[data-baseweb="popover"] > div > ul {
    background-color: #1a3a6b !important; color: #ffffff !important;
}
ul[role="listbox"] li:hover, [data-baseweb="menu"] li:hover { background-color: #1565c0 !important; }
div[data-baseweb="popover"] * { color: #ffffff !important; background-color: #1a3a6b !important; }
input, textarea {
    background-color: #1a3a6b !important; color: #ffffff !important;
    border: 1px solid #3a6bc4 !important; border-radius: 6px !important;
}
input::placeholder, textarea::placeholder { color: #7a9acc !important; }
[data-testid="stRadio"] > div { gap: 1rem; }
[data-testid="stRadio"] label span { color: #ffffff !important; font-size: 1.05rem; }
[data-testid="stCheckbox"] label p { color: #d0e4ff !important; }
.stButton > button[kind="primary"] {
    background-color: #1565c0 !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important; font-size: 1rem !important;
}
.stButton > button[kind="primary"]:hover { background-color: #1976d2 !important; }
.stButton > button {
    background-color: #1a3a6b !important; color: #ffffff !important;
    border: 1px solid #3a6bc4 !important; border-radius: 8px !important;
}
.stButton > button:hover { background-color: #1565c0 !important; }
[data-testid="stExpander"] {
    background-color: #112244 !important; border: 1px solid #2a4a8a !important; border-radius: 8px !important;
}
[data-testid="stExpander"] summary p { color: #90caf9 !important; font-weight: 600; }
[data-testid="stDataEditor"] th { background-color: #0d2a5a !important; color: #90caf9 !important; }
[data-testid="stDataEditor"] td { background-color: #112244 !important; color: #ffffff !important; }
[data-testid="stTabs"] [role="tab"] {
    background-color: #112244 !important; color: #90caf9 !important; border-radius: 6px 6px 0 0 !important; font-weight: 600;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { background-color: #1565c0 !important; color: #ffffff !important; }
[data-testid="stMetricValue"] { color: #90caf9 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #b0c4de !important; font-size: 0.85rem !important; }
[data-testid="stAlert"] { background-color: #112244 !important; border-left: 4px solid #1565c0 !important; }
hr { border-color: #2a4a8a !important; }
h1 { color: #90caf9 !important; font-weight: 700; }
h2 { color: #90caf9 !important; font-weight: 700; }
h3 { color: #b0c4de !important; font-weight: 600; }
[data-testid="stCaptionContainer"] p { color: #7a9acc !important; }
.prog-bar { display: flex; gap: 4px; margin-bottom: 8px; }
.prog-step { flex:1; padding:8px 4px; text-align:center; border-radius:6px; font-size:0.8rem; font-weight:600; }
.prog-done { background:#1b5e20; color:#a5d6a7; }
.prog-now  { background:#1565c0; color:#ffffff; border:2px solid #90caf9; }
.prog-todo { background:#112244; color:#5a7a9a; }
.card { background:#112244; border:1px solid #2a4a8a; border-radius:10px; padding:1rem 1.4rem; margin-bottom:0.8rem; }
.disclaimer { background:#0d2a5a; border:1px solid #1565c0; border-radius:8px; padding:0.6rem 1rem; margin-bottom:1rem; font-size:0.82rem; color:#90caf9 !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES ───────────────────────────────────────────────────────────────
PAISES_CPTPP = [
    "Australia", "Brunei", "Canadá", "Chile", "Japón",
    "Malasia", "México", "Nueva Zelanda", "Perú", "Reino Unido",
    "Singapur", "Vietnam",
]
TODOS_PAISES = PAISES_CPTPP + [
    "Camboya", "Emiratos Árabes Unidos", "Filipinas",
    "India", "Indonesia", "Korea del Sur", "Laos", "Myanmar", "Tailandia",
]

NEGOCIACIONES = [
    "Unión Europea", "Estados Unidos", "EFTA", "India",
    "Canadá", "Egipto", "Israel", "Vietnam", "Indonesia",
    "Emiratos Árabes Unidos", "Japón", "Singapur", "Corea del Sur",
]

NEGOCIACIONES_STATUS = {
    "Unión Europea":        "Vigente (provisional)",
    "Estados Unidos":       "Firmado, sin ratificación parlamentaria",
    "EFTA":                 "En proceso de ratificación parlamentaria",
    "India":                "Vigente Acuerdo de Preferencias Fijas. Diálogos para ampliación",
    "Canadá":               "En negociación",
    "Egipto":               "Vigente",
    "Israel":               "Vigente",
    "Vietnam":              "Negociaciones recientemente iniciadas",
    "Indonesia":            "Negociaciones recientemente iniciadas",
    "Emiratos Árabes Unidos": "En negociación",
    "Japón":                "Negociaciones recientemente iniciadas",
    "Singapur":             "Vigente para Brasil, Paraguay y Uruguay; próxima entrada en vigor para Argentina",
    "Corea del Sur":        "Retomando negociaciones interrumpidas en 2021",
}

NOMBRE_MUNDO = {
    "Australia": "Australia", "Brunei": "Brunei", "Canadá": "Canada",
    "Chile": "Chile", "Japón": "Japon", "Malasia": "Malasia",
    "México": "Mexico", "Nueva Zelanda": "Nueva Zelanda", "Perú": "Peru",
    "Reino Unido": "Reino Unido", "Singapur": "Singapur", "Vietnam": "Vietnam",
    "Camboya": "Camboya", "Filipinas": "Filipinas", "Laos": "Laos",
    "Myanmar": "Myanmar", "Tailandia": "Tailandia",
    "Emiratos Árabes Unidos": "Emiratos Arabes Unidos",
    "Indonesia": "Indonesia",
    "India": "India",
    "Korea del Sur": "Korea del Sur",
}

PASOS = ["Subpartidas NCM", "Países e interés comercial", "Resumen"]

LINKS_ARANCELES = {
    "Australia":              "https://wits.worldbank.org/tariff/trains/en/country/AUS/partner/ARG/product/all",
    "Brunei":                 "https://wits.worldbank.org/tariff/trains/en/country/BRN/partner/ARG/product/All",
    "Camboya":                "https://wits.worldbank.org/tariff/trains/en/country/KHM/partner/ARG/product/All",
    "Canadá":                 "https://wits.worldbank.org/tariff/trains/en/country/CAN/partner/ARG/product/all",
    "Chile":                  "https://wits.worldbank.org/tariff/trains/en/country/CHL/partner/ARG/product/All",
    "Emiratos Árabes Unidos": "https://wits.worldbank.org/tariff/trains/en/country/ARE/partner/ARG/product/All",
    "Filipinas":              "https://wits.worldbank.org/tariff/trains/en/country/PHL/partner/ARG/product/All",
    "Indonesia":              "https://wits.worldbank.org/tariff/trains/en/country/IDN/partner/ARG/product/All",
    "Japón":                  "https://wits.worldbank.org/tariff/trains/en/country/JPN/partner/ARG/product/All",
    "Laos":                   "https://wits.worldbank.org/tariff/trains/en/country/LAO/partner/ARG/product/All",
    "Malasia":                "https://wits.worldbank.org/tariff/trains/en/country/MYS/partner/ARG/product/All",
    "México":                 "https://wits.worldbank.org/tariff/trains/en/country/MEX/partner/ARG/product/All",
    "Myanmar":                "https://wits.worldbank.org/tariff/trains/en/country/MMR/partner/ARG/product/All",
    "Nueva Zelanda":          "https://wits.worldbank.org/tariff/trains/en/country/NZL/partner/ARG/product/All",
    "Perú":                   "https://wits.worldbank.org/tariff/trains/en/country/PER/partner/ARG/product/All",
    "Reino Unido":            "https://wits.worldbank.org/tariff/trains/en/country/GBR/partner/ARG/product/All",
    "Singapur":               "https://wits.worldbank.org/tariff/trains/en/country/SGP/partner/ARG/product/All",
    "Tailandia":              "https://wits.worldbank.org/tariff/trains/en/country/THA/partner/ARG/product/All",
    "Vietnam":                "https://wits.worldbank.org/tariff/trains/en/country/VNM/partner/ARG/product/All",
    "India":                  "https://wits.worldbank.org/tariff/trains/en/country/IND/partner/ARG/product/All",
    "Korea del Sur":          "https://wits.worldbank.org/tariff/trains/en/country/KOR/partner/ARG/product/All",
}

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cargar_datos():
    ncm_df = pd.read_parquet(DATA_DIR / "ncm_sectores.parquet")
    ncm_df.columns = ncm_df.columns.str.strip()
    ncm_df["HSUSA"] = ncm_df["HSUSA"].astype(str).str.strip().str.zfill(6)
    ncm_df["Descripcion Partida"] = ncm_df.get("Descripcion Partida", pd.Series(dtype=str)).fillna("").astype(str).str.strip()

    camaras_df = pd.read_parquet(DATA_DIR / "camaras.parquet")
    camaras_df["PartidaNCM"] = camaras_df["PartidaNCM"].astype(str).str.strip().str.zfill(6)
    camaras_df["NbreCamara"] = camaras_df["NbreCamara"].astype(str).str.strip()

    claves_df = pd.read_parquet(DATA_DIR / "clavecamaras.parquet")
    claves_df["NbreCamara"] = claves_df["NbreCamara"].astype(str).str.strip()
    claves_df["Pass"] = claves_df["Pass"].astype(str).str.strip()

    expo_arg = pd.read_parquet(DATA_DIR / "expo_arg.parquet")
    expo_arg["pais"] = expo_arg["pais"].astype(str)
    expo_arg["fob"] = pd.to_numeric(expo_arg["fob"], errors="coerce").fillna(0)
    expo_arg["partidaNCM"] = expo_arg["partidaNCM"].astype(str).str.strip()
    expo_arg["ncm6"] = expo_arg["partidaNCM"].str[:6].str.zfill(6)

    impo_arg = pd.read_parquet(DATA_DIR / "impo_arg.parquet")
    impo_arg["pais"] = impo_arg["pais"].astype(str)
    impo_arg["cif"] = pd.to_numeric(impo_arg["cif"], errors="coerce").fillna(0)
    impo_arg["partidaNCM"] = impo_arg["partidaNCM"].astype(str).str.strip()
    impo_arg["ncm6"] = impo_arg["partidaNCM"].str[:6].str.zfill(6)

    expo_mundo = pd.read_parquet(DATA_DIR / "expo_pais_mundo.parquet")
    expo_mundo["cmdCode"] = expo_mundo["cmdCode"].astype(str).str.strip().str.zfill(6)
    expo_mundo["fobvalue"] = pd.to_numeric(expo_mundo["fobvalue"], errors="coerce").fillna(0)

    impo_mundo = pd.read_parquet(DATA_DIR / "impo_pais_mundo.parquet")
    impo_mundo["cmdCode"] = impo_mundo["cmdCode"].astype(str).str.strip().str.zfill(6)
    impo_mundo["cifvalue"] = pd.to_numeric(impo_mundo["cifvalue"], errors="coerce").fillna(0)

    paisindec = pd.read_parquet(DATA_DIR / "paisindec.parquet")
    paisindec["codindec"] = paisindec["codindec"].astype(str)

    pais_codindec = {
        "Australia": ["501","507"], "Brunei": ["346"], "Canadá": ["204"],
        "Chile": ["208"], "Japón": ["320"], "Malasia": ["326"],
        "México": ["218"], "Nueva Zelanda": ["504"], "Perú": ["222"],
        "Reino Unido": ["426"], "Singapur": ["333"], "Vietnam": ["337"],
        "Emiratos Árabes Unidos": ["448"], "Indonesia": ["316"],
        "Camboya": ["306"], "Filipinas": ["312"], "Laos": ["324"],
        "Myanmar": ["304"], "Tailandia": ["335"],
        "India": ["315"], "Korea del Sur": ["309"],
    }

    return ncm_df, camaras_df, claves_df, expo_arg, impo_arg, expo_mundo, impo_mundo, paisindec, pais_codindec

try:
    ncm_df, camaras_df, claves_df, expo_arg, impo_arg, expo_mundo, impo_mundo, paisindec, PAIS_CODINDEC = cargar_datos()
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def fmt_usd(val):
    if val >= 1_000_000_000: return f"USD {val/1_000_000_000:.2f} MM"
    if val >= 1_000_000:     return f"USD {val/1_000_000:.1f} M"
    if val >= 1_000:         return f"USD {val/1_000:.1f} K"
    return f"USD {val:,.0f}"

# ─── SESSION STATE ────────────────────────────────────────────────────────────
def init():
    for k, v in {
        "seccion": None,
        "autenticado": False,
        "user_id": None,
        "user_email": "",
        "nombre_empresa": "",
        "camaras_sel": [],        # cámaras que eligió la empresa
        "camara_actual": None,    # cámara activa (primera o seleccionada)
        "paso": 1,
        "nombre": "", "cargo": "", "email": "",
        "ncm_sel": [],
        "matriz_interes": {},
        "paises_sel": [],
        "pais_otro": "",
        "negs_sel": {},
        "neg_otro": "",
        "supabase_id": None,
        "comentario": "",
        "guardado": False,
        "barreras": {},
        "ac_paso": 1,
        "ac_ncm_sel": [],
        "ac_sel": [],
        "ac_matriz": {},
        "ac_otro": "",
        "ac_guardado": False,
        "ac_id": None,
        "contacto_ok": False,
        "camaras_ok": False,      # ya eligió sus cámaras
        "auth_modo": "login",     # "login" o "registro"
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem;">
      <h2 style="color:#90caf9; font-size:1.3rem; margin:0;">🇦🇷 UIA</h2>
      <p style="color:#7a9acc; font-size:0.85rem; margin:0;">Comercio Exterior</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.autenticado and st.session_state.contacto_ok:
        st.markdown('<p style="color:#90caf9; font-size:0.8rem; font-weight:700; margin:0.3rem 0 0.3rem 0.2rem; text-transform:uppercase; letter-spacing:0.05em;">Completá información</p>', unsafe_allow_html=True)
        for op in ["📋 Interés comercial", "🤝 Acuerdos comerciales"]:
            if st.button(op, use_container_width=True, key=f"menu_{op}",
                         type="primary" if st.session_state.seccion == op else "secondary"):
                st.session_state.seccion = op
                st.rerun()
        st.markdown('<p style="color:#90caf9; font-size:0.8rem; font-weight:700; margin:0.8rem 0 0.3rem 0.2rem; text-transform:uppercase; letter-spacing:0.05em;">Consultá información</p>', unsafe_allow_html=True)
        for op in ["🔍 Consulta de comercio exterior y aranceles", "📊 Indicadores macroeconómicos"]:
            if st.button(op, use_container_width=True, key=f"menu_{op}",
                         type="primary" if st.session_state.seccion == op else "secondary"):
                st.session_state.seccion = op
                st.rerun()
    else:
        st.markdown('<p style="color:#7a9acc; font-size:0.9rem;">Iniciá sesión para acceder a las secciones.</p>', unsafe_allow_html=True)

    if st.session_state.autenticado:
        st.markdown("---")
        st.markdown(f'<div style="font-size:0.85rem; color:#90caf9;">🏢 {st.session_state.nombre_empresa}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.8rem; color:#7a9acc;">{st.session_state.user_email}</div>', unsafe_allow_html=True)
        if st.button("Cerrar sesión", use_container_width=True):
            try:
                get_supabase().auth.sign_out()
            except Exception:
                pass
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────
_logo_path = Path(__file__).parent / "LogoBlanco.jpg"
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
st.image(str(_logo_path), width=140)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#7a9acc; margin-top:0.2rem;">Departamento de Comercio y Negociaciones Internacionales</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BARRERA GLOBAL: LOGIN / REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.autenticado:
    modo = st.session_state.auth_modo
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("Ingresar", use_container_width=True,
                     type="primary" if modo == "login" else "secondary"):
            st.session_state.auth_modo = "login"; st.rerun()
    with col_t2:
        if st.button("Registrarme", use_container_width=True,
                     type="primary" if modo == "registro" else "secondary"):
            st.session_state.auth_modo = "registro"; st.rerun()

    st.markdown("")

    if modo == "login":
        st.subheader("Ingresá con tu cuenta")
        email_in  = st.text_input("Email", placeholder="empresa@mail.com", key="li_email")
        clave_in  = st.text_input("Contraseña", type="password", key="li_clave")
        st.markdown("")
        if st.button("Ingresar →", type="primary", use_container_width=True):
            if not email_in or not clave_in:
                st.error("Completá email y contraseña.")
            else:
                try:
                    sb   = get_supabase()
                    resp = sb.auth.sign_in_with_password({"email": email_in, "password": clave_in})
                    uid  = resp.user.id
                    # Cargar datos guardados
                    contacto = sb.table("empresa_contacto").select("*").eq("id", uid).execute().data
                    camaras  = sb.table("empresa_camaras").select("camara").eq("id", uid).execute().data
                    for k in list(st.session_state.keys()): del st.session_state[k]
                    init()
                    st.session_state.autenticado   = True
                    st.session_state.user_id       = uid
                    st.session_state.user_email    = email_in
                    if contacto:
                        c = contacto[0]
                        st.session_state.nombre_empresa = c.get("nombre_empresa", "")
                        st.session_state.nombre         = c.get("nombre", "")
                        st.session_state.cargo          = c.get("cargo", "")
                        st.session_state.email          = c.get("email", "")
                        st.session_state.contacto_ok    = True
                    # Cargar acuerdos guardados
                    acuerdos_prev = sb.table("empresa_acuerdos").select("*").eq("id_empresa", uid).execute().data
                    if acuerdos_prev:
                        ac_matriz = {}
                        ac_sel_set = set()
                        for r in acuerdos_prev:
                            acuerdo = r["acuerdo"]
                            ncm     = r["ncm"]
                            ac_sel_set.add(acuerdo)
                            if acuerdo not in ac_matriz:
                                ac_matriz[acuerdo] = {}
                            try:
                                niveles = json.loads(r["nivel"]) if r["nivel"] else {}
                            except Exception:
                                niveles = {"exportador": r["nivel"], "importadora": "—"}
                            ac_matriz[acuerdo][ncm] = niveles
                        st.session_state.ac_matriz    = ac_matriz
                        st.session_state.ac_sel       = [n for n in NEGOCIACIONES if n in ac_sel_set]
                        st.session_state.ac_ncm_sel   = list({ncm for d in ac_matriz.values() for ncm in d})
                        st.session_state.ac_guardado  = True
                        # Barreras: tomar del primer registro
                        try:
                            st.session_state.barreras = json.loads(acuerdos_prev[0].get("barreras") or "{}")
                        except Exception:
                            pass
                    # Cargar NCMs y matriz de países guardados
                    paises_prev = sb.table("empresa_paises").select("*").eq("id_empresa", uid).execute().data
                    if paises_prev:
                        ncms_guardados = list({r["ncm"] for r in paises_prev})
                        st.session_state.ncm_sel = ncms_guardados
                        matriz = {}
                        for r in paises_prev:
                            key = str((r["ncm"], r["pais"]))
                            matriz[key] = {"exporta": r["exporta"], "importa": r["importa"], "conoce": r["conoce"]}
                        st.session_state.matriz_interes = matriz
                        paises_unicos = list({r["pais"] for r in paises_prev})
                        st.session_state.paises_sel = paises_unicos
                        st.session_state.guardado = True
                    if camaras:
                        cams = [r["camara"] for r in camaras]
                        st.session_state.camaras_sel  = cams
                        st.session_state.camara_actual = cams[0]
                        st.session_state.camaras_ok   = True
                        ncms_prev = set(st.session_state.ncm_sel)
                        for cod in camaras_df[camaras_df["NbreCamara"].isin(cams)]["PartidaNCM"].tolist():
                            st.session_state[f"ck_{cod}"] = cod in ncms_prev
                    st.rerun()
                except Exception as e:
                    st.error(f"Email o contraseña incorrectos.")
        st.markdown("")
        st.caption("¿Olvidaste tu contraseña? Escribinos a uia@uia.org.ar")

    else:
        st.subheader("Crear cuenta nueva")
        nombre_emp = st.text_input("Nombre de la empresa *", placeholder="Ej: Industrias García S.A.", key="rg_empresa")
        email_rg   = st.text_input("Email *", placeholder="empresa@mail.com", key="rg_email")
        col1, col2 = st.columns(2)
        with col1:
            clave_rg  = st.text_input("Contraseña *", type="password", key="rg_clave")
        with col2:
            clave_rg2 = st.text_input("Repetir contraseña *", type="password", key="rg_clave2")
        st.markdown("")
        if st.button("Registrarme →", type="primary", use_container_width=True):
            if not nombre_emp or not email_rg or not clave_rg:
                st.error("Completá todos los campos obligatorios.")
            elif clave_rg != clave_rg2:
                st.error("Las contraseñas no coinciden.")
            elif len(clave_rg) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                try:
                    sb   = get_supabase()
                    resp = sb.auth.sign_up({"email": email_rg, "password": clave_rg})
                    uid  = resp.user.id
                    sb.table("empresa_contacto").insert({
                        "id": uid, "nombre_empresa": nombre_emp.strip(),
                        "nombre": "", "cargo": "", "email": email_rg.strip()
                    }).execute()
                    for k in list(st.session_state.keys()): del st.session_state[k]
                    init()
                    st.session_state.autenticado    = True
                    st.session_state.user_id        = uid
                    st.session_state.user_email     = email_rg
                    st.session_state.nombre_empresa = nombre_emp.strip()
                    st.session_state.email          = email_rg
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo registrar. Es posible que ese email ya tenga cuenta.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# PANTALLA: SELECCIÓN DE CÁMARAS (solo la primera vez)
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.autenticado and not st.session_state.camaras_ok:
    st.subheader(f"Bienvenido/a, {st.session_state.nombre_empresa}")
    st.caption("Seleccioná las cámaras a las que pertenece tu empresa.")
    lista_camaras = sorted(claves_df["NbreCamara"].tolist())
    camaras_elegidas = st.multiselect("Cámaras", options=lista_camaras,
                                      default=st.session_state.camaras_sel,
                                      placeholder="Elegí una o más cámaras")
    st.markdown("")
    if st.button("Continuar →", type="primary", use_container_width=True):
        if not camaras_elegidas:
            st.error("Seleccioná al menos una cámara.")
        else:
            sb  = get_supabase()
            uid = st.session_state.user_id
            sb.table("empresa_camaras").delete().eq("id", uid).execute()
            sb.table("empresa_camaras").insert([{"id": uid, "camara": c} for c in camaras_elegidas]).execute()
            st.session_state.camaras_sel   = camaras_elegidas
            st.session_state.camara_actual = camaras_elegidas[0]
            st.session_state.camaras_ok    = True
            ncms = camaras_df[camaras_df["NbreCamara"].isin(camaras_elegidas)]["PartidaNCM"].tolist()
            ncms_prev = set(st.session_state.ncm_sel)
            for cod in ncms:
                st.session_state[f"ck_{cod}"] = cod in ncms_prev
            st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# PANTALLA DE CONTACTO (solo la primera vez, post-cámaras)
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.autenticado and st.session_state.camaras_ok and not st.session_state.contacto_ok:
    st.subheader("Datos del responsable")
    st.caption("Completá los datos de quien completa el formulario.")
    col1, col2 = st.columns(2)
    with col1:
        nombre_c = st.text_input("Nombre y apellido *", value=st.session_state.nombre, placeholder="Ej: Juan García")
        cargo_c  = st.text_input("Cargo", value=st.session_state.cargo, placeholder="Ej: Gerente de Comercio Exterior")
    with col2:
        email_c  = st.text_input("Email de contacto *", value=st.session_state.email, placeholder="Ej: jgarcia@empresa.com")
    st.markdown("")
    if st.button("Continuar →", type="primary", use_container_width=True):
        if not nombre_c.strip() or not email_c.strip():
            st.error("Nombre y email son obligatorios.")
        else:
            sb  = get_supabase()
            uid = st.session_state.user_id
            sb.table("empresa_contacto").upsert({
                "id": uid,
                "nombre_empresa": st.session_state.nombre_empresa,
                "nombre": nombre_c.strip(),
                "cargo":  cargo_c.strip(),
                "email":  email_c.strip(),
            }).execute()
            st.session_state.nombre      = nombre_c.strip()
            st.session_state.cargo       = cargo_c.strip()
            st.session_state.email       = email_c.strip()
            st.session_state.contacto_ok = True
            st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# PANTALLA DE BIENVENIDA (post-contacto, sin sección elegida)
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.autenticado and st.session_state.contacto_ok and st.session_state.seccion is None:
    st.markdown(f"### Bienvenido/a, {st.session_state.nombre}")
    st.markdown(f'<p style="color:#7a9acc;">Empresa: <strong>{st.session_state.nombre_empresa}</strong></p>', unsafe_allow_html=True)
    st.markdown("Seleccioná una sección del menú lateral para comenzar.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN ENCUESTA
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.seccion == "📋 Interés comercial":

    paso = st.session_state.paso

    if st.session_state.autenticado:
        html = '<div class="prog-bar">'
        for i, label in enumerate(PASOS, 1):
            if i < paso:    cls, txt = "prog-done", f"✓ {label}"
            elif i == paso: cls, txt = "prog-now",  f"● {label}"
            else:           cls, txt = "prog-todo", label
            html += f'<div class="prog-step {cls}">{txt}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    # ── PASOS ─────────────────────────────────────────────────────────────────
    camara = st.session_state.camara_actual
    ncms_camara_todos = camaras_df[camaras_df["NbreCamara"] == camara]["PartidaNCM"].tolist()

    # Si la cámara no tiene NCMs asignadas, saltar directamente a países
    if not ncms_camara_todos and paso == 1:
        st.info(f"La cámara **{camara}** no tiene subpartidas arancelarias asignadas. Podés continuar directamente a la selección de países.")
        if st.button("Continuar →", type="primary"):
            st.session_state.paso = 2; st.rerun()

    # ── PASO 1 — SUBPARTIDAS NCM ──────────────────────────────────────────
    elif paso == 1:
        st.markdown("""
        <div style="background:#1565c0; border-radius:50px; padding:0.7rem 1.5rem; text-align:center; margin-bottom:1rem;">
          <span style="color:#ffffff; font-size:0.95rem;">⚠️ Antes de completar el formulario, realizá la <strong>Consulta de Comercio Exterior y Aranceles</strong> e <strong>Indicadores Macroeconómicos</strong>.</span>
        </div>
        """, unsafe_allow_html=True)
        st.subheader("Subpartidas arancelarias (NCM)")
        st.caption(f"Cámara: **{camara}** | {len(ncms_camara_todos)} subpartidas asignadas — marcá las que son de tu interés.")

        ncm_set_camara = set(ncms_camara_todos)
        ncm_info = (
            ncm_df[ncm_df["HSUSA"].isin(ncm_set_camara)]
            [["HSUSA","Subsector","Descripcion Partida"]]
            .drop_duplicates("HSUSA")
        )
        sin_info = ncm_set_camara - set(ncm_info["HSUSA"])
        if sin_info:
            extra = pd.DataFrame({"HSUSA": list(sin_info), "Subsector": "Sin clasificar", "Descripcion Partida": ""})
            ncm_info = pd.concat([ncm_info, extra], ignore_index=True)
        ncm_info = ncm_info.sort_values("HSUSA")

        col_a, col_b, _ = st.columns([1,1,4])
        with col_a:
            if st.button("✅ Marcar todas"):
                st.session_state.ncm_sel = ncms_camara_todos
                for cod in ncms_camara_todos: st.session_state[f"ck_{cod}"] = True
                st.rerun()
        with col_b:
            if st.button("☐ Desmarcar todas"):
                st.session_state.ncm_sel = []
                for cod in ncms_camara_todos: st.session_state[f"ck_{cod}"] = False
                st.rerun()

        ncm_marcados = set(st.session_state.ncm_sel)

        # ── Buscador ──────────────────────────────────────────────────────
        busqueda = st.text_input("🔍 Buscar por NCM o descripción", placeholder="Ej: 4704 o 'papel'", key="ncm_busqueda")
        term = busqueda.strip().lower()

        if term:
            ncm_filtrado = ncm_info[
                ncm_info["HSUSA"].str.lower().str.contains(term) |
                ncm_info["Descripcion Partida"].str.lower().str.contains(term)
            ]
            if ncm_filtrado.empty:
                st.info("Sin resultados para esa búsqueda.")
            else:
                st.caption(f"{len(ncm_filtrado)} resultado(s) encontrado(s):")
                for _, row in ncm_filtrado.iterrows():
                    cod  = row["HSUSA"]
                    desc = row["Descripcion Partida"]
                    label = f"`{cod}` — {desc}" if desc else f"`{cod}`"
                    val = st.session_state.get(f"ck_{cod}", cod in ncm_marcados)
                    checked = st.checkbox(label, value=val, key=f"ck_{cod}")
                    if checked: ncm_marcados.add(cod)
                    else:       ncm_marcados.discard(cod)
        else:
            subsectores = sorted(ncm_info["Subsector"].dropna().unique())
            for sub in subsectores:
                sub_df = ncm_info[ncm_info["Subsector"] == sub]
                ncms_sub = sub_df["HSUSA"].tolist()
                marcados_sub = sum(1 for n in ncms_sub if n in ncm_marcados)
                with st.expander(f"📂 {sub}  —  {marcados_sub}/{len(ncms_sub)} seleccionadas", expanded=False):
                    for _, row in sub_df.iterrows():
                        cod  = row["HSUSA"]
                        desc = row["Descripcion Partida"]
                        label = f"`{cod}` — {desc}" if desc else f"`{cod}`"
                        val = st.session_state.get(f"ck_{cod}", cod in ncm_marcados)
                        checked = st.checkbox(label, value=val, key=f"ck_{cod}")
                        if checked: ncm_marcados.add(cod)
                        else:       ncm_marcados.discard(cod)

        st.session_state.ncm_sel = list(ncm_marcados)
        st.markdown(f'<div class="card"><strong style="color:#90caf9">{len(st.session_state.ncm_sel)}</strong> subpartidas seleccionadas — esta selección refleja interés comercial y no impacta en el seguimiento de acuerdos o negociaciones.</div>', unsafe_allow_html=True)

        if st.button("Continuar →", type="primary", use_container_width=True):
            if not st.session_state.ncm_sel:
                st.error("Seleccioná al menos una subpartida NCM.")
            else:
                st.session_state.paso = 2; st.rerun()

    # ── PASO 2 — PAÍSES E INTERÉS COMERCIAL ──────────────────────────────
    elif paso == 2:
        st.subheader("Países e interés comercial")
        st.caption("Seleccioná los países de interés e indicá tu relación comercial con cada uno.")

        st.markdown("#### ¿Con qué países tiene o quisiera tener vínculos comerciales?")

        paises_sel = set(st.session_state.paises_sel)
        cols = st.columns(4)
        for i, pais in enumerate(TODOS_PAISES):
            with cols[i % 4]:
                if st.checkbox(pais, value=pais in paises_sel, key=f"pais_{pais}"):
                    paises_sel.add(pais)
                else:
                    paises_sel.discard(pais)

        # Otro país
        st.markdown("")
        otro_check = st.checkbox("Otro país", value=bool(st.session_state.pais_otro), key="pais_otro_check")
        pais_otro = ""
        if otro_check:
            pais_otro = st.text_input("¿Cuál?", value=st.session_state.pais_otro,
                                      placeholder="Ingresá el nombre del país",
                                      help="A la brevedad se incorporarán datos de comercio para este destino.")
            if pais_otro:
                st.info("📌 Registraremos tu interés. A la brevedad se incorporarán datos de ese mercado.")

        paises_lista = list(paises_sel)

        # ── Tabla de interés comercial por NCM × País ─────────────────────
        if paises_lista:
            st.markdown("---")
            st.markdown("#### Interés comercial por subpartida y país")
            st.caption("Indicá para cada combinación si exportás, importás y si conocés el mercado. Podés tildar más de una opción.")

            ncm_sel_set = set(st.session_state.ncm_sel)
            matriz = dict(st.session_state.matriz_interes)

            ncm_info_sel = (
                ncm_df[ncm_df["HSUSA"].isin(ncm_sel_set)]
                [["HSUSA","Descripcion Partida"]]
                .drop_duplicates("HSUSA")
                .sort_values("HSUSA")
            )

            for pais in sorted(paises_lista):
                st.markdown(f"**🌍 {pais}**")
                header_cols = st.columns([3, 1, 1, 1])
                header_cols[0].markdown('<span style="color:#90caf9; font-size:0.85rem;">Subpartida</span>', unsafe_allow_html=True)
                header_cols[1].markdown('<span style="color:#90caf9; font-size:0.85rem;">Exporta</span>', unsafe_allow_html=True)
                header_cols[2].markdown('<span style="color:#90caf9; font-size:0.85rem;">Importa</span>', unsafe_allow_html=True)
                header_cols[3].markdown('<span style="color:#90caf9; font-size:0.85rem;">Conoce el mercado</span>', unsafe_allow_html=True)

                for _, row in ncm_info_sel.iterrows():
                    ncm = row["HSUSA"]
                    desc = row["Descripcion Partida"]
                    label_ncm = f"`{ncm}` {desc[:45]}" if desc else f"`{ncm}`"
                    key = (ncm, pais)
                    prev = matriz.get(str(key), {"exporta": False, "importa": False, "conoce": False})

                    r = st.columns([3, 1, 1, 1])
                    r[0].markdown(f'<span style="font-size:0.85rem;">{label_ncm}</span>', unsafe_allow_html=True)
                    exp_v = r[1].checkbox("", value=prev.get("exporta", False), key=f"exp_{ncm}_{pais}", label_visibility="collapsed")
                    imp_v = r[2].checkbox("", value=prev.get("importa", False), key=f"imp_{ncm}_{pais}", label_visibility="collapsed")
                    con_v = r[3].checkbox("", value=prev.get("conoce",  False), key=f"con_{ncm}_{pais}", label_visibility="collapsed")
                    matriz[str(key)] = {"exporta": exp_v, "importa": imp_v, "conoce": con_v}

                st.markdown("")

            st.session_state.matriz_interes = matriz

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Volver", use_container_width=True): st.session_state.paso = 1; st.rerun()
        with col2:
            if st.button("Continuar →", type="primary", use_container_width=True):
                if not paises_lista:
                    st.error("Seleccioná al menos un país.")
                else:
                    st.session_state.paises_sel = paises_lista
                    st.session_state.pais_otro  = pais_otro
                    st.session_state.paso = 4; st.rerun()

    # paso 3 movido al menú Acuerdos comerciales
    elif paso == 3:
        st.session_state.paso = 5; st.rerun()

    # ── PASO 5 — BARRERAS AL COMERCIO ────────────────────────────────────
    elif paso == 5:
        st.subheader("Paso 5 — Barreras al comercio (opcional)")
        st.caption("Esta sección relevará información sobre obstáculos regulatorios y otras disciplinas comerciales.")

        b = st.session_state.barreras

        # ── REGLAS DE ORIGEN ──
        st.markdown("#### 📋 Reglas de Origen")
        origen_info = st.text_area(
            "Información relevante sobre Reglas de Origen (NCMs, acuerdos, requisitos, etc.)",
            value=b.get("origen_info", ""), height=80,
            placeholder="Ingresá comentarios sobre reglas de origen aplicables a tus productos...",
            key="b_origen_info"
        )
        origen_reos_mercosur = st.radio(
            "¿Pueden adoptarse los mismos Requisitos Específicos de Origen (REOs) negociados en Mercosur (ACE-18)?",
            options=["—", "Sí", "No"], index=["—","Sí","No"].index(b.get("origen_reos_mercosur","—")),
            horizontal=True, key="b_origen_mercosur"
        )
        origen_reos_ue = st.radio(
            "¿Pueden adoptarse los mismos REOs negociados en el acuerdo Mercosur-Unión Europea?",
            options=["—", "Sí", "No"], index=["—","Sí","No"].index(b.get("origen_reos_ue","—")),
            horizontal=True, key="b_origen_ue"
        )

        st.markdown("---")

        # ── TBT ──
        st.markdown("#### 🔧 Barreras Técnicas al Comercio (TBT)")
        TBT_OBSTACULOS = [
            "Falta de transparencia en requisitos técnicos o procedimientos de evaluación de la conformidad",
            "Dificultades de participación en el proceso de elaboración de reglamentos",
            "Reglamentos técnicos divergentes de normas internacionales relevantes (ISO/IEC, etc.)",
            "Requisitos técnicos excesivamente restrictivos o prescriptivos",
            "No reconocimiento de equivalencia de reglamentos técnicos",
            "Duplicidad de ensayos, inspecciones o certificaciones",
            "Procedimientos de evaluación de la conformidad más onerosos de lo necesario",
            "Demoras o incertidumbre en procesos de registro/aprobación (plazos indeterminados)",
            "No reconocimiento de resultados de procedimientos de evaluación de la conformidad",
            "Exigencias impuestas por agentes privados (importadores, distribuidores, retail)",
        ]
        tbt_tiene = st.radio(
            "¿Identificás cuestiones regulatorias en TBT que impacten negativamente la negociación?",
            options=["—", "Sí", "No"], index=["—","Sí","No"].index(b.get("tbt_tiene","—")),
            horizontal=True, key="b_tbt_tiene"
        )
        tbt_obstaculos = []
        tbt_otro = ""
        tbt_caso = ""
        if tbt_tiene == "Sí":
            st.markdown("**Tipos de divergencias/obstáculos identificados** (marcá todos los que apliquen):")
            prev_obs = b.get("tbt_obstaculos", [])
            for i, obs in enumerate(TBT_OBSTACULOS):
                if st.checkbox(obs, value=obs in prev_obs, key=f"tbt_{i}"):
                    tbt_obstaculos.append(obs)
            tbt_otro = st.text_input("Otros (especificá)", value=b.get("tbt_otro",""), key="b_tbt_otro")
            tbt_caso = st.text_area(
                "Describí un caso concreto (sector, producto con NCM, normativa específica, estimación de impacto):",
                value=b.get("tbt_caso",""), height=100, key="b_tbt_caso"
            )

        st.markdown("---")

        # ── SPS ──
        st.markdown("#### 🌱 Medidas Sanitarias y Fitosanitarias (SPS)")
        SPS_OBSTACULOS = [
            "Falta de transparencia en requisitos sanitarios/fitosanitarios o procedimientos de certificación/inspección",
            "Dificultades de participación en el proceso de elaboración de medidas SPS",
            "Divergencia con normas internacionales relevantes (Codex, WOAH, IPPC)",
            "No reconocimiento de regionalización/zonas libres o de compartimentación",
            "No reconocimiento de equivalencia de medidas o sistemas oficiales",
            "Exigencias de certificación/inspección duplicadas",
            "Exigencias de certificación/inspección más onerosas de lo necesario",
            "Metodologías de muestreo/ensayo sin base científica adecuada",
            "Demoras o incertidumbre en procesos de autorización/aprobación (plazos indeterminados)",
            "No aceptación de certificados electrónicos cuando están disponibles",
            "Exigencias impuestas por agentes privados (importadores, distribuidores, retail)",
        ]
        sps_tiene = st.radio(
            "¿Identificás medidas SPS que impacten negativamente la negociación?",
            options=["—", "Sí", "No"], index=["—","Sí","No"].index(b.get("sps_tiene","—")),
            horizontal=True, key="b_sps_tiene"
        )
        sps_obstaculos = []
        sps_otro = ""
        sps_caso = ""
        if sps_tiene == "Sí":
            st.markdown("**Tipos de medidas/obstáculos SPS** (marcá todos los que apliquen):")
            prev_sps = b.get("sps_obstaculos", [])
            for i, obs in enumerate(SPS_OBSTACULOS):
                if st.checkbox(obs, value=obs in prev_sps, key=f"sps_{i}"):
                    sps_obstaculos.append(obs)
            sps_otro = st.text_input("Otros (especificá)", value=b.get("sps_otro",""), key="b_sps_otro")
            sps_caso = st.text_area(
                "Describí un caso concreto (sector, producto con NCM, normativa específica, estimación de impacto):",
                value=b.get("sps_caso",""), height=100, key="b_sps_caso"
            )

        st.markdown("---")

        # ── OTRAS DISCIPLINAS ──
        st.markdown("#### 📌 Otras Disciplinas Comerciales")
        DISCIPLINAS = [
            "Comercio de Servicios",
            "Inversiones",
            "Propiedad Intelectual",
            "Compras Gubernamentales",
            "Defensa Comercial",
            "Salvaguardas bilaterales",
            "Facilitación de Comercio y Cooperación Aduanera",
            "Buenas Prácticas Regulatorias",
            "Defensa de la Competencia",
            "Solución de Controversias",
            "Micro y Pequeñas Empresas",
            "Comercio y Desarrollo Sostenible",
        ]
        st.markdown("¿Identificás disciplinas comerciales relevantes para la negociación? (marcá todas las que apliquen):")
        prev_disc = b.get("disciplinas", [])
        disciplinas_sel = []
        for i, disc in enumerate(DISCIPLINAS):
            if st.checkbox(disc, value=disc in prev_disc, key=f"disc_{i}"):
                disciplinas_sel.append(disc)
        disciplinas_comentario = st.text_area(
            "Si marcaste alguna disciplina, describí el interés ofensivo o la preocupación defensiva:",
            value=b.get("disciplinas_comentario",""), height=100, key="b_disc_comentario"
        )

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Volver", use_container_width=True):
                st.session_state.paso = 2; st.rerun()
        with col2:
            if st.button("Ver resumen →", type="primary", use_container_width=True):
                st.session_state.barreras = {
                    "origen_info":             origen_info,
                    "origen_reos_mercosur":    origen_reos_mercosur,
                    "origen_reos_ue":          origen_reos_ue,
                    "tbt_tiene":               tbt_tiene,
                    "tbt_obstaculos":          tbt_obstaculos,
                    "tbt_otro":                tbt_otro,
                    "tbt_caso":                tbt_caso,
                    "sps_tiene":               sps_tiene,
                    "sps_obstaculos":          sps_obstaculos,
                    "sps_otro":                sps_otro,
                    "sps_caso":                sps_caso,
                    "disciplinas":             disciplinas_sel,
                    "disciplinas_comentario":  disciplinas_comentario,
                }
                st.session_state.paso = 4; st.rerun()

    # ── PASO 4 — RESUMEN ──────────────────────────────────────────────────
    elif paso == 4:
        st.subheader("Resumen")
        st.markdown('<div class="disclaimer">ℹ️ Los datos de comercio son estimados en base a información de INDEC y fuentes oficiales de los países. La selección de subpartidas refleja interés comercial y no implica posición sobre acuerdos o negociaciones.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cargo_h = f'<p><strong style="color:#90caf9">Cargo:</strong> {st.session_state.cargo}</p>' if st.session_state.cargo else ""
            email_h = f'<p><strong style="color:#90caf9">Email:</strong> {st.session_state.email}</p>' if st.session_state.email else ""
            st.markdown(f"""<div class="card">
              <p><strong style="color:#90caf9">Cámara:</strong> {camara}</p>
              <p><strong style="color:#90caf9">Nombre:</strong> {st.session_state.nombre}</p>
              {cargo_h}{email_h}
              <p><strong style="color:#90caf9">Subpartidas NCM seleccionadas:</strong> {len(st.session_state.ncm_sel)}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            paises_txt = ", ".join(sorted(st.session_state.paises_sel))
            if st.session_state.pais_otro:
                paises_txt += f", {st.session_state.pais_otro} (a incorporar)"
            com_h = f'<p><strong style="color:#90caf9">Comentario:</strong><br>{st.session_state.comentario}</p>' if st.session_state.comentario else ""
            st.markdown(f"""<div class="card">
              <p><strong style="color:#90caf9">Países de interés:</strong><br>{paises_txt or "Ninguno"}</p>
              {com_h}
            </div>""", unsafe_allow_html=True)

        # ── Detalle por subpartida NCM con datos de comercio ──────────────
        st.markdown("#### Ver detalle por subpartida NCM con datos de comercio")

        ncm_sel_set = set(st.session_state.ncm_sel)
        paises_elegidos = [p for p in st.session_state.paises_sel if p in NOMBRE_MUNDO or p in PAIS_CODINDEC]
        matriz = st.session_state.matriz_interes

        if not paises_elegidos:
            st.info("No hay países con datos de comercio disponibles para mostrar.")
        else:
            for pais in sorted(paises_elegidos):
                with st.expander(f"🌍 {pais}", expanded=True):
                    codigos = PAIS_CODINDEC.get(pais, [])
                    nombre_m = NOMBRE_MUNDO.get(pais)
                    filas = []
                    for ncm in sorted(ncm_sel_set):
                        key = str((ncm, pais))
                        interes = matriz.get(key, {})
                        expo_v = "✓" if interes.get("exporta") else ""
                        impo_v = "✓" if interes.get("importa") else ""
                        con_v  = "✓" if interes.get("conoce")  else ""

                        desc = ncm_df[ncm_df["HSUSA"] == ncm]["Descripcion Partida"].values
                        desc = desc[0][:55] if len(desc) > 0 else ""

                        expo_a = expo_arg[(expo_arg["ncm6"] == ncm) & (expo_arg["pais"].isin(codigos))]["fob"].sum() / 1000
                        impo_a = impo_arg[(impo_arg["ncm6"] == ncm) & (impo_arg["pais"].isin(codigos))]["cif"].sum() / 1000

                        if nombre_m:
                            expo_p = expo_mundo[(expo_mundo["cmdCode"] == ncm) & (expo_mundo["pais"] == nombre_m)]["fobvalue"].sum()
                            impo_p = impo_mundo[(impo_mundo["cmdCode"] == ncm) & (impo_mundo["pais"] == nombre_m)]["cifvalue"].sum()
                        else:
                            expo_p = impo_p = 0

                        filas.append({
                            "NCM": ncm,
                            "Descripción": desc,
                            "Exporta": expo_v,
                            "Importa": impo_v,
                            "Conoce mercado": con_v,
                            f"Arg → {pais} (Miles de USD)": round(expo_a, 1),
                            f"Arg ← {pais} (Miles de USD)": round(impo_a, 1),
                            f"{pais} → Mundo (Miles de USD)": round(expo_p, 1),
                            f"{pais} ← Mundo (Miles de USD)": round(impo_p, 1),
                        })

                    if filas:
                        df_res = pd.DataFrame(filas)
                        st.dataframe(df_res, use_container_width=True, hide_index=True, height=350)
                    else:
                        st.info("Sin datos para las subpartidas seleccionadas.")

        st.markdown("---")
        if st.session_state.guardado:
            st.success("✅ Respuesta guardada correctamente. ¡Muchas gracias!")
            col1, col2, _ = st.columns([1, 1, 1])
            with col1:
                if st.button("✏️ Modificar respuesta", use_container_width=True):
                    st.session_state.guardado = False
                    st.session_state.paso = 1
                    st.rerun()
            with col2:
                if st.button("➕ Nueva posición", use_container_width=True):
                    # Mantiene camara y usuario, limpia datos de encuesta
                    st.session_state.supabase_id    = None
                    st.session_state.ncm_sel        = []
                    st.session_state.paises_sel     = []
                    st.session_state.pais_otro      = ""
                    st.session_state.matriz_interes = {}
                    st.session_state.negs_sel       = {}
                    st.session_state.neg_otro       = ""
                    st.session_state.comentario     = ""
                    st.session_state.barreras       = {}
                    st.session_state.guardado       = False
                    st.session_state.paso           = 1
                    ncms_camara = camaras_df[camaras_df["NbreCamara"] == camara]["PartidaNCM"].tolist()
                    st.session_state.ncm_sel = []
                    for cod in ncms_camara:
                        st.session_state[f"ck_{cod}"] = False
                    st.rerun()
        else:
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("← Volver", use_container_width=True): st.session_state.paso = 2; st.rerun()
            with col3:
                if st.button("✅ Guardar", type="primary", use_container_width=True):
                    try:
                        sb  = get_supabase()
                        uid = st.session_state.user_id
                        # Borrar y reinsertar países de interés
                        sb.table("empresa_paises").delete().eq("id_empresa", uid).execute()
                        matriz = st.session_state.matriz_interes
                        import ast
                        rows_paises = []
                        for key, flags in matriz.items():
                            if not isinstance(flags, dict): continue
                            try:    ncm, pais = ast.literal_eval(key)
                            except: continue
                            rows_paises.append({
                                "id_empresa": uid, "pais": pais, "ncm": str(ncm)[:6],
                                "exporta": bool(flags.get("exporta")),
                                "importa": bool(flags.get("importa")),
                                "conoce":  bool(flags.get("conoce")),
                            })
                        if rows_paises:
                            sb.table("empresa_paises").insert(rows_paises).execute()
                        # Actualizar contacto con comentario
                        sb.table("empresa_contacto").update({
                            "nombre_empresa": st.session_state.nombre_empresa,
                            "nombre": st.session_state.nombre,
                            "cargo":  st.session_state.cargo,
                            "email":  st.session_state.email,
                        }).eq("id", uid).execute()
                        st.session_state.guardado = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ No se pudo guardar la respuesta: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN ACUERDOS COMERCIALES
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.seccion == "🤝 Acuerdos comerciales":
    if not st.session_state.autenticado:
        st.warning("Iniciá sesión para acceder.")
        st.stop()

    camara = st.session_state.camara_actual
    ncms_camara_df = camaras_df[camaras_df["NbreCamara"] == camara]
    ncms_camara_todos = ncms_camara_df["PartidaNCM"].tolist()

    ac_paso = st.session_state.ac_paso
    NIVELES_AC = ["—", "Alto", "Medio", "Bajo"]

    st.markdown('<hr>', unsafe_allow_html=True)

    pasos_labels = ["1. Partidas NCM", "2. Acuerdos", "3. Intereses por partida", "4. Barreras"]
    cols_p = st.columns(4)
    for i, lbl in enumerate(pasos_labels):
        color = "#1565c0" if ac_paso == i+1 else "#1a3a6b"
        cols_p[i].markdown(f'<div style="background:{color};border-radius:8px;padding:0.4rem;text-align:center;font-size:0.85rem;">{lbl}</div>', unsafe_allow_html=True)
    st.markdown("")

    # ── AC PASO 1 — SELECCIÓN NCM ──────────────────────────────────────────────
    if ac_paso == 1:
        st.subheader("Paso 1 — Seleccioná las partidas NCM de interés")
        ncm_info = ncm_df.copy()
        ncm_info["ncm6"] = ncm_info.iloc[:,0].astype(str).str.zfill(6)
        ncm_map = ncm_info.set_index("ncm6").iloc[:,3].to_dict() if ncm_info.shape[1] > 3 else {}

        ca, cb = st.columns(2)
        if ca.button("✅ Marcar todas", use_container_width=True):
            for cod in ncms_camara_todos:
                st.session_state[f"ac_ck_{cod}"] = True
            st.rerun()
        if cb.button("☐ Desmarcar todas", use_container_width=True):
            for cod in ncms_camara_todos:
                st.session_state[f"ac_ck_{cod}"] = False
            st.rerun()

        ac_ncm_nuevo = []
        subsectores = ncms_camara_df.merge(ncm_df, left_on="PartidaNCM", right_on=ncm_df.columns[0], how="left")
        col_sub = subsectores.columns[subsectores.columns.str.contains("ubsector", case=False)].tolist()
        col_desc = subsectores.columns[subsectores.columns.str.contains("escr", case=False)].tolist()
        subsector_col = col_sub[0] if col_sub else None
        desc_col = col_desc[0] if col_desc else None

        if subsector_col:
            grupos = subsectores.groupby(subsector_col)
            for sub, grp in grupos:
                with st.expander(str(sub)):
                    for _, row in grp.iterrows():
                        cod = str(row["PartidaNCM"])
                        desc = str(row[desc_col]) if desc_col else cod
                        val = st.session_state.get(f"ac_ck_{cod}", cod in st.session_state.ac_ncm_sel)
                        if st.checkbox(f"{cod} — {desc}", value=val, key=f"ac_ck_{cod}"):
                            ac_ncm_nuevo.append(cod)
        else:
            for cod in ncms_camara_todos:
                val = st.session_state.get(f"ac_ck_{cod}", cod in st.session_state.ac_ncm_sel)
                if st.checkbox(cod, value=val, key=f"ac_ck_{cod}"):
                    ac_ncm_nuevo.append(cod)

        st.markdown(f"**{len(ac_ncm_nuevo)} partidas seleccionadas**")
        if st.button("Continuar →", type="primary", use_container_width=True):
            if not ac_ncm_nuevo:
                st.error("Seleccioná al menos una partida NCM.")
            else:
                st.session_state.ac_ncm_sel = ac_ncm_nuevo
                st.session_state.ac_paso = 2; st.rerun()

    # ── AC PASO 2 — SELECCIÓN ACUERDOS ────────────────────────────────────────
    elif ac_paso == 2:
        st.subheader("Paso 2 — Seleccioná los acuerdos de interés")
        ac_sel_nuevo = []
        for neg in NEGOCIACIONES:
            status = NEGOCIACIONES_STATUS.get(neg, "")
            label  = f"**Mercosur-{neg}**"
            col_a, col_b = st.columns([1, 3])
            with col_a:
                if st.checkbox(f"Mercosur-{neg}", value=neg in st.session_state.ac_sel, key=f"ac_neg_{neg}"):
                    ac_sel_nuevo.append(neg)
            with col_b:
                st.markdown(f'<span style="color:#7a9acc; font-size:0.85rem;">{status}</span>', unsafe_allow_html=True)
        ac_otro = st.text_input("Otro acuerdo (opcional)", value=st.session_state.ac_otro, key="ac_otro_input")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Volver", use_container_width=True):
                st.session_state.ac_paso = 1; st.rerun()
        with col2:
            if st.button("Continuar →", type="primary", use_container_width=True):
                if not ac_sel_nuevo and not ac_otro:
                    st.error("Seleccioná al menos un acuerdo.")
                else:
                    st.session_state.ac_sel  = ac_sel_nuevo
                    st.session_state.ac_otro = ac_otro
                    st.session_state.ac_paso = 3; st.rerun()

    # ── AC PASO 3 — MATRIZ ACUERDO × NCM ──────────────────────────────────────
    elif ac_paso == 3:
        st.subheader("Paso 3 — Interés por partida y acuerdo")
        st.caption("Para cada acuerdo seleccionado, indicá el nivel de interés exportador y sensibilidad importadora por partida NCM.")

        ncm_info = ncm_df.copy()
        ncm_info["ncm6"] = ncm_info.iloc[:,0].astype(str).str.zfill(6)
        col_desc = [c for c in ncm_info.columns if "escr" in c.lower()]
        desc_col_name = col_desc[0] if col_desc else None
        ncm_desc_map = ncm_info.set_index("ncm6")[desc_col_name].to_dict() if desc_col_name else {}

        ac_lista = st.session_state.ac_sel + ([st.session_state.ac_otro] if st.session_state.ac_otro else [])
        matriz_ac = dict(st.session_state.ac_matriz)

        for acuerdo in ac_lista:
            with st.expander(f"📄 {acuerdo}", expanded=True):
                h0, h1, h2 = st.columns([4, 1.5, 1.5])
                h0.markdown('<span style="color:#90caf9; font-size:0.85rem;">Partida NCM</span>', unsafe_allow_html=True)
                h1.markdown('<span style="color:#90caf9; font-size:0.85rem;">Interés exportador</span>', unsafe_allow_html=True)
                h2.markdown('<span style="color:#90caf9; font-size:0.85rem;">Sensibilidad importadora</span>', unsafe_allow_html=True)

                if acuerdo not in matriz_ac:
                    matriz_ac[acuerdo] = {}

                for ncm in st.session_state.ac_ncm_sel:
                    ncm6 = str(ncm)[:6].zfill(6)
                    desc = ncm_desc_map.get(ncm6, ncm6)
                    label_ncm = f"{ncm6} — {desc[:50]}" if len(desc) > 50 else f"{ncm6} — {desc}"
                    prev = matriz_ac[acuerdo].get(ncm6, {})
                    r0, r1, r2 = st.columns([4, 1.5, 1.5])
                    r0.markdown(f'<span style="font-size:0.85rem;">{label_ncm}</span>', unsafe_allow_html=True)
                    exp_idx = NIVELES_AC.index(prev.get("exportador","—")) if prev.get("exportador") in NIVELES_AC else 0
                    imp_idx = NIVELES_AC.index(prev.get("importadora","—")) if prev.get("importadora") in NIVELES_AC else 0
                    exp_v = r1.selectbox("", options=NIVELES_AC, index=exp_idx, key=f"ac_exp_{acuerdo}_{ncm6}", label_visibility="collapsed")
                    imp_v = r2.selectbox("", options=NIVELES_AC, index=imp_idx, key=f"ac_imp_{acuerdo}_{ncm6}", label_visibility="collapsed")
                    matriz_ac[acuerdo][ncm6] = {"exportador": exp_v, "importadora": imp_v}

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Volver", use_container_width=True):
                st.session_state.ac_matriz = matriz_ac
                st.session_state.ac_paso = 2; st.rerun()
        with col2:
            if st.button("Siguiente →", type="primary", use_container_width=True):
                st.session_state.ac_matriz = matriz_ac
                st.session_state.ac_paso = 4; st.rerun()

    # ── AC PASO 4 — BARRERAS AL COMERCIO ──────────────────────────────────────
    elif ac_paso == 4:
        st.subheader("Paso 4 — Barreras al comercio (opcional)")
        st.caption("Esta sección relevará información sobre obstáculos regulatorios y otras disciplinas comerciales.")

        b = st.session_state.barreras

        st.markdown("#### 📋 Reglas de Origen")
        origen_info = st.text_area("Información relevante sobre Reglas de Origen", value=b.get("origen_info",""), height=80, key="ac_b_origen_info")
        origen_reos_mercosur = st.radio("¿Pueden adoptarse los mismos REOs negociados en Mercosur (ACE-18)?", options=["—","Sí","No"], index=["—","Sí","No"].index(b.get("origen_reos_mercosur","—")), horizontal=True, key="ac_b_origen_mercosur")
        origen_reos_ue = st.radio("¿Pueden adoptarse los mismos REOs negociados en el acuerdo Mercosur-Unión Europea?", options=["—","Sí","No"], index=["—","Sí","No"].index(b.get("origen_reos_ue","—")), horizontal=True, key="ac_b_origen_ue")

        st.markdown("---")
        st.markdown("#### 🔧 Barreras Técnicas al Comercio (TBT)")
        TBT_OBS = ["Falta de transparencia en requisitos técnicos o procedimientos de evaluación de la conformidad","Dificultades de participación en el proceso de elaboración de reglamentos","Reglamentos técnicos divergentes de normas internacionales relevantes (ISO/IEC, etc.)","Requisitos técnicos excesivamente restrictivos o prescriptivos","No reconocimiento de equivalencia de reglamentos técnicos","Duplicidad de ensayos, inspecciones o certificaciones","Procedimientos de evaluación de la conformidad más onerosos de lo necesario","Demoras o incertidumbre en procesos de registro/aprobación (plazos indeterminados)","No reconocimiento de resultados de procedimientos de evaluación de la conformidad","Exigencias impuestas por agentes privados (importadores, distribuidores, retail)"]
        tbt_tiene = st.radio("¿Identificás cuestiones regulatorias en TBT que impacten negativamente la negociación?", options=["—","Sí","No"], index=["—","Sí","No"].index(b.get("tbt_tiene","—")), horizontal=True, key="ac_b_tbt_tiene")
        tbt_obstaculos, tbt_otro, tbt_caso = [], "", ""
        if tbt_tiene == "Sí":
            st.markdown("**Tipos de obstáculos** (marcá todos los que apliquen):")
            prev_obs = b.get("tbt_obstaculos",[])
            for i, obs in enumerate(TBT_OBS):
                if st.checkbox(obs, value=obs in prev_obs, key=f"ac_tbt_{i}"): tbt_obstaculos.append(obs)
            tbt_otro = st.text_input("Otros (especificá)", value=b.get("tbt_otro",""), key="ac_b_tbt_otro")
            tbt_caso = st.text_area("Caso concreto (sector, NCM, normativa, impacto estimado):", value=b.get("tbt_caso",""), height=90, key="ac_b_tbt_caso")

        st.markdown("---")
        st.markdown("#### 🌱 Medidas Sanitarias y Fitosanitarias (SPS)")
        SPS_OBS = ["Falta de transparencia en requisitos sanitarios/fitosanitarios o procedimientos de certificación/inspección","Dificultades de participación en el proceso de elaboración de medidas SPS","Divergencia con normas internacionales relevantes (Codex, WOAH, IPPC)","No reconocimiento de regionalización/zonas libres o de compartimentación","No reconocimiento de equivalencia de medidas o sistemas oficiales","Exigencias de certificación/inspección duplicadas","Exigencias de certificación/inspección más onerosas de lo necesario","Metodologías de muestreo/ensayo sin base científica adecuada","Demoras o incertidumbre en procesos de autorización/aprobación (plazos indeterminados)","No aceptación de certificados electrónicos cuando están disponibles","Exigencias impuestas por agentes privados (importadores, distribuidores, retail)"]
        sps_tiene = st.radio("¿Identificás medidas SPS que impacten negativamente la negociación?", options=["—","Sí","No"], index=["—","Sí","No"].index(b.get("sps_tiene","—")), horizontal=True, key="ac_b_sps_tiene")
        sps_obstaculos, sps_otro, sps_caso = [], "", ""
        if sps_tiene == "Sí":
            st.markdown("**Tipos de obstáculos SPS** (marcá todos los que apliquen):")
            prev_sps = b.get("sps_obstaculos",[])
            for i, obs in enumerate(SPS_OBS):
                if st.checkbox(obs, value=obs in prev_sps, key=f"ac_sps_{i}"): sps_obstaculos.append(obs)
            sps_otro = st.text_input("Otros (especificá)", value=b.get("sps_otro",""), key="ac_b_sps_otro")
            sps_caso = st.text_area("Caso concreto (sector, NCM, normativa, impacto estimado):", value=b.get("sps_caso",""), height=90, key="ac_b_sps_caso")

        st.markdown("---")
        st.markdown("#### 📌 Otras Disciplinas Comerciales")
        DISC = ["Comercio de Servicios","Inversiones","Propiedad Intelectual","Compras Gubernamentales","Defensa Comercial","Salvaguardas bilaterales","Facilitación de Comercio y Cooperación Aduanera","Buenas Prácticas Regulatorias","Defensa de la Competencia","Solución de Controversias","Micro y Pequeñas Empresas","Comercio y Desarrollo Sostenible"]
        prev_disc = b.get("disciplinas",[])
        disciplinas_sel = []
        for i, disc in enumerate(DISC):
            if st.checkbox(disc, value=disc in prev_disc, key=f"ac_disc_{i}"): disciplinas_sel.append(disc)
        disciplinas_comentario = st.text_area("Describí el interés ofensivo o preocupación defensiva:", value=b.get("disciplinas_comentario",""), height=90, key="ac_b_disc_com")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Volver", use_container_width=True):
                st.session_state.ac_paso = 3; st.rerun()
        with col2:
            if st.button("✅ Guardar", type="primary", use_container_width=True):
                st.session_state.barreras = {
                    "origen_info": origen_info, "origen_reos_mercosur": origen_reos_mercosur,
                    "origen_reos_ue": origen_reos_ue, "tbt_tiene": tbt_tiene,
                    "tbt_obstaculos": tbt_obstaculos, "tbt_otro": tbt_otro, "tbt_caso": tbt_caso,
                    "sps_tiene": sps_tiene, "sps_obstaculos": sps_obstaculos,
                    "sps_otro": sps_otro, "sps_caso": sps_caso,
                    "disciplinas": disciplinas_sel, "disciplinas_comentario": disciplinas_comentario,
                }
                try:
                    sb  = get_supabase()
                    uid = st.session_state.user_id
                    sb.table("empresa_acuerdos").delete().eq("id_empresa", uid).execute()
                    rows_ac = []
                    barreras_json = json.dumps(st.session_state.barreras)
                    for acuerdo, ncm_dict in st.session_state.ac_matriz.items():
                        if not isinstance(ncm_dict, dict):
                            continue
                        for ncm, niveles in ncm_dict.items():
                            rows_ac.append({
                                "id_empresa": uid,
                                "ncm":        str(ncm)[:6],
                                "acuerdo":    str(acuerdo),
                                "nivel":      json.dumps(niveles) if isinstance(niveles, dict) else str(niveles),
                                "barreras":   barreras_json,
                            })
                    if rows_ac:
                        sb.table("empresa_acuerdos").insert(rows_ac).execute()
                    st.session_state.ac_guardado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ No se pudo guardar: {e}")

    if st.session_state.ac_guardado and ac_paso == 4:
        st.success("✅ Información guardada correctamente.")
        if st.button("➕ Nueva carga de acuerdos", use_container_width=True):
            st.session_state.ac_ncm_sel = []
            st.session_state.ac_sel     = []
            st.session_state.ac_matriz  = {}
            st.session_state.ac_otro    = ""
            st.session_state.ac_guardado = False
            st.session_state.ac_id      = None
            st.session_state.ac_paso    = 1
            for cod in ncms_camara_todos:
                st.session_state.pop(f"ac_ck_{cod}", None)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN INDICADORES MACROECONÓMICOS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.seccion == "📊 Indicadores macroeconómicos":
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("### Indicadores macroeconómicos por país")
    st.caption("Seleccioná un país para ver su ficha de indicadores.")

    FICHAS = {f.stem: f for f in sorted(FICHAS_DIR.glob("*.pdf"))}
    pais_ficha = st.selectbox(
        "País", options=["— Seleccioná un país —"] + list(FICHAS.keys()), key="ficha_pais"
    )

    if pais_ficha != "— Seleccioná un país —":
        pdf_path = FICHAS[pais_ficha]
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label=f"⬇️ Descargar ficha {pais_ficha} (PDF)",
            data=pdf_bytes,
            file_name=f"Indicadores_{pais_ficha}.pdf",
            mime="application/pdf",
        )

        try:
            import fitz
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for i, page in enumerate(doc):
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                st.image(img_bytes, use_container_width=True)
            doc.close()
        except Exception as e:
            st.warning(f"No se pudo mostrar el PDF: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN CONSULTA DE COMERCIO
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.seccion == "🔍 Consulta de comercio exterior y aranceles":
    st.markdown('<hr>', unsafe_allow_html=True)

    pais_elegido = st.selectbox("País contraparte", options=["— Elegí un país —"] + sorted(TODOS_PAISES), key="consulta_pais")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sector_c = st.selectbox("Sector (opcional)", options=["— Todos los sectores —"] + sorted(ncm_df["Sector"].dropna().unique().tolist()), key="consulta_sector")
    with col_s2:
        subsectores_disp = ["— Todos los subsectores —"]
        if sector_c != "— Todos los sectores —":
            subsectores_disp += sorted(ncm_df[ncm_df["Sector"] == sector_c]["Subsector"].dropna().unique().tolist())
        subsector_c = st.selectbox("Subsector (opcional)", options=subsectores_disp, key="consulta_subsector")

    if sector_c != "— Todos los sectores —" and subsector_c != "— Todos los subsectores —":
        ncm_set = set(ncm_df[(ncm_df["Sector"] == sector_c) & (ncm_df["Subsector"] == subsector_c)]["HSUSA"].dropna())
    elif sector_c != "— Todos los sectores —":
        ncm_set = set(ncm_df[ncm_df["Sector"] == sector_c]["HSUSA"].dropna())
    else:
        ncm_set = set(ncm_df["HSUSA"].dropna())

    st.markdown("---")

    if pais_elegido == "— Elegí un país —":
        st.info("👆 Seleccioná un país para ver los datos de comercio.")
    else:
        codigos_pais  = PAIS_CODINDEC.get(pais_elegido, [])
        nombre_mundo  = NOMBRE_MUNDO.get(pais_elegido, pais_elegido)

        expo_fil = expo_arg[expo_arg["pais"].isin(codigos_pais) & expo_arg["ncm6"].isin(ncm_set)].copy()
        impo_fil = impo_arg[impo_arg["pais"].isin(codigos_pais) & impo_arg["ncm6"].isin(ncm_set)].copy()
        total_expo_arg = expo_fil["fob"].sum() / 1_000_000      # USD → millones USD
        total_impo_arg = impo_fil["cif"].sum() / 1_000_000      # USD → millones USD

        expo_pais_fil = expo_mundo[(expo_mundo["pais"] == nombre_mundo) & expo_mundo["cmdCode"].isin(ncm_set)]
        impo_pais_fil = impo_mundo[(impo_mundo["pais"] == nombre_mundo) & impo_mundo["cmdCode"].isin(ncm_set)]
        total_expo_pais = expo_pais_fil["fobvalue"].sum()
        total_impo_pais = impo_pais_fil["cifvalue"].sum()
        period_pais = expo_pais_fil["period"].iloc[0] if len(expo_pais_fil) else "N/D"

        def fmt_mill(val):
            return f"{val:,.1f} M USD"

        sector_label = subsector_c if subsector_c != "— Todos los subsectores —" \
                       else sector_c if sector_c != "— Todos los sectores —" else "todos los sectores"
        st.markdown(f"### Argentina ↔ {pais_elegido}")
        st.caption(f"Filtro: **{sector_label}** | **{len(ncm_set):,}** subpartidas NCM | Año Argentina: 2025 | Año {pais_elegido}: {period_pais} | Valores en millones de USD")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"🇦🇷 Arg exporta → {pais_elegido}", fmt_mill(total_expo_arg))
        m2.metric(f"🇦🇷 Arg importa ← {pais_elegido}", fmt_mill(total_impo_arg))
        m3.metric(f"🌍 {pais_elegido} exporta → Mundo", fmt_mill(total_expo_pais))
        m4.metric(f"🌍 {pais_elegido} importa ← Mundo", fmt_mill(total_impo_pais))

        labels = [
            f"🇦🇷 Arg exporta → {pais_elegido}",
            f"🇦🇷 Arg importa ← {pais_elegido}",
            f"🌍 {pais_elegido} exporta → Mundo",
            f"🌍 {pais_elegido} importa ← Mundo",
        ]
        valores = [total_expo_arg, total_impo_arg, total_expo_pais, total_impo_pais]
        colores = ["#2e7d32", "#1565c0", "#66bb6a", "#42a5f5"]

        fig = go.Figure(go.Bar(
            x=labels, y=valores, marker_color=colores,
            text=[fmt_mill(v) for v in valores],
            textposition="outside", textfont=dict(color="white", size=13),
        ))
        fig.update_layout(
            paper_bgcolor="#0d2040", plot_bgcolor="#0d2040", font=dict(color="white"),
            yaxis=dict(title="Millones de USD", gridcolor="#1a3a6b", color="white"),
            xaxis=dict(color="white", tickfont=dict(size=11)),
            showlegend=False, height=430, margin=dict(t=60, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        def tabla_detalle(df_in, col_ncm, col_valor, label_val, es_arg=True):
            if df_in.empty:
                st.info("Sin datos para esta selección.")
                return
            df2 = df_in.copy()
            ncm_join = "ncm6" if es_arg else col_ncm
            df2 = df2.merge(ncm_df[["HSUSA","Subsector","Descripcion Partida"]].drop_duplicates("HSUSA"),
                            left_on=ncm_join, right_on="HSUSA", how="left")
            df2 = df2.rename(columns={col_ncm: "NCM", "Descripcion Partida": "Descripción", col_valor: label_val})
            df2 = df2.groupby(["NCM","Descripción","Subsector"], as_index=False)[label_val].sum()
            df2 = df2.sort_values(label_val, ascending=False)
            total = df2[label_val].sum()
            df2["% del total"] = (df2[label_val] / total * 100).round(1).astype(str) + "%"
            if es_arg: df2[label_val] = (df2[label_val] / 1_000_000).round(2).apply(lambda x: f"{x:,.2f}")
            else:      df2[label_val] = df2[label_val].round(2).apply(lambda x: f"{x:,.2f}")
            st.dataframe(df2[["NCM","Descripción","Subsector",label_val,"% del total"]],
                         use_container_width=True, hide_index=True, height=350)

        t1, t2, t3, t4 = st.tabs([
            f"🇦🇷 Arg exporta → {pais_elegido}",
            f"🇦🇷 Arg importa ← {pais_elegido}",
            f"🌍 {pais_elegido} exporta → Mundo",
            f"🌍 {pais_elegido} importa ← Mundo",
        ])
        with t1: tabla_detalle(expo_fil,      "partidaNCM", "fob",      "FOB (M USD)", es_arg=True)
        with t2: tabla_detalle(impo_fil,      "partidaNCM", "cif",      "CIF (M USD)", es_arg=True)
        with t3: tabla_detalle(expo_pais_fil, "cmdCode",    "fobvalue", "FOB (M USD)", es_arg=False)
        with t4: tabla_detalle(impo_pais_fil, "cmdCode",    "cifvalue", "CIF (M USD)", es_arg=False)

        link = LINKS_ARANCELES.get(pais_elegido)
        if link:
            st.markdown("---")
            st.markdown(f'<p style="color:#ffffff !important;">Para ver aranceles: <a href="{link}" target="_blank" style="color:#90caf9 !important; text-decoration:underline !important;">{link}</a></p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#7a9acc !important; font-size:0.82rem;">Fuente: Elaboración propia de la UIA en base a datos INDEC, COMTRADE y WITS. Para las exportaciones argentinas, a causa del secreto estadístico, se utilizaron datos de INDEC y estimaciones estadísticas propias.</p>', unsafe_allow_html=True)
