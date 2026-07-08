import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

# Configuración de la página
st.set_page_config(page_title="EL DRAGO - Gestión de Barco", page_icon="⛵", layout="centered")

# --- CONEXIÓN ULTRA-SEGURA A GOOGLE ---
def conectar_google():
    # Recuperamos las credenciales de los Secrets
    credenciales = dict(st.secrets["connections"]["gsheets"])
    
    # Limpieza automática de la clave privada para evitar errores de PEM / InvalidByte
    pk = credenciales["private_key"]
    if "\\n" in pk:
        pk = pk.replace("\\n", "\n")
    # Aseguramos que los saltos de línea sean limpios
    pk = "\n".join([line.strip() for line in pk.split("\n") if line.strip()])
    credenciales["private_key"] = pk
    
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
        if datos_str:
            return json.loads(datos_str)
    except Exception:
        pass
    st.error("No se pudieron cargar los datos de la hoja de cálculo.")
    st.stop()

def guardar_datos_nube(datos):
    wks.update_acell("A1", json.dumps(datos, ensure_ascii=False))

datos = cargar_datos_nube()

# Asegurar que existan todas tus estructuras reales de El Drago
if "mantenimientos_mixtos" not in datos: datos["mantenimientos_mixtos"] = []
if "caducidades_puras" not in datos: datos["caducidades_puras"] = []
if "tareas" not in datos: datos["tareas"] = []
if "historial" not in datos: datos["historial"] = []
if "socios" not in datos: datos["socios"] = ["Socio 1", "Socio 2", "Socio 3", "Socio 4", "Socio 5"]

hoy = date.today()

# --- CONTROL DE ACCESO ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ EL DRAGO - Control de Acceso")
    st.markdown("---")
    st.subheader("👤 Identificación de Tripulación")
    usuario_seleccionado = st.selectbox("Selecciona tu nombre para acceder:", datos["socios"])
    if st.button("🚀 Entrar a la Aplicación", use_container_width=True):
        st.session_state["usuario_actual"] = usuario_seleccionado
        st.rerun()

else:
    usuario_actual = st.session_state["usuario_actual"]
    
    st.sidebar.title("⚓ EL DRAGO")
    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state["usuario_actual"] = None
        st.rerun()
        
    st.title("⚓ EL DRAGO - Panel de Control")
    horas_actuales = int(datos.get("horas_motor", 0))
    
    tab1, tab2, tab3 = st.tabs(["📊 Estado y Motor", "🔧 Bricos / Tareas", "📜 Historial"])
    
    # PESTAÑA 1: MOTOR Y MANTENIMIENTOS REALES
    with tab1:
        st.header("⏱️ Horas de Motor")
        st.metric(label="Horas Actuales", value=f"{horas_actuales} hrs")
        
        with st.expander("📝 Actualizar horas de motor"):
            nuevas_horas = st.number_input("Introduce las nuevas horas:", min_value=horas_actuales, value=horas_actuales)
            if st.button("Guardar Horas"):
                if nuevas_horas > horas_actuales:
                    datos["historial"].append({
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "usuario": usuario_actual,
                        "evento": f"Actualizó el motor de {horas_actuales}h a {nuevas_horas}h",
                        "horas": nuevas_horas
                    })
                    datos["horas_motor"] = nuevas_horas
                    guardar_datos_nube(datos)
                    st.rerun()

        st.markdown("---")
        st.header("🔧 Próximos Mantenimientos")
        
        for i, maint in enumerate(datos["mantenimientos_mixtos"]):
            col_info, col_accion = st.columns([3, 1])
            with col_info:
                horas_desde_ultimo = horas_actuales - maint["ultima_vez_horas"]
                horas_restantes = maint["intervalo_horas"] - horas_desde_ultimo
                st.write(f"**{maint['elemento']}**")
                if horas_restantes <= 0:
                    st.error(f"🔴 VENCIDO (Hace {abs(horas_restantes)} horas)")
                elif horas_restantes <= 15:
                    st.warning(f"🟡 Toca pronto (Quedan {horas_restantes} horas)")
                else:
                    st.success(f"🟢 OK (Quedan {horas_restantes} horas)")
            
            with col_accion:
                if st.button("✅ Hecho", key=f"maint_{i}"):
                    datos["mantenimientos_mixtos"][i]["ultima_vez_horas"] = horas_actuales
                    datos["mantenimientos_mixtos"][i]["ultima_vez_fecha"] = hoy.strftime("%Y-%m-%d")
                    datos["historial"].append({
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "usuario": usuario_actual,
                        "evento": f"Realizó mantenimiento: {maint['elemento']}",
                        "horas": horas_actuales
                    })
                    guardar_datos_nube(datos)
                    st.rerun()
                    
        st.markdown("---")
        st.header("📅 Caducidades de Seguridad")
        for i, item in enumerate(datos["caducidades_puras"]):
            col_txt, col_btn = st.columns([3, 1])
            fecha_cad = datetime.strptime(item["fecha_caducidad"], "%Y-%m-%d").date()
            dias_restantes = (fecha_cad - hoy).days
            with col_txt:
                st.write(f"**{item['elemento']}**")
                if dias_restantes <= 0:
                    st.error(f"🔴 CADUCADO el {fecha_cad.strftime('%d/%m/%Y')}")
                elif dias_restantes <= 30:
                    st.warning(f"🟡 Caduca pronto ({dias_restantes} días)")
                else:
                    st.success(f"🟢 OK (Caduca el {fecha_cad.strftime('%d/%m/%Y')})")
            with col_btn:
                if st.button("🔄 Renovado", key=f"cad_{i}"):
                    datos["caducidades_puras"][i]["fecha_caducidad"] = (hoy + timedelta(days=730)).strftime("%Y-%m-%d")
                    datos["historial"].append({
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "usuario": usuario_actual,
                        "evento": f"Renovó caducidad: {item['elemento']}",
                        "horas": horas_actuales
                    })
                    guardar_datos_nube(datos)
                    st.rerun()

    # PESTAÑA 2: BRICOS REALES
    with tab2:
        st.header("📋 Lista de Bricos (Tareas)")
        with st.expander("➕ Añadir nueva tarea"):
            nuevo_brico = st.text_input("¿Qué hay que hacer?")
            nueva_prio = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"])
            if st.button("Agregar Brico"):
                if nuevo_brico:
                    datos["tareas"].append({"nombre": nuevo_brico, "prioridad": nueva_prio, "hecha": False})
                    guardar_datos_nube(datos)
                    st.rerun()
                    
        st.markdown("---")
        for idx, tarea in enumerate(datos["tareas"]):
            if not tarea.get("hecha", False):
                cb1, cb2 = st.columns([3, 1])
                with cb1:
                    st.write(f"🔹 **{tarea['nombre']}**")
                    st.caption(f"Prioridad: {tarea.get('prioridad', 'Media')}")
                with cb2:
                    if st.button("💥 Hecho", key=f"tarea_{idx}"):
                        datos["tareas"][idx]["hecha"] = True
                        datos["historial"].append({
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "usuario": usuario_actual,
                            "evento": f"Completó brico: {tarea['nombre']}",
                            "horas": horas_actuales
                        })
                        guardar_datos_nube(datos)
                        st.rerun()

    # PESTAÑA 3: HISTORIAL
    with tab3:
        st.header("📜 Historial de Actividad")
        for log in reversed(datos["historial"]):
            st.markdown(f"**[{log.get('fecha')}]** - **{log.get('usuario')}**: {log.get('evento')} *({log.get('horas')} hrs)*")
            st.markdown("---")
