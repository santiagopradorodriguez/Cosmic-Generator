# 🌌 REBELDÍA CÓSMICA: MANUAL MAESTRO DEFINITIVO V2.0
## Enciclopedia Técnica y Física Arquitectónica

*(Documento generado automáticamente a partir del código fuente para garantizar 100% de precisión sin alucinaciones de IA)*


---

## 📚 ÍNDICE GENERAL
1. **Introducción y Filosofía del Proyecto**
2. **Arquitectura Principal (App & Core)**
3. **Motores Físicos y Matemáticos (Alta y Baja Energía)**
4. **Motor de Relatividad General (Lentes Gravitacionales)**
5. **Procesamiento de Audio e Inteligencia Artificial (Demucs/Whisper)**
6. **Cromestesia y Renderizado (OpenCV)**
7. **Referencia Completa del Código Fuente (API)**


## 1. Introducción
Cosmic Generator V2 es un motor audiovisual basado puramente en CPU, diseñado para renderizar ecuaciones diferenciales no lineales, física de fluidos, fractales y relatividad general al ritmo de la música. Todo el procesamiento está optimizado con Numba (Just-In-Time Compiler) y Numpy.

## 2. Arquitectura Principal
El pipeline se divide en tres fases críticas:
1. **Análisis:** Extracción de Stems (Meta Demucs), Detección de Transitorios (Librosa) y Transcripción (Whisper).
2. **Simulación:** Integración numérica de Ecuaciones en Derivadas Parciales (PDEs) como Gray-Scott, Kuramoto-Sivashinsky, y Cahn-Hilliard.
3. **Composición:** Mezcla aditiva de buffers en OpenCV con Tone Mapping, Datamoshing y desenfoque direccional.

## 3. Diccionario Exahustivo de Módulos (Auto-Documentado)

### 📄 Módulo: `app.py`
---

**Descripción del Módulo:**
> (C) Rebeldía Cósmica | Creado por Santiago Prado

#### 📦 Clase: `StreamlitLogRedirector`
Redirige stdout y stderr a un elemento de Streamlit en tiempo real de forma segura (Thread-Safe).

- **Método:** `__init__(self, st_empty_element)`
- **Método:** `write(self, msg)`
- **Método:** `flush(self)`
- **Método:** `isatty(self)`
- **Método:** `encoding(self)`


#### ⚙️ Función: `local_css(file_name)`


### 📄 Módulo: `efectos_visuales copy 2.py`
---

#### 📦 Clase: `CamaraVirtual`
- **Método:** `__init__(self, width, height)`
- **Método:** `update(self, energy, kick, snare)`
- **Método:** `aplicar(self, frame)`


#### 📦 Clase: `PostFX`
- **Método:** `__init__(self)`
- **Método:** `feedback_temporal(self, frame, decay)`
  - *Crea estelas de luz mezclando el frame anterior. Da una sensación de fluidez y 'sueño'.*
- **Método:** `aberracion_cromatica(frame, intensidad)`
- **Método:** `bloom(frame, threshold, intensidad)`
  - *Brillo etéreo. Solo afecta a los píxeles más brillantes que el threshold.*
- **Método:** `ruido_grain(frame, cantidad)`




### 📄 Módulo: `efectos_visuales copy.py`
---

#### ⚙️ Función: `simulacion_gray_scott(U, V, Du, Dv, f, k, dt)`
Modelado de patrones de Turing y Morfogénesis.

#### ⚙️ Función: `simulacion_ondas(u, u_prev, damping, c2_dt2)`
Resuelve la ecuación de ondas discretizada: U_tt = c^2 * Lap(U)
Ideal para visualizar interferencias y acústica visual.

#### ⚙️ Función: `simulacion_kuramoto(phases, omega, K, dt, width, height)`
Simulación de osciladores acoplados en una red (Lattice).
dθ_i/dt = ω_i + K * Σ sin(θ_j - θ_i)

#### 📦 Clase: `MotorFX`
- **Método:** `__init__(self, w, h)`
- **Método:** `aplicar_bloom(self, img, intensity, threshold)`
- **Método:** `aberracion_cromatica(self, img, strength)`
- **Método:** `noise_grain(self, img, amount)`
- **Método:** `feedback_temporal(self, current_frame, decay)`




### 📄 Módulo: `fix_imports_script.py`
---



### 📄 Módulo: `fix_tex.py`
---



### 📄 Módulo: `lanzador.py`
---

#### 📦 Clase: `VisualizerLauncher`
- **Método:** `__init__(self, root)`
- **Método:** `start_ai_server(self)`
  - *Inicia el servidor FastAPI en un hilo separado si no está corriendo.*
- **Método:** `listen_voice(self)`
  - *Escucha el micrófono y transcribe a texto.*
- **Método:** `log_to_chat(self, sender, message)`
  - *Escribe un mensaje en la ventana de chat.*
- **Método:** `log_stream_start(self, sender)`
  - *Inicia una línea de chat para streaming.*
- **Método:** `log_stream_chunk(self, text)`
  - *Añade un fragmento de texto al chat actual.*
- **Método:** `log_stream_end(self)`
  - *Finaliza la línea de chat.*
- **Método:** `apply_ai_config(self, prompt_override, callback)`
  - *Envía el prompt a la IA y configura los checkboxes.*
- **Método:** `_update_gui_from_ai(self, engines, explanation, colors, render_modes, objects)`
- **Método:** `select_file(self)`
- **Método:** `extract_lyrics(self, callback, confirm)`
  - *Fuerza la extracción de letra usando Whisper (abre consola nueva).*
- **Método:** `edit_lyrics(self, wait)`
  - *Abre una ventana interna para editar la letra y tiempos (.json).*
- **Método:** `beautify_lyrics_ai(self, callback)`
  - *Lee el JSON actual, manda el texto a la IA y lo actualiza.*
- **Método:** `generate_seed(self)`
- **Método:** `update_config_file(self, event)`
  - *Edita src/config.py con la resolución seleccionada*
- **Método:** `move_videos(self)`
- **Método:** `run_script(self, script_name)`
- **Método:** `_execute(self, script_name)`
- **Método:** `run_all_scripts(self)`
  - *Ejecuta todos los scripts secuencialmente para probar errores.*
- **Método:** `_execute_all(self)`
- **Método:** `process_song_workflow(self)`
  - *Flujo de trabajo paso a paso para procesar una canción completa.*
- **Método:** `_step_1_5_beautify(self)`
- **Método:** `_step_2_edit(self)`
- **Método:** `_step_3_ai_style(self)`
- **Método:** `_step_4_config(self)`
- **Método:** `_step_5_process(self, script_vars, style_vars, win)`
- **Método:** `_execute_sequence(self, scripts_to_run)`
- **Método:** `run_director(self)`
  - *Lanza el script de edición automática.*
- **Método:** `run_process_with_logging(self, cmd, description)`
  - *Ejecuta un proceso capturando stderr y logueando errores.*
- **Método:** `on_closing(self)`
  - *Cierra la aplicación y mata el proceso de IA si existe.*




### 📄 Módulo: `render_main copy.py`
---



### 📄 Módulo: `run_all_tests.py`
---



### 📄 Módulo: `run_demucs.py`
---

#### ⚙️ Función: `mock_load(filepath)`
#### ⚙️ Función: `mock_save(filepath, src, sample_rate)`


### 📄 Módulo: `test_all_engines_5s.py`
---

#### ⚙️ Función: `run_tests()`


### 📄 Módulo: `test_cppn_fast.py`
---



### 📄 Módulo: `test_demucs_pipeline.py`
---

#### ⚙️ Función: `test_demucs_pipeline()`


### 📄 Módulo: `test_lyrics.py`
---

#### ⚙️ Función: `run_test()`


### 📄 Módulo: `test_overnight_QA.py`
---

#### ⚙️ Función: `run_tests()`


### 📄 Módulo: `test_visual.py`
---



### 📄 Módulo: `test_vj_fixed.py`
---



### 📄 Módulo: `scratch\generate_master_manual.py`
---

#### ⚙️ Función: `get_python_files(directory)`
#### ⚙️ Función: `parse_file(filepath)`
#### ⚙️ Función: `generate_markdown()`


### 📄 Módulo: `scratch\test_alien.py`
---



### 📄 Módulo: `scratch\test_segmentation.py`
---

#### ⚙️ Función: `dummy_test()`


### 📄 Módulo: `src\fix_bom.py`
---



### 📄 Módulo: `src\test_physics.py`
---



### 📄 Módulo: `src\ai\api_ai.py`
---

#### 📦 Clase: `PromptRequest`


#### 📦 Clase: `ConfigResponse`


#### 📦 Clase: `LyricsRequest`




### 📄 Módulo: `src\ai\director_ai.py`
---

#### ⚙️ Función: `safe_subclip(clip, start, end)`
Wrapper seguro para subclip/subclipped

#### ⚙️ Función: `get_visual_energy(video_path)`
Usa PyTorch para calcular la 'Energía Visual' del video.
Retorna un valor entre 0.0 (Calma) y 1.0 (Caos total).

#### ⚙️ Función: `generar_montaje_ia(audio_path, duration_arg, clips_dir_arg, output_filename, progress_callback)`
#### ⚙️ Función: `main()`


### 📄 Módulo: `src\ai\__init__.py`
---



### 📄 Módulo: `src\audio\audio_analyzer.py`
---

#### ⚙️ Función: `analizar_audio(ruta_audio, fps, duracion)`
#### ⚙️ Función: `analizar_stems(stem_folder, fps, duracion)`


### 📄 Módulo: `src\audio\motor_lyrics.py`
---

#### ⚙️ Función: `corregir_ortografia_whisper(texto)`
(C) Rebeldía Cósmica
Limpia los artefactos y alucinaciones comunes de Whisper en español.

#### ⚙️ Función: `transcribir_audio_para_edicion(audio_path, model_size, max_duration)`
Extrae la letra usando Whisper y la pasa por el corrector ortográfico.
Devuelve el texto puro para que el usuario lo edite en la UI.

#### 📦 Clase: `LyricsEngine`
- **Método:** `__init__(self, audio_path, max_duration, position, progress_callback, is_reel)`
  - *Inicializa el motor de lyrics. :param audio_path: Ruta al archivo de audio. :param max_duration: Si se especifica, solo procesa esta cantidad de segundos. :param position: "Abajo" o "Centro". :param progress_callback: Función f(current, total) para reportar progreso a la UI. :param is_reel: Si es True, activa formato vertical (Reel).*
- **Método:** `_get_external_lyrics(self)`
  - *Intenta obtener la letra original desde: 1. Un archivo .txt con el mismo nombre. 2. Los metadatos del archivo de audio (FFmpeg). Retorna el texto (str) o None.*
- **Método:** `transcribe_audio(self)`
  - *Ejecuta stable-ts para obtener timestamps a nivel de palabra.*
- **Método:** `load_transcription(self)`
  - *Carga el JSON de caché si ya existe.*
- **Método:** `_flatten_words(self)`
  - *Aplana la estructura jerárquica (Segmentos -> Palabras) a una lista simple para facilitar la búsqueda por tiempo.*
- **Método:** `_resegment_dynamic(self, max_words, max_duration)`
  - *Reconstruye self.data['segments'] agrupando palabras en intervalos cortos. Esto crea subtítulos estilo 'TikTok' o 'Lyric Video' dinámico.*
- **Método:** `print_lyrics(self)`
  - *Imprime la letra extraída y sus tiempos en la consola.*
- **Método:** `get_current_word_data(self, time)`
  - *Busca la palabra activa en el tiempo t. Retorna el diccionario de la palabra {'text': str, 'start': float, 'end': float} o None.*
- **Método:** `get_current_word(self, time)`
  - *Wrapper de compatibilidad.*
- **Método:** `get_text_mask(self, time, resolution_xy)`
  - *Genera una máscara NumPy con la palabra actual rasterizada. :param time: Tiempo actual en segundos. :param resolution_xy: Tupla (width, height) del grid de destino. :return: Array NumPy (height, width) float32, valores 0.0 a 1.0.*
- **Método:** `draw(self, frame, time, kick, snare, energy, scale_mod)`
  - *Dibuja la palabra actual en el frame usando OpenCV/Pillow con estética Cyberpunk Neón y Cromestesia. Incluye posicionamiento y animaciones suaves (Fade-in).*




### 📄 Módulo: `src\audio\procesamiento_audio.py`
---



### 📄 Módulo: `src\audio\__init__.py`
---



### 📄 Módulo: `src\core\blender.py`
---

#### ⚙️ Función: `update_gray_scott(U, V, Du, Dv, f, k, dt)`
Simulación de Reacción-Difusión (Gray-Scott Model).
Resuelve la EDP discretizada usando Diferencias Finitas.
U_t = Du * Lap(U) - uv^2 + f(1-u)
V_t = Dv * Lap(V) + uv^2 - (f+k)v

#### ⚙️ Función: `update_particles(pos, vel, force_field, width, height, damp, max_speed)`
Actualiza miles de partículas basándose en un campo de vectores.

#### ⚙️ Función: `generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps, duracion)`
#### ⚙️ Función: `unir_video_con_musica(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\core\config.py`
---



### 📄 Módulo: `src\core\crear_estructura.py`
---



### 📄 Módulo: `src\core\efectos_visuales.py`
---

**Descripción del Módulo:**
> (C) Rebeldía Cósmica | Creado por Santiago Prado

#### 📦 Clase: `CamaraVirtual`
- **Método:** `__init__(self, width, height)`
- **Método:** `randomize_mode(self, is_chorus)`
- **Método:** `update(self, energy, kick, snare, bass)`
- **Método:** `aplicar(self, frame)`


#### 📦 Clase: `MotorFX`
- **Método:** `__init__(self, w, h)`
- **Método:** `aplicar_bloom(self, img, intensity, threshold)`
  - *Aplica un efecto de resplandor (Bloom / Neon Glow) multi-capa a las áreas brillantes de la imagen. Este método aísla los píxeles que superan un umbral de luminosidad y genera un halo difuso alrededor de ellos mediante una técnica piramidal (downsampling iterativo). Esto permite crear un resplandor masivo de forma matemáticamente eficiente sin comprometer la tasa de fotogramas (FPS). Parámetros: ----------- img : numpy.ndarray La imagen (fotograma) de entrada en formato BGR (tipo uint8) proveniente de OpenCV. intensity : float Factor de multiplicación para la capa de resplandor final al mezclarla aditivamente con la imagen original. Valores más altos (ej. 1.5, 2.0) saturan la luz intensamente. Si intensity <= 0, se devuelve la imagen original sin procesar. threshold : int, opcional Umbral de luminosidad (0 a 255).*
- **Método:** `melting_world_fisheye(self, frame, kick_intensity)`
  - *Fase 12: Shader 'Melting World'. Distorsiona el cuadro simulando un lente ojo de pez que se infla y desinfla con los subgraves (kick).*
- **Método:** `mandelbrot_overlay(self, frame, time_sec, intensity)`
  - *Fase 12: Inyecta un patrón fractal de interferencia usando una simplificación matemática rápida compatible con OpenCV. (Efecto de ruido estático geométrico).*
- **Método:** `aberracion_cromatica(self, img, strength)`
  - *Aplica un desplazamiento de los canales de color (Aberración Cromática) simulando imperfecciones ópticas o fallos VHS. Separa los canales B (Azul), G (Verde) y R (Rojo) de la imagen, manteniendo el Verde intacto como ancla espacial. El canal Rojo se traslada horizontalmente hacia la derecha, y el Azul se traslada hacia la izquierda mediante transformaciones afines. Parámetros: ----------- img : numpy.ndarray La imagen (fotograma) de entrada en formato BGR (tipo uint8). strength : float o int Magnitud del desplazamiento horizontal en píxeles. Representa la distancia que se separarán los canales cromáticos. A mayor valor, mayor es el efecto "Glitch" o defecto de lente. Si strength <= 0, se devuelve la imagen original sin procesar. Retorna: -------- numpy.ndarray La imagen procesada tras recombinar los canales desplazados (R y B) con el canal G original.*
- **Método:** `feedback_temporal(self, current_frame, decay)`
- **Método:** `feedback_zoom(self, current_frame, decay, zoom)`
  - *Crea un efecto de túnel psicodélico escalando el frame anterior.*
- **Método:** `datamosh_biologico(self, current_frame, energy, kick)`
  - *Simula Pixel Sorting / Datamoshing usando el gradiente de luminancia como mapa de desplazamiento para 'derretir' los píxeles hacia abajo.*
- **Método:** `apply_god_rays(self, img, intensity, threshold)`
  - *Genera rayos volumétricos (Radial Blur Aditivo) desde el centro. Reactivo a la energía de la música.*
- **Método:** `plasma_melt_feedback(self, current_frame, decay, kick)`
  - *Mezcla el cuadro actual con el historial, desplazando el historial hacia arriba y difuminándolo para crear estelas de plasma derritiéndose.*
- **Método:** `aplicar_vhs_noise(self, img, intensity)`
  - *Añade ruido analógico sutil para evitar la crudeza digital pura.*
- **Método:** `shift_hue(self, img, shift_amount)`
  - *Rota los colores de la imagen (Ciclo HSV).*
- **Método:** `kaleidoscopio(self, img, active)`
  - *Convierte la imagen en un mandala psicodélico usando espejos (4-way symmetry).*
- **Método:** `aplicar_caleidoscopio(self, img, slices, intensity)`
  - *Wrapper de compatibilidad para legacy. Usa la implementación de espejos (kaleidoscopio) con blending.*
- **Método:** `agujero_negro_remap(self, img, phase, trigger)`
  - *Efecto Gravitacional: Absorbe la imagen y la escupe como onda expansiva en el kick.*
- **Método:** `time_slice_glitch(self, img, trigger)`
  - *Rebana la pantalla horizontalmente mostrando fotogramas del pasado.*
- **Método:** `vision_infrarroja_neon(self, img, trigger)`
  - *Convierte la imagen a alambres brillantes Canny en los picos de intensidad.*
- **Método:** `aberracion_cromatica_ritmica(self, img, kick_val, snare_val)`
  - *Separa el canal Rojo y Azul en función del kick y el snare.*




### 📄 Módulo: `src\core\nucleo_espectral.py`
---

#### 📦 Clase: `NucleoEspectral`
- **Método:** `__init__(self, w, h, dx, dy)`
- **Método:** `simulacion_ks_espectral(self, u_hat, dt, kick_intensity)`
  - *Integrador Pseudo-Espectral para Kuramoto-Sivashinsky (ETD1 Scheme) u_t = -(nabla^2 + nabla^4)u - 0.5 |nabla u|^2*
- **Método:** `simulacion_gpe_espectral(self, psi, V, g, dt)`
  - *Integrador Split-Step Fourier Method (SSFM) para Gross-Pitaevskii. psi_t = (i/2) nabla^2 psi - i V psi - i g |psi|^2 psi Estabilidad incondicional y conservación unitaria cuasi-perfecta.*




### 📄 Módulo: `src\core\nucleo_neural.py`
---

#### 📦 Clase: `CPPNEngine`
Compositional Pattern Producing Network (CPPN)
Un motor de inteligencia artificial hiper-rápido basado en NumPy.
No se entrena; se inicializa con pesos aleatorios y el audio manipula sus parámetros latentes.

- **Método:** `__init__(self, width, height, hidden_size, num_layers, seed)`
- **Método:** `_gaussian(self, x)`
- **Método:** `_step_lorenz(self, dt)`
- **Método:** `generate_frame(self, time_t, audio_z)`
  - *Genera un fotograma completo basado en la integración caótica.*




### 📄 Módulo: `src\core\nucleo_pytorch.py`
---

#### 📦 Clase: `PINN_GPE`
Placeholder para la futura red neuronal que aprenderá la dinámica
de la Ecuación de Gross-Pitaevskii.

- **Método:** `__init__(self)`
- **Método:** `forward(self, x)`




### 📄 Módulo: `src\core\nucleo_visual.py`
---

#### ⚙️ Función: `simulacion_gray_scott(U, V, out_U, out_V, Du, Dv, f, k, dt, seed_mask, tension)`
#### ⚙️ Función: `simulacion_ondas(u, u_prev, out_u, damping, c2_dt2, seed_mask)`
#### ⚙️ Función: `simulacion_ks(u, out_u, dt)`
#### ⚙️ Función: `simulacion_gpe(psi_real, psi_imag, out_r, out_i, V, g, dt)`
#### ⚙️ Función: `simulacion_ohta_kawasaki(u, out_u, dt, gamma, mobility, sigma)`
#### ⚙️ Función: `simulacion_cahn_hilliard(u, out_u, dt, gamma, mobility)`
#### ⚙️ Función: `simulacion_kdv(u, out_u, dt, alpha, beta)`
#### ⚙️ Función: `update_particles(pos, vel, force_field, width, height, damp, max_speed, seed_mask)`
#### ⚙️ Función: `simulacion_lorenz(particulas, dt, sigma, rho, beta)`
#### ⚙️ Función: `simulacion_ifs(grid, iters, transform_matrix, prob, cx, cy)`
#### ⚙️ Función: `compute_lensing_map(width, height, center_x, center_y, Rs, spin, epsilon)`
Computa el mapa de distorsión vectorial 2D para simular una Lente Gravitacional 
de un Agujero Negro usando una métrica de Schwarzschild modificada con 
Frame-Dragging (Efecto Lense-Thirring de Kerr).



### 📄 Módulo: `src\core\rostros_alienigenas.py`
---

#### 📦 Clase: `AlienGenerator`
Motor Matemático Procedimental basado en Pareidolia y Domain Warping.
Diseñado para generar rostros y texturas alienígenas/biomecánicas a 60fps
sin depender de redes neuronales (Deep Learning).

- **Método:** `__init__(self, w, h)`
- **Método:** `_generar_ruido_fbm(self, scale, t_offset)`
  - *Genera una textura de ruido suave combinando resoluciones (Value Noise FBM).*
- **Método:** `_esculpir_con_sdf(self, textura, boca_abierta)`
  - *Aplica Funciones de Distancia Firmada (SDF) para dar forma de cráneo/cabeza.*
- **Método:** `_color_coseno(self, t, a, b, c, d)`
  - *Paleta generativa basada en Inigo Quilez cosine gradients.*
- **Método:** `procesar(self, energy, kick, snare)`




### 📄 Módulo: `src\core\video_utils.py`
---

#### ⚙️ Función: `unir_video_con_musica(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\core\visual_entities.py`
---

**Descripción del Módulo:**
> (C) Rebeldía Cósmica | Creado por Santiago Prado

#### 📦 Clase: `EspirituProcedural`
Clase que representa un espíritu procedural dentro del ecosistema de Rebeldía Cósmica.
Se encarga de generar y actualizar sistemas de partículas que simulan humo volumétrico 
con comportamiento dinámico y reactivo a la música, creando formas orgánicas y etéreas.

- **Método:** `__init__(self, w, h, seed_val)`
  - *Inicializa la instancia de EspirituProcedural, configurando las dimensiones de la pantalla y preparando el sistema de partículas vectorizado mediante NumPy para máxima eficiencia. Parámetros: ----------- w : int Ancho del área de renderizado o pantalla en píxeles. h : int Alto del área de renderizado o pantalla en píxeles. seed_val : int Semilla para el generador de números aleatorios (RandomState), asegurando que el comportamiento sea determinista y reproducible si se requiere la misma semilla.*
- **Método:** `_to_screen(self, x, y)`
  - *Transforma coordenadas lógicas del plano cartesiano 2D al sistema de coordenadas de la pantalla (píxeles). Parámetros: ----------- x : float Coordenada lógica X en el plano. y : float Coordenada lógica Y en el plano. Retorna: -------- tuple[int, int] Una tupla (px, py) que representa las coordenadas transformadas en píxeles listas para dibujar.*
- **Método:** `update(self, frame, x, y, scale, t, kick, harm, color_rgb)`
  - *Actualiza y dibuja el sistema de partículas de humo volumétrico en el fotograma actual. Reacciona en tiempo real a las métricas musicales, calculando la emisión de nuevas partículas, aplicando turbulencia (Browniana) y reduciendo su vida progresivamente para crear un efecto de humo etéreo. Parámetros: ----------- frame : numpy.ndarray El fotograma (imagen BGR de OpenCV) actual donde se dibujará la entidad. x : float Posición lógica X base del espíritu procedural. y : float Posición lógica Y base del espíritu procedural. scale : float Factor de escala base que determina el tamaño del espíritu. Si es <= 0, no se dibuja. t : float Tiempo o fase temporal actual de la animación, usado para el movimiento oscilante. kick : float Intensidad de los graves (bombos) en el momento actual, entre 0 y 1. Impacta la cantidad y explosividad del humo. harm : float Intensidad del contenido armónico de la música. Afecta el tiempo de vida de las partículas. color_rgb : tuple[float, float, float] o list[float] Color base RGB de las partículas (cada canal entre 0 y 1).*


#### 📦 Clase: `SuperformaProcedural`
Clase que genera geometría y curvas 2D extremas mediante la fórmula de las Superformas 
(Superformula), un sistema matemático capaz de modelar una gran cantidad de formas orgánicas 
y naturales. Reacciona a parámetros musicales para mutar su forma a lo largo del tiempo.

- **Método:** `__init__(self, w, h)`
  - *Inicializa la clase SuperformaProcedural con el ancho y alto del fotograma de renderizado. Parámetros: ----------- w : int Ancho del área de renderizado o pantalla en píxeles. h : int Alto del área de renderizado o pantalla en píxeles.*
- **Método:** `_to_screen(self, x, y)`
  - *Transforma coordenadas lógicas a coordenadas de pantalla (píxeles) manteniendo la relación de aspecto correcta del área visual. Parámetros: ----------- x : float Coordenada lógica X a transformar. y : float Coordenada lógica Y a transformar. Retorna: -------- tuple[int, int] Las coordenadas X e Y correspondientes en píxeles de la pantalla.*
- **Método:** `update(self, frame, t, kick, harm, color_rgb)`
  - *Calcula la Superforma (Superformula) evaluando la fórmula para una serie de ángulos, y dibuja el polígono resultante en el frame. La silueta y detalles geométricos mutan con el tiempo y los impulsos rítmicos. Parámetros: ----------- frame : numpy.ndarray El fotograma o lienzo (imagen BGR) donde se renderizará la superforma. t : float Tiempo o fase de la animación; influye directamente en las potencias y componentes armónicos de la forma. kick : float Impulso de batería/bombo (0 a 1). Engrosa los bordes de la figura e influye en parámetros geométricos. harm : float Nivel de contenido armónico o melódico musical (0 a 1). Modifica la variable 'm' (simetría) de la ecuación. color_rgb : tuple[float, float, float] o list[float] Color interno de relleno RGB (cada canal entre 0 y 1). El borde será dibujado en blanco brillante.*


#### 📦 Clase: `LorenzSwarm`
- **Método:** `__init__(self, w, h, num_attractors)`
- **Método:** `_to_screen(self, x, y)`
- **Método:** `update(self, frame, dt_base, kick, cymbals, visible, color_bgr_override)`


#### 📦 Clase: `GeneradorHojas`
Clase encargada de la generación y gestión procedural de figuras con forma de hoja de plantas.
Emite "hojas" que crecen con el tiempo y forman patrones rotatorios orgánicos, simétricos e intrincados,
cuyo comportamiento y ritmo de desarrollo responde a los componentes armónicos de la música.

- **Método:** `__init__(self, w, h)`
  - *Inicializa el generador, definiendo límites de pantalla y estableciendo la capacidad máxima de la lista de hojas en memoria. Parámetros: ----------- w : int Ancho de la pantalla / resolución en píxeles. h : int Alto de la pantalla / resolución en píxeles.*
- **Método:** `_to_screen(self, x, y)`
  - *Convierte una posición 2D expresada en unidades lógicas del sistema de coordenadas a la correspondiente posición de píxeles en pantalla con el aspect ratio corregido. Parámetros: ----------- x : float Posición X en el sistema lógico. y : float Posición Y en el sistema lógico. Retorna: -------- tuple[int, int] Posición X, Y en píxeles como enteros.*
- **Método:** `spawn(self, x, y, color_rgb)`
  - *Añade (instancia) una nueva hoja procedural (representada por un diccionario de propiedades) en las coordenadas dadas. Si se supera el límite máximo, elimina la más vieja. Genera de forma aleatoria la forma base de la hoja, su rotación, y su objetivo de escala máxima. Parámetros: ----------- x : float Posición inicial X en el plano lógico. y : float Posición inicial Y en el plano lógico. color_rgb : tuple[float, float, float] o list[float] Color RGB (cada canal de 0 a 1) base para esta hoja.*
- **Método:** `update(self, frame, kick, harm)`
  - *Itera sobre todas las hojas activas, actualizando sus tamaños (escalado o 'crecimiento'), edades y calculando sus transformaciones afines (rotación y simetría bilateral). Finalmente, dibuja los polígonos generados de cada hoja sobre el fotograma, aplicando efectos de 'fade in/out' basados en su vida útil. Parámetros: ----------- frame : numpy.ndarray El fotograma BGR actual en el que se pintarán las geometrías de las hojas. kick : float Valor del impulso rítmico (bombo) (0 a 1). En la versión actual no tiene uso directo, pero se pasa por compatibilidad con el pipeline de renderizado reactivo a sonido. harm : float Contenido armónico de la música (0 a 1), que actúa como un fertilizante sonoro. A mayor valor, más rápido crecen las hojas en la pantalla.*


#### 📦 Clase: `TunelCuantico3D`
- **Método:** `__init__(self, width, height, num_stars)`
- **Método:** `init_stars(self, indices)`
- **Método:** `update_and_draw(self, frame, speed_base, kick)`


#### 📦 Clase: `AdveccionTextura`
- **Método:** `__init__(self, width, height, image_path)`
- **Método:** `update(self, flow_x, flow_y, strength)`
- **Método:** `render(self, source_image)`


#### 📦 Clase: `BoidsSwarm`
- **Método:** `__init__(self, w, h, num_boids)`
- **Método:** `update(self, frame, kick, cymbals, color_bgr_override)`


#### 📦 Clase: `MotorRelatividad`
Motor Físico: Relatividad General (Lentes Gravitacionales y Agujeros Negros).
Aproximación ultra-optimizada 2D de las métricas de Schwarzschild y Kerr.

- **Método:** `__init__(self, w, h)`
- **Método:** `render(self, frame, kick, harm, color_bgr)`




### 📄 Módulo: `src\core\__init__.py`
---



### 📄 Módulo: `src\render\__init__.py`
---



### 📄 Módulo: `src\render\experimental\render_chaos.py`
---

#### ⚙️ Función: `update_attractor(xyz, a, b, c, d, e, f, dt)`
Integración RK4 del Atractor de Aizawa.

#### ⚙️ Función: `render_chaos(audio_path, output_path, duracion, cmap_name)`


### 📄 Módulo: `src\render\experimental\render_experimental.py`
---

#### ⚙️ Función: `update_gray_scott(U, V, Du, Dv, f, k, dt)`
Simulación de Reacción-Difusión (Gray-Scott Model).
Resuelve la EDP discretizada usando Diferencias Finitas.
U_t = Du * Lap(U) - uv^2 + f(1-u)
V_t = Dv * Lap(V) + uv^2 - (f+k)v

#### ⚙️ Función: `update_particles(pos, vel, force_field, width, height, damp, max_speed)`
Actualiza miles de partículas basándose en un campo de vectores.

#### ⚙️ Función: `generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps, duracion, seed, allowed_engines, use_flash)`
#### ⚙️ Función: `unir_video_con_musica(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\render\experimental\render_ifs.py`
---

#### ⚙️ Función: `ifs_chaos_game(width, height, num_iters, coeffs, probs_acc, scale, offset_x, offset_y)`
Genera un fractal IFS mediante el Juego del Caos y retorna un histograma de densidad.

Parámetros:
- coeffs: Array (N, 6) donde cada fila es [a, b, c, d, e, f] para la transformación afín:
          x_new = a*x + b*y + e
          y_new = c*x + d*y + f
- probs_acc: Array (N,) con probabilidades acumuladas (ej: [0.01, 0.86, 0.93, 1.0])

#### ⚙️ Función: `render_ifs(audio_path, output_path, duracion, cmap_name, seed)`


### 📄 Módulo: `src\render\experimental\__init__.py`
---



### 📄 Módulo: `src\render\stable\render_laboratorio.py`
---

#### ⚙️ Función: `simular_laboratorio_puro(nombre_salida, fps, duracion, seed, engine_code, progress_callback)`
Entorno de simulación Aislado y Estricto.
Sin audio. Sin reactividad. Pura evolución determinista sobre un colormap científico.



### 📄 Módulo: `src\render\stable\render_lbm.py`
---

#### ⚙️ Función: `lbm_step(F, F_new, rho, u, nx, ny, omega)`
Paso de Colisión (BGK) y Streaming.

#### ⚙️ Función: `render_lbm(audio_path, output_path, duracion, cmap_name)`


### 📄 Módulo: `src\render\stable\render_lenia.py`
---

#### ⚙️ Función: `growth_function(U, mu, sigma)`
Función de crecimiento gaussiana (Orbium).

#### ⚙️ Función: `get_kernel(r)`
Genera el kernel anular de Lenia.

#### ⚙️ Función: `render_lenia(audio_path, output_path, duracion, cmap_name)`


### 📄 Módulo: `src\render\stable\render_main_autoencoders.py`
---

#### 📦 Clase: `AudioAutoencoder`
- **Método:** `__init__(self, input_dim, latent_dim)`
- **Método:** `forward(self, x)`


#### ⚙️ Función: `entrenar_red_con_cancion(spectrograma_norm, epochs, song_name)`
Entrena la red para que aprenda la topología específica de ESTA canción.
Usa Checkpoints para no re-entrenar si ya existe.

#### ⚙️ Función: `mapear_latente_a_fisica(latente_array)`
Traduce el vector latente a parámetros de TODOS los motores.
z[0] -> Selector de Motor (Engine Switch)
z[1] -> Parámetro Principal (Feed, Damping, Gamma, etc.)
z[2] -> Parámetro Secundario (Kill, Speed, Mobility, etc.)

#### ⚙️ Función: `check_vital_signs(buffer_img)`
Monitor de signos vitales de la simulación.
Detecta si la imagen se puso toda blanca (saturación) o toda negra (muerte).
Retorna True si la simulación necesita RCP (Reseteo).

#### ⚙️ Función: `soft_normalize(arr, percentile)`
Normalización suave usando percentiles para evitar destellos por picos únicos.

#### ⚙️ Función: `generar_animacion_neural(ruta_audio, nombre_salida_temp, fps, duracion, use_flash)`
#### ⚙️ Función: `unir_audio(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\render\stable\render_main_clasico.py`
---

#### ⚙️ Función: `generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps, duracion, seed, allowed_engines, use_kaleido, use_flash, use_chroma)`
#### ⚙️ Función: `unir_video_con_musica(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\render\stable\render_main_legacy.py`
---

#### ⚙️ Función: `generar_animacion_legacy(ruta_audio, nombre_salida_temp, fps, duracion, seed, allowed_engines, use_kaleido, use_flash, use_chroma)`
#### ⚙️ Función: `unir_video_con_musica(video_path, audio_path, output_path, duracion)`


### 📄 Módulo: `src\render\stable\render_standard.py`
---

**Descripción del Módulo:**
> (C) Rebeldía Cósmica | Creado por Santiago Prado

#### ⚙️ Función: `generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps, duracion, seed, allowed_engines, use_spirits, use_kaleido, use_flash, use_chroma, use_lyrics, lyrics_pos, use_stems, stem_folder, use_superposition, global_cmap, progress_callback, hq_mode, is_reel)`
Función principal encargada de renderizar la animación visual reactiva al audio utilizando múltiples motores físicos.

Esta función orquesta la simulación y composición de diversas capas visuales, integrando
análisis de audio con sistemas dinámicos (Gray-Scott, Kuramoto-Sivashinsky, GPE, etc.), 
efectos de post-procesamiento y geometría generativa.

Parámetros:
-----------
ruta_audio : str
    Ruta absoluta o relativa al archivo de audio que se utilizará como fuente de reactividad.
nombre_salida_temp : str
    Nombre o ruta del archivo de video temporal (sin audio) donde se guardarán los fotogramas generados (ej. 'temp.mp4').
fps : int, opcional
    Fotogramas por segundo del video de salida. Valor por defecto: 30.
duracion : float, opcional
    Duración máxima del render en segundos. Si es None, se renderiza la totalidad del audio. Valor por defecto: None.
seed : int, opcional
    Semilla para el generador de números aleatorios (numpy.random) para garantizar reproducibilidad. Valor por defecto: None.
allowed_engines : list de str, opcional
    Lista de identificadores de los motores físicos o de efectos permitidos para esta sesión (ej. ['GS', 'KS', 'lorenz']). Si es None, se usan todos.
use_spirits : bool, opcional
    Activa o desactiva la capa de entidades visuales procedimentales (Espíritus/Metaballs). Valor por defecto: True.
use_kaleido : bool, opcional
    Habilita el efecto de caleidoscopio dinámico (geometría de mandala). Valor por defecto: True.
use_flash : bool, opcional
    Controla si se permiten flashes intensos en la animación mediante uso masivo de bloom y saturación, útil desactivar por fotosensibilidad. Valor por defecto: True.
use_chroma : bool, opcional
    Activa la cromestesia: teñir o influenciar los colores del fondo usando una paleta asignada a la nota predominante. Valor por defecto: False.
use_lyrics : bool, opcional
    Determina si se superpondrán letras sincronizadas sobre el video, extraídas vía Stable-TS u otro motor. Valor por defecto: False.
lyrics_pos : str, opcional
    Posición de la letra en pantalla ("Abajo" o "Centro"). Valor por defecto: "Abajo".
use_stems : bool, opcional
    Si es True, intentará leer las pistas separadas por IA para modular independientemente cada parámetro físico.
stem_folder : str, opcional
    Ruta a la carpeta que contiene los archivos drums.wav, bass.wav, etc. si use_stems es True.
global_cmap : str, opcional
    Nombre de un colormap de matplotlib (ej. 'viridis', 'magma') que forzará una paleta global, ignorando las de la escena. Valor por defecto: None.
progress_callback : callable, opcional
    Función de retroalimentación invocada en cada fotograma. Su firma debe ser `progress_callback(frame_actual, total_frames)`. Valor por defecto: None.

Retorna:
--------
bool
    Devuelve True si la generación y escritura del video se completó con éxito. False si hubo algún error crítico o falla en el análisis.



### 📄 Módulo: `src\render\stable\__init__.py`
---



### 📄 Módulo: `src\ui\__init__.py`
---


