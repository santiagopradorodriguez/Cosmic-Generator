import librosa
import numpy as np
import pandas as pd

# --- CONFIGURACIÓN ---
RUTA_CANCION = r"data\Rebeldía Cosmica - Sol Que se Va.flac"
FPS = 30
NUM_BANDAS = 10  # Vamos a crear 10 barras de ecualizador

print(f"Procesando espectro de {RUTA_CANCION}...")

y, sr = librosa.load(RUTA_CANCION)
hop_length = int(sr / FPS)

# 1. ESPECTROGRAMA DE MEL (La forma en que el oído humano escucha)
# Esto separa el audio en 'NUM_BANDAS' frecuencias distintas.
spectrogram = librosa.feature.melspectrogram(
    y=y, sr=sr, n_fft=2048, hop_length=hop_length, n_mels=NUM_BANDAS
)

# 2. Convertir a Decibeles (Escala logarítmica)
# Porque la amplitud lineal no se ve bien visualmente.
spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)

# 3. Normalizar entre 0 y 1 para cada banda
# Transponemos la matriz para tener (Tiempo, Bandas)
data_norm = []
for banda in spectrogram_db:
    min_val = np.min(banda)
    max_val = np.max(banda)
    # Evitamos dividir por cero
    if max_val - min_val == 0:
        data_norm.append(np.zeros_like(banda))
    else:
        # Normalizamos y sumamos un offset para que no quede todo chato
        norm = (banda - min_val) / (max_val - min_val)
        data_norm.append(norm)

data_norm = np.array(data_norm).T  # Transponer

# 4. Guardar CSV
columnas = [f'banda_{i}' for i in range(NUM_BANDAS)]
df = pd.DataFrame(data_norm, columns=columnas)
# Agregamos el frame por las dudas
df['frame'] = range(len(df))

nombre_csv = "datos_espectro.csv"
df.to_csv(nombre_csv, index=False)

print(f"¡Listo! Generamos {len(df)} frames con {NUM_BANDAS} bandas de frecuencia.")
print(f"Archivo guardado: {nombre_csv}")