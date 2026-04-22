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

# Filtros de seguridad
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Ajuste de modelo para evitar el Error 404
# Intentamos con la ruta completa que requiere la API v1beta
MODEL_NAME = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(model_name=MODEL_NAME, safety_settings=safety_settings)

# --- FUNCIÓN MAESTRA DE SEGURIDAD IA ---
def llamar_ia_con_seguridad(prompt):
    """Maneja las llamadas a la IA y captura errores de cuota o modelo."""
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "La IA no pudo generar una respuesta. Intenta de nuevo."
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return "⚠️ **Límite alcanzado:** Espera 60 segundos."
        if "404" in error_msg:
            return "❌ **Error de Modelo (404):** El modelo no fue encontrado. Intenta cambiar 'models/gemini-1.5-flash' por 'gemini-pro' en el código."
        return f"❌ Error: {error_msg}"

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
        "dieta_semanal": "Presiona el botón para generar.",
        "rutina_semanal": "Presiona el botón para generar.",
        "analisis_salud": "Completa tu perfil para ver el análisis."
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

# --- FUNCIONES IA ---
def obtener_analisis_ia(user_data):
    est_m = ((user_data['pies'] * 12) + user_data['pulgadas']) * 0.0254
    peso_kg = user_data['peso_lb'] * 0.453592
    imc = peso_kg / (est_m**2) if est_m > 0 else 0
    prompt = f"Analiza estos datos de salud: Sexo {user_data['sexo']}, Edad {user_data['edad']}, IMC {imc:.2f}, Metas {user_data['objetivos']}. Sé breve."
    return llamar_ia_con_seguridad(prompt)

def generar_dieta_ia(user_data):
    prompt = f"Crea una dieta para {user_data['nombre']}, {user_data['edad']} años, meta: {user_data['objetivos']}."
    return llamar_ia_con_seguridad(prompt)

def generar_rutina_ia(user_data):
    prompt = f"Crea una rutina para {user_data['edad']} años, sexo {user_data['sexo']}, meta: {user_data['objetivos']}."
    return llamar_ia_con_seguridad(prompt)

# --- INTERFAZ ---
if "usuario_logueado" not in st.session_state:
    st.title("🏋️ Gym Pro AI")
    t1, t2 = st.tabs(["Entrar", "Registro"])
    with t1:
        u = st.text_input("Usuario", key="l_u")
        p = st.text_input("Contraseña", type="password", key="l_p")
        if st.button("Ingresar"):
            users = cargar_usuarios()
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                st.session_state.data = cargar_todo()
                st.rerun()
            else: st.error("Error en credenciales")
    with t2:
        nu = st.text_input("Nuevo Usuario", key="r_u")
        np = st.text_input("Nueva Contraseña", type="password", key="r_p")
        if st.button("Registrar"):
            users = cargar_usuarios()
            if nu and np:
                users[nu] = {"password": np, "perfil": estructura_vacia(nu)["user"]}
                guardar_usuarios(users)
                st.success("¡Hecho! Loguéate.")

else:
    with st.sidebar:
        st.title(f"Hola {st.session_state.usuario_logueado}")
        opc = st.radio("Navegación", ["Perfil", "Dieta IA", "Rutina IA", "Progreso"])
        if st.button("Cerrar Sesión"):
            del st.session_state.usuario_logueado
            st.rerun()

    if opc == "Perfil":
        st.header("📊 Perfil y Salud")
        user = st.session_state.data["user"]
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("p_form"):
                n_nom = st.text_input("Nombre", value=user["nombre"])
                n_edad = st.number_input("Edad", 14, 100, value=user.get("edad", 25))
                n_sexo = st.selectbox("Sexo", ["Hombre", "Mujer"], index=0 if user["sexo"]=="Hombre" else 1)
                n_peso = st.number_input("Peso (lbs)", 50, 500, value=user["peso_lb"])
                n_pies = st.number_input("Pies", 3, 8, value=user["pies"])
                n_pulg = st.number_input("Pulgadas", 0, 11, value=user["pulgadas"])
                n_dias = st.slider("Días entreno", 1, 7, value=user.get("dias_entreno", 3))
                objs = st.multiselect("Metas", ["Masa muscular", "Perder grasa", "Fuerza", "Salud"], default=user["objetivos"])
                
                if st.form_submit_button("Guardar y Analizar"):
                    est_m = ((n_pies * 12) + n_pulg) * 0.0254
                    new_data = {"nombre": n_nom, "sexo": n_sexo, "peso_lb": n_peso, "pies": n_pies, "pulgadas": n_pulg, "estatura_m": est_m, "objetivos": objs, "edad": n_edad, "dias_entreno": n_dias}
                    st.session_state.data["user"] = new_data
                    with st.spinner("IA Analizando..."):
                        st.session_state.data["analisis_salud"] = obtener_analisis_ia(new_data)
                    guardar_todo(st.session_state.data)
                    actualizar_perfil_usuario(st.session_state.usuario_logueado, new_data)
                    st.rerun()
        with col2:
            st.info(st.session_state.data.get("analisis_salud", "Sin análisis."))

    elif opc == "Dieta IA":
        st.header("🍎 Dieta")
        if st.button("Generar Plan"):
            st.session_state.data["dieta_semanal"] = generar_dieta_ia(st.session_state.data["user"])
            guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["dieta_semanal"])

    elif opc == "Rutina IA":
        st.header("🏋️ Rutina")
        if st.button("Generar Rutina"):
            st.session_state.data["rutina_semanal"] = generar_rutina_ia(st.session_state.data["user"])
            guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["rutina_semanal"])

    elif opc == "Progreso":
        st.header("📈 Progreso")
        nuevo_p = st.number_input("Peso (lbs)", 50, 500)
        if st.button("Registrar"):
            st.session_state.data["historial_peso"].append({"fecha": str(pd.Timestamp.now().date()), "peso": nuevo_p})
            guardar_todo(st.session_state.data)
            st.rerun()
        if st.session_state.data["historial_peso"]:
            st.line_chart(pd.DataFrame(st.session_state.data["historial_peso"]).set_index("fecha"))
