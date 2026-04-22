# 🔐 Sistema de Login y Registro - Gym Pro AI

## 📋 Descripción General

Se ha implementado un sistema completo de autenticación de usuarios que permite:
- **Registrarse** con una cuenta nueva
- **Iniciar sesión** con credenciales existentes
- **Gestionar datos** separados por usuario
- **Cerrar sesión** de forma segura

## 🎯 Características

### 1. **Registro de Nuevo Usuario**
Los usuarios pueden crear una nueva cuenta proporcionando:
- **Nombre de usuario** (único, no sensible a mayúsculas)
- **Contraseña** (con confirmación)
- **Datos de perfil**:
  - Nombre completo
  - Sexo (Masculino/Femenino)
  - Peso (en libras)
  - Altura (Pies y Pulgadas)
  - Edad
  - Días de entreno (3, 4 o 5 días)
  - Objetivos (múltiple selección)

### 2. **Inicio de Sesión**
Los usuarios existentes pueden iniciar sesión con:
- Nombre de usuario
- Contraseña

### 3. **Gestión de Datos**
- Cada usuario tiene sus propios datos en `gym_data.json`
- Los datos de autenticación se guardan en `user_data.json`
- La información se carga automáticamente al iniciar sesión

## 📁 Archivos de Datos

### `user_data.json`
Contiene la información de autenticación de todos los usuarios:
```json
{
  "username1": {
    "username": "username1",
    "password": "contraseña_hasheada",
    "datos_perfil": {
      "nombre": "Juan Pérez",
      "sexo": "Masculino",
      "peso_lb": 180,
      "pies": 5,
      "pulgadas": 10,
      "estatura_m": 1.78,
      "edad": 28,
      "dias_entreno": 5,
      "objetivos": ["🏋️ Ganar masa muscular (hipertrofia)", "...]
    },
    "fecha_registro": "2024-01-15 10:30:00.000000"
  }
}
```

### `gym_data.json`
Contiene todos los datos del entrenamiento de cada usuario (rutinas, historial, etc.):
```json
{
  "username1": {
    "perfil_completado": true,
    "user": { ... },
    "rutina_semanal": { ... },
    "historial_pesos": [ ... ],
    "historial_entrenamientos": [ ... ],
    ...
  }
}
```

## 🔄 Flujo de Uso

### Primer acceso (Sin cuenta)
1. Usuario ve la pantalla de **Login/Registro**
2. Elige registrarse en el panel derecho
3. Completa todos los campos (usuario, contraseña, datos de perfil)
4. Hace clic en "✅ Crear Cuenta"
5. Se le informa que puede iniciar sesión

### Acceso posterior (Con cuenta)
1. Usuario ve la pantalla de **Login/Registro**
2. Ingresa nombre de usuario y contraseña
3. Hace clic en "🚀 Iniciar Sesión"
4. Se carga automáticamente su perfil y datos
5. Accede al dashboard principal

### Cerrar sesión
- En el sidebar, el usuario tiene un botón "🚪 Cerrar Sesión"
- Vuelve a la pantalla de login/registro

## 🔐 Funciones Principales

### `registrar_usuario(username, password, datos_perfil)`
Registra un nuevo usuario con sus datos de perfil.

### `validar_credenciales(username, password)`
Valida que el usuario y contraseña sean correctos.

### `usuario_existe(username)`
Verifica si un usuario ya existe en la base de datos.

### `cargar_usuarios()`
Carga todos los usuarios desde `user_data.json`.

### `guardar_usuarios(usuarios)`
Guarda los usuarios en `user_data.json`.

### `obtener_datos_usuario(username)`
Obtiene los datos de perfil de un usuario específico.

## 📊 Estructura de Sesión

Cuando un usuario inicia sesión, se establecen estas variables en `st.session_state`:
- `usuario_logueado`: El nombre de usuario actual (o None si no está logueado)
- `data`: Los datos del usuario (rutinas, historial, etc.)

## ⚠️ Notas Importantes

1. **Las contraseñas NO están encriptadas** en esta versión. Para producción, considera usar:
   - `bcrypt` o `werkzeug.security` para hash de contraseñas
   - Una base de datos segura en lugar de JSON

2. **Los nombres de usuario no son sensibles a mayúsculas** (se convierten a minúsculas)

3. **Cada usuario tiene su propio espacio de datos** completamente separado

4. **Si eliminas `user_data.json` manualmente**, se perderán todas las cuentas

5. **Si eliminas `gym_data.json` manualmente**, se perderá todo el historial de entrenamiento

## 🚀 Ejemplo de Uso

```python
# Registrar nuevo usuario
registrar_usuario(
    username="juan123",
    password="micontraseña123",
    datos_perfil={
        "nombre": "Juan Pérez",
        "sexo": "Masculino",
        "peso_lb": 180,
        ...
    }
)

# Validar credenciales
if validar_credenciales("juan123", "micontraseña123"):
    print("Login exitoso")

# Obtener datos del usuario
datos = obtener_datos_usuario("juan123")
print(datos["nombre"])  # "Juan Pérez"
```

## 🎨 Interfaz de Usuario

La pantalla de login/registro tiene dos paneles:

### Panel Izquierdo - Iniciar Sesión
- Campo de nombre de usuario
- Campo de contraseña
- Botón "🚀 Iniciar Sesión"

### Panel Derecho - Registrarse
- Campo de nombre de usuario
- Campo de contraseña
- Campo de confirmación de contraseña
- Campos de datos de perfil (nombre, sexo, peso, altura, edad, días de entreno, objetivos)
- Botón "✅ Crear Cuenta"

---

**Versión**: 1.0  
**Última actualización**: Abril 2026  
**Estado**: Funcional y listo para usar
