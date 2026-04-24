# 🚀 Inicio Rápido - Sistema de Login y Registro

## ¿Qué se implementó?

✅ **Página de Login/Registro** - Antes de acceder a la app, ahora los usuarios deben:
- Registrarse con una nueva cuenta, O
- Iniciar sesión con una cuenta existente

✅ **Almacenamiento de datos de usuarios** en `user_data.json`:
- Nombre de usuario
- Contraseña
- Todos los datos del perfil (nombre, sexo, peso, altura, edad, días de entreno, objetivos)

✅ **Datos separados por usuario** en `gym_data.json`:
- Cada usuario tiene su propio espacio de datos completamente aislado
- Rutinas, historial de entrenamiento, pesos, etc.

✅ **Botón de Cerrar Sesión** en el sidebar para logout

---

## ¿Cómo empezar?

### 1. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

### 2. **Primera vez (Sin cuenta)**
- Haz clic en "✅ Crear Cuenta" en el panel derecho
- Completa todos los campos
- Haz clic en "✅ Crear Cuenta"

### 3. **Subsecuentes accesos (Con cuenta)**
- Ingresa tu usuario y contraseña
- Haz clic en "🚀 Iniciar Sesión"

### 4. **Cerrar sesión**
- En el sidebar, haz clic en "🚪 Cerrar Sesión"

---

## Archivos importantes

| Archivo | Descripción |
|---------|-----------|
| `app.py` | Aplicación principal (modificada) |
| `user_data.json` | Base de datos de usuarios (se crea automáticamente) |
| `gym_data.json` | Datos de entrenamiento por usuario (modificado) |
| `LOGIN_REGISTRO.md` | Documentación completa del sistema |
| `CAMBIOS_REALIZADOS.md` | Detalle técnico de cambios |
| `GUIA_PRUEBAS.md` | Cómo probar la funcionalidad |

---

## Campos disponibles en el registro

- **Usuario**: Nombre de usuario único (sin espacios recomendado)
- **Contraseña**: Con confirmación
- **Nombre completo**: Texto libre
- **Sexo**: Masculino / Femenino
- **Peso**: 50 - 500 libras
- **Altura**: Pies y Pulgadas
- **Edad**: 12 - 100 años
- **Días de entreno**: 3, 4 o 5 días
- **Objetivos**: Múltiple selección

---

## Estructura de datos guardada

### user_data.json
```json
{
  "usuario1": {
    "username": "usuario1",
    "password": "contraseña",
    "datos_perfil": { ... },
    "fecha_registro": "..."
  }
}
```

### gym_data.json
```json
{
  "usuario1": {
    "perfil_completado": true,
    "user": { ... },
    "rutina_semanal": { ... },
    ...
  }
}
```

---

## Funciones principales

```python
# Registrar usuario
registrar_usuario(username, password, datos_perfil)

# Validar credenciales
validar_credenciales(username, password)

# Verificar si existe
usuario_existe(username)

# Obtener datos
obtener_datos_usuario(username)
```

---

## Validaciones implementadas

✓ Usuario y contraseña requeridos  
✓ Las contraseñas deben coincidir en registro  
✓ No permite usuarios duplicados  
✓ Nombre completo obligatorio  
✓ Al menos un objetivo requerido  
✓ Validación de credenciales en login  

---

## 🔐 Nota de seguridad

⚠️ Las contraseñas se guardan en **texto plano** en esta versión  
Para producción, usa:
- `bcrypt` para hash de contraseñas
- HTTPS
- Base de datos segura
- Tokens JWT

---

## Preguntas frecuentes

**¿Puedo cambiar mi usuario/contraseña?**  
Todavía no. Es una característica a implementar en futuras versiones.

**¿Qué pasa si olvido mi contraseña?**  
Por ahora, no hay función de recuperación. Edita `user_data.json` manualmente.

**¿Dónde están mis datos guardados?**  
- Credenciales: `user_data.json`
- Entrenamiento: `gym_data.json`

**¿Puedo compartir mi cuenta?**  
Sí, pero cada login creará una nueva sesión. No se puede estar conectado con la misma cuenta en dos lugares simultáneamente.

**¿Se pierden los datos si elimino los JSON?**  
Sí. Mantén backups regulares.

---

## Próximas mejoras sugeridas

1. Recuperación de contraseña por email
2. Editar perfil después de registro
3. Hash de contraseñas
4. Autenticación de dos factores
5. Roles de administrador
6. Backup automático de datos

---

## Support

Si encuentras problemas:
1. Revisa la consola de Streamlit para errores
2. Verifica que `user_data.json` y `gym_data.json` existan
3. Lee `CAMBIOS_REALIZADOS.md` para entender la arquitectura
4. Consulta `GUIA_PRUEBAS.md` para validar funcionamiento

---

**¡Listo para usar! 🎉**

Abre la aplicación, crea una cuenta y comienza tu plan de entrenamiento personalizado.

```bash
streamlit run app.py
```

---

**Versión**: 1.0  
**Última actualización**: Abril 2026  
**Estado**: ✅ Funcional y listo para usar
