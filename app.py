import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")

DB_FILE = "gym_data.json"
USERS_FILE = "user_data.json"

# API KEY
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)

# Configuración del modelo con manejo de errores directo
def configurar_modelo():
    # Lista de modelos por orden de probabilidad de éxito
    modelos_a_probar = ['gemini-1.5-flash', 'gemini-pro']
    
    for nombre in modelos_a_probar:
        try:
            m = genai.GenerativeModel(nombre)
            # Prueba de vida
            m.generate_content("Hola", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

# Inicializamos el modelo una sola vez
if "modelo_ia" not in st.session_state:
    st.session_state.modelo_ia = configurar_modelo()

# --- FUNCIÓN DE LLAMADA ---
def llamar_ia(prompt):
    if st.session_state.modelo_ia is None:
        return "❌ Error: No se pudo conectar con Gemini. Revisa tu conexión o API Key."
    try:
        response = st.session_state.modelo_ia.generate_content(prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Límite de cuota alcanzado. Espera un minuto."
        return f"❌ Error de IA: {e}"

# --- GESTIÓN DE DATOS ---
def cargar_json(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def guardar_json(archivo, datos):
    with open(archivo, "w", encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def estructura_inicial(nombre):
    return {
        "user": {"nombre": nombre, "sexo": "Hombre", "peso_lb": 160, "pies": 5, "pulgadas": 8, "edad": 25, "objetivos": [], "dias_entreno": 3},
        "historial_peso": [], "dieta_semanal": "Sin generar.", "rutina_semanal": "Sin generar.", "analisis_salud": "Sin analizar."
    }

# --- LÓGICA DE SESIÓN ---
if "usuario_logueado" not in st.session_state:
    st.title("🏋️ Gym Pro AI")
    tab1, tab2 = st.tabs(["Ingresar", "Registrar"])
    
    with tab1:
        u = st.text_input("Usuario")
        p = st.text_input("Password", type="password")
        if st.button("Entrar"):
            users = cargar_json(USERS_FILE)
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                db = cargar_json(DB_FILE)
                st.session_state.data = db.get(u, estructura_inicial(u))
                st.rerun()
            else: st.error("Credenciales inválidas")
            
    with tab2:
        nu = st.text_input("Nuevo Usuario")
        np = st.text_input("Nuevo Password", type="password")
        if st.button("Crear"):
            users = cargar_json(USERS_FILE)
            if nu and np and nu not in users:
                users[nu] = {"password": np, "perfil": estructura_inicial(nu)["user"]}
                guardar_json(USERS_FILE, users)
                st.success("¡Creado!")

else:
    # --- APP PRINCIPAL ---
    with st.sidebar:
        st.write(f"Usuario: **{st.session_state.usuario_logueado}**")
        menu = st.radio("Menú", ["Perfil", "Dieta IA", "Rutina IA", "Progreso"])
        if st.button("Salir"):
            del st.session_state.usuario_logueado
            st.rerun()

    if menu == "Perfil":
        st.header("📊 Perfil y Salud")
        user = st.session_state.data["user"]
        
        with st.form("p_form"):
            n_nom = st.text_input("Nombre", value=user["nombre"])
            c1, c2 = st.columns(2)
            n_edad = c1.number_input("Edad", 14, 100, value=user["edad"])
            n_sexo = c2.selectbox("Sexo", ["Hombre", "Mujer"], index=0 if user["sexo"]=="Hombre" else 1)
            n_peso = st.number_input("Peso (lbs)", 50, 500, value=user["peso_lb"])
            n_pies = c1.number_input("Pies", 3, 8, value=user["pies"])
            n_pulg = c2.number_input("Pulgadas", 0, 11, value=user["pulgadas"])
            n_objs = st.multiselect("Metas", ["Masa Muscular", "Perder Grasa", "Fuerza", "Salud"], default=user["objetivos"])
            
            if st.form_submit_button("Guardar y Analizar"):
                user.update({"nombre": n_nom, "edad": n_edad, "sexo": n_sexo, "peso_lb": n_peso, "pies": n_pies, "pulgadas": n_pulg, "objetivos": n_objs})
                with st.spinner("IA Analizando..."):
                    st.session_state.data["analisis_salud"] = llamar_ia(f"Analiza mi salud: {user}")
                
                # Guardar cambios
                db = cargar_json(DB_FILE)
                db[st.session_state.usuario_logueado] = st.session_state.data
                guardar_json(DB_FILE, db)
                st.rerun()
        
        st.info(st.session_state.data["analisis_salud"])

    elif menu == "Dieta IA":
        if st.button("Generar Dieta"):
            st.session_state.data["dieta_semanal"] = llamar_ia(f"Crea una dieta para: {st.session_state.data['user']}")
            db = cargar_json(DB_FILE)
            db[st.session_state.usuario_logueado] = st.session_state.data
            guardar_json(DB_FILE, db)
        st.markdown(st.session_state.data["dieta_semanal"])

    elif menu == "Rutina IA":
        if st.button("Generar Rutina"):
            st.session_state.data["rutina_semanal"] = llamar_ia(f"Crea una rutina para: {st.session_state.data['user']}")
            db = cargar_json(DB_FILE)
            db[st.session_state.usuario_logueado] = st.session_state.data
            guardar_json(DB_FILE, db)
        st.markdown(st.session_state.data["rutina_semanal"])

    elif menu == "Progreso":
        st.header("📈 Progreso")
        nuevo_p = st.number_input("Peso hoy (lbs)", 50, 500)
        if st.button("Registrar"):
            st.session_state.data["historial_peso"].append({"fecha": str(pd.Timestamp.now().date()), "peso": nuevo_p})
            db = cargar_json(DB_FILE)
            db[st.session_state.usuario_logueado] = st.session_state.data
            guardar_json(DB_FILE, db)
            st.rerun()
        if st.session_state.data["historial_peso"]:
            st.line_chart(pd.DataFrame(st.session_state.data["historial_peso"]).set_index("fecha"))
