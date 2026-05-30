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
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

class StreamlitLogRedirector:
    """Redirige stdout y stderr a un elemento de Streamlit en tiempo real de forma segura (Thread-Safe)."""
    def __init__(self, st_empty_element):
        self.st_empty_element = st_empty_element
        self.text = ""
        self.terminal = sys.stdout
        self.last_update = 0
    def write(self, msg):
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
        ["🏠 Inicio", "🎛️ Generador", "🎬 Director IA", "🧪 Motores", "⚙️ Configuración"]
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
            st.selectbox("Selecciona Motor Matemático", ["God Mode (Estándar)", "Main Clásico", "Lenia (Vida Artificial)", "LBM (Fluidos)"])
            ui_seed = st.number_input("Semilla (Seed)", value=42)
            ui_duracion = st.number_input("Duración Test (Segundos, 0 = Canción Completa)", value=0, min_value=0, max_value=600)
            
        with col2:
            use_spirits = st.checkbox("Usar Espíritus", value=True)
            use_kaleido = st.checkbox("Efecto Caleidoscopio", value=True)
            use_flash = st.checkbox("Flash/Bloom", value=True)
            use_chroma = st.checkbox("Color por Nota Musical", value=False)
            use_lyrics = st.checkbox("Incrustar Letra (Lyrics Neón)", value=False)
            
        allowed_engines_dict = None
        with st.expander("⚙️ Modo Avanzado (Constructor de Motores)"):
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
            
            allowed_engines_dict = {
                'gray_scott': e1, 'ks': e2, 'gpe': e3, 'ondas': e4,
                'cahn_hilliard': e5, 'kdv': e6, 'lorenz': e7, 'ifs': e8
            }
            
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
                        allowed_engines=allowed_engines_dict,
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
                        res_container.append(transcribir_audio_para_edicion(temp_audio_path, model_size=whisper_model))
                    
                    t = threading.Thread(target=run_extraction)
                    # Añadir contexto de Streamlit al hilo para evitar "missing ScriptRunContext"
                    try:
                        from streamlit.runtime.scriptrunner import add_script_run_ctx
                        add_script_run_ctx(t)
                    except ImportError:
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

elif menu == "⚙️ Configuración":
    st.title("Configuración Global")
    st.selectbox("Resolución de Salida", ["1920x1080 (FHD)", "1280x720 (HD)", "640x360 (SD)"])
    st.number_input("FPS (Frames por segundo)", value=30, min_value=15, max_value=60)
    st.text_input("Ruta de Guardado", value="RENDERS/")
