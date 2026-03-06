import streamlit as st
import pandas as pd
import base64
import json
import os
from sqlalchemy import text
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

        # --- REEMPLAZO DE LÓGICA DE RECUPERACIÓN (Líneas 31-48 aprox) ---
    if not factura_id:
        periodos = db.get_periodos_disponibles()
        if periodos:
            ultimo_p = periodos[0]
            mes, anio = ultimo_p.split('/')
            with db._get_connection() as conn:
                # Cambiamos cursor.execute por conn.execute (Sintaxis SQLAlchemy)
                result = conn.execute(
                    text("SELECT id FROM facturas WHERE periodo_mes = :mes AND periodo_anio = :anio ORDER BY id DESC LIMIT 1"), 
                    {"mes": mes, "anio": anio}
                )
                row = result.fetchone()
                if row:
                    factura_id = row[0]
                    st.session_state.last_factura_id = factura_id
    else:
        with db._get_connection() as conn:
            result = conn.execute(
                text("SELECT periodo_mes, periodo_anio FROM facturas WHERE id = :id"), 
                {"id": factura_id}
            )
            row = result.fetchone()
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

        # --- VISOR Y DESCARGA DE PDF 
    if "pdf_buffer" in st.session_state:
        buffer_data = st.session_state.pdf_buffer
        raw_content = buffer_data.get('bytes')
        
        
        final_pdf = b""
        try:
            if isinstance(raw_content, bytes):
                final_pdf = raw_content
            elif hasattr(raw_content, 'getvalue'):
                final_pdf = raw_content.getvalue()
            elif hasattr(raw_content, 'output'): 
                final_pdf = raw_content.output(dest='S').encode('latin-1')
            else:
                final_pdf = bytes(raw_content)
        except Exception as e:
            st.error(f"Error procesando el PDF: {e}")

        if final_pdf:
            with st.container(border=True):
                st.subheader(f"📄 Comprobante: {buffer_data['grupo']}")
                
                c_dl, c_cl = st.columns([0.5, 0.5])
                
                
                c_dl.download_button(
                    label=" DESCARGAR PDF",
                    data=final_pdf,
                    file_name=f"Comprobante_{buffer_data['grupo']}.pdf",
                    mime="application/pdf",
                    key="dl_final_ok",
                    use_container_width=True
                )
                
                if c_cl.button("CERRAR VISOR", use_container_width=True):
                    del st.session_state.pdf_buffer
                    st.rerun()

                # Visor Base64 (Opcional, si el navegador lo permite)
                try:
                    b64 = base64.b64encode(final_pdf).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                except:
                    pass




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