import streamlit as st
import os

def render_login(auth):
    # --- LOGO SUPERIOR ---
    # Usamos la misma ruta que tenés en el main
    logo_path = os.path.join("assets", "logo.png")
    
    # Creamos columnas para centrar el logo
    col_logo, _ = st.columns([1, 2]) # Ajustá los pesos si lo querés más grande
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
        else:
            st.subheader("🏢 Hierrosan ERP") # Fallback si no encuentra el logo

    st.divider() # Una línea sutil para separar el logo del formulario

    # --- FORMULARIO DE ACCESO ---
    tab1, tab2 = st.tabs(["🔑 Ingresar", "🛠️ Recuperar"])
    
    with tab1:
        u = st.text_input("Usuario", placeholder="Tu nombre de usuario")
        p = st.text_input("Clave", type="password", placeholder="Tu contraseña")
        
        if st.button("Entrar al Sistema", use_container_width=True, type="primary"):
            if auth.verificar_login(u, p):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Verificá usuario y clave.")

    with tab2:
        st.info("Ingresá tu usuario para ver la pregunta de seguridad.")
        u_r = st.text_input("Usuario", key="user_recuperar")
        
        if u_r:
            preg = auth.obtener_pregunta(u_r)
            if preg:
                st.markdown(f"**Pregunta:** *{preg}*")
                res = st.text_input("Tu respuesta", key="resp_recuperar")
                new_p = st.text_input("Nueva Clave", type="password", key="new_pass")
                
                if st.button("Resetear Contraseña", use_container_width=True):
                    if auth.verificar_y_resetear(u_r, res, new_p):
                        st.success("¡Clave actualizada! Ya podés ir a la pestaña 'Ingresar'.")
                    else:
                        st.error("La respuesta es incorrecta.")
            else:
                st.error("El usuario no existe.")