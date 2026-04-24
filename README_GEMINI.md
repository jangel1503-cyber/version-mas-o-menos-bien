# 🤖 Gym Pro AI - Integración con Google Gemini

## ¿Qué cambió?

Tu app ahora genera **rutinas de entrenamiento personalizadas usando IA (Google Gemini)** en lugar de solo usar un algoritmo local.

## 🎯 Características Principales

### ✅ Generación Inteligente de Rutinas
- **IA Generativa**: Google Gemini analiza tu perfil completo
- **Consideraciones Personalizadas**:
  - 🚹/🚺 **Sexo**: Adapta énfasis muscular (hormonas, distribución muscular)
  - 📅 **Edad**: Ajusta intensidad y reps según capacidad de recuperación
  - ⚖️ **Peso actual**: Calibra cargas relativas
  - 🎯 **Objetivos**: Enfoque específico (ganar masa, perder grasa, etc.)
  - 📊 **Días/semana**: Distribuye volumen según disponibilidad

### 📝 Información en cada Ejercicio
Ahora cada ejercicio incluye:
```json
{
  "ejercicio": "Press de Banca",
  "series": 4,
  "reps": "8-12",
  "peso_recomendado_lb": 140,
  "tip": "Consejo técnico específico para ti",
  "razon_ia": "Por qué es ideal para ti (edad, sexo, objetivos)"
}
```

## 🔧 Cómo Funciona

1. **Completas tu perfil** (nombre, sexo, edad, peso, altura, objetivos, días entreno)
2. **Das click en "Generar Mi Plan Inteligente"**
3. **IA conecta a Gemini API** con tu perfil
4. **Gemini genera rutina personalizada** en segundos
5. **Se guarda automáticamente** en `gym_data.json`

## 🌐 API Key Gemini

Tu API key está configurada:
- **Límite**: 60 llamadas/minuto (gratuito)
- **Modelo**: `gemini-pro` (más rápido)
- **Ubicación**: Línea 11 del código

⚠️ **Mantén tu API key segura** - No compartas publicamente

## 📊 Ejemplo de Rutina Generada

Para: **Hideki, 25 años, Masculino, 160 lbs, Ganar masa muscular**

```
LUNES (Pecho/Hombros)
├── Press de Banca
│   ├── Series: 4
│   ├── Reps: 8-12
│   ├── Peso: 165 lbs
│   └── Razón IA: "Ejercicio principal para ganar volumen pectoral"
├── Press Militar
│   ├── Series: 4
│   ├── Reps: 8-12
│   ├── Peso: 135 lbs
│   └── Razón IA: "Excelente para hombros en hombres jóvenes"
```

## 🔄 Fallback Local

Si Gemini falla (sin internet, límite excedido, etc.):
- **App NO se rompe**
- Genera rutina automáticamente usando algoritmo local
- Funciona sin cambios visibles

## 🚀 Mejoras Futuras

- [ ] Mostrar "Razón IA" en la interfaz
- [ ] Guardar historial de rutinas generadas
- [ ] Ajustes de intensidad basados en feedback del usuario
- [ ] Recomendaciones nutricionales personalizadas por IA
- [ ] Integración con streaming para respuestas más rápidas

## 📞 Troubleshooting

### Error: "Invalid API Key"
- Verifica que la API key sea correcta
- Accede a [https://ai.google.dev](https://ai.google.dev) para regenerarla

### Error: "Rate limit exceeded"
- Espera 1 minuto (límite de 60 llamadas/minuto)
- Usa fallback local mientras esperas

### La rutina no se genera
- Verifica conexión a internet
- Comprueba que tengas todos los campos completados
- Revisa la consola de Streamlit para mensajes de error

## 💡 Tips

1. **Sé específico en objetivos**: Cuantos más objetivos detalles, mejor personalización
2. **Actualiza regularmente**: La IA aprende de tu progreso
3. **Experimenta**: Regenera rutinas si necesitas variedad
4. **Comparte feedback**: Los tips de IA mejoran con tu experiencia

---

**Última actualización**: Abril 2026
**Versión**: 2.1 (Con Gemini Integration)
