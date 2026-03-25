import streamlit as st
import pandas as pd
import json
import os
from time import sleep
from models.auth_db import AuthManager

def render_configuracion():
    st.header("Gestión de Flota e Integridad de Datos")
    
    # --- CONFIGURACIÓN DE RUTAS ---
    ruta_json = os.path.join("json", "config_lineas.json")
    PATH_MARGEN = os.path.join("json", "config_margen.json")
    PATH_MAPEOS = os.path.join("json", "mapeos.json")
    auth = AuthManager()

    # --- FUNCIONES DE PERSISTENCIA ---
    def cargar_config():
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError: return {}
        
    def guardar_config(nueva_config):
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(nueva_config, f, indent=4)
        return True
    
    def leer_margen():
        try:
            with open(PATH_MARGEN, "r", encoding='utf-8') as f:
                return json.load(f).get("margen_actual", 18.0)
        except FileNotFoundError: return 18.0

    def guardar_margen(nuevo_margen):
        with open(PATH_MARGEN, "w", encoding='utf-8') as f:
            json.dump({"margen_actual": nuevo_margen}, f)

    def cargar_mapeos():
        try:
            with open(PATH_MAPEOS, "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "GRUPOS_VALIDOS": ["EMPRESA", "TERCEROS_HRS"],
                "CATEGORIAS_VALIDAS": ["ADMINISTRACION"]
            }

    config = cargar_config()
    mapeos = cargar_mapeos()

    # --- SECCIÓN A: MARGEN DE LUCRO ---
    st.subheader("Parámetros de Rentabilidad")
    margen_guardado = leer_margen()
    
    col_m, _ = st.columns([1, 2])
    with col_m:
        nuevo_margen = st.number_input(
            "Margen de Recargo General (%)", 
            min_value=0.0, 
            value=float(margen_guardado)
        )
        if nuevo_margen != margen_guardado:
            guardar_margen(nuevo_margen)
            st.success(f"Margen actualizado a {nuevo_margen}%")
    
    st.divider()

    # --- SECCIÓN B: GESTIÓN DE LÍNEAS ---
    tab1, tab2 = st.tabs(["📝 Editor Maestro", "📋 Lista Completa"])

    with tab1:
        opciones = ["+ NUEVA LÍNEA"] + [f"{k} - {v.get('nombre', '')}" for k, v in config.items()]
        seleccion = st.selectbox(
            "Buscar por Número o Nombre", 
            opciones, 
            key=f"selector_{st.session_state.form_version}"
        )

        GRUPOS_VALIDOS = mapeos.get("GRUPOS_VALIDOS", [])
        CATEGORIAS_VALIDAS = mapeos.get("CATEGORIAS_VALIDAS", [])

        if seleccion == "+ NUEVA LÍNEA":
            l_sug, n_sug, g_sug, c_sug, edit_mode = "", "", "EMPRESA", "ADMINISTRACION", False
        else:
            l_sug = seleccion.split(" - ")[0]
            datos = config[l_sug]
            n_sug = datos.get("nombre", "")
            g_sug = datos.get("grupo", "EMPRESA")
            c_sug = datos.get("categoria", "ADMINISTRACION")
            edit_mode = True

        with st.form("form_linea"):
            col1, col2 = st.columns(2)
            with col1:
                linea_f = st.text_input("Número de Línea (10 dígitos)", value=l_sug, disabled=edit_mode)
                nombre_f = st.text_input("Nombre del Responsable / Uso", value=n_sug)
            with col2:
                idx_g = GRUPOS_VALIDOS.index(g_sug) if g_sug in GRUPOS_VALIDOS else 0
                grupo_f = st.selectbox("Asignar a Grupo", GRUPOS_VALIDOS, index=idx_g)
                idx_c = CATEGORIAS_VALIDAS.index(c_sug) if c_sug in CATEGORIAS_VALIDAS else 0
                cat_f = st.selectbox("Asignar a Categoría", CATEGORIAS_VALIDAS, index=idx_c)

            if st.form_submit_button("💾 GUARDAR CAMBIOS", type="primary"):
                if linea_f and nombre_f:
                    config[linea_f] = {
                        "nombre": nombre_f.upper().strip(),
                        "grupo": grupo_f,
                        "categoria": cat_f
                    }
                    if guardar_config(config):
                        st.toast(f"✅ Línea {linea_f} actualizada")
                        st.session_state.form_version += 1
                        sleep(1)
                        st.rerun()
                else:
                    st.error("Datos obligatorios faltantes.")

    with tab2:
        if config:
            datos_tabla = [{"Línea": k, "Nombre": v.get("nombre"), "Grupo": v.get("grupo"), "Categoría": v.get("categoria")} for k, v in config.items()]
            st.dataframe(pd.DataFrame(datos_tabla).sort_values("Nombre"), use_container_width=True, hide_index=True)

    st.divider()

    # # --- SECCIÓN C: GESTIÓN DE USUARIOS (ACCESO AL SISTEMA) ---
    # st.subheader("👤 Administración de Accesos")
    # with st.expander("Registrar Nuevo Usuario", expanded=False):
    #     col_u1, col_u2 = st.columns(2)
    #     with col_u1:
    #         nuevo_u = st.text_input("Nombre de Usuario", key="new_user_name")
    #         nuevo_p = st.text_input("Contraseña", type="password", key="new_user_pass")
    #     with col_u2:
    #         preg_u = st.text_input("Pregunta de Seguridad", key="new_user_preg")
    #         resp_u = st.text_input("Respuesta", key="new_user_resp")
        
    #     if st.button("Crear Cuenta", use_container_width=True):
    #         if all([nuevo_u, nuevo_p, preg_u, resp_u]):
    #             auth.registrar_usuario(nuevo_u, nuevo_p, preg_u, resp_u)
    #             st.success(f"Usuario {nuevo_u} creado correctamente.")
    #         else:
    #             st.warning("Completar todos los campos para el registro.")

    # --- SECCIÓN C: GESTIÓN DE USUARIOS (ACCESO AL SISTEMA) ---
    
    st.subheader("Administración de Accesos")
    
    tab_u1, tab_u2 = st.tabs(["➕ Registrar Nuevo", "🔐 Gestionar Existentes"])

    with tab_u1:
        with st.expander("Formulario de Registro", expanded=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                nuevo_u = st.text_input("Nombre de Usuario", key="new_user_name")
                nuevo_p = st.text_input("Contraseña", type="password", key="new_user_pass")
            with col_u2:
                preg_u = st.text_input("Pregunta de Seguridad", key="new_user_preg")
                resp_u = st.text_input("Respuesta", key="new_user_resp")
            
            if st.button("Crear Cuenta", use_container_width=True, type="primary"):
                if all([nuevo_u, nuevo_p, preg_u, resp_u]):
                    auth.registrar_usuario(nuevo_u, nuevo_p, preg_u, resp_u)
                    st.success(f"Usuario {nuevo_u} creado correctamente.")
                    sleep(1)
                    st.rerun()
                else:
                    st.warning("Completar todos los campos para el registro.")

    with tab_u2:
        lista_users = auth.listar_usuarios()
        if lista_users:
            st.write(f"Total de usuarios: **{len(lista_users)}**")
            
            for user in lista_users:
                # Usamos un container para agrupar visualmente cada fila
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**Usuario:** `{user}`")
                    with c2:
                        # Evitamos que se elimine a sí mismo si tenemos el dato en session_state
                        es_mismo_usuario = st.session_state.get('usuario') == user
                        
                        if st.button("🗑️", key=f"btn_del_{user}", help=f"Eliminar a {user}", disabled=es_mismo_usuario):
                            auth.eliminar_usuario(user)
                            st.toast(f"Usuario {user} eliminado.")
                            sleep(1)
                            st.rerun()
        else:
            st.info("No hay usuarios registrados en el sistema.")



    # --- SIDEBAR: GRUPOS Y CATEGORÍAS ---
    with st.sidebar:
        st.divider()
        st.subheader("Listados Maestros")
        
        with st.expander("Grupos", expanded=False):
            nuevo_g = st.text_input("Nuevo Grupo", key="add_g")
            if st.button("Añadir", key="btn_g"):
                if nuevo_g and nuevo_g.upper() not in mapeos["GRUPOS_VALIDOS"]:
                    mapeos["GRUPOS_VALIDOS"].append(nuevo_g.strip().upper())
                    with open(PATH_MAPEOS, "w", encoding='utf-8') as f: json.dump(mapeos, f, indent=4)
                    st.rerun()
            
            del_g = st.selectbox("Borrar Grupo", ["-"] + mapeos["GRUPOS_VALIDOS"])
            if del_g != "-" and st.button("Eliminar"):
                mapeos["GRUPOS_VALIDOS"].remove(del_g)
                with open(PATH_MAPEOS, "w", encoding='utf-8') as f: json.dump(mapeos, f, indent=4)
                st.rerun()

        with st.expander("Categorías", expanded=False):
            nueva_c = st.text_input("Nueva Categoría", key="add_c")
            if st.button("Añadir", key="btn_c"):
                if nueva_c and nueva_c.upper() not in mapeos["CATEGORIAS_VALIDAS"]:
                    mapeos["CATEGORIAS_VALIDAS"].append(nueva_c.strip().upper())
                    with open(PATH_MAPEOS, "w", encoding='utf-8') as f: json.dump(mapeos, f, indent=4)
                    st.rerun()

            del_c = st.selectbox("Borrar Categoría", ["-"] + mapeos["CATEGORIAS_VALIDAS"])
            if del_c != "-" and st.button("Eliminar", key="del_btn_c"):
                mapeos["CATEGORIAS_VALIDAS"].remove(del_c)
                with open(PATH_MAPEOS, "w", encoding='utf-8') as f: json.dump(mapeos, f, indent=4)
                st.rerun()

           