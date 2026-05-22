import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

# Configuración de la página
st.set_page_config(page_title="BARCO DEMO - Gestión de Barco", page_icon="⛵", layout="centered")

# --- SISTEMA DE MENSAJES FLOTANTES ---
if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"]["texto"], icon=st.session_state["toast_msg"]["icono"])
    del st.session_state["toast_msg"]

# --- CONEXIÓN A GOOGLE SHEETS (COPIA DEMO) ---
@st.cache_resource
def conectar_google():
    credenciales = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(credenciales)
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

# Forzar nombres genéricos fijos para la DEMO
datos["socios"] = ["Socio 1", "Socio 2", "Socio 3"]

if "finanzas_gastos" not in datos: datos["finanzas_gastos"] = []
if "finanzas_ingresos" not in datos: datos["finanzas_ingresos"] = []
if "tareas" not in datos: datos["tareas"] = []
if "checklist_salida" not in datos: datos["checklist_salida"] = []
if "checklist_entrada" not in datos: datos["checklist_entrada"] = []

# --- CONTROL DE ACCESO ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ BARCO - Control de Acceso (DEMO)")
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
    st.sidebar.title("⚓ BARCO DEMO")
    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar de Socio"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ BARCO - Gestión de Navegación")
    
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
            proximo = (0 < horas_restantes <= 15) or (0 < dias_restantes <= 30)
            
            fecha_ver = fecha_vencimiento.strftime("%d/%m/%Y")
    
            col_texto, col_boton = st.columns([3, 2]) 
            with col_texto:
                if vence: st.error(f"🔴 **{maint['elemento']}**: VENCIDO")
                elif proximo: st.warning(f"🟡 **{maint['elemento']}**: Próximo a vencer")
                else: st.success(f"🟢 **{maint['elemento']}**: Al día")
                st.caption(f"📅 Fecha límite: **{fecha_ver}** (o a las **{maint['ultima_vez_horas'] + maint['intervalo_horas']} hrs**)")
                
            with col_boton:
                if st.session_state.get(f"conf_maint_{i}", False):
                    st.warning("¿Seguro?")
                    fecha_sugerida = hoy + timedelta(days=maint["intervalo_meses"] * 30)
                    nueva_limite = st.date_input("Ajustar próxima fecha límite:", value=fecha_sugerida, key=f"next_date_maint_{i}")
                    
                    c_y, c_n = st.columns(2)
                    if c_y.button("✔️ Sí", key=f"y_maint_{i}"):
                        datos["mantenimientos_mixtos"][i]["ultima_vez_horas"] = horas_actuales
                        datos["mantenimientos_mixtos"][i]["ultima_vez_fecha"] = hoy.strftime("%Y-%m-%d")
                        datos["mantenimientos_mixtos"][i]["proxima_fecha"] = nueva_limite.strftime("%Y-%m-%d")
                        guardar_datos_nube(datos)
                        st.session_state[f"conf_maint_{i}"] = False
                        st.session_state["toast_msg"] = {"texto": "Mantenimiento registrado.", "icono": "🛠️"}
                        st.rerun()
                    if c_n.button("❌ No", key=f"n_maint_{i}"):
                        st.session_state[f"conf_maint_{i}"] = False
                        st.rerun()
                else:
                    if st.button("🛠️ Hecho", key=f"btn_maint_{i}"):
                        st.session_state[f"conf_maint_{i}"] = True
                        st.rerun()
            st.markdown("---")
    
        st.header("📅 Caducidades de Seguridad")
        for i, item in enumerate(datos["caducidades_puras"]):
            fecha_cad = datetime.strptime(item["fecha_caducidad"], "%Y-%m-%d").date()
            dias_pure = (fecha_cad - hoy).days
            fecha_cad_ver = fecha_cad.strftime("%d/%m/%Y")
            
            col_txt, col_btn = st.columns([3, 2])
            with col_txt:
                if dias_pure < 0: st.error(f"🔴 **{item['elemento']}**: ¡CADUCADO!")
                elif dias_pure <= 30: st.warning(f"🟡 **{item['elemento']}**: Caduca pronto")
                else: st.success(f"🟢 **{item['elemento']}**: OK")
                st.caption(f"📅 Caducidad: **{fecha_cad_ver}** (Faltan {max(0, dias_pure)} días)")
                
            with col_btn:
                if st.session_state.get(f"conf_cad_{i}", False):
                    st.warning("¿Seguro?")
                    c_y, c_n = st.columns(2)
                    if c_y.button("✔️ Sí", key=f"y_cad_{i}"):
                        datos["caducidades_puras"][i]["fecha_caducidad"] = (hoy + timedelta(days=730)).strftime("%Y-%m-%d")
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"🔄 Renovado: {item['elemento']}", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state[f"conf_cad_{i}"] = False
                        st.session_state["toast_msg"] = {"texto": "Renovación registrada.", "icono": "🧯"}
                        st.rerun()
                    if c_n.button("❌ No", key=f"n_cad_{i}"):
                        st.session_state[f"conf_cad_{i}"] = False
                        st.rerun()
                else:
                    if st.button("🔄 Renovado", key=f"btn_cad_{i}"):
                        st.session_state[f"conf_cad_{i}"] = True
                        st.rerun()
            st.markdown("---")
    
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
                        st.session_state["toast_msg"] = {"texto": "Tarea completada.", "icono": "📋"}
                        st.rerun()
    
    with tab3:
        st.header("📝 Listas de Seguridad")
        chk_salida, chk_entrada = st.columns(2)
        
        with chk_salida:
            st.subheader("🛫 Salida")
            for j, elemento_s in enumerate(datos["checklist_salida"]):
                st.checkbox(elemento_s, key=f"check_live_s_{j}")
            if st.button("✅ Registrar Salida", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "✔️ Checklist Salida completado", "horas": horas_actuales})
                guardar_datos_nube(datos)
                st.session_state["toast_msg"] = {"texto": "¡Salida registrada!", "icono": "🛫"}
                st.rerun()

        with chk_entrada:
            st.subheader("🛬 Llegada")
            for k, elemento_e in enumerate(datos["checklist_entrada"]):
                st.checkbox(elemento_e, key=f"check_live_e_{k}")
            if st.button("✅ Registrar Llegada", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "✔️ Checklist Llegada completado", "horas": horas_actuales})
                guardar_datos_nube(datos)
                st.session_state["toast_msg"] = {"texto": "¡Llegada registrada!", "icono": "🛬"}
                st.rerun()
    
    with tab4:
        st.header("📜 Historial de Operaciones")
        st.markdown("---")
        for registro in reversed(datos["historial"]):
            # ✨ FILTRO DE ANONIMIZACIÓN AUTOMÁTICA DEL HISTORIAL:
            # Si el usuario que hizo la acción no está entre los genéricos de la demo, se muestra como "Socio Demo"
            usuario_ver = registro.get("usuario")
            if usuario_ver not in datos["socios"]:
                usuario_ver = "Socio Demo"
                
            st.markdown(f"**[{registro.get('fecha')}]** - *{usuario_ver}*: **{registro.get('evento')}** ({registro.get('horas')} hrs)")
            st.markdown("---")
            
    with tab5:
        st.header("💶 Estado de Cuentas")

        gastos_totales = sum(g["cantidad"] for g in datos["finanzas_gastos"])
        ingresos_totales = sum(i["cantidad"] for i in datos["finanzas_ingresos"])
        gastos_bote = sum(g["cantidad"] for g in datos["finanzas_gastos"] if g["pagado_por"] == "Fondo Común")
        saldo_bote = ingresos_totales - gastos_bote

        meses_transcurridos = (hoy.year - 2025) * 12 + hoy.month
        obligacion_total_teorica = (meses_transcurridos * 100.0) + 720.0

        st.metric("💰 Dinero actual en el Bote Común", f"{saldo_bote:.2f} €")
        st.caption(f"Fondo obligatorio teórico acumulado por socio activo hasta hoy: **{obligacion_total_teorica:.2f} €**")

        st.markdown("---")
        st.subheader("⚖️ Estado de Deuda de los Socios")

        ajustes_historicos = {"Socio 2": 556.94, "Socio 3": 200.00}

        for socio in datos["socios"]:
            aportado_bote = sum(i["cantidad"] for i in datos["finanzas_ingresos"] if i["socio"] == socio)
            pagado_directo = sum(g["cantidad"] for g in datos["finanzas_gastos"] if g["pagado_por"] == socio)
            
            total_aportado_real = aportado_bote + pagado_directo
            credito_total = total_aportado_real + ajustes_historicos.get(socio, 0.0)
            balance_socio = credito_total - obligacion_total_teorica

            col_socio, col_bal = st.columns([3, 1])
            with col_socio:
                st.write(f"**{socio}**")
            with col_bal:
                if balance_socio >= -0.01:
                    st.success("Al día 👍")
                else:
                    st.error(f"Debe {abs(balance_socio):.2f} €")

        st.markdown("---")
        
        col_g, col_i = st.columns(2)
        with col_g:
            with st.expander("💸 Registrar Gasto"):
                concepto_g = st.text_input("Concepto (ej. Filtro combustible):")
                cantidad_g = st.number_input("Importe (€):", min_value=0.0, step=1.0)
                pagador_opciones = ["Fondo Común"] + datos["socios"]
                pagado_por = st.selectbox("¿Quién lo pagó?:", pagador_opciones)
                
                if st.button("Guardar Gasto"):
                    if concepto_g and cantidad_g > 0:
                        datos["finanzas_gastos"].append({
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "concepto": concepto_g,
                            "cantidad": float(cantidad_g),
                            "pagado_por": pagado_por
                        })
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"💸 Gasto: {concepto_g} ({cantidad_g}€)", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state["toast_msg"] = {"texto": "Gasto registrado con éxito.", "icono": "💸"}
                        st.rerun()

        with col_i:
            with st.expander("📥 Aportación al Bote"):
                socio_i = st.selectbox("Socio que ingresa dinero:", datos["socios"])
                cantidad_i = st.number_input("Cantidad (€):", min_value=0.0, step=1.0, key="cant_i")
                concepto_i = st.text_input("Concepto (ej. Aportación mensual...):", value=f"Aportación {socio_i}")
                
                if st.button("Guardar Ingreso"):
                    if cantidad_i > 0:
                        datos["finanzas_ingresos"].append({
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "socio": socio_i,
                            "cantidad": float(cantidad_i),
                            "concepto": concepto_i
                        })
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"📥 Ingreso de {socio_i} ({cantidad_i}€) - {concepto_i}", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state["toast_msg"] = {"texto": "Ingreso registrado con éxito.", "icono": "📥"}
                        st.rerun()

        st.markdown("---")
        with st.expander("📜 Ver y Borrar Historial de Cuentas"):
            st.write("🔴 **Gastos Registrados:**")
            for idx, g in enumerate(datos["finanzas_gastos"]):
                cg1, cg2 = st.columns([4, 1])
                pagador_ver = g['pagado_por'] if g['pagado_por'] in datos["socios"] or g['pagado_por'] == "Fondo Común" else "Socio Demo"
                cg1.write(f"_{g['fecha']}_ - {g['concepto']}: **{g['cantidad']}€** ({pagador_ver})")
                if cg2.button("🗑️", key=f"del_g_{idx}"):
                    datos["finanzas_gastos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.rerun()
            
            st.write("---")
            st.write("🟢 **Aportaciones al Bote Registradas:**")
            for idx, i in enumerate(datos["finanzas_ingresos"]):
                ci1, ci2 = st.columns([4, 1])
                socio_ver = i['socio'] if i['socio'] in datos["socios"] else "Socio Demo"
                det_concepto = i.get("concepto", f"Aportación {socio_ver}")
                ci1.write(f"_{i['fecha']}_ - {socio_ver}: **{i['cantidad']}€** ({det_concepto})")
                if ci2.button("🗑️", key=f"del_i_{idx}"):
                    datos["finanzas_ingresos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.rerun()
    
    with tab6:
        # ✨ RESTAURACIÓN COMPLETA DE LOS MENÚS DEL PANEL DE CONTROL ADAPTADOS A LA DEMO
        st.header("⚙️ Panel de Control y Configuración")
        
        # Bloque 1: Horas del Motor
        st.subheader("⏱️ Actualizar Odómetro General")
        horas_input = st.number_input("¿Con cuántas horas ha quedado el motor?:", min_value=0, value=horas_actuales)
        if st.button("Actualizar Horas y Guardar"):
            datos["horas_motor"] = horas_input
            guardar_datos_nube(datos)
            st.session_state["toast_msg"] = {"texto": "Horas de motor actualizadas.", "icono": "⏱️"}
            st.rerun()
            
        st.markdown("---")
        
        # Bloque 2: Gestión de Bricos
        st.subheader("📋 Añadir Nueva Tarea (Brico)")
        with st.form("nuevo_brico_form", clear_on_submit=True):
            nombre_brico = st.text_input("Nombre de la tarea:")
            prioridad_brico = st.selectbox("Prioridad:", ["Baja", "Media", "Alta"])
            if st.form_submit_button("🔨 Crear Tarea"):
                if nombre_brico:
                    datos["tareas"].append({"nombre": nombre_brico, "prioridad": prioridad_brico, "hecha": False})
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Tarea añadida al panel.", "icono": "🔨"}
                    st.rerun()
                    
        st.markdown("---")
        
        # Bloque 3: Mantenimientos del Motor
        st.subheader("🔧 Configurar Elementos de Mantenimiento Mixto")
        with st.form("nuevo_maint_form", clear_on_submit=True):
            elem_m = st.text_input("Nombre del elemento (ej. Filtro Aire):")
            int_h = st.number_input("Intervalo de Horas (0 si no aplica):", min_value=0, value=100)
            int_m = st.number_input("Intervalo de Meses (0 si no aplica):", min_value=0, value=12)
            if st.form_submit_button("💾 Añadir Mantenimiento"):
                if elem_m and (int_h > 0 or int_m > 0):
                    datos["mantenimientos_mixtos"].append({
                        "elemento": elem_m,
                        "intervalo_horas": int_h,
                        "intervalo_meses": int_m,
                        "ultima_vez_horas": horas_actuales,
                        "ultima_vez_fecha": hoy.strftime("%Y-%m-%d"),
                        "proxima_fecha": (hoy + timedelta(days=int_m*30)).strftime("%Y-%m-%d")
                    })
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Mantenimiento configurado.", "icono": "🔧"}
                    st.rerun()
