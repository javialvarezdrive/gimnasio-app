import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import database as db
from config import APP_NAME

# Configuración de la página
st.set_page_config(
    page_title=APP_NAME,
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para inicializar el estado de la sesión
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

# Inicializar el estado de la sesión
init_session_state()

# Función para mostrar la página de inicio de sesión
def show_login():
    st.title("Acceso al Sistema")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")
            
            if submit:
                usuario = db.verify_credenciales(email, password)
                if usuario:
                    st.session_state.logged_in = True
                    st.session_state.usuario = usuario
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Inténtelo de nuevo.")

# Función para mostrar el panel de control
def show_dashboard():
    st.title(f"Panel de Control - {st.session_state.usuario['nombre']} {st.session_state.usuario['apellidos']}")
    
    # Menú lateral
    with st.sidebar:
        st.subheader("Menú")
        page = st.radio(
            "Ir a:",
            ["Dashboard", "Gestión de Miembros", "Agendar Actividad", "Registro de Actividades", "Estadísticas", "Configuración"]
        )
        
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.usuario = None
            st.session_state.current_page = "login"
            st.rerun()
    
    # Mostrar la página seleccionada
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Gestión de Miembros":
        show_miembros_page()
    elif page == "Agendar Actividad":
        show_agendar_actividad_page()
    elif page == "Registro de Actividades":
        show_registro_actividades_page()
    elif page == "Estadísticas":
        show_estadisticas_page()
    elif page == "Configuración":
        show_configuracion_page()

# Función para mostrar el dashboard principal
def show_dashboard_page():
    st.header("Dashboard")
    
    # Obtener datos para el dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Actividades recientes
        st.subheader("Actividades Recientes")
        actividades_recientes = db.get_registro_actividades(
            fecha_inicio=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            fecha_fin=datetime.now().strftime("%Y-%m-%d")
        )
        
        if actividades_recientes:
            df_recientes = pd.DataFrame([{
                "Fecha": a["fecha"],
                "Miembro": f"{a['miembros']['nombre']} {a['miembros']['apellidos']}",
                "Actividad": a["actividades"]["nombre"],
                "Turno": a["turnos"]["nombre"]
            } for a in actividades_recientes])
            
            st.dataframe(df_recientes, use_container_width=True)
        else:
            st.info("No hay actividades recientes")
    
    with col2:
        # Miembros sin actividades recientes
        st.subheader("Miembros sin Actividades Recientes")
        sin_actividades = db.get_estadisticas_miembros_sin_actividades(
            fecha_inicio=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            fecha_fin=datetime.now().strftime("%Y-%m-%d")
        )
        
        if not sin_actividades.empty:
            st.dataframe(
                sin_actividades[["nip", "nombre", "apellidos", "seccion", "grupo"]],
                use_container_width=True
            )
        else:
            st.info("Todos los miembros han realizado actividades en los últimos 30 días")
    
    # Gráficas resumen
    st.subheader("Resumen de Actividades")
    col1, col2 = st.columns(2)
    
    # Obtener datos para las gráficas
    est_seccion = db.get_estadisticas_actividades_por_seccion(
        fecha_inicio=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        fecha_fin=datetime.now().strftime("%Y-%m-%d")
    )
    
    est_grupo = db.get_estadisticas_actividades_por_grupo(
        fecha_inicio=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        fecha_fin=datetime.now().strftime("%Y-%m-%d")
    )
    
    with col1:
        if not est_seccion.empty:
            fig = px.bar(
                est_seccion,
                x="seccion",
                y="total",
                color="actividad",
                title="Actividades por Sección (Últimos 30 días)",
                labels={"seccion": "Sección", "total": "Total de Actividades", "actividad": "Tipo de Actividad"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para la gráfica")
    
    with col2:
        if not est_grupo.empty:
            fig = px.bar(
                est_grupo,
                x="grupo",
                y="total",
                color="actividad",
                title="Actividades por Grupo (Últimos 30 días)",
                labels={"grupo": "Grupo", "total": "Total de Actividades", "actividad": "Tipo de Actividad"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para la gráfica")

# Función para mostrar la gestión de miembros
def show_miembros_page():
    st.header("Gestión de Miembros")
    
    tab1, tab2 = st.tabs(["Lista de Miembros", "Añadir/Editar Miembro"])
    
    with tab1:
        # Obtener todos los miembros
        miembros = db.get_miembros()
        
        if miembros:
            df_miembros = pd.DataFrame([{
                "ID": m["id"],
                "NIP": m["nip"],
                "Nombre": m["nombre"],
                "Apellidos": m["apellidos"],
                "Sección": m["secciones"]["nombre"],
                "Grupo": m["grupos"]["nombre"],
                "Acciones": m["id"]
            } for m in miembros])
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_seccion = st.selectbox(
                    "Filtrar por Sección",
                    ["Todos"] + list(df_miembros["Sección"].unique()),
                    key="filtro_seccion_miembros"
                )
            
            with col2:
                filtro_grupo = st.selectbox(
                    "Filtrar por Grupo",
                    ["Todos"] + list(df_miembros["Grupo"].unique()),
                    key="filtro_grupo_miembros"
                )
            
            with col3:
                filtro_nombre = st.text_input("Buscar por nombre o apellido", key="filtro_nombre_miembros")
            
            # Aplicar filtros
            df_filtrado = df_miembros.copy()
            
            if filtro_seccion != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Sección"] == filtro_seccion]
            
            if filtro_grupo != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Grupo"] == filtro_grupo]
            
            if filtro_nombre:
                filtro_nombre = filtro_nombre.lower()
                df_filtrado = df_filtrado[
                    df_filtrado["Nombre"].str.lower().str.contains(filtro_nombre) |
                    df_filtrado["Apellidos"].str.lower().str.contains(filtro_nombre)
                ]
            
            # Mostrar la tabla
            st.dataframe(df_filtrado.drop(columns=["ID", "Acciones"]), use_container_width=True)
            
            # Selección para editar/eliminar
            col1, col2 = st.columns(2)
            
            with col1:
                miembro_seleccionado = st.selectbox(
                    "Seleccionar miembro para editar/eliminar",
                    df_filtrado["ID"].tolist(),
                    format_func=lambda x: f"{df_miembros[df_miembros['ID'] == x].iloc[0]['NIP']} - {df_miembros[df_miembros['ID'] == x].iloc[0]['Nombre']} {df_miembros[df_miembros['ID'] == x].iloc[0]['Apellidos']}"
                )
            
            with col2:
                accion = st.radio("Acción", ["Editar", "Eliminar"], horizontal=True)
                
                if st.button("Ejecutar"):
                    if accion == "Editar":
                        # Guardar el ID del miembro para editar
                        st.session_state.miembro_editar = miembro_seleccionado
                        st.rerun()
                    else:  # Eliminar
                        db.delete_miembro(miembro_seleccionado)
                        st.success("Miembro eliminado correctamente")
                        st.rerun()
        else:
            st.info("No hay miembros registrados")
    
    with tab2:
        # Obtener secciones y grupos para los selectores
        secciones = db.get_secciones()
        grupos = db.get_grupos()
        
        # Verificar si estamos editando un miembro existente
        miembro_editar = None
        if hasattr(st.session_state, 'miembro_editar'):
            miembro_id = st.session_state.miembro_editar
            for m in miembros:
                if m["id"] == miembro_id:
                    miembro_editar = m
                    break
        
        st.subheader("Añadir Nuevo Miembro" if not miembro_editar else "Editar Miembro")
        
        with st.form("miembro_form"):
            nip = st.number_input(
                "NIP", 
                min_value=1, 
                value=miembro_editar["nip"] if miembro_editar else 1,
                step=1
            )
            
            nombre = st.text_input(
                "Nombre", 
                value=miembro_editar["nombre"] if miembro_editar else ""
            )
            
            apellidos = st.text_input(
                "Apellidos", 
                value=miembro_editar["apellidos"] if miembro_editar else ""
            )
            
            seccion_id = st.selectbox(
                "Sección",
                options=[s["id"] for s in secciones],
                format_func=lambda x: next((s["nombre"] for s in secciones if s["id"] == x), ""),
                index=next((i for i, s in enumerate(secciones) if s["id"] == miembro_editar["secciones"]["id"]), 0) if miembro_editar else 0
            )
            
            grupo_id = st.selectbox(
                "Grupo",
                options=[g["id"] for g in grupos],
                format_func=lambda x: next((g["nombre"] for g in grupos if g["id"] == x), ""),
                index=next((i for i, g in enumerate(grupos) if g["id"] == miembro_editar["grupos"]["id"]), 0) if miembro_editar else 0
            )
            
            submit_button = st.form_submit_button("Guardar")
            
            if submit_button:
                if miembro_editar:
                    # Actualizar miembro existente
                    db.update_miembro(miembro_editar["id"], nip, nombre, apellidos, seccion_id, grupo_id)
                    st.success("Miembro actualizado correctamente")
                    # Limpiar la variable de sesión
                    if hasattr(st.session_state, 'miembro_editar'):
                        del st.session_state.miembro_editar
                else:
                    # Añadir nuevo miembro
                    db.add_miembro(nip, nombre, apellidos, seccion_id, grupo_id)
                    st.success("Miembro añadido correctamente")
                
                st.rerun()

# Función para mostrar el formulario de agendar actividad
def show_agendar_actividad_page():
    st.header("Agendar Actividad")
    
    # Obtener datos necesarios
    miembros = db.get_miembros()
    actividades = db.get_actividades()
    turnos = db.get_turnos()
    
    # Formulario para agendar actividad
    with st.form("agendar_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", value=datetime.now())
            
            turno_id = st.selectbox(
                "Turno",
                options=[t["id"] for t in turnos],
                format_func=lambda x: next((t["nombre"] for t in turnos if t["id"] == x), "")
            )
            
            actividad_id = st.selectbox(
                "Actividad",
                options=[a["id"] for a in actividades],
                format_func=lambda x: next((a["nombre"] for a in actividades if a["id"] == x), "")
            )
        
        with col2:
            # Filtros para miembros
            filtro_seccion = st.selectbox(
                "Filtrar por Sección",
                ["Todos"] + list(set([m["secciones"]["nombre"] for m in miembros]))
            )
            
            filtro_grupo = st.selectbox(
                "Filtrar por Grupo",
                ["Todos"] + list(set([m["grupos"]["nombre"] for m in miembros]))
            )
            
            # Aplicar filtros
            miembros_filtrados = miembros.copy()
            
            if filtro_seccion != "Todos":
                miembros_filtrados = [m for m in miembros_filtrados if m["secciones"]["nombre"] == filtro_seccion]
            
            if filtro_grupo != "Todos":
                miembros_filtrados = [m for m in miembros_filtrados if m["grupos"]["nombre"] == filtro_grupo]
            
            # Selector de miembros
            miembro_id = st.selectbox(
                "Miembro",
                options=[m["id"] for m in miembros_filtrados],
                format_func=lambda x: next((f"{m['nip']} - {m['nombre']} {m['apellidos']}" for m in miembros_filtrados if m["id"] == x), "")
            )
        
        observaciones = st.text_area("Observaciones")
        
        submit_button = st.form_submit_button("Agendar Actividad")
        
        if submit_button:
            # Guardar el registro
            db.add_registro_actividad(
                miembro_id=miembro_id,
                actividad_id=actividad_id,
                fecha=fecha.strftime("%Y-%m-%d"),
                turno_id=turno_id,
                monitor_id=st.session_state.usuario["id"],
                observaciones=observaciones
            )
            
            st.success("Actividad agendada correctamente")
            st.rerun()
    
    # Mostrar actividades agendadas para el día
    st.subheader("Actividades Agendadas")
    
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime.now())
    fecha_fin = st.date_input("Fecha de fin", value=datetime.now() + timedelta(days=7))
    
    if fecha_inicio and fecha_fin:
        actividades_agendadas = db.get_registro_actividades(
            fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin=fecha_fin.strftime("%Y-%m-%d")
        )
        
        if actividades_agendadas:
            df_agendadas = pd.DataFrame([{
                "Fecha": a["fecha"],
                "Miembro": f"{a['miembros']['nip']} - {a['miembros']['nombre']} {a['miembros']['apellidos']}",
                "Actividad": a["actividades"]["nombre"],
                "Turno": a["turnos"]["nombre"],
                "Monitor": f"{a['monitores']['nombre']} {a['monitores']['apellidos']}",
                "Observaciones": a["observaciones"] or ""
            } for a in actividades_agendadas])
            
            st.dataframe(df_agendadas, use_container_width=True)
        else:
            st.info("No hay actividades agendadas para el período seleccionado")

# Función para mostrar el registro de actividades
def show_registro_actividades_page():
    st.header("Registro de Actividades")
    
    # Obtener datos necesarios
    miembros = db.get_miembros()
    actividades = db.get_actividades()
    turnos = db.get_turnos()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime.now() - timedelta(days=30))
    
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime.now())
    
    with col3:
        filtro_actividad = st.selectbox(
            "Filtrar por Actividad",
            ["Todas"] + [a["nombre"] for a in actividades],
            key="filtro_actividad_registro"
        )
    
    # Más filtros en otra fila
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_turno = st.selectbox(
            "Filtrar por Turno",
            ["Todos"] + [t["nombre"] for t in turnos],
            key="filtro_turno_registro"
        )
    
    with col2:
        filtro_seccion = st.selectbox(
            "Filtrar por Sección",
            ["Todas"] + list(set([m["secciones"]["nombre"] for m in miembros])),
            key="filtro_seccion_registro"
        )
    
    with col3:
        filtro_grupo = st.selectbox(
            "Filtrar por Grupo",
            ["Todos"] + list(set([m["grupos"]["nombre"] for m in miembros])),
            key="filtro_grupo_registro"
        )
    
    # Obtener registros
    registros = db.get_registro_actividades(
        fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=fecha_fin.strftime("%Y-%m-%d")
    )
    
    if registros:
        df_registros = pd.DataFrame([{
            "ID": r["id"],
            "Fecha": r["fecha"],
            "NIP": r["miembros"]["nip"],
            "Miembro": f"{r['miembros']['nombre']} {r['miembros']['apellidos']}",
            "Actividad": r["actividades"]["nombre"],
            "Turno": r["turnos"]["nombre"],
            "Monitor": f"{r['monitores']['nombre']} {r['monitores']['apellidos']}",
            "Observaciones": r["observaciones"] or ""
        } for r in registros])
        
        # Aplicar filtros adicionales
        if filtro_actividad != "Todas":
            df_registros = df_registros[df_registros["Actividad"] == filtro_actividad]
        
        if filtro_turno != "Todos":
            df_registros = df_registros[df_registros["Turno"] == filtro_turno]
        
        # Filtros de sección y grupo requieren unir con los datos de miembros
        if filtro_seccion != "Todas" or filtro_grupo != "Todos":
            df_miembros = pd.DataFrame([{
                "NIP": m["nip"],
                "Seccion": m["secciones"]["nombre"],
                "Grupo": m["grupos"]["nombre"]
            } for m in miembros])
            
            df_registros = df_registros.merge(df_miembros, on="NIP", how="left")
            
            if filtro_seccion != "Todas":
                df_registros = df_registros[df_registros["Seccion"] == filtro_seccion]
            
            if filtro_grupo != "Todos":
                df_registros = df_registros[df_registros["Grupo"] == filtro_grupo]
            
            # Eliminar columnas adicionales
            df_registros = df_registros.drop(columns=["Seccion", "Grupo"])
        
        # Mostrar resultados
        st.dataframe(df_registros.drop(columns=["ID"]), use_container_width=True)
        
        # Descargar datos
        csv = df_registros.drop(columns=["ID"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=f"registro_actividades_{fecha_inicio}_a_{fecha_fin}.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay registros para el período y filtros seleccionados")

# Función para mostrar estadísticas
def show_estadisticas_page():
    st.header("Estadísticas")
    
    # Selección de período
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime.now() - timedelta(days=30))
    
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime.now())
    
    # Obtener datos para las estadísticas
    est_seccion = db.get_estadisticas_actividades_por_seccion(
        fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=fecha_fin.strftime("%Y-%m-%d")
    )
    
    est_grupo = db.get_estadisticas_actividades_por_grupo(
        fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=fecha_fin.strftime("%Y-%m-%d")
    )
    
    sin_actividades = db.get_estadisticas_miembros_sin_actividades(
        fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=fecha_fin.strftime("%Y-%m-%d")
    )
    
    # Mostrar gráficas
    tab1, tab2, tab3 = st.tabs(["Por Sección", "Por Grupo", "Miembros sin Actividades"])
    
    with tab1:
        if not est_seccion.empty:
            # Gráfica de barras
            fig_bar = px.bar(
                est_seccion,
                x="seccion",
                y="total",
                color="actividad",
                title="Actividades por Sección",
                labels={"seccion": "Sección", "total": "Total de Actividades", "actividad": "Tipo de Actividad"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfica de pastel
            fig_pie = px.pie(
                est_seccion,
                values="total",
                names="seccion",
                title="Distribución de Actividades por Sección"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay datos suficientes para las gráficas")
    
    with tab2:
        if not est_grupo.empty:
            # Gráfica de barras
            fig_bar = px.bar(
                est_grupo,
                x="grupo",
                y="total",
                color="actividad",
                title="Actividades por Grupo",
                labels={"grupo": "Grupo", "total": "Total de Actividades", "actividad": "Tipo de Actividad"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfica de pastel
            fig_pie = px.pie(
                est_grupo,
                values="total",
                names="grupo",
                title="Distribución de Actividades por Grupo"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay datos suficientes para las gráficas")
    
    with tab3:
        if not sin_actividades.empty:
            st.subheader(f"Miembros sin Actividades ({len(sin_actividades)})")
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                filtro_seccion = st.selectbox(
                    "Filtrar por Sección",
                    ["Todas"] + list(sin_actividades["seccion"].unique())
                )
            
            with col2:
                filtro_grupo = st.selectbox(
                    "Filtrar por Grupo",
                    ["Todos"] + list(sin_actividades["grupo"].unique())
                )
            
            # Aplicar filtros
            df_filtrado = sin_actividades.copy()
            
            if filtro_seccion != "Todas":
                df_filtrado = df_filtrado[df_filtrado["seccion"] == filtro_seccion]
            
            if filtro_grupo != "Todos":
                df_filtrado = df_filtrado[df_filtrado["grupo"] == filtro_grupo]
            
            # Mostrar tabla
            st.dataframe(df_filtrado[["nip", "nombre", "apellidos", "seccion", "grupo"]], use_container_width=True)
            
            # Gráfica de miembros sin actividades por sección y grupo
            fig = px.bar(
                df_filtrado.groupby(["seccion", "grupo"]).size().reset_index(name="total"),
                x="seccion",
                y="total",
                color="grupo",
                title="Miembros sin Actividades por Sección y Grupo",
                labels={"seccion": "Sección", "total": "Total de Miembros", "grupo": "Grupo"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("¡Todos los miembros han realizado actividades en el período seleccionado!")

# Función para mostrar configuración
def show_configuracion_page():
    st.header("Configuración")
    
    tab1, tab2 = st.tabs(["Actividades", "Monitores"])
    
    with tab1:
        st.subheader("Gestión de Actividades")
        
        # Lista de actividades
        actividades = db.get_actividades()
        
        if actividades:
            st.dataframe(
                pd.DataFrame([{
                    "Nombre": a["nombre"],
                    "Descripción": a["descripcion"] or ""
                } for a in actividades]),
                use_container_width=True
            )
        else:
            st.info("No hay actividades registradas")
        
        # Formulario para añadir actividad
        st.subheader("Añadir Nueva Actividad")
        
        with st.form("actividad_form"):
            nombre_actividad = st.text_input("Nombre")
            descripcion_actividad = st.text_area("Descripción")
            
            submit = st.form_submit_button("Guardar")
            
            if submit:
                db.add_actividad(nombre_actividad, descripcion_actividad)
                st.success("Actividad añadida correctamente")
                st.rerun()
    
    with tab2:
        st.subheader("Gestión de Monitores")
        st.info("Funcionalidad en desarrollo...")

# Función principal
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

