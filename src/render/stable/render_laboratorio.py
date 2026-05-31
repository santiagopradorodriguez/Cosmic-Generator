# (C) Rebeldía Cósmica | Laboratorio de Simulación Pura
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Desacoplamos por completo Librosa y los motores audiovisuales.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.config import WIDTH, HEIGHT, ACTOS
from core.nucleo_visual import (
    simulacion_gray_scott, simulacion_ondas, simulacion_ks, 
    simulacion_gpe, simulacion_ohta_kawasaki, simulacion_kdv
)
from core.nucleo_espectral import NucleoEspectral

def simular_laboratorio_puro(nombre_salida="sim_laboratorio.mp4", fps=30, duracion=5, seed=42, engine_code='GS', progress_callback=None):
    """
    Entorno de simulación Aislado y Estricto.
    Sin audio. Sin reactividad. Pura evolución determinista sobre un colormap científico.
    """
    # Caché de LookUp Tables para colormaps de Matplotlib -> OpenCV
    lut_cache = {}
    def get_lut(name):
        if name not in lut_cache:
            cmap = plt.get_cmap(name)
            lut = (cmap(np.linspace(0, 1, 256))[:, :3] * 255).astype(np.uint8)
            lut = lut[:, ::-1] # RGB a BGR para OpenCV
            lut_cache[name] = lut.reshape(256, 1, 3)
        return lut_cache[name]

    np.random.seed(seed)
    total_frames = duracion * fps
    
    # Resoluciones internas
    gs_w = WIDTH // 4
    gs_h = HEIGHT // 4
    
    # Configuración de Video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(nombre_salida, fourcc, fps, (WIDTH, HEIGHT))
    
    # 1. ESTADO INICIAL
    # (El subagente FisicoMatematicoCaos proporcionará las condiciones iniciales exactas)
    
    print(f"[LABORATORIO PURO] Iniciando motor: {engine_code}")
    
    # --- Estado Inicial Riguroso ---
    gs_w, gs_h = WIDTH // 4, HEIGHT // 4
    
    # 1. Gray-Scott (Patrones de Turing)
    gs_u = np.ones((gs_h, gs_w), dtype=np.float32)
    gs_v = np.zeros((gs_h, gs_w), dtype=np.float32)
    gs_u_next = np.zeros_like(gs_u)
    gs_v_next = np.zeros_like(gs_v)
    # Semilla pura central
    r, c = gs_h//2, gs_w//2
    gs_v[r-5:r+5, c-5:c+5] = 1.0
    
    # 2. Kuramoto-Sivashinsky Espectral
    ks_u_hat = np.fft.fft2(np.random.uniform(-0.1, 0.1, (gs_h, gs_w)))
    
    # 3. Gross-Pitaevskii Cuántica
    gpe_psi = np.ones((gs_h, gs_w), dtype=np.complex128)
    gpe_V = np.zeros((gs_h, gs_w), dtype=np.float64)
    gpe_V[r-10:r+10, c-10:c+10] = 5.0 # Pozo de potencial
    
    # 4. Ecuación de Ondas Hiperbólica
    wave_u = np.zeros((gs_h, gs_w), dtype=np.float32)
    wave_u_prev = np.zeros_like(wave_u)
    wave_u_next = np.zeros_like(wave_u)
    wave_u[r-2:r+2, c-2:c+2] = 5.0 # Perturbación inicial
    
    # 5. Clifford (Caos 2D Discreto)
    num_particles = 100000
    p_pos = np.random.rand(num_particles, 2) * [gs_w, gs_h]
    clifford_density = np.zeros((gs_h, gs_w), dtype=np.float64)
    
    # Instanciar el núcleo espectral para matemáticas pesadas
    nucleo_fft = NucleoEspectral(gs_w, gs_h, dx=1.0, dy=1.0)
    
    for i in range(total_frames):
        if progress_callback and i % 5 == 0:
            progress_callback(int((i / total_frames) * 100))
            
        # 2. EVOLUCIÓN MATEMÁTICA PURA
        img_norm = np.zeros((gs_h, gs_w), dtype=np.float32)
        cmap_name = 'viridis'
        
        if engine_code == 'GS':
            # Diferencias Finitas
            dt = 1.0
            Du, Dv, f, k = 0.16, 0.08, 0.060, 0.062 # Rango de Turing
            simulacion_gray_scott(gs_u, gs_v, gs_u_next, gs_v_next, Du, Dv, f, k, dt, None, 0.0)
            gs_u, gs_u_next = gs_u_next, gs_u
            gs_v, gs_v_next = gs_v_next, gs_v
            
            # Normalización Lineal para V (Concentración)
            img_norm = gs_v / np.max(gs_v + 1e-6)
            cmap_name = 'magma'
            
        elif engine_code == 'KS':
            # Pseudo-Espectral (FFT)
            dt = 0.05
            ks_u_hat = nucleo_fft.simulacion_ks_espectral(ks_u_hat, dt, kick_intensity=0.0)
            img_norm = np.real(np.fft.ifft2(ks_u_hat))
            
            # Normalización Divergente para Caos de Fases
            min_v, max_v = np.min(img_norm), np.max(img_norm)
            limite = max(abs(min_v), abs(max_v)) + 1e-6
            img_norm = (img_norm + limite) / (2.0 * limite)
            cmap_name = 'twilight'
            
        elif engine_code == 'WAVE':
            dt = 0.1
            damping = 0.999
            c2 = 0.25 # Condición CFL c*dt/dx < 1
            simulacion_ondas(wave_u, wave_u_prev, wave_u_next, damping, c2, None)
            wave_u_prev, wave_u, wave_u_next = wave_u, wave_u_next, wave_u_prev
            
            # Normalización Divergente anclada en 0
            limite = 2.0
            img_norm = np.clip(wave_u, -limite, limite)
            img_norm = (img_norm + limite) / (2.0 * limite)
            cmap_name = 'RdBu'
            
        elif engine_code == 'GPE':
            # Split-Step Fourier
            dt = 0.01
            g_nl = 1.0
            gpe_psi = nucleo_fft.simulacion_gpe_espectral(gpe_psi, gpe_V, g_nl, dt)
            
            # Domain Coloring Puro: Densidad a Intensidad (Monocromático para Laboratorio Cuántico)
            densidad = np.abs(gpe_psi)**2
            img_norm = densidad / np.max(densidad + 1e-6)
            cmap_name = 'inferno'
            
        elif engine_code == 'CLIFFORD':
            a, b, c, d = -1.4, 1.6, 1.0, 0.7 
            x_old = (p_pos[:, 0] / gs_w) * 4.0 - 2.0
            y_old = (p_pos[:, 1] / gs_h) * 4.0 - 2.0
            
            x_new = np.sin(a * y_old) + c * np.cos(a * x_old)
            y_new = np.sin(b * x_old) + d * np.cos(b * y_old)
            
            p_pos[:, 0] = ((x_new + 2.0) / 4.0) * gs_w
            p_pos[:, 1] = ((y_new + 2.0) / 4.0) * gs_h
            
            # Fractal Density Renderer 2D (Histograma + Escala Logarítmica)
            x_idx = np.clip(p_pos[:, 0].astype(int), 0, gs_w-1)
            y_idx = np.clip(p_pos[:, 1].astype(int), 0, gs_h-1)
            
            clifford_density *= 0.95 # Decay para observar evolución, aunque la órbita es invariante
            np.add.at(clifford_density, (y_idx, x_idx), 1.0)
            
            # Transformación Logarítmica C = log(1 + N)
            img_norm = np.log1p(clifford_density)
            img_norm /= np.max(img_norm + 1e-6)
            cmap_name = 'hot'
        
        # 3. COLORMAP CIENTÍFICO ESTRUCTURAL (OPTIMIZADO VÍA LUT)
        img_norm = np.clip(img_norm, 0.0, 1.0)
        img_uint8 = (img_norm * 255).astype(np.uint8)
        
        lut = get_lut(cmap_name)
        # cv2.applyColorMap convierte internamente el canal a 3 canales BGR usando la LUT de 256x1x3
        if int(cv2.__version__.split('.')[0]) >= 3:
            # Opencv >= 3.3 soporta custom LUTs en applyColorMap (o alternativamente cv2.LUT con 3-canales)
            try:
                frame_bgr = cv2.applyColorMap(img_uint8, lut)
            except cv2.error:
                # Fallback por si acaso:
                img_uint8_3c = cv2.merge([img_uint8, img_uint8, img_uint8])
                frame_bgr = cv2.LUT(img_uint8_3c, lut)
        else:
            img_uint8_3c = cv2.merge([img_uint8, img_uint8, img_uint8])
            frame_bgr = cv2.LUT(img_uint8_3c, lut)
        
        # Upscale
        frame_final = cv2.resize(frame_bgr, (WIDTH, HEIGHT), interpolation=cv2.INTER_LANCZOS4)
        
        # Guardar
        out.write(frame_final)
        
    out.release()
    print("[LABORATORIO PURO] Generación bruta completada. Transcodificando a H.264 para compatibilidad Web...")
    
    # Transcodificación con FFmpeg (imageio_ffmpeg) para que Streamlit/Navegadores puedan reproducirlo en H.264
    try:
        import subprocess
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        temp_file = nombre_salida.replace(".mp4", "_temp.mp4")
        if os.path.exists(nombre_salida):
            os.rename(nombre_salida, temp_file)
            
            cmd = [
                ffmpeg_exe, "-y",
                "-i", temp_file,
                "-vcodec", "libx264",
                "-pix_fmt", "yuv420p", # Formato de pixel estrictamente necesario para Chrome/Safari
                nombre_salida
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            os.remove(temp_file)
            print("[LABORATORIO PURO] Transcodificación exitosa a H.264 vía FFmpeg directo.")
    except Exception as e:
        print(f"[LABORATORIO PURO] Advertencia: No se pudo transcodificar a H.264. Error: {e}")
        # Restaurar archivo original si falló
        if os.path.exists(temp_file) and not os.path.exists(nombre_salida):
            os.rename(temp_file, nombre_salida)
        
    print("[LABORATORIO PURO] Simulacion Finalizada con Rigor Cientifico.")
    return True
