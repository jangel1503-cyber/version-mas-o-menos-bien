import streamlit as st
import gym_app.services as services
import os
import json

def login_page():
    st.markdown('<h1 class="main-header">💪 GYM PRO AI</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-card">
        <h3 class="hero-title">Tu Entrenador Personal Inteligente</h3>
        <p class="hero-subtitle">Entrenamientos personalizados con IA | Nutricion optimizada | Progreso garantizado</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="section-card section-card-login">
        <h2 class="section-card-title">🔐 Iniciar Sesion</h2>
    </div>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        login_user = st.text_input("👤 Nombre de usuario", key="login_user", placeholder="Ingresa tu usuario")
        login_pass = st.text_input("🔑 Contraseña", type="password", key="login_pass", placeholder="Ingresa tu contraseña")
        login_btn = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
        if login_btn:
            if login_user and login_pass:
                if services.validar_credenciales(login_user, login_pass):
                    st.session_state.usuario_logueado = login_user.lower()
                    datos_cargados = False
                    DB_FILE = services.DB_FILE
                    if os.path.exists(DB_FILE):
                        try:
                            with open(DB_FILE, "r", encoding='utf-8') as f:
                                all_data = json.load(f)
                                if st.session_state.usuario_logueado in all_data:
                                    st.session_state.data = all_data[st.session_state.usuario_logueado]
                                    datos_cargados = True
                        except:
                            pass
                    if not datos_cargados:
                        datos = services.obtener_datos_usuario(login_user)
                        st.session_state.data = {
                            "perfil_completado": True,
                            "user": datos,
                            "rutina_semanal": {},
                            "historial_pesos": [],
                            "historial_entrenamientos": [],
                            "pr_por_ejercicio": {},
                            "fecha_ultima_rotacion": None,
                            "dieta_semanal": {}
                        }
                        services.guardar_todo(st.session_state.data, st.session_state.usuario_logueado)
                    st.success("✅ ¡Sesión iniciada correctamente!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.warning("⚠️ Completa todos los campos")
    st.markdown("""
    <div style='text-align:center; margin-top:2em;'>
        <strong>¿No tienes usuario?</strong>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📝 Registrarse aquí", use_container_width=True, key="show_register_page"):
        st.switch_page("pages/02_Registro.py")

if __name__ == "__main__":
    login_page()
