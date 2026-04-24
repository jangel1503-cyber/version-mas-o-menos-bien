# 📊 Arquitectura del Sistema de Login y Registro V1

## Arquitectura N-Capas (Abril 2026)

La app ahora quedó separada en capas para reducir acoplamiento y facilitar mantenimiento:

1. Capa de presentación
- `app.py`
- Renderizado de UI con Streamlit, formularios, tabs y estado de sesión.

2. Capa de aplicación/negocio
- `gym_app/services.py`
- Reglas de negocio: autenticación, cálculo de macros/IMC, generación de rutina, fallback de dieta, recomendaciones y utilidades de progreso.

3. Capa de infraestructura/persistencia
- `gym_app/repositories.py`
- Acceso a archivos JSON (`gym_data.json` y `user_data.json`) mediante funciones de lectura/escritura reutilizables.

### Flujo entre capas

`app.py` -> `gym_app/services.py` -> `gym_app/repositories.py`

Con esta estructura, `app.py` dejó de contener la lógica de negocio principal y ahora actúa como orquestador de la interfaz.

## Diagrama de flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICACIÓN GYM PRO AI                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ¿Usuario logueado?
                   /          \
                 NO             SÍ
                /                 \
               ▼                   ▼
        ┌──────────────┐    ┌──────────────────────┐
        │  PANTALLA    │    │  DASHBOARD PRINCIPAL │
        │ LOGIN/REGISTRO    │  DEL USUARIO         │
        └──────────────┘    └──────────────────────┘
             │                       │
      ┌──────┴──────┐               │
      │             │               │
      ▼             ▼               ▼
   LOGIN      REGISTRO          FUNCIONALIDADES
    │            │              ├─ Rutinas
    │            │              ├─ Historial
    │            │              ├─ Dieta
    │            │              ├─ Pesos
    │            │              ├─ Entrenamientos
    │            │              └─ Cerrar sesión
    │            │
    ▼            ▼
  ┌─────┐      ┌──────────┐
  │user_│      │ user_    │
  │data.│      │ data.json│
  │json │      │ (nuevo)  │
  └─────┘      └──────────┘
    │               │
    └───────┬───────┘
            │
            ▼
        ┌────────────────┐
        │ gym_data.json  │
        │ (por usuario)  │
        └────────────────┘
```

---

## Estructura de archivos

```
app.py                          # Aplicación principal
├── Funciones de autenticación
├── Pantalla de login/registro
├── Dashboard del usuario
└── Gestión de datos

user_data.json                  # BD de usuarios (credenciales)
├── usuario1
│   ├── username
│   ├── password
│   ├── datos_perfil
│   └── fecha_registro
├── usuario2
└── usuario3

gym_data.json                   # BD de entrenamiento (por usuario)
├── usuario1
│   ├── perfil_completado
│   ├── user
│   ├── rutina_semanal
│   ├── historial_pesos
│   ├── historial_entrenamientos
│   ├── pr_por_ejercicio
│   ├── fecha_ultima_rotacion
│   └── dieta_semanal
└── usuario2
```

---

## Ciclo de vida del usuario

### Primer acceso (Sin cuenta)

```
START
  │
  ├─→ Abre app.py
  │
  ├─→ Ver pantalla LOGIN/REGISTRO
  │
  ├─→ Completar formulario de REGISTRO
  │
  ├─→ Clic "✅ Crear Cuenta"
  │
  ├─→ Validaciones
  │   ├─ Usuario no vacío? ✓
  │   ├─ Contraseña = confirmación? ✓
  │   ├─ Usuario no existe? ✓
  │   └─ Datos completos? ✓
  │
  ├─→ Guardar en user_data.json
  │
  ├─→ Guardar en gym_data.json
  │
  ├─→ Éxito: "Ahora puedes iniciar sesión"
  │
  └─→ Siguiente acceso...
```

### Accesos posteriores (Con cuenta)

```
START
  │
  ├─→ Abre app.py
  │
  ├─→ Ver pantalla LOGIN/REGISTRO
  │
  ├─→ Ingresar credenciales
  │   ├─ Usuario
  │   └─ Contraseña
  │
  ├─→ Clic "🚀 Iniciar Sesión"
  │
  ├─→ Validar credenciales
  │   ├─ Usuario existe? ✓
  │   ├─ Contraseña coincide? ✓
  │   └─ st.session_state.usuario_logueado = usuario
  │
  ├─→ Cargar datos de gym_data.json[usuario]
  │
  ├─→ Cargar datos de user_data.json[usuario]
  │
  ├─→ Mostrar DASHBOARD
  │   ├─ Sidebar con nombre del usuario
  │   ├─ Botón "🚪 Cerrar Sesión"
  │   └─ Acceso a todas las funciones
  │
  └─→ Sesión activa
```

### Cerrar sesión

```
En el DASHBOARD
  │
  ├─→ Clic "🚪 Cerrar Sesión" en sidebar
  │
  ├─→ st.session_state.usuario_logueado = None
  │
  ├─→ Limpiar st.session_state.data
  │
  ├─→ Guardar datos en gym_data.json[usuario]
  │
  ├─→ Volver a LOGIN/REGISTRO
  │
  └─→ Disponible para otro usuario
```

---

## Funciones principales del sistema

### Autenticación

```
┌─────────────────────────────────────────────────────────────┐
│                   FUNCIONES DE LOGIN                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ cargar_usuarios()                                           │
│   → Lee user_data.json                                      │
│   ← Retorna dict de usuarios                                │
│                                                             │
│ guardar_usuarios(usuarios)                                  │
│   → Escribe user_data.json                                  │
│                                                             │
│ usuario_existe(username)                                    │
│   → Verifica en user_data.json                              │
│   ← True/False                                              │
│                                                             │
│ validar_credenciales(username, password)                    │
│   → Compara usuario y contraseña                            │
│   ← True/False                                              │
│                                                             │
│ registrar_usuario(username, password, datos_perfil)        │
│   → Crea nuevo usuario                                      │
│   → Guarda en user_data.json                                │
│   ← (exito, mensaje)                                        │
│                                                             │
│ obtener_datos_usuario(username)                             │
│   → Busca en user_data.json                                 │
│   ← datos_perfil                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Persistencia

```
┌─────────────────────────────────────────────────────────────┐
│                FUNCIONES DE PERSISTENCIA                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ guardar_todo(datos)                                         │
│   → Guarda datos del usuario actual                         │
│   → En gym_data.json[usuario_logueado]                      │
│                                                             │
│ cargar_todo()                                               │
│   → Carga datos del usuario actual                          │
│   ← Desde gym_data.json[usuario_logueado]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Variables de sesión

```
st.session_state
├── usuario_logueado (str o None)
│   └── Nombre de usuario actualmente conectado
│
├── data (dict)
│   ├── perfil_completado (bool)
│   ├── user (dict con datos del perfil)
│   ├── rutina_semanal (dict)
│   ├── historial_pesos (list)
│   ├── historial_entrenamientos (list)
│   ├── pr_por_ejercicio (dict)
│   ├── fecha_ultima_rotacion (date/None)
│   └── dieta_semanal (dict)
│
└── [otras variables de UI]
```

---

## Flujo de datos

### Registro

```
USER INPUT
  │
  ├─ Username
  ├─ Password
  ├─ Nombre completo
  ├─ Sexo
  ├─ Peso, Altura, Edad
  ├─ Días de entreno
  └─ Objetivos
     │
     ▼
  VALIDACIONES
  │
  ├─ ¿Campos completos?
  ├─ ¿Contraseñas coinciden?
  ├─ ¿Usuario no existe?
  ├─ ¿Objetivos seleccionados?
  │
  ├─ Si falla → ERROR (mostrar mensaje)
  │
  ├─ Si pasa → GUARDAR
     │
     ├─ registrar_usuario()
     │  └─ user_data.json[username] = {...}
     │
     ├─ guardar_usuarios()
     │
     └─ SUCCESS (mostrar mensaje)
```

### Login

```
USER INPUT
  │
  ├─ Username
  └─ Password
     │
     ▼
  VALIDAR
  │
  ├─ validar_credenciales(username, password)
  │
  ├─ ¿Encontrado?
  │  │
  │  ├─ NO → ERROR
  │  │
  │  ├─ SÍ → CARGAR DATOS
  │     │
  │     ├─ st.session_state.usuario_logueado = username
  │     │
  │     ├─ obtener_datos_usuario()
  │     │  └─ user_data.json[username].datos_perfil
  │     │
  │     ├─ cargar_todo()
  │     │  └─ gym_data.json[username]
  │     │
  │     └─ MOSTRAR DASHBOARD
```

---

## Ejemplo de uso

### Registrarse

```python
# Usuario envía formulario
datos_perfil = {
    "nombre": "Juan Pérez",
    "sexo": "Masculino",
    "peso_lb": 180,
    "pies": 5,
    "pulgadas": 10,
    "estatura_m": 1.778,
    "edad": 28,
    "dias_entreno": 5,
    "objetivos": ["🏋️ Ganar masa muscular", "🏋️ Aumentar fuerza"]
}

exito, mensaje = registrar_usuario("juan123", "pass456", datos_perfil)

# user_data.json se actualiza:
{
  "juan123": {
    "username": "juan123",
    "password": "pass456",
    "datos_perfil": { ... },
    "fecha_registro": "2024-04-21 15:30:00"
  }
}
```

### Iniciar sesión

```python
# Usuario envía credenciales
if validar_credenciales("juan123", "pass456"):
    # Cargar perfil
    datos = obtener_datos_usuario("juan123")
    st.session_state.usuario_logueado = "juan123"
    st.session_state.data = cargar_todo()
    # → Mostrar dashboard
else:
    # Mostrar error
```

---

## Ventajas de la arquitectura

✅ **Aislamiento**: Cada usuario tiene datos completamente separados  
✅ **Seguridad**: No hay interferencia entre usuarios  
✅ **Escalabilidad**: Fácil agregar más usuarios  
✅ **Persistencia**: Los datos se guardan automáticamente  
✅ **Compatibilidad**: Mantiene funcionalidad existente  
✅ **Simplicidad**: JSON simple, sin base de datos compleja  

---

## Limitaciones actuales

⚠️ Contraseñas en texto plano  
⚠️ Sin encriptación  
⚠️ Sin recuperación de contraseña  
⚠️ Sin edición de perfil  
⚠️ Sin roles/permisos  
⚠️ Sin backup automático  

---

## Mejoras futuras

📌 Implementar bcrypt para contraseñas  
📌 Usar base de datos (MongoDB, PostgreSQL)  
📌 Agregar recuperación de contraseña por email  
📌 Permitir edición de perfil  
📌 Agregar roles (admin, usuario, coach)  
📌 Backup automático en la nube  
📌 Autenticación social (Google, GitHub)  
📌 Autenticación de dos factores  

---

**Versión**: 1.0  
**Última actualización**: Abril 2026  
**Estado**: ✅ Funcional
