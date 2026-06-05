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
    
    # Extraer Tonalidad Reina (Global Note)
    global_chroma = np.sum(chroma, axis=1)
    global_note = int(np.argmax(global_chroma))
    
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    contrast_mean = np.mean(contrast, axis=0)
    contrast_mean = (contrast_mean - np.min(contrast_mean)) / (np.max(contrast_mean) - np.min(contrast_mean) + 1e-6)
    contrast_mean = np.resize(contrast_mean, total_frames)
    
    S = np.abs(librosa.stft(y, hop_length=hop_length))
    idx_high = int(6000 * 2048 / sr)
    cymbals_raw = np.mean(S[idx_high:, :], axis=0)
    cymbals = (cymbals_raw - np.min(cymbals_raw)) / (np.max(cymbals_raw) - np.min(cymbals_raw) + 1e-6)
    cymbals = np.resize(cymbals, total_frames)
    
    # Detectar BPM y Beats (Frases estructurales cada 16 beats)
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr, hop_length=hop_length)
    phrase_length = 16
    cut_frames = beat_frames[::phrase_length] if len(beat_frames) > 0 else np.array([])
    if len(cut_frames) == 0 or cut_frames[0] != 0:
        cut_frames = np.insert(cut_frames, 0, 0)
    if cut_frames[-1] < total_frames:
        cut_frames = np.append(cut_frames, total_frames)
    
    return {
        'y': y, 'sr': sr, 'total_frames': total_frames,
        'rms_perc': rms_perc, 'rms_harm': rms_harm,
        'cent': cent, 'dom_note': dom_note,
        'contrast_mean': contrast_mean, 'cymbals': cymbals,
        'global_note': global_note,
        'tempo': tempo, 'cut_frames': cut_frames
    }

import os
def analizar_stems(stem_folder, fps, duracion=None):
    print(f"--- 1. Analizando Stems de Audio en: {stem_folder} ---")
    
    stems_data = {}
    
    # Archivos esperados
    archivos = {
        'drums': 'drums.wav',
        'bass': 'bass.wav',
        'vocals': 'vocals.wav',
        'other': 'other.wav'
    }
    
    # Cargar primero bass para sacar sr y total_frames de referencia
    try:
        y_bass, sr = librosa.load(os.path.join(stem_folder, archivos['bass']), duration=duracion)
    except FileNotFoundError:
        print("Error: No se encontraron los archivos de stems.")
        return None
        
    hop_length = int(sr / fps)
    total_frames = int(len(y_bass) / hop_length)
    
    # Función auxiliar para extraer RMS normalizado
    def extraer_rms(y, hop):
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        rms = rms / (np.max(rms) + 1e-6)
        return np.resize(rms, total_frames)
        
    def extraer_onsets(y, sr, hop):
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
        onset_env = onset_env / (np.max(onset_env) + 1e-6)
        return np.resize(onset_env, total_frames)
        
    def extraer_centroide(y, sr, hop):
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]
        cent = np.log1p(cent)
        cent = (cent - np.min(cent)) / (np.max(cent) - np.min(cent) + 1e-6)
        return np.resize(cent, total_frames)

    # 1. Bass (Bajo) -> RMS controla gravedad/grosor
    stems_data['bass_rms'] = extraer_rms(y_bass, hop_length)
    
    # 2. Drums (Batería) -> Onsets controla caos, temblor y explosiones
    y_drums, _ = librosa.load(os.path.join(stem_folder, archivos['drums']), sr=sr, duration=duracion)
    stems_data['drums_onsets'] = extraer_onsets(y_drums, sr, hop_length)
    stems_data['drums_rms'] = extraer_rms(y_drums, hop_length)
    
    # 3. Vocals (Voces) -> RMS y Onsets controlan brillo/letras
    y_vocals, _ = librosa.load(os.path.join(stem_folder, archivos['vocals']), sr=sr, duration=duracion)
    stems_data['vocals_rms'] = extraer_rms(y_vocals, hop_length)
    
    # 4. Other (Pads/Synths) -> Centroide controla color/rotación
    y_other, _ = librosa.load(os.path.join(stem_folder, archivos['other']), sr=sr, duration=duracion)
    stems_data['other_rms'] = extraer_rms(y_other, hop_length)
    stems_data['other_cent'] = extraer_centroide(y_other, sr, hop_length)
    
    # Devolveremos también el audio mezclado (o simplemente el de mayor impacto)
    # para no romper el código legacy que espera 'y' y 'sr'
    y_mix = y_bass + y_drums + y_vocals + y_other
    y_mix = y_mix / (np.max(np.abs(y_mix)) + 1e-6)
    
    # Extraer Tonalidad Reina (Global Note) de la mezcla armónica (pads + voces)
    y_harmonic_mix = y_other + y_vocals
    chroma_mix = librosa.feature.chroma_stft(y=y_harmonic_mix, sr=sr, hop_length=hop_length)
    global_chroma = np.sum(chroma_mix, axis=1)
    global_note = int(np.argmax(global_chroma))
    
    # Detectar BPM y Beats (Frases estructurales cada 16 beats)
    tempo, beat_frames = librosa.beat.beat_track(y=y_drums, sr=sr, hop_length=hop_length)
    phrase_length = 16
    cut_frames = beat_frames[::phrase_length] if len(beat_frames) > 0 else np.array([])
    if len(cut_frames) == 0 or cut_frames[0] != 0:
        cut_frames = np.insert(cut_frames, 0, 0)
    if cut_frames[-1] < total_frames:
        cut_frames = np.append(cut_frames, total_frames)
    
    # Devolver estructura compatible con analizar_audio original pero expandida
    return {
        'y': y_mix, 'sr': sr, 'total_frames': total_frames,
        'rms_perc': stems_data['drums_rms'], # Fallback legacy
        'rms_harm': stems_data['other_rms'], # Fallback legacy
        'cent': stems_data['other_cent'],    # Fallback legacy
        'stems': stems_data,                 # Nuevo diccionario multidimensional
        'global_note': global_note,          # Tonalidad Reina
        'tempo': tempo, 'cut_frames': cut_frames
    }
