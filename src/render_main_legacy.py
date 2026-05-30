import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import librosa
import imageio_ffmpeg
from tqdm import tqdm
import os
import sys
import random
import argparse

# Añadir directorio actual al path para importaciones
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from efectos_visuales import CamaraVirtual, MotorFX
from config import WIDTH, HEIGHT, ACTOS, NOTE_PALETTE
from visual_entities import TunelCuantico3D
from nucleo_visual import (
    simulacion_gray_scott,
    simulacion_ks,
    simulacion_gpe,
    simulacion_ondas,
    simulacion_cahn_hilliard,
    update_particles,
    simulacion_kdv
)

# Configuración FFmpeg
plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip

def generar_animacion_legacy(ruta_audio, nombre_salida_temp, fps=30, duracion=None, seed=None, allowed_engines=None, use_kaleido=True, use_flash=True, use_chroma=False):
    print(f"--- 1. Deconstruyendo Audio (Legacy Optimizada): {ruta_audio} ---")
    
    try:
        y, sr = librosa.load(ruta_audio, duration=duracion)
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return False
    
    if seed is not None:
        print(f"🌱 Usando Seed: {seed}")
        np.random.seed(seed)
        random.seed(seed)

    # Análisis DSP
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    hop_length = int(sr / fps)
    total_frames = int(len(y) / hop_length)
    
    # Features
    rms_perc = librosa.feature.rms(y=y_percussive, hop_length=hop_length)[0]
    rms_perc = rms_perc / (np.max(rms_perc) + 1e-6)
    rms_perc = np.resize(rms_perc, total_frames)
    
    rms_harm = librosa.feature.rms(y=y_harmonic, hop_length=hop_length)[0]
    rms_harm = rms_harm / (np.max(rms_harm) + 1e-6)
    rms_harm = np.resize(rms_harm, total_frames)
    
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    cent = np.log1p(cent)
    cent = (cent - np.min(cent)) / (np.max(cent) - np.min(cent) + 1e-6)
    cent = np.resize(cent, total_frames)

    chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, hop_length=hop_length)
    dom_note = np.argmax(chroma, axis=0)
    dom_note = np.resize(dom_note, total_frames)
    
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    contrast_mean = np.mean(contrast, axis=0)
    contrast_mean = (contrast_mean - np.min(contrast_mean)) / (np.max(contrast_mean) - np.min(contrast_mean) + 1e-6)
    contrast_mean = np.resize(contrast_mean, total_frames)

    print(f"--- 2. Inicializando Motor Físico (Double Buffering) ---")
    
    W, H = WIDTH, HEIGHT
    aspect_ratio = W / H
    gs_scale = 4
    gs_w, gs_h = W // gs_scale, H // gs_scale
    
    # --- BUFFERS (DOUBLE BUFFERING) ---
    # 1. Gray-Scott
    gs_U = np.ones((gs_h, gs_w), dtype=np.float32)
    gs_V = np.zeros((gs_h, gs_w), dtype=np.float32)
    gs_U_next = np.empty_like(gs_U); gs_V_next = np.empty_like(gs_V)
    
    # Semillas
    num_seeds = np.random.randint(5, 15)
    for _ in range(num_seeds):
        ry, rx = np.random.randint(0, gs_h), np.random.randint(0, gs_w)
        size = np.random.randint(5, 25)
        gs_V[max(0, ry-size):min(gs_h, ry+size), max(0, rx-size):min(gs_w, rx+size)] = np.random.uniform(0.4, 0.6)
    
    # 2. KS
    ks_u = np.zeros((gs_h, gs_w), dtype=np.float32) + np.random.normal(0, 0.1, (gs_h, gs_w)).astype(np.float32)
    ks_u_next = np.empty_like(ks_u)
    
    # 3. GPE
    gpe_r = np.exp(-(np.linspace(-2, 2, gs_w)**2)).astype(np.float32) * np.ones((gs_h, 1), dtype=np.float32)
    gpe_i = np.zeros_like(gpe_r)
    gpe_r_next = np.empty_like(gpe_r); gpe_i_next = np.empty_like(gpe_i)
    gpe_V = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # 4. Wave
    wave_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_prev = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_next = np.empty_like(wave_u)
    
    # 5. CH
    ch_u = np.random.uniform(-1, 1, (gs_h, gs_w)).astype(np.float32)
    ch_u_next = np.empty_like(ch_u)
    
    # 6. KdV (Solitones) - NUEVO
    kdv_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    kdv_u_next = np.empty_like(kdv_u)

    # 7. Partículas
    num_particles = 5000
    p_pos = np.random.rand(num_particles, 2).astype(np.float32) * [gs_w, gs_h]
    p_vel = np.zeros((num_particles, 2), dtype=np.float32)

    # Geometría (Lorenz)
    dpi = 100
    fig, ax = plt.subplots(figsize=(W/dpi, H/dpi), dpi=dpi)
    ax.set_axis_off()
    ax.set_xlim(-4 * aspect_ratio, 4 * aspect_ratio)
    ax.set_ylim(-4, 4)
    fig.subplots_adjust(0,0,1,1)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    linea_lorenz, = ax.plot([], [], lw=1.5, alpha=0.9)
    state_lorenz = np.array([0.1, 0.0, 0.0]) + np.random.uniform(-0.1, 0.1, 3)
    hist_lorenz = [[], [], []]

    camara = CamaraVirtual(W, H)
    fx = MotorFX(W, H)
    tunel = TunelCuantico3D(W, H)
    out = cv2.VideoWriter(nombre_salida_temp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (W, H))
    
    prev_kick = 0.0
    lookahead_frames = int(2.0 * fps)

    try:
        local_actos = ACTOS
        if allowed_engines:
            local_actos = [a for a in ACTOS if a['engine'] in allowed_engines]
            # Si seleccionaste un motor (ej: KDV) que no está en los ACTOS de config.py, lo agregamos manualmente
            present_engines = set(a['engine'] for a in local_actos)
            for eng in allowed_engines:
                if eng not in present_engines:
                    # Acto por defecto para el motor faltante
                    local_actos.append({'engine': eng, 'cmap': 'viridis', 'kaleido': False, 'p1': 0.1, 'p2': 0.1})
            if not local_actos: local_actos = ACTOS

        for i in tqdm(range(total_frames), desc="Renderizando Legacy"):
            # Datos Audio
            kick = rms_perc[i] if i < len(rms_perc) else 0
            harm = rms_harm[i] if i < len(rms_harm) else 0
            brillo = cent[i] if i < len(cent) else 0
            nota = int(dom_note[i]) % 12 if i < len(dom_note) else 0
            textura = contrast_mean[i] if i < len(contrast_mean) else 0
            
            # Impulso y Tensión
            kick_impulse = max(0.0, kick - prev_kick) * 5.0
            prev_kick = kick
            idx_futuro = min(i + lookahead_frames, total_frames - 1)
            tension = max(0.0, rms_perc[idx_futuro] - kick)
            
            # Selección Acto
            progreso = i / total_frames
            idx_acto = int(progreso * len(local_actos))
            if idx_acto >= len(local_actos): idx_acto = len(local_actos) - 1
            escena = local_actos[idx_acto]
            
            bg_layer = np.zeros((H, W, 3), dtype=np.uint8)
            img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
            
            # --- CONTROL CFL (DT DINÁMICO) ---
            # Si hay mucho caos (kick alto), reducimos el paso de tiempo para estabilidad
            dt_dynamic = 1.0 / (1.0 + kick * 2.0)

            # --- SIMULACIÓN ---
            if escena['engine'] == 'GS':
                f = escena['p1'] + (harm * 0.01)
                k = escena['p2'] - (kick * 0.005)
                
                # HOMEOSTASIS MEJORADA: Si el sistema muere o satura, revivirlo
                mean_v = np.mean(gs_V)
                if mean_v < 0.01 or mean_v > 0.6:
                    # Sembrar múltiples puntos de vida
                    for _ in range(5):
                        rx, ry = np.random.randint(0, gs_w), np.random.randint(0, gs_h)
                        gs_V[max(0, ry-10):min(gs_h, ry+10), max(0, rx-10):min(gs_w, rx+10)] = np.random.uniform(0.5, 0.9)

                for _ in range(8):
                    simulacion_gray_scott(gs_U, gs_V, gs_U_next, gs_V_next, 0.16, 0.08, f, k, 1.0 * dt_dynamic, None, tension)
                    gs_U, gs_U_next = gs_U_next, gs_U
                    gs_V, gs_V_next = gs_V_next, gs_V
                
                # Normalización segura
                max_v = np.max(gs_V)
                img_norm = gs_V / (max_v if max_v > 0.01 else 1.0)
                
            elif escena['engine'] == 'KS':
                dt_ks = escena['p1']
                if kick_impulse > 0.3: ks_u += np.random.normal(0, 0.5, ks_u.shape).astype(np.float32)
                
                # --- HOMEOSTASIS GLOBAL (KS) ---
                # Si está muy plano (std bajo) o explotado, reiniciar
                if np.std(ks_u) < 0.05 or np.max(np.abs(ks_u)) > 1e4:
                    ks_u[:] = np.random.normal(0, 0.1, ks_u.shape)

                for _ in range(4):
                    simulacion_ks(ks_u, ks_u_next, dt_ks * dt_dynamic)
                    ks_u, ks_u_next = ks_u_next, ks_u
                
                ks_blur = cv2.GaussianBlur(ks_u, (3, 3), 0)
                # Normalización suave con tanh para ver detalles sin saturar
                img_norm = 0.5 + 0.5 * np.tanh((ks_blur - np.mean(ks_blur)) * 0.5)
                
            elif escena['engine'] == 'GPE':
                g = escena['p1'] + (brillo * 4.0)
                gpe_V[:] = 0.1 * (1 + kick) * (np.linspace(-1, 1, gs_w, dtype=np.float32)**2)
                
                # --- HOMEOSTASIS GLOBAL (GPE) ---
                if np.any(np.isnan(gpe_r)) or np.max(np.abs(gpe_r)) > 1e4:
                    gpe_r[:] = np.exp(-(np.linspace(-2, 2, gs_w)**2))
                    gpe_i[:] = 0

                for _ in range(6):
                    simulacion_gpe(gpe_r, gpe_i, gpe_r_next, gpe_i_next, gpe_V, g, dt=0.002 * dt_dynamic)
                    gpe_r, gpe_r_next = gpe_r_next, gpe_r
                    gpe_i, gpe_i_next = gpe_i_next, gpe_i
                densidad = gpe_r**2 + gpe_i**2
                max_d = np.max(densidad)
                img_norm = densidad / (max_d if max_d > 1e-6 else 1.0)
            
            elif escena['engine'] == 'WAVE':
                damping = escena['p1']
                c2_dt2 = escena['p2'] * (1 + textura * 2) * dt_dynamic
                if kick_impulse > 0.4:
                    ry, rx = np.random.randint(1, gs_h-1), np.random.randint(1, gs_w-1)
                    wave_u[ry, rx] += np.random.uniform(-1, 1) * kick_impulse * 5
                
                # --- HOMEOSTASIS GLOBAL (WAVE) ---
                if np.any(np.isnan(wave_u)) or np.max(np.abs(wave_u)) > 1e3:
                    wave_u[:] = 0
                    wave_prev[:] = 0
                
                simulacion_ondas(wave_u, wave_prev, wave_next, damping, c2_dt2, None)
                wave_prev, wave_u = wave_u, wave_next
                
                # Visualización de ondas usando tanh para mejor rango dinámico
                img_norm = np.tanh(np.abs(wave_u) * 0.5)

            elif escena['engine'] == 'CH':
                gamma = escena['p1']
                mobility = escena['p2']
                for _ in range(4):
                    simulacion_cahn_hilliard(ch_u, ch_u_next, dt=0.05 * dt_dynamic, gamma=gamma, mobility=mobility)
                    ch_u, ch_u_next = ch_u_next, ch_u
                img_norm = (ch_u + 1) / 2.0
            
            elif escena['engine'] == 'KDV':
                alpha = escena['p1'] * 6.0
                beta = escena['p2'] * 2.0
                if kick_impulse > 0.4:
                    ry, rx = np.random.randint(2, gs_h-2), np.random.randint(2, gs_w-2)
                    kdv_u[ry-2:ry+2, rx-2:rx+2] += np.random.uniform(-2, 2)
                
                # Homeostasis
                if np.max(np.abs(kdv_u)) > 20.0: kdv_u *= 0.5
                
                for _ in range(4):
                    simulacion_kdv(kdv_u, kdv_u_next, dt=0.05 * dt_dynamic, alpha=alpha, beta=beta)
                    kdv_u, kdv_u_next = kdv_u_next, kdv_u
                
                # Normalización robusta
                val_min, val_max = np.min(kdv_u), np.max(kdv_u)
                denom = val_max - val_min
                img_norm = (kdv_u - val_min) / (denom if denom > 1e-6 else 1.0)

            elif escena['engine'] == 'TUNNEL':
                # Fondo oscuro con ruido estelar muy sutil para el túnel
                img_norm = np.random.rand(gs_h, gs_w).astype(np.float32) * 0.05

            elif escena['engine'] == 'PARTICLES':
                grad_y, grad_x = np.gradient(img_norm) # Usa el fluido del frame anterior
                force_field = np.stack((grad_x, grad_y), axis=2).astype(np.float32) * 80.0 * (1 + harm)
                
                p_damp = escena['p1']
                p_max_speed = escena['p2']
                update_particles(p_pos, p_vel, force_field, gs_w, gs_h, p_damp, p_max_speed, None)

                img_particles = np.zeros((gs_h, gs_w), dtype=np.float32)
                for pi in range(num_particles):
                    px, py = int(p_pos[pi, 0]), int(p_pos[pi, 1])
                    if 0 <= px < gs_w and 0 <= py < gs_h:
                        img_particles[py, px] = 0.8
                
                img_norm = cv2.GaussianBlur(img_particles, (3,3), 0)

            # --- RENDERIZADO y POST-PROCESADO ---
            
            # Mapeo de color y normalización
            cmap = plt.get_cmap(escena.get('cmap', 'viridis'))
            img_norm = np.nan_to_num(img_norm)
            # Gamma menos agresivo (0.8 a 1.8) para no oscurecer todo
            img_norm = np.power(np.clip(img_norm, 0, 1), 0.8 + textura * 1.0)
            frame_sm = (cmap(img_norm)[:, :, :3] * 255).astype(np.uint8)

            if use_kaleido and escena.get('kaleido', False):
                frame_sm = fx.aplicar_caleidoscopio(frame_sm, slices=6, intensity=harm)
            
            frame = cv2.resize(frame_sm, (W, H), interpolation=cv2.INTER_LINEAR)
            
            # Dibujar Túnel 3D (Warp Speed) si el acto lo requiere
            if escena['engine'] == 'TUNNEL':
                tunel.update_and_draw(frame, speed_base=15.0, kick=kick)

            if use_chroma:
                color_nota = np.array(NOTE_PALETTE[nota])
                frame = cv2.addWeighted(frame, 0.7, np.full_like(frame, color_nota), 0.3, 0)
            
            # Feedback reducido para evitar "lavado" de imagen
            frame = fx.feedback_zoom(frame, decay=0.80 - harm * 0.1, zoom=1.005 + kick * 0.01)
            if use_flash and kick_impulse > 0.5:
                frame = fx.aplicar_bloom(frame, intensity=kick_impulse * 0.3)
            
            camara.update(energy=brillo, kick=kick, snare=textura)
            frame = camara.aplicar(frame)
            
            out.write(frame)

        out.release()
        plt.close(fig)
        return True

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False

def unir_video_con_musica(video_path, audio_path, output_path, duracion=None):
    print(f"--- 3. Renderizando Audio Final ---")
    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        if duracion:
            if hasattr(audio, 'subclipped'):
                audio = audio.subclipped(0, duracion)
                video = video.subclipped(0, duracion)
            else:
                audio = audio.subclip(0, duracion)
                video = video.subclip(0, duracion)
            
        if hasattr(video, 'with_audio'):
            final = video.with_audio(audio)
        else:
            final = video.set_audio(audio)
            
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)
    except Exception as e:
        print(f"Error uniendo audio: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", default="Rebeldía Cosmica - Sol Que se Va.flac", help="Ruta del archivo de audio")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--engines", nargs="+", default=None)
    parser.add_argument("--no-kaleido", action="store_true")
    parser.add_argument("--no-flash", action="store_true")
    parser.add_argument("--chroma", action="store_true")
    parser.add_argument("--no-spirits", action="store_true")
    
    args, unknown = parser.parse_known_args()
    
    temp_file = "temp_legacy.mp4"
    final_file = "output_legacy.mp4"
    
    success = generar_animacion_legacy(args.audio, temp_file, fps=30, duracion=args.duration, 
                                       seed=args.seed, allowed_engines=args.engines, 
                                       use_kaleido=not args.no_kaleido, use_flash=not args.no_flash, 
                                       use_chroma=args.chroma)
    
    if success:
        unir_video_con_musica(temp_file, args.audio, final_file, duracion=args.duration)