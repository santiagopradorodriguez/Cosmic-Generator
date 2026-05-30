import sys
import os

# Asegurar que el modulo src se pueda importar
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.render.stable.render_standard import generar_animacion_god_mode

audio_path = "temp/Rebeldia Cosmica - La Realidad.flac"
out_temp = "temp_QA_video.mp4"

print("Iniciando Render de Test QA (5 Segundos)")

exito = generar_animacion_god_mode(
    ruta_audio=audio_path,
    nombre_salida_temp=out_temp,
    fps=30,
    duracion=5, # Solo 5 segundos para test visual
    seed=42,
    allowed_engines=['CH', 'WAVE', 'GS'], # Usar algunos clásicos para ver interacción
    use_spirits=True,
    use_kaleido=True,
    use_flash=True,
    use_chroma=False,
    use_lyrics=True,
    global_cmap="inferno"
)

if exito:
    print(f"Video generado con exito en {out_temp}")
else:
    print("Error generando video")
