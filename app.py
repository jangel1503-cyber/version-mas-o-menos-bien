import streamlit as st
import os

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide", initial_sidebar_state="expanded")
def aplicar_estilos():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
aplicar_estilos()

# --- NAVEGACIÓN MULTIPÁGINA ---
if 'usuario_logueado' not in st.session_state:
    st.session_state.usuario_logueado = None
if 'data' not in st.session_state:
    st.session_state.data = {
        "perfil_completado": False,
        "user": {},
        "rutina_semanal": {},
        "historial_pesos": [],
        "historial_entrenamientos": [],
        "pr_por_ejercicio": {},
        "fecha_ultima_rotacion": None,
        "dieta_semanal": {}
    }

# Redirigir según estado y navegación
if not st.session_state.usuario_logueado:
    st.switch_page("Login")
elif not st.session_state.data.get("perfil_completado", False):
    st.switch_page("Perfil")
else:
    # Navegación básica entre Dashboard y Perfil
    st.markdown("<h1 class='main-header'>Gym Pro AI</h1>", unsafe_allow_html=True)
    nav = st.sidebar.radio("Navegación", ["Dashboard", "Perfil"], index=0)
    if nav == "Dashboard":
        st.switch_page("Dashboard")
    elif nav == "Perfil":
        st.switch_page("Perfil")
