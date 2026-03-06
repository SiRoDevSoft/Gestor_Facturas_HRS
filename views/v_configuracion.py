import streamlit as st
import pandas as pd
import json
import os
from time import sleep

def render_configuracion():
    st.header("Gestión de Flota e Integridad de Datos")
    
    ruta_json = os.path.join("json", "config_lineas.json")
    PATH_MARGEN = os.path.join("json", "config_margen.json")
    # Nueva ruta para los mapeos dinámicos
    PATH_MAPEOS = os.path.join("json", "mapeos.json")

    def cargar_config():
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        
    def guardar_config(nueva_config):
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(nueva_config, f, indent=4)
        return True
    
    def leer_margen():
        try:
            with open(PATH_MARGEN, "r", encoding='utf-8') as f:
                return json.load(f).get("margen_actual", 18.0)
        except FileNotFoundError:
            return 18.0

    def guardar_margen(nuevo_margen):
        with open(PATH_MARGEN, "w", encoding='utf-8') as f:
            json.dump({"margen_actual": nuevo_margen}, f)

    # --- NUEVA FUNCIÓN PARA MAPEOS ---
    def cargar_mapeos():
        try:
            with open(PATH_MAPEOS, "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback por si el archivo no existe
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

        # --- MEJORA: Listados desde JSON ---
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

        # Formulario de edición
        with st.form("form_linea"):
            col1, col2 = st.columns(2)
            with col1:
                linea_f = st.text_input("Número de Línea (10 dígitos)", value=l_sug, disabled=edit_mode)
                nombre_f = st.text_input("Nombre del Responsable / Uso", value=n_sug)
            
            with col2:
                # Selector de Grupo
                idx_g = GRUPOS_VALIDOS.index(g_sug) if g_sug in GRUPOS_VALIDOS else 0
                grupo_f = st.selectbox("Asignar a Grupo (Facturación)", GRUPOS_VALIDOS, index=idx_g)
                
                # Selector de Categoría
                idx_c = CATEGORIAS_VALIDAS.index(c_sug) if c_sug in CATEGORIAS_VALIDAS else 0
                cat_f = st.selectbox("Asignar a Categoría (Uso)", CATEGORIAS_VALIDAS, index=idx_c)

            submitted = st.form_submit_button("💾 GUARDAR CAMBIOS", type="primary")
            
            if submitted:
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
                    st.error("El número de línea y el nombre son obligatorios.")

    with tab2:
        st.subheader("📋 Estado Actual de la Flota")
        if config:
            datos_tabla = [
                {
                    "Línea": k, 
                    "Nombre": v.get("nombre"), 
                    "Grupo": v.get("grupo"), 
                    "Categoría": v.get("categoria")
                } for k, v in config.items()
            ]
            df_c = pd.DataFrame(datos_tabla)
            st.dataframe(df_c.sort_values("Nombre"), use_container_width=True, hide_index=True)
        else:
            st.info("No hay líneas configuradas.")
    st.divider()
    
    st.divider()
        
  # --- SECCIÓN C: GESTIÓN DE LISTADOS MAESTROS (En Sidebar con BAJAS) ---
    with st.sidebar:
        st.divider()
        st.subheader("Gestion de Grupos y Categorias")
        
        # --- GESTIÓN DE GRUPOS ---
        with st.expander("Grupos de Facturacion", expanded=False):
            # Alta
            nuevo_g = st.text_input("Anadir Nuevo Grupo", placeholder="Ej: SUC. BALLOFET", key="add_g")
            if st.button("Agregar Grupo", use_container_width=True):
                if nuevo_g:
                    nombre_g = nuevo_g.strip().upper()
                    if nombre_g not in mapeos["GRUPOS_VALIDOS"]:
                        mapeos["GRUPOS_VALIDOS"].append(nombre_g)
                        with open(PATH_MAPEOS, "w", encoding='utf-8') as f:
                            json.dump(mapeos, f, indent=4)
                        st.success(f"✅ Grupo {nombre_g} añadido")
                        sleep(1)
                        st.rerun()
            
            st.write("---")
            # Baja
            grupo_a_borrar = st.selectbox("Eliminar Grupo", ["Seleccionar..."] + mapeos["GRUPOS_VALIDOS"], key="del_g")
            if grupo_a_borrar != "Seleccionar...":
                if st.button(f"Eliminar {grupo_a_borrar}", type="secondary", use_container_width=True):
                    mapeos["GRUPOS_VALIDOS"].remove(grupo_a_borrar)
                    with open(PATH_MAPEOS, "w", encoding='utf-8') as f:
                        json.dump(mapeos, f, indent=4)
                    st.warning(f"⚠️ Grupo {grupo_a_borrar} eliminado")
                    sleep(1)
                    st.rerun()

        # --- GESTIÓN DE CATEGORÍAS ---
        with st.expander("Categorias de Usuarios", expanded=False):
            # Alta
            nueva_c = st.text_input("Anadir Nueva Categoria", placeholder="Ej: REPARTO", key="add_c")
            if st.button("Agregar Categoria", use_container_width=True):
                if nueva_c:
                    nombre_c = nueva_c.strip().upper()
                    if nombre_c not in mapeos["CATEGORIAS_VALIDAS"]:
                        mapeos["CATEGORIAS_VALIDAS"].append(nombre_c)
                        with open(PATH_MAPEOS, "w", encoding='utf-8') as f:
                            json.dump(mapeos, f, indent=4)
                        st.success(f"✅ Categoria {nombre_c} añadida")
                        sleep(1)
                        st.rerun()

            st.write("---")
            # Baja
            cat_a_borrar = st.selectbox("Eliminar Categoria", ["Seleccionar..."] + mapeos["CATEGORIAS_VALIDAS"], key="del_c")
            if cat_a_borrar != "Seleccionar...":
                if st.button(f"Eliminar {cat_a_borrar}", type="secondary", use_container_width=True):
                    mapeos["CATEGORIAS_VALIDAS"].remove(cat_a_borrar)
                    with open(PATH_MAPEOS, "w", encoding='utf-8') as f:
                        json.dump(mapeos, f, indent=4)
                    st.warning(f"⚠️ Categoria {cat_a_borrar} eliminada")
                    sleep(1)
                    st.rerun()
        
        st.divider()

           