import os
import streamlit as st
from views.v_auditoria import render_auditoria
from views.v_abonos import render_abonos
from views.v_configuracion import render_configuracion
from views.v_consultas import render_consultas 


st.set_page_config(
    page_title="Hierrosan ERP", 
    # page_icon=icon_path, 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CARGA DE ASSETS Y ESTILOS (Incluye tu firma y el CSS embebido)
# st.sidebar.load_footer()

st.markdown("""
    <style>
    /* Fondo principal de la aplicación */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Sidebar Blanco Puro y Texto Negro */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #dee2e6;
    }
    
    /* Forzar visibilidad de todo el texto en el sidebar */
    [data-testid="stSidebar"] * {
        color: #212529 !important;
    }

    /* Estilo de botones de navegación (Radio Buttons) */
    div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 6px;
        border: 1px solid #e9ecef;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label:hover {
        border-color: #714B67;
        background-color: #f1eff1;
    }

    /* Ajuste de Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1a2c38 !important;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    logo_display_path = os.path.join("assets", "logo.png")

    # Inicialización de Session State
    if 'menu_option' not in st.session_state:
        st.session_state.menu_option = "📊 Auditoría"
    if 'form_version' not in st.session_state:
        st.session_state.form_version = 0
    if 'config_lucro' not in st.session_state:
        st.session_state.config_lucro = 21.0
    if 'last_factura_id' not in st.session_state:
        st.session_state.last_factura_id = None

    # --- MENÚ LATERAL ---
    with st.sidebar:
        if os.path.exists(logo_display_path):
            st.image(logo_display_path, use_container_width=True)
        else:
            st.error("No se encontró assets/logo.png")
        
        st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.8rem;'>v18.0.1 Stable</p>", unsafe_allow_html=True)
        st.divider()
     
        menu = st.radio(
            "Navegación",
            ["Auditoría de Factura", "Boletos de Cobro", "Consultas Históricas", "Configuración"],
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
    elif menu == "Configuración":
        render_configuracion()





if __name__ == "__main__":
    main()