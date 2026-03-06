from pathlib import Path

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






