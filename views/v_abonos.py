#####################################################################################################

# import streamlit as st
# import pandas as pd
# import base64
# from models.database import DatabaseManager
# from core.pdf_generator import generar_pdf_bytes

# def callback_pdf(grupo, df, total):
#     """Callback para persistir el PDF en el estado de la sesión."""
#     st.session_state.pdf_buffer = {
#         "grupo": grupo,
#         "bytes": generar_pdf_bytes(grupo, df, total)
#     }

# def render_abonos():
#     db = DatabaseManager()
    
#     # 1. Recuperación del ID y Período
#     factura_id = st.session_state.get('last_factura_id')
#     mes, anio = None, None # Inicializamos para evitar el UnboundLocalError

#     if not factura_id:
#         periodos = db.get_periodos_disponibles()
#         if periodos:
#             ultimo_p = periodos[0]
#             mes, anio = ultimo_p.split('/')
            
#             with db._get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "SELECT id FROM facturas WHERE periodo_mes = ? AND periodo_anio = ? ORDER BY id DESC LIMIT 1", 
#                     (mes, anio)
#                 )
#                 row = cursor.fetchone()
#                 if row:
#                     factura_id = row[0]
#                     st.session_state.last_factura_id = factura_id
#     else:
#         # Si ya tenemos el ID, buscamos su mes/año para el encabezado
#         with db._get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT periodo_mes, periodo_anio FROM facturas WHERE id = ?", (factura_id,))
#             row = cursor.fetchone()
#             if row:
#                 mes, anio = row[0], row[1]

#     # --- ENCABEZADO DINÁMICO ---
#     # Solo mostramos el header si logramos identificar el período
#     if mes and anio:
#         st.header(f"Emisión de boletos de cobro: {mes}/{anio}")
#     else:
#         st.header("Emisión de boletos de cobro")

#     if not factura_id:
#         st.info("💡 No hay datos previos. Procesa una factura en 'Auditoría' primero.")
#         return

#     # 2. Carga de datos
#     df_detalle = db.get_consumos_por_factura(factura_id)
#     if df_detalle.empty: return

#     # --- 3. VISOR DE PDF ---
#     if "pdf_buffer" in st.session_state:
#         buffer = st.session_state.pdf_buffer
#         with st.container(border=True):
#             c1, c2 = st.columns([0.8, 0.2])
#             c1.subheader(f"📄 Comprobante: {buffer['grupo']}")
#             if c2.button("Cerrar Visor ❌"):
#                 del st.session_state.pdf_buffer
#                 st.rerun()
            
#             base64_pdf = base64.b64encode(buffer['bytes']).decode('utf-8')
#             pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
#             st.markdown(pdf_display, unsafe_allow_html=True)
    
#     # --- 1. CLIENTES DIRECTOS ---
#     st.subheader("👥 Clientes Externos")

#         # Obtenemos todos los grupos únicos que existen en esta factura
#     todos_los_grupos = df_detalle['grupo'].unique().tolist()

#         # Definimos quiénes NO son externos para filtrarlos de esta sección
#     internos = ["EMPRESA", "TERCEROS_HRS"]
        
#         # La lista de clientes ahora se genera sola basándose en lo que hay en la DB
#     clientes_externos = [g for g in todos_los_grupos if g not in internos and g is not None]
        
#         # Ordenamos alfabéticamente para que no salten de lugar
#     clientes_externos.sort()

#     if not clientes_externos:
#         st.info("No se detectaron grupos externos en esta factura.")
#     else:
#             cols = st.columns(3)
            
#             for i, grupo in enumerate(clientes_externos):
#                 df_g = df_detalle[df_detalle['grupo'] == grupo].copy()
#                 if df_g.empty: continue
                
#                 df_g = df_g.sort_values(by="nombre")
#                 total_g = df_g['precio_con_markup'].sum()

#                 with cols[i % 3]:
#                     with st.container(border=True):
#                         st.subheader(grupo)
#                         st.metric("Total", f"${total_g:,.2f}")
                        
#                         df_view = df_g[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
#                             columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
#                                     "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
#                         )

#                         with st.expander("Ver detalle"):
#                             st.dataframe(df_view, hide_index=True)

#                         st.button(f"🖨️ PDF {grupo}", key=f"btn_{grupo}", 
#                                 on_click=callback_pdf, args=(grupo, df_view, total_g), use_container_width=True)

#     # --- 2. TERCEROS HRS ---
#     st.divider()
#     df_hrs = df_detalle[df_detalle['grupo'] == "TERCEROS_HRS"].copy()
#     if not df_hrs.empty:
#         st.subheader("Listado de Terceros (HRS)")
#         df_hrs = df_hrs.sort_values(by="nombre")
#         total_hrs = df_hrs['precio_con_markup'].sum()
        
#         with st.container(border=True):
#             c1, c2 = st.columns([0.7, 0.3])
#             c1.write("### TERCEROS_HRS")
#             c2.metric("Total", f"${total_hrs:,.2f}")
            
#             df_view_hrs = df_hrs[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
#                 columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
#                          "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
#             )
#             st.dataframe(df_view_hrs, hide_index=True, use_container_width=True)
#             st.button("🖨️ PDF TERCEROS_HRS", key="btn_hrs", on_click=callback_pdf, args=("TERCEROS_HRS", df_view_hrs, total_hrs))

#     # --- 3. SECCIÓN EMPRESA ---
#     st.divider()
#     df_empresa = df_detalle[df_detalle['grupo'] == "EMPRESA"].copy()
#     if not df_empresa.empty:
#         with st.expander("🏠 Gasto Interno Hierrosan"):
#             df_emp_view = df_empresa[["nombre", "linea", "precio_con_markup"]].sort_values("nombre").rename(
#                 columns={"nombre": "Nombre", "linea": "Línea", "precio_con_markup": "Costo"}
#             )
#             st.dataframe(df_emp_view, hide_index=True, use_container_width=True)
#             st.write(f"**Total Gasto Empresa:** ${df_empresa['precio_con_markup'].sum():,.2f}")

#############################################################################

# import streamlit as st
# import pandas as pd
# import base64
# import json
# import os
# from models.database import DatabaseManager
# from core.pdf_generator import generar_pdf_bytes

# def callback_pdf(grupo, df, total):
#     st.session_state.pdf_buffer = {
#         "grupo": grupo,
#         "bytes": generar_pdf_bytes(grupo, df, total)
#     }

# def render_abonos():
#     db = DatabaseManager()
#     PATH_MAPEOS = os.path.join("json", "mapeos.json")
    
#     # Carga de mapeos para identificar grupos internos
#     try:
#         with open(PATH_MAPEOS, "r", encoding='utf-8') as f:
#             mapeos = json.load(f)
#             internos = mapeos.get("GRUPOS_VALIDOS", ["EMPRESA", "TERCEROS_HRS"])[:2] # Fallback a los dos primeros
#     except:
#         internos = ["EMPRESA", "TERCEROS_HRS"]

#     factura_id = st.session_state.get('last_factura_id')
#     mes, anio = None, None

#     if not factura_id:
#         periodos = db.get_periodos_disponibles()
#         if periodos:
#             ultimo_p = periodos[0]
#             mes, anio = ultimo_p.split('/')
#             with db._get_connection() as conn:
#                 cursor = conn.cursor()
#                 cursor.execute(
#                     "SELECT id FROM facturas WHERE periodo_mes = ? AND periodo_anio = ? ORDER BY id DESC LIMIT 1", 
#                     (mes, anio)
#                 )
#                 row = cursor.fetchone()
#                 if row:
#                     factura_id = row[0]
#                     st.session_state.last_factura_id = factura_id
#     else:
#         with db._get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT periodo_mes, periodo_anio FROM facturas WHERE id = ?", (factura_id,))
#             row = cursor.fetchone()
#             if row:
#                 mes, anio = row[0], row[1]

#     if mes and anio:
#         st.header(f"Emisión de boletos de cobro: {mes}/{anio}")
#     else:
#         st.header("Emisión de boletos de cobro")

#     if not factura_id:
#         st.info("Procesa una factura en 'Auditoría' primero.")
#         return

#     df_detalle = db.get_consumos_por_factura(factura_id)
#     if df_detalle.empty: return

#     if "pdf_buffer" in st.session_state:
#         buffer = st.session_state.pdf_buffer
#         with st.container(border=True):
#             c1, c2 = st.columns([0.8, 0.2])
#             c1.subheader(f"Comprobante: {buffer['grupo']}")
#             if c2.button("Cerrar Visor"):
#                 del st.session_state.pdf_buffer
#                 st.rerun()
            
#             base64_pdf = base64.b64encode(buffer['bytes']).decode('utf-8')
#             pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
#             st.markdown(pdf_display, unsafe_allow_html=True)
    
#     # --- CLIENTES EXTERNOS ---
#     st.subheader("Clientes Externos")
#     todos_los_grupos = df_detalle['grupo'].unique().tolist()
#     clientes_externos = [g for g in todos_los_grupos if g not in internos and g is not None]
#     clientes_externos.sort()

#     if not clientes_externos:
#         st.info("No se detectaron grupos externos en esta factura.")
#     else:
#         cols = st.columns(3)
#         for i, grupo in enumerate(clientes_externos):
#             df_g = df_detalle[df_detalle['grupo'] == grupo].copy()
#             if df_g.empty: continue
            
#             df_g = df_g.sort_values(by="nombre")
#             total_g = df_g['precio_con_markup'].sum()

#             with cols[i % 3]:
#                 with st.container(border=True):
#                     st.subheader(grupo)
#                     st.metric("Total", f"${total_g:,.2f}")
                    
#                     df_view = df_g[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
#                         columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
#                                 "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
#                     )
#                     with st.expander("Ver detalle"):
#                         st.dataframe(df_view, hide_index=True)

#                     st.button(f"Generar PDF {grupo}", key=f"btn_{grupo}", 
#                             on_click=callback_pdf, args=(grupo, df_view, total_g), use_container_width=True)

#     # --- TERCEROS HRS ---
#     st.divider()
#     df_hrs = df_detalle[df_detalle['grupo'] == "TERCEROS_HRS"].copy()
#     if not df_hrs.empty:
#         st.subheader("Listado de Terceros (HRS)")
#         df_hrs = df_hrs.sort_values(by="nombre")
#         total_hrs = df_hrs['precio_con_markup'].sum()
#         with st.container(border=True):
#             c1, c2 = st.columns([0.7, 0.3])
#             c1.write("### TERCEROS_HRS")
#             c2.metric("Total", f"${total_hrs:,.2f}")
#             df_view_hrs = df_hrs[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
#                 columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
#                          "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
#             )
#             st.dataframe(df_view_hrs, hide_index=True, use_container_width=True)
#             st.button("Generar PDF TERCEROS_HRS", key="btn_hrs", on_click=callback_pdf, args=("TERCEROS_HRS", df_view_hrs, total_hrs))

#     # --- SECCIÓN EMPRESA ---
#     st.divider()
#     df_empresa = df_detalle[df_detalle['grupo'] == "EMPRESA"].copy()
#     if not df_empresa.empty:
#         with st.expander("Gasto Interno Hierrosan"):
#             df_emp_view = df_empresa[["nombre", "linea", "precio_con_markup"]].sort_values("nombre").rename(
#                 columns={"nombre": "Nombre", "linea": "Línea", "precio_con_markup": "Costo"}
#             )
#             st.dataframe(df_emp_view, hide_index=True, use_container_width=True)
#             st.write(f"**Total Gasto Empresa:** ${df_empresa['precio_con_markup'].sum():,.2f}")

#########################################################################################3
##################################################################################

import streamlit as st
import pandas as pd
import base64
import json
import os
from models.database import DatabaseManager
from core.pdf_generator import generar_pdf_bytes

def callback_pdf(grupo, df, total):
    st.session_state.pdf_buffer = {
        "grupo": grupo,
        "bytes": generar_pdf_bytes(grupo, df, total)
    }

def render_abonos():

    db = DatabaseManager()
    
    # 1. CARGA DE CONFIGURACIÓN ACTUAL (JSON)
    # Este es el "cerebro" que va a mandar sobre los datos de la DB
    ruta_lineas = os.path.join("json", "config_lineas.json")
    try:
        with open(ruta_lineas, 'r', encoding='utf-8') as f:
            config_maestro = json.load(f)
    except FileNotFoundError:
        config_maestro = {}

    factura_id = st.session_state.get('last_factura_id')
    mes, anio = None, None

    # Lógica de recuperación de factura (Mantenemos tu estructura)
    if not factura_id:
        periodos = db.get_periodos_disponibles()
        if periodos:
            ultimo_p = periodos[0]
            mes, anio = ultimo_p.split('/')
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM facturas WHERE periodo_mes = ? AND periodo_anio = ? ORDER BY id DESC LIMIT 1", 
                    (mes, anio)
                )
                row = cursor.fetchone()
                if row:
                    factura_id = row[0]
                    st.session_state.last_factura_id = factura_id
    else:
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT periodo_mes, periodo_anio FROM facturas WHERE id = ?", (factura_id,))
            row = cursor.fetchone()
            if row:
                mes, anio = row[0], row[1]

    if mes and anio:
        col_tit, col_logo = st.columns([3, 1])
        with col_tit:
            st.header(f"Emisión de boletos de cobro: {mes}/{anio}")
        with col_logo:
            logo_movistar = os.path.join("assets", "logo-Movistar.png") 
            if os.path.exists(logo_movistar):
             st.image(logo_movistar, width=200)

    else:
        st.header("Emisión de boletos de cobro")

    if not factura_id:
        st.info("Procesa una factura en 'Auditoría' primero.")
        return

    # 2. CARGA Y RE-MAPEO DINÁMICO (Motor Pandas)
    df_db = db.get_consumos_por_factura(factura_id)
    if df_db.empty: return

    # Convertimos el JSON a un DataFrame para cruzarlo rápido
    # Orient='index' porque las llaves son los números de línea
    df_config = pd.DataFrame.from_dict(config_maestro, orient='index').reset_index()
    df_config.rename(columns={'index': 'linea', 'grupo': 'grupo_nuevo'}, inplace=True)

    # El "Join" que actualiza los grupos en tiempo real
    df_detalle = df_db.merge(df_config[['linea', 'grupo_nuevo']], on='linea', how='left')
    
    # Si la línea no está en el JSON, la mandamos a "SIN ASIGNAR"
    df_detalle['grupo'] = df_detalle['grupo_nuevo'].fillna('SIN ASIGNAR')

    # --- VISOR DE PDF ---
    if "pdf_buffer" in st.session_state:
        buffer = st.session_state.pdf_buffer
        with st.container(border=True):
            c1, c2 = st.columns([0.8, 0.2])
            c1.subheader(f"Comprobante: {buffer['grupo']}")
            if c2.button("Cerrar Visor"):
                del st.session_state.pdf_buffer
                st.rerun()
            
            base64_pdf = base64.b64encode(buffer['bytes']).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)

    # --- RENDERIZADO DE TARJETAS ---
    # Ahora usamos la columna 'grupo' que ya fue actualizada por el JSON
    grupos_en_factura = sorted(df_detalle['grupo'].unique().tolist())
    
    # Separamos internos de externos (puedes ajustar esta lista)
    internos = ["TERCEROS_HRS","EMPRESA"]
    externos = [g for g in grupos_en_factura if g not in internos]

    # SECCIÓN: Clientes Externos y Sin Asignar
    st.subheader("Clientes Externos")
    if not externos:
        st.info("No hay grupos externos detectados.")
    else:
        cols = st.columns(3)
        for i, grupo in enumerate(externos):
            df_g = df_detalle[df_detalle['grupo'] == grupo].copy().sort_values("nombre")
            total_g = df_g['precio_con_markup'].sum()

            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(grupo)
                    st.metric("Total", f"${total_g:,.2f}")
                    
                    df_view = df_g[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
                        columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
                                "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
                    )
                    with st.expander("Ver detalle"):
                        st.dataframe(df_view, hide_index=True)

                    st.button(f"Generar PDF {grupo}", key=f"btn_{grupo}", 
                            on_click=callback_pdf, args=(grupo, df_view, total_g), use_container_width=True)

    # SECCIÓN: Otros Grupos (Internos)
    for grupo_int in internos:
        df_int = df_detalle[df_detalle['grupo'] == grupo_int].copy()
        if not df_int.empty:
            st.divider()
            st.subheader(f"Listado {grupo_int}")
            total_int = df_int['precio_con_markup'].sum()
            with st.container(border=True):
                c1, c2 = st.columns([0.7, 0.3])
                c1.write(f"### {grupo_int}")
                c2.metric("Total", f"${total_int:,.2f}")
                df_view_int = df_int[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
                    columns={"nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
                             "costo_variable": "Variable", "costo_juegos": "Juegos", "precio_con_markup": "Total c/Imp"}
                )
                st.dataframe(df_view_int, hide_index=True, use_container_width=True)
                st.button(f"Generar PDF {grupo_int}", key=f"btn_{grupo_int}", on_click=callback_pdf, args=(grupo_int, df_view_int, total_int))