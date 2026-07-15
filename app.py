import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import json

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DATA_DIR  = Path(__file__).parent / "data_parquet"
FICHAS_DIR = Path(__file__).parent / "fichas"
OUT_FILE  = Path(__file__).parent / "respuestas.csv"

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
[data-baseweb="menu"], [data-baseweb="menu"] ul, [data-baseweb="menu"] li {
    background-color: #1a3a6b !important; color: #ffffff !important;
}
[data-baseweb="menu"] li:hover { background-color: #1565c0 !important; }
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
PAISES_EXTRA = ["Emiratos Árabes Unidos", "Indonesia", "Japón"]
TODOS_PAISES = PAISES_CPTPP + ["Emiratos Árabes Unidos", "Indonesia"]

NEGOCIACIONES = [
    "Unión Europea", "Estados Unidos", "EFTA", "India",
    "Canadá", "Egipto", "Israel", "Vietnam", "Indonesia",
    "Emiratos Árabes Unidos", "Japón",
]

NOMBRE_MUNDO = {
    "Australia": "Australia", "Brunei": "Brunei", "Canadá": "Canada",
    "Chile": "Chile", "Japón": "Japon", "Malasia": "Malasia",
    "México": "Mexico", "Nueva Zelanda": "Nueva Zelanda", "Perú": "Peru",
    "Reino Unido": "Reino Unido", "Singapur": "Singapur", "Vietnam": "Vietnam",
}

PASOS = ["Subpartidas NCM", "Países e interés comercial", "Acuerdos y negociaciones", "Resumen"]

# ─── CARGA DE DATOS ───────────────────────────────────────────────────────────
@st.cache_data
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
        "seccion": "📋 Interés comercial",
        "autenticado": False,
        "camara_actual": None,
        "paso": 1,
        "nombre": "", "cargo": "", "email": "",
        "ncm_sel": [],
        "matriz_interes": {},   # {(ncm, pais): {"exporta": bool, "importa": bool, "conoce": bool}}
        "paises_sel": [],
        "pais_otro": "",
        "negs_sel": [],
        "neg_otro": "",
        "comentario": "",
        "guardado": False,
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

    opciones = ["📋 Interés comercial", "🔍 Consulta de comercio exterior", "📊 Indicadores macroeconómicos"]
    idx = opciones.index(st.session_state.seccion) if st.session_state.seccion in opciones else 0
    seccion = st.radio("", options=opciones, index=idx, label_visibility="collapsed")
    st.session_state.seccion = seccion

    if st.session_state.autenticado:
        st.markdown("---")
        st.markdown(f'<div style="font-size:0.85rem; color:#90caf9;">🏢 {st.session_state.camara_actual}</div>', unsafe_allow_html=True)
        if st.button("Cerrar sesión", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-bottom:1rem;">
  <h1>🇦🇷 UIA — Intereses de Internacionalización Comercial para Socios</h1>
  <p style="color:#7a9acc;">Departamento de Comercio y Negociaciones Internacionales</p>
</div>
""", unsafe_allow_html=True)

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

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    if not st.session_state.autenticado:
        st.subheader("Acceso")
        st.caption("Seleccioná tu cámara e ingresá la clave para continuar.")

        lista_camaras = sorted(claves_df["NbreCamara"].tolist())
        col1, col2 = st.columns(2)
        with col1:
            camara_sel = st.selectbox("Cámara", options=["— Seleccioná tu cámara —"] + lista_camaras)
        with col2:
            clave_input = st.text_input("Clave de acceso", type="password", placeholder="Ingresá tu clave")

        col_i1, col_i2 = st.columns(2)
        with col_i1:
            nombre_l = st.text_input("Nombre completo *", placeholder="Ej: Juan Pérez")
            cargo_l  = st.text_input("Cargo (opcional)")
        with col_i2:
            email_l  = st.text_input("Email (opcional)")

        st.markdown("")
        if st.button("Ingresar →", type="primary", use_container_width=True):
            if camara_sel == "— Seleccioná tu cámara —":
                st.error("Seleccioná una cámara.")
            elif not clave_input:
                st.error("Ingresá la clave de acceso.")
            elif not nombre_l.strip():
                st.error("Ingresá tu nombre para continuar.")
            else:
                clave_ok = claves_df[claves_df["NbreCamara"] == camara_sel]["Pass"].values
                if len(clave_ok) > 0 and clave_input == clave_ok[0]:
                    st.session_state.autenticado   = True
                    st.session_state.camara_actual = camara_sel
                    st.session_state.nombre        = nombre_l.strip()
                    st.session_state.cargo         = cargo_l.strip()
                    st.session_state.email         = email_l.strip()
                    st.session_state.paso          = 1
                    ncms_camara = camaras_df[camaras_df["NbreCamara"] == camara_sel]["PartidaNCM"].tolist()
                    st.session_state.ncm_sel = ncms_camara
                    for cod in ncms_camara:
                        st.session_state[f"ck_{cod}"] = True
                    st.rerun()
                else:
                    st.error("Clave incorrecta. Verificá e intentá nuevamente.")

    # ── PASOS POST-LOGIN ──────────────────────────────────────────────────────
    else:
        camara = st.session_state.camara_actual
        ncms_camara_todos = camaras_df[camaras_df["NbreCamara"] == camara]["PartidaNCM"].tolist()

        # Si la cámara no tiene NCMs asignadas, saltar directamente a países
        if not ncms_camara_todos and paso == 1:
            st.info(f"La cámara **{camara}** no tiene subpartidas arancelarias asignadas. Podés continuar directamente a la selección de países.")
            if st.button("Continuar →", type="primary"):
                st.session_state.paso = 2; st.rerun()

        # ── PASO 1 — SUBPARTIDAS NCM ──────────────────────────────────────────
        elif paso == 1:
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
                        st.session_state.paso = 3; st.rerun()

        # ── PASO 3 — ACUERDOS Y NEGOCIACIONES ────────────────────────────────
        elif paso == 3:
            st.subheader("Acuerdos y negociaciones")
            st.caption("Seleccioná los acuerdos o negociaciones de interés para tu cámara.")

            st.markdown("#### ¿Le interesa el seguimiento de algún acuerdo o negociación en curso?")
            st.caption("Tu selección queda registrada junto con el resto de la encuesta.")
            negs_sel = set(st.session_state.negs_sel)
            cols = st.columns(4)
            for i, neg in enumerate(NEGOCIACIONES):
                with cols[i % 4]:
                    if st.checkbox(neg, value=neg in negs_sel, key=f"neg_{neg}"):
                        negs_sel.add(neg)
                    else:
                        negs_sel.discard(neg)

            st.markdown("")
            otro_neg_check = st.checkbox("Otro acuerdo / negociación", value=bool(st.session_state.neg_otro), key="neg_otro_check")
            neg_otro = ""
            if otro_neg_check:
                neg_otro = st.text_input("¿Cuál?", value=st.session_state.neg_otro,
                                         placeholder="Ingresá el nombre del acuerdo o negociación")

            st.markdown("---")
            comentario = st.text_area("Comentario adicional (opcional)",
                                      value=st.session_state.comentario, height=90,
                                      placeholder="Oportunidades, sensibilidades u otros comentarios...")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Volver", use_container_width=True): st.session_state.paso = 2; st.rerun()
            with col2:
                if st.button("Ver resumen →", type="primary", use_container_width=True):
                    st.session_state.negs_sel   = list(negs_sel)
                    st.session_state.neg_otro   = neg_otro
                    st.session_state.comentario = comentario
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
                negs_txt = ", ".join(st.session_state.negs_sel) or "Ninguna"
                if st.session_state.neg_otro:
                    negs_txt += f", {st.session_state.neg_otro}"
                com_h = f'<p><strong style="color:#90caf9">Comentario:</strong><br>{st.session_state.comentario}</p>' if st.session_state.comentario else ""
                st.markdown(f"""<div class="card">
                  <p><strong style="color:#90caf9">Países de interés:</strong><br>{paises_txt or "Ninguno"}</p>
                  <p><strong style="color:#90caf9">Acuerdos y negociaciones:</strong><br>{negs_txt}</p>
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
                                f"Arg → {pais} (KUSD)": round(expo_a, 1),
                                f"Arg ← {pais} (KUSD)": round(impo_a, 1),
                                f"{pais} → Mundo (KUSD)": round(expo_p, 1),
                                f"{pais} ← Mundo (KUSD)": round(impo_p, 1),
                            })

                        if filas:
                            df_res = pd.DataFrame(filas)
                            st.dataframe(df_res, use_container_width=True, hide_index=True, height=350)
                        else:
                            st.info("Sin datos para las subpartidas seleccionadas.")

            st.markdown("---")
            if st.session_state.guardado:
                st.success("✅ Encuesta enviada correctamente. ¡Muchas gracias!")
            else:
                col1, col2, col3 = st.columns([1,1,1])
                with col1:
                    if st.button("← Volver", use_container_width=True): st.session_state.paso = 3; st.rerun()
                with col3:
                    if st.button("✅ Fin de consulta", type="primary", use_container_width=True):
                        registro = {
                            "fecha_ingreso":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "camara":             camara,
                            "nombre":             st.session_state.nombre,
                            "cargo":              st.session_state.cargo,
                            "email":              st.session_state.email,
                            "cantidad_ncm":       len(st.session_state.ncm_sel),
                            "ncm_seleccionados":  json.dumps(sorted(st.session_state.ncm_sel)),
                            "paises_interes":     json.dumps(sorted(st.session_state.paises_sel)),
                            "pais_otro":          st.session_state.pais_otro,
                            "matriz_interes":     json.dumps(st.session_state.matriz_interes),
                            "negociaciones":      json.dumps(st.session_state.negs_sel),
                            "neg_otro":           st.session_state.neg_otro,
                            "comentario":         st.session_state.comentario,
                        }
                        df_new = pd.DataFrame([registro])
                        df_out = pd.concat([pd.read_csv(OUT_FILE), df_new], ignore_index=True) if OUT_FILE.exists() else df_new
                        try:
                            df_out.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
                            st.session_state.guardado = True
                            st.rerun()
                        except PermissionError:
                            st.error("❌ No se pudo guardar: el archivo **respuestas.csv** está abierto en Excel. Cerralo y hacé clic en **Enviar** nuevamente.")

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN CONSULTA
# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN INDICADORES MACROECONÓMICOS
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.seccion == "📊 Indicadores macroeconómicos":
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown("### Indicadores macroeconómicos por país")
    st.caption("Seleccioná un país para ver su ficha de indicadores.")

    FICHAS = {f.stem: f for f in sorted(FICHAS_DIR.glob("*.pdf"))}
    pais_ficha = st.selectbox("País", options=["— Seleccioná un país —"] + list(FICHAS.keys()), key="ficha_pais")

    if pais_ficha != "— Seleccioná un país —":
        pdf_path = FICHAS[pais_ficha]
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        import base64
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="800px" style="border:none; border-radius:8px;"></iframe>',
            unsafe_allow_html=True,
        )
        st.download_button(
            label=f"⬇️ Descargar ficha {pais_ficha}",
            data=pdf_bytes,
            file_name=f"Indicadores_{pais_ficha}.pdf",
            mime="application/pdf",
        )

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN CONSULTA DE COMERCIO
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<hr>', unsafe_allow_html=True)

    pais_elegido = st.selectbox("País contraparte", options=["— Elegí un país —"] + PAISES_CPTPP, key="consulta_pais")

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
        codigos_pais  = PAIS_CODINDEC[pais_elegido]
        nombre_mundo  = NOMBRE_MUNDO[pais_elegido]

        expo_fil = expo_arg[expo_arg["pais"].isin(codigos_pais) & expo_arg["ncm6"].isin(ncm_set)].copy()
        impo_fil = impo_arg[impo_arg["pais"].isin(codigos_pais) & impo_arg["ncm6"].isin(ncm_set)].copy()
        total_expo_arg = expo_fil["fob"].sum() / 1000
        total_impo_arg = impo_fil["cif"].sum() / 1000

        expo_pais_fil = expo_mundo[(expo_mundo["pais"] == nombre_mundo) & expo_mundo["cmdCode"].isin(ncm_set)]
        impo_pais_fil = impo_mundo[(impo_mundo["pais"] == nombre_mundo) & impo_mundo["cmdCode"].isin(ncm_set)]
        total_expo_pais = expo_pais_fil["fobvalue"].sum()
        total_impo_pais = impo_pais_fil["cifvalue"].sum()
        period_pais = expo_pais_fil["period"].iloc[0] if len(expo_pais_fil) else "N/D"

        sector_label = subsector_c if subsector_c != "— Todos los subsectores —" \
                       else sector_c if sector_c != "— Todos los sectores —" else "todos los sectores"
        st.markdown(f"### Argentina ↔ {pais_elegido}")
        st.caption(f"Filtro: **{sector_label}** | **{len(ncm_set):,}** subpartidas NCM | Año Argentina: 2025 | Año {pais_elegido}: {period_pais} | Valores en miles de USD")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"🇦🇷 Arg exporta → {pais_elegido}", fmt_usd(total_expo_arg))
        m2.metric(f"🇦🇷 Arg importa ← {pais_elegido}", fmt_usd(total_impo_arg))
        m3.metric(f"🌍 {pais_elegido} exporta → Mundo", fmt_usd(total_expo_pais))
        m4.metric(f"🌍 {pais_elegido} importa ← Mundo", fmt_usd(total_impo_pais))

        labels = [
            f"🇦🇷 Arg exporta → {pais_elegido}",
            f"🌍 {pais_elegido} exporta → Mundo",
            f"🇦🇷 Arg importa ← {pais_elegido}",
            f"🌍 {pais_elegido} importa ← Mundo",
        ]
        valores = [total_expo_arg, total_expo_pais, total_impo_arg, total_impo_pais]
        colores = ["#1565c0", "#42a5f5", "#2e7d32", "#66bb6a"]

        fig = go.Figure(go.Bar(
            x=labels, y=valores, marker_color=colores,
            text=[fmt_usd(v) for v in valores],
            textposition="outside", textfont=dict(color="white", size=13),
        ))
        fig.update_layout(
            paper_bgcolor="#0d2040", plot_bgcolor="#0d2040", font=dict(color="white"),
            yaxis=dict(title="Miles USD", gridcolor="#1a3a6b", color="white"),
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
            if es_arg: df2[label_val] = (df2[label_val] / 1000).round(1).apply(lambda x: f"{x:,.1f}")
            else:      df2[label_val] = df2[label_val].apply(lambda x: f"{x:,.1f}")
            st.dataframe(df2[["NCM","Descripción","Subsector",label_val,"% del total"]],
                         use_container_width=True, hide_index=True, height=350)

        t1, t2, t3, t4 = st.tabs([
            f"🇦🇷 Arg exporta → {pais_elegido}",
            f"🇦🇷 Arg importa ← {pais_elegido}",
            f"🌍 {pais_elegido} exporta → Mundo",
            f"🌍 {pais_elegido} importa ← Mundo",
        ])
        with t1: tabla_detalle(expo_fil,      "partidaNCM", "fob",      "FOB (KUSD)", es_arg=True)
        with t2: tabla_detalle(impo_fil,      "partidaNCM", "cif",      "CIF (KUSD)", es_arg=True)
        with t3: tabla_detalle(expo_pais_fil, "cmdCode",    "fobvalue", "FOB (KUSD)", es_arg=False)
        with t4: tabla_detalle(impo_pais_fil, "cmdCode",    "cifvalue", "CIF (KUSD)", es_arg=False)
