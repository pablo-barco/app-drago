import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Gestión de Barco Compartido", page_icon="⚓", layout="centered")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google():
    # Convertimos tus secretos TOML en algo que Google entienda
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
        # Intentamos leer la celda A1, donde guardaremos todo comprimido
        datos_str = wks.acell("A1").value
        if datos_str:
            return json.loads(datos_str)
    except Exception:
        pass
        
    # Si la celda está vacía (la primera vez), leemos tu archivo original subido a GitHub
    with open("datos_barco.json", "r", encoding="utf-8") as f:
        datos_base = json.load(f)
    
    # Y lo subimos a Google Sheets para que ya se quede ahí para siempre
    wks.update_acell("A1", json.dumps(datos_base, ensure_ascii=False))
    return datos_base

def guardar_datos_nube(datos):
    # Cada vez que haya un cambio, machacamos la celda A1 con los datos nuevos
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
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"Reparación: {tarea['nombre']}", "horas": horas_actuales})
                        hubo_cambios = True
        if hubo_cambios:
            guardar_datos_nube(datos)
            st.rerun()
    
    with tab3:
        st.header("📝 Listas de Verificación de Seguridad")
        chk_salida, chk_entrada = st.columns(2)
        with chk_salida:
            st.subheader("🛫 Antes de Zarpar")
            for j, elemento_s in enumerate(datos["checklist_salida"]):
                st.checkbox(elemento_s, key=f"check_live_s_{j}")
        with chk_entrada:
            st.subheader("🛬 Al Llegar a Puerto")
            for k, elemento_e in enumerate(datos["checklist_entrada"]):
                st.checkbox(elemento_e, key=f"check_live_e_{k}")
    
    with tab4:
        st.header("📜 Historial de Operaciones")
        for registro in reversed(datos["historial"]):
            fecha_reg = registro.get("fecha", "Fecha N/A")
            usuario_reg = registro.get("usuario", "Socio Desconocido")
            evento_reg = registro.get("evento", "Evento sin detallar")
            horas_reg = registro.get("horas", "---")
            st.markdown(f"**[{fecha_reg}]** - 👤 *{usuario_reg}*: **{evento_reg}** ({horas_reg} hrs)")
            st.markdown("---")
    
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
            st.write("Modifica los nombres existentes, añade nuevos miembros o elimínalos:")
            lista_editada = []
            for idx, socio in enumerate(datos["socios"]):
                col_txt, col_btn = st.columns([4, 1])
                with col_txt:
                    nombre_nuevo = st.text_input(f"Socio {idx + 1}", value=socio, key=f"input_socio_{idx}")
                    if nombre_nuevo.strip():
                        lista_editada.append(nombre_nuevo.strip())
                with col_btn:
                    st.write("") 
                    if st.button("🗑️", key=f"btn_del_socio_{idx}"):
                        datos["socios"].pop(idx)
                        guardar_datos_nube(datos)
                        if socio == usuario_actual:
                            st.session_state["usuario_actual"] = None
                        st.rerun()
            
            if lista_editada != datos["socios"] and len(lista_editada) == len(datos["socios"]):
                if usuario_actual in datos["socios"]:
                    idx_actual = datos["socios"].index(usuario_actual)
                    st.session_state["usuario_actual"] = lista_editada[idx_actual]
                
                datos["socios"] = lista_editada
                guardar_datos_nube(datos)
                st.rerun()
                
            st.markdown("---")
            st.write("**➕ Añadir un nuevo socio a la lista:**")
            nuevo_socio_nombre = st.text_input("Nombre del nuevo miembro:")
            if st.button("Guardar nuevo socio"):
                if nuevo_socio_nombre.strip() and nuevo_socio_nombre.strip() not in datos["socios"]:
                    datos["socios"].append(nuevo_socio_nombre.strip())
                    guardar_datos_nube(datos)
                    st.rerun()
        
        st.markdown("---")
        
        st.header("➕ Añadir Nuevos Controles")
        with st.expander("🛠️ Añadir Nueva Reparación Pendiente"):
            nueva_tarea = st.text_input("Descripción de la reparación:", key="input_add_tarea")
            prioridad_tarea = st.selectbox("Prioridad:", ["Baja", "Media", "Alta"], key="select_add_tarea")
            if st.button("Añadir Tarea", key="btn_add_tarea"):
                if nueva_tarea:
                    datos["tareas"].append({"nombre": nueva_tarea, "hecha": False, "prioridad": prioridad_tarea})
                    guardar_datos_nube(datos)
                    st.rerun()

        with st.expander("📅 Añadir Elemento con Caducidad"):
            nuevo_elemento = st.text_input("Nombre del elemento de seguridad:", key="input_add_cad")
            fecha_input = st.date_input("Fecha de caducidad:", value=date.today(), key="date_add_cad")
            if st.button("Añadir Caducidad", key="btn_add_cad"):
                if nuevo_elemento:
                    datos["caducidades_puras"].append({"elemento": nuevo_elemento, "fecha_caducidad": fecha_input.strftime("%Y-%m-%d")})
                    guardar_datos_nube(datos)
                    st.rerun()

        with st.expander("🔧 Añadir Mantenimiento Mixto (Por horas y fecha)"):
            nombre_maint = st.text_input("Nombre del mantenimiento crítico:", key="input_add_mixto")
            int_h = st.number_input("¿Cada cuántas horas?:", value=100, key="num_add_mixto_h")
            int_m = st.number_input("¿Cada cuántos meses?:", value=12, key="num_add_mixto_m")
            if st.button("Guardar Mantenimiento", key="btn_add_mixto"):
                if nombre_maint:
                    datos["mantenimientos_mixtos"].append({"elemento": nombre_maint, "intervalo_horas": int_h, "ultima_vez_horas": horas_actuales, "intervalo_meses": int_m, "ultima_vez_fecha": hoy.strftime("%Y-%m-%d")})
                    guardar_datos_nube(datos)
                    st.rerun()

        st.markdown("---")
        
        st.header("📝 Editar Listas de Verificación (Checklists)")
        with st.expander("🛫 Gestionar Lista: Antes de Zarpar"):
            item_salida_nuevo = st.text_input("Añadir nueva verificación para la salida:", key="in_add_chk_s")
            if st.button("➕ Añadir a Salida", key="btn_add_chk_s"):
                if item_salida_nuevo and item_salida_nuevo not in datos["checklist_salida"]:
                    datos["checklist_salida"].append(item_salida_nuevo)
                    guardar_datos_nube(datos)
                    st.rerun()
            st.write("**Elementos actuales:**")
            for idx, item in enumerate(datos["checklist_salida"]):
                c_item, c_btn = st.columns([4, 1])
                c_item.write(f"• {item}")
                if c_btn.button("🗑️", key=f"del_s_{idx}"):
                    datos["checklist_salida"].pop(idx)
                    guardar_datos_nube(datos)
                    st.rerun()

        with st.expander("🛬 Gestionar Lista: Al Llegar a Puerto"):
            item_entrada_nuevo = st.text_input("Añadir nueva verificación para el puerto:", key="in_add_chk_e")
            if st.button("➕ Añadir a Puerto", key="btn_add_chk_e"):
                if item_entrada_nuevo and item_entrada_nuevo not in datos["checklist_entrada"]:
                    datos["checklist_entrada"].append(item_entrada_nuevo)
                    guardar_datos_nube(datos)
                    st.rerun()
            st.write("**Elementos actuales:**")
            for idx, item in enumerate(datos["checklist_entrada"]):
                c_item, c_btn = st.columns([4, 1])
                c_item.write(f"• {item}")
                if c_btn.button("🗑️", key=f"del_e_{idx}"):
                    datos["checklist_entrada"].pop(idx)
                    guardar_datos_nube(datos)
                    st.rerun()
