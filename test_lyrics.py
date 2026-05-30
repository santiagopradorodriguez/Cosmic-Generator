import os
import sys
import numpy as np
import cv2
import argparse
import shutil

# Asegurar que podemos importar desde src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from motor_lyrics import LyricsEngine
except ImportError as e:
    print(f"❌ No se pudo importar LyricsEngine: {e}")
    print("Asegúrate de que 'src/motor_lyrics.py' existe.")
    sys.exit(1)

def run_test():
    print("========================================")
    print("🧪 TEST UNITARIO: MOTOR LYRICS")
    print("========================================")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", nargs="?", default=r"data\Rebeldía Cosmica - Chica Lunar.flac", help="Ruta del archivo de audio")
    args = parser.parse_args()
    audio_file = args.audio

    # 1. Verificar Dependencia stable-ts
    print("\n[1] Verificando librería 'stable-ts'...")
    try:
        import stable_whisper
        print("   ✅ stable-ts está instalada.")
    except ImportError:
        print("   ❌ stable-ts NO encontrada.")
        print("   ⚠️ El test continuará simulando la transcripción, pero el programa real fallará.")

    # 1.5 Verificar FFmpeg antes de empezar
    print("\n[1.5] Verificando disponibilidad de FFmpeg en el sistema...")
    if shutil.which("ffmpeg"):
        print(f"   ✅ FFmpeg detectado en: {shutil.which('ffmpeg')}")
    else:
        print("   ⚠️ FFmpeg no está en el PATH global (LyricsEngine intentará arreglarlo).")

    # 2. Inicialización del Motor (Mock)
    print(f"\n[2] Inicializando LyricsEngine con: {audio_file}")
    print("    (Esto buscará metadatos internos en el FLAC o archivo .txt)")
    
    if not os.path.exists(audio_file):
        print(f"⚠️ ADVERTENCIA: No se encontró '{audio_file}'.")
        print("   Asegúrate de poner el nombre correcto o pasar la ruta como argumento.")
        # Creamos un archivo dummy vacío para que no falle la carga, aunque la transcripción fallará
        with open("test_audio_dummy.mp3", "w") as f: f.write("dummy")
        audio_file = "test_audio_dummy.mp3"
    else:
        # Si existe el archivo de audio real, BORRAMOS el JSON antiguo para forzar
        # la re-transcripción con el nuevo modelo
        json_path = os.path.splitext(audio_file)[0] + ".json"
        if os.path.exists(json_path):
            print(f"   🗑️ Borrando caché antiguo (posiblemente corrupto): {json_path}")
            try: os.remove(json_path)
            except: pass
            
        # Verificar si hay txt para alineación
        txt_path = os.path.splitext(audio_file)[0] + ".txt"
        if os.path.exists(txt_path):
            print(f"   📄 DETECTADO: Archivo de letra '{os.path.basename(txt_path)}'. Se usará para corrección.")
            with open(txt_path, 'r', encoding='utf-8') as f:
                preview = f.read().strip()[:100].replace('\n', ' ')
                print(f"      Contenido: \"{preview}...\"")
    
    # Instanciamos. Esto intentará transcribir y fallará controladamente (imprimirá error), 
    # pero el objeto se creará correctamente.
    engine = LyricsEngine(audio_file)
    
    # 3. Inyección de Datos de Prueba
    print(f"\n[3] Verificando extracción de palabras...")
    if engine.words:
        print(f"   ✅ Se detectaron {len(engine.words)} palabras/segmentos.")
        print(f"   📝 Primeras 5 palabras: {[w['text'] for w in engine.words[:5]]}")
    else:
        print("   ❌ No se detectaron palabras (o falló la transcripción).")

    print("\n✅ Test finalizado.")

if __name__ == "__main__":
    run_test()