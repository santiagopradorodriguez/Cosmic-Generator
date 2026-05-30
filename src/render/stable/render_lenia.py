import numpy as np
import matplotlib.pyplot as plt
import cv2
import librosa
import subprocess
import os
from scipy.signal import fftconvolve
from numba import jit
import sys
import imageio_ffmpeg
import argparse
from tqdm import tqdm

# --- CONFIGURACIÓN ---
WIDTH, HEIGHT = 640, 360  # Resolución interna (se escala al final)
FPS = 30
SCALE = 2  # Escala de visualización (1280x720 final)

@jit(nopython=True)
def growth_function(U, mu, sigma):
    """Función de crecimiento gaussiana (Orbium)."""
    # G(u) = 2 * exp( - (u - mu)^2 / (2 * sigma^2) ) - 1
    return 2.0 * np.exp(-((U - mu)**2) / (2.0 * sigma**2)) - 1.0

def get_kernel(r):
    """Genera el kernel anular de Lenia."""
    x = np.linspace(-1, 1, 2*r+1)
    X, Y = np.meshgrid(x, x)
    D = np.sqrt(X**2 + Y**2)
    # Anillo suave (Shell)
    K = np.exp(-((D - 0.5)**2) / 0.02)
    K = K / np.sum(K) # Normalizar
    return K

def render_lenia(audio_path, output_path, duracion=None, cmap_name='magma'):
    print(f"🧬 Iniciando Lenia: {audio_path}")
    
    # 1. Audio
    y, sr = librosa.load(audio_path, duration=duracion)
    duration = librosa.get_duration(y=y, sr=sr)
    total_frames = int(duration * FPS)
    hop = int(sr / FPS)
    
    # Features
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    rms = rms / (np.max(rms) + 1e-6)
    rms = np.resize(rms, total_frames)
    
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]
    cent = np.log1p(cent)
    cent = (cent - np.min(cent)) / (np.max(cent) - np.min(cent) + 1e-6)
    cent = np.resize(cent, total_frames)

    # 2. Estado Inicial
    # FIX: Iniciar limpio para evitar ruido estático global que satura la simulación
    grid = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    # Sembrar vida en el centro (Área más grande para generar inercia)
    cx, cy = WIDTH//2, HEIGHT//2
    grid[cy-40:cy+40, cx-40:cx+40] = np.random.rand(80, 80)

    # Parámetros Lenia
    R = 13
    kernel = get_kernel(R)
    mu_base = 0.15
    sigma_base = 0.017
    dt = 0.1

    # 3. FFmpeg Pipe
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    command = [
        ffmpeg_exe,
        '-y', # Sobreescribir
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{WIDTH*SCALE}x{HEIGHT*SCALE}',
        '-pix_fmt', 'bgr24',
        '-r', str(FPS),
        '-i', '-', # Input pipe
        '-i', audio_path, # Input audio
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',
        '-preset', 'fast',
        '-loglevel', 'error',
        output_path
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    
    # Colormap
    cmap = plt.get_cmap(cmap_name)

    try:
        for i in tqdm(range(total_frames), desc="Simulando Vida Artificial (Lenia)"):
            kick = rms[i] if i < len(rms) else 0
            high = cent[i] if i < len(cent) else 0
            
            # --- FÍSICA ---
            # 1. Convolución (Sentir vecinos)
            # Usamos scipy fftconvolve porque es más rápido que numba para kernels grandes
            potential = fftconvolve(grid, kernel, mode='same')
            
            # 2. Reactividad
            # El kick expande el rango de vida (mu)
            mu = mu_base + (kick * 0.015) # Reducido ligeramente para evitar extinción masiva
            sigma = sigma_base + (high * 0.005)
            
            # 3. Crecimiento
            growth = growth_function(potential, mu, sigma)
            
            # 4. Actualización
            grid = grid + dt * growth
            grid = np.clip(grid, 0, 1) # Robustez
            
            # --- DINÁMICA DE FLUIDO (DRIFT) ---
            # Desplazar el universo suavemente para evitar sensación estática
            if i % 2 == 0:
                grid = np.roll(grid, 1, axis=1) # Drift horizontal constante

            # --- SISTEMA DE RESURRECCIÓN ---
            # Si la actividad promedio es muy baja (muerte) o muy alta (saturación), reiniciar zona
            # Umbral aumentado de 0.01 a 0.05 para revivir antes
            mean_activity = np.mean(grid)
            if mean_activity < 0.05 or mean_activity > 0.90:
                # Re-sembrar vida en posiciones aleatorias (Lluvia de vida)
                rx, ry = np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT)
                
                y1, y2 = max(0, ry-30), min(HEIGHT, ry+30)
                x1, x2 = max(0, rx-30), min(WIDTH, rx+30)
                
                if y2 > y1 and x2 > x1:
                    grid[y1:y2, x1:x2] = np.random.rand(y2-y1, x2-x1)

            # --- VISUALIZACIÓN ---
            # Mapear 0-1 a color
            frame_color = cmap(grid)[:, :, :3] # RGBA -> RGB
            frame_color = (frame_color * 255).astype(np.uint8)
            
            # Convertir RGB a BGR para OpenCV/FFmpeg
            frame_bgr = cv2.cvtColor(frame_color, cv2.COLOR_RGB2BGR)
            
            # Escalar
            if SCALE > 1:
                frame_bgr = cv2.resize(frame_bgr, (WIDTH*SCALE, HEIGHT*SCALE), interpolation=cv2.INTER_NEAREST)
            
            # Escribir al pipe
            process.stdin.write(frame_bgr.tobytes())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.stdin.close()
        process.wait()
        print(f"✅ Video guardado: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Ruta del archivo de audio")
    parser.add_argument("--output", default="output_lenia.mp4", help="Ruta de salida")
    parser.add_argument("--duration", type=float, default=None, help="Duración en segundos")
    parser.add_argument("--cmap", default="magma", help="Mapa de color")
    args, unknown = parser.parse_known_args()

    audio_file = args.audio
    duracion = args.duration
        
    render_lenia(audio_file, args.output, duracion=duracion, cmap_name=args.cmap)
