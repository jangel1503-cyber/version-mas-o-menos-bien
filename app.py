import streamlit as st
import json
import os
import random
import pandas as pd
import google.generativeai as genai
import hashlib
from config import *  # Importar todas las configuraciones

# --- CONFIGURACIÓN ---
st.set_page_config(**PAGE_CONFIG)

def hash_password(password):
    """Hashea una contraseña usando SHA-256 con salt"""
    salt = PASSWORD_SALT.encode()
    return hashlib.sha256(salt + password.encode()).hexdigest()

def verificar_password(password, hash_guardado):
    """Verifica si una contraseña coincide con el hash guardado"""
    return hash_password(password) == hash_guardado

# --- ESTILOS CSS PERSONALIZADOS ---
def aplicar_estilos():
    """Aplica estilos CSS desde archivo externo"""
    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            estilos = f"<style>{f.read()}</style>"
        st.markdown(estilos, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Archivo styles.css no encontrado. Usando estilos básicos.")
        estilos_basicos = """
        <style>
        body { font-family: Arial, sans-serif; }
        .main-header { font-size: 2rem; color: #333; }
        </style>
        """
        st.markdown(estilos_basicos, unsafe_allow_html=True)

# Aplicar estilos al cargar la página
aplicar_estilos()

# Cargar API key desde secrets (Streamlit Cloud) o variable local
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Inicializar estado de sesión
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

# --- GESTIÓN DE USUARIOS ---
def cargar_usuarios():
    """Carga la base de datos de usuarios desde user_data.json"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            st.error(f"Error cargando usuarios: {e}")
            return {}
    return {}

def guardar_usuarios(usuarios):
    """Guarda la base de datos de usuarios en user_data.json"""
    with open(USERS_FILE, "w", encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

def usuario_existe(username):
    """Verifica si un usuario ya existe"""
    usuarios = cargar_usuarios()
    return username.lower() in usuarios

def validar_credenciales(username, password):
    """Valida el nombre de usuario y contraseña"""
    usuarios = cargar_usuarios()
    user_lower = username.lower()
    if user_lower in usuarios:
        hash_guardado = usuarios[user_lower].get("password")
        return verificar_password(password, hash_guardado)
    return False

def registrar_usuario(username, password, datos_perfil):
    """Registra un nuevo usuario con sus datos de perfil"""
    usuarios = cargar_usuarios()
    usuario_lower = username.lower()
    
    if usuario_lower in usuarios:
        return False, "El usuario ya existe"
    
    usuarios[usuario_lower] = {
        "username": username,
        "password": hash_password(password),  # ⚠️ SEGURIDAD: Ahora usa hash
        "datos_perfil": datos_perfil,
        "fecha_registro": str(pd.Timestamp.now())
    }
    guardar_usuarios(usuarios)
    
    # IMPORTANTE: Guardar estructura inicial en gym_data.json
    todo_datos = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                todo_datos = json.load(f)
        except:
            todo_datos = {}
    
    # Crear estructura inicial para el usuario
    todo_datos[usuario_lower] = {
        "perfil_completado": True,
        "user": datos_perfil,
        "rutina_semanal": {},
        "historial_pesos": [],
        "historial_entrenamientos": [],
        "pr_por_ejercicio": {},
        "fecha_ultima_rotacion": None,
        "dieta_semanal": {}
    }
    
    # Guardar en gym_data.json
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(todo_datos, f, ensure_ascii=False, indent=4)
    
    return True, "Usuario registrado exitosamente"

def actualizar_perfil_usuario(username, datos_perfil):
    """Actualiza los datos del perfil de un usuario en user_data.json"""
    usuarios = cargar_usuarios()
    user_lower = username.lower()
    
    if user_lower in usuarios:
        usuarios[user_lower]["datos_perfil"] = datos_perfil
        guardar_usuarios(usuarios)
        return True
    return False

def obtener_datos_usuario(username):
    """Obtiene los datos del perfil de un usuario"""
    usuarios = cargar_usuarios()
    user_lower = username.lower()
    if user_lower in usuarios:
        datos = usuarios[user_lower].get("datos_perfil", {})
        # Asegurar que tienen valores por defecto
        if not datos:
            datos = {}
        if "peso_lb" not in datos:
            datos["peso_lb"] = 160.0
        if "estatura_m" not in datos:
            datos["estatura_m"] = 1.70
        if "dias_entreno" not in datos:
            datos["dias_entreno"] = 5
        return datos
    return {"peso_lb": 160.0, "estatura_m": 1.70, "dias_entreno": 5}

# --- PERSISTENCIA ---
def guardar_todo(datos):
    """Guarda datos del usuario actual en gym_data.json"""
    usuario = st.session_state.usuario_logueado if st.session_state.usuario_logueado else "default"
    
    # Cargar datos existentes
    todos_datos = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                todos_datos = json.load(f)
        except:
            todos_datos = {}
    
    # Guardar datos del usuario especifico
    todos_datos[usuario] = datos
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(todos_datos, f, ensure_ascii=False, indent=4)

def cargar_todo():
    """Carga datos del usuario actual desde gym_data.json"""
    usuario = st.session_state.usuario_logueado if st.session_state.usuario_logueado else "default"

    estructura_vacia = {
        "perfil_completado": False,
        "user": {"dias_entreno": 5},
        "rutina_semanal": {},
        "historial_pesos": [],
        "historial_entrenamientos": [],
        "pr_por_ejercicio": {},
        "fecha_ultima_rotacion": None,
        "dieta_semanal": {}
    }

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                todos_datos = json.load(f)
                if usuario in todos_datos:
                    data = todos_datos[usuario]
                else:
                    data = estructura_vacia.copy()

                # Asegurar compatibilidad
                if "historial_pesos" not in data:
                    data["historial_pesos"] = []
                if "user" in data and "dias_entreno" not in data["user"]:
                    data["user"]["dias_entreno"] = 5
                if "historial_entrenamientos" not in data:
                    data["historial_entrenamientos"] = []
                if "pr_por_ejercicio" not in data:
                    data["pr_por_ejercicio"] = {}
                if "fecha_ultima_rotacion" not in data:
                    data["fecha_ultima_rotacion"] = None
                if "dieta_semanal" not in data:
                    data["dieta_semanal"] = {}
                return data
        except (json.JSONDecodeError, IOError, KeyError) as e:
            st.warning(f"Error cargando datos de {usuario}: {e}. Usando datos por defecto.")
            return estructura_vacia
    return estructura_vacia

def asegurar_datos_frescos():
    """Asegura que los datos en session_state estén actualizados sin recargar innecesariamente"""
    # Solo recargar si no hay datos o si han pasado cambios
    if not hasattr(st.session_state, '_ultima_carga') or st.session_state._ultima_carga != st.session_state.usuario_logueado:
        st.session_state.data = cargar_todo()
        st.session_state._ultima_carga = st.session_state.usuario_logueado

if 'data' not in st.session_state or (st.session_state.usuario_logueado and st.session_state.data.get('user', {}) == {}):
    # Cargar datos si hay usuario logueado O si nunca se ha cargado nada
    if st.session_state.usuario_logueado:
        st.session_state.data = cargar_todo()
    else:
        # Estructura vacía para la pantalla de login
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

# --- LÓGICA DE SALUD ---
def obtener_analisis(peso_lb, estatura_m):
    if estatura_m <= 0: return 0, "N/A", 0, 0
    peso_kg = peso_lb * 0.453592
    imc = round(peso_kg / (estatura_m**2), 1)
    
    if imc < 18.5: estado = "Bajo peso"
    elif 18.5 <= imc <= 24.9: estado = "Peso normal"
    elif 25.0 <= imc <= 29.9: estado = "Sobrepeso"
    else: estado = "Obesidad"
    
    p_min = round(18.5 * (estatura_m**2) / 0.453592, 1)
    p_max = round(24.9 * (estatura_m**2) / 0.453592, 1)
    
    return imc, estado, p_min, p_max

# --- LÓGICA NUTRICIONAL ---
def calcular_macros(u):
    peso_kg = u.get('peso_lb', 160) * 0.453592
    estatura_cm = u.get('estatura_m', 1.70) * 100
    edad = u.get('edad', 25)
    dias = u.get('dias_entreno', 5)
    sexo = u.get('sexo', 'Masculino')
    
    # BMR (Mifflin-St Jeor) - fórmula según sexo
    if sexo == 'Femenino':
        bmr = (10 * peso_kg) + (6.25 * estatura_cm) - (5 * edad) - 161
    else:  # Masculino
        bmr = (10 * peso_kg) + (6.25 * estatura_cm) - (5 * edad) + 5
    
    # Multiplicador dinámico basado en días de entreno
    activ = 1.2 if dias < 3 else (1.375 if dias == 3 else (1.55 if dias == 4 else 1.725))
    tdee = bmr * activ
    
    objetivos = u.get('objetivos', [])
    target = tdee
    if any("perder grasa" in obj.lower() or "bajar peso" in obj.lower() for obj in objetivos):
        target = tdee * 0.8 # Déficit 20%
    elif any("ganar masa" in obj.lower() or "aumentar fuerza" in obj.lower() for obj in objetivos):
        target = tdee * 1.1 # Superávit 10%
        
    prot = peso_kg * 2.0 # 2g por kg
    grasas = peso_kg * 0.8
    carbs = (target - (prot * 4) - (grasas * 9)) / 4
    
    return round(target), round(prot), round(grasas), round(carbs)

# --- BASE DE DATOS LOCAL DE COMIDAS VARIADAS Y PERSONALIZADAS ---
COMIDAS_DB = {
    "proteinas": {
        "general": ["Pechuga de pollo", "Salmón", "Atún", "Pavo", "Huevo", "Carne molida 85%", "Tilapia", "Yogur griego", "Requesón"],
        "femenino": ["Salmón", "Atún", "Espinacas", "Lentejas", "Huevo", "Yogur griego", "Pechuga de pollo", "Requesón"],  # Alto hierro
        "masculino": ["Pechuga de pollo", "Carne molida 85%", "Huevo", "Pavo", "Tilapia", "Salmón", "Atún"]
    },
    "carbos": {
        "general": ["Arroz integral", "Papa blanca", "Papa dulce", "Pan integral", "Avena", "Plátano", "Quinoa", "Pasta integral", "Arroz blanco"],
        "pre_entreno": ["Plátano", "Papa blanca", "Arroz blanco", "Pan integral", "Pasta integral"],  # Carbos rápidos/moderados
        "post_entreno": ["Plátano", "Papa blanca", "Arroz blanco", "Avena"],  # Carbos de absorción rápida
        "edad_mayor": ["Avena", "Quinoa", "Papa dulce", "Pan integral", "Arroz integral"]  # Más fibra
    },
    "grasas": {
        "general": ["Aguacate", "Aceite de oliva", "Mantequilla de maní", "Almendras", "Nueces", "Semillas de linaza"],
        "omega3": ["Salmón", "Atún", "Semillas de linaza", "Aceite de oliva"]  # Para edad avanzada
    },
    "verduras": {
        "general": ["Brócoli", "Espinaca", "Lechuga", "Tomate", "Zanahoria", "Calabacín", "Chayote", "Vainitas", "Pepino"],
        "femenino": ["Espinaca", "Brócoli", "Lechuga", "Tomate", "Zanahoria"],  # Hierro y fibra
        "edad_mayor": ["Brócoli", "Espinaca", "Zanahoria", "Calabacín"]  # Fácil digestión
    }
}

def generar_dieta_fallback_local(perfil_json):
    """Genera plan de dieta completamente personalizado considerando sexo, edad y objetivo"""
    try:
        perfil = json.loads(perfil_json)
        cal_objetivo = perfil.get("calorias_objetivo", 2100)
        sexo = perfil.get("sexo", "Masculino")
        edad = perfil.get("edad", 25)
        objetivo = perfil.get("objetivos", ["Tonificar"])[0].lower()
        dias_entreno = perfil.get("dias_entreno", 5)
        
        # Determinar tipo de usuario para selección de alimentos
        es_mujer = sexo == "Femenino"
        es_mayor = edad >= 50
        mucho_entreno = dias_entreno >= 5
        
        # Ajustar macros según objetivo
        if "perder grasa" in objetivo or "bajar peso" in objetivo:
            objetivo_text = "Déficit calórico 20%"
            proteina_g = int(cal_objetivo / 4.5)  # 2.2g/kg equiv
            carbs_g = int((cal_objetivo * 0.35) / 4)
            grasas_g = int((cal_objetivo * 0.3) / 9)
            cal_objetivo = int(cal_objetivo)
        elif "ganar masa" in objetivo or "aumentar fuerza" in objetivo:
            objetivo_text = "Superávit 10%"
            proteina_g = int((cal_objetivo * 0.35) / 4)
            carbs_g = int((cal_objetivo * 0.45) / 4)
            grasas_g = int((cal_objetivo * 0.20) / 9)
            cal_objetivo = int(cal_objetivo)
        else:
            objetivo_text = "Mantenimiento"
            proteina_g = int((cal_objetivo * 0.30) / 4)
            carbs_g = int((cal_objetivo * 0.40) / 4)
            grasas_g = int((cal_objetivo * 0.30) / 9)
            cal_objetivo = int(cal_objetivo)
        
        # Seleccionar pool de alimentos según perfil
        proteinas_pool = COMIDAS_DB["proteinas"].get(
            "femenino" if es_mujer else "masculino", 
            COMIDAS_DB["proteinas"]["general"]
        )
        verduras_pool = COMIDAS_DB["verduras"].get(
            "femenino" if es_mujer else "general", 
            COMIDAS_DB["verduras"]["general"]
        )
        carbos_pool_general = COMIDAS_DB["carbos"].get(
            "edad_mayor" if es_mayor else "general",
            COMIDAS_DB["carbos"]["general"]
        )
        carbos_pre = COMIDAS_DB["carbos"]["pre_entreno"]
        carbos_post = COMIDAS_DB["carbos"]["post_entreno"]
        grasas_pool = COMIDAS_DB["grasas"].get(
            "omega3" if es_mayor else "general",
            COMIDAS_DB["grasas"]["general"]
        )
        
        # Generar plan para 7 días
        plan_semanal = {}
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        proteinas_usadas = []
        
        for idx_dia, dia in enumerate(dias):
            # Seleccionar proteína sin repetición
            prot_disponibles = [p for p in proteinas_pool if p not in proteinas_usadas[-2:]]
            proteina_hoy = random.choice(prot_disponibles if prot_disponibles else proteinas_pool)
            proteinas_usadas.append(proteina_hoy)
            
            # Seleccionar carbos específicos para timing de entreno
            carbos_hoy = random.sample(carbos_pool_general, min(3, len(carbos_pool_general)))
            carbo_pre = random.choice(carbos_pre)  # Para merienda mañana
            carbo_post = random.choice(carbos_post)  # Para merienda tarde
            verduras_hoy = random.sample(verduras_pool, min(3, len(verduras_pool)))
            grasa_hoy = random.choice(grasas_pool)
            
            # ===== DESAYUNO =====
            if es_mujer and random.random() > 0.5:
                # Variante alto hierro para mujeres
                desayuno_comida = f"Espinacas salteadas con huevos y pan integral"
                desayuno_cantidad = "100g espinacas + 2 huevos + 2 rebanadas pan integral + 5g aceite"
                desayuno_ingredientes = "Espinacas, huevo, pan integral, aceite de oliva"
                desayuno_cal = 300
                desayuno_prot = 16
                desayuno_tip = "Alto en hierro + proteína para mantener energía (especialmente importante para mujeres)"
            else:
                desayuno_comida = "2 huevos + tostadas de pan integral con tomate"
                desayuno_cantidad = "2 huevos (60g) + 2 rebanadas pan integral + 100g tomate + 5g aceite"
                desayuno_ingredientes = "Huevos, pan integral, tomate, aceite de oliva"
                desayuno_cal = 280
                desayuno_prot = 18
                desayuno_tip = "Proteína de alta calidad + carbos complejos para energía sostenida"
            
            # ===== MERIENDA MAÑANA (PRE-ENTRENO) =====
            if mucho_entreno:
                # Más energía pre-entreno si entrena 5+ días
                merienda_m_comida = f"{carbo_pre.lower()} con {grasa_hoy.lower()}"
                merienda_m_cantidad = f"1 {carbo_pre.lower()} mediano/a (120g) + 20g {grasa_hoy.lower()}"
                merienda_m_cal = 220
                merienda_m_prot = 5
                merienda_m_tip = "Energía PRE-ENTRENO: carbos + grasas para rendimiento máximo"
            else:
                merienda_m_comida = f"{carbo_pre.lower()} con {grasa_hoy.lower()}"
                merienda_m_cantidad = f"1 {carbo_pre.lower()} mediano/a (120g) + 15g {grasa_hoy.lower()}"
                merienda_m_cal = 180
                merienda_m_prot = 3
                merienda_m_tip = "Energía pre-entreno: carbos + grasas saludables"
            
            # ===== ALMUERZO =====
            almuerzo_comida = f"{proteina_hoy} a la parrilla con {carbos_hoy[0].lower()} y {verduras_hoy[0].lower()}"
            almuerzo_cantidad = f"180g {proteina_hoy.lower()} cocida + 150g {carbos_hoy[0].lower()} cocido + 200g ensalada ({verduras_hoy[0].lower()}, {verduras_hoy[1].lower()}) + 10ml aceite"
            almuerzo_ingredientes = f"{proteina_hoy}, {carbos_hoy[0]}, {verduras_hoy[0]}, {verduras_hoy[1]}, aceite de oliva"
            almuerzo_cal = 620
            almuerzo_prot = 48
            almuerzo_tip = "Comida principal: proteína magra + carbos complejos + vitaminas y minerales"
            
            # ===== MERIENDA TARDE (POST-ENTRENO) =====
            if mucho_entreno:
                # Recuperación rápida si entrena mucho
                merienda_t_comida = f"Batido de proteína con {carbo_post.lower()}"
                merienda_t_cantidad = f"30g proteína en polvo + 200ml leche + 100g {carbo_post.lower()}"
                merienda_t_cal = 280
                merienda_t_prot = 30
                merienda_t_tip = "POST-ENTRENO: proteína + carbos rápidos para recuperación y síntesis muscular"
            else:
                if es_mujer:
                    # Más rico en calcio para mujeres
                    merienda_t_comida = f"Yogur griego con {carbo_post.lower()}"
                else:
                    merienda_t_comida = f"Yogur griego con {carbo_post.lower()}"
                merienda_t_cantidad = f"150g yogur griego + 80g {carbo_post.lower()} + 10g miel"
                merienda_t_cal = 210
                merienda_t_prot = 20
                merienda_t_tip = "POST-ENTRENO: proteína rápida + carbos para recuperación muscular"
            
            # ===== CENA =====
            if es_mayor:
                # Cena más ligera y fácil de digerir para mayor edad
                cena_comida = f"{proteina_hoy} al vapor con {carbos_hoy[2].lower()} y {verduras_hoy[2].lower()}"
                cena_cantidad = f"120g {proteina_hoy.lower()} + 100g {carbos_hoy[2].lower()} + 150g {verduras_hoy[2].lower()} al vapor"
                cena_cal = 320
                cena_prot = 28
                cena_tip = "Cena ligera: fácil de digerir, proteína moderada, sin exceso de grasas"
            else:
                cena_comida = f"{proteina_hoy} a la parrilla con {carbos_hoy[2].lower()} y {verduras_hoy[2].lower()}"
                cena_cantidad = f"150g {proteina_hoy.lower()} + 120g {carbos_hoy[2].lower()} + 150g {verduras_hoy[2].lower()} al vapor + 5ml aceite"
                cena_cal = 380
                cena_prot = 32
                cena_tip = "Cena equilibrada: proteína + carbos de lenta absorción + verduras bajas en calorías"
            
            plan_semanal[dia] = {
                "desayuno": {
                    "comida": desayuno_comida,
                    "cantidad": desayuno_cantidad,
                    "ingredientes": desayuno_ingredientes,
                    "calorias_aprox": desayuno_cal,
                    "proteina_g": desayuno_prot,
                    "tip": desayuno_tip
                },
                "merienda_manana": {
                    "comida": merienda_m_comida,
                    "cantidad": merienda_m_cantidad,
                    "ingredientes": f"{carbo_pre}, {grasa_hoy}",
                    "calorias_aprox": merienda_m_cal,
                    "proteina_g": merienda_m_prot,
                    "tip": merienda_m_tip
                },
                "almuerzo": {
                    "comida": almuerzo_comida,
                    "cantidad": almuerzo_cantidad,
                    "ingredientes": almuerzo_ingredientes,
                    "calorias_aprox": almuerzo_cal,
                    "proteina_g": almuerzo_prot,
                    "tip": almuerzo_tip
                },
                "merienda_tarde": {
                    "comida": merienda_t_comida,
                    "cantidad": merienda_t_cantidad,
                    "ingredientes": f"Proteína, {carbo_post}, leche/yogur" if mucho_entreno else f"Yogur, {carbo_post}",
                    "calorias_aprox": merienda_t_cal,
                    "proteina_g": merienda_t_prot,
                    "tip": merienda_t_tip
                },
                "cena": {
                    "comida": cena_comida,
                    "cantidad": cena_cantidad,
                    "ingredientes": f"{proteina_hoy}, {carbos_hoy[2]}, {verduras_hoy[2]}",
                    "calorias_aprox": cena_cal,
                    "proteina_g": cena_prot,
                    "tip": cena_tip
                }
            }
        
        return {
            "objetivo_nutricional": objetivo_text,
            "calorias_diarias_aprox": cal_objetivo,
            "proteina_g": proteina_g,
            "carbos_g": carbs_g,
            "grasas_g": grasas_g,
            "plan_semanal": plan_semanal
        }
    except Exception as e:
        st.error(f"Error en fallback local: {str(e)}")
        return None

# --- GENERADOR DE DIETA IA ---
def generar_dieta_semanal(perfil_json):
    """Consulta a Gemini o usa fallback local"""
    try:
        response = model.generate_content("test")  # Test para verificar disponibilidad
        # Si llegamos aquí, la API funciona, intentar generar completo
        prompt = f"""
ERES UN NUTRICIONISTA CERTIFICADO CON 15+ AÑOS DE EXPERIENCIA EN DIETAS PERSONALIZADAS.

GENERA UN PLAN DE COMIDAS SEMANAL ULTRA PERSONALIZADO (Lunes a Domingo) CON ALIMENTOS REALES Y ESPECÍFICOS.

PERFIL DEL CLIENTE:
{json.dumps(perfil_json, indent=2, ensure_ascii=False)}

CRÍTICOS - AJUSTA POR:
- Objetivo: Si es PERDER GRASA → déficit calórico 20%, proteína alta 2.2g/kg. Si es GANAR MASA → superávit 10%, proteína 2g/kg + carbos. Si es TONIFICAR → proteína 1.8g/kg, equilibrio de macros.
- Sexo: MUJERES → menos calorías base (ajusta -150-200kcal), enfatiza hierro y fibra. HOMBRES → calorías/proteína estándar, más volumen de carbos.
- Edad: >50 años → menos sodio, más omega-3 y fibra. <25 años → puede ser más flexible, más carbos alrededor del entreno.
- Nivel de energía: Si entrena 5+ días/semana → más carbos, cargas post-entreno con proteína inmediata.

ALIMENTOS ESPECÍFICOS QUE DEBES USAR (NO GENÉRICOS):

PROTEÍNAS: Pechuga de pollo, muslo de pollo, huevo, clara de huevo, salmón, atún, tilapia, pavo, carne molida 85%, carne de res magra, requesón, yogur griego, pollo desmenuzado

CARBOHIDRATOS: Arroz integral, arroz blanco, avena, trigo sarraceno, papa blanca, papa dulce, batata, pan integral, pan de centeno, plátano, manzana, piña, arándanos, quinoa, lentejas, frijoles negros, pasta integral

GRASAS: Aguacate, aceite de oliva, aceite de coco, mantequilla de maní, almendras, nueces, semillas de linaza, sardinas, huevos, coco rallado

VERDURAS: Brócoli, espinaca, lechuga, tomate, pepino, zanahoria, calabacín, chayote, vainitas, choclo, maíz, cebolla, ajo

CADA DÍA DEBE INCLUIR (5 COMIDAS ESPECÍFICAS):
1. 🌅 DESAYUNO (500-700 kcal, proteína 25-35g) - ALIMENTOS REALES CONCRETOS
2. 🥪 MERIENDA MEDIA MAÑANA (100-150 kcal, snack energético)
3. 🍽️ ALMUERZO (600-800 kcal, proteína 35-45g) - LA COMIDA FUERTE CON 3-4 INGREDIENTES ESPECÍFICOS
4. 🍌 MERIENDA MEDIA TARDE (150-200 kcal, post-entreno con proteína rápida)
5. 🌙 CENA (400-500 kcal, proteína 25-30g, MÁS LIGERA QUE ALMUERZO)

FORMATO JSON REQUERIDO (EXACTO):
{{
  "objetivo_nutricional": "Déficit/Superávit/Mantenimiento",
  "calorias_diarias_aprox": 2100,
  "proteina_g": 160,
  "carbos_g": 210,
  "grasas_g": 70,
  "plan_semanal": {{
    "Lunes": {{
      "desayuno": {{
        "comida": "Omelette de 2 claras + 1 yema con cebolla y brócoli + tostadas de pan integral",
        "cantidad": "3 huevos (2 claras + 1 yema) + 150g brócoli + 1/2 cebolla mediana + 2 tostadas de pan integral con 5g de mantequilla",
        "ingredientes": "Huevos, brócoli, cebolla, pan integral, mantequilla",
        "calorias_aprox": 350,
        "proteina_g": 28,
        "tip": "Alto en proteína, fibra del brócoli, carbos complejos del pan integral"
      }},
      "merienda_manana": {{
        "comida": "Manzana roja con mantequilla de maní",
        "cantidad": "1 manzana roja mediana (180g) + 15g de mantequilla de maní natural (sin azúcar)",
        "ingredientes": "Manzana, mantequilla de maní",
        "calorias_aprox": 140,
        "tip": "Energía sostenida para el entreno, glucosa + grasas saludables"
      }},
      "almuerzo": {{
        "comida": "Pechuga de pollo a la parrilla con arroz integral y ensalada de verduras",
        "cantidad": "180g pechuga de pollo cocida + 100g arroz integral cocido + 250g ensalada (lechuga + tomate + pepino + zanahoria rallada) + 10ml aceite de oliva",
        "ingredientes": "Pechuga de pollo, arroz integral, lechuga, tomate, pepino, zanahoria, aceite de oliva",
        "calorias_aprox": 580,
        "proteina_g": 42,
        "tip": "Proteína magra, carbos complejos, vitaminas y minerales de las verduras"
      }},
      "merienda_tarde": {{
        "comida": "Batido proteico post-entreno con plátano",
        "cantidad": "30g proteína en polvo (whey) + 200ml leche descremada + 1 plátano mediano (120g) + 5g miel",
        "ingredientes": "Proteína whey, leche, plátano, miel",
        "calorias_aprox": 220,
        "proteina_g": 32,
        "tip": "Absorción rápida post-entreno, carbos rápidos + proteína para recuperación muscular"
      }},
      "cena": {{
        "comida": "Salmón a la parrilla con papa dulce y verduras al vapor",
        "cantidad": "150g salmón cocido + 150g papa dulce cocida + 200g verduras (brócoli + chayote vapor) + 5ml aceite de oliva",
        "ingredientes": "Salmón, papa dulce, brócoli, chayote, aceite de oliva",
        "calorias_aprox": 420,
        "proteina_g": 32,
        "tip": "Omega-3 del salmón, carbos de lenta absorción, micronutrientes, cena ligera"
      }}
    }},
    "Martes": {{...}}
  }}
}}

RESTRICCIONES OBLIGATORIAS:
- ALIMENTOS REALES: Especifica marca/tipo siempre que sea posible (ej: "pechuga de pollo sin piel" no "pollo")
- CANTIDADES EXACTAS: Gramos, no "una porción" o "una taza"
- INGREDIENTES LISTADOS: Cada comida debe listar todos los ingredientes específicos
- VARIEDAD TOTAL: No repetir NINGÚN ALIMENTO en el mismo día. Entre días máximo 2 repeticiones de proteínas.
- COMIDAS REALES: Alimentos prácticos que se consiguen en cualquier supermercado local
- SIN SUPLEMENTOS INNECESARIOS: Solo proteína en polvo en merienda de tarde (post-entreno)
- RESPETAR OBJETIVO: Si pierde grasa, baja calorías. Si gana masa, aumenta calorías y carbos.
- CADA ALIMENTO TIENE RAZÓN: Explica por qué cada ingrediente (ej: "proteína de rápida absorción", "fibra para saciedad")

Solo retorna JSON válido. Sin markdown, sin explicaciones adicionales. IMPORTANTE: Todos los 7 días (Lunes-Domingo) con 5 comidas cada uno.
"""
        response = model.generate_content(prompt)
        respuesta_texto = response.text.strip()
        
        # Limpiar marcadores de código
        if respuesta_texto.startswith("```json"):
            respuesta_texto = respuesta_texto[7:]
        if respuesta_texto.startswith("```"):
            respuesta_texto = respuesta_texto[3:]
        if respuesta_texto.endswith("```"):
            respuesta_texto = respuesta_texto[:-3]
        
        dieta_dict = json.loads(respuesta_texto.strip())
        return dieta_dict
    except Exception as e:
        st.warning(f"⚠️ API de Gemini no disponible. Usando plan de dieta local personalizado.")
        return generar_dieta_fallback_local(perfil_json)

# --- MOTOR DE RUTINA IA v2 ---
EJERCICIOS_AVANZADOS = {
    "Pecho": [
        {"nombre": "Press de Banca", "tip": "Baja la barra hasta el pecho con control."},
        {"nombre": "Aperturas con Mancuernas", "tip": "Siente el estiramiento en las fibras del pectoral."},
        {"nombre": "Flexiones de Brazos", "tip": "Mantén el core activado y la espalda recta."},
        {"nombre": "Press Inclinado", "tip": "Enfócate en la parte superior del pecho."},
        {"nombre": "Fondos de Pecho", "tip": "Inclina el torso hacia adelante para activar el pectoral."}
    ],
    "Espalda": [
        {"nombre": "Remo con Barra", "tip": "Lleva el ombligo hacia atrás y junta las escápulas."},
        {"nombre": "Jalón al Pecho", "tip": "Tira desde los codos, no solo con las manos."},
        {"nombre": "Dominadas", "tip": "Cruza los pies y mantén el pecho alto."},
        {"nombre": "Remo en Polea Baja", "tip": "Mantén la espalda recta y no te balancees."},
        {"nombre": "Peso Muerto Convencional", "tip": "Mantén la barra pegada a tus canillas."}
    ],
    "Piernas": [
        {"nombre": "Sentadillas", "tip": "Baja la cadera por debajo de las rodillas si puedes."},
        {"nombre": "Prensa de Piernas", "tip": "No bloquees las rodillas al extender."},
        {"nombre": "Peso Muerto Rumano", "tip": "Siente el estiramiento en los isquiotibiales."},
        {"nombre": "Zancadas", "tip": "Mantén el equilibrio y el torso erguido."},
        {"nombre": "Extensiones de Cuádriceps", "tip": "Controla el descenso en cada repetición."},
        {"nombre": "Curl Femoral", "tip": "Aprieta los isquios en la parte superior del movimiento."}
    ],
    "Brazos": [
        {"nombre": "Curl de Bíceps", "tip": "No balancees el cuerpo, solo mueve los antebrazos."},
        {"nombre": "Press Francés", "tip": "Mantén los codos cerrados y apuntando al techo."},
        {"nombre": "Martillo", "tip": "Excelente para el braquial y antebrazo."},
        {"nombre": "Extensiones en Polea", "tip": "Extiende el brazo completamente para máxima contracción."},
        {"nombre": "Curl Predicador", "tip": "Aísla el bíceps evitando usar los hombros."}
    ],
    "Hombros": [
        {"nombre": "Press Militar", "tip": "Empuja la barra sobre tu cabeza de forma explosiva."},
        {"nombre": "Elevaciones Laterales", "tip": "No subas más allá de la altura de los hombros."},
        {"nombre": "Face Pulls", "tip": "Ideal para la salud del hombro y postura."},
        {"nombre": "Press Arnold", "tip": "Gira las palmas mientras subes para mayor rango."},
        {"nombre": "Pájaros (Hombro Posterior)", "tip": "Lucha por mantener los codos arriba."}
    ],
    "Core/Postura": [
        {"nombre": "Plancha Abdominal", "tip": "No dejes que la cadera se caiga."},
        {"nombre": "Bird-Dog", "tip": "Mejora la estabilidad lumbar y coordinación."},
        {"nombre": "Deadbug", "tip": "Mantén la espalda baja pegada al suelo."},
        {"nombre": "Rueda Abdominal", "tip": "Extiende hasta donde controles tu espalda."},
        {"nombre": "Elevación de Piernas", "tip": "No balancees las piernas, controla el movimiento."},
        {"nombre": "Russian Twists", "tip": "Gira el torso, no solo los brazos."}
    ],
    "Cardio/Funcional": [
        {"nombre": "Burpees", "tip": "El ejercicio total para quemar grasa."},
        {"nombre": "Mountain Climbers", "tip": "Velocidad constante y espalda estable."},
        {"nombre": "Salto a la Comba", "tip": "Mantén los saltos cortos y elásticos."},
        {"nombre": "Caminata Inclinada", "tip": "Quema grasa sin impacto articular."},
        {"nombre": "Kettlebell Swings", "tip": "Potencia desde la cadera, no los brazos."},
        {"nombre": "Box Jumps", "tip": "Aterriza suavemente para proteger tus rodillas."}
    ]
}

def generar_rutina_gemini(perfil_json):
    """Consulta a Gemini para generar rutina personalizada"""
    try:
        prompt = f"""
IMPORTANTE: Eres un entrenador personal certificado con 20+ años. Genera una rutina ULTRA PERSONALIZADA.

PERFIL DEL CLIENTE (CRÍTICO):
{json.dumps(perfil_json, indent=2, ensure_ascii=False)}

RESTRICCIONES ESPECÍFICAS POR SEXO Y EDAD:
- Si es MUJER: Enfatiza glúteos, piernas, core. Evita cargas muy pesadas al inicio. Incluye ejercicios para tonificación.
- Si es HOMBRE: Enfatiza pecho, espalda, brazos. Cargas más pesadas. Enfoque en masa muscular si aplica.
- Si edad > 50: Reducir impacto articular. Más énfasis en movilidad y postura.
- Si edad < 25: Puede ser más intenso. Enfoque en desarrollo y fuerza.

AJUSTA REPS POR OBJETIVO:
- Ganancia muscular: 6-12 reps con peso pesado
- Pérdida grasa: 12-15+ reps, tempo más rápido
- Tonificación: 10-15 reps, peso moderado
- Resistencia: 15-20 reps, poco descanso

FORMATO JSON REQUERIDO (EXACTO):
{{
  "Lunes": [
    {{
      "ejercicio": "Press de Banca",
      "series": 4,
      "reps_por_serie": ["12", "10", "8", "6"],
      "peso_lb_por_serie": [100, 110, 120, 130],
      "tip": "Consejo técnico para ESTE cliente específicamente",
      "razon": "Por qué es perfecto para {perfil_json.get('sexo')}, {perfil_json.get('edad')} años, objetivo: ..."
    }}
  ],
  "Martes": [...],
  "Miércoles": "Día de descanso: Estiramientos o yoga"
}}

OBLIGATORIO:
- Reps VARÍAN en cada serie (no repetir)
- Peso AUMENTA conforme bajan las reps (pirámide inversa)
- Mínimo 3-4 ejercicios por día
- Personalizar según SEXO y OBJETIVOS
- Respeta dias_entreno={perfil_json.get('dias_entreno')}

Solo retorna JSON válido. Sin markdown, sin explicaciones.
"""
        response = model.generate_content(prompt)
        respuesta_texto = response.text.strip()
        
        # Limpiar marcadores de código si existen
        if respuesta_texto.startswith("```json"):
            respuesta_texto = respuesta_texto[7:]
        if respuesta_texto.startswith("```"):
            respuesta_texto = respuesta_texto[3:]
        if respuesta_texto.endswith("```"):
            respuesta_texto = respuesta_texto[:-3]
        
        rutina_dict = json.loads(respuesta_texto.strip())
        return rutina_dict
    except Exception as e:
        st.error(f"Error generando rutina con IA: {str(e)}")
        return None

def generar_rutina_ia(u):
    """Genera rutina completamente personalizada por sexo, edad, objetivos y más"""
    objetivos = u.get('objetivos', [])
    peso_lb = u.get('peso_lb', 160)
    edad = u.get('edad', 25)
    sexo = u.get('sexo', 'Masculino')
    dias_e = u.get('dias_entreno', 5)
    
    # Preparar perfil para IA
    perfil = {
        "nombre": u.get('nombre', 'Usuario'),
        "sexo": sexo,
        "edad": edad,
        "peso_lb": peso_lb,
        "estatura_m": u.get('estatura_m', 1.70),
        "objetivos": objetivos[:3],
        "dias_entreno": dias_e
    }
    
    # Intentar con Gemini
    with st.spinner("🤖 IA generando rutina personalizada..."):
        rutina_ia = generar_rutina_gemini(json.dumps(perfil))
    
    if rutina_ia:
        return rutina_ia
    
    # FALLBACK LOCAL: Generar rutina ultra personalizada
    es_mujer = sexo == "Femenino"
    es_joven = edad < 25
    es_adulto = 25 <= edad < 50
    es_mayor = edad >= 50
    
    # Detectar objetivos
    es_intenso = any("masa" in obj.lower() or "fuerza" in obj.lower() for obj in objetivos)
    enfasis_gluteos = any("glúteo" in obj.lower() or "pierna" in obj.lower() for obj in objetivos)
    enfasis_cardio = any("grasa" in obj.lower() or "resistencia" in obj.lower() or "correr" in obj.lower() for obj in objetivos)
    enfasis_tonificacion = any("tonificar" in obj.lower() or "definir" in obj.lower() for obj in objetivos)
    
    # Determinar intensidad y volumen por edad
    if es_joven:
        series = 4 if es_intenso else 3
        reps = "6-10" if es_intenso else "10-15"
        descanso_base = "90-120s" if es_intenso else "60-90s"
    elif es_adulto:
        series = 3 if es_intenso else 3
        reps = "8-12" if es_intenso else "12-15"
        descanso_base = "60-90s" if es_intenso else "45-60s"
    else:  # es_mayor
        series = 2 if es_intenso else 2
        reps = "10-15" if es_intenso else "15-20"
        descanso_base = "60-90s"
    
    rutina = {}
    
    # DISTRIBUCIÓN PERSONALIZADA POR SEXO Y OBJETIVO
    if es_mujer:
        # Énfasis en glúteos, piernas, core para mujeres
        if dias_e == 3:
            distribucion = {
                "Lunes": "Piernas/Glúteos",
                "Miércoles": "Espalda/Core",
                "Viernes": "Glúteos/Cardio"
            }
        elif dias_e == 4:
            distribucion = {
                "Lunes": "Piernas/Glúteos",
                "Martes": "Espalda/Brazos",
                "Jueves": "Glúteos/Core",
                "Viernes": "Cardio/Funcional"
            }
        else:  # 5 días
            distribucion = {
                "Lunes": "Piernas/Glúteos",
                "Martes": "Espalda/Hombros",
                "Miércoles": "Descanso Activo",
                "Jueves": "Glúteos/Core",
                "Viernes": "Cardio/Brazos"
            }
    else:
        # Énfasis en pecho, espalda, brazos para hombres
        if dias_e == 3:
            distribucion = {
                "Lunes": "Pecho/Espalda/Hombros",
                "Miércoles": "Piernas/Core",
                "Viernes": "Full Body/Funcional"
            }
        elif dias_e == 4:
            distribucion = {
                "Lunes": "Pecho/Hombros",
                "Martes": "Piernas",
                "Jueves": "Espalda/Brazos",
                "Viernes": "Híbrido/Funcional"
            }
        else:  # 5 días
            distribucion = {
                "Lunes": "Pecho/Hombros",
                "Martes": "Piernas",
                "Miércoles": "Descanso Activo",
                "Jueves": "Espalda/Brazos",
                "Viernes": "Funcional/Core"
            }

    for dia, enfoque in distribucion.items():
        if "Descanso" in enfoque:
            if es_mayor:
                rutina[dia] = "Día de recuperación: Estiramientos suaves o yoga (15-20 min) + movilidad articular."
            else:
                rutina[dia] = "Día de recuperación: Estiramientos dinámicos o 30 min de caminata ligera."
            continue
            
        ejercicios_dia = []
        grupos = enfoque.split("/")
        for g in grupos:
            pool = []
            
            # Seleccionar grupo muscular
            if g == "Pecho": pool = EJERCICIOS_AVANZADOS["Pecho"]
            elif g == "Hombros": pool = EJERCICIOS_AVANZADOS["Hombros"]
            elif g == "Piernas": 
                # Para mujeres: más énfasis en piernas
                pool = EJERCICIOS_AVANZADOS["Piernas"]
            elif g == "Espalda": pool = EJERCICIOS_AVANZADOS["Espalda"]
            elif g == "Brazos": pool = EJERCICIOS_AVANZADOS["Brazos"]
            elif g == "Glúteos":
                # Ejercicios especiales para glúteos (mujeres)
                pool = [
                    {"nombre": "Hip Thrusts", "tip": "Máxima activación de glúteos con control."},
                    {"nombre": "Sentadillas Búlgara", "tip": "Unilateral: énfasis en glúteos y cuádriceps."},
                    {"nombre": "Peso Muerto Rumano", "tip": "Siente el estiramiento en glúteos e isquios."},
                    {"nombre": "Patada de Glúteos", "tip": "Cable o máquina: aislamiento de glúteos."},
                    {"nombre": "Prensa de Piernas (posición ancha)", "tip": "Enfoque en glúteos."}
                ]
            elif g in ["Funcional", "Híbrido", "Full Body"]:
                if enfasis_cardio:
                    pool = EJERCICIOS_AVANZADOS["Cardio/Funcional"]
                else:
                    pool = EJERCICIOS_AVANZADOS["Cardio/Funcional"]
            elif g == "Core": pool = EJERCICIOS_AVANZADOS["Core/Postura"]
            elif g == "Cardio": pool = EJERCICIOS_AVANZADOS["Cardio/Funcional"]
            
            if pool:
                num_ej = 2 if len(grupos) > 1 else 4
                seleccion = random.sample(pool, min(len(pool), num_ej))
                for s in seleccion:
                    detalles_sets = []
                    
                    # Ajustar peso base por sexo y edad
                    if es_mujer:
                        peso_multiplicador = 0.25 if es_joven else 0.20
                    else:
                        peso_multiplicador = 0.35 if es_joven else 0.30
                    
                    if es_mayor:
                        peso_multiplicador *= 0.8  # Reducir peso para mayor edad
                    
                    libras_base = round(peso_lb * peso_multiplicador, 0)
                    
                    # Generar reps y pesos variados
                    for set_idx in range(series):
                        # Reps según intensidad
                        if reps == "6-10":
                            reps_set = str(max(6, 10 - set_idx * 1))
                        elif reps == "8-12":
                            reps_set = str(max(8, 12 - set_idx * 2))
                        elif reps == "10-15":
                            reps_set = str(max(10, 15 - set_idx * 1))
                        elif reps == "12-15":
                            reps_set = str(max(10, 15 - set_idx * 1))
                        else:  # 15-20
                            reps_set = str(max(15, 20 - set_idx * 1))
                        
                        # Peso progresivo
                        factor_fatiga = 1.0 - (set_idx * 0.08)
                        libras_set = round(max(libras_base * factor_fatiga, 5), 0)
                        detalles_sets.append({"reps": reps_set, "libras": libras_set})

                    ejercicios_dia.append({
                        "ejercicio": s["nombre"], 
                        "series": series,
                        "detalles_sets": detalles_sets,
                        "tip": s["tip"]
                    })
        rutina[dia] = ejercicios_dia
    return rutina

# --- FUNCIONES AVANZADAS ---

def obtener_ejercicios_alternativos(ejercicio, musculo_objetivo):
    """Genera ejercicios alternativos usando IA con fallback local"""
    # Primero, encontrar el músculo objetivo del ejercicio
    musculo_encontrado = None
    for musculo, ejercicios_lista in EJERCICIOS_AVANZADOS.items():
        for ej in ejercicios_lista:
            if ej["nombre"].lower() == ejercicio.lower():
                musculo_encontrado = musculo
                break
        if musculo_encontrado:
            break
    
    # Si no lo encontramos, intentar con Gemini
    if not musculo_encontrado:
        musculo_encontrado = "músculos objetivo"
    
    try:
        prompt = f"""
Eres un experto en entrenamiento físico certificado. 

El usuario está haciendo: {ejercicio}
Grupo muscular: {musculo_encontrado}

Dame EXACTAMENTE 3 ejercicios alternativos que trabajen el MISMO grupo muscular.

IMPORTANTE: Devuelve SOLO JSON válido, sin explicaciones adicionales:

{{
  "alternativas": [
    {{"nombre": "Nombre Ejercicio 1", "razon": "Breve razón por qué es buen sustituto"}},
    {{"nombre": "Nombre Ejercicio 2", "razon": "Breve razón por qué es buen sustituto"}},
    {{"nombre": "Nombre Ejercicio 3", "razon": "Breve razón por qué es buen sustituto"}}
  ]
}}
"""
        response = model.generate_content(prompt)
        texto = response.text.strip()
        
        # Limpiar markdown
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0]
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0]
        
        resultado = json.loads(texto.strip())
        
        if resultado.get("alternativas") and len(resultado["alternativas"]) > 0:
            return resultado
    except Exception as e:
        pass
    
    # Fallback: generar alternativas locales
    if musculo_encontrado and musculo_encontrado in EJERCICIOS_AVANZADOS:
        ejercicios_disponibles = [e["nombre"] for e in EJERCICIOS_AVANZADOS[musculo_encontrado] if e["nombre"].lower() != ejercicio.lower()]
        alternativas = []
        for ej in ejercicios_disponibles[:3]:
            alternativas.append({
                "nombre": ej,
                "razon": f"Excelente alternativa para {musculo_encontrado}"
            })
        
        if alternativas:
            return {"alternativas": alternativas}
    
    return {"alternativas": []}

def generar_warmup(dia_entreno, ejercicios_dia):
    """Genera warmup personalizado para el día"""
    try:
        ejercicios_str = ", ".join([e.get('ejercicio', '') for e in (ejercicios_dia if isinstance(ejercicios_dia, list) else [])])
        prompt = f"""
Eres entrenador certificado. Genera un warmup de 10 minutos para {dia_entreno} con estos ejercicios: {ejercicios_str}.

Formato JSON:
{{
  "warmup": [
    {{"actividad": "Descripción", "duracion_min": 2}},
    {{"actividad": "Descripción", "duracion_min": 3}},
    {{"actividad": "Descripción", "duracion_min": 5}}
  ]
}}

Solo JSON válido.
"""
        response = model.generate_content(prompt)
        texto = response.text.strip()
        if "```" in texto:
            texto = texto.replace("```json", "").replace("```", "")
        return json.loads(texto.strip())
    except:
        return {"warmup": [{"actividad": "Cardio ligero", "duracion_min": 5}, {"actividad": "Movilidad articular", "duracion_min": 5}]}

def calcular_tiempo_descanso(objetivo, reps):
    """Calcula tiempo de descanso sugerido"""
    tiempos = {
        "hipertrofia": {"6-8": "90-120s", "8-12": "60-90s", "12-15": "45-60s"},
        "fuerza": {"1-5": "120-180s", "5-8": "90-120s"},
        "resistencia": {"15-20": "30-45s"},
        "tonificacion": {"10-15": "45-60s"}
    }
    
    if objetivo == "Ganancia muscular":
        objetivo = "hipertrofia"
    elif objetivo == "Pérdida grasa":
        objetivo = "resistencia"
    elif objetivo == "Tonificación":
        objetivo = "tonificacion"
    else:
        objetivo = "hipertrofia"
    
    try:
        for rango, tiempo in tiempos.get(objetivo, {}).items():
            return tiempo
    except:
        return "60s"

def registrar_entrenamiento(dia, ejercicios_completados):
    """Registra un entrenamiento completo"""
    from datetime import datetime
    entrenamiento = {
        "fecha": str(datetime.now().date()),
        "hora": str(datetime.now().time())[0:5],
        "dia": dia,
        "ejercicios": ejercicios_completados,
        "duracion_min": 0
    }
    return entrenamiento

def calcular_progreso_ejercicio(ejercicio_nombre, historial):
    """Calcula progreso en un ejercicio específico"""
    registros = [e for entrenamientos in historial 
                 for e in entrenamientos.get('ejercicios', []) 
                 if e.get('nombre') == ejercicio_nombre]
    
    if len(registros) < 2:
        return {"tendencia": "sin datos", "mejora": 0}
    
    primer_peso = registros[0].get('peso_levantado', 0)
    ultimo_peso = registros[-1].get('peso_levantado', 0)
    mejora = ultimo_peso - primer_peso
    
    return {
        "tendencia": "↑" if mejora > 0 else ("↓" if mejora < 0 else "→"),
        "mejora": mejora,
        "registros_totales": len(registros)
    }

def detectar_meseta_y_rotar_rutina(historial_entrenamientos, fecha_ultima_rotacion, dias_entrenamientos):
    """Detecta si hay meseta y genera nueva rutina"""
    from datetime import datetime, timedelta
    
    if not fecha_ultima_rotacion:
        return False, "Nueva rutina"
    
    dias_desde_rotacion = (datetime.now().date() - datetime.fromisoformat(fecha_ultima_rotacion).date()).days
    
    # Si pasó 4 semanas sin mejoría, rotar
    if dias_desde_rotacion >= 28:
        return True, "⚠️ Meseta detectada. Nueva rutina generada."
    
    return False, ""

def recomendaciones_ia(progreso_data, user_profile):
    """Genera recomendaciones inteligentes basadas en progreso"""
    try:
        prompt = f"""
Eres entrenador certificado. Basado en este progreso:
{json.dumps(progreso_data, ensure_ascii=False)}

Perfil: {user_profile.get('sexo')}, {user_profile.get('edad')} años, objetivo: {user_profile.get('objetivos', [''])[0]}

Dame 3 recomendaciones ESPECÍFICAS para mejorar (máx 50 palabras cada una):

Formato JSON:
{{
  "recomendaciones": [
    {{"titulo": "Recomendación 1", "descripcion": "..."}},
    {{"titulo": "Recomendación 2", "descripcion": "..."}},
    {{"titulo": "Recomendación 3", "descripcion": "..."}}
  ]
}}

Solo JSON válido.
"""
        response = model.generate_content(prompt)
        texto = response.text.strip()
        if "```" in texto:
            texto = texto.replace("```json", "").replace("```", "")
        return json.loads(texto.strip())
    except:
        return {"recomendaciones": []}

def obtener_musculos_del_dia(ejercicios_dia):
    """Extrae los grupos musculares trabajados en un día"""
    # Crear mapeo de ejercicios a músculos
    mapeo_ejercicios = {}
    for musculo, ejercicios_lista in EJERCICIOS_AVANZADOS.items():
        for ej in ejercicios_lista:
            mapeo_ejercicios[ej["nombre"].lower()] = musculo
    
    musculos_unicos = set()
    if isinstance(ejercicios_dia, list):
        for ej in ejercicios_dia:
            nombre = ej.get("ejercicio", "").lower()
            musculo = mapeo_ejercicios.get(nombre, "Otros")
            musculos_unicos.add(musculo)
    
    return sorted(list(musculos_unicos))

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
                        # ⚠️ RENDIMIENTO: Evitar rerun innecesario, usar navegación natural
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
            peso = c_p.number_input("Peso (Lbs)", PESO_MIN, PESO_MAX, 160.0)
            pies = c_ft.number_input("Pies", 3, 8, 5)
            pulgadas = c_in.number_input("Pulg", 0, 11, 7)
            edad = c_ed.number_input("Edad", EDAD_MIN, EDAD_MAX, 25)
            
            st.markdown("**💪 Entrenamiento**")
            c_d, c_o = st.columns([1, 2])
            dias_e = c_d.selectbox("Días/Semana", DIAS_ENTRENO_OPCIONES, index=2)
            objs = c_o.multiselect("🎯 Tus metas:", LISTA_OBJETIVOS, max_selections=MAX_OBJECTIVES)
            
            signup_btn = st.form_submit_button("✅ Crear Cuenta", use_container_width=True)
            
            if signup_btn:
                if not signup_user or not signup_pass:
                    st.error("❌ Usuario y contraseña son requeridos")
                elif len(signup_pass) < MIN_PASSWORD_LENGTH:
                    st.error(f"❌ La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")
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
        asegurar_datos_frescos()
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


