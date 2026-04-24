# 🧪 Guía de Prueba - Sistema de Login y Registro

## Pruebas básicas recomendadas

### Prueba 1: Registro de nuevo usuario
**Pasos:**
1. Abre la aplicación (`streamlit run app.py`)
2. En el panel derecho, ingresa:
   - Usuario: `testuser1`
   - Contraseña: `pass123`
   - Confirmar contraseña: `pass123`
   - Nombre: `Juan Prueba`
   - Sexo: `Masculino`
   - Peso: `180`
   - Altura: `5` pies `10` pulgadas
   - Edad: `28`
   - Días de entreno: `5`
   - Objetivos: Selecciona al menos 2
3. Haz clic en "✅ Crear Cuenta"

**Resultado esperado:**
- ✓ Mensaje de éxito
- ✓ Aparece mensaje "Ahora puedes iniciar sesión"
- ✓ Se crea `user_data.json` con el nuevo usuario

---

### Prueba 2: Validación de registro (campos vacíos)
**Pasos:**
1. En el panel de registro, intenta enviar sin llenar campos
2. Prueba cada combinación de campos vacíos

**Resultado esperado:**
- ✓ Error: "Completa todos los campos"
- ✓ Error: "Las contraseñas no coinciden"
- ✓ Error: "Completa nombre y selecciona al menos un objetivo"

---

### Prueba 3: Intentar registro con usuario existente
**Pasos:**
1. Registra el usuario `testuser1` (como en Prueba 1)
2. Intenta registrar otro usuario con el mismo nombre

**Resultado esperado:**
- ✗ Error: "El usuario ya existe"

---

### Prueba 4: Login exitoso
**Pasos:**
1. En el panel izquierdo, ingresa:
   - Usuario: `testuser1`
   - Contraseña: `pass123`
2. Haz clic en "🚀 Iniciar Sesión"

**Resultado esperado:**
- ✓ Mensaje de éxito
- ✓ Se carga el dashboard del usuario
- ✓ El nombre del usuario aparece en el sidebar
- ✓ Los datos del perfil se muestran correctamente

---

### Prueba 5: Login con credenciales incorrectas
**Pasos:**
1. En el panel izquierdo, ingresa:
   - Usuario: `testuser1`
   - Contraseña: `wrongpassword`
2. Haz clic en "🚀 Iniciar Sesión"

**Resultado esperado:**
- ✗ Error: "Usuario o contraseña incorrectos"
- ✓ No se abre el dashboard

---

### Prueba 6: Cerrar sesión
**Pasos:**
1. Inicia sesión como `testuser1`
2. En el sidebar, haz clic en "🚪 Cerrar Sesión"

**Resultado esperado:**
- ✓ Vuelve a la pantalla de login/registro
- ✓ Los datos de sesión se limpian

---

### Prueba 7: Datos separados por usuario
**Pasos:**
1. Registra usuario `user1` con peso 180 lbs
2. Inicia sesión como `user1`
3. Realiza algunas acciones (agrega weight, entrena, etc.)
4. Cierra sesión
5. Registra usuario `user2` con peso 150 lbs
6. Inicia sesión como `user2` - verifica que los datos sean diferentes
7. Cierra sesión
8. Inicia sesión como `user1` - verifica que sus datos originales estén intactos

**Resultado esperado:**
- ✓ Cada usuario tiene datos completamente separados
- ✓ Cambios en user2 no afectan a user1

---

### Prueba 8: Persistencia de datos
**Pasos:**
1. Inicia sesión como `testuser1`
2. Realiza alguna acción en la aplicación
3. Cierra Streamlit (Ctrl+C)
4. Reabre Streamlit
5. Inicia sesión como `testuser1`

**Resultado esperado:**
- ✓ Todos los datos se mantienen
- ✓ Los cambios realizados persisten

---

### Prueba 9: Múltiples usuarios simultáneos
**Pasos:**
1. Abre dos ventanas del navegador (localhost:8501)
2. En la primera, inicia sesión como `user1`
3. En la segunda, inicia sesión como `user2`
4. Realiza acciones diferentes en cada una

**Resultado esperado:**
- ✓ Cada ventana mantiene su sesión independiente
- ✓ No hay interferencia entre usuarios

---

## Verificación de archivos

### Después de Prueba 1:
**Verifica que exista `user_data.json` con:**
```json
{
  "testuser1": {
    "username": "testuser1",
    "password": "pass123",
    "datos_perfil": {
      "nombre": "Juan Prueba",
      "sexo": "Masculino",
      "peso_lb": 180,
      ...
    }
  }
}
```

### Después de Prueba 3:
**Verifica que exista `gym_data.json` con:**
```json
{
  "testuser1": {
    "perfil_completado": true,
    "user": { ... },
    ...
  }
}
```

---

## Casos edge a probar

1. **Nombres de usuario con mayúsculas:**
   - Registra: `TestUser`
   - Intenta login con: `testuser`
   - Resultado: Debe funcionar (insensible a mayúsculas)

2. **Contraseñas especiales:**
   - Registra: `p@ss!w0rd#123`
   - Intenta login: Debe funcionar

3. **Nombres con espacios:**
   - Registra usuario: `test user`
   - Intenta login: Debe funcionar

4. **Datos de perfil extremos:**
   - Peso mínimo: 50 lbs
   - Peso máximo: 500 lbs
   - Edad mínima: 12 años
   - Edad máxima: 100 años
   - Altura mínima: 3 pies
   - Altura máxima: 8 pies

5. **Seleccionar múltiples objetivos:**
   - Registra usuario con 5+ objetivos
   - Verifica que se guarden todos

---

## Pruebas de estrés

1. **Registrar 10+ usuarios**
   - Crea varios usuarios
   - Verifica que `user_data.json` tenga todos

2. **Cambiar entre usuarios rápidamente**
   - Login/logout múltiples veces
   - Verifica que no haya pérdida de datos

3. **Operaciones simultáneas**
   - Múltiples ventanas modificando datos
   - Verifica consistencia

---

## Checklist de validación final

- [ ] Registro funciona correctamente
- [ ] Login funciona correctamente
- [ ] Logout funciona correctamente
- [ ] Datos se guardan en `user_data.json`
- [ ] Datos se guardan en `gym_data.json` por usuario
- [ ] Validaciones funcionan
- [ ] Mensajes de error son claros
- [ ] Cada usuario tiene datos separados
- [ ] Los datos persisten después de cerrar la aplicación
- [ ] El dashboard carga los datos del usuario correcto
- [ ] El sidebar muestra el nombre del usuario conectado
- [ ] No hay errores en la consola

---

## Notas para QA

- Revisa la consola de Streamlit para mensajes de error
- Verifica los archivos JSON después de cada operación
- Prueba con datos realistas y también casos extremos
- Intenta acceder a datos de otro usuario editando JSON

---

**Versión**: 1.0  
**Última actualización**: Abril 2026
