import streamlit as st
import time

def render_login(auth_manager):
    st.container()
    with st.columns([1, 2, 1])[1]:  # Centramos el formulario
        st.title("🔐 Acceso al Sistema")
        
        tab_login, tab_recuperar = st.tabs(["Ingresar", "Olvidé mi clave"])

        # --- TAB: LOGIN ---
        with tab_login:
            user = st.text_input("Usuario", key="login_user")
            password = st.text_input("Contraseña", type="password", key="login_pass")
            
            if st.button("Entrar", use_container_width=True):
                if auth_manager.verificar_login(user, password):
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = user
                    st.success("¡Bienvenido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        # --- TAB: RECUPERACIÓN ---
        with tab_recuperar:
            user_rec = st.text_input("Ingresa tu usuario para recuperar", key="rec_user")
            if user_rec:
                # Aquí auth_manager debería tener un método para traer la pregunta
                pregunta = auth_manager.obtener_pregunta(user_rec)
                if pregunta:
                    st.info(f"Pregunta de seguridad: {pregunta}")
                    respuesta = st.text_input("Tu respuesta", key="rec_ans")
                    nueva_pass = st.text_input("Nueva contraseña", type="password", key="new_pass")
                    
                    if st.button("Restablecer", use_container_width=True):
                        if auth_manager.verificar_y_resetear(user_rec, respuesta, nueva_pass):
                            st.success("Contraseña actualizada. Ya puedes loguearte.")
                        else:
                            st.error("Respuesta incorrecta.")
                else:
                    st.warning("El usuario no existe.")