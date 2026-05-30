import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import librosa
import imageio_ffmpeg
from tqdm import tqdm
import os
import torch
import torch.nn as nn
import torch.optim as optim
import sys
from scipy.ndimage import gaussian_filter1d

# Importar nuestros módulos existentes
from core.efectos_visuales import CamaraVirtual, MotorFX
from audio.motor_lyrics import LyricsEngine
from core.nucleo_visual import (
    simulacion_gray_scott,
    simulacion_ks,
    simulacion_ondas,
    update_particles,
    simulacion_gpe,
    simulacion_cahn_hilliard
)

# Configuración FFmpeg
plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip

# ==========================================
# 1. EL CEREBRO: AUTOENCODER NEURONAL
# ==========================================
# Forzar uso de CPU para compatibilidad garantizada
device = torch.device('cpu')

class AudioAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=3):
        super(AudioAutoencoder, self).__init__()
        
        # ENCODER: Comprime la realidad (Audio) a una idea abstracta (Latente)
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim), # Cuello de botella (Espacio Latente)
            nn.Tanh() # Normalizamos entre -1 y 1 para facilitar el mapeo físico
        )
        
        # DECODER: Reconstruye la realidad desde la idea (para calcular el error)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.encoder(x)
        reconstruction = self.decoder(z)
        return reconstruction, z

def entrenar_red_con_cancion(spectrograma_norm, epochs=400, song_name="unknown"):
    """
    Entrena la red para que aprenda la topología específica de ESTA canción.
    Usa Checkpoints para no re-entrenar si ya existe.
    """
    # Crear carpeta de checkpoints si no existe
    ckpt_dir = "checkpoints_db"
    os.makedirs(ckpt_dir, exist_ok=True)
    
    # Limpiar nombre de archivo
    safe_name = "".join([c for c in song_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    ckpt_path = os.path.join(ckpt_dir, f"{safe_name}_model.pth")

    input_dim = spectrograma_norm.shape[1]
    model = AudioAutoencoder(input_dim=input_dim, latent_dim=3).to(device)
    
    # 1. Intentar cargar Checkpoint
    if os.path.exists(ckpt_path):
        print(f"💾 Checkpoint encontrado: {ckpt_path}. Cargando modelo...")
        model.load_state_dict(torch.load(ckpt_path))
        model.eval() # Modo evaluación
        return model
    
    # Convertir a tensores
    data_tensor = torch.FloatTensor(spectrograma_norm).to(device)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    print(f"🧠 Entrenando Red Neuronal en CPU ({epochs} épocas)...")
    pbar = tqdm(range(epochs), desc="Aprendiendo estructura musical")
    
    for epoch in pbar:
        optimizer.zero_grad()
        recon, latente = model(data_tensor)
        loss = criterion(recon, data_tensor)
        loss.backward()
        optimizer.step()
        pbar.set_postfix({'Error (Loss)': f"{loss.item():.6f}"})
        
    # 2. Guardar Checkpoint
    print(f"💾 Guardando entrenamiento en: {ckpt_path}")
    torch.save(model.state_dict(), ckpt_path)
        
    return model

# ==========================================
# 2. EL MAPEO: LATENTE -> FÍSICA
# ==========================================
def mapear_latente_a_fisica(latente_array):
    """
    Traduce el vector latente a parámetros de TODOS los motores.
    z[0] -> Selector de Motor (Engine Switch)
    z[1] -> Parámetro Principal (Feed, Damping, Gamma, etc.)
    z[2] -> Parámetro Secundario (Kill, Speed, Mobility, etc.)
    """
    # Suavizar la trayectoria para que el fluido no "tiemble" demasiado
    # FIX: Reducido de 30 a 5. El valor anterior mataba la reactividad musical.
    latente_smooth = gaussian_filter1d(latente_array, sigma=5, axis=0) 
    
    # Normalizar z entre 0 y 1 para facilitar el mapeo
    # FIX: Usar percentiles para evitar que outliers compriman el rango de movimiento
    z_min = np.percentile(latente_smooth, 2, axis=0)
    z_max = np.percentile(latente_smooth, 98, axis=0)
    
    denom = z_max - z_min
    denom[denom < 1e-6] = 1.0 # Evitar división por cero si la red colapsa
    
    z_norm = (latente_smooth - z_min) / denom
    
    return z_norm

def check_vital_signs(buffer_img):
    """
    Monitor de signos vitales de la simulación.
    Detecta si la imagen se puso toda blanca (saturación) o toda negra (muerte).
    Retorna True si la simulación necesita RCP (Reseteo).
    """
    if buffer_img is None: return False
    
    mean_val = np.mean(buffer_img)
    std_val = np.std(buffer_img)
    
    # Si la desviación estándar es muy baja, la imagen es plana (todo igual)
    # Si el promedio es muy alto (>0.8) es pantalla blanca (Saturación)
    # Si el promedio es muy bajo (<0.01) es pantalla negra
    if std_val < 0.001 or mean_val > 0.80 or mean_val < 0.005:
        return True
    return False

def soft_normalize(arr, percentile=99.0):
    """Normalización suave usando percentiles para evitar destellos por picos únicos."""
    if arr.size == 0: return arr
    val_max = np.percentile(np.abs(arr), percentile)
    if val_max < 1e-6: return arr
    return np.tanh(arr / val_max * 2.0) # Tanh comprime suavemente el rango

# ==========================================
# 3. GENERADOR PRINCIPAL V2.0
# ==========================================
def generar_animacion_neural(ruta_audio, nombre_salida_temp, fps=30, duracion=None, use_flash=True):
    
    print(f"--- 1. Análisis Espectral: {ruta_audio} ---")
    
    # Cargar Audio
    try:
        y, sr = librosa.load(ruta_audio, duration=duracion)
    except FileNotFoundError:
        print("❌ Archivo no encontrado.")
        return False

    # Inicializar Motor de Letras
    lyrics_engine = LyricsEngine(ruta_audio)

    hop_length = int(sr / fps)
    
    # Generar Mel Spectrogram (La "imagen" del sonido)
    n_mels = 128
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, hop_length=hop_length)
    S_db = librosa.power_to_db(S, ref=np.max)
    
    # Normalizar entre 0 y 1 para la red neuronal
    S_norm = (S_db - S_db.min()) / (S_db.max() - S_db.min() + 1e-6)
    S_norm = np.nan_to_num(S_norm, nan=0.0, posinf=1.0, neginf=0.0) # FIX: Seguridad espectral
    S_norm = S_norm.T # (Tiempo, Features)
    
    total_frames = S_norm.shape[0]
    
    # --- FASE NEURONAL ---
    # 1. Entrenar la red con esta canción
    song_name = os.path.basename(ruta_audio)
    modelo = entrenar_red_con_cancion(S_norm, epochs=150, song_name=song_name)
    
    # 2. Extraer la "Esencia" (Espacio Latente) de toda la canción
    print("🔮 Extrayendo trayectoria latente...")
    with torch.no_grad():
        data_tensor = torch.FloatTensor(S_norm).to(device)
        _, latente_tensor = modelo(data_tensor)
        latente_trajectory = latente_tensor.cpu().numpy()
        
    # 3. Convertir Esencia en Física
    z_params = mapear_latente_a_fisica(latente_trajectory)
    
    print(f"📊 Estadísticas de Parámetros Neurales (Reactividad):")
    print(f"   Motor (z0): std={np.std(z_params[:,0]):.3f} (Si es < 0.05, la red está estática)")
    print(f"   Param A (z1): std={np.std(z_params[:,1]):.3f}")
    print(f"   Param B (z2): std={np.std(z_params[:,2]):.3f}")
    
    # --- CONFIGURACIÓN DE RENDER ---
    W, H = 1280, 720
    gs_scale = 4
    gs_w, gs_h = W // gs_scale, H // gs_scale
    
    # --- INICIALIZAR TODOS LOS MOTORES FÍSICOS ---
    
    # 1. Gray-Scott (GS)
    U = np.ones((gs_h, gs_w), dtype=np.float32)
    V = np.zeros((gs_h, gs_w), dtype=np.float32)
    U_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    V_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    # Semilla inicial
    mid_r, mid_c = gs_h//2, gs_w//2
    V[mid_r-20:mid_r+20, mid_c-20:mid_c+20] = 0.5
    
    # 2. Kuramoto-Sivashinsky (KS)
    ks_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    ks_u_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    ks_u += np.random.normal(0, 0.1, (gs_h, gs_w))
    
    # 3. Gross-Pitaevskii (GPE)
    gpe_psi_r = np.exp(-(np.linspace(-2, 2, gs_w)**2)) * np.ones((gs_h, 1))
    gpe_psi_r = gpe_psi_r.astype(np.float32)
    gpe_psi_i = np.zeros_like(gpe_psi_r)
    gpe_psi_r_next = np.zeros_like(gpe_psi_r)
    gpe_psi_i_next = np.zeros_like(gpe_psi_i)
    gpe_V = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # 4. Ondas (WAVE)
    wave_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_u_prev = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_u_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # 5. Cahn-Hilliard (CH)
    ch_u = np.random.uniform(-1, 1, (gs_h, gs_w)).astype(np.float32)
    ch_u_next = np.zeros((gs_h, gs_w), dtype=np.float32)
    
    # Semillas iniciales (Caos primordial)
    for _ in range(20):
        rx, ry = np.random.randint(0, gs_w), np.random.randint(0, gs_h)
        V[ry-10:ry+10, rx-10:rx+10] = np.random.rand()
        
    # Inicializar Partículas (Conectadas al vector de Caos)
    num_particles = 4000
    p_pos = np.random.rand(num_particles, 2) * [gs_w, gs_h]
    p_vel = np.zeros((num_particles, 2), dtype=np.float32)
    p_pos = p_pos.astype(np.float32)
    p_vel = p_vel.astype(np.float32)
    
    # Inicializar FX
    camara = CamaraVirtual(W, H)
    fx = MotorFX(W, H)
    
    # Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombre_salida_temp, fourcc, fps, (W, H))
    
    # Análisis de ritmo básico para la cámara (Kick)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.util.sync(onset_env, np.arange(total_frames), aggregate=np.mean)
    onset_frames = np.resize(onset_frames, total_frames)
    onset_frames = (onset_frames - onset_frames.min()) / (onset_frames.max() - onset_frames.min())

    # Calcular energía RMS para 'harm' (Corrección del error NameError)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    rms = rms / (np.max(rms) + 1e-6)
    rms = np.resize(rms, total_frames)

    print(f"--- 2. Renderizando Simulación Multi-Motor ---")
    
    prev_kick = 0.0
    try:
        for i in tqdm(range(total_frames), desc="Simulando"):
            
            # --- PARÁMETROS DICTADOS POR LA IA ---
            # z[0]: Selector de Motor (0.0-1.0 dividido en 5 zonas)
            # z[1]: Parámetro A (Control principal)
            # z[2]: Parámetro B (Control secundario)
            
            # Definir harm para este frame
            harm = rms[i]
            
            # --- 1. CÁLCULO DE IMPULSO (DERIVADA) ---
            kick_actual = onset_frames[i]
            kick_impulse = max(0.0, kick_actual - prev_kick) * 5.0
            prev_kick = kick_actual
            
            # --- MEZCLA NEURO-ACÚSTICA (REACTIVIDAD FÍSICA) ---
            # La IA define el "Clima" (Base), el Audio define el "Viento" (Modulación)
            # Esto fuerza a la física a responder a los golpes de la música
            engine_val = z_params[i, 0]
            param_a = np.clip(z_params[i, 1] + (harm * 0.3), 0.0, 1.0)
            param_b = np.clip(z_params[i, 2] + (kick_impulse * 0.3), 0.0, 1.0)
            
            # --- 2. CONTROL CFL (DT DINÁMICO) ---
            # Si hay mucho caos (param_b alto), reducimos el paso de tiempo para estabilidad
            dt_dynamic = 1.0 / (1.0 + param_b * 2.0)
            # Compensar velocidad visual: Si dt baja, iteramos más veces
            iters = int(8 + (param_b * 4)) 
            
            img_fluid = np.zeros((gs_h, gs_w), dtype=np.float32)
            
            # --- SELECCIÓN DE MOTOR ---
            # Usamos interpolación suave o switch directo. Switch es más seguro para CPU.
            
            if engine_val < 0.2:
                # === 1. GRAY-SCOTT ===
                # Mapeo a zona de Pearson interesante + Modulación por Kick
                f = 0.015 + (param_a * 0.045) - (kick_impulse * 0.005)
                k = 0.045 + (param_b * 0.020) + (kick_impulse * 0.005)
                
                # Monitor de vida: Si V muere, reinyectar caos
                if check_vital_signs(V):
                    # Si está saturado (blanco), matar todo primero (Hard Reset)
                    if np.mean(V) > 0.5:
                        V[:] = 0
                        U[:] = 1
                    
                    rx, ry = np.random.randint(0, gs_w), np.random.randint(0, gs_h)
                    V[ry-20:ry+20, rx-20:rx+20] = np.random.rand()
                
                for _ in range(iters):
                    # FIX: Añadidos argumentos faltantes (seed_mask=None, tension=0.0)
                    simulacion_gray_scott(U, V, U_next, V_next, 0.16, 0.08, f, k, 1.0 * dt_dynamic, None, 0.0)
                    U, U_next = U_next, U
                    V, V_next = V_next, V
                
                # FIX: Normalización por contraste fijo para evitar saturación blanca
                # Reducido de 3.0 a 1.8 para evitar quemado
                img_fluid = np.clip(V * 1.8, 0, 1.0)
                
            elif engine_val < 0.45:
                # === 2. KURAMOTO-SIVASHINSKY ===
                dt_ks = (0.2 + (param_a * 0.3)) * dt_dynamic
                if kick_impulse > 0.5: ks_u += np.random.normal(0, 0.5, ks_u.shape)
                
                # --- HOMEOSTASIS GLOBAL (KS) ---
                if np.any(np.isnan(ks_u)) or np.max(np.abs(ks_u)) > 1e4:
                    ks_u[:] = np.random.normal(0, 0.1, ks_u.shape)
                    ks_u_next[:] = 0

                for _ in range(max(4, iters // 2)):
                    simulacion_ks(ks_u, ks_u_next, dt_ks)
                    ks_u, ks_u_next = ks_u_next, ks_u
                
                # Sanitizar y Normalizar
                # FIX: Manejo robusto de infinitos para evitar (inf - inf)
                ks_u = np.nan_to_num(ks_u, nan=0.0, posinf=50.0, neginf=-50.0)
                ks_u = np.clip(ks_u, -50.0, 50.0)
                
                # FIX: Normalización suave
                img_fluid = soft_normalize(ks_u)
                
            elif engine_val < 0.65:
                # === 3. GROSS-PITAEVSKII ===
                g = 1.0 + (param_a * 5.0)
                # Potencial reactivo al volumen (kick_actual), no al impulso
                gpe_V[:] = 0.1 * (1 + kick_actual) * (np.linspace(-1, 1, gs_w)**2)
                
                # --- HOMEOSTASIS GLOBAL (GPE) ---
                if np.any(np.isnan(gpe_psi_r)) or np.max(np.abs(gpe_psi_r)) > 1e4:
                    gpe_psi_r[:] = np.exp(-(np.linspace(-2, 2, gs_w)**2)).reshape(-1, 1)
                    gpe_psi_i[:] = 0

                for _ in range(max(6, iters // 2)): # Menos pasos para CPU
                    simulacion_gpe(gpe_psi_r, gpe_psi_i, gpe_psi_r_next, gpe_psi_i_next, gpe_V, g, 0.002 * dt_dynamic)
                    gpe_psi_r, gpe_psi_r_next = gpe_psi_r_next, gpe_psi_r
                    gpe_psi_i, gpe_psi_i_next = gpe_psi_i_next, gpe_psi_i
                
                # FIX: Sanitizar estado GPE para evitar explosiones numéricas
                gpe_psi_r = np.nan_to_num(gpe_psi_r, nan=0.0, posinf=10.0, neginf=-10.0)
                gpe_psi_i = np.nan_to_num(gpe_psi_i, nan=0.0, posinf=10.0, neginf=-10.0)

                densidad = gpe_psi_r**2 + gpe_psi_i**2
                img_fluid = soft_normalize(densidad)
                
            elif engine_val < 0.85:
                # === 4. ONDAS ===
                damping = 0.90 + (param_a * 0.08) + (kick_impulse * 0.01) # El kick inyecta energía (reduce damping)
                c2 = (0.1 + (param_b * 0.3)) * dt_dynamic # CFL Safety applied
                
                if kick_impulse > 0.4:
                    ry, rx = np.random.randint(1, gs_h-1), np.random.randint(1, gs_w-1)
                    wave_u[ry, rx] += np.random.uniform(-1, 1) * kick_impulse * 5
                
                # --- HOMEOSTASIS GLOBAL (WAVE) ---
                if np.any(np.isnan(wave_u)) or np.max(np.abs(wave_u)) > 1e3:
                    wave_u[:] = 0
                    wave_u_prev[:] = 0
                
                # FIX: Añadido argumento faltante (seed_mask=None)
                simulacion_ondas(wave_u, wave_u_prev, wave_u_next, damping, c2, None)
                wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
                
                # FIX: Sanitizar estado Wave
                wave_u = np.nan_to_num(wave_u, nan=0.0, posinf=10.0, neginf=-10.0)
                wave_u = np.clip(wave_u, -10.0, 10.0)
                
                # FIX: Normalización dinámica en lugar de clipping agresivo
                img_fluid = soft_normalize(np.abs(wave_u))
                
            else:
                # === 5. CAHN-HILLIARD ===
                gamma = 0.01 + (param_a * 0.05)
                mobility = 1.0 + (param_b * 2.0)
                
                for _ in range(max(4, iters // 2)):
                    simulacion_cahn_hilliard(ch_u, ch_u_next, 0.05 * dt_dynamic, gamma, mobility)
                    ch_u, ch_u_next = ch_u_next, ch_u
                
                img_fluid = (ch_u + 1) / 2
                img_fluid = np.clip(img_fluid, 0, 1)
            
            # 2. SISTEMA DE PARTÍCULAS (Guiado por el fluido)
            # Calculamos el gradiente del fluido para empujar las partículas
            
            # FIX: Sanitizar fluido antes de calcular gradientes
            img_fluid = np.nan_to_num(img_fluid, nan=0.0, posinf=1.0, neginf=0.0)
            
            grad_y, grad_x = np.gradient(img_fluid)
            force_field = np.stack((grad_x, grad_y), axis=2) * 80.0 * (1 + param_b)
            
            # FIX: Sanitizar campo de fuerza
            force_field = np.nan_to_num(force_field, nan=0.0)
            
            # Actualizar partículas
            # FIX: Añadido argumento faltante (seed_mask=None)
            update_particles(p_pos, p_vel, force_field, gs_w, gs_h, 0.9, 2.0 + kick_impulse*2, None)
            
            # FIX: Recuperar partículas perdidas (NaNs) si la física explotó
            if np.isnan(p_pos).any():
                mask_nan = np.isnan(p_pos).any(axis=1)
                p_pos[mask_nan] = np.random.rand(np.sum(mask_nan), 2) * [gs_w, gs_h]
                p_vel[mask_nan] = 0
            
            # 3. RENDERIZADO
            # Mapa de color dinámico basado en la dimensión latente 'chaos'
            # Si chaos es bajo -> Magma (Calma)
            # Si chaos es alto -> Twilight/HSV (Psicodelia)
            if param_b < 0.4:
                cmap = plt.get_cmap('magma')
            elif param_b < 0.7:
                cmap = plt.get_cmap('viridis')
            else:
                cmap = plt.get_cmap('twilight')
                
            # FIX: Corrección Gamma agresiva para eliminar el fondo blanco/grisáceo
            # Usamos tanh para saturación suave en lugar de clip duro
            img_fluid = np.tanh(img_fluid * 2.5) 
            
            # Aplicar color al fluido
            img_colored = (cmap(img_fluid)[:, :, :3] * 255).astype(np.uint8)
            
            # Dibujar partículas
            img_particles = np.zeros((gs_h, gs_w), dtype=np.float32)
            for pi in range(num_particles):
                px, py = int(p_pos[pi, 0]), int(p_pos[pi, 1])
                if 0 <= px < gs_w and 0 <= py < gs_h:
                    # Reducir brillo de partículas (0.6 en vez de 1.0)
                    img_particles[py, px] = 0.6
            
            # Blur a las partículas y colorearlas blanco/cian
            img_particles = cv2.GaussianBlur(img_particles, (3, 3), 0)
            mask_p = np.dstack([img_particles]*3)
            
            # Composición: Fluido + Partículas
            # Reducir pesos para evitar saturación (0.8 -> 0.7, 1.0 -> 0.5)
            frame = cv2.addWeighted(img_colored, 0.7, (mask_p * 255).astype(np.uint8), 0.5, 0)
            
            # Escalar a HD
            frame = cv2.resize(frame, (W, H), interpolation=cv2.INTER_LINEAR)
            
            # 4. POST-PROCESADO (FX)
            # Feedback temporal controlado por la IA
            # Usamos kick_actual para el zoom (respiración) pero decay controlado
            frame = fx.feedback_zoom(frame, decay=0.50 + (param_a * 0.15), zoom=1.005 + (kick_actual * 0.01))
            
            # Cámara Virtual
            camara.update(energy=param_b, kick=kick_impulse, snare=0)
            frame = camara.aplicar(frame)
            
            # Bloom reactivo al IMPULSO (Flash corto) en lugar de volumen sostenido
            if kick_impulse > 0.4 and use_flash:
                # Intensidad basada en el cambio brusco
                frame = fx.aplicar_bloom(frame, intensity=kick_impulse * 0.3)
                
            # --- AUTO-LIMPIEZA (ANTI-FLASHBANG) ---
            # Si el frame es demasiado brillante, oscurecerlo automáticamente
            mean_val = np.mean(frame)
            if mean_val > 200:
                frame = (frame.astype(np.float32) * (190.0 / mean_val)).astype(np.uint8)
                
            # Debug visual: Mostrar parámetros f/k en una esquina pequeña
            # cv2.putText(frame, f"f: {f_curr:.4f} k: {k_curr:.4f}", (50, 50), 
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            out.write(frame)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        out.release()
        
    return True

def unir_audio(video_path, audio_path, output_path, duracion=None):
    print("--- 3. Mezclando Audio Final ---")
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
    
    final.write_videofile(output_path, codec='libx264', audio_codec='aac')

# ==========================================
# RUN V2.0
# ==========================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", default="Rebeldía Cosmica - Sol Que se Va.flac")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-flash", action="store_true")
    
    # Usamos parse_known_args para ignorar argumentos extra que pueda enviar el lanzador
    args, unknown = parser.parse_known_args()
    
    CANCION = args.audio
    TEMP = "temp_neural.mp4"
    FINAL = "Rebeldia_Cosmica_Neural_V2.mp4"
    
    if args.seed is not None:
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
    
    if generar_animacion_neural(CANCION, TEMP, fps=30, duracion=args.duration, use_flash=not args.no_flash):
        unir_audio(TEMP, CANCION, FINAL, duracion=args.duration)
