# (C) Rebeldía Cósmica | Creado por Santiago Prado
import numpy as np
import matplotlib.pyplot as plt
import cv2
import librosa
import subprocess
from numba import jit, prange
import sys
import imageio_ffmpeg
import argparse
from tqdm import tqdm

# --- CONFIGURACIÓN LBM D2Q9 ---
NX, NY = 400, 200 # Resolución de simulación
FPS = 30
SCALE = 3

# Pesos D2Q9
w = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36], dtype=np.float32)
# Vectores dirección (c_x, c_y)
cx = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1], dtype=np.int32)
cy = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1], dtype=np.int32)
# Índices opuestos para rebote
opp = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6], dtype=np.int32)

@jit(nopython=True, parallel=True, fastmath=True)
def lbm_step(F, F_new, rho, u, nx, ny, omega):
    """Paso de Colisión (BGK) y Streaming."""
    
    # 1. Momentos Macroscópicos
    for y in prange(ny):
        for x in prange(nx):
            rho_val = 0.0
            ux_val = 0.0
            uy_val = 0.0
            for i in range(9):
                f_val = F[i, y, x]
                rho_val += f_val
                ux_val += f_val * cx[i]
                uy_val += f_val * cy[i]
            
            rho[y, x] = rho_val
            if rho_val > 0:
                u[0, y, x] = ux_val / rho_val
                u[1, y, x] = uy_val / rho_val

    # 2. Colisión BGK
    for y in prange(ny):
        for x in prange(nx):
            rho_val = rho[y, x]
            ux = u[0, y, x]
            uy = u[1, y, x]
            u2 = ux*ux + uy*uy
            
            for i in range(9):
                cu = cx[i]*ux + cy[i]*uy
                f_eq = w[i] * rho_val * (1.0 + 3.0*cu + 4.5*cu*cu - 1.5*u2)
                F[i, y, x] = F[i, y, x] + omega * (f_eq - F[i, y, x])

    # 3. Streaming (Propagación) con condiciones periódicas
    for i in range(9):
        # np.roll es lento en numba, hacemos shift manual o usamos lógica de índices
        # Aquí usamos lógica directa para streaming periódico
        dx = cx[i]
        dy = cy[i]
        for y in prange(ny):
            target_y = (y + dy) % ny
            for x in prange(nx):
                target_x = (x + dx) % nx
                F_new[i, target_y, target_x] = F[i, y, x]
                
    return F_new

def render_lbm(audio_path, output_path, duracion=None, cmap_name='inferno'):
    print(f"🌊 Iniciando LBM Fluidos: {audio_path}")
    
    y_audio, sr = librosa.load(audio_path, duration=duracion)
    duration = librosa.get_duration(y=y_audio, sr=sr)
    total_frames = int(duration * FPS)
    hop = int(sr / FPS)
    
    onset_env = librosa.onset.onset_strength(y=y_audio, sr=sr)
    onset = librosa.util.sync(onset_env, np.arange(total_frames), aggregate=np.mean)
    onset = onset / (np.max(onset) + 1e-6)
    
    # Calcular RMS para flujo continuo (no solo golpes)
    rms = librosa.feature.rms(y=y_audio, hop_length=hop)[0]
    rms = rms / (np.max(rms) + 1e-6)
    rms = np.resize(rms, total_frames)
    
    # Inicialización
    F = np.ones((9, NY, NX), dtype=np.float32) + 0.01 * np.random.randn(9, NY, NX)
    # Normalizar pesos iniciales
    for i in range(9): F[i, :, :] *= w[i]
    
    F_new = np.zeros_like(F)
    rho = np.ones((NY, NX), dtype=np.float32)
    u = np.zeros((2, NY, NX), dtype=np.float32)
    
    # Viscosidad
    tau = 0.9 # Aumentado para estabilidad (0.6 era muy inestable)
    omega = 1.0 / tau

    # FFmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{NX*SCALE}x{NY*SCALE}', '-pix_fmt', 'bgr24', '-r', str(FPS),
        '-i', '-', '-i', audio_path, '-c:v', 'libx264', '-c:a', 'aac',
        '-shortest', '-preset', 'fast', '-loglevel', 'error', output_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    
    cmap = plt.get_cmap(cmap_name)

    try:
        for i in tqdm(range(total_frames), desc="Simulando Fluidos (LBM)"):
            kick = onset[i] if i < len(onset) else 0
            vol = rms[i] if i < len(rms) else 0
            
            # --- FÍSICA ---
            # Inyección de Audio (La Bomba)
            # AHORA: Inyectamos si hay volumen, no solo si hay kick
            if vol > 0.05 or kick > 0.01:
                # --- MEJORA: EMISOR MÓVIL (BAILA) ---
                # El punto de inyección se mueve en ochos (Lissajous)
                t = i * 0.05
                cx = int(NX//2 + np.sin(t) * (NX//3))
                cy = int(NY//2 + np.cos(t * 0.7) * (NY//4))
                
                r = 10
                # Fuerza oscilante
                force_y = np.sin(i * 0.2) * 0.2 * kick
                force_x = 0.2 * kick
                
                # Inyección directa en las funciones de distribución (Momentum)
                # Indices: 1:E, 2:N, 3:W, 4:S, 5:NE, 6:NW, 7:SW, 8:SE
                amount_x = force_x * 0.05
                amount_y = force_y * 0.05
                
                # Empujar X
                F[1, cy-r:cy+r, cx-r:cx+r] += amount_x
                F[3, cy-r:cy+r, cx-r:cx+r] -= amount_x
                
                # Empujar Y
                F[2, cy-r:cy+r, cx-r:cx+r] += amount_y
                F[4, cy-r:cy+r, cx-r:cx+r] -= amount_y
            
            # "Keep Alive": Si hay muy poca energía cinética, añadir ruido de fondo
            # Aumentado para evitar estancamiento
            if np.mean(u**2) < 1e-4:
                u += np.random.randn(2, NY, NX) * 0.01

            # Pasos de simulación (varios por frame para estabilidad)
            for _ in range(4):
                F = lbm_step(F, F_new, rho, u, NX, NY, omega)
                # Swap buffers
                F, F_new = F_new, F

            # --- DESFIBRILADOR ---
            # Si la simulación explota (NaN o Infinito), reiniciar suavemente
            if np.any(np.isnan(rho)) or np.max(rho) > 10.0:
                F = np.ones((9, NY, NX), dtype=np.float32) + 0.01 * np.random.randn(9, NY, NX)
                for k in range(9): F[k] *= w[k]
                rho = np.ones((NY, NX), dtype=np.float32)
                u = np.zeros((2, NY, NX), dtype=np.float32)

            # RELAJACIÓN DE DENSIDAD (Evita que la pantalla se ponga amarilla/blanca)
            rho = rho * 0.99 + 1.0 * 0.01

            # --- VISUALIZACIÓN ---
            # Calcular Curl (Vorticidad) para ver remolinos
            # curl = dv_y/dx - dv_x/dy
            uy, ux = u[1], u[0]
            dy_ux, dx_ux = np.gradient(ux)
            dy_uy, dx_uy = np.gradient(uy)
            curl = dx_uy - dy_ux
            
            # Visualizar Curl + Velocidad + Densidad (Para que no se vea negro si solo fluye laminar)
            speed = np.sqrt(ux**2 + uy**2)
            
            # FIX: Sanitizar valores para evitar RuntimeWarning de overflow
            curl = np.nan_to_num(curl)
            speed = np.nan_to_num(speed)
            rho = np.nan_to_num(rho)
            
            # FIX: Clampear valores extremos para evitar overflow en la multiplicación
            curl = np.clip(curl, -10.0, 10.0)
            speed = np.clip(speed, 0.0, 10.0)
            rho = np.clip(rho, 0.0, 10.0)
            
            # Normalizamos para visualización
            vis = (np.abs(curl) * 3.0) + (speed * 5.0) + (np.abs(rho - 1.0) * 2.0)
            vis = np.clip(vis, 0, 1)
            
            # --- MEJORA: COLOR DINÁMICO ---
            # Cambiar paleta según el tiempo o intensidad
            # Rotamos el índice del colormap
            vis_shifted = (vis + (i * 0.001)) % 1.0
            
            img = cmap(vis_shifted)[:, :, :3]
            img = (img * 255).astype(np.uint8)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            if SCALE > 1:
                img_bgr = cv2.resize(img_bgr, (NX*SCALE, NY*SCALE), interpolation=cv2.INTER_LINEAR)
            
            proc.stdin.write(img_bgr.tobytes())
            
    except Exception as e:
        print(e)
    finally:
        proc.stdin.close()
        proc.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Ruta del archivo de audio")
    parser.add_argument("--output", default="output_lbm.mp4", help="Ruta de salida")
    parser.add_argument("--duration", type=float, default=None, help="Duración en segundos")
    parser.add_argument("--cmap", default="inferno", help="Mapa de color (matplotlib)")
    args, unknown = parser.parse_known_args()

    audio_file = args.audio
    duracion = args.duration
        
    render_lbm(audio_file, args.output, duracion=duracion, cmap_name=args.cmap)
