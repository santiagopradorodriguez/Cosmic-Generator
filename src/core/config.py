# (C) Rebeldía Cósmica | Creado por Santiago Prado
# Configuración Global y Constantes

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

# Paleta Sinestésica Global (Envolvente de la Canción entera)
GLOBAL_MOOD_PALETTES = {
    0: 'inferno',          # C (Do) - Rojo/Fuego (Acción, Energía)
    1: 'plasma',           # C# - Púrpura (Misterio)
    2: 'Wistia',           # D (Re) - Amarillo (Otoño, Alegría, Nostalgia)
    3: 'twilight',         # D# - Oliva/Dorado Oscuro
    4: 'copper',           # E (Mi) - Dorado (Épico, Brillante)
    5: 'afmhot',           # F (Fa) - Marrón/Tierra (Melancolía, Raíces)
    6: 'twilight_shifted', # F# - Naranja Intenso
    7: 'ocean',            # G (Sol) - Azul/Agua (Paz, Fluidez)
    8: 'seismic',          # G# - Violeta/Contraste
    9: 'viridis',          # A (La) - Verde (Naturaleza, Bosque)
    10: 'YlGnBu',          # A# - Verde Azulado
    11: 'winter'           # B (Si) - Cian/Hielo (Cristalino, Frío)
}

# Definición de Actos Visuales por Energía (Dinámico)
# Baja Energía: Intros, Outros, Puentes tranquilos. Visuales flotantes, geométricos, fractales limpios.
ACTOS_LOW_ENERGY = [
    {'engine': 'WAVE',      'cmap': 'ocean',         'kaleido': False, 'p1': 0.1,   'p2': 0.1},
    {'engine': 'ifs',       'cmap': 'copper',        'kaleido': True,  'p1': 0.1,   'p2': 0},
    {'engine': 'CPPN',      'cmap': 'twilight',      'kaleido': False, 'p1': 0.1,   'p2': 0},
    {'engine': 'lorenz',    'cmap': 'bone',          'kaleido': False, 'p1': 0.1,   'p2': 0},
]

# Energía Media: Versos rítmicos. Visuales de evolución constante y crecimiento biológico/caótico.
ACTOS_MID_ENERGY = [
    {'engine': 'GS',        'cmap': 'magma',         'kaleido': False, 'p1': 0.055, 'p2': 0.062},
    {'engine': 'CH',        'cmap': 'viridis',       'kaleido': False, 'p1': 0.1,   'p2': 0.1},
    {'engine': 'ALIEN',     'cmap': 'spring',        'kaleido': False, 'p1': 0.1,   'p2': 0},
    {'engine': 'CLIFFORD',  'cmap': 'rainbow',       'kaleido': False, 'p1': 0.1,   'p2': 0},

    {'engine': 'OK',        'cmap': 'YlGnBu',        'kaleido': False, 'p1': 0.1,   'p2': 0},
    {'engine': 'lorenz',    'cmap': 'hsv',           'kaleido': True,  'p1': 0.1,   'p2': 0},
]

# Alta Energía: Estribillos, Clímax, Drops. Visuales agresivos, explosivos, muy rítmicos.
ACTOS_HIGH_ENERGY = [
    {'engine': 'KS',        'cmap': 'inferno',       'kaleido': True,  'p1': 0.03,  'p2': 0},
    {'engine': 'RELATIVITY','cmap': 'inferno',       'kaleido': False, 'p1': 0.1,   'p2': 0}, # Black Hole
    {'engine': 'GPE',       'cmap': 'plasma',        'kaleido': False, 'p1': -2.0,  'p2': 0},
    {'engine': 'KDV',       'cmap': 'seismic',       'kaleido': True,  'p1': 0.1,   'p2': 0},
    {'engine': 'PARTICLES', 'cmap': 'cool',          'kaleido': True,  'p1': 0.85,  'p2': 5.0},
    {'engine': 'KS',        'cmap': 'winter',        'kaleido': False, 'p1': 0.02,  'p2': 0},
    {'engine': 'WAVE',      'cmap': 'magma',         'kaleido': True,  'p1': 0.1,   'p2': 0.1}, # Wave agitado
]

# Compatibilidad legacy (por si algún módulo busca ACTOS)
ACTOS = ACTOS_LOW_ENERGY + ACTOS_MID_ENERGY + ACTOS_HIGH_ENERGY
