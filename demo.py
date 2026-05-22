import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

# Configuración de la página
st.set_page_config(page_title="DRAGO DEMO - Gestión de Barco", page_icon="⛵", layout="centered")

# --- SISTEMA DE MENSAJES FLOTANTES ---
if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"]["texto"], icon=st.session_state["toast_msg"]["icono"])
    del st.session_state["toast_msg"]

# --- CONEXIÓN A GOOGLE SHEETS (COPIA DEMO) ---
@st.cache_resource
def conectar_google():
    credenciales = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(credenciales)
    # Busca la hoja de pruebas genérica
    return gc.open("datos_barco_demo")

try:
    sh = conectar_google()
    wks = sh.worksheet("config")
except Exception as e:
    st.error(f"Error conectando a la hoja de cálculo DEMO: {e}")
    st.markdown("⚠️ **Recuerda:** Tienes que crear una copia de tu Google Sheets, llamarla `datos_barco_demo` y compartirla con el correo de tu cuenta de servicio como 'Editor'.")
    st.stop()

def cargar_datos_nube():
    try:
        datos_str = wks.acell("A1").value
        if datos_str:
            return json.loads(datos_str)
    except Exception:
        pass
    with open("datos_barco.json", "r", encoding="utf-8") as f:
        datos_base = json.load(f)
    wks.update_acell("A1", json.dumps(datos_base, ensure_ascii=False))
    return datos_base

def guardar_datos_nube(datos):
    wks.update_acell("A1", json.dumps(datos, ensure_ascii=False))

datos = cargar_datos_nube()

# Forzar nombres genéricos en la estructura interna de la DEMO
datos["socios"] = ["Socio 1", "Socio 2", "Socio 3"]

if "finanzas_gastos" not in datos: datos["finanzas_gastos"] = []
if "finanzas_ingresos" not in datos: datos["finanzas_ingresos"] = []

# --- CONTROL DE ACCESO ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ DRAGO - Control de Acceso (DEMO)")
    st.markdown("---")
    st.subheader("👤 Identificación de Tripulación")
    
    usuario_seleccionado = st.selectbox("Selecciona qué socio va a acceder a la app:", datos["socios"])
    
    if st.button("🚀 Entrar a la Aplicación", use_container_width=True):
        st.session_state["usuario_actual"] = usuario_seleccionado
        st.session_state["toast_msg"] = {"texto": f"¡Bienvenido a bordo, {usuario_seleccionado}!", "icono": "⛵"}
        st.rerun()

else:
    usuario_actual = st.session_state["usuario_actual"]
    
    # --- BARRA LATERAL ---
    st.sidebar.title("⚓ DRAGO DEMO")
    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar de Socio"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ DRAGO - Gestión de Navegación")
    
    hoy = date.today()
    horas_actuales = int(datos["horas_motor"])
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Mandos", "📋 Bricos", "📝 Checks", "📜 Hist", "💶 Cuentas", "⚙️ Panel"])
    
    with tab1:
        st.header("⏱️ Estado del Motor")
        st.metric(label="Horas Actuales", value=f"{horas_actuales} hrs")
        
        st.header("🔧 Mantenimientos Críticos")
        for i, maint in enumerate(datos["mantenimientos_mixtos"]):
            horas_desde_ultimo = horas_actuales - maint["ultima_vez_horas"]
            horas_restantes = maint["intervalo_horas"] - horas_desde_ultimo
            
            if "proxima_fecha" in maint:
                fecha_vencimiento = datetime.strptime(maint["proxima_fecha"], "%Y-%m-%d").date()
            else:
                fecha_ultima = datetime.strptime(maint["ultima_vez_fecha"], "%Y-%m-%d").date()
                fecha_vencimiento = fecha_ultima + timedelta(days=maint["intervalo_meses"] * 30)
            
            dias_restantes = (fecha_vencimiento - hoy).days
            vence = (horas_restantes <= 0) or (dias_restantes <= 0)
            pro
