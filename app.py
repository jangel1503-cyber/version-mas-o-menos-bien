import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Gym Pro AI", page_icon="🏋️‍♂️", layout="wide")

DB_FILE = "gym_data.json"
USERS_FILE = "user_data.json"

# Cargar API key (Prioriza secrets de Streamlit Cloud)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    # Clave proporcionada por el usuario
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)

# Configuración de seguridad para permitir consejos de salud y ejercicio sin bloqueos
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety_settings)

# --- GESTIÓN DE ARCHIVOS Y USUARIOS ---
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
        "prs": {},
        "dieta_semanal": "Aún no has generado una dieta.",
        "rutina_semanal": "Aún no has generado una rutina.",
        "analisis_salud": "Completa tu perfil para recibir un análisis de la IA."
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

# --- NÚCLEO DE INTELIGENCIA ARTIFICIAL ---

def obtener_analisis_ia(user_data):
    """La IA interpreta los datos físicos del usuario."""
    est_m = ((user_data['pies'] * 12) + user_data['pulgadas']) * 0.0254
    peso_kg = user_data['peso_lb'] * 0.453592
    imc = peso_kg / (est_m**2) if est_m > 0 else 0
    
    prompt = f"""
    Actúa como un experto en salud. Analiza estos datos:
    - Nombre: {user_data['nombre']}, Edad: {user_data['edad']}, Sexo: {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, Estatura: {user_data['pies']} pies {user_data['pulgadas']} pulgadas.
    - IMC calculado: {imc:.2f}
    - Objetivos: {", ".join(user_data['objetivos'])}

    PROPORCIONA:
    1. Diagnóstico de categoría de peso.
    2. Rango de peso ideal en Libras.
    3. Un análisis de cómo sus objetivos se alinean con su estado actual.
    Se breve, profesional y motivador.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar análisis: {e}"

def generar_dieta_ia(user_data):
    """Genera nutrición personalizada 100% mediante IA."""
    prompt = f"""
    Eres un Nutricionista Deportivo de élite. Crea un plan detallado para:
    - Usuario: {user_data['nombre']}, {user_data['edad']} años, {user_data['sexo']}
    - Peso: {user_data['peso_lb']} lbs, Estatura: {user_data['pies']}'{user_data['pulgadas']}"
    - Actividad: {user_data['dias_entreno']} días de gimnasio por semana.
    - Objetivos: {", ".join(user_data['objetivos'])}

    EL PLAN DEBE INCLUIR:
    1. Calorías diarias sugeridas y distribución de Macros.
    2. Un ejemplo de menú diario (Desayuno, Almuerzo, Merienda, Cena).
    3. Tips específicos para optimizar resultados según su edad y metas.
    Usa formato Markdown.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Hubo un problema al conectar con el nutricionista virtual: {e}"

def generar_rutina_ia(user_data):
    """Genera entrenamiento personalizado 100% mediante IA."""
    prompt = f"""
    Eres un Entrenador Personal experto. Diseña una rutina para:
    - Perfil: {user_data['sexo']}, {user_data['edad']} años, {user_data['peso_lb']} lbs.
    - Frecuencia: {user_data['dias_entreno']} días/semana.
    - Objetivos: {", ".join(user_data['objetivos'])}

    REGLAS:
    1. Si busca 'Fuerza', series pesadas (1-5 reps). Si busca 'Hipertrofia', (8-12 reps).
    2. Si tiene más de 45 años, priorizar salud articular y técnica.
    3. Estructura clara por días con ejercicios, series, repeticiones y descansos.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar la rutina: {e}"

# --- FLUJO DE LA INTERFAZ ---

if "usuario_logueado" not in st.session_state:
    st.title("🏋️ Gym Pro AI")
    st.subheader("Tu transformación física potenciada por IA")
    
    auth_tab1, auth_tab2 = st.tabs(["Ingresar", "Registrarse"])
    
    with auth_tab1:
        u = st.text_input("Usuario", key="login_user")
        p = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Iniciar Sesión", use_container_width=True):
            users = cargar_usuarios()
            if u in users and users[u]["password"] == p:
                st.session_state.usuario_logueado = u
                st.session_state.data = cargar_todo()
                st.success(f"Bienvenido de nuevo, {u}")
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos.")

    with auth_tab2:
        new_u = st.text_input("Elige un nombre de usuario")
        new_p = st.text_input("Elige una contraseña", type="password")
        if st.button("Crear Cuenta", use_container_width=True):
            users = cargar_usuarios()
            if new_u in users: st.warning("Ese nombre ya está en uso.")
            elif new_u and new_p:
                users[new_u] = {"password": new_p, "perfil": estructura_vacia(new_u)["user"]}
                guardar_usuarios(users)
                st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")
            else: st.error("Por favor rellena todos los campos.")

else:
    # --- PANEL PRINCIPAL (LOGUEADO) ---
    with st.sidebar:
        st.title(f"Hola, {st.session_state.usuario_logueado} 👋")
        opcion = st.radio("Navegación", ["Perfil y Salud", "Plan de Nutrición IA", "Rutina de Entrenamiento IA", "Mi Progreso"])
        st.markdown("---")
        if st.button("Cerrar Sesión"):
            del st.session_state.usuario_logueado
            st.rerun()

    # 1. PERFIL Y SALUD
    if opcion == "Perfil y Salud":
        st.header("📊 Perfil y Análisis de Salud IA")
        user = st.session_state.data["user"]
        
        col_form, col_ia = st.columns([1, 1.2])
        
        with col_form:
            with st.form("perfil_update"):
                st.subheader("Tus Datos Físicos")
                n_nombre = st.text_input("Nombre", value=user["nombre"])
                n_edad = st.number_input("Edad", 14, 100, value=user.get("edad", 25))
                n_sexo = st.selectbox("Sexo", ["Hombre", "Mujer"], index=0 if user["sexo"]=="Hombre" else 1)
                n_peso = st.number_input("Peso Actual (lbs)", 50, 500, value=user["peso_lb"])
                c1, c2 = st.columns(2)
                n_pies = c1.number_input("Estatura (Pies)", 3, 8, value=user["pies"])
                n_pulgadas = c2.number_input("Estatura (Pulg.)", 0, 11, value=user["pulgadas"])
                n_dias = st.slider("Días de entrenamiento por semana", 1, 7, value=user.get("dias_entreno", 3))
                
                objs_disponibles = [
                    "Ganar masa muscular (hipertrofia)", "Perder grasa corporal", "Aumentar fuerza", 
                    "Mejorar resistencia cardiovascular", "Tonificar el cuerpo", "Reducir el estrés", 
                    "Dormir mejor", "Aprender técnica correcta", "Crear una rutina constante", "Mejorar postura"
                ]
                n_objs = st.multiselect("Tus Objetivos Actuales", objs_disponibles, default=user["objetivos"])
                
                if st.form_submit_button("💾 Guardar y Analizar con IA", use_container_width=True):
                    est_m = ((n_pies * 12) + n_pulgadas) * 0.0254
                    nueva_data = {
                        "nombre": n_nombre, "sexo": n_sexo, "peso_lb": n_peso, "pies": n_pies, 
                        "pulgadas": n_pulgadas, "estatura_m": est_m, "objetivos": n_objs,
                        "edad": n_edad, "dias_entreno": n_dias
                    }
                    st.session_state.data["user"] = nueva_data
                    
                    with st.spinner("La IA está analizando tu perfil..."):
                        st.session_state.data["analisis_salud"] = obtener_analisis_ia(nueva_data)
                    
                    guardar_todo(st.session_state.data)
                    actualizar_perfil_usuario(st.session_state.usuario_logueado, nueva_data)
                    st.success("¡Datos actualizados!")
                    st.rerun()

        with col_ia:
            st.subheader("Resumen de Salud Inteligente")
            st.info(st.session_state.data.get("analisis_salud", "Sin análisis disponible."))

    # 2. PLAN ALIMENTICIO
    elif opcion == "Plan de Nutrición IA":
        st.header("🍎 Nutrición Basada en Ciencia e IA")
        if st.button("🚀 Generar Nuevo Plan Alimenticio con IA", use_container_width=True):
            with st.spinner("Calculando macros y diseñando menú..."):
                plan = generar_dieta_ia(st.session_state.data["user"])
                st.session_state.data["dieta_semanal"] = plan
                guardar_todo(st.session_state.data)
        
        st.markdown("---")
        st.markdown(st.session_state.data["dieta_semanal"])

    # 3. RUTINA IA
    elif opcion == "Rutina de Entrenamiento IA":
        st.header("🏋️ Entrenamiento Personalizado por IA")
        if st.button("⚡ Generar Nueva Rutina Semanal con IA", use_container_width=True):
            with st.spinner("Diseñando tu entrenamiento inteligente..."):
                rutina = generar_rutina_ia(st.session_state.data["user"])
                st.session_state.data["rutina_semanal"] = rutina
                guardar_todo(st.session_state.data)
        
        st.markdown("---")
        st.markdown(st.session_state.data["rutina_semanal"])

    # 4. PROGRESO
    elif opcion == "Mi Progreso":
        st.header("📈 Seguimiento de Resultados")
        col_input, col_chart = st.columns([1, 2])
        
        with col_input:
            nuevo_p = st.number_input("Registrar peso de hoy (lbs)", 50, 500, value=st.session_state.data["user"]["peso_lb"])
            if st.button("Guardar Peso", use_container_width=True):
                fecha_hoy = str(pd.Timestamp.now().date())
                st.session_state.data["historial_peso"].append({"fecha": fecha_hoy, "peso": nuevo_p})
                guardar_todo(st.session_state.data)
                st.success("¡Peso registrado!")
                st.rerun()
        
        with col_chart:
            if st.session_state.data["historial_peso"]:
                df_peso = pd.DataFrame(st.session_state.data["historial_peso"])
                st.line_chart(df_peso.set_index("fecha"))
            else:
                st.write("Aún no tienes registros de peso históricos.")
