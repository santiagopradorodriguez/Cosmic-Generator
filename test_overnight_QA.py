import sys
import os
import time

# Aseguramos el PATH
sys.path.append(os.path.abspath('src'))

from render.stable.render_standard import generar_animacion_god_mode
from render.stable.render_laboratorio import simular_laboratorio_puro

def run_tests():
    print("======================================================")
    print("--- INICIANDO QA OVERNIGHT: COOPERATIVA DE IA ---")
    print("======================================================")
    
    motores_a_probar = ['GS', 'KS', 'GPE', 'WAVE', 'CLIFFORD', 'CPPN']
    
    print("\n--- FASE 1: PROBANDO GENERADOR DE VIDEOS MUSICALES ---")
    for motor in motores_a_probar:
        print(f"\n[Arte VJ] Probando Motor: {motor}")
        start = time.time()
        try:
            success = generar_animacion_god_mode(
                ruta_audio=None,
                nombre_salida_temp=f"QA_vj_{motor}.mp4",
                fps=30,
                duracion=5,
                seed=42,
                allowed_engines=[motor]
            )
            if success:
                print(f"[OK] VJ {motor} completado en {time.time()-start:.2f}s")
            else:
                print(f"[FAIL] VJ {motor} retornó False.")
        except Exception as e:
            print(f"[CRASH] VJ {motor} generó excepción: {e}")
            
    print("\n--- FASE 2: PROBANDO LABORATORIO DE FÍSICA PURA ---")
    for motor in motores_a_probar:
        print(f"\n[Ciencia] Probando Motor: {motor}")
        start = time.time()
        try:
            success = simular_laboratorio_puro(
                nombre_salida=f"QA_lab_{motor}.mp4",
                fps=30,
                duracion=5,
                seed=42,
                engine_code=motor
            )
            if success:
                print(f"[OK] LAB {motor} completado en {time.time()-start:.2f}s")
            else:
                print(f"[FAIL] LAB {motor} retornó False.")
        except Exception as e:
            print(f"[CRASH] LAB {motor} generó excepción: {e}")

    print("\n======================================================")
    print("--- BATERIA DE PRUEBAS OVERNIGHT FINALIZADA ---")
    print("======================================================")

if __name__ == "__main__":
    run_tests()
