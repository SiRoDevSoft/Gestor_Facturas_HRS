import streamlit as st
import os
import time

def render_login(auth):
    # --- 1. INICIALIZACIÓN DE ESTADO (Evita el AttributeError) ---
    if "loading" not in st.session_state:
        st.session_state.loading = False

    # --- 2. ESTILO PERSONALIZADO (CSS) ---
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

    _, col_central, _ = st.columns([2, 3, 2])

    with col_central:
        # --- LOGO ---
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=300)
        else:
            st.markdown("<h2 style='text-align: center;'>HIERROSAN</h2>", unsafe_allow_html=True)

        st.divider()

        tab1, tab2 = st.tabs(["Ingresar", "Recuperar"])
        
        with tab1:
            # Deshabilitamos los inputs mientras carga para que no cambien nada
            u = st.text_input("Usuario", placeholder="Tu nombre de usuario", key="login_user", disabled=st.session_state.loading)
            p = st.text_input("Clave", type="password", placeholder="Tu contraseña", key="login_pass", disabled=st.session_state.loading)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # El botón se deshabilita si loading es True
            if st.button("Entrar al Sistema", use_container_width=True, type="secondary", disabled=st.session_state.loading):
                if u and p:
                    st.session_state.loading = True
                    st.rerun() 
                else:
                    st.warning("Por favor, completar todos los campos.")

            # --- LÓGICA DE VERIFICACIÓN ---
            if st.session_state.loading:
                with st.spinner("Conectando con el servidor..."):
                    # Aquí es donde el sistema se comunica con Neon (San Pablo)
                    if auth.verificar_login(u, p):
                        st.session_state.autenticado = True
                        st.session_state.loading = False
                        st.success("Acceso correcto.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Usuario o clave incorrectos.")
                        st.session_state.loading = False
                        # No hacemos rerun aquí para que el mensaje de error permanezca en pantalla
        
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

    st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'><br>Hierrosan ERP_MOVISTAR v18.05</p>", unsafe_allow_html=True)