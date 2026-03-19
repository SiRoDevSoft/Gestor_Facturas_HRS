# import os
# import streamlit as st
# from views.v_auditoria import render_auditoria
# from views.v_abonos import render_abonos
# from views.v_configuracion import render_configuracion
# from views.v_consultas import render_consultas 
# from views.v_login import render_login
# from auth_db import AuthManager

# auth = AuthManager()

# def main():
#     # Inicializamos el estado de autenticación
#     if 'autenticado' not in st.session_state:
#         st.session_state.autenticado = False

#     if not st.session_state.autenticado:
#         render_login(auth)
#         return

# st.set_page_config(
#     page_title="Hierrosan ERP", 
#     # page_icon=icon_path, 
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # 2. CARGA DE ASSETS Y ESTILOS (Incluye tu firma y el CSS embebido)
# # st.sidebar.load_footer()

# st.markdown("""
#     <style>
#     /* 1. Fondo principal y Color de Texto Global (Vital para móviles) */
#     .stApp {
#         background-color: #f8f9fa !important;
#     }
    
#     /* Forzar que todo el texto fuera del sidebar sea gris oscuro/negro */
#     .stApp * {
#         color: #212529;
#     }

#     /* 2. Sidebar Blanco Puro */
#     [data-testid="stSidebar"] {
#         background-color: #ffffff !important;
#         border-right: 1px solid #dee2e6;
#     }
    
#     /* Texto del Sidebar */
#     [data-testid="stSidebar"] * {
#         color: #212529 !important;
#     }

#     /* 3. Estilo de Radio Buttons (Menú) */
#     div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label {
#         background-color: #f8f9fa !important;
#         padding: 12px;
#         border-radius: 6px;
#         margin-bottom: 6px;
#         border: 1px solid #e9ecef;
#         width: 100%;
#     }
    
#     /* Texto dentro de los botones del menú */
#     div[data-testid="stSidebarUserContent"] div[role="radiogroup"] label div {
#         color: #212529 !important;
#     }

#     /* 4. Métricas (Números grandes) */
#     [data-testid="stMetricValue"] {
#         color: #1a2c38 !important;
#     }
    
#     /* Estilo para los dataframes (tablas) para que no se vean blancos sobre blanco */
#     [data-testid="stTable"], [data-testid="stDataFrame"] {
#         background-color: #ffffff;
#     }
#     </style>
# """, unsafe_allow_html=True)
# def main():
#     logo_display_path = os.path.join("assets", "logo.png")

#     # Inicialización de Session State
#     if 'menu_option' not in st.session_state:
#         st.session_state.menu_option = "📊 Auditoría"
#     if 'form_version' not in st.session_state:
#         st.session_state.form_version = 0
#     if 'config_lucro' not in st.session_state:
#         st.session_state.config_lucro = 21.0
#     if 'last_factura_id' not in st.session_state:
#         st.session_state.last_factura_id = None

#     # --- MENÚ LATERAL ---
#     with st.sidebar:
#         if os.path.exists(logo_display_path):
#             st.image(logo_display_path, use_container_width=True)
#         else:
#             st.error("No se encontró assets/logo.png")
        
#         st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.8rem;'>v18.0.1 Stable</p>", unsafe_allow_html=True)
#         st.divider()
     
#         menu = st.radio(
#             "Navegación",
#             ["Auditoría de Factura", "Boletos de Cobro", "Consultas Históricas", "Configuración"],
#             index=0
#         )
#         st.divider()

   

#     # --- LÓGICA DE NAVEGACIÓN ---
#     if menu == "Auditoría de Factura":
#         render_auditoria()
#     elif menu == "Boletos de Cobro":
#         render_abonos()
#     elif menu == "Consultas Históricas": 
#         render_consultas()
#     elif menu == "Configuración":
#         render_configuracion()





# if __name__ == "__main__":
#     main()

##################################################

import os
import streamlit as st
from views.v_auditoria import render_auditoria
from views.v_abonos import render_abonos
from views.v_configuracion import render_configuracion
from views.v_consultas import render_consultas 
from views.v_login import render_login
from models.auth_db import AuthManager

# 1. Configuración de página (SIEMPRE PRIMERO)
st.set_page_config(
    page_title="Hierrosan ERP", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializamos el gestor de seguridad
auth = AuthManager()

def main():
    # --- A: INICIALIZACIÓN DE TODAS LAS VARIABLES DE ESTADO ---
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

    # --- B: REGISTRO INICIAL (Comentar después de la primera ejecución) ---
    # auth.registrar_usuario("admin", "1234", "Color?", "Azul")
    
    # --- C: CONTROL DE ACCESO ---
    if not st.session_state.autenticado:
        render_login(auth)
        return # Frena la ejecución si no está logueado

    # --- D: SI ESTÁ LOGUEADO, CARGAMOS LA UI ---
    
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

    # --- SIDEBAR ---
    # with st.sidebar:
    #     logo_display_path = os.path.join("assets", "logo.png")
        
    #     if st.button("Cerrar Sesión"):
    #         st.session_state.autenticado = False
    #         st.rerun()
        
    #     if os.path.exists(logo_display_path):
    #         st.image(logo_display_path, use_container_width=True)
    #     else:
    #         st.error("No se encontró assets/logo.png")
        
    #     st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.8rem;'>v18.0.1 Stable</p>", unsafe_allow_html=True)
    #     st.divider()
    with st.sidebar:
        # 1. CSS para achicar el botón específicamente en la sidebar
        st.markdown("""
            <style>
            [data-testid="stSidebar"] .stButton > button {
                width: auto;
                padding: 2px 15px;
                font-size: 12px;
                height: 28px;
                color: #7f8c8d;
                border: 1px solid #dcdde1;
            }
            </style>
        """, unsafe_allow_html=True)

        # 2. Botón de Cerrar Sesión (Superior y Pequeño)
        if st.button("🚪 Cerrar Sesión", type="secondary"):
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
        st.markdown("<p style='text-align: center; color: #bdc3c7; font-size: 0.75rem; margin-top: -10px;'>v18.0.1 Stable</p>", unsafe_allow_html=True)
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