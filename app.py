import streamlit as st
import json
import os
import random
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gym Pro AI", page_icon="💪", layout="wide")
DB_FILE = "gym_data.json"

# Cargar API key desde secrets (Streamlit Cloud) o variable local
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')



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
def guardar_todo(datos):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def cargar_todo():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                # Asegurar compatibilidad
                if "historial_pesos" not in data:
                    data["historial_pesos"] = []
                if "user" in data and "dias_entreno" not in data["user"]:
                    data["user"]["dias_entreno"] = 5
                if "historial_entrenamientos" not in data:
                    data["historial_entrenamientos"] = []
                if "pr_por_ejercicio" not in data:  # Personal Records
                    data["pr_por_ejercicio"] = {}
                if "fecha_ultima_rotacion" not in data:
                    data["fecha_ultima_rotacion"] = None
                return data
        except: pass
    return {
        "perfil_completado": False, 
        "user": {"dias_entreno": 5}, 
        "rutina_semanal": {}, 
        "historial_pesos": [],
        "historial_entrenamientos": [],
        "pr_por_ejercicio": {},
        "fecha_ultima_rotacion": None
    }

if 'data' not in st.session_state:
    st.session_state.data = cargar_todo()

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

@st.cache_data
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
    """Genera rutina usando Gemini o fallback local"""
    objetivos = u.get('objetivos', [])
    peso_lb = u.get('peso_lb', 160)
    edad = u.get('edad', 25)
    sexo = u.get('sexo', 'Masculino')
    dias_e = u.get('dias_entreno', 5)
    
    # Preparar perfil para IA
    perfil = {
        "nombre": u.get('nombre'),
        "sexo": sexo,
        "edad": edad,
        "peso_lb": peso_lb,
        "estatura_m": u.get('estatura_m', 1.70),
        "objetivos": objetivos[:3],  # Top 3 objetivos
        "dias_entreno": dias_e
    }
    
    # Intentar con Gemini
    with st.spinner("🤖 IA generando rutina personalizada..."):
        rutina_ia = generar_rutina_gemini(json.dumps(perfil))
    
    if rutina_ia:
        return rutina_ia
    
    # Fallback: Generar localmente si IA falla
    es_intenso = any("masa" in obj.lower() or "fuerza" in obj.lower() or "glúteos" in obj.lower() for obj in objetivos)
    enfasis_cardio = any("grasa" in obj.lower() or "resistencia" in obj.lower() or "correr" in obj.lower() for obj in objetivos)
    
    series = 4 if es_intenso and edad < 45 else 3
    reps = "8-12" if es_intenso else "12-15"
    if edad > 55: reps = "15-20"

    rutina = {}
    dias_e = u.get('dias_entreno', 5)
    
    # Distribuir por días (fallback)
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
    else: # 5 Días
        distribucion = {
            "Lunes": "Pecho/Hombros",
            "Martes": "Piernas",
            "Miércoles": "Descanso Activo",
            "Jueves": "Espalda/Brazos",
            "Viernes": "Funcional/Core"
        }

    for dia, enfoque in distribucion.items():
        if "Descanso" in enfoque:
            rutina[dia] = "Día de recuperación: Estiramientos dinámicos o 30 min de caminata ligera."
            continue
            
        ejercicios_dia = []
        grupos = enfoque.split("/")
        for g in grupos:
            pool = []
            if g == "Pecho": pool = EJERCICIOS_AVANZADOS["Pecho"]
            elif g == "Hombros": pool = EJERCICIOS_AVANZADOS["Hombros"]
            elif g == "Piernas": pool = EJERCICIOS_AVANZADOS["Piernas"]
            elif g == "Espalda": pool = EJERCICIOS_AVANZADOS["Espalda"]
            elif g == "Brazos": pool = EJERCICIOS_AVANZADOS["Brazos"]
            elif g in ["Funcional", "Híbrido", "Full Body"]: pool = EJERCICIOS_AVANZADOS["Cardio/Funcional"]
            elif g == "Core": pool = EJERCICIOS_AVANZADOS["Core/Postura"]
            
            if pool:
                num_ej = 2 if len(grupos) > 1 else 4
                seleccion = random.sample(pool, min(len(pool), num_ej))
                for s in seleccion:
                    detalles_sets = []
                    libras_base = round(peso_lb * random.uniform(0.20, 0.40), 0)
                    
                    # Generar reps y pesos variados realísticamente
                    for set_idx in range(series):
                        # Reps bajan conforme suben las series (pirámide inversa)
                        if reps == "8-12":  # Hipertrofia
                            reps_set = str(max(6, 12 - set_idx * 2))  # 12, 10, 8, 6
                        elif reps == "12-15":  # Tonificación
                            reps_set = str(max(10, 15 - set_idx * 1))  # 15, 14, 13, 12
                        else:  # Resistencia 15-20
                            reps_set = str(max(15, 20 - set_idx * 1))  # 20, 19, 18, 17
                        
                        # Peso aumenta conforme bajan reps (pirámide inversa)
                        factor_fatiga = 1.0 - (set_idx * 0.08)  # ~8% menos por cada set
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
if not st.session_state.data.get("perfil_completado", False):
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
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h2 style="margin:0;">💪 Gym Pro AI</h2>
                <p style="color: grey;">Tu Entrenador Personal Inteligente</p>
            </div>
            <hr style="margin: 10px 0; border: 0.1px solid rgba(255,255,255,0.1);">
            <p class="sidebar-label">Perfil de Usuario</p>
            <h3>👤 {u.get('nombre')}</h3>            <p>⚧️ Sexo: {u.get('sexo', 'N/A')}</p>            <p>🎂 Edad: {u.get('edad', 'N/A')} años</p>
            <p>🎯 {u.get('objetivos')[0] if u.get('objetivos') else 'Sin objetivos'}</p>
        """, unsafe_allow_html=True)
        st.info(f"📍 Meta: {len(u.get('objetivos', []))} objetivos seleccionados.")
        
        if not st.session_state.get('confirmar_reinicio', False):
            if st.button("⚠️ Reiniciar App", use_container_width=True):
                st.session_state.confirmar_reinicio = True
                st.rerun()
        else:
            st.warning("¿Estás seguro?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Sí", use_container_width=True):
                st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}, "historial_pesos": [], "historial_entrenamientos": [], "pr_por_ejercicio": {}, "fecha_ultima_rotacion": None}
                st.session_state.confirmar_reinicio = False
                guardar_todo(st.session_state.data)
                st.rerun()
            if c2.button("❌ No", use_container_width=True):
                st.session_state.confirmar_reinicio = False
                st.rerun()

    # --- DASHBOARD PRINCIPAL ---
    st.markdown(f'<h1 class="main-header">Panel de Control: {u.get("nombre")}</h1>', unsafe_allow_html=True)
    
    # Métrica de Salud Siempre Visible
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("IMC Actual", imc, help="Índice de Masa Corporal")
    with c2:
        st.metric("Estado Físico", estado)
    with c3:
        st.metric("Peso Ideal (Lbs)", f"{p_min} - {p_max}")

    t_rutina, t_entrenamiento, t_progreso, t_alternativas, t_recomendaciones, t_perfil = st.tabs(
        ["📅 Mi Rutina", "💪 Entrenar Hoy", "📈 Progreso", "🔄 Alternativas", "🤖 Recomendaciones", "👤 Perfil"]
    )

    with t_rutina:
        st.markdown("### 🏋️ Tu Plan de Entrenamiento Personalizado")
        
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
            
            # Entrenamientos
            if isinstance(ejercicios_hoy, list):
                ejercicios_registrados = []
                for idx, ej in enumerate(ejercicios_hoy):
                    with st.expander(f"🏋️ {ej['ejercicio']}", expanded=(idx == 0)):
                        st.info(f"💡 {ej.get('tip', '')}")
                        
                        # Mostrar plan
                        for s_idx, detalle in enumerate(ej.get('detalles_sets', [])):
                            col1, col2, col3, col4 = st.columns(4)
                            col1.write(f"**Set {s_idx+1}**")
                            col2.write(f"🔢 {detalle['reps']} reps")
                            col3.write(f"⚖️ {detalle['libras']} lbs")
                            col4.write(f"⏱️ {calcular_tiempo_descanso(u.get('objetivos', [''])[0] if u.get('objetivos') else 'hipertrofia', detalle['reps'])}")
                        
                        # Registrar resultado
                        with st.form(f"form_ejer_{idx}"):
                            reps_real = st.number_input(f"Reps completadas", 0, 100, key=f"reps_{idx}")
                            peso_real = st.number_input(f"Peso levantado (lbs)", 0.0, 1000.0, key=f"peso_{idx}")
                            notas = st.text_area(f"Notas", key=f"notas_{idx}")
                            
                            if st.form_submit_button(f"✅ Completado {ej['ejercicio']}", key=f"submit_{idx}"):
                                ejercicios_registrados.append({
                                    "nombre": ej['ejercicio'],
                                    "reps_completadas": reps_real,
                                    "peso_levantado": peso_real,
                                    "notas": notas
                                })
                                st.success("✅ Registrado!")
                
                # Botón para guardar todo el entrenamiento
                if st.button("💾 Guardar Entrenamiento Completo", key="save_all_training"):
                    entrenamiento = registrar_entrenamiento(dia_hoy, ejercicios_registrados)
                    st.session_state.data["historial_entrenamientos"].append(entrenamiento)
                    guardar_todo(st.session_state.data)
                    st.success("¡Entrenamiento guardado!")
                    st.balloons()
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
                n_p = st.number_input("Peso de hoy (Lbs)", 50.0, 500.0, float(u.get('peso_lb')))
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
                    st.dataframe(entrenamientos_df[['fecha', 'dia', 'duracion_min']], use_container_width=True)
            else:
                st.info("Aún no has registrado entrenamientos.")

    with t_perfil:
        st.markdown("### ⚙️ Configuración de Perfil")
        with st.form("edit_perfil"):
            st.markdown("#### 👤 Información Personal")
            n_nombre = st.text_input("Nombre", u.get('nombre'))
            n_sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if u.get('sexo') == 'Masculino' else 1)
            
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
                
                guardar_todo(st.session_state.data)
                st.success("¡Perfil y rutina actualizados con éxito!")
                st.rerun()

        st.markdown("---")
        if st.button("🔄 Regenerar Rutina Inteligente", help="Crea una nueva rutina basada en tus objetivos actuales"):
            st.session_state.data["rutina_semanal"] = generar_rutina_ia(u)
            guardar_todo(st.session_state.data)
            st.success("¡Nueva rutina generada con IA!")
            st.rerun()


