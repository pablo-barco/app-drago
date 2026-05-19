import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Gestión de Barco Compartido", page_icon="⚓", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google():
    credenciales = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(credenciales)
    return gc.open("datos_barco_cloud")

try:
    sh = conectar_google()
    wks = sh.worksheet("config")
except Exception as e:
    st.error(f"Error conectando a la hoja de cálculo: {e}")
    st.stop()

# --- FUNCIONES DE NUBE ---
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

# --- CONTROL DE ACCESO (PANTALLA DE INICIO) ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ DRAGO - Control de Acceso")
    st.markdown("---")
    st.subheader("👤 Identificación de Tripulación")
    
    usuario_seleccionado = st.selectbox("Selecciona qué socio va a acceder a la app:", datos["socios"])
    
    if st.button("🚀 Entrar a la Aplicación", use_container_width=True):
        st.session_state["usuario_actual"] = usuario_seleccionado
        st.rerun()

# SI YA HAY UN SOCIO IDENTIFICADO:
else:
    usuario_actual = st.session_state["usuario_actual"]
    
    st.sidebar.title("⚓ DRAGO")
    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar de Socio"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ DRAGO - Gestión de Navegación")
    
    hoy = date.today()
    horas_actuales = int(datos["horas_motor"])
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Cuadro de Mandos", "📋 Tareas", "📝 Checklists", "📜 Historial", "⚙️ Panel de Control"])
    
    # PESTAÑA 1: CUADRO DE MANDOS
    with tab1:
        st.header("⏱️ Estado del Motor")
        st.metric(label="Horas Actuales", value=f"{horas_actuales} hrs")
        
        st.header("⚠️ Alertas Activas y Mantenimiento")
        st.subheader("🔧 Motor y Elementos Críticos")
        for i, maint in enumerate(datos["mantenimientos_mixtos"]):
            horas_desde_ultimo = horas_actuales - maint["ultima_vez_horas"]
            horas_restantes = maint["intervalo_horas"] - horas_desde_ultimo
            fecha_ultima = datetime.strptime(maint["ultima_vez_fecha"], "%Y-%m-%d").date()
            fecha_vencimiento = fecha_ultima + timedelta(days=maint["intervalo_meses"] * 30)
            dias_restantes = (fecha_vencimiento - hoy).days
            vence = (horas_restantes <= 0) or (dias_restantes <= 0)
            proximo = (0 < horas_restantes <= 15) or (0 < dias_restantes <= 30)
    
            col_texto, col_boton = st.columns([3, 1])
            with col_texto:
                if vence: st.error(f"🔴 **{maint['elemento']}**: ¡VENCIDO!")
                elif proximo: st.warning(f"🟡 **{maint['elemento']}**: Próximo a vencer.")
                else: st.success(f"🟢 **{maint['elemento']}**: Al día.")
            with col_boton:
                if st.button("🛠️ Hecho", key=f"btn_maint_{i}"):
                    datos["mantenimientos_mixtos"][i]["ultima_vez_horas"] = horas_actuales
                    datos["mantenimientos_mixtos"][i]["ultima_vez_fecha"] = hoy.strftime("%Y-%m-%d")
                    datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Mantenimiento: {maint['elemento']}", "horas": horas_actuales})
                    guardar_datos_nube(datos)
                    st.rerun()
    
        st.subheader("📅 Caducidades de Seguridad")
        for i, item in enumerate(datos["caducidades_puras"]):
            fecha_cad = datetime.strptime(item["fecha_caducidad"], "%Y-%m-%d").date()
            dias_pure = (fecha_cad - hoy).days
            col_txt, col_btn = st.columns([3, 1])
            with col_txt:
                if dias_pure < 0: st.error(f"🔴 **{item['elemento']}**: ¡CADUCADO!")
                elif dias_pure <= 30: st.warning(f"🟡 **{item['elemento']}**: Caduca en {dias_pure} días")
                else: st.success(f"🟢 **{item['elemento']}**: OK (Faltan {dias_pure} días)")
            with col_btn:
                if st.button("🔄 Renovado", key=f"btn_cad_{i}"):
                    datos["caducidades_puras"][i]["fecha_caducidad"] = (hoy + timedelta(days=730)).strftime("%Y-%m-%d")
                    datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Renovado: {item['elemento']}", "horas": horas_actuales})
                    guardar_datos_nube(datos)
                    st.rerun()
    
    # PESTAÑA 2: LISTA DE TAREAS
    with tab2:
        st.header("📋 Tareas de Bricolaje / Reparaciones")
        hubo_cambios = False
        for i, tarea in enumerate(datos["tareas"]):
            if not tarea["hecha"]:
                col_t, col_b = st.columns([4, 1])
                with col_t: st.info(f"🔹 {tarea['nombre']} [{tarea['prioridad']}]")
                with col_b:
                    if st.button("✅ Terminado", key=f"btn_tar_{i}"):
                        datos["tareas"][i]["hecha"] = True
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Reparación completada: {tarea['nombre']}", "horas": horas_actuales})
                        hubo_cambios = True
        if hubo_cambios:
            guardar_datos_nube(datos)
            st.rerun()
    
    # PESTAÑA 3: CHECKLISTS CON VALIDACIÓN
    with tab3:
        st.header("📝 Listas de Verificación de Seguridad")
        chk_salida, chk_entrada = st.columns(2)
        
        with chk_salida:
            st.subheader("🛫 Antes de Zarpar")
            for j, elemento_s in enumerate(datos["checklist_salida"]):
                st.checkbox(elemento_s, key=f"check_live_s_{j}")
            
            st.write("") # Espacio
            if st.button("✅ Registrar Salida en Historial", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "Completado: Checklist Antes de Zarpar", "horas": horas_actuales})
                guardar_datos_nube(datos)
                # Limpiamos los checks para el siguiente usuario
                for j in range(len(datos["checklist_salida"])):
                    st.session_state[f"check_live_s_{j}"] = False
                st.success("¡Salida registrada!")
                st.rerun()

        with chk_entrada:
            st.subheader("🛬 Al Llegar a Puerto")
            for k, elemento_e in enumerate(datos["checklist_entrada"]):
                st.checkbox(elemento_e, key=f"check_live_e_{k}")
            
            st.write("") # Espacio
            if st.button("✅ Registrar Llegada en Historial", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "Completado: Checklist Al Llegar a Puerto", "horas": horas_actuales})
                guardar_datos_nube(datos)
                # Limpiamos los checks para el siguiente usuario
                for k in range(len(datos["checklist_entrada"])):
                    st.session_state[f"check_live_e_{k}"] = False
                st.success("¡Llegada registrada!")
                st.rerun()
    
    # PESTAÑA 4: HISTORIAL DE EVENTOS
    with tab4:
        st.header("📜 Historial de Operaciones")
        for registro in reversed(datos["historial"]):
            fecha_reg = registro.get("fecha", "Fecha N/A")
            usuario_reg = registro.get("usuario", "Socio Desconocido")
            evento_reg = registro.get("evento", "Evento sin detallar")
            horas_reg = registro.get("horas", "---")
            st.markdown(f"**[{fecha_reg}]** - 👤 *{usuario_reg}*: **{evento_reg}** ({horas_reg} hrs)")
            st.markdown("---")
    
    # PESTAÑA 5: PANEL DE CONTROL MEJORADO
    with tab5:
        st.header("⚙️ Registrar Salida (Actualizar horas)")
        st.write(f"Socio registrando la navegación: **{usuario_actual}**")
        horas_input = st.number_input("¿Con cuántas horas ha quedado el motor?:", min_value=0, value=horas_actuales)
        if st.button("Registrar Fin de Navegación"):
            if horas_input > horas_actuales:
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Navegación: +{horas_input - horas_actuales} horas", "horas": horas_input})
            datos["horas_motor"] = horas_input
            guardar_datos_nube(datos)
            st.success("¡Horas actualizadas!")
            st.rerun()
            
        st.markdown("---")
        
        st.header("👥 Gestión de la Tripulación")
        with st.expander("⚙️ Configuración: Personalizar nombres de los socios"):
            lista_editada = []
            for idx, socio in enumerate(datos["socios"]):
                col_txt, col_btn = st.columns([4, 1])
                with col_txt:
                    nombre_nuevo = st.text_input(f"Socio {idx + 1}", value=socio,
