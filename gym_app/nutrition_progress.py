"""
Module for nutrition and progress tracking operations
"""
import json
from datetime import datetime
from gym_app.services import calcular_macros, COMIDAS_DB, cargar_todo
import random


def obtener_alternativas_comida_categoria(categoria):
    """Get alternative foods for a specific category"""
    if categoria in COMIDAS_DB:
        return COMIDAS_DB[categoria].get("general", [])
    return []


def calcular_macros_comida(alimento, cantidad_g=100):
    """Calculate macros for a specific food item (stub - returns estimated values)"""
    # Estimated macro values per 100g for common foods
    macros_db = {
        "pechuga de pollo": {"proteina": 31, "carbos": 0, "grasas": 3.6},
        "salmón": {"proteina": 25, "carbos": 0, "grasas": 13},
        "huevo": {"proteina": 13, "carbos": 1.1, "grasas": 11},
        "arroz integral": {"proteina": 2.6, "carbos": 23, "grasas": 0.9},
        "papa blanca": {"proteina": 2, "carbos": 17, "grasas": 0.1},
        "brócoli": {"proteina": 2.8, "carbos": 7, "grasas": 0.4},
        "atún": {"proteina": 29, "carbos": 0, "grasas": 0.5},
    }
    
    alimento_lower = alimento.lower()
    macros = macros_db.get(alimento_lower, {"proteina": 10, "carbos": 15, "grasas": 5})
    
    factor = cantidad_g / 100
    return {
        "alimento": alimento,
        "cantidad_g": cantidad_g,
        "proteina_g": round(macros["proteina"] * factor, 1),
        "carbos_g": round(macros["carbos"] * factor, 1),
        "grasas_g": round(macros["grasas"] * factor, 1),
        "calorias": round((macros["proteina"] * 4 + macros["carbos"] * 4 + macros["grasas"] * 9) * factor, 1)
    }


def generar_opciones_comida_alternativa(categoria, cantidad=3):
    """Generate alternative meal options for a category"""
    opciones = obtener_alternativas_comida_categoria(categoria)
    if opciones:
        return random.sample(opciones, min(cantidad, len(opciones)))
    return []


def crear_registro_entrenamiento(dia, ejercicios_completados, usuario=None):
    """Create a training session record"""
    registro = {
        "fecha": str(datetime.now()),
        "dia": dia,
        "ejercicios": ejercicios_completados,
        "duracion_minutos": 0,
        "notas": ""
    }
    
    # Save to user data if needed
    if usuario:
        datos = cargar_todo(usuario)
        if "historial_entrenamientos" not in datos:
            datos["historial_entrenamientos"] = []
        datos["historial_entrenamientos"].append(registro)
        from gym_app.services import guardar_todo
        guardar_todo(datos, usuario)
    
    return registro


def calcular_progreso_ejercicio(nombre_ejercicio, historial):
    """Calculate progress for a specific exercise based on history"""
    if not historial or not isinstance(historial, list):
        return {"mejora": 0, "tendencia": "estable", "reps_inicio": 0, "reps_actual": 0}
    
    ejercicio_registros = [
        h for h in historial 
        if isinstance(h, dict) and h.get("ejercicio", "").lower() == nombre_ejercicio.lower()
    ]
    
    if len(ejercicio_registros) < 2:
        return {"mejora": 0, "tendencia": "insuficientes datos", "reps_inicio": 0, "reps_actual": 0}
    
    reps_inicio = ejercicio_registros[0].get("reps", 0)
    reps_actual = ejercicio_registros[-1].get("reps", 0)
    mejora = reps_actual - reps_inicio
    
    tendencia = "mejora" if mejora > 0 else ("declive" if mejora < 0 else "estable")
    
    return {
        "mejora": mejora,
        "tendencia": tendencia,
        "reps_inicio": reps_inicio,
        "reps_actual": reps_actual,
        "porcentaje_mejora": round((mejora / reps_inicio * 100) if reps_inicio > 0 else 0, 1)
    }


def generar_analisis_progreso(historial_entrenamientos, objetivos):
    """Generate overall progress analysis"""
    if not historial_entrenamientos:
        return {
            "consistencia": 0,
            "ejercicios_completados": 0,
            "tendencia": "sin datos",
            "recomendaciones": ["Comienza a registrar tus entrenamientos"]
        }
    
    total_sesiones = len(historial_entrenamientos)
    ejercicios_unicos = set()
    
    for sesion in historial_entrenamientos:
        if isinstance(sesion, dict) and "ejercicios" in sesion:
            for ej in sesion.get("ejercicios", []):
                if isinstance(ej, dict):
                    ejercicios_unicos.add(ej.get("ejercicio", ""))
    
    recomendaciones = []
    if total_sesiones < 5:
        recomendaciones.append("Realiza más sesiones para tener datos de progreso")
    if "ganar masa" in str(objetivos).lower():
        recomendaciones.append("Incrementa el peso progresivamente en los ejercicios")
    if "perder grasa" in str(objetivos).lower():
        recomendaciones.append("Mantén consistencia en el cardio y cuidado nutricional")
    
    return {
        "sesiones_registradas": total_sesiones,
        "ejercicios_unicos": len(ejercicios_unicos),
        "tendencia": "en progreso",
        "recomendaciones": recomendaciones
    }


def calcular_consistencia(historial_entrenamientos, dias_entrenamiento_objetivo):
    """Calculate training consistency percentage"""
    if not historial_entrenamientos or dias_entrenamiento_objetivo == 0:
        return 0
    
    # Get unique dates from historial
    fechas_unicas = set()
    for sesion in historial_entrenamientos:
        if isinstance(sesion, dict) and "fecha" in sesion:
            fecha = sesion["fecha"][:10]  # Extract date part
            fechas_unicas.add(fecha)
    
    # This is a simple approximation
    # In a real scenario, you'd calculate against expected days
    consistencia = min(100, (len(fechas_unicas) / dias_entrenamiento_objetivo * 100)) if dias_entrenamiento_objetivo > 0 else 0
    
    return round(consistencia, 1)
