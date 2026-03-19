import streamlit as st
import os

def render_login(auth):
    # --- CENTRADO PRINCIPAL ---
    # Creamos 3 columnas: [margen_izq, centro_formulario, margen_der]
    # El ratio [1, 2, 1] hace que el centro sea el doble de ancho que los lados
    _, col_central, _ = st.columns([1, 2, 1])

    with col_central:
        # --- LOGO ---
        logo_path = os.path.join("assets", "logo.png")
        
        c1, c2, c3 = st.columns([1, 2, 1]) 
        with c2: # El logo solo ocupa la parte del medio de la columna central
            if os.path.exists(logo_path):
                # width=150 o 200 suele ser el tamaño ideal para logins
                st.image(logo_path, width=200) 
            else:
                st.subheader("🏢 Hierrosan ERP")

        st.divider()

        # --- FORMULARIO DE ACCESO ---
        # Usamos un contenedor para agrupar visualmente los elementos
        with st.container():
            tab1, tab2 = st.tabs(["🔑 Ingresar", "🛠️ Recuperar"])
            
            with tab1:
                u = st.text_input("Usuario", placeholder="Tu nombre de usuario")
                p = st.text_input("Clave", type="password", placeholder="Tu contraseña")
                
                # El botón 'primary' le da el color resaltado (rojo/naranja según tu tema)
                if st.button("Entrar al Sistema", use_container_width=True, type="primary"):
                    if auth.verificar_login(u, p):
                        st.session_state.autenticado = True
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")

            with tab2:
                u_r = st.text_input("Usuario", key="user_recuperar", placeholder="Ingresá tu usuario")
                
                if u_r:
                    preg = auth.obtener_pregunta(u_r)
                    if preg:
                        st.info(f"**Pregunta de seguridad:**\n{preg}")
                        res = st.text_input("Tu respuesta", key="resp_recuperar")
                        new_p = st.text_input("Nueva Clave", type="password", key="new_pass")
                        
                        if st.button("Resetear Contraseña", use_container_width=True):
                            if auth.verificar_y_resetear(u_r, res, new_p):
                                st.success("¡Clave actualizada! Ya podés ingresar.")
                            else:
                                st.error("Respuesta incorrecta.")
                    else:
                        st.error("El usuario no existe.")
