import streamlit as st
import os

def render_login(auth):
    # --- 1. ESTILO PERSONALIZADO (CSS) ---
    # Esto centra el logo y asegura que el botón primario sea rojo/naranja
    st.markdown("""
        <style>
        .stButton > button {
            border-radius: 5px;
            height: 3em;
        }
        div[data-testid="stImage"] > img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. ESTRUCTURA DE COLUMNAS (CENTRADO) ---
    # Creamos un margen a los lados (1.2) y el contenido al centro (1.5)
    # Esto evita que el login ocupe todo el ancho de la pantalla.
    _, col_central, _ = st.columns([2, 3, 2])

    with col_central:
        # --- LOGO ---
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            # Usamos un ancho fijo (300) para que no sea gigante
            st.image(logo_path, width=300)
        else:
            st.markdown("<h2 style='text-align: center;'>HIERROSAN</h2>", unsafe_allow_html=True)

        st.divider()

        # --- FORMULARIO CON TABS ---
        tab1, tab2 = st.tabs(["🔑 Ingresar", "🛠️ Recuperar"])
        
        with tab1:
            # Campos de entrada
            u = st.text_input("Usuario", placeholder="Tu nombre de usuario", key="login_user")
            p = st.text_input("Clave", type="password", placeholder="Tu contraseña", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True) # Espaciado simple
            
            # Botón de acceso resaltado
            if st.button("Entrar al Sistema", use_container_width=True, type="primary"):
                if auth.verificar_login(u, p):
                    st.session_state.autenticado = True
                    st.success("Acceso concedido")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verificá usuario y clave.")

        with tab2:
            st.info("Ingresá tu usuario para ver la pregunta de seguridad.")
            u_r = st.text_input("Usuario", key="user_recuperar", placeholder="Nombre de usuario")
            
            if u_r:
                preg = auth.obtener_pregunta(u_r)
                if preg:
                    st.markdown(f"**Pregunta de seguridad:**\n\n> *{preg}*")
                    res = st.text_input("Tu respuesta", key="resp_recuperar")
                    new_p = st.text_input("Nueva Clave", type="password", key="new_pass")
                    
                    if st.button("Resetear Contraseña", use_container_width=True):
                        if auth.verificar_y_resetear(u_r, res, new_p):
                            st.success("¡Clave actualizada correctamente!")
                            st.info("Ya podés volver a la pestaña 'Ingresar'.")
                        else:
                            st.error("La respuesta es incorrecta.")
                else:
                    st.warning("El usuario no existe en la base de datos.")

    # Pie de página opcional
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'><br>Hierrosan ERP_MOVISTAR v18.05</p>", unsafe_allow_html=True)

# --- NOTA PARA EL MAIN ---
# Asegúrate de llamar a esta función pasando tu objeto de autenticación:
# render_login(mi_objeto_auth)
