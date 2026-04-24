import streamlit as st
import gym_app.services as services
import os
import json
import pandas as pd


import google.generativeai as genai
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = "AIzaSyB2KaHLEIebj5JQ99O_oG_k28vtSvcpRzA"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def guardar_todo(datos):
    return services.guardar_todo(datos, st.session_state.usuario_logueado)
def cargar_todo():
    return services.cargar_todo(st.session_state.usuario_logueado)
def calcular_macros(u):
    return services.calcular_macros(u)
def generar_dieta_semanal(perfil_json):
    return services.generar_dieta_semanal(perfil_json, model)
def generar_rutina_ia(u):
    return services.generar_rutina_ia(u, model)
def obtener_ejercicios_alternativos(ejercicio, musculo_objetivo):
    return services.obtener_ejercicios_alternativos(ejercicio, musculo_objetivo, model)
def generar_warmup(dia_entreno, ejercicios_dia):
    return services.generar_warmup(dia_entreno, ejercicios_dia, model)
def calcular_tiempo_descanso(objetivo, reps):
    return services.calcular_tiempo_descanso(objetivo, reps)
def registrar_entrenamiento(dia, ejercicios_completados):
    return services.registrar_entrenamiento(dia, ejercicios_completados)
def recomendaciones_ia(progreso_data, user_profile):
    return services.recomendaciones_ia(progreso_data, user_profile, model)
def obtener_musculos_del_dia(ejercicios_dia):
    return services.obtener_musculos_del_dia(ejercicios_dia)
def dashboard_page():
    u = st.session_state.data.get("user", {})
    imc, estado, p_min, p_max = services.obtener_analisis(u.get('peso_lb', 160), u.get('estatura_m', 1.70))
    with st.sidebar:
        nombre_usuario = u.get('nombre', 'Usuario')
        sexo_usuario = u.get('sexo', 'N/A')
        edad_usuario = u.get('edad', 'N/A')
        objetivos_usuario = u.get('objetivos', [])
        objetivo_principal = objetivos_usuario[0] if objetivos_usuario else 'Sin objetivos'
        st.markdown(f"""
            <div class="sidebar-profile">
                <h2 class="sidebar-brand-title">💪 Gym Pro AI</h2>
                <p class="sidebar-brand-subtitle">Tu Entrenador Personal Inteligente</p>
                <hr class="sidebar-divider">
                <p class="sidebar-profile-label">👤 Perfil de Usuario</p>
                <h3 class="sidebar-profile-name">{nombre_usuario}</h3>
                <p class="sidebar-profile-meta">⚧️ {sexo_usuario}</p>
                <p class="sidebar-profile-meta">🎂 {edad_usuario} años</p>
                <p class="sidebar-profile-goal">🎯 {objetivo_principal}</p>
            </div>
        """, unsafe_allow_html=True)
        st.info(f"📍 **Meta**: {len(objetivos_usuario)} objetivos seleccionados")
        st.markdown("---")
        if st.button("🚪 Salir", use_container_width=True, help="Cerrar sesión"):
            st.success("👋 ¡Hasta luego!")
            import time
            time.sleep(1)
            st.session_state.usuario_logueado = None
            st.session_state.data = {"perfil_completado": False, "user": {}, "rutina_semanal": {}, "historial_pesos": [], "historial_entrenamientos": [], "pr_por_ejercicio": {}, "fecha_ultima_rotacion": None, "dieta_semanal": {}}
            st.rerun()
        st.markdown("---")
        with st.expander("🔍 Verificar Datos Guardados"):
            st.write("**Datos en Session State (User):**")
            st.json(u)
            st.write("**Usuario Logueado:**", st.session_state.usuario_logueado)
            try:
                DB_FILE = services.DB_FILE
                if os.path.exists(DB_FILE):
                    with open(DB_FILE, "r", encoding='utf-8') as f:
                        todos_datos = json.load(f)
                        if st.session_state.usuario_logueado in todos_datos:
                            st.write("✅ Datos encontrados en gym_data.json")
                            st.write("**Campos guardados:**", list(todos_datos[st.session_state.usuario_logueado].keys()))
                        else:
                            st.write("❌ No hay datos en gym_data.json para este usuario")
            except:
                st.write("❌ Error leyendo gym_data.json")
    nombre_usuario = u.get("nombre", "Usuario")
    st.markdown(f'<h1 class="main-header">¡Bienvenido, {nombre_usuario}! 💪</h1>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 Tu Estado Actual")
    col_imc, col_estado, col_ideal, col_dias = st.columns(4)
    with col_imc:
        st.markdown(f"""
        <div class="dashboard-metric-card metric-card-imc">
            <h4 class="metric-title">📏 IMC</h4>
            <h2 class="metric-value">{imc}</h2>
            <p class="metric-caption">Indice de Masa Corporal</p>
        </div>
        """, unsafe_allow_html=True)
    with col_estado:
        estado_class = "status-normal" if estado == "Peso normal" else "status-sobrepeso" if estado == "Sobrepeso" else "status-obesidad" if estado == "Obesidad" else "status-bajo"
        st.markdown(f"""
        <div class="dashboard-metric-card metric-card-estado {estado_class}">
            <h4 class="metric-title">💪 Estado</h4>
            <h2 class="metric-value">{estado}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col_ideal:
        st.markdown(f"""
        <div class="dashboard-metric-card metric-card-ideal">
            <h4 class="metric-title">⚖️ Peso Ideal</h4>
            <h2 class="metric-value">{p_min}-{p_max}</h2>
            <p class="metric-caption">en Lbs</p>
        </div>
        """, unsafe_allow_html=True)
    with col_dias:
        st.markdown(f"""
        <div class="dashboard-metric-card metric-card-dias">
            <h4 class="metric-title">📅 Dias</h4>
            <h2 class="metric-value">{u.get("dias_entreno", 5)}</h2>
            <p class="metric-caption">entrenos/semana</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    t_rutina, t_entrenamiento, t_dieta, t_progreso, t_alternativas, t_recomendaciones = st.tabs(
        ["📅 Mi Rutina", "💪 Entrenar Hoy", "🍽️ Mi Dieta", "📈 Progreso", "🔄 Alternativas", "🤖 Recomendaciones"]
    )

    with t_rutina:
        st.markdown("### 🏋️ Tu Plan de Entrenamiento Personalizado")
        
        # Botones de acción en la parte superior
        col_btn1, col_btn2, col_info = st.columns([1, 1, 2])
        with col_btn1:
            if st.button("🤖 Generar Rutina", use_container_width=True, help="Crea una nueva rutina basada en tus objetivos"):
                with st.spinner("⏳ IA generando rutina personalizada..."):
                    st.session_state.data["rutina_semanal"] = generar_rutina_ia(u)
                    guardar_todo(st.session_state.data)
                st.success("✅ ¡Nueva rutina generada con IA!")
                st.balloons()
                st.rerun()
        
        with col_btn2:
            if st.button("🔄 Regenerar", use_container_width=True, help="Crea una nueva rutina"):
                st.session_state.data["rutina_semanal"] = generar_rutina_ia(u)
                guardar_todo(st.session_state.data)
                st.success("✅ ¡Nueva rutina generada!")
                st.rerun()
        
        st.markdown("---")
        
        # Recargar siempre los datos más frescos
        st.session_state.data = cargar_todo()
        rutina = st.session_state.data.get("rutina_semanal", {})
        for dia, ejercicios in rutina.items():
            # Obtener músculos del día
            musculos = obtener_musculos_del_dia(ejercicios if isinstance(ejercicios, list) else [])
            musculos_text = ", ".join(musculos) if musculos else "Descanso"
            
            with st.expander(f"📅 {dia.upper()} - 🔥 {musculos_text}", expanded=(dia=="Lunes")):
                if isinstance(ejercicios, str):
                    st.info(ejercicios)
                else:
                    for i, ej in enumerate(ejercicios):
                        # Convertir formato de Gemini (reps_por_serie/peso_lb_por_serie) al nuestro
                        if 'reps_por_serie' in ej and 'peso_lb_por_serie' in ej:
                            ej['detalles_sets'] = [
                                {"reps": str(ej['reps_por_serie'][idx]), "libras": float(ej['peso_lb_por_serie'][idx])}
                                for idx in range(len(ej['reps_por_serie']))
                            ]
                            ej['series'] = len(ej['reps_por_serie'])
                        # Asegurar compatibilidad con datos antiguos
                        elif 'detalles_sets' not in ej:
                            old_reps = ej.get('reps', '12')
                            old_lbs = ej.get('libras', 0)
                            ej['detalles_sets'] = [{"reps": old_reps, "libras": old_lbs} for _ in range(int(ej.get('series', 3)))]

                        st.markdown(f"""
                            <div class="exercise-card">
                                <div class="exercise-card-header">
                                    <strong>{ej['ejercicio']}</strong>
                                    <span title="{ej.get('tip', '')}" class="exercise-card-tip-icon">💡 Tip</span>
                                </div>
                                <small class="exercise-card-tip-text">{ej.get('tip', 'Mantén la técnica correcta.')}</small><br>
                                <small>Configuración: {ej['series']} sets totales</small>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([3, 1])
                        rutina[dia][i]['ejercicio'] = c1.text_input("Ejercicio", ej['ejercicio'], key=f"e_{dia}_{i}")
                        num_sets = c2.number_input("Sets totales", 1, 12, int(ej['series']), key=f"s_{dia}_{i}")
                        rutina[dia][i]['series'] = num_sets
                        
                        # Ajustar lista de detalles si cambió el número de sets
                        if len(ej['detalles_sets']) != num_sets:
                            if len(ej['detalles_sets']) < num_sets:
                                extra = num_sets - len(ej['detalles_sets'])
                                last_val = ej['detalles_sets'][-1] if ej['detalles_sets'] else {"reps": "10", "libras": 0}
                                for _ in range(extra):
                                    ej['detalles_sets'].append(last_val.copy())
                            else:
                                ej['detalles_sets'] = ej['detalles_sets'][:num_sets]
                        
                        # Grid para editar reps y lbs de cada set
                        st.markdown("###### Detalles por Set (Reps | Lbs)")
                        for s_idx in range(num_sets):
                            sc1, sc2, sc3 = st.columns([1, 2, 2])
                            sc1.markdown(f"**Set {s_idx+1}**")
                            ej['detalles_sets'][s_idx]['reps'] = sc2.text_input(f"Reps S{s_idx}", ej['detalles_sets'][s_idx]['reps'], key=f"r_{dia}_{i}_{s_idx}", label_visibility="collapsed")
                            ej['detalles_sets'][s_idx]['libras'] = sc3.number_input(f"Lbs S{s_idx}", 0.0, 1000.0, float(ej['detalles_sets'][s_idx]['libras']), key=f"l_{dia}_{i}_{s_idx}", label_visibility="collapsed")
                        st.markdown("---")
        
        if st.button("💾 Guardar Cambios en la Rutina"):
            st.session_state.data["rutina_semanal"] = rutina
            guardar_todo(st.session_state.data)
            st.toast("¡Cambios guardados!", icon="✅")

    with t_dieta:
        st.markdown("### 🍽️ Tu Plan de Nutrición Personalizado")
        
        # Cargar datos frescos
        st.session_state.data = cargar_todo()
        dieta = st.session_state.data.get("dieta_semanal", {})
        u = st.session_state.data.get("user", {})
        
        # Información nutricional resumen
        st.markdown("#### 📊 Tu Objetivo Nutricional")
        cal, p, g, c = calcular_macros(u)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calorías", f"{cal} kcal")
        with col2:
            st.metric("🥩 Proteína", f"{p}g")
        with col3:
            st.metric("🍞 Carbos", f"{c}g")
        with col4:
            st.metric("🥑 Grasas", f"{g}g")
        
        st.markdown("---")
        
        if dieta and any(dieta.values()):
            st.markdown(f"**Objetivo Nutricional:** {dieta.get('objetivo_nutricional', 'N/A')}")
            st.markdown(f"**Calorías Diarias Aprox:** {dieta.get('calorias_diarias_aprox', cal)} kcal")
            
            plan = dieta.get('plan_semanal', {})
            
            for dia in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
                if dia in plan:
                    comidas = plan[dia]
                    
                    with st.expander(f"📅 {dia}", expanded=(dia == "Lunes")):
                        # Desayuno
                        if "desayuno" in comidas:
                            des = comidas["desayuno"]
                            st.markdown(f"""<div class="exercise-card meal-card meal-breakfast">
                                <h4 class="meal-title">🌅 Desayuno</h4>
                                <strong>{des.get('comida', 'N/A')}</strong><br>
                                <small>📏 {des.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {des.get('tip', '')}</small><br>
                                <small>🔥 {des.get('calorias_aprox', '')} kcal | 🥩 {des.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Merienda Mañana
                        if "merienda_manana" in comidas:
                            mer_m = comidas["merienda_manana"]
                            st.markdown(f"""<div class="exercise-card meal-card meal-midmorning">
                                <h4 class="meal-title">🥪 Merienda Media Manana</h4>
                                <strong>{mer_m.get('comida', 'N/A')}</strong><br>
                                <small>📏 {mer_m.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {mer_m.get('tip', '')}</small><br>
                                <small>🔥 {mer_m.get('calorias_aprox', '')} kcal</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Almuerzo
                        if "almuerzo" in comidas:
                            alm = comidas["almuerzo"]
                            st.markdown(f"""<div class="exercise-card meal-card meal-lunch">
                                <h4 class="meal-title">🍽️ Almuerzo</h4>
                                <strong>{alm.get('comida', 'N/A')}</strong><br>
                                <small>📏 {alm.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {alm.get('tip', '')}</small><br>
                                <small>🔥 {alm.get('calorias_aprox', '')} kcal | 🥩 {alm.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Merienda Tarde
                        if "merienda_tarde" in comidas:
                            mer_t = comidas["merienda_tarde"]
                            st.markdown(f"""<div class="exercise-card meal-card meal-afternoon">
                                <h4 class="meal-title">🍌 Merienda Media Tarde (Post-Entreno)</h4>
                                <strong>{mer_t.get('comida', 'N/A')}</strong><br>
                                <small>📏 {mer_t.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {mer_t.get('tip', '')}</small><br>
                                <small>🔥 {mer_t.get('calorias_aprox', '')} kcal | 🥩 {mer_t.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
                            st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Cena
                        if "cena" in comidas:
                            cena = comidas["cena"]
                            st.markdown(f"""<div class="exercise-card meal-card meal-dinner">
                                <h4 class="meal-title">🌙 Cena</h4>
                                <strong>{cena.get('comida', 'N/A')}</strong><br>
                                <small>📏 {cena.get('cantidad', 'N/A')}</small><br>
                                <small>💡 {cena.get('tip', '')}</small><br>
                                <small>🔥 {cena.get('calorias_aprox', '')} kcal | 🥩 {cena.get('proteina_g', '')}g proteína</small>
                            </div>""", unsafe_allow_html=True)
        else:
            st.info("No tienes un plan de dieta aún. ¡Genera uno abajo!")
        
        st.markdown("---")
        
        # Botones para generar y actualizar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generar Mi Plan de Nutrición con IA", use_container_width=True, key="gen_dieta"):
                perfil_nutri = {
                    "nombre": u.get('nombre', 'Usuario'),
                    "sexo": u.get('sexo', 'Masculino'),
                    "edad": u.get('edad', 25),
                    "peso_lb": u.get('peso_lb', 160),
                    "estatura_m": u.get('estatura_m', 1.70),
                    "objetivos": u.get('objetivos', [])[:2],  # Top 2 objetivos
                    "dias_entreno": u.get('dias_entreno', 5),
                    "calorias_objetivo": cal
                }
                
                with st.spinner("🤖 IA generando plan nutricional personalizado..."):
                    nueva_dieta = generar_dieta_semanal(json.dumps(perfil_nutri))
                
                if nueva_dieta:
                    st.session_state.data["dieta_semanal"] = nueva_dieta
                    guardar_todo(st.session_state.data)
                    st.success("✅ ¡Plan de nutrición generado exitosamente!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error generando el plan. Intenta nuevamente.")
        
        with col2:
            if dieta and any(dieta.values()):
                if st.button("🔄 Regenerar Plan", use_container_width=True, key="regen_dieta"):
                    # Limpiar caché para permitir regeneración
                    st.cache_data.clear()
                    st.rerun()

    with t_entrenamiento:
        st.markdown("### 💪 Entrenar Hoy")
        from datetime import datetime
        hoy = datetime.now().strftime("%A")
        dias_map = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
        dia_hoy = dias_map.get(hoy, hoy)
        
        rutina = st.session_state.data.get("rutina_semanal", {})
        
        if dia_hoy in rutina:
            ejercicios_hoy = rutina[dia_hoy]
            # Obtener músculos del día
            musculos = obtener_musculos_del_dia(ejercicios_hoy if isinstance(ejercicios_hoy, list) else [])
            musculos_text = ", ".join(musculos) if musculos else "Descanso"
            
            st.success(f"✅ Hoy es {dia_hoy} - 🔥 {musculos_text}")
            
            # Mostrar warmup sugerido
            with st.expander("🔥 Warmup Personalizado (5 min)"):
                warmup = generar_warmup(dia_hoy, ejercicios_hoy if isinstance(ejercicios_hoy, list) else [])
                for actividad in warmup.get('warmup', []):
                    st.write(f"⏱️ {actividad['actividad']} - {actividad['duracion_min']} min")
            
            st.markdown("---")
            st.markdown("#### 📋 Marcar Ejercicios Completados")
            
            # Entrenamientos
            if isinstance(ejercicios_hoy, list):
                # Crear un contenedor para trackear ejercicios completados
                if 'ejercicios_completados_hoy' not in st.session_state:
                    st.session_state.ejercicios_completados_hoy = {idx: False for idx in range(len(ejercicios_hoy))}
                
                ejercicios_datos = []
                
                for idx, ej in enumerate(ejercicios_hoy):
                    with st.container():
                        # Checkbox para marcar como completado
                        col_check, col_content = st.columns([0.5, 9.5])
                        
                        with col_check:
                            completado = st.checkbox(
                                "✓",
                                value=st.session_state.ejercicios_completados_hoy.get(idx, False),
                                key=f"check_{idx}",
                                label_visibility="collapsed"
                            )
                            st.session_state.ejercicios_completados_hoy[idx] = completado
                        
                        with col_content:
                            with st.expander(f"{'✅' if completado else '🏋️'} {ej['ejercicio']}", expanded=(idx == 0)):
                                col_info1, col_info2 = st.columns(2)
                                
                                with col_info1:
                                    st.info(f"💡 {ej.get('tip', '')}")
                                
                                with col_info2:
                                    st.markdown(f"**Plan del día:**")
                                    for s_idx, detalle in enumerate(ej.get('detalles_sets', [])):
                                        st.write(f"Set {s_idx+1}: {detalle['reps']} reps × {detalle['libras']} lbs (⏱️ {calcular_tiempo_descanso(u.get('objetivos', [''])[0] if u.get('objetivos') else 'hipertrofia', detalle['reps'])})")
                                
                                st.markdown("---")
                                st.markdown("**Registra tu desempeño real:**")
                                
                                # Registrar resultado
                                with st.form(f"form_ejer_{idx}"):
                                    col_r, col_p, col_n = st.columns([1, 1, 2])
                                    
                                    with col_r:
                                        reps_real = st.number_input(f"Reps completadas", 0, 100, key=f"reps_{idx}")
                                    
                                    with col_p:
                                        peso_real = st.number_input(f"Peso (lbs)", 0.0, 1000.0, key=f"peso_{idx}")
                                    
                                    with col_n:
                                        notas = st.text_input(f"Notas (opcional)", key=f"notas_{idx}", label_visibility="visible")
                                    
                                    col_submit1, col_submit2 = st.columns(2)
                                    with col_submit1:
                                        if st.form_submit_button(f"✅ Registrar {ej['ejercicio']}", use_container_width=True):
                                            if reps_real > 0 and peso_real > 0:
                                                ejercicios_datos.append({
                                                    "nombre": ej['ejercicio'],
                                                    "reps_completadas": reps_real,
                                                    "peso_levantado": peso_real,
                                                    "notas": notas,
                                                    "series_planificadas": int(ej['series']),
                                                    "reps_planificadas": ej.get('detalles_sets', [{}])[0].get('reps', 0),
                                                    "peso_planificado": ej.get('detalles_sets', [{}])[0].get('libras', 0)
                                                })
                                                st.session_state.ejercicios_completados_hoy[idx] = True
                                                st.success(f"✅ {ej['ejercicio']} registrado!")
                                            else:
                                                st.warning("⚠️ Debes ingresar reps y peso")
                
                st.markdown("---")
                
                # Resumen del entrenamiento
                completados = sum(1 for v in st.session_state.ejercicios_completados_hoy.values() if v)
                total = len(ejercicios_hoy)
                
                st.markdown(f"### 📊 Progreso de Hoy")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Ejercicios Completados", f"{completados}/{total}")
                with col_p2:
                    porcentaje = int((completados / total * 100) if total > 0 else 0)
                    st.metric("Porcentaje", f"{porcentaje}%")
                with col_p3:
                    if completados == total:
                        st.success("¡ENTRENAMIENTO COMPLETO! 🎉")
                    else:
                        st.info(f"Te faltan {total - completados} ejercicio(s)")
                
                # Botón para guardar todo el entrenamiento
                if st.button("💾 Guardar Entrenamiento Completo", key="save_all_training", use_container_width=True):
                    if completados > 0:
                        entrenamiento = registrar_entrenamiento(dia_hoy, ejercicios_datos)
                        st.session_state.data["historial_entrenamientos"].append(entrenamiento)
                        
                        # Actualizar PR por ejercicio
                        pr_data = st.session_state.data.get("pr_por_ejercicio", {})
                        for ej_data in ejercicios_datos:
                            ej_nombre = ej_data["nombre"]
                            peso_levantado = ej_data["peso_levantado"]
                            if ej_nombre not in pr_data or peso_levantado > pr_data[ej_nombre]:
                                pr_data[ej_nombre] = peso_levantado
                        st.session_state.data["pr_por_ejercicio"] = pr_data
                        
                        guardar_todo(st.session_state.data)
                        st.success("¡Entrenamiento guardado exitosamente!")
                        st.balloons()
                        
                        # Limpiar estado
                        st.session_state.ejercicios_completados_hoy = {idx: False for idx in range(len(ejercicios_hoy))}
                        st.rerun()
                    else:
                        st.warning("⚠️ Debes registrar al menos un ejercicio")
            else:
                st.info(f"📅 {ejercicios_hoy}")
        else:
            st.warning(f"📅 No hay rutina para {dia_hoy}")

    with t_alternativas:
        st.markdown("### 🔄 Ejercicios Alternativos")
        st.write("¿No tienes equipo disponible? Encuentra alternativas para tus ejercicios.")
        
        rutina = st.session_state.data.get("rutina_semanal", {})
        todos_ejercicios = []
        mapeo_ejercicio_dia = {}
        
        # Crear lista con ID único
        for dia, ejercicios in rutina.items():
            if isinstance(ejercicios, list):
                for idx, e in enumerate(ejercicios):
                    ej_name = e['ejercicio']
                    unique_id = f"{dia}_{idx}"  # ID único: día_índice
                    todos_ejercicios.append((ej_name, unique_id))
                    mapeo_ejercicio_dia[unique_id] = (dia, idx, ej_name)
        
        if todos_ejercicios:
            col1, col2 = st.columns([2, 1])
            with col1:
                ejercicio_display = [e[0] for e in todos_ejercicios]
                idx_sel = st.selectbox("Selecciona un ejercicio", range(len(ejercicio_display)), 
                                       format_func=lambda i: ejercicio_display[i])
                unique_id = todos_ejercicios[idx_sel][1]
                ejercicio_sel = todos_ejercicios[idx_sel][0]
            
            with col2:
                buscar = st.button("🔍 Buscar Alternativas", use_container_width=True)
            
            if buscar:
                with st.spinner("Buscando alternativas con IA..."):
                    alternativas = obtener_ejercicios_alternativos(ejercicio_sel, "")
                    
                    st.markdown(f"**Alternativas para: {ejercicio_sel}**")
                    
                    if alternativas.get('alternativas') and len(alternativas['alternativas']) > 0:
                        for idx, alt in enumerate(alternativas['alternativas'], 1):
                            col_alt1, col_alt2 = st.columns([3, 1])
                            with col_alt1:
                                st.write(f"**Opción {idx}: {alt['nombre']}**")
                                st.caption(f"💡 {alt['razon']}")
                            with col_alt2:
                                if st.button(f"✅ Usar", key=f"alt_{idx}_{unique_id}"):
                                    # Obtener datos del mapeo
                                    dia, ej_idx, ej_original = mapeo_ejercicio_dia[unique_id]
                                    
                                    # Reemplazar en rutina
                                    st.session_state.data["rutina_semanal"][dia][ej_idx]['ejercicio'] = alt['nombre']
                                    guardar_todo(st.session_state.data)
                                    
                                    # Recargar desde JSON para asegurar sincronización
                                    st.session_state.data = cargar_todo()
                                    
                                    st.success(f"✅ {ej_original} → {alt['nombre']}")
                                    st.toast(f"Cambio guardado en {dia}", icon="💪")
                                    st.balloons()
                                    
                                    # Pequeña pausa y rerun
                                    import time
                                    time.sleep(0.5)
                                    st.rerun()
                    else:
                        st.warning("⚠️ No se encontraron alternativas en este momento")
        else:
            st.info("Carga una rutina primero")

    with t_recomendaciones:
        st.markdown("### 🤖 Recomendaciones Personalizadas")
        
        historial_ent = st.session_state.data.get("historial_entrenamientos", [])
        if len(historial_ent) >= 3:
            if st.button("🔮 Generar Recomendaciones"):
                with st.spinner("Analizando tu progreso..."):
                    progreso = {
                        "entrenamientos_totales": len(historial_ent),
                        "ultimo_entrenamiento": historial_ent[-1] if historial_ent else None
                    }
                    recomendaciones = recomendaciones_ia(progreso, u)
                    
                    for rec in recomendaciones.get('recomendaciones', []):
                        st.info(f"**{rec['titulo']}**\n{rec['descripcion']}")
        else:
            st.info(f"Necesitas al menos 3 entrenamientos registrados (tienes {len(historial_ent)})")


    with t_progreso:
        st.markdown("### 📊 Evolución y Análisis Nutricional")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("#### ⚖️ Registrar Peso")
            with st.form("log_peso"):
                peso_actual = float(u.get('peso_lb', 160.0)) if u.get('peso_lb') else 160.0
                n_p = st.number_input("Peso de hoy (Lbs)", 50.0, 500.0, peso_actual)
                if st.form_submit_button("Anotar Peso"):
                    from datetime import date
                    hoy = str(date.today())
                    st.session_state.data["historial_pesos"].append({"fecha": hoy, "peso": n_p})
                    st.session_state.data["user"]["peso_lb"] = n_p
                    guardar_todo(st.session_state.data)
                    st.success(f"¡Peso de {n_p} lbs registrado!")
                    st.rerun()
            
            cal, p, g, c = calcular_macros(u)
            st.markdown(f"""
                <div class="exercise-card macro-card">
                    <h4 class="meal-title">🔥 Calorias Objetivo</h4>
                    <h2 class="metric-value">{cal} kcal</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"**Macros Directriz:**")
            st.write(f"🥩 Proteína: {p}g | 🍞 Carbos: {c}g | 🥑 Grasas: {g}g")

        with c2:
            st.markdown("#### 📉 Tendencia de Peso")
            historial = st.session_state.data.get("historial_pesos", [])
            if historial:
                df = pd.DataFrame(historial)
                df['fecha'] = pd.to_datetime(df['fecha'])
                st.line_chart(df.set_index('fecha')['peso'])
                
                # Estadísticas
                pesos = [h['peso'] for h in historial]
                st.metric("Peso Inicial", f"{pesos[0]:.1f} lbs", f"{pesos[-1] - pesos[0]:.1f} lbs")
            else:
                st.info("Aún no tienes registros de peso. ¡Empieza hoy!")
            
            st.markdown("#### 📅 Historial de Entrenamientos")
            historial_ent = st.session_state.data.get("historial_entrenamientos", [])
            if historial_ent:
                entrenamientos_df = pd.DataFrame(historial_ent)
                if len(entrenamientos_df) > 0:
                    st.metric("Total Entrenamientos", len(entrenamientos_df))
                    
                    # Mostrar últimos entrenamientos con detalles
                    st.markdown("**Últimos Entrenamientos:**")
                    for entrenamiento in historial_ent[-5:]:  # Mostrar últimos 5
                        fecha = entrenamiento.get('fecha', 'N/A')
                        dia = entrenamiento.get('dia', 'N/A')
                        ejercicios = entrenamiento.get('ejercicios', [])
                        
                        with st.expander(f"📅 {fecha} - {dia} ({len(ejercicios)} ejercicios)"):
                            for ej in ejercicios:
                                st.write(f"✅ **{ej['nombre']}**: {ej['reps_completadas']} reps × {ej['peso_levantado']} lbs")
                                if ej.get('notas'):
                                    st.caption(f"📝 {ej['notas']}")
            else:
                st.info("Aún no has registrado entrenamientos.")
            
            st.markdown("#### 🏆 Personal Records (PR)")
            pr_data = st.session_state.data.get("pr_por_ejercicio", {})
            if pr_data:
                st.markdown("**Tus mejores pesos levantados:**")
                for ejercicio, peso in sorted(pr_data.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"🥇 **{ejercicio}**: {peso} lbs")
            else:
                st.info("Aún no tienes records. ¡Empieza a entrenar!")


if __name__ == "__main__":
    dashboard_page()
