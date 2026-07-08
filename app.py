import streamlit as st
import json
import os
from datetime import datetime, date, timedelta

# Configuración de la página móvil/web
st.set_page_config(page_title="Gestión del Barco", page_icon="⛵", layout="centered")

# Archivo local para simular la base de datos de forma limpia y rápida
ARCHIVO_DATOS = "datos_barco.json"

# Datos iniciales por defecto si el archivo no existe
def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        datos_iniciales = {
            "socios": ["Amigo 1", "Amigo 2", "Amigo 3", "Amigo 4", "Amigo 5"],
            "horas_motor": 120,
            "mantenimientos": [
                {"elemento": "Aceite y Filtro de Motor", "intervalo_horas": 100, "ultima_vez_horas": 100, "tipo": "horas"},
                {"elemento": "Ánodos de Sacrificio", "intervalo_meses": 12, "ultima_vez_fecha": "2025-06-01", "tipo": "fecha"},
                {"elemento": "Rodete de Bomba (Impeller)", "intervalo_horas": 200, "ultima_vez_horas": 50, "tipo": "horas"},
                {"elemento": "Inspección Técnica (ITB)", "intervalo_meses": 60, "ultima_vez_fecha": "2024-01-01", "tipo": "fecha"}
            ],
            "bricos": [
                {"nombre": "Reparar luz de fondeo", "prioridad": "Alta", "hecho": False},
                {"nombre": "Lijar mesa de la bañera", "prioridad": "Baja", "hecho": False}
            ],
            "historial": [
                {"fecha": "2026-07-01", "usuario": "Sistema", "evento": "App iniciada desde cero", "horas": 120}
            ]
        }
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos_iniciales, f, indent=4, ensure_ascii=False)

inicializar_datos()

# Cargar y guardar datos
def cargar_datos():
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

datos = cargar_datos()
hoy = date.today()

# --- CONTROL DE ACCESO (PANTALLA PRINCIPAL) ---
if "socio_activo" not in st.session_state:
    st.session_state["socio_activo"] = None

if st.session_state["socio_activo"] is None:
    st.title("⚓ Gestión del Barco")
    st.markdown("---")
    st.subheader("👤 ¿Quién va a entrar a la aplicación?")
    
    # Selector de los 5 amigos
    socio_elegido = st.selectbox("Selecciona tu nombre:", datos["socios"])
    
    if st.button("🚀 Entrar a la App", use_container_width=True):
        st.session_state["socio_activo"] = socio_elegido
        st.rerun()

# --- APLICACIÓN UNA VEZ IDENTIFICADO ---
else:
    socio_actual = st.session_state["socio_activo"]
    
    # Barra lateral para saber quién está dentro y poder cambiar de usuario
    st.sidebar.title("⛵ El Barco")
    st.sidebar.markdown(f"Tripulante: **{socio_actual}**")
    if st.sidebar.button("🚪 Cerrar Sesión / Cambiar"):
        st.session_state["socio_activo"] = None
        st.rerun()
    st.sidebar.markdown("---")
    
    st.title("⚓ Panel de Control")
    
    # Pestañas de navegación de la app
    tab1, tab2, tab3 = st.tabs(["📊 Estado y Motor", "🔧 Bricos / Tareas", "📜 Historial"])
    
    # PESTAÑA 1: MOTOR Y MANTENIMIENTOS
    with tab1:
        st.header("⏱️ Horas de Motor")
        st.metric(label="Horas Actuales", value=f"{datos['horas_motor']} hrs")
        
        # Formulario rápido para actualizar horas
        with st.expander("📝 Actualizar horas de motor"):
            nuevas_horas = st.number_input("Introduce las nuevas horas:", min_value=datos["horas_motor"], value=datos["horas_motor"])
            if st.button("Guardar Horas"):
                if nuevas_horas > datos["horas_motor"]:
                    datos["historial"].append({
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "usuario": socio_actual,
                        "evento": f"Actualizó el motor de {datos['horas_motor']}h a {nuevas_horas}h",
                        "horas": nuevas_horas
                    })
                    datos["horas_motor"] = nuevas_horas
                    guardar_datos(datos)
                    st.success("Horas actualizadas correctamente.")
                    st.rerun()

        st.markdown("---")
        st.header("🔧 Próximos Mantenimientos")
        
        for i, maint in enumerate(datos["mantenimientos"]):
            col_info, col_accion = st.columns([3, 1])
            
            with col_info:
                if maint["tipo"] == "horas":
                    horas_desde_ultimo = datos["horas_motor"] - maint["ultima_vez_horas"]
                    horas_restantes = maint["intervalo_horas"] - horas_desde_ultimo
                    st.write(f"**{maint['elemento']}**")
                    if horas_restantes <= 0:
                        st.error(f"🔴 VENCIDO (Hace {abs(horas_restantes)} horas)")
                    elif horas_restantes <= 15:
                        st.warning(f"🟡 Toca pronto (Quedan {horas_restantes} horas)")
                    else:
                        st.success(f"🟢 OK (Quedan {horas_restantes} horas)")
                        
                elif maint["tipo"] == "fecha":
                    ultima_fecha = datetime.strptime(maint["ultima_vez_fecha"], "%Y-%m-%d").date()
                    # Estimación simple de meses agregando días
                    fecha_vencimiento = ultima_fecha + timedelta(days=maint["intervalo_meses"] * 30)
                    dias_restantes = (fecha_vencimiento - hoy).days
                    st.write(f"**{maint['elemento']}**")
                    if dias_restantes <= 0:
                        st.error(f"🔴 VENCIDO (Venció el {fecha_vencimiento.strftime('%d/%m/%Y')})")
                    elif dias_restantes <= 30:
                        st.warning(f"🟡 Caduca pronto (Quedan {dias_restantes} días)")
                    else:
                        st.success(f"🟢 OK (Caduca el {fecha_vencimiento.strftime('%d/%m/%Y')})")
            
            with col_accion:
                if st.button("✅ Hecho", key=f"maint_{i}"):
                    if maint["tipo"] == "horas":
                        maint["ultima_vez_horas"] = datos["horas_motor"]
                        evento_txt = f"Realizó mantenimiento: {maint['elemento']}"
                    else:
                        maint["ultima_vez_fecha"] = hoy.strftime("%Y-%m-%d")
                        evento_txt = f"Renovó/Revisó por fecha: {maint['elemento']}"
                        
                    datos["historial"].append({
                        "fecha": hoy.strftime("%Y-%m-%d"),
                        "usuario": socio_actual,
                        "evento": evento_txt,
                        "horas": datos["horas_motor"]
                    })
                    guardar_datos(datos)
                    st.rerun()
            st.markdown("---")

    # PESTAÑA 2: BRICOS
    with tab2:
        st.header("📋 Lista de Bricos")
        
        # Añadir nuevo brico
        with st.expander("➕ Añadir nueva tarea"):
            nuevo_brico_nombre = st.text_input("¿Qué hay que hacer?")
            nueva_prio = st.selectbox("Prioridad:", ["Alta", "Media", "Baja"])
            if st.button("Agregar Brico"):
                if nuevo_brico_nombre:
                    datos["bricos"].append({"nombre": nuevo_brico_nombre, "prioridad": nueva_prio, "hecho": False})
                    guardar_datos(datos)
                    st.rerun()
                    
        st.markdown("---")
        # Mostrar bricos activos
        for idx, brico in enumerate(datos["bricos"]):
            if not brico["hecho"]:
                cb1, cb2 = st.columns([3, 1])
                with cb1:
                    st.write(f"🔹 **{brico['nombre']}**")
                    st.caption(f"Prioridad: {brico['prioridad']}")
                with cb2:
                    if st.button("💥 Hecho", key=f"brico_{idx}"):
                        brico["hecho"] = True
                        datos["historial"].append({
                            "fecha": hoy.strftime("%Y-%m-%d"),
                            "usuario": socio_actual,
                            "evento": f"Completó el brico: {brico['nombre']}",
                            "horas": datos["horas_motor"]
                        })
                        guardar_datos(datos)
                        st.rerun()

    # PESTAÑA 3: HISTORIAL
    with tab3:
        st.header("📜 Historial de Actividad")
        for log in reversed(datos["historial"]):
            st.markdown(f"**[{log['fecha']}]** - **{log['usuario']}**: {log['evento']} *(Con {log['horas']} hrs)*")
            st.markdown("---")
