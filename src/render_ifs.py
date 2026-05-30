import numpy as np
import cv2
import librosa
import subprocess
from numba import jit
import matplotlib.pyplot as plt
import imageio_ffmpeg
import argparse
from tqdm import tqdm
import sys
import os

# Importar módulos estandarizados del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import WIDTH, HEIGHT, FPS
from audio_analyzer import analizar_audio

# --- NÚCLEO MATEMÁTICO OPTIMIZADO (NUMBA) ---
@jit(nopython=True, fastmath=True, cache=True)
def ifs_chaos_game(width, height, num_iters, coeffs, probs_acc, scale, offset_x, offset_y):
    """
    Genera un fractal IFS mediante el Juego del Caos y retorna un histograma de densidad.
    
    Parámetros:
    - coeffs: Array (N, 6) donde cada fila es [a, b, c, d, e, f] para la transformación afín:
              x_new = a*x + b*y + e
              y_new = c*x + d*y + f
    - probs_acc: Array (N,) con probabilidades acumuladas (ej: [0.01, 0.86, 0.93, 1.0])
    """
    # Histograma acumulativo (Matriz de densidad)
    histogram = np.zeros((height, width), dtype=np.float32)
    
    x, y = 0.0, 0.0
    
    # 1. Pre-calentamiento: Iterar sin dibujar para converger al atractor
    for _ in range(20):
        r = np.random.random()
        idx = 0
        # Búsqueda lineal de la transformación basada en probabilidad
        for i in range(len(probs_acc)):
            if r < probs_acc[i]:
                idx = i
                break
        
        a, b, c, d, e, f = coeffs[idx]
        nx = a * x + b * y + e
        ny = c * x + d * y + f
        x, y = nx, ny

    # 2. Ciclo Principal de Renderizado
    for _ in range(num_iters):
        r = np.random.random()
        idx = 0
        for i in range(len(probs_acc)):
            if r < probs_acc[i]:
                idx = i
                break
        
        a, b, c, d, e, f = coeffs[idx]
        
        # Transformación Afín
        nx = a * x + b * y + e
        ny = c * x + d * y + f
        x, y = nx, ny
        
        # Mapeo a Espacio de Pantalla
        # Invertimos Y porque en imágenes el 0 está arriba
        px = int(x * scale + offset_x)
        py = int(height - (y * scale + offset_y))
        
        # Acumulación (Histograma)
        if 0 <= px < width and 0 <= py < height:
            histogram[py, px] += 1.0
            
    return histogram

def render_ifs(audio_path, output_path, duracion=None, cmap_name='viridis', seed=None):
    print(f"🌿 Iniciando Motor IFS (Fractales): {audio_path}")
    
    if seed is not None:
        np.random.seed(seed)

    # 1. Análisis de Audio (Estandarizado)
    audio_data = analizar_audio(audio_path, FPS, duracion)
    if not audio_data:
        return
    
    total_frames = audio_data['total_frames']
    rms = audio_data['rms_harm']  # Energía general (Crecimiento sostenido)
    onset = audio_data['rms_perc'] # Golpes (Impactos)
    cent = audio_data['cent']      # Brillo

    # 2. Configuración de Fractales
    # A. Helecho de Barnsley
    fern_coeffs = np.array([
        [0.0, 0.0, 0.0, 0.16, 0.0, 0.0],        # Tallo (Prob 1%)
        [0.85, 0.04, -0.04, 0.85, 0.0, 1.6],    # Hojas pequeñas sucesivas (Prob 85%)
        [0.20, -0.26, 0.23, 0.22, 0.0, 1.6],    # Hojas izquierda (Prob 7%)
        [-0.15, 0.28, 0.26, 0.24, 0.0, 0.44]    # Hojas derecha (Prob 7%)
    ], dtype=np.float32)
    fern_probs = np.array([0.01, 0.85, 0.07, 0.07])

    # B. Triángulo de Sierpinski (Equilátero)
    # Altura de triángulo equilátero de lado 1 = sqrt(3)/2 approx 0.866
    h_tri = np.sqrt(3) / 2
    sierp_coeffs = np.array([
        [0.5, 0.0, 0.0, 0.5, 0.0, 0.0],         # Izquierda Abajo
        [0.5, 0.0, 0.0, 0.5, 0.5, 0.0],         # Derecha Abajo
        [0.5, 0.0, 0.0, 0.5, 0.25, h_tri/2]     # Arriba
    ], dtype=np.float32)
    sierp_probs = np.array([0.33, 0.33, 0.34])

    # Parámetros de Renderizado Globales
    iters_per_frame = 200000 # Alta densidad de puntos

    # 3. Pipeline de Video (FFmpeg)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}', '-pix_fmt', 'bgr24', '-r', str(FPS),
        '-i', '-', '-i', audio_path, '-c:v', 'libx264', '-c:a', 'aac',
        '-shortest', '-preset', 'medium', '-loglevel', 'error', output_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    cmap = plt.get_cmap(cmap_name)

    try:
        for i in tqdm(range(total_frames), desc="Renderizando Fractal IFS", file=sys.stdout):
            # Obtener parámetros de audio del frame actual
            energy = rms[i] if i < len(rms) else 0 # Volumen/Armonía
            kick = onset[i] if i < len(onset) else 0
            bright = cent[i] if i < len(cent) else 0
            
            # --- SELECCIÓN DE FRACTAL (Alternar cada 10 segundos) ---
            cycle_sec = 10.0
            time_sec = i / FPS
            is_fern = (time_sec % (cycle_sec * 2)) < cycle_sec
            
            if is_fern:
                # === LÓGICA HELECHO ===
                current_coeffs = fern_coeffs.copy()
                current_probs = fern_probs.copy()
                
                # Escala y Posición para Helecho
                scale_base = HEIGHT / 11.0
                offset_x_base = WIDTH / 2
                offset_y_base = 0

                # Reactividad Helecho: CRECIMIENTO ORGÁNICO
                # Modulamos los coeficientes de escala (a, d) con la energía.
                # Base d=0.85. Con la música crece hasta ~0.95 (Helecho alto) o baja a 0.75 (Helecho pequeño)
                growth = 0.75 + (energy * 0.20) 
                current_coeffs[1, 3] = growth # d (Altura)
                current_coeffs[1, 0] = growth # a (Anchura proporcional)
                
                dance = kick * 0.2
                current_coeffs[2, 2] += dance * np.sin(i * 0.2) 
                current_coeffs[2, 3] += dance * np.cos(i * 0.2)
                current_coeffs[3, 2] += dance * np.cos(i * 0.25)
                current_coeffs[3, 3] -= dance * np.sin(i * 0.25)
                
                if energy > 0.5:
                    boost = 0.03 * energy
                    current_probs[2] += boost
                    current_probs[3] += boost
                    current_probs[1] -= (boost * 2)
            
            else:
                # === LÓGICA SIERPINSKI ===
                current_coeffs = sierp_coeffs.copy()
                current_probs = sierp_probs.copy()
                
                # Escala y Posición para Sierpinski (Centrado)
                scale_base = HEIGHT * 0.9
                # Centrar X: El triángulo va de 0 a 1 en X. 0.5 es el centro.
                offset_x_base = WIDTH / 2 - (0.5 * scale_base)
                offset_y_base = HEIGHT * 0.05

                # Reactividad Sierpinski: LATIDO Y ZOOM
                # 1. Zoom Global: El triángulo entero crece con la energía
                scale_base = (HEIGHT * 0.8) * (1.0 + energy * 0.3)
                
                # 2. Respiración Interna: Los triángulos se separan con el Kick
                pulse = 0.5 + (kick * 0.05) 
                current_coeffs[:, 0] = pulse # a
                current_coeffs[:, 3] = pulse # d
                
                # Rotación/Cizallamiento sutil con la melodía (bright)
                twist = (bright - 0.5) * 0.1
                current_coeffs[2, 1] += twist # b (shear) en el triángulo superior

            # Calcular probabilidades acumuladas finales
            current_probs_acc = np.cumsum(current_probs)
            
            # Zoom Dinámico Global
            current_scale = scale_base * (1.0 + bright * 0.2)
            
            # --- GENERACIÓN (NUMBA) ---
            # Llamada a la función compilada JIT
            hist = ifs_chaos_game(WIDTH, HEIGHT, iters_per_frame, current_coeffs, current_probs_acc, current_scale, offset_x_base, offset_y_base)
            
            # --- POST-PROCESADO VISUAL ---
            # Transformación Logarítmica para revelar detalles sutiles (High Dynamic Range)
            hist_log = np.log1p(hist)
            hist_norm = hist_log / (np.max(hist_log) + 1e-6)
            
            # Aplicar Colormap
            frame_color = cmap(hist_norm)[:, :, :3]
            frame_bgr = (frame_color * 255).astype(np.uint8)
            frame_bgr = cv2.cvtColor(frame_bgr, cv2.COLOR_RGB2BGR)
            
            # Escribir al pipe
            proc.stdin.write(frame_bgr.tobytes())
            
    except Exception as e:
        print(f"❌ Error en render_ifs: {e}")
    finally:
        proc.stdin.close()
        proc.wait()
        print(f"✅ Fractal renderizado: {output_path}")

if __name__ == "__main__":
    # Este bloque permite probar el script individualmente
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Ruta del archivo de audio")
    parser.add_argument("--output", default="output_ifs.mp4", help="Ruta de salida")
    parser.add_argument("--duration", type=float, default=None, help="Duración en segundos")
    parser.add_argument("--cmap", default="viridis", help="Mapa de color (matplotlib)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    
    args, unknown = parser.parse_known_args()
    render_ifs(args.audio, args.output, duracion=args.duration, cmap_name=args.cmap, seed=args.seed)