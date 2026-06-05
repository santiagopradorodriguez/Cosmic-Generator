import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from audio.audio_analyzer import analizar_audio
import librosa
import numpy as np

# Test a fake segment of music to see the cut logic
def dummy_test():
    sr = 22050
    hop_length = 512
    # Create 30 seconds of white noise to fake y_mix
    y_mix = np.random.rand(sr * 30) - 0.5
    y_drums = y_mix # fake
    total_frames = len(y_mix) // hop_length
    
    tempo_array, beat_frames = librosa.beat.beat_track(y=y_drums, sr=sr, hop_length=hop_length)
    tempo = float(tempo_array[0]) if isinstance(tempo_array, np.ndarray) else float(tempo_array)
    
    if tempo > 150:
        base_phrase = 32
    elif tempo < 100:
        base_phrase = 8
    else:
        base_phrase = 16
        
    print(f"Tempo: {tempo}, Base Phrase: {base_phrase}")
    
    onset_env = librosa.onset.onset_strength(y=y_mix, sr=sr, hop_length=hop_length)
    # test peak_pick
    peaks = librosa.util.peak_pick(onset_env, pre_max=20, post_max=20, pre_avg=20, post_avg=20, delta=0.5, wait=30)
    print(f"Detected structural peaks: {len(peaks)}")
    
    quantized_cuts = []
    if len(beat_frames) > 0:
        for peak in peaks:
            idx = np.searchsorted(beat_frames, peak)
            if idx == 0:
                quantized_cuts.append(beat_frames[0])
            elif idx == len(beat_frames):
                quantized_cuts.append(beat_frames[-1])
            else:
                left = beat_frames[idx-1]
                right = beat_frames[idx]
                closest = left if (peak - left) < (right - peak) else right
                quantized_cuts.append(closest)
                
    base_cuts = beat_frames[::base_phrase].tolist() if len(beat_frames) > 0 else []
    all_cuts = sorted(list(set(base_cuts + quantized_cuts)))
    
    final_cuts = []
    min_frames_between_cuts = 15
    for cut in all_cuts:
        if len(final_cuts) == 0 or (cut - final_cuts[-1]) > min_frames_between_cuts:
            final_cuts.append(cut)
            
    cut_frames = np.array(final_cuts)
    if len(cut_frames) == 0 or cut_frames[0] != 0:
        cut_frames = np.insert(cut_frames, 0, 0)
    if cut_frames[-1] < total_frames:
        cut_frames = np.append(cut_frames, total_frames)
        
    print(f"Cut frames: {cut_frames}")
    
dummy_test()
