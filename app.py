import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai
import gym_app.services as services

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS PERSONALIZADOS ---
def aplicar_estilos():
    """Aplica estilos CSS con tema oscuro elegante, glow effects y sin bordes"""
    estilos = """
    <style>
    /* Variables de color - Paleta oscura elegante tipo Vercel/Stripe */
    :root {
        --dark-bg: #0f172a;
        --dark-bg-secondary: #1a202c;
        --dark-card: #1e293b;
        --dark-border: #334155;
        --dark-text: #f1f5f9;
        --dark-text-secondary: #cbd5e1;
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Fondo oscuro elegante */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a !important;
        color: #f1f5f9 !important;
    }
    
    /* Headers principales */
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -1px !important;
    }
    
    /* Subtítulos - SIN BORDES */
    h2, h3 {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        letter-spacing: 0 !important;
        text-transform: none !important;
        border: none !important;
        padding-bottom: 0.75rem !important;
    }
    
    h4 {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    
    /* Tarjetas de ejercicios - GLOW FLOTANTE */
    .exercise-card {
        background: #1e293b !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 18px !important;
        margin: 12px 0 !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.2), 0 0 50px rgba(59, 130, 246, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .exercise-card:hover {
        background: #334155 !important;
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.4), 0 0 80px rgba(59, 130, 246, 0.2), 0 8px 25px rgba(59, 130, 246, 0.15) !important;
        transform: translateY(-4px) translateX(2px) !important;
    }
    
    /* Botones mejorados */
    button {
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    
    /* Botones primarios - GLOW FLOTANTE */
    [data-testid="baseButton-primary"] {
        background: #3b82f6 !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5), 0 0 40px rgba(59, 130, 246, 0.25) !important;
    }
    
    [data-testid="baseButton-primary"]:hover {
        background: #2563eb !important;
        box-shadow: 0 0 35px rgba(59, 130, 246, 0.7), 0 0 70px rgba(59, 130, 246, 0.4), 0 6px 30px rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Tabs */
    [data-baseweb="tab-list"] {
        border: none !important;
    }
    
    [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    [aria-selected="true"] {
        color: #3b82f6 !important;
        box-shadow: 0 2px 15px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Métricas - CON GLOW */
    [data-testid="metric-container"] {
        background: #1e293b !important;
        border-radius: 8px !important;
        padding: 18px !important;
        border: none !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.2), 0 0 50px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Inputs - SIN BORDES, GLOW FLOTANTE */
    input, textarea, select {
        background-color: #1a202c !important;
        border: none !important;
        color: #f1f5f9 !important;
        border-radius: 8px !important;
        font-weight: 400 !important;
        padding: 10px 14px !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.15), inset 0 0 10px rgba(59, 130, 246, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, textarea:focus, select:focus {
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.35), 0 0 60px rgba(59, 130, 246, 0.2), inset 0 0 15px rgba(59, 130, 246, 0.1) !important;
        transform: scale(1.01) !important;
    }
    
    /* Expanders - SIN BORDES, GLOW */
    [data-testid="stExpander"] {
        background: #1e293b !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15), 0 0 40px rgba(59, 130, 246, 0.08) !important;
    }
    
    /* Info boxes - SIN BORDES, GLOW */
    [data-testid="stInfo"] {
        background: rgba(59, 130, 246, 0.08) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.25), 0 0 50px rgba(59, 130, 246, 0.12) !important;
    }
    
    [data-testid="stSuccess"] {
        background: rgba(16, 185, 129, 0.08) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.25), 0 0 50px rgba(16, 185, 129, 0.12) !important;
    }
    
    [data-testid="stWarning"] {
        background: rgba(139, 92, 246, 0.08) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.25), 0 0 50px rgba(139, 92, 246, 0.12) !important;
    }
    
    [data-testid="stError"] {
        background: rgba(239, 68, 68, 0.08) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #cbd5e1 !important;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.25), 0 0 50px rgba(239, 68, 68, 0.12) !important;
    }
    
    /* Checkboxes */
    [data-testid="stCheckbox"] {
        padding: 8px !important;
    }
    
    /* Sidebar - SIN BORDES */
    [data-testid="stSidebar"] {
        background: #1a202c !important;
        border: none !important;
    }
    
    /* Textos generales */
    p, span, div {
        color: #f1f5f9 !important;
    }
    
    /* Enlace */
    a {
        color: #3b82f6 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }
    
    a:hover {
        color: #60a5fa !important;
        text-decoration: underline !important;
    }
    
    /* Divisor - GLOW SUTIL */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent) !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* DataFrames */
    [data-testid="stDataFrame"] {
        background-color: #1e293b !important;
    }
    
    /* Cards personalizadas - GLOW FLOTANTE */
    .stat-card {
        background: #1e293b !important;
        border-radius: 10px !important;
        padding: 20px !important;
        color: #f1f5f9 !important;
        text-align: center !important;
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.25), 0 0 60px rgba(59, 130, 246, 0.15) !important;
        font-weight: 500 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stat-card:hover {
        box-shadow: 0 0 45px rgba(59, 130, 246, 0.35), 0 0 90px rgba(59, 130, 246, 0.2), 0 8px 30px rgba(59, 130, 246, 0.2) !important;
        transform: translateY(-5px) !important;
    }
    
    /* Progress bar - GLOW */
    .progress-bar {
        background: rgba(59, 130, 246, 0.15) !important;
        border: none !important;
        border-radius: 10px !important;
        height: 10px !important;
        box-shadow: inset 0 0 10px rgba(59, 130, 246, 0.1) !important;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #3b82f6, #60a5fa) !important;
        height: 100% !important;
        border-radius: 10px !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6), inset 0 0 10px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Animaciones */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Animaciones sutiles */
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .pulse {
        animation: pulse 1.5s infinite;
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Scrollbar personalizada - Tema oscuro con glow */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.2) inset;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3b82f6;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.4) inset;
    }
    
    /* Labels en sidebar */
    .sidebar-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #94a3b8;
        margin: 1.5rem 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Tarjetas de comidas - CON GLOW */
    .meal-card {
        background: #1e293b !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 14px !important;
        margin: 8px 0 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.1) !important;
    }
    
    .meal-card:hover {
        background: #334155 !important;
        transform: translateX(2px) !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.25) !important;
    }
    
    /* Badges de progreso - CON GLOW */
    .progress-badge {
        display: inline-block;
        background: #3b82f6 !important;
        color: white !important;
        padding: 4px 10px !important;
        border-radius: 16px !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Animación shimmer para carga */
    @keyframes shimmer {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    .shimmer {
        animation: shimmer 1.5s infinite;
    }
    
    /* Espaciado y tipografía mejorados */
    [data-testid="stMarkdownContainer"] {
        line-height: 1.6 !important;
        color: #f1f5f9 !important;
    }
    
    /* Color de texto en elementos especiales */
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }
    
    /* Mejora visual para elementos de streamlit */
    [data-testid="stVerticalBlock"] {
        color: #f1f5f9 !important;
    }
    
    /* Buttons secundarios */
    [data-testid="baseButton-secondary"] {
        background: #334155 !important;
        color: #f1f5f9 !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background: #475569 !important;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.35) !important;
    }
    
    </style>
    """
    st.markdown(estilos, unsafe_allow_html=True)

# Aplicar estilos al cargar la página
aplicar_estilos()

# Cargar API key desde secrets (Streamlit Cloud) o variable local
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- CAPA DE SERVICIOS (N-CAPAS) ---
DB_FILE = services.DB_FILE
USERS_FILE = services.USERS_FILE
LISTA_OBJETIVOS = services.LISTA_OBJETIVOS


def cargar_usuarios():
    return services.cargar_usuarios()


def guardar_usuarios(usuarios):
    return services.guardar_usuarios(usuarios)


def usuario_existe(username):
    return services.usuario_existe(username)


def validar_credenciales(username, password):
    return services.validar_credenciales(username, password)


def registrar_usuario(username, password, datos_perfil):
    return services.registrar_usuario(username, password, datos_perfil)


def actualizar_perfil_usuario(username, datos_perfil):
    return services.actualizar_perfil_usuario(username, datos_perfil)


def obtener_datos_usuario(username):
    return services.obtener_datos_usuario(username)


def guardar_todo(datos):
    return services.guardar_todo(datos, st.session_state.usuario_logueado)


def cargar_todo():
    return services.cargar_todo(st.session_state.usuario_logueado)


def obtener_analisis(peso_lb, estatura_m):
    return services.obtener_analisis(peso_lb, estatura_m)


def calcular_macros(u):
    return services.calcular_macros(u)


def generar_dieta_fallback_local(perfil_json):
    return services.generar_dieta_fallback_local(perfil_json)


def generar_dieta_semanal(perfil_json):
    return services.generar_dieta_semanal(perfil_json, model)


def generar_rutina_gemini(perfil_json):
    return services.generar_rutina_gemini(perfil_json, model)


def generar_rutina_ia(u):
    return services.generar_rutina_ia(u, model)


def obtener_ejercicios_alternativos(ejercicio, musculo_objetivo):
    return services.obtener_ejercicios_alternativos(ejercicio, musculo_objetivo, model)


def generar_warmup(dia_entreno, ejercicios_dia):
    return services.generar_warmup(dia_entreno, ejercicios_dia, model)


def calcular_tiempo_descanso(objetivo, reps):
    return services.calcular_tiempo_descanso(objetivo, reps)


def registrar_entrenamiento(dia, ejercicios_completados):
    return services.registrar_entrenamiento(dia, ejercicios_completados)


def calcular_progreso_ejercicio(ejercicio_nombre, historial):
    return services.calcular_progreso_ejercicio(ejercicio_nombre, historial)


def detectar_meseta_y_rotar_rutina(historial_entrenamientos, fecha_ultima_rotacion, dias_entrenamientos):
    return services.detectar_meseta_y_rotar_rutina(historial_entrenamientos, fecha_ultima_rotacion, dias_entrenamientos)


def recomendaciones_ia(progreso_data, user_profile):
    return services.recomendaciones_ia(progreso_data, user_profile, model)


def obtener_musculos_del_dia(ejercicios_dia):
    return services.obtener_musculos_del_dia(ejercicios_dia)


if 'usuario_logueado' not in st.session_state:
    st.session_state.usuario_logueado = None

if 'data' not in st.session_state or (st.session_state.usuario_logueado and st.session_state.data.get('user', {}) == {}):
    if st.session_state.usuario_logueado:
        st.session_state.data = cargar_todo()
    else:
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

# --- INTERFAZ ---
# PANTALLA DE LOGIN/REGISTRO
if not st.session_state.usuario_logueado:
    # Header mejorado
    st.markdown('<h1 class="main-header">💪 GYM PRO AI</h1>', unsafe_allow_html=True)
    
    # Subtítulo con estilo
    col_header = st.columns([1])[0]
    with col_header:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%); 
                    border-radius: 12px; border: 2px solid #FF6B35; margin-bottom: 30px;'>
            <h3 style='color: #4ECDC4; margin: 0; font-size: 1.5rem;'>Tu Entrenador Personal Inteligente</h3>
            <p style='color: #FFE66D; margin: 10px 0 0 0; font-size: 1rem;'>Entrenamientos personalizados con IA | Nutrición optimizada | Progreso garantizado</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(255, 107, 53, 0.15) 0%, rgba(255, 184, 77, 0.15) 100%); 
                    padding: 30px; border-radius: 12px; border: 2px solid #FF6B35; text-align: center;'>
            <h2 style='color: #FF6B35; margin-top: 0;'>🔐 Iniciar Sesión</h2>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            login_user = st.text_input("👤 Nombre de usuario", key="login_user", placeholder="Ingresa tu usuario")
            login_pass = st.text_input("🔑 Contraseña", type="password", key="login_pass", placeholder="Ingresa tu contraseña")
            
            login_btn = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
            
            if login_btn:
                if login_user and login_pass:
                    if validar_credenciales(login_user, login_pass):
                        st.session_state.usuario_logueado = login_user.lower()
                        
                        # Cargar datos DIRECTAMENTE desde gym_data.json
                        datos_cargados = False
                        if os.path.exists(DB_FILE):
                            try:
                                with open(DB_FILE, "r", encoding='utf-8') as f:
                                    all_data = json.load(f)
                                    if st.session_state.usuario_logueado in all_data:
                                        st.session_state.data = all_data[st.session_state.usuario_logueado]
                                        datos_cargados = True
                            except:
                                pass
                        
                        # Si no hay datos en gym_data.json, crear estructura
                        if not datos_cargados:
                            datos = obtener_datos_usuario(login_user)
                            st.session_state.data = {
                                "perfil_completado": True,
                                "user": datos,
                                "rutina_semanal": {},
                                "historial_pesos": [],
                                "historial_entrenamientos": [],
                                "pr_por_ejercicio": {},
                                "fecha_ultima_rotacion": None,
                                "dieta_semanal": {}
                            }
                            # Guardar esta estructura en gym_data.json
                            guardar_todo(st.session_state.data)
                        
                        st.success("✅ ¡Sesión iniciada correctamente!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.warning("⚠️ Completa todos los campos")
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(78, 205, 196, 0.15) 0%, rgba(52, 152, 219, 0.15) 100%); 
                    padding: 30px; border-radius: 12px; border: 2px solid #4ECDC4; text-align: center;'>
            <h2 style='color: #4ECDC4; margin-top: 0;'>📝 Registrarse</h2>
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
            objs = c_o.multiselect("🎯 Tus metas:", LISTA_OBJETIVOS, max_selections=5)
            
            signup_btn = st.form_submit_button("✅ Crear Cuenta", use_container_width=True)
            
            if signup_btn:
                if not signup_user or not signup_pass:
                    st.error("❌ Usuario y contraseña son requeridos")
                elif len(signup_pass) < 6:
                    st.error("❌ La contraseña debe tener al menos 6 caracteres")
                elif signup_pass != signup_pass_conf:
                    st.error("❌ Las contraseñas no coinciden")
                elif usuario_existe(signup_user):
                    st.error("❌ El usuario ya existe")
                elif not nombre or not objs:
                    st.error("❌ Completa nombre y selecciona al menos un objetivo")
                else:
                    # Calcular estatura en metros
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
                    exito, mensaje = registrar_usuario(signup_user, signup_pass, datos_perfil)
                    if exito:
                        st.success(mensaje)
                        st.info("✅ Ahora puedes iniciar sesión con tu nueva cuenta")
                    else:
                        st.error(f"❌ {mensaje}")

elif not st.session_state.data.get("perfil_completado", False):
    st.markdown('<h1 class="main-header">💪 Gym Pro AI</h1>', unsafe_allow_html=True)
    st.markdown("### Bienvenido. Vamos a construir tu mejor versión.")
    
    with st.form("registro_inicial"):
        st.markdown("#### 👤 Datos Personales")
        nombre = st.text_input("¿Cuál es tu nombre?")
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0)
        
        st.markdown("#### 📏 Medidas y Objetivos")
        c_p, c_ft, c_in, c_ed = st.columns(4)
        peso = c_p.number_input("Peso (Lbs)", 50.0, 500.0, 160.0)
        pies = c_ft.number_input("Pies", 3, 8, 5)
        pulgadas = c_in.number_input("Pulgadas", 0, 11, 7)
        edad = c_ed.number_input("Edad", 12, 100, 25)
        
        c_d, c_o = st.columns([1, 2])
        dias_e = c_d.selectbox("Días de Entreno", [3, 4, 5], index=2)
        objs = c_o.multiselect("Selecciona tus metas:", LISTA_OBJETIVOS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Generar Mi Plan Inteligente", use_container_width=True)
        
        if submit:
            if nombre and objs:
                est_m = ((pies * 12) + pulgadas) * 0.0254
                st.session_state.data["user"] = {
                    "nombre": nombre, "sexo": sexo, "peso_lb": peso, "pies": pies, 
                    "pulgadas": pulgadas, "estatura_m": est_m, "objetivos": objs,
                    "edad": edad, "dias_entreno": dias_e
                }
                st.session_state.data["perfil_completado"] = True
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(st.session_state.data["user"])
                guardar_todo(st.session_state.data)
                st.rerun()
            else:
                st.warning("⚠️ Completa tu nombre y elige al menos un objetivo para continuar.")

else:
    u = st.session_state.data.get("user", {})
    imc, estado, p_min, p_max = obtener_analisis(u.get('peso_lb', 160), u.get('estatura_m', 1.70))
    
    # --- SIDEBAR PREMIUN ---
    with st.sidebar:
        nombre_usuario = u.get('nombre', 'Usuario')
        sexo_usuario = u.get('sexo', 'N/A')
        edad_usuario = u.get('edad', 'N/A')
        objetivos_usuario = u.get('objetivos', [])
        objetivo_principal = objetivos_usuario[0] if objetivos_usuario else 'Sin objetivos'
        
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="margin:0;">💪 Gym Pro AI</h2>
                <p style="color: grey;">Tu Entrenador Personal Inteligente</p>
            </div>
            <hr style="margin: 10px 0; border: 0.1px solid rgba(255,255,255,0.1);">
            <p class="sidebar-label" style="color: #FFE66D; font-size: 0.9rem; font-weight: 700; text-transform: uppercase;">👤 Perfil de Usuario</p>
            <h3 style="color: #FF6B35; margin: 10px 0;">{nombre_usuario}</h3>
            <p style="color: #bbb; margin: 5px 0;">⚧️ {sexo_usuario}</p>
            <p style="color: #bbb; margin: 5px 0;">🎂 {edad_usuario} años</p>
            <p style="color: #4ECDC4; margin: 5px 0; font-weight: 600;">🎯 {objetivo_principal}</p>
        """, unsafe_allow_html=True)
        st.info(f"📍 **Meta**: {len(objetivos_usuario)} objetivos seleccionados")
        
        st.markdown("---")
        
        col_logout, col_reinicio = st.columns([1, 1])
        
        with col_logout:
            if st.button("🚪 Salir", use_container_width=True, help="Cerrar sesión"):
                st.success("👋 ¡Hasta luego!")
                import time
                time.sleep(1)
                st.session_state.usuario_logueado = None
                st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}, "historial_pesos": [], "historial_entrenamientos": [], "pr_por_ejercicio": {}, "fecha_ultima_rotacion": None, "dieta_semanal": {}}
                st.rerun()
        
        with col_reinicio:
            if not st.session_state.get('confirmar_reinicio', False):
                if st.button("⚠️ Reiniciar", use_container_width=True, help="Reiniciar datos"):
                    st.session_state.confirmar_reinicio = True
                    st.rerun()
            else:
                st.warning("❓ ¿Estás seguro? Se borrarán todos los datos.")
                c1, c2 = st.columns(2)
                if c1.button("✅ Sí", use_container_width=True, key="confirm_yes"):
                    st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}, "historial_pesos": [], "historial_entrenamientos": [], "pr_por_ejercicio": {}, "fecha_ultima_rotacion": None, "dieta_semanal": {}}
                    st.session_state.confirmar_reinicio = False
                    guardar_todo(st.session_state.data)
                    st.success("✅ Datos reiniciados")
                    st.rerun()
                if c2.button("❌ No", use_container_width=True, key="confirm_no"):
                    st.session_state.confirmar_reinicio = False
                    st.rerun()
        
        st.markdown("---")
        
        # Panel de depuración para verificar datos
        with st.expander("🔍 Verificar Datos Guardados"):
            st.write("**Datos en Session State (User):**")
            st.json(u)
            st.write("**Usuario Logueado:**", st.session_state.usuario_logueado)
            
            # Verificar qué hay en gym_data.json
            try:
                if os.path.exists(DB_FILE):
                    with open(DB_FILE, "r", encoding='utf-8') as f:
                        todos_datos = json.load(f)
                        if st.session_state.usuario_logueado in todos_datos:
                            st.write("✅ Datos encontrados en gym_data.json")
                            st.write("**Campos guardados:**", list(todos_datos[st.session_state.usuario_logueado].keys()))
                        else:
                            st.write("❌ No hay datos en gym_data.json para este usuario")
            except:
                st.write("❌ Error leyendo gym_data.json")

    # --- DASHBOARD PRINCIPAL ---
    nombre_usuario = u.get("nombre", "Usuario")
    st.markdown(f'<h1 class="main-header">¡Bienvenido, {nombre_usuario}! 💪</h1>', unsafe_allow_html=True)
    
    # Barra de métricas mejorada
    st.markdown("---")
    st.markdown("### 📊 Tu Estado Actual")
    
    col_imc, col_estado, col_ideal, col_dias = st.columns(4)
    
    with col_imc:
        st.markdown(f"""
        <div class="stat-card">
            <h4 style="margin: 0; font-size: 0.9rem;">📏 IMC</h4>
            <h2 style="margin: 10px 0; color: white; font-size: 2.5rem;">{imc}</h2>
            <p style="margin: 0; font-size: 0.85rem; opacity: 0.9;">Índice de Masa Corporal</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_estado:
        color_estado = "#27AE60" if estado == "Peso normal" else "#F39C12" if estado == "Sobrepeso" else "#E74C3C"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba({','.join(map(str, [39, 174, 96][:3]))}, 0.2) 0%, rgba(46, 204, 113, 0.2) 100%); 
                    border-radius: 12px; padding: 20px; border: 2px solid {color_estado}; text-align: center;'>
            <h4 style='margin: 0; font-size: 0.9rem; color: {color_estado};'>💪 Estado</h4>
            <h2 style='margin: 10px 0; color: {color_estado}; font-size: 1.8rem;'>{estado}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ideal:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(52, 152, 219, 0.2) 0%, rgba(41, 128, 185, 0.2) 100%); 
                    border-radius: 12px; padding: 20px; border: 2px solid #3498DB; text-align: center;'>
            <h4 style='margin: 0; font-size: 0.9rem; color: #3498DB;'>⚖️ Peso Ideal</h4>
            <h2 style='margin: 10px 0; color: #3498DB; font-size: 1.8rem;'>{p_min}-{p_max}</h2>
            <p style='margin: 0; font-size: 0.85rem; color: #bbb;'>en Lbs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dias:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(155, 89, 182, 0.2) 0%, rgba(142, 68, 173, 0.2) 100%); 
                    border-radius: 12px; padding: 20px; border: 2px solid #9B59B6; text-align: center;'>
            <h4 style='margin: 0; font-size: 0.9rem; color: #9B59B6;'>📅 Días</h4>
            <h2 style='margin: 10px 0; color: #9B59B6; font-size: 1.8rem;'>{u.get("dias_entreno", 5)}</h2>
            <p style='margin: 0; font-size: 0.85rem; color: #bbb;'>entrenos/semana</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    t_rutina, t_entrenamiento, t_dieta, t_progreso, t_alternativas, t_recomendaciones, t_perfil = st.tabs(
        ["📅 Mi Rutina", "💪 Entrenar Hoy", "🍽️ Mi Dieta", "📈 Progreso", "🔄 Alternativas", "🤖 Recomendaciones", "👤 Perfil"]
    )

    with t_rutina:
        st.markdown("### 🏋️ Tu Plan de Entrenamiento Personalizado")
        
        # Botones de acción en la parte superior
        col_btn1, col_btn2, col_info = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("🤖 Generar Rutina", use_container_width=True, help="Crea una nueva rutina basada en tus objetivos"):
                with st.spinner("⏳ IA generando rutina personalizada..."):
                    st.session_state.data["rutina_semanal"] = generar_rutina_ia(u)
                    guardar_todo(st.session_state.data)
                st.success("✅ ¡Nueva rutina generada con IA!")
                st.balloons()
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Regenerar", use_container_width=True, help="Crea una nueva rutina"):
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(u)
                guardar_todo(st.session_state.data)
                st.success("✅ ¡Nueva rutina generada!")
                st.rerun()
        
        st.markdown("---")
        
        # Recargar siempre los datos más frescos
        st.session_state.data = cargar_todo()
        rutina = st.session_state.data.get("rutina_semanal", {})
        for dia, ejercicios in rutina.items():
            # Obtener músculos del día
            musculos = obtener_musculos_del_dia(ejercicios if isinstance(ejercicios, list) else [])
            musculos_text = ", ".join(musculos) if musculos else "Descanso"
            
            with st.expander(f"📅 {dia.upper()} - 🔥 {musculos_text}", expanded=(dia=="Lunes")):
                if isinstance(ejercicios, str):
                    st.info(ejercicios)
                else:
                    for i, ej in enumerate(ejercicios):
                        # Convertir formato de Gemini (reps_por_serie/peso_lb_por_serie) al nuestro
                        if 'reps_por_serie' in ej and 'peso_lb_por_serie' in ej:
                            ej['detalles_sets'] = [
                                {"reps": str(ej['reps_por_serie'][idx]), "libras": float(ej['peso_lb_por_serie'][idx])}
                                for idx in range(len(ej['reps_por_serie']))
                            ]
                            ej['series'] = len(ej['reps_por_serie'])
                        # Asegurar compatibilidad con datos antiguos
                        elif 'detalles_sets' not in ej:
                            old_reps = ej.get('reps', '12')
                            old_lbs = ej.get('libras', 0)
                            ej['detalles_sets'] = [{"reps": old_reps, "libras": old_lbs} for _ in range(int(ej.get('series', 3)))]

                        st.markdown(f"""
                            <div class="exercise-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong>{ej['ejercicio']}</strong>
                                    <span title="{ej.get('tip', '')}" style="cursor:help;">💡 Tip</span>
                                </div>
                                <small style="color: #bbb;">{ej.get('tip', 'Mantén la técnica correcta.')}</small><br>
                                <small>Configuración: {ej['series']} sets totales</small>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([3, 1])
                        rutina[dia][i]['ejercicio'] = c1.text_input("Ejercicio", ej['ejercicio'], key=f"e_{dia}_{i}")
                        num_sets = c2.number_input("Sets totales", 1, 12, int(ej['series']), key=f"s_{dia}_{i}")
                        rutina[dia][i]['series'] = num_sets
                        
                        # Ajustar lista de detalles si cambió el número de sets
                        if len(ej['detalles_sets']) != num_sets:
                            if len(ej['detalles_sets']) < num_sets:
                                extra = num_sets - len(ej['detalles_sets'])
                                last_val = ej['detalles_sets'][-1] if ej['detalles_sets'] else {"reps": "10", "libras": 0}
                                for _ in range(extra):
                                    ej['detalles_sets'].append(last_val.copy())
                            else:
                                ej['detalles_sets'] = ej['detalles_sets'][:num_sets]
                        
                        # Grid para editar reps y lbs de cada set
                        st.markdown("###### Detalles por Set (Reps | Lbs)")
                        for s_idx in range(num_sets):
                            sc1, sc2, sc3 = st.columns([1, 2, 2])
                            sc1.markdown(f"**Set {s_idx+1}**")
                            ej['detalles_sets'][s_idx]['reps'] = sc2.text_input(f"Reps S{s_idx}", ej['detalles_sets'][s_idx]['reps'], key=f"r_{dia}_{i}_{s_idx}", label_visibility="collapsed")
                            ej['detalles_sets'][s_idx]['libras'] = sc3.number_input(f"Lbs S{s_idx}", 0.0, 1000.0, float(ej['detalles_sets'][s_idx]['libras']), key=f"l_{dia}_{i}_{s_idx}", label_visibility="collapsed")
                        st.markdown("---")
        
        if st.button("💾 Guardar Cambios en la Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.toast("¡Cambios guardados!", icon="✅")

    with t_dieta:
        st.markdown("### 🍽️ Tu Plan de Nutrición Personalizado")
        
        # Cargar datos frescos
        st.session_state.data = cargar_todo()
        dieta = st.session_state.data.get("dieta_semanal", {})
        u = st.session_state.data.get("user", {})
        
        # Información nutricional resumen
        st.markdown("#### 📊 Tu Objetivo Nutricional")
        cal, p, g, c = calcular_macros(u)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calorías", f"{cal} kcal")
        with col2:
            st.metric("🥩 Proteína", f"{p}g")
        with col3:
            st.metric("🍞 Carbos", f"{c}g")
        with col4:
            st.metric("🥑 Grasas", f"{g}g")
        
        st.markdown("---")
        
        if dieta and any(dieta.values()):
            st.markdown(f"**Objetivo Nutricional:** {dieta.get('objetivo_nutricional', 'N/A')}")
            st.markdown(f"**Calorías Diarias Aprox:** {dieta.get('calorias_diarias_aprox', cal)} kcal")
            
            plan = dieta.get('plan_semanal', {})
            
            for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                if dia in plan:
                    comidas = plan[dia]
                    
                    with st.expander(f"📅 {dia}", expanded=(dia == "Lunes")):
                        # Desayuno
                        if "desayuno" in comidas:
                            des = comidas["desayuno"]
                            st.markdown(f"""<div class="exercise-card" style="border-left-color: #FFB84D;">
                                <h4 style="margin:0; color: #FFB84D;">🌅 Desayuno</h4>
                                <strong>{des.get('comida', 'N/A')}</strong><br>
                                <small>📏 {des.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {des.get('tip', '')}</small><br>
                                <small>🔥 {des.get('calorias_aprox', '')} kcal | 🥩 {des.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Merienda Mañana
                        if "merienda_manana" in comidas:
                            mer_m = comidas["merienda_manana"]
                            st.markdown(f"""<div class="exercise-card" style="border-left-color: #81C784;">
                                <h4 style="margin:0; color: #81C784;">🥪 Merienda Media Mañana</h4>
                                <strong>{mer_m.get('comida', 'N/A')}</strong><br>
                                <small>📏 {mer_m.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {mer_m.get('tip', '')}</small><br>
                                <small>🔥 {mer_m.get('calorias_aprox', '')} kcal</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Almuerzo
                        if "almuerzo" in comidas:
                            alm = comidas["almuerzo"]
                            st.markdown(f"""<div class="exercise-card" style="border-left-color: #64B5F6;">
                                <h4 style="margin:0; color: #64B5F6;">🍽️ Almuerzo</h4>
                                <strong>{alm.get('comida', 'N/A')}</strong><br>
                                <small>📏 {alm.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {alm.get('tip', '')}</small><br>
                                <small>🔥 {alm.get('calorias_aprox', '')} kcal | 🥩 {alm.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Merienda Tarde
                        if "merienda_tarde" in comidas:
                            mer_t = comidas["merienda_tarde"]
                            st.markdown(f"""<div class="exercise-card" style="border-left-color: #F06292;">
                                <h4 style="margin:0; color: #F06292;">🍌 Merienda Media Tarde (Post-Entreno)</h4>
                                <strong>{mer_t.get('comida', 'N/A')}</strong><br>
                                <small>📏 {mer_t.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {mer_t.get('tip', '')}</small><br>
                                <small>🔥 {mer_t.get('calorias_aprox', '')} kcal | 🥩 {mer_t.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Cena
                        if "cena" in comidas:
                            cena = comidas["cena"]
                            st.markdown(f"""<div class="exercise-card" style="border-left-color: #9C27B0;">
                                <h4 style="margin:0; color: #9C27B0;">🌙 Cena</h4>
                                <strong>{cena.get('comida', 'N/A')}</strong><br>
                                <small>📏 {cena.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {cena.get('tip', '')}</small><br>
                                <small>🔥 {cena.get('calorias_aprox', '')} kcal | 🥩 {cena.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
        else:
            st.info("No tienes un plan de dieta aún. ¡Genera uno abajo!")
        
        st.markdown("---")
        
        # Botones para generar y actualizar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generar Mi Plan de Nutrición con IA", use_container_width=True, key="gen_dieta"):
                perfil_nutri = {
                    "nombre": u.get('nombre', 'Usuario'),
                    "sexo": u.get('sexo', 'Masculino'),
                    "edad": u.get('edad', 25),
                    "peso_lb": u.get('peso_lb', 160),
                    "estatura_m": u.get('estatura_m', 1.70),
                    "objetivos": u.get('objetivos', [])[:2],  # Top 2 objetivos
                    "dias_entreno": u.get('dias_entreno', 5),
                    "calorias_objetivo": cal
                }
                
                with st.spinner("🤖 IA generando plan nutricional personalizado..."):
                    nueva_dieta = generar_dieta_semanal(json.dumps(perfil_nutri))
                
                if nueva_dieta:
                    st.session_state.data["dieta_semanal"] = nueva_dieta
                    guardar_todo(st.session_state.data)
                    st.success("✅ ¡Plan de nutrición generado exitosamente!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error generando el plan. Intenta nuevamente.")
        
        with col2:
            if dieta and any(dieta.values()):
                if st.button("🔄 Regenerar Plan", use_container_width=True, key="regen_dieta"):
                    # Limpiar caché para permitir regeneración
                    st.cache_data.clear()
                    st.rerun()

    with t_entrenamiento:
        st.markdown("### 💪 Entrenar Hoy")
        from datetime import datetime
        hoy = datetime.now().strftime("%A")
        dias_map = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
        dia_hoy = dias_map.get(hoy, hoy)
        
        rutina = st.session_state.data.get("rutina_semanal", {})
        
        if dia_hoy in rutina:
            ejercicios_hoy = rutina[dia_hoy]
            # Obtener músculos del día
            musculos = obtener_musculos_del_dia(ejercicios_hoy if isinstance(ejercicios_hoy, list) else [])
            musculos_text = ", ".join(musculos) if musculos else "Descanso"
            
            st.success(f"✅ Hoy es {dia_hoy} - 🔥 {musculos_text}")
            
            # Mostrar warmup sugerido
            with st.expander("🔥 Warmup Personalizado (5 min)"):
                warmup = generar_warmup(dia_hoy, ejercicios_hoy if isinstance(ejercicios_hoy, list) else [])
                for actividad in warmup.get('warmup', []):
                    st.write(f"⏱️ {actividad['actividad']} - {actividad['duracion_min']} min")
            
            st.markdown("---")
            st.markdown("#### 📋 Marcar Ejercicios Completados")
            
            # Entrenamientos
            if isinstance(ejercicios_hoy, list):
                # Crear un contenedor para trackear ejercicios completados
                if 'ejercicios_completados_hoy' not in st.session_state:
                    st.session_state.ejercicios_completados_hoy = {idx: False for idx in range(len(ejercicios_hoy))}
                
                ejercicios_datos = []
                
                for idx, ej in enumerate(ejercicios_hoy):
                    with st.container():
                        # Checkbox para marcar como completado
                        col_check, col_content = st.columns([0.5, 9.5])
                        
                        with col_check:
                            completado = st.checkbox(
                                "✓",
                                value=st.session_state.ejercicios_completados_hoy.get(idx, False),
                                key=f"check_{idx}",
                                label_visibility="collapsed"
                            )
                            st.session_state.ejercicios_completados_hoy[idx] = completado
                        
                        with col_content:
                            # Estilo visual dependiendo si está completado
                            style = "border: 2px solid #4CAF50; background-color: rgba(76, 175, 80, 0.1);" if completado else "border: 2px solid #ddd;"
                            
                            with st.expander(f"{'✅' if completado else '🏋️'} {ej['ejercicio']}", expanded=(idx == 0)):
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.info(f"💡 {ej.get('tip', '')}")
                                
                                with col_info2:
                                    st.markdown(f"**Plan del día:**")
                                    for s_idx, detalle in enumerate(ej.get('detalles_sets', [])):
                                        st.write(f"Set {s_idx+1}: {detalle['reps']} reps × {detalle['libras']} lbs (⏱️ {calcular_tiempo_descanso(u.get('objetivos', [''])[0] if u.get('objetivos') else 'hipertrofia', detalle['reps'])})")
                                
                                st.markdown("---")
                                st.markdown("**Registra tu desempeño real:**")
                                
                                # Registrar resultado
                                with st.form(f"form_ejer_{idx}"):
                                    col_r, col_p, col_n = st.columns([1, 1, 2])
                                    
                                    with col_r:
                                        reps_real = st.number_input(f"Reps completadas", 0, 100, key=f"reps_{idx}")
                                    
                                    with col_p:
                                        peso_real = st.number_input(f"Peso (lbs)", 0.0, 1000.0, key=f"peso_{idx}")
                                    
                                    with col_n:
                                        notas = st.text_input(f"Notas (opcional)", key=f"notas_{idx}", label_visibility="visible")
                                    
                                    col_submit1, col_submit2 = st.columns(2)
                                    with col_submit1:
                                        if st.form_submit_button(f"✅ Registrar {ej['ejercicio']}", use_container_width=True):
                                            if reps_real > 0 and peso_real > 0:
                                                ejercicios_datos.append({
                                                    "nombre": ej['ejercicio'],
                                                    "reps_completadas": reps_real,
                                                    "peso_levantado": peso_real,
                                                    "notas": notas,
                                                    "series_planificadas": int(ej['series']),
                                                    "reps_planificadas": ej.get('detalles_sets', [{}])[0].get('reps', 0),
                                                    "peso_planificado": ej.get('detalles_sets', [{}])[0].get('libras', 0)
                                                })
                                                st.session_state.ejercicios_completados_hoy[idx] = True
                                                st.success(f"✅ {ej['ejercicio']} registrado!")
                                            else:
                                                st.warning("⚠️ Debes ingresar reps y peso")
                
                st.markdown("---")
                
                # Resumen del entrenamiento
                completados = sum(1 for v in st.session_state.ejercicios_completados_hoy.values() if v)
                total = len(ejercicios_hoy)
                
                st.markdown(f"### 📊 Progreso de Hoy")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Ejercicios Completados", f"{completados}/{total}")
                with col_p2:
                    porcentaje = int((completados / total * 100) if total > 0 else 0)
                    st.metric("Porcentaje", f"{porcentaje}%")
                with col_p3:
                    if completados == total:
                        st.success("¡ENTRENAMIENTO COMPLETO! 🎉")
                    else:
                        st.info(f"Te faltan {total - completados} ejercicio(s)")
                
                # Botón para guardar todo el entrenamiento
                if st.button("💾 Guardar Entrenamiento Completo", key="save_all_training", use_container_width=True):
                    if completados > 0:
                        entrenamiento = registrar_entrenamiento(dia_hoy, ejercicios_datos)
                        st.session_state.data["historial_entrenamientos"].append(entrenamiento)
                        
                        # Actualizar PR por ejercicio
                        pr_data = st.session_state.data.get("pr_por_ejercicio", {})
                        for ej_data in ejercicios_datos:
                            ej_nombre = ej_data["nombre"]
                            peso_levantado = ej_data["peso_levantado"]
                            if ej_nombre not in pr_data or peso_levantado > pr_data[ej_nombre]:
                                pr_data[ej_nombre] = peso_levantado
                        st.session_state.data["pr_por_ejercicio"] = pr_data
                        
                        guardar_todo(st.session_state.data)
                        st.success("¡Entrenamiento guardado exitosamente!")
                        st.balloons()
                        
                        # Limpiar estado
                        st.session_state.ejercicios_completados_hoy = {idx: False for idx in range(len(ejercicios_hoy))}
                        st.rerun()
                    else:
                        st.warning("⚠️ Debes registrar al menos un ejercicio")
            else:
                st.info(f"📅 {ejercicios_hoy}")
        else:
            st.warning(f"📅 No hay rutina para {dia_hoy}")

    with t_alternativas:
        st.markdown("### 🔄 Ejercicios Alternativos")
        st.write("¿No tienes equipo disponible? Encuentra alternativas para tus ejercicios.")
        
        rutina = st.session_state.data.get("rutina_semanal", {})
        todos_ejercicios = []
        mapeo_ejercicio_dia = {}
        
        # Crear lista con ID único
        for dia, ejercicios in rutina.items():
            if isinstance(ejercicios, list):
                for idx, e in enumerate(ejercicios):
                    ej_name = e['ejercicio']
                    unique_id = f"{dia}_{idx}"  # ID único: día_índice
                    todos_ejercicios.append((ej_name, unique_id))
                    mapeo_ejercicio_dia[unique_id] = (dia, idx, ej_name)
        
        if todos_ejercicios:
            col1, col2 = st.columns([2, 1])
            with col1:
                ejercicio_display = [e[0] for e in todos_ejercicios]
                idx_sel = st.selectbox("Selecciona un ejercicio", range(len(ejercicio_display)), 
                                       format_func=lambda i: ejercicio_display[i])
                unique_id = todos_ejercicios[idx_sel][1]
                ejercicio_sel = todos_ejercicios[idx_sel][0]
            
            with col2:
                buscar = st.button("🔍 Buscar Alternativas", use_container_width=True)
            
            if buscar:
                with st.spinner("Buscando alternativas con IA..."):
                    alternativas = obtener_ejercicios_alternativos(ejercicio_sel, "")
                    
                    st.markdown(f"**Alternativas para: {ejercicio_sel}**")
                    
                    if alternativas.get('alternativas') and len(alternativas['alternativas']) > 0:
                        for idx, alt in enumerate(alternativas['alternativas'], 1):
                            col_alt1, col_alt2 = st.columns([3, 1])
                            with col_alt1:
                                st.write(f"**Opción {idx}: {alt['nombre']}**")
                                st.caption(f"💡 {alt['razon']}")
                            with col_alt2:
                                if st.button(f"✅ Usar", key=f"alt_{idx}_{unique_id}"):
                                    # Obtener datos del mapeo
                                    dia, ej_idx, ej_original = mapeo_ejercicio_dia[unique_id]
                                    
                                    # Reemplazar en rutina
                                    st.session_state.data["rutina_semanal"][dia][ej_idx]['ejercicio'] = alt['nombre']
                                    guardar_todo(st.session_state.data)
                                    
                                    # Recargar desde JSON para asegurar sincronización
                                    st.session_state.data = cargar_todo()
                                    
                                    st.success(f"✅ {ej_original} → {alt['nombre']}")
                                    st.toast(f"Cambio guardado en {dia}", icon="💪")
                                    st.balloons()
                                    
                                    # Pequeña pausa y rerun
                                    import time
                                    time.sleep(0.5)
                                    st.rerun()
                    else:
                        st.warning("⚠️ No se encontraron alternativas en este momento")
        else:
            st.info("Carga una rutina primero")

    with t_recomendaciones:
        st.markdown("### 🤖 Recomendaciones Personalizadas")
        
        historial_ent = st.session_state.data.get("historial_entrenamientos", [])
        if len(historial_ent) >= 3:
            if st.button("🔮 Generar Recomendaciones"):
                with st.spinner("Analizando tu progreso..."):
                    progreso = {
                        "entrenamientos_totales": len(historial_ent),
                        "ultimo_entrenamiento": historial_ent[-1] if historial_ent else None
                    }
                    recomendaciones = recomendaciones_ia(progreso, u)
                    
                    for rec in recomendaciones.get('recomendaciones', []):
                        st.info(f"**{rec['titulo']}**\n{rec['descripcion']}")
        else:
            st.info(f"Necesitas al menos 3 entrenamientos registrados (tienes {len(historial_ent)})")


    with t_progreso:
        st.markdown("### 📊 Evolución y Análisis Nutricional")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("#### ⚖️ Registrar Peso")
            with st.form("log_peso"):
                peso_actual = float(u.get('peso_lb', 160.0)) if u.get('peso_lb') else 160.0
                n_p = st.number_input("Peso de hoy (Lbs)", 50.0, 500.0, peso_actual)
                if st.form_submit_button("Anotar Peso"):
                    from datetime import date
                    hoy = str(date.today())
                    st.session_state.data["historial_pesos"].append({"fecha": hoy, "peso": n_p})
                    st.session_state.data["user"]["peso_lb"] = n_p
                    guardar_todo(st.session_state.data)
                    st.success(f"¡Peso de {n_p} lbs registrado!")
                    st.rerun()
            
            cal, p, g, c = calcular_macros(u)
            st.markdown(f"""
                <div class="exercise-card" style="border-left-color: var(--secondary);">
                    <h4 style="margin:0;">🔥 Calorías Objetivo</h4>
                    <h2 style="margin:0; color: var(--secondary);">{cal} kcal</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Macros Directriz:**")
            st.write(f"🥩 Proteína: {p}g | 🍞 Carbos: {c}g | 🥑 Grasas: {g}g")

        with c2:
            st.markdown("#### 📉 Tendencia de Peso")
            historial = st.session_state.data.get("historial_pesos", [])
            if historial:
                df = pd.DataFrame(historial)
                df['fecha'] = pd.to_datetime(df['fecha'])
                st.line_chart(df.set_index('fecha')['peso'])
                
                # Estadísticas
                pesos = [h['peso'] for h in historial]
                st.metric("Peso Inicial", f"{pesos[0]:.1f} lbs", f"{pesos[-1] - pesos[0]:.1f} lbs")
            else:
                st.info("Aún no tienes registros de peso. ¡Empieza hoy!")
            
            st.markdown("#### 📅 Historial de Entrenamientos")
            historial_ent = st.session_state.data.get("historial_entrenamientos", [])
            if historial_ent:
                entrenamientos_df = pd.DataFrame(historial_ent)
                if len(entrenamientos_df) > 0:
                    st.metric("Total Entrenamientos", len(entrenamientos_df))
                    
                    # Mostrar últimos entrenamientos con detalles
                    st.markdown("**Últimos Entrenamientos:**")
                    for entrenamiento in historial_ent[-5:]:  # Mostrar últimos 5
                        fecha = entrenamiento.get('fecha', 'N/A')
                        dia = entrenamiento.get('dia', 'N/A')
                        ejercicios = entrenamiento.get('ejercicios', [])
                        
                        with st.expander(f"📅 {fecha} - {dia} ({len(ejercicios)} ejercicios)"):
                            for ej in ejercicios:
                                st.write(f"✅ **{ej['nombre']}**: {ej['reps_completadas']} reps × {ej['peso_levantado']} lbs")
                                if ej.get('notas'):
                                    st.caption(f"📝 {ej['notas']}")
            else:
                st.info("Aún no has registrado entrenamientos.")
            
            st.markdown("#### 🏆 Personal Records (PR)")
            pr_data = st.session_state.data.get("pr_por_ejercicio", {})
            if pr_data:
                st.markdown("**Tus mejores pesos levantados:**")
                for ejercicio, peso in sorted(pr_data.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"🥇 **{ejercicio}**: {peso} lbs")
            else:
                st.info("Aún no tienes records. ¡Empieza a entrenar!")

    with t_perfil:
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
                
                # Actualización automática de la rutina al editar el perfil
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(nueva_data_user)
                
                # Guardar en gym_data.json
                guardar_todo(st.session_state.data)
                
                # Guardar también en user_data.json para que persista el perfil
                actualizar_perfil_usuario(st.session_state.usuario_logueado, nueva_data_user)
                
                st.success("¡Perfil y rutina actualizados con éxito!")
                st.rerun()

        st.markdown("---")
        st.info("💡 Tip: Ve a la sección 'Mi Rutina' para regenerar tu rutina inteligente con los nuevos datos.")


