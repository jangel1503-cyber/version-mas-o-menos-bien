import json
import random
from datetime import datetime

import pandas as pd
from gym_app.repositories import cargar_json, guardar_json

DB_FILE = "gym_data.json"
USERS_FILE = "user_data.json"


def _estructura_base(user_data=None, perfil_completado=False):
    return {
        "perfil_completado": perfil_completado,
        "user": user_data if user_data is not None else {"dias_entreno": 5},
        "rutina_semanal": {},
        "historial_pesos": [],
        "historial_entrenamientos": [],
        "pr_por_ejercicio": {},
        "fecha_ultima_rotacion": None,
        "dieta_semanal": {},
    }


def _normalizar_perfil(perfil_json):
    if isinstance(perfil_json, str):
        try:
            return json.loads(perfil_json)
        except Exception:
            return {}
    return perfil_json if isinstance(perfil_json, dict) else {}


# --- GESTIÓN DE USUARIOS ---
def cargar_usuarios():
    """Carga la base de datos de usuarios desde user_data.json"""
    return cargar_json(USERS_FILE, {})

def guardar_usuarios(usuarios):
    """Guarda la base de datos de usuarios en user_data.json"""
    guardar_json(USERS_FILE, usuarios)

def usuario_existe(username):
    """Verifica si un usuario ya existe"""
    usuarios = cargar_usuarios()
    return username.lower() in usuarios

def validar_credenciales(username, password):
    """Valida el nombre de usuario y contraseña"""
    usuarios = cargar_usuarios()
    user_lower = username.lower()
    if user_lower in usuarios:
        return usuarios[user_lower].get("password") == password
    return False

def registrar_usuario(username, password, datos_perfil):
    """Registra un nuevo usuario con sus datos de perfil"""
    usuarios = cargar_usuarios()
    usuario_lower = username.lower()
    
    if usuario_lower in usuarios:
        return False, "El usuario ya existe"
    
    usuarios[usuario_lower] = {
        "username": username,
        "password": password,
        "datos_perfil": datos_perfil,
        "fecha_registro": str(pd.Timestamp.now())
    }
    guardar_usuarios(usuarios)
    
    # IMPORTANTE: Guardar estructura inicial en gym_data.json
    todo_datos = cargar_json(DB_FILE, {})
    
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
    guardar_json(DB_FILE, todo_datos)
    
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



# --- LISTA MAESTRA DE OBJETIVOS (PROTEGIDA) ---
LISTA_OBJETIVOS = [
    "🏋️ Ganar masa muscular (hipertrofia)",
    "🏋️ Perder grasa corporal",
    "🏋️ Aumentar fuerza (ej. mejorar en ejercicios clave)",
    "🏋️ Mejorar resistencia cardiovascular",
    "🏋️ Tonificar el cuerpo",
    "🏋️ Mejorar la movilidad y flexibilidad",
    "❤️ Reducir el estrés",
    "❤️ Dormir mejor",
    "❤️ Mejorar la salud cardiovascular",
    "❤️ Prevenir lesiones o dolores",
    "❤️ Aumentar niveles de energía diarios",
    "⚡ Correr más rápido o más distancia",
    "⚡ Saltar más alto o mejorar potencia",
    "⚡ Prepararse para un deporte específico",
    "⚡ Mejorar coordinación y equilibrio",
    "🎯 Marcar abdomen",
    "🎯 Aumentar glúteos o piernas",
    "🎯 Definir brazos y hombros",
    "🎯 Mejorar postura corporal",
    "🧠 Crear una rutina constante",
    "🧠 Aprender técnica correcta de ejercicios",
    "🧠 Mantener consistencia a largo plazo",
    "🧠 Desarrollar disciplina y autocontrol",
    "📊 Bajar peso en tiempo específico",
    "📊 Levantar cierto peso en ejercicios clave",
    "📊 Reducir porcentaje de grasa corporal",
    "📊 Completar metas de cardio"
]

# --- PERSISTENCIA ---
def guardar_todo(datos, usuario=None):
    """Guarda datos de usuario en gym_data.json."""
    usuario = usuario if usuario else "default"
    todos_datos = cargar_json(DB_FILE, {})
    
    # Guardar datos del usuario especifico
    todos_datos[usuario] = datos
    guardar_json(DB_FILE, todos_datos)

def cargar_todo(usuario=None):
    """Carga datos del usuario desde gym_data.json."""
    usuario = usuario if usuario else "default"
    
    estructura_vacia = _estructura_base()
    
    todos_datos = cargar_json(DB_FILE, {})
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
        perfil = _normalizar_perfil(perfil_json)
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
    except Exception:
        return None

# --- GENERADOR DE DIETA IA ---
def generar_dieta_semanal(perfil_json, model):
    """Consulta a Gemini o usa fallback local"""
    perfil = _normalizar_perfil(perfil_json)
    try:
        model.generate_content("test")  # Test para verificar disponibilidad
        # Si llegamos aquí, la API funciona, intentar generar completo
        prompt = f"""
ERES UN NUTRICIONISTA CERTIFICADO CON 15+ AÑOS DE EXPERIENCIA EN DIETAS PERSONALIZADAS.

GENERA UN PLAN DE COMIDAS SEMANAL ULTRA PERSONALIZADO (Lunes a Domingo) CON ALIMENTOS REALES Y ESPECÍFICOS.

PERFIL DEL CLIENTE:
{json.dumps(perfil, indent=2, ensure_ascii=False)}

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
    except Exception:
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

def generar_rutina_gemini(perfil_json, model):
    """Consulta a Gemini para generar rutina personalizada"""
    perfil = _normalizar_perfil(perfil_json)
    try:
        prompt = f"""
IMPORTANTE: Eres un entrenador personal certificado con 20+ años. Genera una rutina ULTRA PERSONALIZADA.

PERFIL DEL CLIENTE (CRÍTICO):
{json.dumps(perfil, indent=2, ensure_ascii=False)}

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
    "razon": "Por qué es perfecto para {perfil.get('sexo')}, {perfil.get('edad')} años, objetivo: ..."
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
- Respeta dias_entreno={perfil.get('dias_entreno')}

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
    except Exception:
        return None

def generar_rutina_ia(u, model):
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
    rutina_ia = generar_rutina_gemini(json.dumps(perfil), model)
    
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

def obtener_ejercicios_alternativos(ejercicio, musculo_objetivo, model):
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
    except Exception:
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

def generar_warmup(dia_entreno, ejercicios_dia, model):
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

    if not fecha_ultima_rotacion:
        return False, "Nueva rutina"

    try:
        dias_desde_rotacion = (datetime.now().date() - datetime.fromisoformat(fecha_ultima_rotacion).date()).days
    except Exception:
        return False, ""
    
    # Si pasó 4 semanas sin mejoría, rotar
    if dias_desde_rotacion >= 28:
        return True, "⚠️ Meseta detectada. Nueva rutina generada."
    
    return False, ""

def recomendaciones_ia(progreso_data, user_profile, model):
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

