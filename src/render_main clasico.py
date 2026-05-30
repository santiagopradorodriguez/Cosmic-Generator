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
import random

# Añadir carpeta src al path para poder importar módulos
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar nuestros módulos
from efectos_visuales import CamaraVirtual, MotorFX
from config import WIDTH, HEIGHT # Importar resolución global
from nucleo_visual import (
    simulacion_gray_scott,
    simulacion_ks,
    simulacion_gpe,
    simulacion_ondas,
    simulacion_cahn_hilliard,
    update_particles
)



# Configuración FFmpeg

plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()

try:

    from moviepy import VideoFileClip, AudioFileClip

except ImportError:

    from moviepy.editor import VideoFileClip, AudioFileClip


# ==========================================

# GENERADOR DE ANIMACIÓN

# ==========================================

def generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps=30, duracion=None, seed=None, allowed_engines=None, use_kaleido=True, use_flash=True, use_chroma=False):

   

    print(f"--- 1. Deconstruyendo Audio: {ruta_audio} ---")

   

    # A) ANÁLISIS DE AUDIO AVANZADO (HPSS)

    try:

        y, sr = librosa.load(ruta_audio, duration=duracion)

    except FileNotFoundError:

        print("Error: Archivo no encontrado.")

        return False
    
    if seed is not None:
        print(f"🌱 Usando Seed: {seed}")
        np.random.seed(seed)
        random.seed(seed)



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

    # 4. Dominant Note (Chroma) - Para colorear según la nota musical
    chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, hop_length=hop_length)
    dom_note = np.argmax(chroma, axis=0)
    dom_note = np.resize(dom_note, total_frames)

    # 5. Spectral Contrast (Textura) - Para distorsión visual
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    contrast_mean = np.mean(contrast, axis=0)
    contrast_mean = (contrast_mean - np.min(contrast_mean)) / (np.max(contrast_mean) - np.min(contrast_mean) + 1e-6)
    contrast_mean = np.resize(contrast_mean, total_frames)



    print(f"--- 2. Inicializando Motor de Física (Numba Accelerated) ---")

   

    # Configuración de Video

    W, H = 1280, 720 # HD (Full HD 1920x1080 es posible pero tarda más)

    aspect_ratio = W / H
   
    # --- INICIALIZACIÓN DE BUFFERS FÍSICOS ---
    # Resolución reducida para la simulación (se escala después)
    gs_scale = 4
    gs_w, gs_h = W // gs_scale, H // gs_scale
    
    # 1. Gray-Scott (Turing)
    U = np.ones((gs_h, gs_w), dtype=np.float32)
    V = np.zeros((gs_h, gs_w), dtype=np.float32)
    U_next = np.zeros_like(U); V_next = np.zeros_like(V)
    
    # Sembrar perturbación inicial ALEATORIA (Varios puntos al azar)
    num_seeds = np.random.randint(5, 15)
    for _ in range(num_seeds):
        ry, rx = np.random.randint(0, gs_h), np.random.randint(0, gs_w)
        size = np.random.randint(5, 25)
        V[max(0, ry-size):min(gs_h, ry+size), max(0, rx-size):min(gs_w, rx+size)] = np.random.uniform(0.4, 0.6)
   
    Da, Db = 0.16, 0.08
   
    # 2. Kuramoto-Sivashinsky (Caos)
    ks_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    ks_u_next = np.zeros_like(ks_u)
    # Ruido inicial
    ks_u += np.random.normal(0, 0.1, (gs_h, gs_w))
    
    # 3. Gross-Pitaevskii (Cuántica)
    gpe_psi_r = np.exp(-(np.linspace(-2, 2, gs_w)**2)) * np.ones((gs_h, 1)) # Solitón inicial
    gpe_psi_r = gpe_psi_r.astype(np.float32)
    gpe_psi_i = np.zeros_like(gpe_psi_r)
    gpe_psi_r_next = np.zeros_like(gpe_psi_r)
    gpe_psi_i_next = np.zeros_like(gpe_psi_i)
    gpe_V = np.zeros((gs_h, gs_w), dtype=np.float32) # Potencial
    
    # 4. Ondas (Wave Equation) - NUEVO
    wave_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_u_prev = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_u_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # 5. Cahn-Hilliard (Aceite/Agua) - NUEVO
    ch_u = np.random.uniform(-1, 1, (gs_h, gs_w)).astype(np.float32)
    ch_u_next = np.zeros_like(ch_u)
    
    # 6. Partículas de Flujo - NUEVO
    num_particles = 5000
    p_pos = np.random.rand(num_particles, 2) * [gs_w, gs_h]
    p_vel = np.zeros((num_particles, 2), dtype=np.float32)
    p_pos = p_pos.astype(np.float32)
    p_vel = p_vel.astype(np.float32)

    # --- SISTEMA GEOMETRÍA (LORENZ) ---
    # Usamos esto SOLO para líneas vectoriales precisas (Lorenz, Cubos)
    dpi = 100
    fig, ax = plt.subplots(figsize=(W/dpi, H/dpi), dpi=dpi)
    ax.set_axis_off()
    ax.set_xlim(-4 * aspect_ratio, 4 * aspect_ratio)
    ax.set_ylim(-4, 4)
    fig.subplots_adjust(0,0,1,1)
    # Fondo transparente para superponer
    fig.patch.set_alpha(0.0)
    fig.set_facecolor('none')
    ax.patch.set_alpha(0.0) # Asegurar que el fondo de los ejes también sea transparente
    ax.set_facecolor('none')
   
    # Atractor de Lorenz (Objeto 3D)
    linea_lorenz, = ax.plot([], [], lw=1.5, alpha=0.9)
    state_lorenz = np.array([0.1, 0.0, 0.0]) + np.random.uniform(-0.1, 0.1, 3)
    hist_lorenz = [[], [], []]

    # --- INICIALIZAR RENDER ---
    camara = CamaraVirtual(W, H)
    fx = MotorFX(W, H)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombre_salida_temp, fourcc, fps, (W, H))
   
    # ==========================================
    # DEFINICIÓN DE 30 ACTOS VISUALES (EXTENDIDO)
    # ==========================================
    # 'engine': GS, KS, GPE, WAVE, CH, PARTICLES
    # 'color_mode': 'fixed' (usa cmap) o 'chroma' (usa notas musicales)
    ACTOS = [
        # INTRO (Ambiente)
        {'engine': 'CH',   'cmap': 'bone',          'kaleido': False, 'p1': 0.5,   'p2': 1.0},   # Burbujas oscuras
        {'engine': 'GS',   'cmap': 'magma',         'kaleido': False, 'p1': 0.055, 'p2': 0.062}, # Manchas clásicas
        {'engine': 'WAVE', 'cmap': 'ocean',         'kaleido': True,  'p1': 0.99,  'p2': 0.5},   # Océano espejado
        {'engine': 'PARTICLES', 'cmap': 'inferno',  'kaleido': False, 'p1': 0.9,   'p2': 2.0},   # Flujo de partículas
        {'engine': 'KS',   'cmap': 'inferno',       'kaleido': False, 'p1': 0.05,  'p2': 0},     # Fuego lento
        
        # BUILD-UP (Crecimiento)
        {'engine': 'GPE',  'cmap': 'twilight',      'kaleido': False, 'p1': 2.0,   'p2': 0},     # Nebulosa
        {'engine': 'GS',   'cmap': 'viridis',       'kaleido': True,  'p1': 0.029, 'p2': 0.057}, # Corales
        {'engine': 'CH',   'cmap': 'spring',        'kaleido': True,  'p1': 0.8,   'p2': 2.0},   # Células rosas
        {'engine': 'KS',   'cmap': 'winter',        'kaleido': True,  'p1': 0.02,  'p2': 0},     # Hielo
        {'engine': 'WAVE', 'cmap': 'seismic',       'kaleido': False, 'p1': 0.98,  'p2': 0.8},   # Interferencia
        
        # DROP 1 (Energía)
        {'engine': 'GPE',  'cmap': 'hsv',           'kaleido': True,  'p1': 4.0,   'p2': 0},     # Psicodelia
        {'engine': 'PARTICLES', 'cmap': 'rainbow',  'kaleido': True,  'p1': 0.85,  'p2': 5.0},   # Explosión partículas
        {'engine': 'GS',   'cmap': 'plasma',        'kaleido': False, 'p1': 0.018, 'p2': 0.050}, # Espirales
        {'engine': 'KS',   'cmap': 'nipy_spectral', 'kaleido': True,  'p1': 0.1,   'p2': 0},     # Ácido
        {'engine': 'WAVE', 'cmap': 'Blues',         'kaleido': False, 'p1': 0.95,  'p2': 0.2},   # Lluvia
        
        # PUENTE (Misterio)
        {'engine': 'CH',   'cmap': 'copper',        'kaleido': False, 'p1': 0.3,   'p2': 0.5},   # Metal líquido
        {'engine': 'GPE',  'cmap': 'bone',          'kaleido': False, 'p1': -2.0,  'p2': 0},     # Materia oscura
        {'engine': 'GS',   'cmap': 'spring',        'kaleido': True,  'p1': 0.025, 'p2': 0.060}, # Mitosis
        {'engine': 'KS',   'cmap': 'afmhot',        'kaleido': False, 'p1': 0.01,  'p2': 0},     # Lava
        {'engine': 'WAVE', 'cmap': 'jet',           'kaleido': True,  'p1': 0.90,  'p2': 1.0},   # Tormenta
        
        # DROP 2 (Caos Total)
        {'engine': 'PARTICLES', 'cmap': 'cool',     'kaleido': True,  'p1': 0.9,   'p2': 8.0},   # Hipervelocidad
        {'engine': 'GPE',  'cmap': 'cool',          'kaleido': True,  'p1': 1.0,   'p2': 0},     # Eter
        {'engine': 'GS',   'cmap': 'cividis',       'kaleido': False, 'p1': 0.078, 'p2': 0.061}, # Gusanos
        {'engine': 'KS',   'cmap': 'gist_ncar',     'kaleido': True,  'p1': 0.2,   'p2': 0},     # Glitch
        {'engine': 'WAVE', 'cmap': 'GnBu',          'kaleido': False, 'p1': 0.995, 'p2': 0.1},   # Calma
        
        # OUTRO
        {'engine': 'CH',   'cmap': 'ocean',         'kaleido': False, 'p1': 0.6,   'p2': 0.2},   # Mar profundo
        {'engine': 'GS',   'cmap': 'rainbow',       'kaleido': True,  'p1': 0.030, 'p2': 0.055}, # Final simétrico
        {'engine': 'PARTICLES', 'cmap': 'gray',     'kaleido': False, 'p1': 0.95,  'p2': 1.0},   # Polvo estelar
        {'engine': 'GPE',  'cmap': 'magma',         'kaleido': False, 'p1': 0.5,   'p2': 0},     # Desvanecimiento
        {'engine': 'WAVE', 'cmap': 'binary',        'kaleido': False, 'p1': 0.99,  'p2': 0.01}   # Silencio
    ]


    try:

        # Filtrar ACTOS
        local_actos = ACTOS
        if allowed_engines:
            local_actos = [a for a in ACTOS if a['engine'] in allowed_engines]
            if not local_actos:
                print("⚠️ Advertencia: Ningún motor seleccionado. Usando todos.")
                local_actos = ACTOS

        for i in tqdm(range(total_frames), desc="Renderizando Física + Geometría"):

           

            # --- DATOS DE AUDIO ---

            kick = rms_perc[i] if i < len(rms_perc) else 0

            harm = rms_harm[i] if i < len(rms_harm) else 0
            brillo = cent[i] if i < len(cent) else 0
            nota = dom_note[i] if i < len(dom_note) else 0
            textura = contrast_mean[i] if i < len(contrast_mean) else 0
           
            # ============================
            # CAPA 1: MULTIVERSO FÍSICO (20 ACTOS)
            # ============================
            
            # Selector de escena basado en el tiempo
            progreso = i / total_frames
            idx_acto = int(progreso * len(local_actos))
            if idx_acto >= len(local_actos): idx_acto = len(local_actos) - 1
            escena = local_actos[idx_acto]
            
            bg_layer = np.zeros((H, W, 3), dtype=np.uint8)
            img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
            
            # --- CONTROL CFL (DT DINÁMICO) ---
            # Si hay mucho caos (kick alto), reducimos el paso de tiempo para estabilidad
            dt_dynamic = 1.0 / (1.0 + kick * 2.0)

            # --- EJECUTAR MOTOR SEGÚN LA ESCENA ---
            if escena['engine'] == 'GS':
                # Gray-Scott
                f = escena['p1'] + (harm * 0.01)
                k = escena['p2'] - (kick * 0.005)
                
                # HOMEOSTASIS: Si el sistema muere (todo 0 o todo 1), reinyectar vida
                if np.mean(V) < 0.001 or np.mean(V) > 0.99:
                     V[gs_h//2-20:gs_h//2+20, gs_w//2-20:gs_w//2+20] = np.random.uniform(0.4, 0.6, (40, 40))

                for _ in range(8):
                    simulacion_gray_scott(U, V, U_next, V_next, Da, Db, f, k, dt=1.0 * dt_dynamic)
                    U, U_next = U_next, U
                    V, V_next = V_next, V
                img_norm = V / (np.max(V) + 1e-6)
                
            elif escena['engine'] == 'KS':
                # Kuramoto-Sivashinsky
                dt_ks = escena['p1']
                if kick > 0.5: ks_u += np.random.normal(0, 0.5, ks_u.shape)
                
                # --- HOMEOSTASIS GLOBAL (KS) ---
                if np.any(np.isnan(ks_u)) or np.max(np.abs(ks_u)) > 1e4:
                    ks_u[:] = np.random.normal(0, 0.1, ks_u.shape)
                    ks_u_next[:] = 0
                
                for _ in range(4):
                    simulacion_ks(ks_u, ks_u_next, dt=dt_ks * dt_dynamic)
                    ks_u, ks_u_next = ks_u_next, ks_u
                ks_blur = cv2.GaussianBlur(ks_u, (3, 3), 0)
                
                denom = np.max(ks_blur) - np.min(ks_blur)
                if denom < 1e-6: img_norm = np.zeros_like(ks_blur)
                else: img_norm = (ks_blur - np.min(ks_blur)) / denom
                
            elif escena['engine'] == 'GPE':
                # Gross-Pitaevskii
                gpe_V[:] = 0.1 * (1 + kick) * (np.linspace(-1, 1, gs_w)**2)
                g = escena['p1']
                for _ in range(10):
                    simulacion_gpe(gpe_psi_r, gpe_psi_i, gpe_psi_r_next, gpe_psi_i_next, gpe_V, g, dt=0.002 * dt_dynamic)
                    gpe_psi_r, gpe_psi_r_next = gpe_psi_r_next, gpe_psi_r
                    gpe_psi_i, gpe_psi_i_next = gpe_psi_i_next, gpe_psi_i
                
                # --- HOMEOSTASIS GLOBAL (GPE) ---
                if np.any(np.isnan(gpe_psi_r)) or np.max(np.abs(gpe_psi_r)) > 1e4:
                    gpe_psi_r[:] = np.exp(-(np.linspace(-2, 2, gs_w)**2)).reshape(-1, 1)
                    gpe_psi_i[:] = 0

                densidad = gpe_psi_r**2 + gpe_psi_i**2
                img_norm = densidad / (np.max(densidad) + 1e-6)
                
            elif escena['engine'] == 'WAVE':
                # Ecuación de Ondas
                damping = escena['p1']
                c2 = escena['p2'] * dt_dynamic
                # Inyectar gotas con el audio
                if kick > 0.4 or harm > 0.6:
                    ry, rx = np.random.randint(1, gs_h-1), np.random.randint(1, gs_w-1)
                    wave_u[ry, rx] += np.random.uniform(-1, 1) * kick
                
                # --- HOMEOSTASIS GLOBAL (WAVE) ---
                if np.any(np.isnan(wave_u)) or np.max(np.abs(wave_u)) > 1e3:
                    wave_u[:] = 0
                    wave_u_prev[:] = 0

                simulacion_ondas(wave_u, wave_u_prev, wave_u_next, damping, c2)
                wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
                
                img_norm = 0.5 + (wave_u * 0.5) # Centrar en gris medio
                img_norm = np.clip(img_norm, 0, 1)
                
            elif escena['engine'] == 'CH':
                # Cahn-Hilliard
                gamma = escena['p1'] * 0.01
                mobility = escena['p2'] * (1 + kick)
                for _ in range(5):
                    simulacion_cahn_hilliard(ch_u, ch_u_next, dt=0.05 * dt_dynamic, gamma=gamma, mobility=mobility)
                    ch_u, ch_u_next = ch_u_next, ch_u
                img_norm = (ch_u + 1) / 2 # Normalizar de -1,1 a 0,1
                
            elif escena['engine'] == 'PARTICLES':
                # Sistema de Partículas
                # Usamos el campo de ondas o ruido como fuerza
                damp = escena['p1']
                speed = escena['p2'] * (1 + kick * 2)
                
                # Generar campo de fuerza basado en ruido Perlin (simulado con ondas suaves)
                # Ojo: Usamos wave_u temporalmente para generar gradientes
                
                # --- SANITIZACIÓN (Evitar NaNs) ---
                wave_u = np.nan_to_num(wave_u, nan=0.0)
                wave_u_prev = np.nan_to_num(wave_u_prev, nan=0.0)

                # FIX: Limitar valores para evitar Overflow (Explosión numérica)
                wave_u = np.clip(wave_u, -50.0, 50.0)
                wave_u_prev = np.clip(wave_u_prev, -50.0, 50.0)
                
                simulacion_ondas(wave_u, wave_u_prev, wave_u_next, 0.99, 0.1 * dt_dynamic)
                wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
                
                grad_y, grad_x = np.gradient(wave_u)
                force_field = np.stack((grad_x, grad_y), axis=2) * 50.0
                force_field = np.nan_to_num(force_field, nan=0.0)
                
                p_pos, p_vel = update_particles(p_pos, p_vel, force_field, gs_w, gs_h, damp, speed)
                
                # Recuperar partículas perdidas (NaNs)
                if np.isnan(p_pos).any():
                    p_pos = np.nan_to_num(p_pos, nan=gs_w/2)
                    p_vel = np.nan_to_num(p_vel, nan=0.0)

                # Dibujar partículas en img_norm
                img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
                for pi in range(num_particles):
                    px, py = int(p_pos[pi, 0]), int(p_pos[pi, 1])
                    if 0 <= px < gs_w and 0 <= py < gs_h:
                        img_norm[py, px] = 1.0
                # Blur para que parezcan luces
                img_norm = cv2.GaussianBlur(img_norm, (3, 3), 0)

            # --- COLOREADO Y EFECTOS ---
            cmap = plt.get_cmap(escena['cmap'])
            bg_layer = (cmap(img_norm)[:, :, :3] * 255).astype(np.uint8)
            
            # --- COLOR DINÁMICO POR NOTA (CROMESTESIA) ---
            # Solo se activa si se seleccionó en el lanzador (--chroma)
            if use_chroma:
                # Mapeamos la nota (0-11) al círculo cromático (Hue 0-179)
                hue_nota = int((nota / 12.0) * 179)
                
                # Creamos el color BGR correspondiente a la nota
                color_pixel = np.uint8([[[hue_nota, 255, 255]]])
                color_nota_bgr = cv2.cvtColor(color_pixel, cv2.COLOR_HSV2BGR)[0, 0]
                
                # Factor de mezcla: Base suave + Intensidad armónica
                # Esto hace que el color "respire" con la música
                blend_factor = 0.15 + (harm * 0.35) 
                if kick > 0.5: blend_factor += 0.2 # Golpe de color con el bombo
                blend_factor = np.clip(blend_factor, 0.0, 0.8)
                
                # Aplicar tinte
                color_layer = np.full_like(bg_layer, color_nota_bgr)
                bg_layer = cv2.addWeighted(bg_layer, 1.0 - blend_factor, color_layer, blend_factor, 0)
            
            # --- EFECTO CALEIDOSCOPIO (MANDALA) ---
            if use_kaleido:
                bg_layer = fx.kaleidoscopio(bg_layer, active=escena['kaleido'])

            # Escalar a HD
            bg_layer = cv2.resize(bg_layer, (W, H), interpolation=cv2.INTER_LINEAR)
           
            # Oscurecer el fondo si la música es baja
            bg_layer = (bg_layer * (0.3 + harm * 0.7)).astype(np.uint8)

            # ============================
            # CAPA 2: GEOMETRÍA (LORENZ)
            # ============================
            
            # Verificar si Lorenz está permitido
            use_lorenz = ('LORENZ' in allowed_engines) if allowed_engines else True
            
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
            if use_lorenz:
                scale_l = 0.05
                linea_lorenz.set_data(pts_rot[:, 0] * scale_l, pts_rot[:, 2] * scale_l - 1.5) # Centrar aprox
            else:
                linea_lorenz.set_data([], [])
           
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
            # Mezcla Alpha Correcta (Evita que el fondo negro de Matplotlib tape la física)
            # Normalizar alpha a 0.0 - 1.0
            alpha = buf[:, :, 3].astype(np.float32) / 255.0
            alpha_3c = cv2.merge([alpha, alpha, alpha])
            
            # Fórmula: Final = Overlay * Alpha + Fondo * (1 - Alpha)
            fg = overlay_layer.astype(np.float32)
            bg = bg_layer.astype(np.float32)
            frame_final = (fg * alpha_3c + bg * (1.0 - alpha_3c)).astype(np.uint8)
           
            # ============================
            # POST-PROCESADO (FX)
            # ============================
            # 1. Feedback Temporal (Estelas)
            frame_final = fx.feedback_temporal(frame_final, decay=0.85 + (harm * 0.1))
           
            # 2. Cámara Virtual (Movimiento)
            camara.update(energy=harm, kick=kick, snare=rms_perc[i])
            frame_final = camara.aplicar(frame_final)
           
            # 3. Bloom (Brillo en los picos altos)
            if kick > 0.5 and use_flash:
                frame_final = fx.aplicar_bloom(frame_final, intensity=kick)
               
            # 4. Aberración Cromática (Glitch basado en textura/ruido de la canción)
            if use_flash:
                frame_final = fx.aberracion_cromatica(frame_final, strength=kick * 5 + textura * 10)

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
        if hasattr(audio, 'subclipped'):
            audio = audio.subclipped(0, duracion)
            video = video.subclipped(0, duracion)
        else:
            audio = audio.subclip(0, duracion)
            video = video.subclip(0, duracion)
   
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
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", default="Rebeldía Cosmica - Sol Que se Va.flac")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--engines", nargs="+", default=None)
    parser.add_argument("--no-spirits", action="store_true")
    parser.add_argument("--no-kaleido", action="store_true")
    parser.add_argument("--no-flash", action="store_true")
    parser.add_argument("--chroma", action="store_true") # Opción para activar color por nota
    args = parser.parse_args()

    CANCION = args.audio
    TEMP = "temp_legacy.mp4"
    FINAL = "Rebeldia_Cosmica_Legacy.mp4"
   
    DURACION_TEST = args.duration
   
    if generar_animacion_god_mode(CANCION, TEMP, fps=30, duracion=DURACION_TEST, seed=args.seed, allowed_engines=args.engines, use_kaleido=not args.no_kaleido, use_flash=not args.no_flash, use_chroma=args.chroma):
        unir_video_con_musica(TEMP, CANCION, FINAL, duracion=DURACION_TEST)