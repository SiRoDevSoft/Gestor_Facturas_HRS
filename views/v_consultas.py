#########################################################################


# import streamlit as st
# import pandas as pd
# from models.database import DatabaseManager

# def render_consultas():
#     st.header("🔍 Centro de Consultas Históricas")
    
#     db = DatabaseManager()

#     periodos_db = db.get_periodos_disponibles()

#     if not periodos_db:
#         st.info("No se encontraron registros en la base de datos.")
#         return

#     # --- BLOQUE DE FILTROS ---
#     with st.container(border=True):
#         col1, col2, col3 = st.columns([2, 2, 3])
        
#         with col1:
#             # SE ELIMINÓ "TODOS". El selector toma el primer valor (índice 0) por defecto.
#             periodo_sel = st.selectbox("📅 Mes/Período", periodos_db, index=0)
            
#         with col2:
#             grupos_db = db.get_grupos_unicos()
#             # Mantenemos "TODOS" solo para filtrar dentro del mes seleccionado
#             lista_grupos = ["TODOS"] + grupos_db
#             grupo_sel = st.selectbox("👥 Grupo de Cobro", lista_grupos)
            
#         with col3:
#             filtro_texto = st.text_input("👤 Buscar por Nombre o Línea", placeholder="Ej: 2604... o Antequera")

#     # --- OBTENCIÓN DE DATOS DEL PERÍODO SELECCIONADO ---
#     df = db.get_datos_consulta(periodo_sel, grupo_sel)

#     if not df.empty:
#         # Filtro de búsqueda en memoria (insensible a mayúsculas)
#         if filtro_texto:
#             df = df[
#                 df['linea'].astype(str).str.contains(filtro_texto) | 
#                 df['nombre'].str.contains(filtro_texto.upper())
#             ]

#         # --- PANEL DE MÉTRICAS ESPECÍFICAS ---
#         m1, m2, m3, m4 = st.columns(4)
        
#         # Datos extraídos directamente de la cabecera de la factura seleccionada
#         total_pdf_val = df['total_final_pdf'].iloc[0]
#         margen_val = df['markup_porcentaje'].iloc[0]
#         neto_mov_total = df['neto_movistar'].sum()
#         total_a_cobrar = df['precio_con_markup'].sum()
        
#         m1.metric("Líneas Activas", len(df))
#         m2.metric("Neto Movistar (Sin Imp)", f"$ {neto_mov_total:,.2f}")
#         m3.metric("Total Factura PDF", f"$ {total_pdf_val:,.2f}")
#         m4.metric(f"Total a Cobrar ({margen_val}%)", f"$ {total_a_cobrar:,.2f}")

#         # --- TABLA DE RESULTADOS ---
#         st.subheader(f"📋 Detalle del Período: {periodo_sel}")
        
#         df_display = df[[
#             "periodo", "linea", "nombre", "grupo", "categoria", 
#             "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"
#         ]].rename(columns={
#             "periodo": "Mes", 
#             "linea": "Línea", 
#             "nombre": "Responsable",
#             "grupo": "Grupo", 
#             "categoria": "Área", 
#             "precio_con_markup": "Subtotal"
#         })

#         st.dataframe(df_display, use_container_width=True, hide_index=True)
#     else:
#         st.info(f"No hay datos para el período {periodo_sel} con los filtros aplicados.")

#####################################################################

# import streamlit as st
# import pandas as pd
# from models.database import DatabaseManager

# def render_consultas():
#     st.header("Centro de Consultas Historicas")
#     db = DatabaseManager()
#     periodos_db = db.get_periodos_disponibles()

#     if not periodos_db:
#         st.info("No se encontraron registros en la base de datos.")
#         return

#     with st.container(border=True):
#         col1, col2, col3 = st.columns([2, 2, 3])
#         with col1:
#             periodo_sel = st.selectbox("Mes/Periodo", periodos_db, index=0)
#         with col2:
#             grupos_db = db.get_grupos_unicos()
#             lista_grupos = ["TODOS"] + grupos_db
#             grupo_sel = st.selectbox("Grupo de Cobro", lista_grupos)
#         with col3:
#             filtro_texto = st.text_input("Buscar por Nombre o Linea", placeholder="Ej: 2604... o Antequera")

#     df = db.get_datos_consulta(periodo_sel, grupo_sel)

#     if not df.empty:
#         if filtro_texto:
#             df = df[
#                 df['linea'].astype(str).str.contains(filtro_texto) | 
#                 df['nombre'].str.contains(filtro_texto.upper())
#             ]

#         m1, m2, m3, m4 = st.columns(4)
#         total_pdf_val = df['total_final_pdf'].iloc[0]
#         margen_val = df['markup_porcentaje'].iloc[0]
#         neto_mov_total = df['neto_movistar'].sum()
#         total_a_cobrar = df['precio_con_markup'].sum()
        
#         m1.metric("Lineas Activas", len(df))
#         m2.metric("Neto Movistar", f"$ {neto_mov_total:,.2f}")
#         m3.metric("Total Factura PDF", f"$ {total_pdf_val:,.2f}")
#         m4.metric(f"Total a Cobrar ({margen_val}%)", f"$ {total_a_cobrar:,.2f}")

#         st.subheader(f"Detalle del Periodo: {periodo_sel}")
#         df_display = df[[
#             "periodo", "linea", "nombre", "grupo", "categoria", 
#             "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"
#         ]].rename(columns={
#             "periodo": "Mes", "linea": "Linea", "nombre": "Responsable",
#             "grupo": "Grupo", "categoria": "Area", "precio_con_markup": "Subtotal"
#         })
#         st.dataframe(df_display, use_container_width=True, hide_index=True)
#     else:
#         st.info(f"No hay datos para el periodo {periodo_sel} con los filtros aplicados.")

########################################################################
###############################################################################

import streamlit as st
import pandas as pd
import json
import os
from models.database import DatabaseManager

def render_consultas():
    col_tit, col_logo = st.columns([3, 1])
    with col_tit:
        st.header("Centro de Consultas Historicas")
    with col_logo:
        logo_movistar = os.path.join("assets", "logo-Movistar.png") 
        if os.path.exists(logo_movistar):
            st.image(logo_movistar, width=200)
    
    db = DatabaseManager()
    periodos_db = db.get_periodos_disponibles()

    if not periodos_db:
        st.info("No se encontraron registros en la base de datos.")
        return

    # 1. CARGA DE CONFIGURACIÓN ACTUAL (JSON) para re-mapeo
    ruta_lineas = os.path.join("json", "config_lineas.json")
    try:
        with open(ruta_lineas, 'r', encoding='utf-8') as f:
            config_maestro = json.load(f)
    except FileNotFoundError:
        config_maestro = {}

    # --- BLOQUE DE FILTROS ---
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            periodo_sel = st.selectbox("Mes/Periodo", periodos_db, index=0)
            
        with col2:
            # Los grupos ahora vienen del JSON de mapeos para que coincidan con el Sidebar
            ruta_mapeos = os.path.join("json", "mapeos.json")
            try:
                with open(ruta_mapeos, 'r', encoding='utf-8') as f:
                    mapeos = json.load(f)
                    grupos_validos = mapeos.get("GRUPOS_VALIDOS", [])
            except:
                grupos_validos = db.get_grupos_unicos()
            
            lista_grupos = ["TODOS"] + grupos_validos
            grupo_sel = st.selectbox("Grupo de Cobro", lista_grupos)
            
        with col3:
            filtro_texto = st.text_input("Buscar por Nombre o Linea", placeholder="Ej: 2604... o Antequera")

    # 2. OBTENCIÓN DE DATOS Y RE-MAPEO DINÁMICO
    # Traemos los datos crudos del periodo
    df_raw = db.get_datos_consulta(periodo_sel, "TODOS") # Traemos todo para mapear en memoria
    
    if not df_raw.empty:
        # Preparamos el DataFrame de configuración para el Join
        df_config = pd.DataFrame.from_dict(config_maestro, orient='index').reset_index()
        df_config.rename(columns={'index': 'linea', 'grupo': 'grupo_actual', 'categoria': 'cat_actual'}, inplace=True)
        
        # Cruzamos datos: La línea es la clave
        df = df_raw.merge(df_config[['linea', 'grupo_actual', 'cat_actual']], on='linea', how='left')
        
        # Actualizamos las columnas con la realidad del JSON
        df['grupo'] = df['grupo_actual'].fillna('SIN ASIGNAR')
        df['categoria'] = df['cat_actual'].fillna('SIN ASIGNAR')

        # 3. APLICAR FILTROS DE USUARIO (Sobre los datos ya mapeados)
        if grupo_sel != "TODOS":
            df = df[df['grupo'] == grupo_sel]

        if filtro_texto:
            df = df[
                df['linea'].astype(str).str.contains(filtro_texto) | 
                df['nombre'].str.contains(filtro_texto.upper())
            ]

        if df.empty:
            st.warning(f"No hay registros para los filtros aplicados en {periodo_sel}")
            return

        # --- PANEL DE MÉTRICAS ---
        m1, m2, m3, m4 = st.columns(4)
        
        total_pdf_val = df['total_final_pdf'].iloc[0] if 'total_final_pdf' in df.columns else 0
        margen_val = df['markup_porcentaje'].iloc[0] if 'markup_porcentaje' in df.columns else 0
        neto_mov_total = df['neto_movistar'].sum()
        total_a_cobrar = df['precio_con_markup'].sum()
        
        m1.metric("Lineas Activas", len(df))
        m2.metric("Neto Movistar", f"$ {neto_mov_total:,.2f}")
        m3.metric("Total Factura PDF", f"$ {total_pdf_val:,.2f}")
        m4.metric(f"Total a Cobrar ({margen_val}%)", f"$ {total_a_cobrar:,.2f}")

        # --- TABLA DE RESULTADOS ---
        st.subheader(f"Detalle del Periodo: {periodo_sel}")
        
        df_display = df[[
            "periodo", "linea", "nombre", "grupo", "categoria", 
            "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"
        ]].rename(columns={
            "periodo": "Mes", 
            "linea": "Linea", 
            "nombre": "Responsable",
            "grupo": "Grupo", 
            "categoria": "Area", 
            "precio_con_markup": "Subtotal"
        })

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info(f"No hay datos para el periodo {periodo_sel}.")