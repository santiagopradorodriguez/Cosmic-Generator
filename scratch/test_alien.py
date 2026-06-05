import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from core.rostros_alienigenas import AlienGenerator
import numpy as np

try:
    alien = AlienGenerator(800, 600)
    print("Alien generator initialized.")
    # Test procesar
    energy, kick, snare = 0.5, 0.9, 0.1
    img = alien.procesar(energy, kick, snare)
    print(f"Generated image shape: {img.shape}, dtype: {img.dtype}")
except Exception as e:
    import traceback
    traceback.print_exc()
