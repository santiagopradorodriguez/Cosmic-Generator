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
        
    def isatty(self):
        return False
        
    @property
    def encoding(self):
        return getattr(self.terminal, 'encoding', 'utf-8')

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
        ["🏠 Inicio", "🎛️ Generador", "🎬 Director IA", "🧪 Motores", "🎧 Separador de Stems", "⚙️ Configuración", "📚 Academia Matemática", "🧪 Laboratorio de Física", "🎵 Nihil Morari (Álbum)"]
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
    
    ### 🌟 Novedades (V2.1)
    - **Cromestesia Global:** La IA ahora extrae la "Tonalidad Reina" de toda la canción (ej. Do Mayor, Sol Menor) y fuerza una paleta emocional a todos los motores físicos (Otoño, Océano, Fuego, etc). ¡El color ya no rota caóticamente!
    - **Modo Sinestesia (Multi-Stems):** Separación neuronal de pistas. La batería controla el caos y la cámara, la voz brilla las letras, y los sintetizadores mutan la geometría sagrada.
    - **Estabilidad Matemática:** Se parchó la explosión numérica del motor de Redes Neuronales (CPPN). ¡Adiós errores NaN!
    
    ### Instrucciones
    1. Ve a la pestaña **Generador**.
    2. Sube o selecciona tu archivo `.wav` (o usa la pestaña **Separador de Stems** primero).
    3. Ajusta los parámetros o pide sugerencias a la IA.
    4. Haz clic en generar y disfruta del arte matemático.
    """)
    
    st.markdown("---")
    st.markdown("### 🎬 Última Creación (Showcase)")
    import glob
    import os
    renders_dir = "RENDERS"
    if os.path.exists(renders_dir):
        videos = glob.glob(os.path.join(renders_dir, "*.mp4"))
        if videos:
            latest_video = max(videos, key=os.path.getctime)
            st.markdown(f"**Viendo:** `{os.path.basename(latest_video)}`")
            st.video(latest_video)
        else:
            st.info("Aún no has renderizado ningún video. ¡Ve al Generador para crear el primero!")
    else:
        st.info("Aún no has renderizado ningún video. ¡Ve al Generador para crear el primero!")
        
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
                    "Cahn-Hilliard Clásico (Aceite y Agua)",
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
            use_chroma = st.checkbox("Activar Cromestesia Global (Color por Vibra de la Canción)", value=False)
            use_stems = st.checkbox("Modo Sinestesia (Usar Stems si existen)", value=False, help="Si ya usaste el Separador de Pistas, la física reaccionará de forma independiente a cada instrumento.")
            use_lyrics = st.checkbox("Incrustar Letra (Lyrics Neón)", value=False)
            lyrics_pos = "Abajo"
            if use_lyrics:
                lyrics_pos = st.radio("Posición de la Letra", ["Abajo", "Centro"], horizontal=True)
            
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
                    e5b = st.checkbox("Cahn-Hilliard Clásico", value=True)
                    e6 = st.checkbox("KdV (Tsunamis)", value=True)
                    e7 = st.checkbox("Caos 3D (Atractores de Lorenz)", value=False)
                    e8 = st.checkbox("Geometría Sagrada (Fractales IFS)", value=False)
                    e9 = st.checkbox("Red Neuronal Rápida (CPPN)", value=True)
                
                if e1: custom_engines_list.append('GS')
                if e2: custom_engines_list.append('KS')
                if e3: custom_engines_list.append('GPE')
                if e4: custom_engines_list.append('WAVE')
                if e5: custom_engines_list.append('OK')
                if e5b: custom_engines_list.append('CH')
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
            allowed_engines_list = ['OK']
        elif modo_render == "Cahn-Hilliard Clásico (Aceite y Agua)":
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
                        lyrics_pos=lyrics_pos,
                        use_stems=use_stems,
                        stem_folder=os.path.join(os.getcwd(), "STEMS", "htdemucs", os.path.splitext(audio_file.name)[0]),
                        progress_callback=update_progress
                    )
                    progress_bar.progress(100)
                    
                    if success:
                        st.info("Mezclando audio con el video...")
                        unir_video_con_musica(temp_video, temp_audio_path, final_video, duracion=mix_dur_val)
                        progress_bar.progress(100)
                        st.success(f"✅ ¡Video generado con éxito! Guardado en: {final_video}")
                        st.video(final_video)
                        with open(final_video, "rb") as file:
                            st.download_button(
                                label="💾 Descargar Video Generado",
                                data=file,
                                file_name=os.path.basename(final_video),
                                mime="video/mp4"
                            )
                    else:
                        st.error("Error durante el renderizado físico.")
                except Exception as e:
                    st.error(f"Excepción crítica: {str(e)}")
                finally:
                    # Desactivar redirección pase lo que pase
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

        if use_lyrics:
            st.warning("Opciones de Letras (Lyrics)")
            modo_letra = st.radio(
                "¿Cómo quieres sincronizar la letra?", 
                ["📝 Extraer con IA (No tengo la letra)", "🎯 Alineación Forzada (Pegar Letra Original)"]
            )
            
            if modo_letra == "📝 Extraer con IA (No tengo la letra)":
                st.info("La IA adivinará la letra desde cero. Primero debemos extraerla y luego podrás corregirla.")
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
                        import time
                        print("Iniciando transcripción con IA... (Esto puede tomar varios minutos)")
                        progress_bar_letra.progress(10)
                        
                        texto_extraido = transcribir_audio_para_edicion(
                            temp_audio_path, 
                            model_size=whisper_model,
                            max_duration=ui_duracion
                        )
                        
                        progress_bar_letra.progress(100)
                        print("¡Extracción completada con éxito!")
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
                st.info("Pega tu letra oficial aquí. La IA usará exactamente estas palabras y solo buscará en qué milisegundo se pronuncian para lograr una sincronización perfecta.")
                texto_original = st.text_area("Letra Original de la Canción:", height=300, help="Asegúrate de que la letra esté completa e incluya todas las partes cantadas.")
                if st.button("🚀 Sincronizar Letra y Renderizar Video"):
                    if texto_original.strip() == "":
                        st.error("¡Por favor, pega la letra original en la caja de texto antes de continuar!")
                    else:
                        # Escribimos el .txt
                        with open(temp_audio_txt, "w", encoding="utf-8") as f:
                            f.write(texto_original.strip())
                        
                        # También tenemos que asegurar que el audio se extraiga para el engine
                        os.makedirs("temp", exist_ok=True)
                        with open(temp_audio_path, "wb") as f:
                            f.write(audio_file.getbuffer())
                            
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
                        with open(res, "rb") as file:
                            st.download_button(
                                label="💾 Descargar Montaje IA",
                                data=file,
                                file_name=os.path.basename(res),
                                mime="video/mp4"
                            )
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

elif menu == "🎧 Separador de Stems":
    st.title("Separador de Pistas (Stems) 🎧")
    st.markdown("""
    Utiliza IA (**Demucs de Meta**) para separar tu canción en **Batería, Bajo, Voces y Otros**.
    *Nota: Si es la primera vez que lo usas, descargará automáticamente el modelo preentrenado (puede tardar unos minutos).*
    """)
    
    audio_file = st.file_uploader("Sube tu canción (.wav, .mp3, .flac)", type=["wav", "mp3", "flac"], key="stem_uploader")
    
    if audio_file is not None:
        st.audio(audio_file, format='audio/wav')
        
        if st.button("Separar Pistas (4 Stems)", type="primary"):
            with st.spinner("Instalando dependencias e inicializando Demucs..."):
                import subprocess
                import sys
                
                # Verificar e instalar demucs si no existe
                try:
                    import demucs
                except ImportError:
                    st.info("Instalando Demucs... (esto solo ocurre una vez)")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "demucs"])
                    st.success("Demucs instalado. Comenzando separación...")
            
            with st.spinner("Separando audio en Batería, Bajo, Voces y Otros... (Esto tomará tiempo)"):
                # Guardar temp file forzando conversión a WAV puro (PCM_16)
                import tempfile
                import librosa
                import soundfile as sf
                
                y, sr = librosa.load(audio_file, sr=None)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    temp_audio_path = tmp_file.name
                    
                sf.write(temp_audio_path, y, sr, subtype='PCM_16')
                
                # Ejecutar comando demucs
                stem_output_dir = os.path.join(os.getcwd(), "STEMS")
                os.makedirs(stem_output_dir, exist_ok=True)
                
                try:
                    # Usar script wrapper propio para evitar el bug de torchaudio en Windows
                    script_wrapper = os.path.join(os.getcwd(), "run_demucs.py")
                    cmd = [sys.executable, script_wrapper, "-n", "htdemucs", "-o", stem_output_dir, temp_audio_path]
                    
                    # Ejecución interactiva para barra de carga en vivo
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
                    
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()
                    status_text.text("Iniciando motores de IA...")
                    
                    for line in process.stdout:
                        if "%|" in line:
                            try:
                                pct_str = line.split("%|")[0].strip()
                                pct = min(float(pct_str) / 100.0, 1.0)
                                progress_bar.progress(pct)
                                status_text.text(f"Decodificando y separando frecuencias: {int(pct*100)}%")
                            except:
                                pass
                                
                    process.wait()
                    if process.returncode == 0:
                        progress_bar.progress(1.0)
                        status_text.text("¡Completado!")
                        st.success("¡Separación completada con éxito!")
                        st.balloons()
                        
                        # Mostrar rutas
                        base_name = os.path.splitext(os.path.basename(temp_audio_path))[0]
                        folder_path = os.path.join(stem_output_dir, "htdemucs", base_name)
                        st.markdown(f"**Tus stems están guardados en:** `{folder_path}`")
                        
                        st.info("Abre esa carpeta en tu explorador de archivos para ver 'drums.wav', 'bass.wav', 'vocals.wav' y 'other.wav'.")
                    else:
                        st.error(f"Error al separar pistas. Revisa la consola para más detalles. (Exit Code: {process.returncode})")
                        
                except Exception as e:
                    st.error(f"Error crítico durante la separación: {e}")
                finally:
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)

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
                "Cahn-Hilliard Clásico (Aceite y Agua)",
                "KdV (Tsunamis)",
                "Caos 3D (Atractores de Lorenz)",
                "Atractor de Clifford (Caos 2D)",
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
            **Ecuación de Ohta-Kawasaki (Frustración Topológica):**
            $$ \frac{\partial u}{\partial t} = M(\nabla^2 \mu) - \sigma(u - \bar{u}) $$
            $$ \mu = u^3 - u - \gamma \nabla^2 u $$
            *Dinámica:* El término $\sigma$ fuerza la formación de burbujas pequeñas o laberintos repulsivos, simulando membranas celulares estables.
            ''',
            "Cahn-Hilliard Clásico (Aceite y Agua)": r'''
            **Ecuación de Cahn-Hilliard:**
            $$ \frac{\partial u}{\partial t} = \nabla \cdot (M \nabla \mu) $$
            $$ \mu = u^3 - u - \gamma \nabla^2 u $$
            *Dinámica:* Modela la separación de fases termodinámica. Las manchas se agrupan libremente formando manchas gigantes y fluidas.
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
            "Atractor de Clifford (Caos 2D)": r'''
            \begin{align*}
            x_{n+1} &= \sin(a y_n) + c \cos(a x_n) \\
            y_{n+1} &= \sin(b x_n) + d \cos(b y_n)
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
            "Ecuación de Ondas (Líquido)": "Estabilidad: Damping < 1.0, c² < 0.5",
            "Allen-Cahn / Ohta-Kawasaki (Burbujas)": "Estabilidad: Movilidad M < 0.1, dt < 0.05",
            "Cahn-Hilliard Clásico (Aceite y Agua)": "Estabilidad: Movilidad M < 0.1, dt < 0.05",
            "KdV (Tsunamis)": "Estabilidad: alpha pequeño, beta < 0.01",
            "Caos 3D (Atractores de Lorenz)": "Rango Caótico Estándar: σ=10, β=8/3, ρ=28",
            "Atractor de Clifford (Caos 2D)": "Parámetros Estándar: a=-1.4, b=1.6, c=1.0, d=0.7",
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
        st.info("Laboratorio Puro de Sistemas Complejos: Evaluando Ecuación en Derivadas Parciales (Determinista)...")
        
        # Desacople total: Importar el simulador puro en lugar del motor audiovisual
        from render.stable.render_laboratorio import simular_laboratorio_puro
        import os
        
        temp_video_lab = "temp_lab_simulation.mp4"
        
        # Mapear motor
        lab_engines = []
        if motor_lab == "Gray-Scott Puro": lab_engines = ['GS']
        elif motor_lab == "Kuramoto-Sivashinsky (Fuego)": lab_engines = ['KS']
        elif motor_lab == "Gross-Pitaevskii (Cuántica)": lab_engines = ['GPE']
        elif motor_lab == "Ecuación de Ondas (Líquido)": lab_engines = ['WAVE']
        elif motor_lab == "Allen-Cahn / Ohta-Kawasaki (Burbujas)": lab_engines = ['OK']
        elif motor_lab == "Cahn-Hilliard Clásico (Aceite y Agua)": lab_engines = ['CH']
        elif motor_lab == "KdV (Tsunamis)": lab_engines = ['KDV']
        elif motor_lab == "Caos 3D (Atractores de Lorenz)": lab_engines = ['lorenz']
        elif motor_lab == "Atractor de Clifford (Caos 2D)": lab_engines = ['CLIFFORD']
        elif motor_lab == "Geometría Sagrada (Fractales IFS)": lab_engines = ['ifs']
        elif motor_lab == "Red Neuronal Rápida (CPPN)": lab_engines = ['CPPN']
        
        engine_code = lab_engines[0] if lab_engines else 'GS'
        
        progress_bar_lab = st.progress(0)
        def update_progress_lab(current, msg=""):
            progress_bar_lab.progress(current)
            
        with st.spinner(f"Calculando evolución determinista para {engine_code}..."):
            try:
                success = simular_laboratorio_puro(
                    nombre_salida=temp_video_lab,
                    fps=30,
                    duracion=duracion_lab,
                    seed=seed_lab,
                    engine_code=engine_code,
                    progress_callback=update_progress_lab
                )
                
                if success and os.path.exists(temp_video_lab):
                    st.success("✅ Simulación rigurosa completada.")
                    st.video(temp_video_lab)
                    with open(temp_video_lab, "rb") as file:
                        st.download_button(
                            label="💾 Descargar Simulación",
                            data=file,
                            file_name=os.path.basename(temp_video_lab),
                            mime="video/mp4"
                        )
                else:
                    st.error("Error al generar la simulación determinista.")
            except Exception as e:
                st.error(f"Error Crítico Numérico: {e}")

elif menu == "⚙️ Configuración":
    st.title("Configuración Global")
    st.selectbox("Resolución de Salida", ["1920x1080 (FHD)", "1280x720 (HD)", "640x360 (SD)"])
    st.number_input("FPS (Frames por segundo)", value=30, min_value=15, max_value=60)
    st.text_input("Ruta de Guardado", value="RENDERS/")

elif menu == "🎵 Nihil Morari (Álbum)":
    st.title("🎵 Nihil Morari - Rebeldía Cósmica")
    st.write("*Rebeldía Cósmica es un proyecto musical latinoamericano que mezcla rock progresivo y experimental con synth-pop, heavy metal, salsa y más. Sus canciones forman parte de un álbum conceptual que explora temas como el nihilismo, la conciencia y el cosmos.*")
    st.markdown("### Escucha el álbum completo aquí:")
    st.markdown("[▶️ **Rebeldía Cósmica en Bandcamp: Nihil Morari**](https://rebeldiacosmica.bandcamp.com/album/nihil-morari-2)", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('''
"Nihil Morari" es una obra que trasciende las fronteras de la música para llevar al oyente a un viaje introspectivo y filosófico a través de las profundidades de la condición humana y el vasto cosmos que nos rodea. Consta de doce pistas, cada una de ellas una exploración profunda de temas que abarcan desde el miedo y la soledad hasta la mortalidad y la búsqueda de significado en un universo en constante expansión.

Este álbum desafía la musica convencional y nos invita a explorar al ser humano desde su posición en el cosmos. Cada canción es un portal a un mundo de reflexión filosófica y autoexploración. Si buscas una experiencia musical que te haga reflexionar sobre tu lugar en el universo y la complejidad de la existencia humana, este álbum es una elección recomendada. Su diversidad de géneros y letras lo convierten en una obra, capaz de dejarte asombrado y con una profunda apreciación por la vastedad del cosmos y la profundidad de la mente humana.

Invita a los oyentes a explorar temas existenciales y filosóficos profundos. A lo largo del álbum, el astronauta protagonista emprende un viaje introspectivo en busca de respuestas sobre la vida, la muerte, el tiempo y el universo. Cada canción aporta una perspectiva única a esta odisea cósmica, creando una narrativa emocionante y reflexiva.
''')
    
    st.info("**Géneros Musicales:** Dream Pop, Ambient, Neopsicodelia, Art Rock, Electropop, Synth-Pop, Rock Electrónico, Drum and Bass, Emo, Avant-Garde Pop, Folk, Psicodelia, Rock Progresivo, Post-Rock, Space Rock, Hard Rock, Art Rock, Soft Rock, Hip-Hop, Latin, Metal Progresivo.")
    
    st.markdown("---")
    st.markdown("### Créditos")
    st.markdown("""
*Released April 2, 2024*

- **Guitarras:** Santiago Prado, Emanuel Prado
- **Voces:** Santiago Prado, Emanuel Prado
- **Sintetizadores:** Santiago Prado
- **Batería:** Alejandro Viñales
- **Productor:** Santiago Prado
- **Diseño de Tapa:** Sofía Martínez
    """)
