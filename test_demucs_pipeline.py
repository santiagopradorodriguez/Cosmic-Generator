import os
import subprocess
import sys
import numpy as np
import soundfile as sf
import tempfile

def test_demucs_pipeline():
    print("Generando audio de prueba estéreo (2 canales)...")
    sr = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    # Generar señal estéreo
    left_channel = np.sin(2 * np.pi * 440 * t)
    right_channel = np.sin(2 * np.pi * 880 * t)
    audio_data = np.vstack((left_channel, right_channel)).T
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        test_wav = tmp_file.name
        
    sf.write(test_wav, audio_data, sr, subtype='PCM_16')
    print(f"Archivo de prueba creado en: {test_wav}")
    
    stem_output_dir = os.path.join(os.getcwd(), "STEMS_TEST")
    os.makedirs(stem_output_dir, exist_ok=True)
    
    script_wrapper = os.path.join(os.getcwd(), "run_demucs.py")
    
    cmd = [sys.executable, script_wrapper, "-n", "htdemucs", "-o", stem_output_dir, test_wav]
    
    print(f"Ejecutando demucs wrapper: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ ÉXITO. Salida de demucs:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ FALLO. Error en demucs:")
        print(e.stderr)
    finally:
        if os.path.exists(test_wav):
            os.remove(test_wav)

if __name__ == "__main__":
    test_demucs_pipeline()
