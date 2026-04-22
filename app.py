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

# --- LÓGICA DE SELECCIÓN DE MODELO (SOLUCIÓN AL ERROR 404) ---
@st.cache_resource
def inicializar_modelo():
    # Lista de nombres de modelos en orden de modernidad/compatibilidad
    nombres_modelos = [
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
        'gemini-pro'
    ]
    
    for nombre in nombres_modelos:
        try:
            m = genai.GenerativeModel(model_name=nombre, safety_settings=safety_settings)
            # Prueba rápida para ver si el modelo responde
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue
    return None

model = inicializar_modelo()

# --- FUNCIÓN MAESTRA DE SEGURIDAD IA ---
def llamar_ia_con_seguridad(prompt):
    if model is None:
        return "❌ **Error Crítico:** No se pudo conectar con ningún modelo de Google Gemini. Verifica tu API Key o actualiza la librería con `pip install -U google-generativeai`."
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "La IA no pudo generar una respuesta clara. Intenta de nuevo."
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return "⚠️ **Límite de cuota alcanzado:** Espera 60 segundos antes de reintentar."
        return f"❌ Error de conexión: {err}"

# --- GESTIÓN DE USUARIOS ---
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
    prompt = f"Analiza estos datos de salud: Sexo {user_data['sexo']}, Edad {user_data['edad']}, IMC {imc:.2f}, Metas {user_data['objetivos']}. Dime su categoría de peso y peso ideal en lbs."
    return llamar_ia_con_seguridad(prompt)

def generar_dieta_ia(user_data):
    prompt = f"Crea una dieta diaria para {user_data['nombre']}, edad {user_data['edad']}, objetivos: {user_data['objetivos']}. Incluye macros y menú."
    return llamar_ia_con_seguridad(prompt)

def generar_rutina_ia(user_data):
    prompt = f"Crea una rutina de ejercicios para {user_data['edad']} años, sexo {user_data['sexo']}, frecuencia {user_data['dias_entreno']} días/sem, meta: {user_data['objetivos']}."
    return llamar_ia_con_seguridad(prompt)

# --- INTERFAZ ---
if "usuario_logueado" not in st.session_state:
    st.title("🏋️ Gym Pro AI")
    t1, t2 = st.tabs(["Login", "Registro"])
    with t1:
        u = st.text_input("Usuario", key="u_log")
        p = st.text_input("Contraseña", type="password", key="p_log")
        if st.button("Entrar"):
            users = cargar_usuarios()
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                st.session_state.data = cargar_todo()
                st.rerun()
            else: st.error("Acceso denegado.")
    with t2:
        nu = st.text_input("Nuevo Usuario", key="u_reg")
        np = st.text_input("Nueva Contraseña", type="password", key="p_reg")
        if st.button("Crear Cuenta"):
            users = cargar_usuarios()
            if nu and np:
                users[nu] = {"password": np, "perfil": estructura_vacia(nu)["user"]}
                guardar_usuarios(users)
                st.success("Cuenta creada.")

else:
    with st.sidebar:
        st.title(f"Hola {st.session_state.usuario_logueado}")
        opc = st.radio("Menú", ["Perfil", "Dieta IA", "Rutina IA", "Progreso"])
        if st.button("Cerrar Sesión"):
            del st.session_state.usuario_logueado
            st.rerun()

    if opc == "Perfil":
        st.header("📊 Datos de Salud")
        user = st.session_state.data["user"]
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("form_perfil"):
                n_nom = st.text_input("Nombre", value=user["nombre"])
                n_edad = st.number_input("Edad", 14, 100, value=user.get("edad", 25))
                n_sexo = st.selectbox("Sexo", ["Hombre", "Mujer"], index=0 if user["sexo"]=="Hombre" else 1)
                n_peso = st.number_input("Peso (lbs)", 50, 500, value=user["peso_lb"])
                n_pies = st.number_input("Pies", 3, 8, value=user["pies"])
                n_pulg = st.number_input("Pulgadas", 0, 11, value=user["pulgadas"])
                n_dias = st.slider("Días entreno", 1, 7, value=user.get("dias_entreno", 3))
                objs = st.multiselect("Metas", ["Ganar masa", "Perder grasa", "Fuerza", "Salud"], default=user["objetivos"])
                
                if st.form_submit_button("Guardar y Analizar"):
                    est_m = ((n_pies * 12) + n_pulg) * 0.0254
                    new_data = {
                        "nombre": n_nom, "sexo": n_sexo, "peso_lb": n_peso, 
                        "pies": n_pies, "pulgadas": n_pulg, "estatura_m": est_m, 
                        "objetivos": objs, "edad": n_edad, "dias_entreno": n_dias
                    }
                    st.session_state.data["user"] = new_data
                    with st.spinner("Analizando con IA..."):
                        st.session_state.data["analisis_salud"] = obtener_analisis_ia(new_data)
                    guardar_todo(st.session_state.data)
                    actualizar_perfil_usuario(st.session_state.usuario_logueado, new_data)
                    st.rerun()
        with col2:
            st.info(st.session_state.data.get("analisis_salud", "Sin análisis."))

    elif opc == "Dieta IA":
        st.header("🍎 Nutrición")
        if st.button("Generar Dieta"):
            st.session_state.data["dieta_semanal"] = generar_dieta_ia(st.session_state.data["user"])
            guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["dieta_semanal"])

    elif opc == "Rutina IA":
        st.header("🏋️ Entrenamiento")
        if st.button("Generar Rutina"):
            st.session_state.data["rutina_semanal"] = generar_rutina_ia(st.session_state.data["user"])
            guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["rutina_semanal"])

    elif opc == "Progreso":
        st.header("📈 Mi Progreso")
        nuevo_p = st.number_input("Peso (lbs)", 50, 500)
        if st.button("Guardar"):
            st.session_state.data["historial_peso"].append({"fecha": str(pd.Timestamp.now().date()), "peso": nuevo_p})
            guardar_todo(st.session_state.data)
            st.rerun()
        if st.session_state.data["historial_peso"]:
            st.line_chart(pd.DataFrame(st.session_state.data["historial_peso"]).set_index("fecha"))
