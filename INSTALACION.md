# 🚀 Gym Pro AI - Guía de Instalación y Ejecución

## ✅ Instalación Rápida (Local)

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la app
```bash
streamlit run app.py
```

La app se abrirá en: **http://localhost:8501**

---

## 🌐 Desplegar en Streamlit Cloud

### Requisitos:
- Repositorio en GitHub
- Cuenta en [Streamlit Cloud](https://streamlit.io/cloud)
- El archivo `requirements.txt` debe estar en la raíz

### Pasos:
1. Sube tu código a GitHub
2. Ve a https://share.streamlit.io
3. Click en "New app"
4. Selecciona tu repositorio
5. Elige la rama y el archivo `app.py`
6. Click "Deploy"

### Estructura esperada:
```
tu-repositorio/
├── app.py
├── gym_data.json
├── requirements.txt
└── .streamlit/
    └── config.toml
```

---

## 🔑 Variables de Entorno (Importante)

Si usas Streamlit Cloud, **NO guardes tu API key en el código**.

### Opción 1: Secrets Management (Recomendado)
1. En Streamlit Cloud: App settings → Secrets
2. Agrega:
```toml
GEMINI_API_KEY = "tu_clave_aqui"
```

3. En `app.py`, cambia la línea 11:
```python
# En lugar de:
# GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"

# Usa:
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
```

### Opción 2: Variables de Entorno Local
Crea `.env`:
```
GEMINI_API_KEY=tu_clave_aqui
```

Instala python-dotenv:
```bash
pip install python-dotenv
```

---

## ⚠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'google.generativeai'"
**Solución:**
```bash
pip install google-generativeai==0.4.0
```

### Error: "API key invalid"
- Verifica que la API key sea correcta
- Regenera en: https://ai.google.dev

### Streamlit Cloud no instala las dependencias
- Revisa que `requirements.txt` esté en la **raíz** del repositorio
- Haz un push nuevo para forzar reinstalación

### La rutina se genera lentamente
- La primera llamada a Gemini tarda ~3-5 segundos
- Es normal, Streamlit cachea resultados posteriores
- Si tarda más, verifica tu conexión a internet

---

## 📝 Contenido de requirements.txt

```
streamlit==1.28.1
google-generativeai==0.4.0
pandas==2.0.3
protobuf==3.20.0
```

---

## ✨ Características Incluidas

✅ Generación IA de rutinas (Gemini)
✅ Cálculo de macros personalizados
✅ Historial de peso
✅ Edición de rutinas
✅ Soporte para sexo, edad, peso, altura
✅ Regeneración de rutinas
✅ Almacenamiento local en JSON

---

**¡Listo! Tu app está lista para usar 💪**
