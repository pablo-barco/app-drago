import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

st.set_page_config(page_title="EL DRAGO - Gestión de Barco", page_icon="⛵", layout="centered")

if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"]["texto"], icon=st.session_state["toast_msg"]["icono"])
    del st.session_state["toast_msg"]

def conectar_google():
    credenciales = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(credenciales)
    return gc.open("datos_barco")

try:
    sh = conectar_google()
    wks = sh.worksheet("config")
except Exception as e:
    st.error(f"Error conectando a la hoja de cálculo de El Drago: {e}")
    st.stop()

def cargar_datos_nube():
    try:
        datos_str = wks.acell("A1").value
        if datos_str and datos_str.strip().startswith("{"):
            return json.loads(datos_str)
    except Exception:
        pass
    
    # ESTRUCTURA DE EMERGENCIA SI LA HOJA DE GOOGLE ESTÁ VACÍA
    datos_base = {
        "socios": ["PABLO DÍEZ", "DAVID NAVARRO", "JUSTO HUERTAS", "CARLOS NAVARRO", "RUBEN MESEGUER"],
        "horas_motor": 0,
        "mantenimientos_mixtos": [],
        "caducidades_puras": [],
        "tareas": [],
        "checklist_salida": [],
        "checklist_entrada": [],
        "finanzas_gastos": [],
        "finanzas_ingresos": [],
        "historial": [{"fecha": date.today().strftime("%Y-%m-%d"), "usuario": "Sistema", "evento": "Inicialización de base de datos", "horas": 0}]
    }
    wks.update_acell("A1", json.dumps(datos_base, ensure_ascii=False))
    return datos_base

def guardar_datos_nube(datos):
    wks.update_acell("A1", json.dumps(datos, ensure_ascii=False))

datos = cargar_datos_nube()

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ EL DRAGO - Control de Acceso")
    st.markdown("---")
    st.subheader("👤 Identificación de Tripulación")
    usuario_seleccionado = st.selectbox("Selecciona tu nombre para acceder:", datos["socios"])
    if st.button("🚀 Entrar a la Aplicación", use_container_width=True):
        st.session_state["usuario_actual"] = usuario_seleccionado
        st.session_state["toast_msg"] = {"texto": f"¡Bienvenido a bordo, {usuario_seleccionado}!", "icono": "⛵"}
        st.rerun()
else:
    usuario_actual = st.session_state["usuario_actual"]
    st.sidebar.title("⚓ EL DRAGO")
    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    
    st.title("⚓ EL DRAGO - Gestión de Navegación")
    hoy = date.today()
    horas_actuales = int(datos.get("horas_motor", 0))
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Mandos", "📋 Bricos", "📝 Checks", "📜 Hist", "💶 Cuentas", "⚙️ Panel"
    ])
    
    with tab1:
        st.header("⏱️ Estado del Motor")
        st.metric(label="Horas Actuales", value=f"{horas_actuales} hrs")
        
    with tab2:
        st.header("📋 Tareas de Bricolaje")
        st.info("Usa el panel de configuración para añadir tareas.")
        
    with tab3:
        st.header("📝 Listas de Seguridad")
        st.write("Listas listas para configurar.")
        
    with tab4:
        st.header("📜 Historial de Operaciones")
        for registro in reversed(datos.get("historial", [])):
            st.markdown(f"**[{registro.get('fecha')}]** - *{registro.get('usuario')}*: **{registro.get('evento')}**")
            
    with tab5:
        st.header("💶 Estado de Cuentas")
        st.metric("💰 Dinero actual en el Bote Común", "0.00 €")
        
    with tab6:
        st.header("⚙️ Panel de Control")
        horas_input = st.number_input("Actualizar horas de motor:", min_value=0, value=horas_actuales)
        if st.button("Guardar Horas"):
            datos["horas_motor"] = horas_input
            guardar_datos_nube(datos)
            st.rerun()
