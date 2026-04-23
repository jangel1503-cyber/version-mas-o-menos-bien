# config.py - Configuraciones y constantes para Gym Pro AI

import os

# Archivos de datos
DB_FILE = "gym_data.json"
USERS_FILE = "user_data.json"

# Configuración de seguridad
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "gym_pro_salt_2024")

# Configuración de IA
GEMINI_MODEL = "gemini-2.0-flash"

# Límites y validaciones
MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 6
MAX_OBJECTIVES = 5

# Constantes de nutrición
CALORIAS_POR_G_PROTEINA = 4
CALORIAS_POR_G_CARBO = 4
CALORIAS_POR_G_GRASA = 9

# Constantes de entrenamiento
DIAS_ENTRENO_OPCIONES = [3, 4, 5]
PESO_MIN = 50.0
PESO_MAX = 500.0
EDAD_MIN = 12
EDAD_MAX = 100

# Configuración de UI
PAGE_CONFIG = {
    "page_title": "Gym Pro AI",
    "page_icon": "💪",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Lista de objetivos (protegida)
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