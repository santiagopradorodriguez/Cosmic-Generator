# (C) Rebeldía Cósmica | Creado por Santiago Prado
import numpy as np
import cv2
import librosa
import subprocess
from numba import jit, prange
import matplotlib.pyplot as plt
import sys
import imageio_ffmpeg
import argparse
from tqdm import tqdm

WIDTH, HEIGHT = 1280, 720
FPS = 30
NUM_PARTICLES = 10000

@jit(nopython=True, parallel=True)
def update_attractor(xyz, a, b, c, d, e, f, dt):
    """Integración RK4 del Atractor de Aizawa."""
    n = xyz.shape[0]
    new_xyz = np.empty_like(xyz)
    
    for i in prange(n):
        x, y, z = xyz[i, 0], xyz[i, 1], xyz[i, 2]
        
        # Función auxiliar para derivadas
        def get_derivs(tx, ty, tz):
            dx = (tz - b) * tx - d * ty
            dy = d * tx + (tz - b) * ty
            dz = c + a * tz - (tz**3 / 3) - (tx**2 + ty**2) * (1 + e * tz) + f * tz * tx**3
            return dx, dy, dz

        # RK4
        k1x, k1y, k1z = get_derivs(x, y, z)
        k2x, k2y, k2z = get_derivs(x + 0.5*dt*k1x, y + 0.5*dt*k1y, z + 0.5*dt*k1z)
        k3x, k3y, k3z = get_derivs(x + 0.5*dt*k2x, y + 0.5*dt*k2y, z + 0.5*dt*k2z)
        k4x, k4y, k4z = get_derivs(x + dt*k3x, y + dt*k3y, z + dt*k3z)
        
        new_xyz[i, 0] = x + (dt/6.0)*(k1x + 2*k2x + 2*k3x + k4x)
        new_xyz[i, 1] = y + (dt/6.0)*(k1y + 2*k2y + 2*k3y + k4y)
        new_xyz[i, 2] = z + (dt/6.0)*(k1z + 2*k2z + 2*k3z + k4z)
        
    return new_xyz

def render_chaos(audio_path, output_path, duracion=None, cmap_name='viridis'):
    print(f"🌀 Iniciando Caos: {audio_path}")
    
    y_audio, sr = librosa.load(audio_path, duration=duracion)
    duration = librosa.get_duration(y=y_audio, sr=sr)
    total_frames = int(duration * FPS)
    hop = int(sr / FPS)
    
    chroma = librosa.feature.chroma_stft(y=y_audio, sr=sr, hop_length=hop)
    rms = librosa.feature.rms(y=y_audio, hop_length=hop)[0]
    rms = rms / np.max(rms)
    
    # Inicializar partículas
    xyz = np.random.randn(NUM_PARTICLES, 3).astype(np.float32) * 0.1
    
    # Buffer de estela (Trail)
    trail_buffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{WIDTH}x{HEIGHT}', '-pix_fmt', 'bgr24', '-r', str(FPS),
        '-i', '-', '-i', audio_path, '-c:v', 'libx264', '-c:a', 'aac',
        '-shortest', '-preset', 'fast', '-loglevel', 'error', output_path
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    # Parámetros base Aizawa
    a_base, b_base, c_base = 0.95, 0.7, 0.6
    d_base, e_base, f_base = 3.5, 0.25, 0.1
    dt = 0.01
    
    cmap = plt.get_cmap(cmap_name)

    try:
        for i in tqdm(range(total_frames), desc="Simulando Caos (Attractors)"):
            energy = rms[i] if i < len(rms) else 0
            # Usar chroma para variar parámetros
            c_idx = i if i < chroma.shape[1] else -1
            note_val = np.mean(chroma[:, c_idx])
            
            # Modulación de parámetros (El atractor respira)
            a = a_base + (energy * 0.1)
            d = d_base + (note_val * 0.5)
            
            # Simulación
            xyz = update_attractor(xyz, a, b_base, c_base, d, e_base, f_base, dt)
            
            # HOMEOSTASIS: Si las partículas explotan, traerlas de vuelta
            mask_explode = (np.abs(xyz[:, 0]) > 50) | (np.abs(xyz[:, 1]) > 50) | (np.abs(xyz[:, 2]) > 50)
            if np.any(mask_explode):
                xyz[mask_explode] = np.random.randn(np.sum(mask_explode), 3) * 0.1
            
            # Proyección 3D -> 2D
            # Rotación simple
            theta = i * 0.005
            rot_y = np.array([
                [np.cos(theta), 0, np.sin(theta)],
                [0, 1, 0],
                [-np.sin(theta), 0, np.cos(theta)]
            ])
            xyz_rot = xyz @ rot_y.T
            
            # Perspectiva
            fov = 300
            dist = 4.0
            x_2d = (xyz_rot[:, 0] * fov) / (xyz_rot[:, 2] + dist) + WIDTH/2
            y_2d = (xyz_rot[:, 1] * fov) / (xyz_rot[:, 2] + dist) + HEIGHT/2
            z_depth = xyz_rot[:, 2]
            
            # Render
            img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            
            # Dibujar puntos
            # Vectorizado es difícil con cv2.circle, hacemos loop simple o numpy mask
            # Para velocidad, usamos numpy assignment directo si es posible, o loop numba
            # Aquí loop simple python optimizado
            valid = (x_2d >= 0) & (x_2d < WIDTH) & (y_2d >= 0) & (y_2d < HEIGHT)
            
            # Color basado en profundidad y energía
            # Usamos el colormap seleccionado
            # Mapeamos energía + oscilación a 0-1
            val_norm = (0.5 + 0.5*np.sin(i*0.1)) * 0.5 + energy * 0.5
            color_rgba = cmap(np.clip(val_norm, 0, 1))
            r, g, b = [int(c*255) for c in color_rgba[:3]]
            
            for j in range(NUM_PARTICLES):
                if valid[j]:
                    px, py = int(x_2d[j]), int(y_2d[j])
                    # Tamaño por profundidad
                    size = 1 if z_depth[j] > 0 else 2
                    cv2.circle(img, (px, py), size, (b, g, r), -1)
            
            # Trail effect
            trail_buffer = cv2.addWeighted(trail_buffer, 0.90, img.astype(np.float32), 1.0, 0)
            final_img = np.clip(trail_buffer, 0, 255).astype(np.uint8)
            
            proc.stdin.write(final_img.tobytes())
            
            if i % 100 == 0: print(f"Chaos Frame {i}/{total_frames}")

    except Exception as e:
        print(e)
    finally:
        proc.stdin.close()
        proc.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Ruta del archivo de audio")
    parser.add_argument("--output", default="output_chaos.mp4", help="Ruta de salida")
    parser.add_argument("--duration", type=float, default=None, help="Duración en segundos")
    parser.add_argument("--cmap", default="viridis", help="Mapa de color")
    args, unknown = parser.parse_known_args()

    audio_file = args.audio
    duracion = args.duration
    
    render_chaos(audio_file, args.output, duracion=duracion, cmap_name=args.cmap)
