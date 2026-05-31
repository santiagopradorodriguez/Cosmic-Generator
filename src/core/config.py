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
    {'engine': 'WAVE', 'cmap': 'ocean',         'kaleido': False, 'p1': 0.99,  'p2': 0.01},
    {'engine': 'KDV',  'cmap': 'viridis',       'kaleido': True,  'p1': 1.0,   'p2': 0.5},
    {'engine': 'CPPN', 'cmap': 'hsv',           'kaleido': True,  'p1': 0.5,   'p2': 0.5}
]
