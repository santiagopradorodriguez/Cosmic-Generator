import sys
import os
import time
sys.path.append(os.path.abspath('src'))

from render.stable.render_standard import generar_animacion_god_mode
from core.config import ACTOS

def run_tests():
    print("--- INICIANDO BATERIA DE PRUEBAS RAPIDAS (5 SEGUNDOS) ---")
    
    # Intentar usar un archivo de audio real de 5s, o dejar que Laboratorio genere uno sintético.
    # Dado que estamos probando TODOS los motores, usaremos el modo Laboratorio (ruta_audio=None) para que no dependa de archivos.
    
    for motor in ACTOS:
        print(f"\nProbando Motor: {motor}")
        start = time.time()
        try:
            success = generar_animacion_god_mode(
                ruta_audio=None,
                nombre_salida_temp=f"temp_test_{motor}.mp4",
                fps=30,
                duracion=5, # 5 segundos
                seed=42,
                allowed_engines=[motor],
                use_spirits=False,
                use_kaleido=False,
                use_flash=False,
                use_chroma=False,
                use_lyrics=False,
                progress_callback=None
            )
            if success:
                print(f"✅ {motor} OK - Tiempo: {time.time()-start:.2f}s")
            else:
                print(f"❌ {motor} FAIL - Fallo interno.")
        except Exception as e:
            print(f"❌ {motor} CRASH: {e}")

if __name__ == "__main__":
    run_tests()
