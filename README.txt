==============================================================================
PROYECTO: MOTOR DE VISUALIZACIÓN DE AUDIO NEURONAL Y FÍSICO
==============================================================================

DESCRIPCIÓN GENERAL:
Este sistema genera videos musicales artísticos y reactivos mediante la convergencia 
de tres campos: Simulación de Fluidos (CFD), Inteligencia Artificial (Deep Learning) 
y Procesamiento Digital de Señales (DSP).

A diferencia de los visualizadores tradicionales que usan disparadores simples, 
este motor "escucha" la canción completa, aprende su estructura mediante una 
Red Neuronal (Autoencoder) y traduce esa estructura en leyes físicas que gobiernan 
un universo simulado.

ARQUITECTURA DEL SISTEMA:
-------------------------

1. EL CEREBRO (IA & DSP):
   - Análisis Espectral: Descomposición del audio en Espectrogramas de Mel (Librosa).
   - Autoencoder (PyTorch): Una red neuronal comprime la información auditiva 
     en un "Espacio Latente" de 3 dimensiones.
     * Encoder: Reduce la complejidad del audio a conceptos abstractos.
     * Decoder: Reconstruye el audio para calcular el error (Loss MSE).
   - Mapeo Latente: La trayectoria en el espacio latente controla qué motor físico 
     se activa y sus parámetros (viscosidad, reacción, caos).

2. EL CORAZÓN (Simulación Física - Numba JIT):
   Resuelve Ecuaciones Diferenciales Parciales (EDP) en tiempo real sobre grillas:
   - Reacción-Difusión (Gray-Scott): Patrones biológicos tipo Turing (corales, manchas).
   - Kuramoto-Sivashinsky: Modelado de frentes de llama y caos espacio-temporal.
   - Gross-Pitaevskii: Ecuación de Schrödinger no lineal (Condensados de Bose-Einstein).
   - Ecuación de Ondas: Propagación acústica y fenómenos de interferencia.
   - Cahn-Hilliard: Separación de fases (dinámica de fluidos inmiscibles).
   - Lattice Boltzmann (LBM): Dinámica de fluidos avanzada (Navier-Stokes).
   - Partículas Lagrangianas: Miles de agentes movidos por los campos de fuerza de los fluidos.

3. LA VOZ (Motor de Letras - Whisper):
   - Transcripción: Usa `stable-ts` (basado en OpenAI Whisper) para obtener 
     timestamps precisos a nivel de palabra.
   - Alineación Forzada: Si existe un .txt, alinea el texto oficial con el audio.
   - Renderizado: Genera máscaras de texto dinámicas que actúan como obstáculos 
     o emisores en la simulación de fluidos.

4. LOS OJOS (Renderizado & Post-Procesado):
   - Composición Híbrida: Mezcla mapas de calor (Matplotlib) con partículas (OpenCV).
   - Cámara Virtual: Simula movimientos de cámara, zoom y rotación reactivos al "Kick".
   - FX: Feedback Loop (estelas), Bloom (resplandor), Aberración Cromática.

DESCRIPCIÓN DE ARCHIVOS:
------------------------

[RAÍZ]
* lanzador.py: GUI de control. Permite seleccionar canción, configurar resolución y lanzar motores.
* test_lyrics.py: Diagnóstico para verificar FFmpeg y Whisper.

[SRC/]
* render_main_autoencoders.py: MOTOR PRINCIPAL (V2). Implementa el pipeline neuronal completo:
  Entrenamiento del Autoencoder -> Extracción de Latentes -> Simulación Multi-Física -> Video.
* render_standard.py: Motor clásico basado en scripts de guion ("Actos").
* nucleo_visual.py: Librería de solvers matemáticos acelerados con Numba (FDM, Euler, Verlet).
* motor_lyrics.py: Clase para gestión de subtítulos y generación de máscaras de texto.
* audio_analyzer.py: Lógica de análisis DSP en tiempo real (Librosa) usada por los renderizadores.
* efectos_visuales.py: Motores de post-procesamiento de imagen.
* visual_entities.py: Objetos visuales (Enjambres, Sprites).
* config.py: Configuraciones globales.

FUNDAMENTOS MATEMÁTICOS:
------------------------
El proyecto implementa métodos numéricos avanzados para garantizar estabilidad visual:
- Integración Temporal: Euler Explícito (Rápido), Verlet (Conservativo).
- Discretización Espacial: Diferencias Finitas (Stencil de 5 puntos).
- Estabilidad: Control de condiciones CFL y Von Neumann para evitar explosiones numéricas.
- Optimización: Descenso de Gradiente (Adam) para el entrenamiento de la IA.

REQUISITOS DEL SISTEMA:
-----------------------
- Python 3.8+
- PyTorch (CPU o CUDA)
- FFmpeg (en el PATH del sistema)
- Librerías: numpy, scipy, matplotlib, opencv-python, librosa, moviepy, stable-ts, tqdm, numba.

INSTRUCCIONES RÁPIDAS:
----------------------
1. Coloca tu música (.flac/.mp3) en la carpeta `data/` o raíz.
2. (Opcional) Crea un archivo .txt con la letra exacta (mismo nombre que el audio) para karaoke perfecto.
3. Ejecuta `lanzador.py`.
4. Selecciona "Render Neural" para la experiencia completa IA + Física.