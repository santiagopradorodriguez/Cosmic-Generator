import librosa
import numpy as np

def analizar_audio(ruta_audio, fps, duracion=None):
    print(f"--- 1. Deconstruyendo Audio: {ruta_audio} ---")
    
    try:
        y, sr = librosa.load(ruta_audio, duration=duracion)
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
        return None

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    hop_length = int(sr / fps)
    total_frames = int(len(y) / hop_length)
    
    rms_perc = librosa.feature.rms(y=y_percussive, hop_length=hop_length)[0]
    rms_perc = rms_perc / (np.max(rms_perc) + 1e-6)
    rms_perc = np.resize(rms_perc, total_frames)
    
    rms_harm = librosa.feature.rms(y=y_harmonic, hop_length=hop_length)[0]
    rms_harm = rms_harm / (np.max(rms_harm) + 1e-6)
    rms_harm = np.resize(rms_harm, total_frames)
    
    cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    cent = np.log1p(cent)
    cent = (cent - np.min(cent)) / (np.max(cent) - np.min(cent) + 1e-6)
    cent = np.resize(cent, total_frames)
    
    chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, hop_length=hop_length)
    dom_note = np.argmax(chroma, axis=0)
    dom_note = np.resize(dom_note, total_frames)
    
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    contrast_mean = np.mean(contrast, axis=0)
    contrast_mean = (contrast_mean - np.min(contrast_mean)) / (np.max(contrast_mean) - np.min(contrast_mean) + 1e-6)
    contrast_mean = np.resize(contrast_mean, total_frames)
    
    S = np.abs(librosa.stft(y, hop_length=hop_length))
    idx_high = int(6000 * 2048 / sr)
    cymbals_raw = np.mean(S[idx_high:, :], axis=0)
    cymbals = (cymbals_raw - np.min(cymbals_raw)) / (np.max(cymbals_raw) - np.min(cymbals_raw) + 1e-6)
    cymbals = np.resize(cymbals, total_frames)
    
    return {
        'y': y, 'sr': sr, 'total_frames': total_frames,
        'rms_perc': rms_perc, 'rms_harm': rms_harm,
        'cent': cent, 'dom_note': dom_note,
        'contrast_mean': contrast_mean, 'cymbals': cymbals
    }
