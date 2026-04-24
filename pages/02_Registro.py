import streamlit as st
import gym_app.services as services

def registro_page():
    st.markdown("""
    <div class="section-card section-card-register">
        <h2 class="section-card-title">📝 Registrarse</h2>
    </div>
    """, unsafe_allow_html=True)
    with st.form("signup_form"):
        st.markdown("**👤 Crear nueva cuenta**")
        signup_user = st.text_input("Nombre de usuario", key="signup_user", placeholder="Elige tu usuario")
        signup_pass = st.text_input("Contraseña", type="password", key="signup_pass", placeholder="Mínimo 6 caracteres")
        signup_pass_conf = st.text_input("Confirmar contraseña", type="password", key="signup_pass_conf", placeholder="Repite tu contraseña")
        st.markdown("**📋 Datos de perfil**")
        nombre = st.text_input("¿Cuál es tu nombre completo?", placeholder="Ej: Juan Pérez")
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0)
        st.markdown("**📏 Medidas**")
        c_p, c_ft, c_in, c_ed = st.columns(4)
        peso = c_p.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        pies = c_ft.number_input("Pies", 3, 8, 5)
        pulgadas = c_in.number_input("Pulg", 0, 11, 7)
        edad = c_ed.number_input("Edad", 12, 100, 25)
        st.markdown("**💪 Entrenamiento**")
        c_d, c_o = st.columns([1, 2])
        dias_e = c_d.selectbox("Días/Semana", [3, 4, 5], index=2)
        LISTA_OBJETIVOS = services.LISTA_OBJETIVOS
        objs = c_o.multiselect("🎯 Tus metas:", LISTA_OBJETIVOS, max_selections=5)
        signup_btn = st.form_submit_button("✅ Crear Cuenta", use_container_width=True)
        if signup_btn:
            if not signup_user or not signup_pass:
                st.error("❌ Usuario y contraseña son requeridos")
            elif len(signup_pass) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres")
            elif signup_pass != signup_pass_conf:
                st.error("❌ Las contraseñas no coinciden")
            elif services.usuario_existe(signup_user):
                st.error("❌ El usuario ya existe")
            elif not nombre or not objs:
                st.error("❌ Completa nombre y selecciona al menos un objetivo")
            else:
                est_m = ((pies * 12) + pulgadas) * 0.0254
                datos_perfil = {
                    "nombre": nombre,
                    "sexo": sexo,
                    "peso_lb": peso,
                    "pies": pies,
                    "pulgadas": pulgadas,
                    "estatura_m": est_m,
                    "edad": edad,
                    "dias_entreno": dias_e,
                    "objetivos": objs
                }
                exito, mensaje = services.registrar_usuario(signup_user, signup_pass, datos_perfil)
                if exito:
                    st.success(mensaje)
                    st.info("✅ Ahora puedes iniciar sesión con tu nueva cuenta")
                    if st.button("Volver al Login", use_container_width=True, key="volver_login"):
                        st.switch_page("pages/01_Login.py")
                else:
                    st.error(f"❌ {mensaje}")
    if st.button("Volver al Login", use_container_width=True, key="volver_login2"):
        st.switch_page("pages/01_Login.py")

if __name__ == "__main__":
    registro_page()
