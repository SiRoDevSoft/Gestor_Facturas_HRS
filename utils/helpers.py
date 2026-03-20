from pathlib import Path
import os
import streamlit as st


def clean_currency(value):
    """
    Transforma formatos de moneda (ej: '1.234,56' o '$ 1.234,56') 
    en valores numéricos operables (float).
    """
    if value is None: 
        return 0.0
    
    # Convertimos a string y quitamos espacios en los extremos
    s = str(value).strip()
    
    if not s: 
        return 0.0

    # 1. Quitamos el símbolo de moneda si existe
    s = s.replace('$', '').strip()
    
    # 2. Manejo de formato contable: 
    # Quitamos puntos de miles (1.234,56 -> 1234,56)
    # Cambiamos coma decimal por punto (1234,56 -> 1234.56)
    s = s.replace('.', '').replace(',', '.')
    
    try:
        # 3. Conversión final a flotante
        return float(s)
    except ValueError:
        # Si el texto no es un número (ej: "Línea"), devolvemos 0.0 para no romper la suma
        return 0.0



def configure_ui_assets(is_authenticated=False):
    """Carga CSS y, si el usuario está logueado, inyecta el botón de menú."""
    # 1. Cargar el CSS base (siempre, para que el login se vea bien)
    css_path = os.path.join("assets", "css", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # 2. Inyectar el botón de Menú SOLO si ya pasó el login
    if is_authenticated:
        st.markdown("""
            <button id="custom-sidebar-btn" 
                    onclick="window.parent.document.querySelector('[data-testid=\\'stSidebarCollapseButton\\']').click()">
                ☰ Menú
            </button>
        """, unsafe_allow_html=True)


