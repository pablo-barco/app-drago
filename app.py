import streamlit as st
import json
import gspread
from datetime import datetime, date, timedelta

# Configuración de la página
st.set_page_config(page_title="DRAGO - Gestión de Barco Compartido", page_icon="⛵", layout="centered")

# --- SISTEMA DE MENSAJES FLOTANTES (TRUCO POST-RECARGA) ---
if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"]["texto"], icon=st.session_state["toast_msg"]["icono"])
    del st.session_state["toast_msg"]

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

# --- INYECCIÓN DEL HISTÓRICO COMPLETO 2025 - 2026 ---
if "finanzas_ingresos" not in datos or len(datos["finanzas_ingresos"]) <= 1:
    st.info("Inyectando histórico de cuentas de 2025 y 2026...")
    datos["finanzas_ingresos"] = [
        {"fecha": "2025-01-01", "socio": "Fondo Inicial 2024", "cantidad": 1304.16},
        {"fecha": "2025-01-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-01-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-01-14", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-02-04", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-02-04", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-02-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-03-04", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-03-04", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-03-04", "socio": "Rubén", "cantidad": 400.0},
        {"fecha": "2025-03-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-04-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-04-02", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-04-14", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-05-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-05-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-05-13", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-05-21", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-05-22", "socio": "Justo", "cantidad": 843.06},
        {"fecha": "2025-06-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-06-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-06-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-06-30", "socio": "Rubén", "cantidad": 300.0},
        {"fecha": "2025-07-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-07-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-07-12", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-07-14", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-08-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-08-05", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-08-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-09-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-09-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-09-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-10-01", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-10-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-10-03", "socio": "Rubén", "cantidad": 1020.0},
        {"fecha": "2025-10-03", "socio": "Pablo", "cantidad": 520.0},
        {"fecha": "2025-10-04", "socio": "Leandro", "cantidad": 720.0},
        {"fecha": "2025-10-08", "socio": "Justo", "cantidad": 720.0},
        {"fecha": "2025-10-08", "socio": "Juan Carlos", "cantidad": 720.0},
        {"fecha": "2025-10-13", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-11-04", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-11-04", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-11-11", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2025-12-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2025-12-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2025-12-11", "socio": "Juan Carlos", "cantidad": 100.0},
        # Registros 2026
        {"fecha": "2026-01-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2026-01-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2026-01-12", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2026-02-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2026-02-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2026-02-11", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2026-03-03", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2026-03-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2026-03-11", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2026-04-02", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2026-04-03", "socio": "Pablo", "cantidad": 100.0},
        {"fecha": "2026-04-13", "socio": "Juan Carlos", "cantidad": 100.0},
        {"fecha": "2026-04-05", "socio": "Leandro", "cantidad": 100.0},
        {"fecha": "2026-04-05", "socio": "Pablo", "cantidad": 100.0}
    ]
    datos["finanzas_gastos"] = [
        {"fecha": "2025-02-23", "concepto": "Tela camarote", "cantidad": 55.96, "pagado_por": "Fondo Común"},
        {"fecha": "2025-04-22", "concepto": "Seguro", "cantidad": 255.57, "pagado_por": "Fondo Común"},
        {"fecha": "2025-04-29", "concepto": "Batería motor", "cantidad": 99.00, "pagado_por": "Fondo Común"},
        {"fecha": "2025-05-06", "concepto": "50% varadero patente", "cantidad": 446.00, "pagado_por": "Fondo Común"},
        {"fecha": "2025-05-12", "concepto": "Recibo varadero patente (RESTO)", "cantidad": 446.01, "pagado_por": "Fondo Común"},
        {"fecha": "2025-05-22", "concepto": "Molinete", "cantidad": 843.06, "pagado_por": "Fondo Común"},
        {"fecha": "2025-05-27", "concepto": "Francobordo, pulsador, boza y filtro bomba", "cantidad": 54.31, "pagado_por": "Fondo Común"},
        {"fecha": "2025-05-28", "concepto": "50% pago toldos", "cantidad": 1288.65, "pagado_por": "Fondo Común"},
        {"fecha": "2025-07-10", "concepto": "Resto patente varadero", "cantidad": 328.29, "pagado_por": "Fondo Común"},
        {"fecha": "2025-07-10", "concepto": "Bandera", "cantidad": 9.99, "pagado_por": "Fondo Común"},
        {"fecha": "2025-07-10", "concepto": "Colchoneta e hinchador", "cantidad": 87.93, "pagado_por": "Fondo Común"},
        {"fecha": "2025-07-10", "concepto": "Placa veleta y extintor", "cantidad": 132.00, "pagado_por": "Fondo Común"},
        {"fecha": "2025-07-14", "concepto": "Resto toldo bimini", "cantidad": 665.50, "pagado_por": "Fondo Común"},
        {"fecha": "2025-08-05", "concepto": "Gasoil", "cantidad": 60.00, "pagado_por": "Fondo Común"},
        {"fecha": "2025-09-03", "concepto": "Foco mastil", "cantidad": 40.85, "pagado_por": "Fondo Común"},
        {"fecha": "2025-09-04", "concepto": "Licencia pesca", "cantidad": 41.86, "pagado_por": "Fondo Común"},
        {"fecha": "2025-09-19", "concepto": "Escota genova y amantillo", "cantidad": 136.85, "pagado_por": "Fondo Común"},
        {"fecha": "2025-11-10", "concepto": "Varadero amarre", "cantidad": 4533.72, "pagado_por": "Fondo Común"},
        # Registros 2026
        {"fecha": "2026-03-04", "concepto": "Francobordo bandera, poleas", "cantidad": 92.87, "pagado_por": "Fondo Común"},
        {"fecha": "2026-04-06", "concepto": "Gasoil", "cantidad": 35.00, "pagado_por": "Fondo Común"},
        {"fecha": "2026-04-08", "concepto": "Seguro", "cantidad": 255.57, "pagado_por": "Fondo Común"}
    ]
    guardar_datos_nube(datos)
# -----------------------------------------------------

# PARCHE DE ACTUALIZACIÓN V2.0: Añadimos las variables de finanzas si no existen en la nube
if "finanzas_gastos" not in datos: datos["finanzas_gastos"] = []
if "finanzas_ingresos" not in datos: datos["finanzas_ingresos"] = []

# --- CONTROL DE ACCESO ---
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

if st.session_state["usuario_actual"] is None:
    st.title("⚓ DRAGO - Control de Acceso")
    st.markdown("---")
    st.subheader("👤 Identificación de Tripulación")
    
    usuario_seleccionado = st.selectbox("Selecciona qué socio va a acceder a la app:", datos["socios"])
    
    if st.button("🚀 Entrar a la Aplicación", use_container_width=True):
        st.session_state["usuario_actual"] = usuario_seleccionado
        st.session_state["toast_msg"] = {"texto": f"¡Bienvenido a bordo, {usuario_seleccionado}!", "icono": "⛵"}
        st.rerun()

else:
    usuario_actual = st.session_state["usuario_actual"]
    
    # --- BARRA LATERAL EMBELLECIDA ---
    st.sidebar.title("⚓ DRAGO")
    
    try:
        st.sidebar.image("foto_barco.jpg", use_container_width=True)
    except FileNotFoundError:
        pass

    st.sidebar.markdown(f"👤 Socio activo: **{usuario_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar de Socio"):
        st.session_state["usuario_actual"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ DRAGO - Gestión de Navegación")
    
    hoy = date.today()
    horas_actuales = int(datos["horas_motor"])
    
    # NUEVA PESTAÑA AÑADIDA PARA CUENTAS
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
                if vence: 
                    st.error(f"🔴 **{maint['elemento']}**: VENCIDO")
                elif proximo: 
                    st.warning(f"🟡 **{maint['elemento']}**: Próximo a vencer")
                else: 
                    st.success(f"🟢 **{maint['elemento']}**: Al día")
                
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
                        st.session_state["toast_msg"] = {"texto": "Mantenimiento registrado con nueva fecha límite.", "icono": "🛠️"}
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
                if dias_pure < 0: 
                    st.error(f"🔴 **{item['elemento']}**: ¡CADUCADO!")
                elif dias_pure <= 30: 
                    st.warning(f"🟡 **{item['elemento']}**: Caduca pronto")
                else: 
                    st.success(f"🟢 **{item['elemento']}**: OK")
                
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
                        st.session_state["toast_msg"] = {"texto": "Tarea completada y archivada.", "icono": "📋"}
                        st.rerun()
    
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
                for j in range(len(datos["checklist_salida"])):
                    if f"check_live_s_{j}" in st.session_state:
                        del st.session_state[f"check_live_s_{j}"]
                st.session_state["toast_msg"] = {"texto": "¡Salida registrada en historial!", "icono": "🛫"}
                st.rerun()

        with chk_entrada:
            st.subheader("🛬 Llegada")
            for k, elemento_e in enumerate(datos["checklist_entrada"]):
                st.checkbox(elemento_e, key=f"check_live_e_{k}")
            
            st.write("") 
            if st.button("✅ Registrar Llegada", use_container_width=True):
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": "✔️ Checklist Llegada completado", "horas": horas_actuales})
                guardar_datos_nube(datos)
                for k in range(len(datos["checklist_entrada"])):
                    if f"check_live_e_{k}" in st.session_state:
                        del st.session_state[f"check_live_e_{k}"]
                st.session_state["toast_msg"] = {"texto": "¡Llegada registrada en historial!", "icono": "🛬"}
                st.rerun()
    
    with tab4:
        st.header("📜 Historial de Operaciones")
        st.markdown("---")
        for registro in reversed(datos["historial"]):
            st.markdown(f"**[{registro.get('fecha')}]** - *{registro.get('usuario')}*: **{registro.get('evento')}** ({registro.get('horas')} hrs)")
            st.markdown("---")
            
    # --- NUEVA PESTAÑA 5: FINANZAS ---
    with tab5:
        st.header("💶 Estado de Cuentas")

        # Cálculos Matemáticos
        gastos_totales = sum(g["cantidad"] for g in datos["finanzas_gastos"])
        ingresos_totales = sum(i["cantidad"] for i in datos["finanzas_ingresos"])
        gastos_bote = sum(g["cantidad"] for g in datos["finanzas_gastos"] if g["pagado_por"] == "Fondo Común")

        saldo_bote = ingresos_totales - gastos_bote
        num_socios = len(datos["socios"])
        gasto_por_socio = gastos_totales / num_socios if num_socios > 0 else 0

        # Tarjeta principal
        st.metric("💰 Dinero actual en el Bote Común", f"{saldo_bote:.2f} €")
        st.caption(f"Gasto total histórico del barco: **{gastos_totales:.2f} €** | Gasto teórico por socio: **{gasto_por_socio:.2f} €**")

        st.markdown("---")
        st.subheader("⚖️ Balance de Socios (Compensación)")
        st.write("*(En verde: el barco le debe dinero. En rojo: debe dinero al barco)*")

        for socio in datos["socios"]:
            # Sumamos lo que el socio ingresó al bote + lo que pagó directamente de su bolsillo
            aportado_bote = sum(i["cantidad"] for i in datos["finanzas_ingresos"] if i["socio"] == socio)
            pagado_directo = sum(g["cantidad"] for g in datos["finanzas_gastos"] if g["pagado_por"] == socio)
            total_aportado = aportado_bote + pagado_directo
            
            balance = total_aportado - gasto_por_socio

            col_socio, col_bal = st.columns([3, 1])
            with col_socio:
                st.write(f"**{socio}** (Aportó en total: {total_aportado:.2f}€)")
            with col_bal:
                if balance > 0.01:
                    st.success(f"+{balance:.2f}€")
                elif balance < -0.01:
                    st.error(f"{balance:.2f}€")
                else:
                    st.info("0.00€")

        st.markdown("---")
        
        col_g, col_i = st.columns(2)
        with col_g:
            with st.expander("💸 Registrar Gasto"):
                concepto_g = st.text_input("Concepto (ej. Aceite motor):")
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
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"💸 Gasto: {concepto_g} ({cantidad_g}€ - pagado por {pagado_por})", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state["toast_msg"] = {"texto": "Gasto registrado con éxito.", "icono": "💸"}
                        st.rerun()

        with col_i:
            with st.expander("📥 Aportación al Bote"):
                socio_i = st.selectbox("Socio que ingresa dinero:", datos["socios"])
                cantidad_i = st.number_input("Cantidad (€):", min_value=0.0, step=1.0, key="cant_i")
                
                if st.button("Guardar Ingreso"):
                    if cantidad_i > 0:
                        datos["finanzas_ingresos"].append({
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "socio": socio_i,
                            "cantidad": float(cantidad_i)
                        })
                        datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"📥 Ingreso al bote de {socio_i} ({cantidad_i}€)", "horas": horas_actuales})
                        guardar_datos_nube(datos)
                        st.session_state["toast_msg"] = {"texto": "Ingreso registrado con éxito.", "icono": "📥"}
                        st.rerun()

        st.markdown("---")
        with st.expander("📜 Ver y Borrar Historial de Cuentas"):
            st.write("🔴 **Gastos Registrados:**")
            for idx, g in enumerate(datos["finanzas_gastos"]):
                cg1, cg2 = st.columns([4, 1])
                cg1.write(f"_{g['fecha']}_ - {g['concepto']}: **{g['cantidad']}€** ({g['pagado_por']})")
                if cg2.button("🗑️", key=f"del_g_{idx}"):
                    datos["finanzas_gastos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Gasto eliminado.", "icono": "🗑️"}
                    st.rerun()
            
            st.write("---")
            st.write("🟢 **Aportaciones al Bote Registradas:**")
            for idx, i in enumerate(datos["finanzas_ingresos"]):
                ci1, ci2 = st.columns([4, 1])
                ci1.write(f"_{i['fecha']}_ - {i['socio']}: **{i['cantidad']}€**")
                if ci2.button("🗑️", key=f"del_i_{idx}"):
                    datos["finanzas_ingresos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Ingreso eliminado.", "icono": "🗑️"}
                    st.rerun()
    
    # --- PESTAÑA 6: PANEL DE CONTROL ---
    with tab6:
        st.header("⚙️ Final de Navegación")
        horas_input = st.number_input("¿Con cuántas horas ha quedado el motor?:", min_value=0, value=horas_actuales)
        if st.button("Actualizar Horas y Guardar"):
            if horas_input > horas_actuales:
                datos["historial"].append({"fecha": hoy.strftime("%Y-%m-%d"), "usuario": usuario_actual, "evento": f"⏱️ Fin Navegación: {horas_input - horas_actuales} hrs", "horas": horas_input})
            datos["horas_motor"] = horas_input
            guardar_datos_nube(datos)
            st.session_state["toast_msg"] = {"texto": "Horas de motor actualizadas.", "icono": "⏱️"}
            st.rerun()
            
        st.markdown("---")
        
        st.header("➕ Gestión de Controles")
        with st.expander("🛠️ Tareas"):
            nt = st.text_input("Nueva tarea:", key="in_tar")
            pr = st.selectbox("Prioridad:", ["Baja", "Media", "Alta"], key="sl_tar")
            if st.button("Añadir", key="bt_tar"):
                if nt:
                    datos["tareas"].append({"nombre": nt, "hecha": False, "prioridad": pr})
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Tarea añadida.", "icono": "✅"}
                    st.rerun()
            st.write("**Actuales:**")
            for idx, tar in enumerate(datos["tareas"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{tar['nombre']} [{tar['prioridad']}]")
                if c2.button("🗑️", key=f"dt_{idx}"):
                    datos["tareas"].pop(idx)
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Tarea borrada.", "icono": "🗑️"}
                    st.rerun()

        with st.expander("📅 Caducidades"):
            ne = st.text_input("Elemento:", key="in_cad")
            fc = st.date_input("Caducidad:", value=date.today(), key="da_cad")
            if st.button("Añadir", key="bt_cad"):
                if ne:
                    datos["caducidades_puras"].append({"elemento": ne, "fecha_caducidad": fc.strftime("%Y-%m-%d")})
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Caducidad añadida.", "icono": "✅"}
                    st.rerun()
            st.write("**Actuales:**")
            for idx, item in enumerate(datos["caducidades_puras"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{item['elemento']} ({item['fecha_caducidad']})")
                if c2.button("🗑️", key=f"dc_{idx}"):
                    datos["caducidades_puras"].pop(idx)
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Caducidad borrada.", "icono": "🗑️"}
                    st.rerun()

        with st.expander("🔧 Mantenimientos"):
            nm = st.text_input("Mantenimiento:", key="in_maint")
            ih = st.number_input("Horas:", value=100, key="nu_h")
            im = st.number_input("Meses:", value=12, key="nu_m")
            fl_inicial = st.date_input("Primera fecha límite tope:", value=date.today() + timedelta(days=365), key="nu_fl")
            if st.button("Guardar", key="bt_maint"):
                if nm:
                    datos["mantenimientos_mixtos"].append({
                        "elemento": nm, 
                        "intervalo_horas": ih, 
                        "ultima_vez_horas": horas_actuales, 
                        "intervalo_meses": im, 
                        "ultima_vez_fecha": hoy.strftime("%Y-%m-%d"),
                        "proxima_fecha": fl_inicial.strftime("%Y-%m-%d")
                    })
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Mantenimiento guardado.", "icono": "✅"}
                    st.rerun()
            st.write("**Actuales:**")
            for idx, maint in enumerate(datos["mantenimientos_mixtos"]):
                c1, c2 = st.columns([4, 1])
                st.write(f"{maint['elemento']} ({maint['intervalo_horas']}h/{maint['intervalo_meses']}m)")
                if c2.button("🗑️", key=f"dm_{idx}"):
                    datos["mantenimientos_mixtos"].pop(idx)
                    guardar_datos_nube(datos)
                    st.session_state["toast_msg"] = {"texto": "Mantenimiento borrado.", "icono": "🗑️"}
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
                if c2.button("🗑️", key=f"ds_{idx}"): datos["checklist_salida"].pop(idx); guardar_datos_nube(datos); st.session_state["toast_msg"] = {"texto": "Elemento borrado.", "icono": "🗑️"}; st.rerun()
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
                if c2.button("🗑️", key=f"de_{idx}"): datos["checklist_entrada"].pop(idx); guardar_datos_nube(datos); st.session_state["toast_msg"] = {"texto": "Elemento borrado.", "icono": "🗑️"}; st.rerun()

        st.markdown("---")
        
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
                        st.session_state["toast_msg"] = {"texto": "Socio eliminado.", "icono": "🗑️"}
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
                    st.session_state["toast_msg"] = {"texto": f"¡Bienvenido a la tripulación, {nsn}!", "icono": "✅"}
                    st.rerun()
