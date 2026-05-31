# (C) Rebeldía Cósmica | Creado por Santiago Prado

import sys
import os
# Hack para que los subdirectorios puedan ver los modulos de src/
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = current_dir
while not src_dir.endswith('src') and not src_dir.endswith('src\\') and not src_dir.endswith('src/'):
    parent = os.path.dirname(src_dir)
    if parent == src_dir:
        break
    src_dir = parent
if src_dir not in sys.path:
    sys.path.append(src_dir)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import librosa
import imageio_ffmpeg 
from tqdm import tqdm
import os
from numba import jit
from scipy.ndimage import gaussian_filter

# Importar nuestros módulos
from core.efectos_visuales import CamaraVirtual, PostFX

# Configuración FFmpeg
plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip

# ==========================================
# FÍSICA AVANZADA (JIT COMPILADA)
# ==========================================

@jit(nopython=True)
def update_gray_scott(U, V, Du, Dv, f, k, dt):
    """
    Simulación de Reacción-Difusión (Gray-Scott Model).
    Resuelve la EDP discretizada usando Diferencias Finitas.
    U_t = Du * Lap(U) - uv^2 + f(1-u)
    V_t = Dv * Lap(V) + uv^2 - (f+k)v
    """
    rows, cols = U.shape
    new_U = np.copy(U)
    new_V = np.copy(V)
    
    # Laplaciano stencil 3x3 (Diferencias finitas)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            # Cálculo del Laplaciano
            lap_u = (U[r+1, c] + U[r-1, c] + U[r, c+1] + U[r, c-1] - 4*U[r, c])
            lap_v = (V[r+1, c] + V[r-1, c] + V[r, c+1] + V[r, c-1] - 4*V[r, c])
            
            uvv = U[r, c] * V[r, c] * V[r, c]
            
            # Ecuaciones de reacción
            du = Du * lap_u - uvv + f * (1 - U[r, c])
            dv = Dv * lap_v + uvv - (f + k) * V[r, c]
            
            new_U[r, c] += du * dt
            new_V[r, c] += dv * dt
            
    return new_U, new_V

@jit(nopython=True)
def update_particles(pos, vel, force_field, width, height, damp, max_speed):
    """
    Actualiza miles de partículas basándose en un campo de vectores.
    """
    n = pos.shape[0]
    for i in range(n):
        # Obtener coordenadas enteras para el campo de fuerza
        x, y = int(pos[i, 0]), int(pos[i, 1])
        
        # Limites seguros
        if 0 <= x < width and 0 <= y < height:
            # Aplicar fuerza del campo (ruido/audio)
            vel[i, 0] += force_field[y, x, 0]
            vel[i, 1] += force_field[y, x, 1]
        
        # Límites de velocidad
        speed = np.sqrt(vel[i, 0]**2 + vel[i, 1]**2)
        if speed > max_speed:
            vel[i] = (vel[i] / speed) * max_speed
            
        # Actualizar posición
        pos[i] += vel[i]
        vel[i] *= damp # Fricción
        
        # Bordes (Wrap around)
        if pos[i, 0] < 0: pos[i, 0] += width
        if pos[i, 0] >= width: pos[i, 0] -= width
        if pos[i, 1] < 0: pos[i, 1] += height
        if pos[i, 1] >= height: pos[i, 1] -= height
        
    return pos, vel

# ==========================================
# GENERADOR DE ANIMACIÓN
# ==========================================
def generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps=30, duracion=None):
    
    print(f"--- 1. Deconstruyendo Audio: {ruta_audio} ---")
    
    # A) ANÁLISIS DE AUDIO AVANZADO (HPSS)
    try:
        y, sr = librosa.load(ruta_audio, duration=duracion)
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return False

    # Separación Armónica / Percusiva (Magia negra de DSP)
    # y_harmonic lleva la melodía/pads, y_percussive lleva los golpes
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    hop_length = int(sr / fps)
    total_frames = int(len(y) / hop_length)
    
    # 1. Energía Percusiva (Para Kicks y Shakes)
    rms_perc = librosa.feature.rms(y=y_percussive, hop_length=hop_length)[0]
    rms_perc = rms_perc / (np.max(rms_perc) + 1e-6)
    rms_perc = np.resize(rms_perc, total_frames)
    
    # 2. Energía Armónica (Para colores y flujos)
    rms_harm = librosa.feature.rms(y=y_harmonic, hop_length=hop_length)[0]
    rms_harm = rms_harm / (np.max(rms_harm) + 1e-6)
    rms_harm = np.resize(rms_harm, total_frames)
    
    # 3. Spectral Centroid (Brillo del sonido -> Color)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    cent = np.log1p(cent) # Escala logarítmica para mejor visualización
    cent = (cent - np.min(cent)) / (np.max(cent) - np.min(cent) + 1e-6)
    cent = np.resize(cent, total_frames)

    print(f"--- 2. Inicializando Motor de Física (Numba Accelerated) ---")
    
    # Configuración de Video
    W, H = 1280, 720 # HD (Full HD 1920x1080 es posible pero tarda más)
    aspect_ratio = W / H
    
    # --- SISTEMA 1: GRAY-SCOTT (Textura Biológica) ---
    # Resolución reducida para la simulación (se escala después)
    gs_scale = 4 
    gs_w, gs_h = W // gs_scale, H // gs_scale
    U = np.ones((gs_h, gs_w), dtype=np.float32)
    V = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # Sembrar perturbación inicial en el centro
    mid_r, mid_c = gs_h//2, gs_w//2
    r_seed = 20
    V[mid_r-r_seed:mid_r+r_seed, mid_c-r_seed:mid_c+r_seed] = 0.5
    
    # Parámetros Gray-Scott (El "DNA" del patrón)
    # Feed (f) y Kill (k) determinan si son manchas, corales, espirales...
    Da, Db = 0.16, 0.08
    
    # --- SISTEMA 2: MATPLOTLIB (Geometría Vectorial) ---
    # Usamos esto SOLO para líneas vectoriales precisas (Lorenz, Cubos)
    dpi = 100
    fig, ax = plt.subplots(figsize=(W/dpi, H/dpi), dpi=dpi)
    ax.set_axis_off()
    ax.set_xlim(-4 * aspect_ratio, 4 * aspect_ratio)
    ax.set_ylim(-4, 4)
    fig.subplots_adjust(0,0,1,1)
    # Fondo transparente para superponer
    fig.patch.set_alpha(0.0) 
    
    # Atractor de Lorenz (Objeto 3D)
    linea_lorenz, = ax.plot([], [], lw=1.5, alpha=0.9)
    state_lorenz = np.array([0.1, 0.0, 0.0])
    hist_lorenz = [[], [], []]

    # --- INICIALIZAR RENDER ---
    camara = CamaraVirtual(W, H)
    fx = PostFX()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombre_salida_temp, fourcc, fps, (W, H))
    
    # Colormap para el Gray-Scott
    cmap_gs = plt.get_cmap('magma')

    try:
        for i in tqdm(range(total_frames), desc="Renderizando Física + Geometría"):
            
            # --- DATOS DE AUDIO ---
            kick = rms_perc[i] if i < len(rms_perc) else 0
            harm = rms_harm[i] if i < len(rms_harm) else 0
            brillo = cent[i] if i < len(cent) else 0
            
            # ============================
            # CAPA 1: FONDO (GRAY-SCOTT)
            # ============================
            # Modulamos los parámetros f y k con la música para que el "hongo" baile
            f = 0.055 + (harm * 0.01)       # La armonía alimenta el sistema
            k = 0.062 - (kick * 0.005)      # El kick mata/modifica la reacción
            
            # Corremos varias iteraciones por frame para estabilidad numérica
            for _ in range(8):
                U, V = update_gray_scott(U, V, Da, Db, f, k, dt=1.0)
            
            # Convertir V a imagen
            # V representa la "sustancia" visible
            gs_img = V / (np.max(V) + 1e-6) 
            gs_img_color = cmap_gs(gs_img)[:, :, :3] # Aplicar colormap (RGBA -> RGB)
            gs_img_color = (gs_img_color * 255).astype(np.uint8)
            
            # Escalar a HD
            bg_layer = cv2.resize(gs_img_color, (W, H), interpolation=cv2.INTER_LINEAR)
            
            # Oscurecer el fondo si la música es baja
            bg_layer = (bg_layer * (0.3 + harm * 0.7)).astype(np.uint8)

            # ============================
            # CAPA 2: GEOMETRÍA (LORENZ)
            # ============================
            # Ecuaciones de Lorenz
            sigma, rho, beta = 10, 28, 8/3
            # FIX: Reducir dt máximo para evitar overflow numérico
            dt_lorenz = 0.005 * (1 + kick * 3) 
            
            x, y, z = state_lorenz
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            
            # FIX: Reiniciar si el sistema explota (NaN o Infinito)
            new_state = np.array([x + dx*dt_lorenz, y + dy*dt_lorenz, z + dz*dt_lorenz])
            if np.any(np.isnan(new_state)) or np.any(np.isinf(new_state)) or np.max(np.abs(new_state)) > 1e5:
                state_lorenz[:] = [0.1, 0.0, 0.0] # Reset suave
            else:
                state_lorenz[:] = new_state
            
            # Guardar historia
            hist_lorenz[0].append(state_lorenz[0])
            hist_lorenz[1].append(state_lorenz[1])
            hist_lorenz[2].append(state_lorenz[2])
            if len(hist_lorenz[0]) > 300: # Limitar cola
                for k_idx in range(3): hist_lorenz[k_idx].pop(0)
            
            # Rotación 3D Manual
            pts = np.array(hist_lorenz).T
            theta = i * 0.01
            # Matriz rotación Y
            Ry = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
            pts_rot = pts @ Ry
            
            # Proyección y Dibujo
            scale_l = 0.05
            linea_lorenz.set_data(pts_rot[:, 0] * scale_l, pts_rot[:, 2] * scale_l - 1.5) # Centrar aprox
            
            # Color dinámico geometría
            color_geo = plt.cm.hsv(brillo) # Color basado en la frecuencia (grave=rojo, agudo=violeta)
            linea_lorenz.set_color(color_geo)
            linea_lorenz.set_linewidth(1 + kick * 4) # Grosor reactivo
            
            # Renderizar Matplotlib a buffer transparente
            fig.canvas.draw()
            buf = np.asarray(fig.canvas.buffer_rgba())
            
            # Convertir a formato OpenCV
            overlay_layer = cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)
            overlay_mask = buf[:, :, 3] # Canal Alpha
            
            # ============================
            # COMPOSICIÓN (Blending)
            # ============================
            # Mezclar Fondo (Gray-Scott) con Overlay (Matplotlib)
            # Usamos la máscara alpha para pegar la geometría sobre el fluido
            inv_mask = cv2.bitwise_not(overlay_mask)
            
            bg_masked = cv2.bitwise_and(bg_layer, bg_layer, mask=inv_mask)
            fg_masked = cv2.bitwise_and(overlay_layer, overlay_layer, mask=overlay_mask)
            
            frame_final = cv2.add(bg_masked, fg_masked)
            
            # ============================
            # POST-PROCESADO (FX)
            # ============================
            # 1. Feedback Temporal (Estelas)
            frame_final = fx.feedback_temporal(frame_final, decay=0.85 + (harm * 0.1))
            
            # 2. Cámara Virtual (Movimiento)
            camara.update(energy=harm, kick=kick, snare=rms_perc[i])
            frame_final = camara.aplicar(frame_final)
            
            # 3. Bloom (Brillo en los picos altos)
            if kick > 0.5:
                frame_final = fx.bloom(frame_final, intensidad=kick)
                
            # 4. Aberración Cromática (Glitch en transiciones)
            frame_final = fx.aberracion_cromatica(frame_final, intensidad=kick * 10)

            # Escribir frame
            out.write(frame_final)

        out.release()
        plt.close(fig)
        return True

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# UNIÓN FINAL
# ==========================================
def unir_video_con_musica(video_path, audio_path, output_path, duracion=None):
    print(f"--- 3. Renderizando Audio Final ---")
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    if duracion:
        audio = audio.subclip(0, duracion)
        video = video.subclip(0, duracion) # Asegurar sincronía
    
    # FIX: Compatibilidad con MoviePy v2.0 (set_audio pasó a ser with_audio)
    if hasattr(video, 'with_audio'):
        final = video.with_audio(audio)
    else:
        final = video.set_audio(audio)
        
    final.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)

# ==========================================
# RUN
# ==========================================
if __name__ == "__main__":
    CANCION = "Rebeldía Cosmica - Sol Que se Va.flac"
    TEMP = "temp_godmode.mp4"
    FINAL = "Rebeldia_Cosmica_Official.mp4"
    
    # Pon esto en None para renderizar TODA la canción
    # Ponlo en 20 para probar los primeros 20 segundos rápido
    DURACION_TEST = None 
    
    if generar_animacion_god_mode(CANCION, TEMP, fps=30, duracion=DURACION_TEST):
        unir_video_con_musica(TEMP, CANCION, FINAL, duracion=DURACION_TEST)