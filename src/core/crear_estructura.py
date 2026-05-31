# (C) Rebeldía Cósmica | Creado por Santiago Prado
import os

# Asegurar que la carpeta src existe
os.makedirs('src', exist_ok=True)

archivos = {
    'src/config.py': r'''# Configuración Global y Constantes

# Resolución de Render
WIDTH = 1280
HEIGHT = 720
FPS = 30

# Paleta Sinestésica (Cromestesia) - Formato BGR (OpenCV)
NOTE_PALETTE = [
    (0, 0, 255),    # C (Do) - Rojo
    (128, 0, 128),  # C# - Púrpura
    (0, 255, 255),  # D (Re) - Amarillo
    (128, 128, 0),  # D# - Oliva/Dorado
    (0, 215, 255),  # E (Mi) - Dorado Intenso
    (0, 0, 128),    # F (Fa) - Rojo Oscuro/Marrón
    (0, 128, 255),  # F# - Naranja Intenso
    (255, 0, 0),    # G (Sol) - Azul
    (255, 0, 128),  # G# - Violeta
    (0, 255, 0),    # A (La) - Verde
    (128, 255, 0),  # A# - Verde Azulado
    (255, 255, 0)   # B (Si) - Cian/Celeste
]

# Definición de Actos Visuales
ACTOS = [
    {'engine': 'GS',   'cmap': 'magma',         'kaleido': False, 'p1': 0.055, 'p2': 0.062},
    {'engine': 'GS',   'cmap': 'magma',         'kaleido': False, 'p1': 0.055, 'p2': 0.062},
    {'engine': 'GS',   'cmap': 'inferno',       'kaleido': True,  'p1': 0.030, 'p2': 0.060},
    {'engine': 'GS',   'cmap': 'twilight',      'kaleido': False, 'p1': 0.025, 'p2': 0.055},
    {'engine': 'GS',   'cmap': 'twilight',      'kaleido': False, 'p1': 0.025, 'p2': 0.055},
    {'engine': 'GS',   'cmap': 'viridis',       'kaleido': False, 'p1': 0.029, 'p2': 0.057},
    {'engine': 'GS',   'cmap': 'viridis',       'kaleido': True,  'p1': 0.029, 'p2': 0.057},
    {'engine': 'GS',   'cmap': 'plasma',        'kaleido': True,  'p1': 0.040, 'p2': 0.060},
    {'engine': 'KS',   'cmap': 'winter',        'kaleido': True,  'p1': 0.02,  'p2': 0},
    {'engine': 'GS',   'cmap': 'seismic',       'kaleido': False, 'p1': 0.060, 'p2': 0.061},
    {'engine': 'GS',   'cmap': 'hsv',           'kaleido': True,  'p1': 0.030, 'p2': 0.060},
    {'engine': 'PARTICLES', 'cmap': 'rainbow',  'kaleido': True,  'p1': 0.85,  'p2': 5.0},
    {'engine': 'GS',   'cmap': 'plasma',        'kaleido': False, 'p1': 0.018, 'p2': 0.050},
    {'engine': 'KS',   'cmap': 'nipy_spectral', 'kaleido': True,  'p1': 0.1,   'p2': 0},
    {'engine': 'GS',   'cmap': 'magma',         'kaleido': True,  'p1': 0.060, 'p2': 0.061},
    {'engine': 'GS',   'cmap': 'copper',        'kaleido': False, 'p1': 0.035, 'p2': 0.065},
    {'engine': 'GPE',  'cmap': 'inferno',       'kaleido': False, 'p1': -2.0,  'p2': 0},
    {'engine': 'GS',   'cmap': 'spring',        'kaleido': True,  'p1': 0.025, 'p2': 0.060},
    {'engine': 'GS',   'cmap': 'afmhot',        'kaleido': False, 'p1': 0.050, 'p2': 0.063},
    {'engine': 'GS',   'cmap': 'jet',           'kaleido': True,  'p1': 0.045, 'p2': 0.065},
    {'engine': 'PARTICLES', 'cmap': 'cool',     'kaleido': True,  'p1': 0.9,   'p2': 8.0},
    {'engine': 'GS',   'cmap': 'cool',          'kaleido': True,  'p1': 0.020, 'p2': 0.050},
    {'engine': 'GS',   'cmap': 'cividis',       'kaleido': False, 'p1': 0.078, 'p2': 0.061},
    {'engine': 'KS',   'cmap': 'gist_ncar',     'kaleido': True,  'p1': 0.2,   'p2': 0},
    {'engine': 'GS',   'cmap': 'GnBu',          'kaleido': False, 'p1': 0.055, 'p2': 0.062},
    {'engine': 'CH',   'cmap': 'ocean',         'kaleido': False, 'p1': 0.6,   'p2': 0.2},
    {'engine': 'GS',   'cmap': 'rainbow',       'kaleido': True,  'p1': 0.030, 'p2': 0.055},
    {'engine': 'PARTICLES', 'cmap': 'twilight_shifted', 'kaleido': False, 'p1': 0.95, 'p2': 1.0},
    {'engine': 'GS',   'cmap': 'magma',         'kaleido': False, 'p1': 0.055, 'p2': 0.062},
    {'engine': 'WAVE', 'cmap': 'ocean',         'kaleido': False, 'p1': 0.99,  'p2': 0.01}
]
''',
    'src/video_utils.py': r'''import imageio_ffmpeg
import os
try:
    from moviepy import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip

def unir_video_con_musica(video_path, audio_path, output_path, duracion=None):
    print(f"--- 3. Renderizando Audio Final ---")
    
    if not os.path.exists(video_path):
        print(f"❌ Error: El archivo de video '{video_path}' no existe.")
        return
    if os.path.getsize(video_path) == 0:
        print(f"❌ Error: El archivo de video '{video_path}' está vacío (0 bytes). Probablemente el render falló antes.")
        return

    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        if duracion:
            audio = audio.subclip(0, duracion)
            video = video.subclip(0, duracion)
    
        if hasattr(video, 'with_audio'):
            final = video.with_audio(audio)
        else:
            final = video.set_audio(audio)
        
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=video.fps)
    except Exception as e:
        print(f"Error uniendo audio: {e}")
''',
    'src/audio_analyzer.py': r'''import librosa
import numpy as np

def analizar_audio(ruta_audio, fps, duracion=None):
    print(f"--- 1. Deconstruyendo Audio: {ruta_audio} ---")
    
    try:
        y, sr = librosa.load(ruta_audio, duration=duracion)
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return None

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    hop_length = int(sr / fps)
    total_frames = int(len(y) / hop_length)
    
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
    
    S = np.abs(librosa.stft(y, hop_length=hop_length))
    idx_high = int(6000 * 2048 / sr)
    cymbals_raw = np.mean(S[idx_high:, :], axis=0)
    cymbals = (cymbals_raw - np.min(cymbals_raw)) / (np.max(cymbals_raw) - np.min(cymbals_raw) + 1e-6)
    cymbals = np.resize(cymbals, total_frames)
    
    return {
        'y': y, 'sr': sr, 'total_frames': total_frames,
        'rms_perc': rms_perc, 'rms_harm': rms_harm,
        'cent': cent, 'dom_note': dom_note,
        'contrast_mean': contrast_mean, 'cymbals': cymbals
    }
''',
    'src/visual_entities.py': r'''import numpy as np
import matplotlib.pyplot as plt

class EspirituProcedural:
    def __init__(self, ax, seed_val):
        np.random.seed(seed_val)
        self.parts = []
        self.num_brazos = np.random.randint(2, 6)
        self.scale_var = np.random.uniform(0.8, 1.5)
        self.speed_var = np.random.uniform(0.5, 2.0)
        
        for _ in range(4 + self.num_brazos):
            l, = ax.plot([], [], lw=2, alpha=0.0, color='white')
            self.parts.append(l)
            
    def update(self, x, y, scale, t, kick, harm, color_rgb):
        if scale <= 0:
            for p in self.parts: p.set_data([], [])
            return

        scale *= self.scale_var
        t *= self.speed_var
        wobble = np.sin(t * 3) * 0.05 * scale
        
        theta = np.linspace(0, 2*np.pi, 20)
        hx = x + (0.15 * scale * np.cos(theta)) + wobble
        hy = y + (1.6 * scale) + (0.2 * scale * np.sin(theta)) + np.cos(t*2)*0.05
        self.parts[0].set_data(hx, hy)
        self.parts[0].set_color(color_rgb)
        self.parts[0].set_alpha(0.3 + harm*0.5)
        
        ty = np.linspace(y, y + 1.4*scale, 15)
        tx = x + np.sin(ty * 8 + t*4) * 0.08 * scale
        self.parts[1].set_data(tx, ty)
        self.parts[1].set_color(color_rgb)
        self.parts[1].set_alpha(0.2 + harm*0.4)

        for i in range(self.num_brazos):
            angle_base = (i / self.num_brazos) * 2 * np.pi + t * 0.2
            limb_len = np.linspace(0, 1.2*scale, 15)
            lx = x + np.sin(limb_len*3 + t*2 + i)*0.1*scale + np.cos(angle_base) * limb_len
            ly = (y + 0.8*scale) + np.cos(limb_len*3 + t*2 + i)*0.1*scale + np.sin(angle_base) * limb_len * 0.5
            
            idx_part = 2 + i
            self.parts[idx_part].set_data(lx, ly)
            self.parts[idx_part].set_color(color_rgb)
            self.parts[idx_part].set_alpha(0.15 + harm*0.25)

        idx_aura = 2 + self.num_brazos
        if harm > 0.2:
            num_puntos = 12
            angulos = np.linspace(0, 2*np.pi, num_puntos) + t*5
            radios = scale * (1.5 + np.random.uniform(-0.5, 1.0, num_puntos) * (1+kick))
            ax_aura = x + radios * np.cos(angulos)
            ay_aura = y + 0.5*scale + radios * np.sin(angulos)
            
            self.parts[idx_aura].set_data(ax_aura, ay_aura)
            self.parts[idx_aura].set_color(color_rgb)
            self.parts[idx_aura].set_alpha(0.3 * harm)
            self.parts[idx_aura].set_linestyle(':')
        else:
            self.parts[idx_aura].set_data([], [])

        idx_ojos = idx_aura + 1
        ex = [x - 0.06*scale, x + 0.06*scale]
        ey = [y + 1.65*scale, y + 1.65*scale]
        self.parts[idx_ojos].set_data(ex, ey)
        self.parts[idx_ojos].set_color('white') 
        self.parts[idx_ojos].set_marker('o')
        self.parts[idx_ojos].set_markersize(2 + kick * 3)
        self.parts[idx_ojos].set_linestyle('None')
        self.parts[idx_ojos].set_alpha(0.8 + np.sin(t*10)*0.2)

class SuperformaProcedural:
    def __init__(self, ax):
        self.line, = ax.plot([], [], lw=1.5, alpha=0.9)
        
    def update(self, t, kick, harm, color_rgb):
        m = 3 + (harm * 12)
        n1 = 0.5 + kick * 2
        n2 = 1.0 + np.sin(t) 
        n3 = 1.0 + np.cos(t)
        
        phi = np.linspace(0, 2*np.pi, 500)
        part1 = np.abs(np.cos(m * phi / 4.0)) ** n2
        part2 = np.abs(np.sin(m * phi / 4.0)) ** n3
        r = (part1 + part2) ** (-1.0 / n1)
        
        scale = 3.5
        x = r * np.cos(phi) * scale
        y = r * np.sin(phi) * scale
        
        self.line.set_data(x, y)
        self.line.set_color(color_rgb)
        self.line.set_linewidth(1.0 + kick * 3.0)

class LorenzSwarm:
    def __init__(self, ax, num_attractors=3):
        self.attractors = []
        colors = plt.cm.cool(np.linspace(0, 1, num_attractors))
        
        for i in range(num_attractors):
            line, = ax.plot([], [], lw=0.8, alpha=0.7)
            state = np.random.rand(3) * 20 
            offset_x = np.random.uniform(-4.0, 4.0)
            offset_y = np.random.uniform(-2.5, 2.5)
            sigma = 10 + np.random.uniform(-1, 1)
            rho = 28 + np.random.uniform(-2, 2)
            
            self.attractors.append({
                'line': line, 'state': state, 'hist': [[],[],[]], 
                'offset': (offset_x, offset_y), 'params': (sigma, rho, 8/3),
                'color_base': colors[i]
            })

    def update(self, dt_base, kick, cymbals, visible=True):
        if not visible:
            for attr in self.attractors: attr['line'].set_alpha(0.0)
            return

        theta = cymbals * 15.0 
        Ry = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
        
        for attr in self.attractors:
            x, y, z = attr['state']
            sigma, rho, beta = attr['params']
            dt = dt_base * (1 + cymbals * 3.0)
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            new_state = np.array([x + dx*dt, y + dy*dt, z + dz*dt])
            
            if np.max(np.abs(new_state)) > 1e4 or np.isnan(new_state).any():
                attr['state'] = np.random.rand(3) * 10
                attr['hist'] = [[],[],[]]
            else:
                attr['state'] = new_state
                
            attr['hist'][0].append(attr['state'][0])
            attr['hist'][1].append(attr['state'][1])
            attr['hist'][2].append(attr['state'][2])
            if len(attr['hist'][0]) > 80: 
                for k in range(3): attr['hist'][k].pop(0)
                
            pts = np.array(attr['hist']).T
            pts_rot = pts @ Ry
            scale = 0.04
            off_x, off_y = attr['offset']
            shake = np.random.uniform(-0.02, 0.02) * kick
            
            attr['line'].set_data(pts_rot[:, 0] * scale + off_x + shake, pts_rot[:, 2] * scale + off_y + shake)
            attr['line'].set_linewidth(0.5 + cymbals * 2.5)
            attr['line'].set_color(attr['color_base'])
            attr['line'].set_alpha(0.7)

class GeneradorHojas:
    def __init__(self, ax):
        self.ax = ax
        self.hojas = []
        self.max_hojas = 20
        
    def spawn(self, x, y, color):
        if len(self.hojas) >= self.max_hojas:
            oldest = self.hojas.pop(0)
            oldest['line'].remove()
        line, = self.ax.plot([], [], lw=2, color=color, alpha=0.0)
        t = np.linspace(0, 1, 40)
        self.hojas.append({'line': line, 'x': x, 'y': y, 'shape_x': t, 'shape_y': np.sin(t * np.pi) * (0.3 + np.random.rand()*0.2), 'scale': 0.01, 'target_scale': np.random.uniform(0.5, 1.5), 'age': 0, 'angle': np.random.uniform(0, 2*np.pi)})
        
    def update(self, kick, harm):
        for hoja in self.hojas[:]:
            growth_rate = 0.02 + (harm * 0.05)
            if hoja['scale'] < hoja['target_scale']: hoja['scale'] += growth_rate
            hoja['age'] += 1
            c, s = np.cos(hoja['angle']), np.sin(hoja['angle'])
            rx = hoja['shape_x'] * c - hoja['shape_y'] * s
            ry = hoja['shape_x'] * s + hoja['shape_y'] * c
            hoja['line'].set_data(hoja['x'] + rx * hoja['scale'], hoja['y'] + ry * hoja['scale'])
            alpha = 1.0
            if hoja['scale'] < 0.2: alpha = hoja['scale'] * 5
            if hoja['age'] > 150: alpha = max(0, 1.0 - (hoja['age']-150)*0.02)
            hoja['line'].set_alpha(alpha)
            if alpha <= 0:
                hoja['line'].remove()
                self.hojas.remove(hoja)
'''
}

for path, content in archivos.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Creado: {path}")
