import sys
sys.path.insert(0, r"c:\Users\MSI\OneDrive\Documentos\DOCUMENTOS SANTIAGO\Musica mas Python\src")
from render.stable.render_standard import generar_animacion_god_mode
import numpy as np

def progress(msg, p):
    print(f"[{p*100:.1f}%] {msg}")

app_state = {
    'progress_callback': progress,
    'scene_params': None,
    'allowed_engines': None, # None significa TODOS los motores (Mix Mode)
    'color_palette': 'inferno',
    'use_chroma': True,
    'use_flash': False,
    'use_kaleido': False,
    'use_spirits': False,
    'use_lyrics': False,
    'is_reel': False,
    'lyrics_pos': 'Abajo',
    'hq_mode': False,
    'video_seed': 42,
    'test_duration': 15,
    'use_stems': False,
    'use_superposition': False
}

audio_path = r"c:\Users\MSI\OneDrive\Documentos\DOCUMENTOS SANTIAGO\Musica mas Python\temp\Rebeldía Cosmica - Sol Que se Va.flac"
out_path = r"c:\Users\MSI\OneDrive\Documentos\DOCUMENTOS SANTIAGO\Musica mas Python\temp\test_rel.mp4"

generar_animacion_god_mode(
    ruta_audio=audio_path,
    nombre_salida_temp=out_path,
    fps=30,
    duracion=15,
    seed=42,
    allowed_engines=app_state['allowed_engines'],
    use_spirits=False,
    use_kaleido=False,
    use_flash=False,
    use_chroma=False,
    use_lyrics=False,
    use_stems=False,
    is_reel=False
)
