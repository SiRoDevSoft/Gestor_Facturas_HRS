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
    
    ruta_lineas = os.path.join("json", "config_lineas.json")
    try:
        with open(ruta_lineas, 'r', encoding='utf-8') as f:
            config_maestro = json.load(f)
    except FileNotFoundError:
        config_maestro = {}

    factura_id = st.session_state.get('last_factura_id')
    mes, anio = None, None
    

    # 1. CARGA DE PERIODOS (Para que el selector tenga vida)
    periodos_disponibles = db.get_periodos_disponibles()

    if not periodos_disponibles:
        st.info("No hay facturas procesadas. Ve a 'Auditoría' para cargar la primera.")
        return

    # 2. Contenedor del Selector
    with st.container(border=False):
        col_sel, col_info, col_logo = st.columns([2, 2, 1])
        
        with col_sel:
            st.header(f"Emisión de boletos de cobro")
            # 'index=0' asegura que al cargar la página siempre muestre el último periodo ingresado
            periodo_elegido = st.selectbox(
                "📅 Seleccionar Periodo de Facturación", 
                periodos_disponibles, 
                index=0,
                help="Por defecto se muestra el último periodo cargado en la base de datos."
             )
        with col_logo:
            logo_movistar = os.path.join("assets", "logo-Movistar.png") 
            if os.path.exists(logo_movistar):
             st.image(logo_movistar, width=200)

        with col_info:
            # Extraemos mes y año de la selección actual
            mes_sel, anio_sel = periodo_elegido.split('/')
            
            with db._get_connection() as conn:
                # Buscamos el ID de la factura que corresponde a ese periodo
                result = conn.execute(
                    text("""
                        SELECT id 
                        FROM facturas 
                        WHERE periodo_mes = :mes AND periodo_anio = :anio 
                        ORDER BY id DESC 
                        LIMIT 1
                    """), 
                    {"mes": mes_sel, "anio": anio_sel}
                )
                row = result.fetchone()
                
                if row:
                    factura_id = row[0]
                    # Actualizamos variables globales para que el resto del código funcione
                    st.session_state.last_factura_id = factura_id
                    mes, anio = mes_sel, anio_sel
                    # st.success(f"Visualizando periodo actualizado: {periodo_elegido}")
                else:
                    st.error("No se encontró registro para este periodo.")
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

    
    # =========================================================================
    # LOGICA DE EXCEPCIÓN: GRUPO PIEDECASAS (No paga impuesto/markup)
    # =========================================================================
    # Si el grupo es PIEDECASAS, forzamos que el 'precio_con_markup' sea solo la suma de costos base
    condicion_exenta = df_detalle['grupo'] == 'PIEDECASAS'
    
    df_detalle.loc[condicion_exenta, 'precio_con_markup'] = (
        df_detalle['costo_fijo'] + 
        df_detalle['costo_variable'] + 
        df_detalle['costo_juegos']
    )
    
        # --- DESCARGA DE PDF (Única y Directa) ---
    if "pdf_buffer" in st.session_state:
        buffer_data = st.session_state.pdf_buffer
        raw_pdf = buffer_data.get('bytes')
        
        # EXTRACCIÓN FORZADA DE BYTES (Esto elimina el unsupported_error)
        if hasattr(raw_pdf, 'getvalue'):
            pdf_final = raw_pdf.getvalue()
        elif isinstance(raw_pdf, bytes):
            pdf_final = raw_pdf
        else:
            # Caso extremo: si es un objeto FPDF u otro, intentamos convertir
            try:
                pdf_final = bytes(raw_pdf)
            except:
                pdf_final = b""

        # Nombre del archivo dinámico
        nombre_archivo = f"{mes}-{anio}_{buffer_data['grupo']}.pdf"

        with st.container(border=True):
            st.subheader(f"📄 Comprobante Generado: {buffer_data['grupo']}")
            
            c_dl, c_cl = st.columns([0.5, 0.5])
            
            # BOTÓN DE DESCARGA NATIVO (Solo con pdf_final verificado)
            if pdf_final:
                c_dl.download_button(
                    label=f"DESCARGAR {nombre_archivo}",
                    data=pdf_final,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    key="btn_descarga_final_ok",
                    use_container_width=True,
                    type="primary"
                )
            
            if c_cl.button("CERRAR", key="btn_cerrar_final_limpio", use_container_width=True):
                del st.session_state.pdf_buffer
                st.rerun()




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
        n_cols = 3
        cols = st.columns(n_cols)
        for i, grupo in enumerate(externos):
            df_g = df_detalle[df_detalle['grupo'] == grupo].copy().sort_values("nombre")
            total_g = df_g['precio_con_markup'].sum()

            # Validación de índice segura
            target_col = cols[i % n_cols]
            
            with target_col:
                with st.container(border=True):
                    st.subheader(grupo)
                    st.metric("Total", f"${total_g:,.2f}")
                    
                    df_view = df_g[["nombre", "linea", "costo_fijo", "costo_variable", "costo_juegos", "precio_con_markup"]].rename(
                        columns={
                            "nombre": "Usuario", "linea": "Línea", "costo_fijo": "Fijo", 
                            "costo_variable": "Variable", "costo_juegos": "Juegos", 
                            "precio_con_markup": "Total c/Imp"
                        }
                    )
                    
                    with st.expander("Ver detalle"):
                        st.dataframe(df_view, hide_index=True, use_container_width=True)

                    st.button(
                        f"Generar PDF {grupo}", 
                        key=f"btn_{grupo}", 
                        on_click=callback_pdf, 
                        args=(grupo, df_view, total_g), 
                        use_container_width=True
                    )
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