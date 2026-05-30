import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from render.stable.render_standard import generar_animacion_god_mode

cancion_prueba = r"C:\Users\MSI\OneDrive\Documentos\DOCUMENTOS SANTIAGO\Musica mas Python\data\Rebeldía Cosmica - Sol Que se Va.flac"

motores = ['GS', 'KS', 'GPE', 'WAVE', 'CH', 'KDV', 'PARTICLES']

print("--- INICIANDO BATERIA DE PRUEBAS ---")
for motor in motores:
    print(f"\nProbando Motor: {motor}")
    output_name = f"test_{motor}.mp4"
    try:
        exito = generar_animacion_god_mode(
            ruta_audio=cancion_prueba,
            nombre_salida_temp=output_name,
            fps=30,
            duracion=3.0, # 3 segundos para ir rápido
            seed=42,
            allowed_engines=[motor],
            use_spirits=False,
            use_kaleido=False,
            use_flash=False,
            use_chroma=False,
            use_lyrics=False,
            global_cmap='magma'
        )
    except Exception as e:
        print(f"Error {motor}: {e}")
