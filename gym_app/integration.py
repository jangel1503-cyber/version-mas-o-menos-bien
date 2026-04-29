"""
Module for integrated operations between exercises, nutrition, and other systems
"""
from gym_app.exercises_db import (
    obtener_descripcion_ejercicio,
    obtener_alternativas_ejercicio,
    obtener_ejercicios_por_musculo,
    EJERCICIOS_POR_MUSCULO
)
from gym_app.nutrition_progress import (
    obtener_alternativas_comida_categoria,
    calcular_macros_comida,
    generar_opciones_comida_alternativa
)


def obtener_ejercicio_info(nombre_ejercicio):
    """Get comprehensive information about an exercise"""
    descripcion = obtener_descripcion_ejercicio(nombre_ejercicio)
    musculo = descripcion.get("musculo", "Desconocido")
    
    alternativas = obtener_alternativas_ejercicio(nombre_ejercicio, musculo)
    
    return {
        "ejercicio": nombre_ejercicio,
        "descripcion": descripcion,
        "musculo_principal": musculo,
        "alternativas": alternativas,
        "tips": descripcion.get("tip", "")
    }


def obtener_ejercicios_categoria(categoria):
    """Get all exercises in a muscle category"""
    if categoria in EJERCICIOS_POR_MUSCULO:
        ejercicios = EJERCICIOS_POR_MUSCULO[categoria]
        return [
            {
                "nombre": ej["nombre"],
                "tip": ej.get("tip", ""),
                "musculo": categoria
            }
            for ej in ejercicios
        ]
    return []


def obtener_alternativas_comida(categoria, cantidad=3):
    """Get alternative food options for a meal category"""
    alternativas = generar_opciones_comida_alternativa(categoria, cantidad)
    
    resultado = []
    for comida in alternativas:
        macros = calcular_macros_comida(comida, 100)
        resultado.append({
            "alimento": comida,
            "macros": macros,
            "categoria": categoria
        })
    
    return resultado
