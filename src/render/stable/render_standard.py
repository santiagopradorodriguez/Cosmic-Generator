"""
(C) Rebeldía Cósmica | Creado por Santiago Prado
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import imageio_ffmpeg
from tqdm import tqdm
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))) # Añadir src al path

# Importar nuestros módulos
from core.efectos_visuales import CamaraVirtual, MotorFX
from core.config import WIDTH, HEIGHT, FPS, ACTOS, NOTE_PALETTE
from audio.audio_analyzer import analizar_audio
from core.video_utils import unir_video_con_musica
from core.visual_entities import EspirituProcedural, SuperformaProcedural, LorenzSwarm, GeneradorHojas

from core.nucleo_visual import (
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

def generar_animacion_god_mode(ruta_audio, nombre_salida_temp, fps=30, duracion=None, seed=None, allowed_engines=None, use_spirits=True, use_kaleido=True, use_flash=True, use_chroma=False, use_lyrics=False, global_cmap=None, progress_callback=None):
    """
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
    global_cmap : str, opcional
        Nombre de un colormap de matplotlib (ej. 'viridis', 'magma') que forzará una paleta global, ignorando las de la escena. Valor por defecto: None.
    progress_callback : callable, opcional
        Función de retroalimentación invocada en cada fotograma. Su firma debe ser `progress_callback(frame_actual, total_frames)`. Valor por defecto: None.

    Retorna:
    --------
    bool
        Devuelve True si la generación y escritura del video se completó con éxito. False si hubo algún error crítico o falla en el análisis.
    """
    # 1. Análisis de Audio
    audio_data = analizar_audio(ruta_audio, fps, duracion)
    if not audio_data:
        return False
    
    total_frames = audio_data['total_frames']

    if seed is not None:
        print(f"Usando Seed: {seed}")
        np.random.seed(seed)

    # 1.5 Motor de Letras (Lyrics)
    lyrics_engine = None
    if use_lyrics:
        try:
            from audio.motor_lyrics import LyricsEngine
            print("Inicializando Motor de Lyrics (Stable-TS)...")
            lyrics_engine = LyricsEngine(ruta_audio, max_duration=duracion)
        except Exception as e:
            print(f"Advertencia: Error cargando LyricsEngine: {e}")

    print(f"--- 2. Inicializando Motor de Física (Numba Accelerated) ---")

    W, H = WIDTH, HEIGHT
    aspect_ratio = WIDTH / HEIGHT
   
    # --- INICIALIZACIÓN DE BUFFERS FÍSICOS ---
    # Resolución reducida para la simulación (se escala después)
    gs_scale = 4
    gs_w, gs_h = WIDTH // gs_scale, HEIGHT // gs_scale
    
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
    
    # 7. KdV (Solitones) - NUEVO
    kdv_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    kdv_u_next = np.zeros_like(kdv_u)

    # --- INICIALIZAR NUEVOS ELEMENTOS (OPENCV PURO) ---
    lorenz_swarm = LorenzSwarm(WIDTH, HEIGHT, num_attractors=3) # MOD: Max 3
    gen_hojas = GeneradorHojas(WIDTH, HEIGHT)
    
    # --- INICIALIZAR GEOMETRÍA SAGRADA ---
    superforma = SuperformaProcedural(WIDTH, HEIGHT)
    
    # --- INICIALIZAR ESPÍRITUS ---
    # Creamos 7 entidades con semillas aleatorias para que sean distintas
    espiritus = []
    num_espiritus = 0
    if use_spirits:
        num_espiritus = 7
        espiritus = [EspirituProcedural(WIDTH, HEIGHT, seed_val=i*100) for i in range(num_espiritus)]
        # Posiciones distribuidas
        pos_espiritus = np.linspace(-5.0, 5.0, num_espiritus)
    
    # Variable para la rotación de color acumulativa
    hue_accumulator = 0.0

    # --- INICIALIZAR RENDER ---
    camara = CamaraVirtual(WIDTH, HEIGHT)
    fx = MotorFX(WIDTH, HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombre_salida_temp, fourcc, fps, (WIDTH, HEIGHT))
   
    # Estado para aleatoriedad de escenas
    prev_idx_acto = -1
    scene_flags = {'lorenz': False, 'leaves': False, 'superforma': False}

    try:
        # Filtrar ACTOS según motores permitidos
        local_actos = ACTOS
        if allowed_engines:
            local_actos = [a for a in ACTOS if a['engine'] in allowed_engines]
            
            # FIX: Inyectar motores seleccionados que no estén en ACTOS
            present_engines = set(a['engine'] for a in local_actos)
            for eng in allowed_engines:
                if eng not in present_engines:
                    # Inyectar acto genérico
                    local_actos.append({'engine': eng, 'cmap': 'viridis', 'kaleido': False, 'p1': 0.1, 'p2': 0.1})

            if not local_actos:
                print("⚠️ Advertencia: Ningún motor seleccionado coincide con ACTOS. Usando todos.")
                local_actos = ACTOS

        for i in tqdm(range(total_frames), desc="Renderizando Física + Geometría"):
            if progress_callback:
                progress_callback(i, total_frames)

            # --- DATOS DE AUDIO ---
            kick = audio_data['rms_perc'][i] if i < len(audio_data['rms_perc']) else 0
            harm = audio_data['rms_harm'][i] if i < len(audio_data['rms_harm']) else 0
            nota = audio_data['dom_note'][i] if i < len(audio_data['dom_note']) else 0
            textura = audio_data['contrast_mean'][i] if i < len(audio_data['contrast_mean']) else 0
            cymbals_val = audio_data['cymbals'][i] if i < len(audio_data['cymbals']) else 0
            
            # Sanitización extra para la nota (asegurar rango 0-11)
            nota = int(nota) % 12
           
            # ============================
            # CAPA 1: MULTIVERSO FÍSICO (20 ACTOS)
            # ============================
            
            # Selector de escena basado en el tiempo
            progreso = i / total_frames
            idx_acto = int(progreso * len(local_actos))
            if idx_acto >= len(local_actos): idx_acto = len(local_actos) - 1
            escena = local_actos[idx_acto]

            # MOD: Aleatoriedad al cambiar de escena
            if idx_acto != prev_idx_acto:
                prev_idx_acto = idx_acto
                # Solo activar Lorenz/IFS si están permitidos
                use_lorenz = ('lorenz' in allowed_engines) if allowed_engines else True
                use_geometry = ('ifs' in allowed_engines) if allowed_engines else True
                scene_flags['lorenz'] = (np.random.rand() < 0.3) and use_lorenz
                scene_flags['leaves'] = np.random.rand() < 0.3
                scene_flags['superforma'] = (np.random.rand() < 0.4) and use_geometry
            
            
            bg_layer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
            
            # --- CONTROL CFL (DT DINÁMICO) ---
            # Si hay mucho caos (kick alto), reducimos el paso de tiempo para estabilidad
            dt_dynamic = 1.0 / (1.0 + kick * 2.0)

            # --- EJECUTAR MOTOR SEGÚN LA ESCENA ---
            if escena['engine'] == 'GS':
                # Gray-Scott
                # SINESTESIA DE FORMA: La textura del sonido define la "biología"
                # Sonido suave (textura baja) = Manchas (f alto)
                # Sonido rugoso (textura alta) = Gusanos/Caos (f bajo)
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
                
                # HOMEOSTASIS: Si KS explota, reiniciar
                if np.max(np.abs(ks_u)) > 1e3 or np.any(np.isnan(ks_u)):
                    ks_u = np.zeros_like(ks_u) + np.random.normal(0, 0.1, ks_u.shape)
                
                for _ in range(4):
                    simulacion_ks(ks_u, ks_u_next, dt=dt_ks * dt_dynamic)
                    ks_u, ks_u_next = ks_u_next, ks_u
                
                # FIX: Sanitización de NaNs/Infs para evitar RuntimeWarning
                ks_u = np.nan_to_num(ks_u, nan=0.0, posinf=10.0, neginf=-10.0)
                ks_blur = cv2.GaussianBlur(ks_u, (5, 5), 0)
                
                # FIX: Normalización segura (Evita división por cero)
                min_v, max_v = np.nanmin(ks_blur), np.nanmax(ks_blur)
                denom = max_v - min_v
                if denom < 1e-6: img_norm = np.zeros_like(ks_blur)
                else: img_norm = (ks_blur - min_v) / denom
                
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
                
                # HOMEOSTASIS WAVE
                if np.max(np.abs(wave_u)) > 50.0:
                    wave_u *= 0.5
                    wave_u_prev *= 0.5 # CORRECCIÓN FÍSICO: Escalar prev también para evitar choque no físico
                
                # FIX: Añadido argumento faltante (seed_mask=None)
                simulacion_ondas(wave_u, wave_u_prev, wave_u_next, damping, c2, None)
                wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
                
                # CONTRASTE FUERTE: Usar valor absoluto para que 0 sea negro, no gris
                img_norm = np.abs(wave_u) 
                img_norm = np.clip(img_norm, 0, 1) # Asegurar rango
                
            elif escena['engine'] == 'CH':
                # Allen-Cahn (Nombrado Cahn-Hilliard originalmente, pero es Allen-Cahn por no conservar masa localmente)
                gamma = escena['p1'] * 0.01
                mobility = escena['p2'] * (1 + kick)
                for _ in range(5):
                    simulacion_cahn_hilliard(ch_u, ch_u_next, dt=0.05 * dt_dynamic, gamma=gamma, mobility=mobility)
                    ch_u, ch_u_next = ch_u_next, ch_u
                img_norm = (ch_u + 1) / 2 # Normalizar de -1,1 a 0,1
                
            elif escena['engine'] == 'KDV':
                # Korteweg-de Vries (Zakharov-Kuznetsov)
                # p1: alpha (no-linealidad), p2: beta (dispersión)
                alpha = escena['p1'] * 6.0
                beta = escena['p2'] * 2.0
                
                # Inyección de energía (Solitones aleatorios)
                if kick > 0.5:
                    ry, rx = np.random.randint(2, gs_h-2), np.random.randint(2, gs_w-2)
                    kdv_u[ry-2:ry+2, rx-2:rx+2] += np.random.uniform(-2, 2)
                
                # Homeostasis
                if np.max(np.abs(kdv_u)) > 20.0:
                    kdv_u *= 0.5
                
                for _ in range(4):
                    simulacion_kdv(kdv_u, kdv_u_next, dt=0.05 * dt_dynamic, alpha=alpha, beta=beta)
                    kdv_u, kdv_u_next = kdv_u_next, kdv_u
                
                # Normalización
                kdv_blur = cv2.GaussianBlur(kdv_u, (3, 3), 0)
                # FIX: Usar nanmin/nanmax para evitar crash por NaNs
                min_v, max_v = np.nanmin(kdv_blur), np.nanmax(kdv_blur)
                denom = max_v - min_v
                if denom < 1e-6: img_norm = np.zeros_like(kdv_blur)
                else: img_norm = (kdv_blur - min_v) / denom
                
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
                
                # FIX: Añadido argumento faltante (seed_mask=None)
                simulacion_ondas(wave_u, wave_u_prev, wave_u_next, 0.99, 0.1 * dt_dynamic, None)
                wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
                
                grad_y, grad_x = np.gradient(wave_u)
                force_field = np.stack((grad_x, grad_y), axis=2) * 50.0
                force_field = np.nan_to_num(force_field, nan=0.0)
                
                # FIX: Añadido argumento faltante (seed_mask=None)
                update_particles(p_pos, p_vel, force_field, gs_w, gs_h, damp, speed, None)
                
                # Recuperar partículas perdidas (NaNs)
                if np.isnan(p_pos).any():
                    p_pos = np.nan_to_num(p_pos, nan=gs_w/2)
                    p_vel = np.nan_to_num(p_vel, nan=0.0)

                # Dibujar partículas en img_norm
                img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
                for pi in range(num_particles):
                    px, py = int(p_pos[pi, 0]), int(p_pos[pi, 1])
                    if 0 <= px < gs_w and 0 <= py < gs_h:
                        img_norm[py, px] = 0.55 # Reducir brillo base aún más (antes 0.75)
                # Blur para que parezcan luces
                img_norm = cv2.GaussianBlur(img_norm, (3, 3), 0)

            # --- COLOREADO Y EFECTOS ---
            cmap_name = global_cmap if global_cmap else escena['cmap']
            cmap = plt.get_cmap(cmap_name)
            
            # CORRECCIÓN GAMMA (CONTRASTE):
            # FIX: Restauramos gamma a 1.2 para no aplastar la simulación a negro
            img_norm = np.clip(img_norm, 0.0, 1.0)
            img_norm = np.power(img_norm, 1.2) 
            
            bg_layer = (cmap(img_norm)[:, :, :3] * 255).astype(np.uint8)
            
            # EFECTO PSICODÉLICO 1: Rotación de Color Global
            # El color gira lentamente, y rápido cuando hay mucha energía armónica
            hue_accumulator += 0.5 + (harm * 5.0)
            bg_layer = fx.shift_hue(bg_layer, int(hue_accumulator))
            
            # --- SINESTESIA DE COLOR (CROMESTESIA) ---
            # Teñir la escena sutilmente con el color de la nota musical actual
            target_color_bgr = NOTE_PALETTE[nota] # Se usa para espíritus y hojas también
            
            if use_chroma:
                # Crear una capa sólida del color de la nota
                color_layer = np.full_like(bg_layer, target_color_bgr)
                
                # Mezclar: Cuanto más fuerte la armonía, más se nota el color de la nota
                blend_factor = 0.05 + (harm * 0.25) # Reducido: Entre 5% y 30% (antes saturaba mucho)
                bg_layer = cv2.addWeighted(bg_layer, 1.0 - blend_factor, color_layer, blend_factor, 0)
            
            # --- EFECTO CALEIDOSCOPIO (MANDALA) ---
            if use_kaleido:
                bg_layer = fx.kaleidoscopio(bg_layer, active=escena['kaleido'])

            # Escalar a HD
            bg_layer = cv2.resize(bg_layer, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
           
            # Oscurecer el fondo si la música es baja
            # FIX: Establecer piso mínimo (0.4) para que la física no desaparezca
            bg_layer = (bg_layer * (0.4 + harm * 0.6)).astype(np.uint8)

            # --- UPDATE GEOMETRÍA Y OBJETOS (OPENCV NEON) ---
            overlay_layer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            
            # 1. Lorenz Swarm (Sigue a los platillos)
            dt_lorenz = 0.005
            lorenz_swarm.update(overlay_layer, dt_lorenz, kick, cymbals_val, visible=scene_flags['lorenz'])
            
            # 2. Generador de Hojas
            if scene_flags['leaves']:
                if kick > 0.7 and np.random.rand() < 0.3:
                    hx = np.random.uniform(-3, 3)
                    hy = np.random.uniform(-2, 2)
                    color_hoja = (target_color_bgr[2]/255, target_color_bgr[1]/255, target_color_bgr[0]/255)
                    gen_hojas.spawn(hx, hy, color_hoja)
            
            gen_hojas.update(overlay_layer, kick, harm)
            
            # 3. Superforma (Arte Matemático)
            color_mpl = (target_color_bgr[2]/255.0, target_color_bgr[1]/255.0, target_color_bgr[0]/255.0)
            if scene_flags['superforma']:
                superforma.update(overlay_layer, i*0.02, kick, harm, color_mpl)
            
            # 4. Espíritus (Metaballs/Trails)
            num_active_spirits = int(1 + (num_espiritus - 1) * (progreso ** 1.5))
            for idx, esp in enumerate(espiritus):
                if idx < num_active_spirits:
                    t_esp = i * 0.05 + (idx * 13.0) 
                    esp.update(overlay_layer, pos_espiritus[idx], -0.5, 0.8, t_esp, kick, harm, color_mpl)
            
            # Aplicar suave resplandor (Neon Glow) al overlay
            overlay_layer = cv2.GaussianBlur(overlay_layer, (3, 3), 0)
            
            # Crear máscara Alpha realista basada en la luminosidad del overlay
            overlay_gray = cv2.cvtColor(overlay_layer, cv2.COLOR_BGR2GRAY)
            _, alpha_mask = cv2.threshold(overlay_gray, 5, 255, cv2.THRESH_BINARY)
            alpha_mask = cv2.GaussianBlur(alpha_mask, (7, 7), 0) # Suavizar bordes
           
            # ============================
            # COMPOSICIÓN (Blending)
            # ============================
            # Normalizar alpha a 0.0 - 1.0
            alpha_3c = cv2.merge([alpha_mask, alpha_mask, alpha_mask]).astype(np.float32) / 255.0
            
            # FIX BLENDING: cv2.addWeighted puro no recorta la luz ni ahoga la física.
            fg = overlay_layer.astype(np.float32)
            bg = bg_layer.astype(np.float32)
            # Aplicar overlay mediante máxima luminosidad para evitar oscurecer
            frame_final = np.maximum(fg * alpha_3c, bg).astype(np.uint8)

            # --- POST-PROCESADO (FASE 12: Melting World & Fractales) ---
            # Aplicar distorsión lente ojo de pez con subgraves
            frame_final = fx.melting_world_fisheye(frame_final, kick)
            
            # Aplicar ruido fractal interferencial (muy tenue)
            t = i / fps
            frame_final = fx.mandelbrot_overlay(frame_final, t, intensity=0.3 * harm)
            
            # ============================
            # POST-PROCESADO (FX CLÁSICOS)
            # ============================
            # 1. Feedback 1.005 + (kick * 0.03) 
            zoom_factor = 1.005 + (kick * 0.03)
            # Reducimos el decay base para que la luz se disipe
            frame_final = fx.feedback_zoom(frame_final, decay=0.78 + (harm * 0.08), zoom=zoom_factor)
           
            # 2. Cámara Virtual (Movimiento)
            camara.update(energy=harm, kick=kick, snare=kick)
            
            # MOD: Efecto Remolino (Trance) en subdivisiones
            # Si hay mucha actividad en platillos o kick, girar cámara fuerte
            if cymbals_val > 0.6 or kick > 0.75:
                camara.angle += 0.2 * (1 if i % 20 < 10 else -1) # Giro rápido ida y vuelta
                
            frame_final = camara.aplicar(frame_final)
           
            # --- 2.5 LYRICS OVERLAY (TEXTO NEÓN DIRECTO EN SIMULACIÓN) ---
            if lyrics_engine:
                tiempo_actual = i / float(fps)
                frame_final = lyrics_engine.draw(frame_final, tiempo_actual, kick=kick)
           
            # 3. Bloom (Resplandor MASIVO analógico)
            if use_flash:
                # Intensidad base alta, explota con el kick, umbral bajo para que brille casi todo lo blanco
                frame_final = fx.aplicar_bloom(frame_final, intensity=0.5 + (kick * 1.5), threshold=160)
               
            # 4. Aberración Cromática (Glitch VHS constante basado en textura/ruido)
            if use_flash:
                # La aberración siempre tiene un mínimo (VHS tracking error)
                frame_final = fx.aberracion_cromatica(frame_final, strength=5.0 + kick * 15 + textura * 15)
            
            # 5. Modelo Freemium (Marca de Agua)
            # Solo desaparece si el usuario compró la versión Pro
            # En el futuro esto vendrá de un argumento de la interfaz
            es_freemium = True
            if es_freemium:
                # Marca elegante y traslúcida en la esquina inferior derecha
                wm_text = "Generated by Cosmic Generator V2"
                cv2.putText(frame_final, wm_text, (WIDTH - 500, HEIGHT - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2, cv2.LINE_AA)
            
            # Escribir frame
            out.write(frame_final)

        out.release()
        return True

    except Exception as e:
        print(f"Error critico: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# RUN
# ==========================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generador de Visuales Cuánticos")
    parser.add_argument("audio", nargs="?", default=r"data\Rebeldía Cosmica - Sol Que se Va.flac", help="Ruta del archivo de audio")
    parser.add_argument("--test", action="store_true", help="Renderizar solo 20 segundos de prueba")
    parser.add_argument("--duration", type=float, help="Duración personalizada en segundos")
    parser.add_argument("--seed", type=int, help="Semilla aleatoria")
    parser.add_argument("--engines", nargs="+", help="Lista de motores permitidos")
    parser.add_argument("--no-spirits", action="store_true", help="Desactivar espíritus")
    parser.add_argument("--no-kaleido", action="store_true", help="Desactivar caleidoscopio")
    parser.add_argument("--no-flash", action="store_true", help="Modo seguro (sin flashes fuertes)")
    parser.add_argument("--chroma", action="store_true", help="Activar color por nota")
    parser.add_argument("--lyrics", action="store_true", help="Activar Motor de Letras")
    parser.add_argument("--cmap", type=str, help="Mapa de color global")
    parser.add_argument("--output", type=str, help="Ruta de salida")
    
    args = parser.parse_args()
    
    CANCION = args.audio
    TEMP = "temp_godmode.mp4"
    FINAL = args.output if args.output else "Rebeldia_Cosmica_Official.mp4"
   
    if args.duration:
        DURACION_TEST = args.duration
    else:
        DURACION_TEST = 20 if args.test else None
   
    if generar_animacion_god_mode(CANCION, TEMP, fps=30, duracion=DURACION_TEST, seed=args.seed, allowed_engines=args.engines, use_spirits=not args.no_spirits, use_kaleido=not args.no_kaleido, use_flash=not args.no_flash, use_chroma=args.chroma, use_lyrics=args.lyrics, global_cmap=args.cmap):
        unir_video_con_musica(TEMP, CANCION, FINAL, duracion=DURACION_TEST)