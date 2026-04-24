import streamlit as st
import gym_app.services as services

def perfil_page():
    u = st.session_state.data.get("user", {})
    LISTA_OBJETIVOS = services.LISTA_OBJETIVOS
    st.markdown("### ⚙️ Configuración de Perfil")
    with st.form("edit_perfil"):
        st.markdown("#### 👤 Información Personal")
        n_nombre = st.text_input("Nombre", u.get('nombre', ''))
        n_sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if u.get('sexo', 'Masculino') == 'Masculino' else 1)
        st.markdown("#### 📏 Medidas y Frecuencia")
        n_peso = st.number_input("Peso (Lbs)", value=float(u.get('peso_lb', 160)))
        c_f, c_i, c_e, c_d = st.columns(4)
        n_pies = c_f.number_input("Pies", 3, 8, value=int(u.get('pies', 5)))
        n_pulgadas = c_i.number_input("Pulgadas", 0, 11, value=int(u.get('pulgadas', 7)))
        n_edad = c_e.number_input("Edad", 12, 100, value=int(u.get('edad', 25)))
        n_dias = c_d.selectbox("Días/Semana", [3, 4, 5], index=[3, 4, 5].index(u.get('dias_entreno', 5)))
        st.markdown("#### 🎯 Mis Objetivos")
        objs_actuales = [o for o in u.get('objetivos', []) if o in LISTA_OBJETIVOS]
        n_objs = st.multiselect("Editar objetivos:", LISTA_OBJETIVOS, default=objs_actuales)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("✅ Actualizar mi Perfil", use_container_width=True):
            est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
            nueva_data_user = {
                "nombre": n_nombre, "sexo": n_sexo, "peso_lb": n_peso, "pies": n_pies,
                "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": n_objs,
                "edad": n_edad, "dias_entreno": n_dias
            }
            st.session_state.data["user"] = nueva_data_user
            st.session_state.data["rutina_semanal"] = services.generar_rutina_ia(nueva_data_user, services.genai.GenerativeModel('gemini-2.0-flash'))
            services.guardar_todo(st.session_state.data, st.session_state.usuario_logueado)
            services.actualizar_perfil_usuario(st.session_state.usuario_logueado, nueva_data_user)
            st.success("¡Perfil y rutina actualizados con éxito!")
            st.rerun()
    st.markdown("---")
    st.info("💡 Tip: Ve a la sección 'Mi Rutina' para regenerar tu rutina inteligente con los nuevos datos.")

if __name__ == "__main__":
    perfil_page()
