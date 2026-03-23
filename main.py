import os
import streamlit as st
from PIL import Image
from views.v_auditoria import render_auditoria
from views.v_abonos import render_abonos
from views.v_configuracion import render_configuracion
from views.v_consultas import render_consultas 
from utils.helpers import configure_ui_assets
from views.v_login import render_login
from views.v_dashboard import render_dashboard
from models.auth_db import AuthManager

# --- FUNCIONES DE SOPORTE ---
def load_assets():
    """Carga estilos CSS y Script de JS para el sidebar"""
    css_file = os.path.join("assets", "css", "styles.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
  
# --- 1. CONFIGURACIÓN DE PÁGINA ---
favicon_path = os.path.join("assets", "ICONO.png")
try:
    img_icon = Image.open(favicon_path)
    st.set_page_config(page_title="ERP Hierrosan | SiRoDevSoft", 
                       page_icon=img_icon,
                        layout="wide",
                        initial_sidebar_state="expanded")
except:
    st.set_page_config(page_title="ERP Hierrosan | SiRoDevSoft", page_icon="🏗️", layout="wide")

load_assets()

# Inicializamos el gestor de seguridad
auth = AuthManager()

def main():
    # Inicialización de Session State
    states = {
        'autenticado': False, 'form_version': 0, 
        'config_lucro': 21.0, 'last_factura_id': None
    }
    for key, val in states.items():
        if key not in st.session_state: st.session_state[key] = val

    # # Registro inicial de admin (Solo para desarrollo)
    # auth.registrar_usuario("admin", "1234", "Color?", "Azul")
    
    if not st.session_state.autenticado:
        # configure_ui_assets(is_authenticated=False)
        render_login(auth)
        return 

    # --- SIDEBAR NAVEGACIÓN ---
    # configure_ui_assets(is_authenticated=True)
    with st.sidebar:
        if st.button("<< Cerrar Sesión", type="secondary"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        
        st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.75rem; margin-top: -10px;'>v18.0.5 Stable</p>", unsafe_allow_html=True)
        st.divider()
     
        menu = st.radio(
            "Navegación",
            ["Auditoría de Factura", "Boletos de Cobro", "Consultas Históricas", "Pronostico Empresa", "Configuración"],
            index=0
        )
        st.divider()

    # --- RUTEO DE VISTAS ---
    vistas = {
        "Auditoría de Factura": render_auditoria,
        "Boletos de Cobro": render_abonos,
        "Consultas Históricas": render_consultas,
        "Pronostico Empresa": render_dashboard,
        "Configuración": render_configuracion
    }
    vistas[menu]()

if __name__ == "__main__":
    main()