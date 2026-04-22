import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Gym Pro AI", page_icon="🏋️‍♂️", layout="wide")

DB_FILE = "gym_data.json"
USERS_FILE = "user_data.json"

# Cargar API key
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)

# Filtros de seguridad para contenido de salud
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Usamos 1.5-flash para mayor estabilidad en la cuota gratuita
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# --- FUNCIÓN MAESTRA DE SEGURIDAD IA ---
def llamar_ia_con_seguridad(prompt):
    """Maneja las llamadas a la IA y captura errores de cuota (429)."""
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "La IA no pudo generar una respuesta en este momento."
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            return "⚠️ **Límite de peticiones alcanzado:** Google está procesando muchas solicitudes. Por favor, espera 60 segundos y vuelve a intentar."
        return f"❌ Error de conexión: {e}"

# --- GESTIÓN DE USUARIOS Y ARCHIVOS ---
def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w", encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

def actualizar_perfil_usuario(usuario, nueva_data):
    usuarios = cargar_usuarios()
    if usuario in usuarios:
        usuarios[usuario]["perfil"] = nueva_data
        guardar_usuarios(usuarios)

def estructura_vacia(nombre="Usuario"):
    return {
        "user": {
            "nombre": nombre, "sexo": "Hombre", "peso_lb": 160, 
            "pies": 5, "pulgadas": 8, "estatura_m": 1.72, 
            "objetivos": [], "edad": 25, "dias_entreno": 3
        },
        "historial_peso": [],
        "dieta_semanal": "Presiona el botón para generar tu plan.",
        "rutina_semanal": "Presiona el botón para generar tu rutina.",
        "analisis_salud": "Completa tu perfil para recibir el análisis."
    }

def cargar_todo():
    usuario = st.session_state.get("usuario_logueado")
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data.get(usuario, estructura_vacia(usuario))
        except: return estructura_vacia(usuario)
    return estructura_vacia(usuario)

def guardar_todo(data_usuario):
    usuario = st.session_state.get("usuario_logueado")
    todas_las_datas = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                todas_las_datas = json.load(f)
        except: todas_las_datas = {}
    
    todas_las_datas[usuario] = data_usuario
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(todas_las_datas, f, indent=4, ensure_ascii=False)

# --- NÚCLEO DE IA CON SEGURIDAD ---

def obtener_analisis_ia(user_data):
    est_m = ((user_data['pies'] * 12) + user_data['pulgadas']) * 0.0254
    peso_kg = user_data['peso_lb'] * 0.453592
    imc = peso_kg / (est_m**2) if est_m > 0 else 0
    
    prompt = f"""
    Analiza estos datos de salud de forma profesional:
    - Nombre: {user_data['nombre']}, Edad: {user_data['edad']}, Sexo: {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, IMC: {imc:.2f}
    - Objetivos: {", ".join(user_data['objetivos'])}
    Determina categoría de peso, peso ideal en libras y consejos motivadores.
    """
    return llamar_ia_con_seguridad(prompt)

def generar_dieta_ia(user_data):
    prompt = f"""
    Eres un Nutricionista experto. Crea un plan para:
    - {user_data['nombre']}, {user_data['edad']} años, {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, Entrena: {user_data['dias_entreno']} días/sem.
    - Objetivos: {", ".join(user_data['objetivos'])}
    Incluye macros detallados, menú de un día y tips de hidratación.
    """
    return llamar_ia_con_seguridad(prompt)

def generar_rutina_ia(user_data):
    prompt = f"""
    Eres un Entrenador Personal. Diseña una rutina para:
    - Edad: {user_data['edad']} años, Sexo: {user_data['sexo']}
    - Frecuencia: {user_data['dias_entreno']} días/semana.
    - Metas: {", ".join(user_data['objetivos'])}
    Ajusta series y repeticiones según el objetivo y la edad. Formato Markdown.
    """
    return llamar_ia_con_seguridad(prompt)

# --- INTERFAZ ---

if "usuario_logueado" not in st.session_state:
    st.title("🏋️ Gym Pro AI")
    t1, t2 = st.tabs(["Login", "Registro"])
    with t1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            users = cargar_usuarios()
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                st.session_state.data = cargar_todo()
                st.rerun()
            else: st.error("Datos incorrectos")
    with t2:
        nu = st.text_input("Nuevo Usuario")
        np = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear Cuenta"):
            users = cargar_usuarios()
            if nu and np:
                users[nu] = {"password": np, "perfil": estructura_vacia(nu)["user"]}
                guardar_usuarios(users)
                st.success("¡Listo! Inicia sesión.")

else:
    with st.sidebar:
        st.title(f"Hola, {st.session_state.usuario_logueado}")
        opc = st.radio("Ir a:", ["Perfil y Salud", "Dieta IA", "Rutina IA", "Progreso"])
        if st.button("Salir"):
            del st.session_state.usuario_logueado
            st.rerun()

    if opc == "Perfil y Salud":
        st.header("📊 Análisis de Salud Inteligente")
        user = st.session_state.data["user"]
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            with st.form("perfil_form"):
                n_nom = st.text_input("Nombre", value=user["nombre"])
                n_edad = st.number_input("Edad", 14, 100, value=user.get("edad", 25))
                n_sexo = st.selectbox("Sexo", ["Hombre", "Mujer"], index=0 if user["sexo"]=="Hombre" else 1)
                n_peso = st.number_input("Peso (lbs)", 50, 500, value=user["peso_lb"])
                n_pies = st.number_input("Pies", 3, 8, value=user["pies"])
                n_pulg = st.number_input("Pulgadas", 0, 11, value=user["pulgadas"])
                n_dias = st.slider("Entrenos/semana", 1, 7, value=user.get("dias_entreno", 3))
                objs = st.multiselect("Objetivos", ["Ganar masa", "Perder grasa", "Fuerza", "Resistencia", "Salud"], default=user["objetivos"])
                
                if st.form_submit_button("Guardar y Analizar"):
                    est_m = ((n_pies * 12) + n_pulg) * 0.0254
                    new_data = {"nombre": n_nom, "sexo": n_sexo, "peso_lb": n_peso, "pies": n_pies, "pulgadas": n_pulg, "estatura_m": est_m, "objetivos
