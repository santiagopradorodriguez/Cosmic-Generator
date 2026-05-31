import sys
import torchaudio
import soundfile as sf
import torch

# Parcheamos torchaudio.load para evadir la dependencia de torchcodec en Windows
def mock_load(filepath, *args, **kwargs):
    import numpy as np
    data, samplerate = sf.read(filepath)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    if data.shape[1] == 1:
        # Convertir a estéreo nativamente para evitar que Demucs haga un tensor.expand()
        # el cual genera una dimensión de stride 0 y explota al restarle el valor medio.
        data = np.concatenate([data, data], axis=1)
        
    data = np.ascontiguousarray(data.T) # Convertir a (channels, frames)
    return torch.from_numpy(data).float(), samplerate

# Parcheamos torchaudio.save para guardar usando soundfile directamente
def mock_save(filepath, src, sample_rate, *args, **kwargs):
    data = src.cpu().numpy().T
    sf.write(filepath, data, sample_rate)

torchaudio.load = mock_load
torchaudio.save = mock_save

# Una vez parcheado, importamos y corremos el CLI de Demucs
from demucs.separate import main

if __name__ == "__main__":
    # Eliminamos el nombre del script de sys.argv para que Demucs parsee bien los argumentos
    sys.argv[0] = "demucs"
    main()
