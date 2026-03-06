import streamlit as st
import pandas as pd
import json
import os
from core.processor import BillingProcessor
from models.database import DatabaseManager

def render_auditoria():
    if 'cargado_exitoso' not in st.session_state:
        st.session_state.cargado_exitoso = False
    
    if 'dict_juegos' not in st.session_state:
        st.session_state.dict_juegos = {}
    # --- LOGOS Y TÍTULO ---
    col_tit, col_logo = st.columns([3, 1])
    
    with col_tit:
        st.header("Auditoría de Factura Movistar")
     
    with col_logo:
        # Ruta al logo de movistar (asegúrate de tenerlo en assets)
        logo_movistar = os.path.join("assets", "logo-Movistar.png") 
        if os.path.exists(logo_movistar):
            st.image(logo_movistar, width=200)
    # 

    # --- CONFIGURACIÓN INICIAL ---
    PATH_MARGEN = os.path.join("json", "config_margen.json")

    def leer_margen():
        try:
            with open(PATH_MARGEN, "r", encoding='utf-8') as f:
                return json.load(f).get("margen_actual", 18.0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 18.0

    db = DatabaseManager()
    processor = BillingProcessor()
    margen_final = leer_margen()
    
    # if 'dict_juegos' not in st.session_state:
    #     st.session_state.dict_juegos = {}
    if st.session_state.cargado_exitoso:
        st.success("✅ La facturación ha sido consolidada y guardada en la base de datos con éxito.")
        # st.info("Puede ver el historial en el módulo de 'Consultas Históricas'.")
        with st.expander("Ver instrucciones de uso", expanded=True):
            st.session_state.cargado_exitoso = False
            st.session_state.dict_juegos = {}
            st.rerun()
          
        return
    # --- SIDEBAR: PASO 1 ---
    st.sidebar.header("1. Archivo Principal")
    archivo_p = st.sidebar.file_uploader(
        "Seleccione Factura Principal (PDF)", 
        type="pdf",
        help="Cargue el resumen de cuenta de Movistar."
    )

    fecha_facturacion = st.sidebar.date_input(
        "Fecha de la Factura",
        value=None, # Empieza vacío para obligar a elegir
        format="DD/MM/YYYY",
        help="Seleccione la fecha que figura en el encabezado de la factura Movistar."
    )

    if not fecha_facturacion and archivo_p:
        st.sidebar.warning("⚠️ Debe seleccionar la fecha de facturación.")

    factura_valida = False
    resultado = None

    # --- LÓGICA DE VISUALIZACIÓN CONDICIONAL ---
    if archivo_p:
        # Una vez que hay un archivo, procesamos
        resultado = processor.process_invoice(
            archivo_p, 
            pdf_juegos=None, 
            otros_cargos_manual=0.0, 
            juegos_manuales=st.session_state.dict_juegos
        )
        
        if resultado["auditoria_fiscal"]["error_lectura"]:
            st.error("⚠️ El PDF no es una factura válida de Movistar. Por favor, verifique el archivo.")
            st.sidebar.warning("Archivo inválido detectado.")
        else:
            # CASO: ARCHIVO EXITOSO
            factura_valida = True
            st.sidebar.success("Archivo válido detectado.")
            st.sidebar.markdown("---")
            st.sidebar.header("2. Anexo y Cargos")
            archivo_j = st.sidebar.file_uploader("Cargue Anexo Juegos (Opcional)", type="pdf")

            st.sidebar.subheader("Otros Cargos")
            int_mora = st.sidebar.number_input("Intereses ($)", min_value=0.0, value=0.0, step=0.01)
            recon = st.sidebar.number_input("Otros cargos ($)", min_value=0.0, value=0.0, step=0.01)
            
            st.sidebar.markdown("---")
            st.sidebar.header("3. Extras Manuales")
            lineas_disponibles = sorted(list(processor.config_lineas.keys()))
            l_sel = st.sidebar.selectbox("Seleccione Línea", [""] + lineas_disponibles)
            m_sel = st.sidebar.number_input("Monto ($)", min_value=0.0, step=0.01)
            
            if st.sidebar.button("➕ Aplicar Cargo", use_container_width=True):
                if l_sel:
                    st.session_state.dict_juegos[l_sel] = m_sel
                    st.rerun()

            # Procesamiento final con todos los datos
            resultado = processor.process_invoice(
                archivo_p, 
                archivo_j, 
                otros_cargos_manual=round(int_mora + recon, 2),
                juegos_manuales=st.session_state.dict_juegos
            )

            # --- RENDERIZADO DE TABLAS Y MÉTRICAS ---
            for d in resultado['datos']:
                linea_cfg = processor.config_lineas.get(d['linea'], {})
                d['grupo'] = linea_cfg.get('grupo', 'TERCEROS_HRS')
                d['categoria'] = linea_cfg.get('categoria', 'EXTERNOS')

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Neto Plan", f"$ {resultado['total_principal']:,.2f}")
            m2.metric("Total Juegos", f"$ {resultado['total_juegos']:,.2f}")
            m3.metric("Ajustes Extra", f"$ {round(int_mora + recon, 2):,.2f}")
            m4.metric("TOTAL MOVISTAR", f"$ {resultado['total_final']:,.2f}")

            st.subheader(f"📋 Detalle de {len(resultado['datos'])} Abonados")
            df = pd.DataFrame(resultado["datos"])
            df_display = df[["linea", "nombre", "grupo", "categoria", "total_fijo", "total_variable", "juegos_extra", "total_neto"]]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            if resultado["resumen_impositivo"]:
                st.divider()
                st.subheader("🧾 Resumen Impositivo y Auditoría")
                df_tax = pd.DataFrame(resultado["resumen_impositivo"])
                st.table(df_tax.style.format({
                    "Base Imponible": "$ {:,.2f}", "IVA": "$ {:,.2f}", 
                    "Total": "$ {:,.2f}", "Total Factura": "$ {:,.2f}"
                }))

                st.divider()


                @st.dialog("💾 Confirmar Carga a Base de Datos")
                def confirmar_consolidacion(datos_mes):
                    mes_f = str(fecha_facturacion.month).zfill(2)
                    anio_f = str(fecha_facturacion.year)
                    total_f_pdf = df_tax[df_tax['Concepto'] == 'Totales']['Total Factura'].values[0]
                    impuestos_pdf = df_tax[df_tax['Concepto'] == 'Totales']['Total'].values[0]
                    neto_con_margen = resultado['total_final'] * (1 + (margen_final / 100))
                    total_recaudar = round(neto_con_margen + impuestos_pdf, 2)
                    cantidad_lineas = len(datos_mes['datos'])
                    datos_mes['periodo_mes'] = mes_f
                    datos_mes['periodo_anio'] = anio_f
                    datos_mes['fecha_manual'] = fecha_facturacion.strftime('%d/%m/%Y')

                    st.warning(f"⚠️ Esta acción guardará el detalle de **{cantidad_lineas}** líneas del periodo: **{mes_f}/{anio_f}** de Facturación.")
                    st.write(f'**Total Movistar:** ${total_f_pdf:,.2f}\n\n**Total con Impuestos ({margen_final:,.2f}%):** ${total_recaudar:,.2f}')
                    st.info("Asegurese de que los extras (juegos u otros cargos) estén correctos antes de confirmar.")
                    col_si, col_no = st.columns(2)
                    if col_si.button("CONFIRMAR Y GUARDAR", type="primary", use_container_width=True):
                        
                        id_factura = db.registrar_consolidacion(datos_mes, margen_final, total_f_pdf)
                        st.session_state.last_factura_id = id_factura
                        st.success("¡Datos guardados con éxito!")
                        st.session_state.cargado_exitoso = True
                        st.rerun()
                    
                    if col_no.button("CANCELAR", use_container_width=True):
                        st.rerun()

                # Botonera principal
                c1, c2, _ = st.columns([1, 1, 2])
                af = resultado["auditoria_fiscal"]
                if c1.button("✅ Consolidar Facturación", type="primary" if af["match_factura"] else "secondary"):
                    confirmar_consolidacion(resultado)
                
                if c2.button("🗑️ Descartar Cambios"):
                    st.session_state.dict_juegos = {}
                    st.rerun()
    else:
        # CASO: ESTADO INICIAL (SIN ARCHIVO)
        st.info("👋 Bienvenida/o. Para comenzar, cargue la factura de Movistar en la barra lateral izquierda.")
        with st.expander("Ver instrucciones de uso", expanded=True):
            st.markdown("""
            1. Suba el archivo PDF principal en el panel izquierdo.
            2. El sistema validará automáticamente si es un documento compatible.
            3. Una vez validado, se habilitarán las opciones de juegos y cargos manuales.
            """)