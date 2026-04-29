"""
Module for exercise database and related operations
"""
import random
from gym_app.services import EJERCICIOS_AVANZADOS

# Create exercise database from available exercises
EJERCICIOS_COMPLETOS = {}
for musculo, ejercicios in EJERCICIOS_AVANZADOS.items():
    for ej in ejercicios:
        EJERCICIOS_COMPLETOS[ej["nombre"].lower()] = {
            "nombre": ej["nombre"],
            "musculo": musculo,
            "tip": ej.get("tip", "")
        }

# Create exercises by muscle group mapping
EJERCICIOS_POR_MUSCULO = EJERCICIOS_AVANZADOS.copy()


def obtener_descripcion_ejercicio(nombre_ejercicio):
    """Get description and tips for a specific exercise"""
    nombre_lower = nombre_ejercicio.lower()
    if nombre_lower in EJERCICIOS_COMPLETOS:
        return EJERCICIOS_COMPLETOS[nombre_lower]
    return {"nombre": nombre_ejercicio, "musculo": "Desconocido", "tip": "Ejercicio no encontrado en la base de datos"}


def obtener_alternativas_ejercicio(ejercicio, musculo_objetivo):
    """Get alternative exercises for a given muscle group"""
    alternativas = []
    if musculo_objetivo in EJERCICIOS_POR_MUSCULO:
        ejercicios = EJERCICIOS_POR_MUSCULO[musculo_objetivo]
        alternativas = [
            ej["nombre"] for ej in ejercicios 
            if ej["nombre"].lower() != ejercicio.lower()
        ]
    return alternativas


def obtener_ejercicios_por_musculo(musculo):
    """Get all exercises for a specific muscle group"""
    if musculo in EJERCICIOS_POR_MUSCULO:
        return [ej["nombre"] for ej in EJERCICIOS_POR_MUSCULO[musculo]]
    return []


def validar_ejercicio(nombre_ejercicio):
    """Validate if an exercise exists in the database"""
    return nombre_ejercicio.lower() in EJERCICIOS_COMPLETOS
