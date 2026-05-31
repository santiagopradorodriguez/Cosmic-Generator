"""
(C) Rebeldía Cósmica | Creado por Santiago Prado
"""
import streamlit as st
import os
import sys
import threading

# Añadir src al path para importar módulos correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from render.stable.render_standard import generar_animacion_god_mode
from core.video_utils import unir_video_con_musica
from audio.motor_lyrics import transcribir_audio_para_edicion

import time

import time

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx
except ImportError:
    try:
        from streamlit.scriptrunner import get_script_run_ctx, add_script_run_ctx
    except ImportError:
        try:
            from streamlit.report_thread import get_report_ctx as get_script_run_ctx
            from streamlit.report_thread import add_report_ctx as add_script_run_ctx
        except ImportError:
            get_script_run_ctx = lambda: None
            add_script_run_ctx = lambda thread: None

class StreamlitLogRedirector:
    """Redirige stdout y stderr a un elemento de Streamlit en tiempo real de forma segura (Thread-Safe)."""
    def __init__(self, st_empty_element):
        self.st_empty_element = st_empty_element
        self.text = ""
        self.terminal = sys.stdout
        self.last_update = 0
        self._is_writing = False
        
    def write(self, msg):
        if self._is_writing:
            self.terminal.write(msg)
            return
            
        self._is_writing = True
        try:
            self.text += msg
            self.terminal.write(msg)
            
            # Ignorar actualización visual si el log viene de un hilo secundario sin contexto (Numba, Audio)
            if get_script_run_ctx() is None:
                return
                
            now = time.time()
            # Actualizar UI como máximo 2 veces por segundo (cada 0.5s)
            if now - self.last_update > 0.5:
                self.st_empty_element.code(self.text[-2500:], language='bash')
                self.last_update = now
        finally:
            self._is_writing = False
            
    def flush(self):
        self.terminal.flush()

# Configuración de la página (DEBE ser la primera llamada a st)
st.set_page_config(
    page_title="Cosmic Generator V2.0",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos personalizados
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("src/ui/style.css")
except Exception as e:
    st.warning("No se pudo cargar el archivo de estilos CSS.")

# Barra lateral (Sidebar)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2048px-Spotify_logo_without_text.svg.png", width=50) # Imagen placeholder
    st.title("Cosmic Generator")
    st.markdown("---")
    
    menu = st.radio(
        "Navegación",
        ["🏠 Inicio", "🎛️ Generador", "🎬 Director IA", "🧪 Motores", "⚙️ Configuración", "📚 Academia Matemática", "🧪 Laboratorio de Física"]
    )
    
    st.markdown("---")
    st.markdown("### Info")
    st.markdown("**Proyecto:** Generador de videos musicales de Rebeldía Cósmica")
    st.markdown("**Autor:** Santiago Prado")
    st.markdown("**Versión:** 2.0 (Streamlit Beta)")

# Lógica principal según el menú
if menu == "🏠 Inicio":
    st.title("Bienvenido a Cosmic Generator 🌌")
    st.markdown("""
    > **Propósito de Rebeldía Cósmica:**
    > Nuestra misión es *democratizar el acceso a la producción de videos musicales*. Queremos que los pequeños artistas, bandas emergentes y creadores independientes tengan la capacidad de generar videoclips hiper-profesionales y estéticamente alucinantes sin necesidad de presupuestos millonarios. Combinamos el **Arte Matemático**, los **Sistemas Dinámicos No-Lineales** y la **Inteligencia Artificial** para que tu música tenga el acompañamiento visual que merece.
    
    Esta es la nueva interfaz profesional para el Generador de Videos Musicales.
    
    ### ¿Qué quieres hacer hoy?
    - **Generador:** Selecciona una canción y genera un video usando nuestros motores estables.
    - **Director IA:** Deja que nuestra IA escuche la canción, imagine la escena y elija los parámetros.
    - **Motores:** Explora el modo manual y motores experimentales (Caos, IFS, LBM).
    
    ### Instrucciones
    1. Ve a la pestaña **Generador**.
    2. Sube o selecciona tu archivo `.wav`.
    3. Ajusta los parámetros o pide sugerencias a la IA.
    4. Haz clic en generar y disfruta del arte matemático.
    """)
    
elif menu == "🎛️ Generador":
    st.title("Generador de Videos (Motores Estables)")
    
    # Subida de archivo
    audio_file = st.file_uploader("Sube tu canción (.wav, .mp3, .flac)", type=["wav", "mp3", "flac"])
    
    if audio_file is not None:
        st.audio(audio_file, format='audio/wav')
        
        col1, col2 = st.columns(2)
        with col1:
            modo_render = st.selectbox(
                "Selecciona Motor Matemático", 
                [
                    "Mix (Todos los Motores)", 
                    "Gray-Scott Puro", 
                    "Kuramoto-Sivashinsky (Fuego)",
                    "Gross-Pitaevskii (Cuántica)", 
                    "Ecuación de Ondas (Líquido)",
                    "Allen-Cahn / Ohta-Kawasaki (Burbujas)",
                    "KdV (Tsunamis)",
                    "Caos 3D (Atractores de Lorenz)",
                    "Geometría Sagrada (Fractales IFS)",
                    "Red Neuronal Rápida (CPPN)"
                ]
            )
            ui_seed = st.number_input("Semilla (Seed)", value=42)
            ui_duracion = st.number_input("Duración Test (Segundos, 0 = Canción Completa)", value=0, min_value=0, max_value=600)
            
        with col2:
            use_spirits = st.checkbox("Usar Espíritus", value=True)
            use_kaleido = st.checkbox("Efecto Caleidoscopio", value=True)
            use_flash = st.checkbox("Flash/Bloom", value=True)
            use_chroma = st.checkbox("Color por Nota Musical", value=False)
            use_lyrics = st.checkbox("Incrustar Letra (Lyrics Neón)", value=False)
            
        allowed_engines_list = None
        custom_engines_list = []
        if modo_render == "Mix (Todos los Motores)":
            with st.expander("⚙️ Modo Avanzado (Constructor de Motores)", expanded=True):
                st.markdown("Activa o desactiva ecuaciones individuales para crear tu propio ecosistema físico:")
                colA, colB = st.columns(2)
                with colA:
                    e1 = st.checkbox("Gray-Scott (Corrosión)", value=True)
                    e2 = st.checkbox("Kuramoto-Sivashinsky (Fuego)", value=True)
                    e3 = st.checkbox("Gross-Pitaevskii (Cuántica)", value=True)
                    e4 = st.checkbox("Ecuación de Ondas (Líquido)", value=True)
                with colB:
                    e5 = st.checkbox("Allen-Cahn (Burbujas)", value=True)
                    e6 = st.checkbox("KdV (Tsunamis)", value=True)
                    e7 = st.checkbox("Caos 3D (Atractores de Lorenz)", value=False)
                    e8 = st.checkbox("Geometría Sagrada (Fractales IFS)", value=False)
                    e9 = st.checkbox("Red Neuronal Rápida (CPPN)", value=True)
                
                if e1: custom_engines_list.append('GS')
                if e2: custom_engines_list.append('KS')
                if e3: custom_engines_list.append('GPE')
                if e4: custom_engines_list.append('WAVE')
                if e5: custom_engines_list.append('CH')
                if e6: custom_engines_list.append('KDV')
                if e7: custom_engines_list.append('lorenz')
                if e8: custom_engines_list.append('ifs')
                if e9: custom_engines_list.append('CPPN')
            
        # Determinar allowed_engines final basado en el selectbox principal
        if modo_render == "Mix (Todos los Motores)":
            allowed_engines_list = custom_engines_list # Usa lo que haya en avanzado
        elif modo_render == "Gray-Scott Puro":
            allowed_engines_list = ['GS']
        elif modo_render == "Kuramoto-Sivashinsky (Fuego)":
            allowed_engines_list = ['KS']
        elif modo_render == "Gross-Pitaevskii (Cuántica)":
            allowed_engines_list = ['GPE']
        elif modo_render == "Ecuación de Ondas (Líquido)":
            allowed_engines_list = ['WAVE']
        elif modo_render == "Allen-Cahn / Ohta-Kawasaki (Burbujas)":
            allowed_engines_list = ['CH']
        elif modo_render == "KdV (Tsunamis)":
            allowed_engines_list = ['KDV']
        elif modo_render == "Caos 3D (Atractores de Lorenz)":
            allowed_engines_list = ['lorenz']
        elif modo_render == "Geometría Sagrada (Fractales IFS)":
            allowed_engines_list = ['ifs']
        elif modo_render == "Red Neuronal Rápida (CPPN)":
            allowed_engines_list = ['CPPN']
        else:
            allowed_engines_list = custom_engines_list
            
        # --- NUEVO FLUJO DE RENDERIZADO CON EDITOR DE LETRAS ---
        temp_audio_path = os.path.join("temp", audio_file.name)
        temp_audio_txt = os.path.join("temp", os.path.splitext(audio_file.name)[0] + ".txt")
        
        if "lyrics_text" not in st.session_state:
            st.session_state.lyrics_text = ""
        if "lyrics_ready" not in st.session_state:
            st.session_state.lyrics_ready = False
            
        def procesar_y_renderizar(dur_val, mix_dur_val):
            st.success("Renderizando... Por favor mira la consola para ver el progreso detallado.")
            progress_bar = st.progress(0)
            
            temp_video = os.path.join("temp", "temp_render.mp4")
            final_video = os.path.join("RENDERS", f"FINAL_{audio_file.name}.mp4")
            os.makedirs("RENDERS", exist_ok=True)
            
            st.markdown("### 🖥️ Consola de Desarrollo (Logs)")
            log_box = st.empty()
            
            with st.spinner("Ejecutando simulación física (esto puede tomar tiempo)..."):
                # Activar redirección
                redirector = StreamlitLogRedirector(log_box)
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = redirector
                sys.stderr = redirector
                
                try:
                    def update_progress(current, total):
                        progress_bar.progress(int((current / total) * 100))
                        
                    success = generar_animacion_god_mode(
                        ruta_audio=temp_audio_path,
                        nombre_salida_temp=temp_video,
                        fps=30,
                        duracion=dur_val,
                        seed=ui_seed,
                        allowed_engines=allowed_engines_list,
                        use_spirits=use_spirits,
                        use_kaleido=use_kaleido,
                        use_flash=use_flash,
                        use_chroma=use_chroma,
                        use_lyrics=use_lyrics,
                        progress_callback=update_progress
                    )
                    progress_bar.progress(100)
                    
                    if success:
                        st.info("Mezclando audio con el video...")
                        unir_video_con_musica(temp_video, temp_audio_path, final_video, duracion=mix_dur_val)
                        progress_bar.progress(100)
                        st.success(f"✅ ¡Video generado con éxito! Guardado en: {final_video}")
                        st.video(final_video)
                    else:
                        st.error("Error durante el renderizado físico.")
                except Exception as e:
                    st.error(f"Excepción crítica: {str(e)}")
                finally:
                    # Desactivar redirección pase lo que pase
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

        if use_lyrics:
            st.warning("Has activado las letras. Primero debemos extraerlas y corregirlas.")
            whisper_model = st.selectbox(
                "Potencia de Transcripción (Modelo de Inteligencia Artificial)",
                ["tiny", "base", "small", "medium", "large"],
                index=3, # medium por defecto
                help="Los modelos más grandes (medium/large) son mucho más precisos con la ortografía y el tiempo, pero requieren más potencia y tiempo de cálculo."
            )
            if st.button("📝 Paso 1: Extraer Letra"):
                # Guardar el archivo subido temporalmente para Whisper
                os.makedirs("temp", exist_ok=True)
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                    
                st.markdown("### 🖥️ Consola de Extracción (IA)")
                log_box_letra = st.empty()
                progress_bar_letra = st.progress(0)
                
                # Activar redirección de logs también para la extracción
                redirector_letra = StreamlitLogRedirector(log_box_letra)
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = redirector_letra
                sys.stderr = redirector_letra
                
                texto_extraido = ""
                try:
                    import threading
                    import time
                    
                    res_container = []
                    def run_extraction():
                        res_container.append(transcribir_audio_para_edicion(
                            temp_audio_path, 
                            model_size=whisper_model,
                            max_duration=ui_duracion
                        ))
                    
                    t = threading.Thread(target=run_extraction)
                    # Añadir contexto de Streamlit al hilo para evitar "missing ScriptRunContext"
                    try:
                        add_script_run_ctx(t)
                    except Exception:
                        pass
                    t.start()
                    
                    # Barra de progreso simulada inteligente
                    prog = 0
                    while t.is_alive():
                        time.sleep(0.5)
                        prog += 1
                        if prog > 95: prog = 95
                        progress_bar_letra.progress(prog)
                        
                    t.join()
                    progress_bar_letra.progress(100)
                    texto_extraido = res_container[0] if res_container else "Error desconocido."
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    st.session_state.lyrics_text = texto_extraido
                    st.session_state.lyrics_ready = True
            
            if st.session_state.lyrics_ready:
                st.info("Corrige cualquier error en la letra antes de renderizar:")
                texto_editado = st.text_area("Editor de Letras (Revisa y aprueba):", value=st.session_state.lyrics_text, height=250)
                
                if st.button("🚀 Paso 2: Aprobar Letra y Renderizar Video"):
                    # Guardar el archivo .txt para que el motor físico lo alinee
                    with open(temp_audio_txt, "w", encoding="utf-8") as f:
                        f.write(texto_editado)
                    
                    dur_val = ui_duracion if ui_duracion > 0 else None
                    procesar_y_renderizar(dur_val, dur_val)
                    
        else:
            if st.button("🚀 Renderizar Video"):
                # Guardar el archivo subido temporalmente
                os.makedirs("temp", exist_ok=True)
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                dur_val = ui_duracion if ui_duracion > 0 else None
                procesar_y_renderizar(dur_val, dur_val)

elif menu == "🎬 Director IA":
    st.title("Director IA (Deep Learning)")
    st.markdown("Delega el montaje visual y la sincronización a nuestra red neuronal.")
    
    audio_file_ia = st.file_uploader("Sube tu canción para el Montaje (.wav, .mp3, .flac)", type=["wav", "mp3", "flac"], key="ia_audio")
    clips_folder = st.text_input("Carpeta origen de clips generados (Opcional):", placeholder="Ej: RENDERS o deja vacío para escanear todo")
    duration_ia = st.number_input("Duración Test (Segundos, 0 = Completo)", value=0, min_value=0, max_value=600, key="ia_dur")
    
    if st.button("✨ Iniciar Montaje Automático"):
        if audio_file_ia is None:
            st.error("Debes subir una canción para iniciar el montaje.")
        else:
            # Guardar el archivo subido temporalmente
            temp_audio_path_ia = os.path.join("temp", audio_file_ia.name)
            os.makedirs("temp", exist_ok=True)
            with open(temp_audio_path_ia, "wb") as f:
                f.write(audio_file_ia.getbuffer())
                
            progress_bar_ia = st.progress(0)
            status_text = st.empty()
            
            def update_progress_ia(percent, message):
                progress_bar_ia.progress(percent)
                status_text.text(message)
                
            with st.spinner("El Director IA está analizando los clips mediante PyTorch..."):
                try:
                    from ai.director_ai import generar_montaje_ia
                    final_out = os.path.join("RENDERS", f"IA_DIRECTOR_{audio_file_ia.name}.mp4")
                    os.makedirs("RENDERS", exist_ok=True)
                    
                    dur_arg = duration_ia if duration_ia > 0 else None
                    cdir_arg = clips_folder if clips_folder.strip() != "" else None
                    
                    res = generar_montaje_ia(
                        audio_path=temp_audio_path_ia, 
                        duration_arg=dur_arg, 
                        clips_dir_arg=cdir_arg,
                        output_filename=final_out,
                        progress_callback=update_progress_ia
                    )
                    
                    if res:
                        st.success(f"✅ ¡Montaje Épico completado! Guardado en {res}")
                        st.video(res)
                    else:
                        st.error("El Director IA no pudo completar el montaje. Asegúrate de tener clips renderizados preexistentes en la carpeta.")
                except Exception as e:
                    st.error(f"Excepción en el Director IA: {e}")

elif menu == "🧪 Motores":
    st.title("Motores Experimentales")
    st.warning("⚠️ Estos motores están en desarrollo y pueden ser inestables.")
    st.selectbox("Motores", ["Caos 3D (Lorenz/Atractores)", "Fractales (IFS)", "Ecuaciones Inestables"])

elif menu == "📚 Academia Matemática":
    st.title("Academia Matemática Cósmica 📚")
    st.markdown("Bienvenido al centro de aprendizaje matemático de la Cooperativa. Aquí podrás estudiar la física real detrás de nuestras simulaciones.")
    
    # Cargar reporte del agente
    try:
        with open("data/reporte_matematico.md", "r", encoding="utf-8") as f:
            reporte = f.read()
        st.markdown(reporte, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("El reporte matemático aún se está generando o no se encontró el archivo. Por favor espera unos minutos e intenta nuevamente.")

elif menu == "🧪 Laboratorio de Física":
    st.title("Laboratorio de Simulación (Sin Música)")
    st.markdown("Modo de simulación puramente física. No requiere canciones. Se inyectan perturbadores matemáticos sintéticos para observar la dinámica canónica de los sistemas fluidos y de reacción-difusión.")
    
    col1, col2 = st.columns(2)
    with col1:
        motor_lab = st.selectbox(
            "Selecciona Sistema Físico:", 
            [
                "Gray-Scott Puro", 
                "Kuramoto-Sivashinsky (Fuego)",
                "Gross-Pitaevskii (Cuántica)", 
                "Ecuación de Ondas (Líquido)",
                "Allen-Cahn / Ohta-Kawasaki (Burbujas)",
                "KdV (Tsunamis)",
                "Caos 3D (Atractores de Lorenz)",
                "Geometría Sagrada (Fractales IFS)",
                "Red Neuronal Rápida (CPPN)"
            ]
        )
        duracion_lab = st.number_input("Duración de Simulación (Segundos)", value=10, min_value=1, max_value=60)
        seed_lab = st.number_input("Semilla Inicial (Seed)", value=42)
    
    with col2:
        st.info("Variables de entorno Matemático")
        
        # Diccionario de ecuaciones LaTeX
        ecuaciones_latex = {
            "Gray-Scott Puro": r'''
            \begin{align*}
            \frac{\partial u}{\partial t} &= D_u \nabla^2 u - u v^2 + F(1-u) \\
            \frac{\partial v}{\partial t} &= D_v \nabla^2 v + u v^2 - (F+k)v
            \end{align*}
            ''',
            "Kuramoto-Sivashinsky (Fuego)": r'''
            \frac{\partial u}{\partial t} + \nabla^4 u + \nabla^2 u + \frac{1}{2}|\nabla u|^2 = 0
            ''',
            "Gross-Pitaevskii (Cuántica)": r'''
            i\hbar \frac{\partial \psi}{\partial t} = \left(-\frac{\hbar^2}{2m}\nabla^2 + V(r) + g|\psi|^2 \right)\psi
            ''',
            "Ecuación de Ondas (Líquido)": r'''
            \frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u - \gamma \frac{\partial u}{\partial t}
            ''',
            "Allen-Cahn / Ohta-Kawasaki (Burbujas)": r'''
            \frac{\partial u}{\partial t} = \nabla \cdot (M \nabla \mu) - \gamma (u - \overline{u}), \quad \mu = u^3 - u - \nabla^2 u
            ''',
            "KdV (Tsunamis)": r'''
            \frac{\partial u}{\partial t} + \alpha u \frac{\partial u}{\partial x} + \beta \frac{\partial^3 u}{\partial x^3} = 0
            ''',
            "Caos 3D (Atractores de Lorenz)": r'''
            \begin{align*}
            \dot{x} &= \sigma(y-x) \\
            \dot{y} &= x(\rho-z)-y \\
            \dot{z} &= xy-\beta z
            \end{align*}
            ''',
            "Geometría Sagrada (Fractales IFS)": r'''
            W_i(x) = A_i x + b_i, \quad P(x \to W_i(x)) = p_i
            ''',
            "Red Neuronal Rápida (CPPN)": r'''
            f_{CPPN}(x, y, r, t, z) = \sigma(W_n \dots \sigma(W_1 \vec{v} + b_1) \dots + b_n)
            '''
        }
        
        # Diccionario de Espacio de Fases (Límites Simulables)
        espacio_fases = {
            "Gray-Scott Puro": "Espacio de Fases Estables: F ∈ [0.01, 0.06], k ∈ [0.03, 0.07]",
            "Kuramoto-Sivashinsky (Fuego)": "Restricción de Estabilidad: dt < 0.01 (CFL condition)",
            "Gross-Pitaevskii (Cuántica)": "Condición: Conservación de |ψ|^2 = 1.0",
            "Ecuación de Ondas (Líquido)": "Límites Courant: c * dt / dx <= 1",
            "Allen-Cahn / Ohta-Kawasaki (Burbujas)": "Estabilidad: Movilidad M < 0.1, dt < 0.05",
            "KdV (Tsunamis)": "Espacio Solitónico: α > 0, β > 0. Si β < 0 -> Choque inelástico.",
            "Caos 3D (Atractores de Lorenz)": "Rango Caótico Estándar: σ=10, β=8/3, ρ=28",
            "Geometría Sagrada (Fractales IFS)": "Restricción Contractiva: det(A_i) < 1",
            "Red Neuronal Rápida (CPPN)": "Espacio Latente (Z): Normalizado entre -1.0 y 1.0"
        }
        
        st.markdown("### Ecuación Diferencial Canónica")
        st.latex(ecuaciones_latex.get(motor_lab, ""))
        
        st.markdown("### Espacio de Fases (Validación Numérica)")
        st.warning(espacio_fases.get(motor_lab, ""))
        st.markdown("- Ruido Estocástico: ON")
        st.markdown("- Perturbador de Frecuencia: Oscilador Senoidal (0.5 Hz)")
        st.markdown("- Renderizado: God Mode V2 (Numba + Multi-Threading)")
        
    if st.button("🔬 Iniciar Simulación de Laboratorio", type="primary"):
        from render.stable.render_standard import generar_animacion_god_mode
        import os
        
        temp_video_lab = "temp_lab_simulation.mp4"
        
        # Mapear motor
        lab_engines = []
        if motor_lab == "Gray-Scott Puro": lab_engines = ['GS']
        elif motor_lab == "Kuramoto-Sivashinsky (Fuego)": lab_engines = ['KS']
        elif motor_lab == "Gross-Pitaevskii (Cuántica)": lab_engines = ['GPE']
        elif motor_lab == "Ecuación de Ondas (Líquido)": lab_engines = ['WAVE']
        elif motor_lab == "Allen-Cahn / Ohta-Kawasaki (Burbujas)": lab_engines = ['CH']
        elif motor_lab == "KdV (Tsunamis)": lab_engines = ['KDV']
        elif motor_lab == "Caos 3D (Atractores de Lorenz)": lab_engines = ['lorenz']
        elif motor_lab == "Geometría Sagrada (Fractales IFS)": lab_engines = ['ifs']
        elif motor_lab == "Red Neuronal Rápida (CPPN)": lab_engines = ['CPPN']
        
        progress_bar_lab = st.progress(0)
        def update_progress_lab(current, total):
            progress_bar_lab.progress(int((current / total) * 100))
            
        with st.spinner(f"Calculando campos para {motor_lab}..."):
            try:
                success = generar_animacion_god_mode(
                    ruta_audio=None, # Indicador para modo de simulación pura
                    nombre_salida_temp=temp_video_lab,
                    fps=30,
                    duracion=duracion_lab,
                    seed=seed_lab,
                    allowed_engines=lab_engines,
                    use_spirits=False,
                    use_kaleido=False,
                    use_flash=False,
                    use_chroma=False,
                    use_lyrics=False,
                    global_cmap=None,
                    progress_callback=update_progress_lab
                )
                
                if success and os.path.exists(temp_video_lab):
                    st.success("Simulación finalizada. Renderización en alta calidad.")
                    st.video(temp_video_lab)
                else:
                    st.error("Hubo un fallo crítico en la simulación física.")
            except Exception as e:
                st.error(f"Error en la simulación: {str(e)}")

elif menu == "⚙️ Configuración":
    st.title("Configuración Global")
    st.selectbox("Resolución de Salida", ["1920x1080 (FHD)", "1280x720 (HD)", "640x360 (SD)"])
    st.number_input("FPS (Frames por segundo)", value=30, min_value=15, max_value=60)
    st.text_input("Ruta de Guardado", value="RENDERS/")
