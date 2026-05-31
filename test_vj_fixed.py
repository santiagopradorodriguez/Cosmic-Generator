import sys
import os
sys.path.append(os.path.abspath('src'))
from render.stable.render_standard import generar_animacion_god_mode

if __name__ == "__main__":
    print("Generando video VJ con parches esteticos (Lyrics protegidos, VHS, Melt seguro)...")
    generar_animacion_god_mode(
        ruta_audio=None,
        nombre_salida_temp="QA_vj_fixed.mp4",
        fps=30,
        duracion=5,
        seed=42,
        allowed_engines=['KS'],
        use_spirits=False,
        use_kaleido=False,
        use_flash=True,
        use_chroma=True,
        use_lyrics=True
    )
    print("Video generado exitosamente: QA_vj_fixed.mp4")
