import sys
import os
import time

sys.path.append(os.path.abspath('src'))
from core.nucleo_neural import CPPNEngine

cppn = CPPNEngine(320, 180, hidden_size=24, num_layers=4, seed=42)

start = time.time()
for i in range(10):
    output = cppn.generate_frame(i / 30.0, 0.5)
    print(f"Frame {i} generated. Shape: {output.shape}")
print(f"10 frames generated in {time.time() - start:.2f} seconds.")
