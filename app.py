import streamlit as st
import os

def nav_page(filename):
    abs_path = os.path.join(os.path.dirname(__file__), "pages", filename)
    rel_path = os.path.relpath(abs_path, os.getcwd())
    st.switch_page(rel_path.replace("\\", "/"))

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
    nav_page("01_Login.py")
elif not st.session_state.data.get("perfil_completado", False):
    nav_page("04_Perfil.py")
else:
    # Navegación básica entre Dashboard y Perfil
    st.markdown("<h1 class='main-header'>Gym Pro AI</h1>", unsafe_allow_html=True)
    nav = st.sidebar.radio("Navegación", ["Dashboard", "Perfil"], index=0)
    if nav == "Dashboard":
        nav_page("03_Dashboard.py")
    elif nav == "Perfil":
        nav_page("04_Perfil.py")
