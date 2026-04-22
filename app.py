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

# Filtros de seguridad para evitar bloqueos en temas de salud y fitness
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Usamos 1.5-flash por ser el más estable para la cuota gratuita
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# --- FUNCIÓN MAESTRA DE SEGURIDAD IA ---
def llamar_ia_con_seguridad(prompt):
    """Maneja las llamadas a la IA y captura errores de cuota (429) de forma limpia."""
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "La IA no pudo generar una respuesta en este momento."
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            return "⚠️ **Límite de peticiones alcanzado:** El servidor gratuito de Google está saturado. Por favor, espera 60 segundos y vuelve a intentar."
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
        "dieta_semanal": "Presiona el botón para generar tu plan con IA.",
        "rutina_semanal": "Presiona el botón para generar tu rutina con IA.",
        "analisis_salud": "Completa tu perfil para recibir el análisis de la IA."
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

# --- NÚCLEO DE IA ---

def obtener_analisis_ia(user_data):
    est_m = ((user_data['pies'] * 12) + user_data['pulgadas']) * 0.0254
    peso_kg = user_data['peso_lb'] * 0.453592
    imc = peso_kg / (est_m**2) if est_m > 0 else 0
    
    prompt = f"""
    Analiza clínicamente estos datos de salud:
    - Nombre: {user_data['nombre']}, Edad: {user_data['edad']}, Sexo: {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, IMC: {imc:.2f}
    - Objetivos: {", ".join(user_data['objetivos'])}
    Determina categoría de peso, peso ideal en libras y consejos motivadores.
    """
    return llamar_ia_con_seguridad(prompt)

def generar_dieta_ia(user_data):
    prompt = f"""
    Eres un Nutricionista experto. Crea un plan detallado para:
    - {user_data['nombre']}, {user_data['edad']} años, {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, Entrena: {user_data['dias_entreno']} días/sem.
    - Objetivos: {", ".join(user_data['objetivos'])}
    Calcula calorías, macros, un menú de un día y tips de hidratación. Formato Markdown.
    """
    return llamar_ia_con_seguridad(prompt)

def generar_rutina_ia(user_data):
    prompt = f"""
    Eres un Entrenador Personal experto. Diseña una rutina para:
    - Perfil: {user_data['sexo']}, {user_data['edad']} años, {user_data['peso_lb']} lbs.
    - Frecuencia: {user_data['dias_entreno']} días/semana.
    - Objetivos: {", ".join(user_data['objetivos'])}
    Ajusta ejercicios, series y repeticiones según el objetivo y la edad. Formato Markdown.
    """
    return llamar_ia_con_seguridad(prompt)

# --- INTERFAZ ---

if "usuario_logueado" not in st.session_state:
    st.title("💪 Gym Pro AI")
    t1, t2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    with t1:
        u = st.text_input("Usuario", key="l_u")
        p = st.text_input("Contraseña", type="password", key="l_p")
        if st.button("Entrar"):
            users = cargar_usuarios()
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                st.session_state.data = cargar_todo()
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
    with t2:
        nu = st.text_input("Nuevo Usuario", key="r_u")
        np = st.text_input("Nueva Contraseña", type="password", key="r_p")
        if st.button("Crear Cuenta"):
            users = cargar_usuarios()
            if nu and np:
                if nu in users: st.warning("El usuario ya existe.")
                else:
                    users[nu] = {"password": np, "perfil": estructura_vacia(nu)["user"]}
                    guardar_usuarios(users)
                    st.success("¡Cuenta creada! Ya puedes iniciar sesión.")

else:
    with st.sidebar:
        st.title(f"Hola, {st.session_state.usuario_logueado} 👋")
        opc = st.radio("Navegación", ["Perfil y Salud", "Dieta IA", "Rutina IA", "Mi Progreso"])
        if st.button("Cerrar Sesión"):
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
                n_dias = st.slider("Días de entreno/semana", 1, 7, value=user.get("dias_entreno", 3))
                objs = st.multiselect("Tus Objetivos", ["Ganar masa muscular", "Perder grasa", "Aumentar fuerza", "Resistencia", "Mejorar postura", "Reducir estrés"], default=user["objetivos"])
                
                if st.form_submit_button("Guardar y Analizar"):
                    est_m = ((n_pies * 12) + n_pulg) * 0.0254
                    new_data = {
                        "nombre": n_nom, 
                        "sexo": n_sexo, 
                        "peso_lb": n_peso, 
                        "pies": n_pies, 
                        "pulgadas": n_pulg, 
                        "estatura_m": est_m, 
                        "objetivos": objs, 
                        "edad": n_edad, 
                        "dias_entreno": n_dias
                    }
                    st.session_state.data["user"] = new_data
                    with st.spinner("La IA está analizando tu estado físico..."):
                        st.session_state.data["analisis_salud"] = obtener_analisis_ia(new_data)
                    guardar_todo(st.session_state.data)
                    actualizar_perfil_usuario(st.session_state.usuario_logueado, new_data)
                    st.rerun()
        with col2:
            st.subheader("Interpretación de la IA")
            st.info(st.session_state.data.get("analisis_salud", "Sin análisis generado."))

    elif opc == "Dieta IA":
        st.header("🍎 Tu Plan Nutricional IA")
        if st.button("🚀 Generar Nuevo Plan Alimenticio"):
            with st.spinner("Calculando tu dieta personalizada..."):
                st.session_state.data["dieta_semanal"] = generar_dieta_ia(st.session_state.data["user"])
                guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["dieta_semanal"])

    elif opc == "Rutina IA":
        st.header("🏋️ Tu Entrenamiento IA")
        if st.button("⚡ Generar Nueva Rutina"):
            with st.spinner("Diseñando tu rutina de ejercicios..."):
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(st.session_state.data["user"])
                guardar_todo(st.session_state.data)
        st.markdown(st.session_state.data["rutina_semanal"])

    elif opc == "Mi Progreso":
        st.header("📈 Mi Progreso")
        nuevo_p = st.number_input("Registrar peso de hoy (lbs)", 50, 500)
        if st.button("Guardar Registro"):
            st.session_state.data["historial_peso"].append({"fecha": str(pd.Timestamp.now().date()), "peso": nuevo_p})
            guardar_todo(st.session_state.data)
            st.success("Peso registrado correctamente.")
            st.rerun()
        if st.session_state.data["historial_peso"]:
            df_p = pd.DataFrame(st.session_state.data["historial_peso"])
            st.line_chart(df_p.set_index("fecha"))
