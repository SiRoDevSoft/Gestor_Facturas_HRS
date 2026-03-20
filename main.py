import os
import streamlit as st
from views.v_auditoria import render_auditoria
from views.v_abonos import render_abonos
from views.v_configuracion import render_configuracion
from views.v_consultas import render_consultas 
from views.v_login import render_login
from views.v_dashboard import render_dashboard
from models.auth_db import AuthManager

# 1. Configuración de página 
st.set_page_config(
    page_title="Hierrosan ERP", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializamos el gestor de seguridad
auth = AuthManager()

def main():
    # Esto evita el AttributeError en v_configuracion y otras vistas
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'form_version' not in st.session_state:
        st.session_state.form_version = 0
    if 'config_lucro' not in st.session_state:
        st.session_state.config_lucro = 21.0
    if 'last_factura_id' not in st.session_state:
        st.session_state.last_factura_id = None
    if 'menu_option' not in st.session_state:
        st.session_state.menu_option = "📊 Auditoría"

    # --- B: REGISTRO INICIAL
    auth.registrar_usuario("admin", "1234", "Color?", "Azul")
    
    # --- C: CONTROL DE ACCESO ---
    if not st.session_state.autenticado:
        render_login(auth)
        return 

   
    
    # Estilos CSS
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa !important; }
        .stApp * { color: #212529; }
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #dee2e6; }
        [data-testid="stSidebar"] * { color: #212529 !important; }
        div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label {
            background-color: #f8f9fa !important;
            padding: 12px; border-radius: 6px; margin-bottom: 6px;
            border: 1px solid #e9ecef; width: 100%;
        }
        [data-testid="stMetricValue"] { color: #1a2c38 !important; }
        [data-testid="stTable"], [data-testid="stDataFrame"] { background-color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

    
    with st.sidebar:
        # 1. CSS para achicar el botón específicamente en la sidebar
        st.markdown("""
                <style>
    /* Buscamos el botón secundario dentro de la sidebar y le quitamos el borde y fondo */
    div[data-testid="stSidebar"] button[kind="secondary"] {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        color: #7f8c8d !important; /* Color gris suave */
        padding: 0px !important;    /* Para que sea lo más pequeño posible */
        height: auto !important;
    }
    
    /* Efecto al pasar el mouse (opcional) */
    div[data-testid="stSidebar"] button[kind="secondary"]:hover {
        color: #e74c3c !important; /* Cambia a rojo al pasar el mouse */
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

        # 2. Botón de Cerrar Sesión (Superior y Pequeño)
        if st.button("<< Cerrar Sesión", type="secondary"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True) # Espacio sutil

        # 3. Logo
        logo_display_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_display_path):
            # Usamos un ancho controlado para que no sature la sidebar
            st.image(logo_display_path, use_container_width=True)
        else:
            st.error("No se encontró assets/logo.png")
        
        # 4. Versión y Separador
        st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.75rem; margin-top: -10px;'>v18.0.5 Stable</p>", unsafe_allow_html=True)
        st.divider()
     
        menu = st.radio(
            "Navegación",
            ["Auditoría de Factura", "Boletos de Cobro", "Consultas Históricas","Pronostico Empresa", "Configuración"],
            index=0
        )
        st.divider()

    # --- LÓGICA DE NAVEGACIÓN ---
    if menu == "Auditoría de Factura":
        render_auditoria()
    elif menu == "Boletos de Cobro":
        render_abonos()
    elif menu == "Consultas Históricas": 
        render_consultas()
    elif menu == "Pronostico Empresa": 
        render_dashboard()    
    elif menu == "Configuración":
        render_configuracion()

if __name__ == "__main__":
    main()