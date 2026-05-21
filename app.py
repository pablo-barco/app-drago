import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

# Configuración mejorada de la página con icono de vela
st.set_page_config(page_title="DRAGO - Gestión de Barco Compartido", page_icon="⛵", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS (Sin cambios) ---
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

# --- FUNCIONES DE NUBE (Sin cambios) ---
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
        # TOAST DE BIENVENIDA FLOTANTE
        st.toast(f"¡Bienvenido a bordo, {usuario_seleccionado}!", icon='⛵')
        st.rerun()

# SI YA HAY UN SOCIO IDENTIFICADO:
else:
    usuario_actual = st.session_state["usuario_actual"]
    
    # --- BARRA LATERAL EMBELLECIDA (OPCIÓN 2) ---
    st.sidebar.title("⚓ DRAGO")
    
    # Intentamos cargar la foto del barco. Si no existe, no hacemos nada.
    try:
        st.sidebar.image("foto_barco.jpg", use_container_width=True)
    except FileNotFoundError:
        pass # Si no hay foto, simplemente no la mostramos

    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar de Socio"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ DRAGO - Gestión de Navegación")
    
    hoy = date.today()
    horas_actuales = int(datos["horas_motor"])
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Mandos", "📋 Bricos", "📝 Checks", "📜 Historial", "⚙️ Panel"])
    
    # PESTAÑA 1: CUADRO DE MANDOS CON CONFIRMACIÓN Y TOASTS
    with tab1:
        st.header("⏱️ Estado del Motor")
        st.metric(label="Horas Actuales", value=f"{horas_actuales} hrs")
        
        st.header("🔧 Mantenimientos Críticos")
        for i, maint in enumerate(datos["mantenimientos_mixtos"]):
            horas_desde_ultimo = horas_actuales - maint["ultima_vez_horas"]
            horas_restantes = maint["intervalo_horas"] - horas_desde_ultimo
            fecha_ultima = datetime.strptime(maint["ultima_vez_fecha"], "%Y-%m-%d").date()
            fecha_vencimiento = fecha_ultima + timedelta(days=maint["intervalo_meses"] * 30)
            dias_restantes = (fecha_vencimiento - hoy).days
            vence = (horas_restantes <= 0) or (dias_restantes <= 0)
            proximo = (0 < horas_restantes <= 15) or (0 < dias_restantes <= 30)
    
            col_texto, col_boton = st.columns([3, 2]) 
            with col_texto:
                if vence: st.error(f"🔴 **{maint['elemento']}**: VENCIDO!")
                elif proximo: st.warning(f"🟡 **{maint['elemento']}**: Próximo.")
                else: st.success(f"🟢 **{maint['elemento']}**: OK.")
            with col_boton:
                if st.session_state.get(f"conf_maint_{i}", False):
                    st.warning("¿Seguro?")
                    c_y, c_n = st.columns(2)
                    if c_y.button("✔️ Sí", key=f"y_maint_{i}"):
                        datos["mantenimientos_mixtos"][i]["ultima_vez_horas"] = horas_actuales
                        datos["mantenimientos_mixtos"][i]["ultima_vez_fecha"] = hoy.strftime("%Y-%m-%d")
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"🛠️ Hecho: {maint['elemento']}", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state[f"conf_maint_{i}"] = False
                        st.toast("✅ Mantenimiento registrado y reiniciado.", icon='🛠️')
                        st.rerun()
                    if c_n.button("❌ No", key=f"n_maint_{i}"):
                        st.session_state[f"conf_maint_{i}"] = False
                        st.rerun()
                else:
                    if st.button("🛠️ Hecho", key=f"btn_maint_{i}"):
                        st.session_state[f"conf_maint_{i}"] = True
                        st.rerun()
    
        st.header("📅 Caducidades de Seguridad")
        for i, item in enumerate(datos["caducidades_puras"]):
            fecha_cad = datetime.strptime(item["fecha_caducidad"], "%Y-%m-%d").date()
            dias_pure = (fecha_cad - hoy).days
            col_txt, col_btn = st.columns([3, 2])
            with col_txt:
                if dias_pure < 0: st.error(f"🔴 **{item['elemento']}**: CADUCADO!")
                elif dias_pure <= 30: st.warning(f"🟡 **{item['elemento']}**: Caduca pronto.")
                else: st.success(f"🟢 **{item['elemento']}**: OK.")
            with col_btn:
                if st.session_state.get(f"conf_cad_{i}", False):
                    st.warning("¿Seguro?")
                    c_y, c_n = st.columns(2)
                    if c_y.button("✔️ Sí", key=f"y_cad_{i}"):
                        datos["caducidades_puras"][i]["fecha_caducidad"] = (hoy + timedelta(days=730)).strftime("%Y-%m-%d")
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"🔄 Renovado: {item['elemento']}", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state[f"conf_cad_{i}"] = False
                        st.toast("✅ Renovación registrada.", icon='🧯')
                        st.rerun()
                    if c_n.button("❌ No", key=f"n_cad_{i}"):
                        st.session_state[f"conf_cad_{i}"] = False
                        st.rerun()
                else:
                    if st.button("🔄 Renovado", key=f"btn_cad_{i}"):
                        st.session_state[f"conf_cad_{i}"] = True
                        st.rerun()
    
    # PESTAÑA 2: LISTA DE TAREAS CON TOASTS
    with tab2:
        st.header("📋 Tareas de Bricolaje")
        for i, tarea in enumerate(datos["tareas"]):
            if not tarea["hecha"]:
                col_t, col_b = st.columns([4, 1])
                with col_t: st.info(f"🔹 {tarea['nombre']} [{tarea['prioridad']}]")
                with col_b:
                    if st.button("✅", key=f"btn_tar_{i}"):
                        datos["tareas"][i]["hecha"] = True
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Completado: {tarea['nombre']}", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.toast("✅ Tarea completada y archivada.", icon='📋')
                        st.rerun()
    
    # PESTAÑA 3: CHECKLISTS CON TOASTS Y PARCHE APLICADO
    with tab3:
        st.header("📝 Listas de Seguridad")
        chk_salida, chk_entrada = st.columns(2)
        
        with chk_salida:
            st.subheader("🛫 Salida")
            for j, elemento_s in enumerate(datos["checklist_salida"]):
                st.checkbox(elemento_s, key=f"check_live_s_{j}")
            
            st.write("") 
            if st.button("✅ Registrar Salida", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "✔️ Checklist Salida completado", "horas": horas_actuales})
                guardar_datos_nube(datos)
                # Parche aplicado (Uso de del)
                for j in range(len(datos["checklist_salida"])):
                    if f"check_live_s_{j}" in st.session_state:
                        del st.session_state[f"check_live_s_{j}"]
                # TOAST FLOTANTE (OPCIÓN 3)
                st.toast("✅ ¡Salida registrada en historial!", icon='🛫')
                st.rerun()

        with chk_entrada:
            st.subheader("🛬 Llegada")
            for k, elemento_e in enumerate(datos["checklist_entrada"]):
                st.checkbox(elemento_e, key=f"check_live_e_{k}")
            
            st.write("") 
            if st.button("✅ Registrar Llegada", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "✔️ Checklist Llegada completado", "horas": horas_actuales})
                guardar_datos_nube(datos)
                # Parche aplicado (Uso de del)
                for k in range(len(datos["checklist_entrada"])):
                    if f"check_live_e_{k}" in st.session_state:
                        del st.session_state[f"check_live_e_{k}"]
                # TOAST FLOTANTE (OPCIÓN 3)
                st.toast("✅ ¡Llegada registrada en historial!", icon='🛬')
                st.rerun()
    
    # PESTAÑA 4: HISTORIAL DE EVENTOS
    with tab4:
        st.header("📜 Historial de Operaciones")
        st.markdown("---")
        for registro in reversed(datos["historial"]):
            st.markdown(f"**[{registro.get('fecha')}]** - *{registro.get('usuario')}*: **{registro.get('evento')}** ({registro.get('horas')} hrs)")
            st.markdown("---")
    
    # PESTAÑA 5: PANEL DE CONTROL REORDENADO CON TOASTS
    with tab5:
        st.header("⚙️ Final de Navegación")
        horas_input = st.number_input("¿Con cuántas horas ha quedado el motor?:", min_value=0, value=horas_actuales)
        if st.button("Actualizar Horas y Guardar"):
            if horas_input > horas_actuales:
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"⏱️ Fin Navegación: {horas_input - horas_actuales} hrs", "horas": horas_input})
            datos["horas_motor"] = horas_input
            guardar_datos_nube(datos)
            # TOAST FLOTANTE (OPCIÓN 3)
            st.toast("✅ Horas de motor actualizadas.", icon='⏱️')
            st.rerun()
            
        st.markdown("---")
        
        # --- GESTIÓN DE CONTROLES ---
        st.header("➕ Gestión de Controles")
        with st.expander("🛠️ Tareas"):
            nt = st.text_input("Nueva tarea:", key="in_tar")
            pr = st.selectbox("Prioridad:", ["Baja", "Media", "Alta"], key="sl_tar")
            if st.button("Añadir", key="bt_tar"):
                if nt:
                    datos["tareas"].append({"nombre": nt, "hecha": False, "prioridad": pr})
                    guardar_datos_nube(datos)
                    st.toast("Añadida", icon='✅')
                    st.rerun()
            st.write("**Actuales:**")
            for idx, tar in enumerate(datos["tareas"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{tar['nombre']} [{tar['prioridad']}]")
                if c2.button("🗑️", key=f"dt_{idx}"):
                    datos["tareas"].pop(idx)
                    guardar_datos_nube(datos)
                    st.toast("Borrado", icon='🗑️')
                    st.rerun()

        with st.expander("📅 Caducidades"):
            ne = st.text_input("Elemento:", key="in_cad")
            fc = st.date_input("Caducidad:", value=date.today(), key="da_cad")
            if st.button("Añadir", key="bt_cad"):
                if ne:
                    datos["caducidades_puras"].append({"elemento": ne, "fecha_caducidad": fc.strftime("%Y-%m-%d")})
                    guardar_datos_nube(datos)
                    st.toast("Añadida", icon='✅')
                    st.rerun()
            st.write("**Actuales:**")
            for idx, item in enumerate(datos["caducidades_puras"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{item['elemento']} ({item['fecha_caducidad']})")
                if c2.button("🗑️", key=f"dc_{idx}"):
                    datos["caducidades_puras"].pop(idx)
                    guardar_datos_nube(datos)
                    st.toast("Borrado", icon='🗑️')
                    st.rerun()

        with st.expander("🔧 Mantenimientos"):
            nm = st.text_input("Mantenimiento:", key="in_maint")
            ih = st.number_input("Horas:", value=100, key="nu_h")
            im = st.number_input("Meses:", value=12, key="nu_m")
            if st.button("Guardar", key="bt_maint"):
                if nm:
                    datos["mantenimientos_mixtos"].append({"elemento": nm, "intervalo_horas": ih, "ultima_vez_horas": horas_actuales, "intervalo_meses": im, "ultima_vez_fecha": hoy.strftime("%Y-%m-%d")})
                    guardar_datos_nube(datos)
                    st.toast("Guardado", icon='✅')
                    st.rerun()
            st.write("**Actuales:**")
            for idx, maint in enumerate(datos["mantenimientos_mixtos"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{maint['elemento']} ({maint['intervalo_horas']}h/{maint['intervalo_meses']}m)")
                if c2.button("🗑️", key=f"dm_{idx}"):
                    datos["mantenimientos_mixtos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.toast("Borrado", icon='🗑️')
                    st.rerun()

        with st.expander("📝 Checklists"):
            is_n = st.text_input("Añadir Salida:", key="in_ch_s")
            if st.button("Añadir", key="bt_ch_s"):
                if is_n and is_n not in datos["checklist_salida"]:
                    datos["checklist_salida"].append(is_n)
                    guardar_datos_nube(datos)
                    st.toast("Añadido", icon='✅')
                    st.rerun()
            for idx, item in enumerate(datos["checklist_salida"]):
                c1, c2 = st.columns([4, 1]); st.write(item)
                if c2.button("🗑️", key=f"ds_{idx}"): datos["checklist_salida"].pop(idx); guardar_datos_nube(datos); st.toast("Borrado", icon='🗑️'); st.rerun()
            st.write("---")
            ie_n = st.text_input("Añadir Entrada:", key="in_ch_e")
            if st.button("Añadir", key="bt_ch_e"):
                if ie_n and ie_n not in datos["checklist_entrada"]:
                    datos["checklist_entrada"].append(ie_n)
                    guardar_datos_nube(datos)
                    st.toast("Añadido", icon='✅')
                    st.rerun()
            for idx, item in enumerate(datos["checklist_entrada"]):
                c1, c2 = st.columns([4, 1]); st.write(item)
                if c2.button("🗑️", key=f"de_{idx}"): datos["checklist_entrada"].pop(idx); guardar_datos_nube(datos); st.toast("Borrado", icon='🗑️'); st.rerun()

        st.markdown("---")
        
        # --- GESTIÓN DE LA TRIPULACIÓN (Al final) ---
        st.header("👥 Gestión de la Tripulación")
        with st.expander("Configuración socios"):
            lista_editada = []
            for idx, socio in enumerate(datos["socios"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    nombre_nuevo = st.text_input(f"Socio {idx + 1}", value=socio, key=f"is_{idx}")
                    if nombre_nuevo.strip(): lista_editada.append(nombre_nuevo.strip())
                with col2:
                    st.write("") 
                    if st.button("🗑️", key=f"dsoc_{idx}"):
                        datos["socios"].pop(idx); guardar_datos_nube(datos)
                        if socio == usuario_actual: st.session_state["usuario_actual"] = None
                        st.toast("Socio eliminado", icon='🗑️')
                        st.rerun()
            
            if lista_editada != datos["socios"] and len(lista_editada) == len(datos["socios"]):
                if usuario_actual in datos["socios"]:
                    idx_actual = datos["socios"].index(usuario_actual)
                    st.session_state["usuario_actual"] = lista_editada[idx_actual]
                datos["socios"] = lista_editada; guardar_datos_nube(datos); st.rerun()
            
            st.markdown("---")
            nsn = st.text_input("Nombre del nuevo miembro:")
            if st.button("Añadir nuevo socio"):
                if nsn.strip() and nsn.strip() not in datos["socios"]:
                    datos["socios"].append(nsn.strip()); guardar_datos_nube(datos)
                    st.toast(f"¡Bienvenido, {nsn}!", icon='✅')
                    st.rerun()
