import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.nucleo_visual import simulacion_gray_scott, simulacion_ks, simulacion_gpe

W, H = 256, 256

print("--- DIAGNÓSTICO MATEMÁTICO DIRECTO ---")

# 1. GRAY SCOTT
print("\n--- Test Gray-Scott ---")
gs_h, gs_w = 256, 256
U = np.ones((gs_h, gs_w), dtype=np.float32)
V = np.zeros((gs_h, gs_w), dtype=np.float32)
U_next = np.zeros_like(U); V_next = np.zeros_like(V)
V[100:150, 100:150] = 0.5
Da, Db, f, k = 0.16, 0.08, 0.060, 0.062

try:
    for i in range(200):
        simulacion_gray_scott(U, V, U_next, V_next, Da, Db, f, k, dt=1.0)
        U, U_next = U_next, U
        V, V_next = V_next, V
        if i % 50 == 0 or i == 199:
            print(f"GS Frame {i}: V min={np.min(V):.4f}, max={np.max(V):.4f}, mean={np.mean(V):.4f}")
except Exception as e:
    print(f"Error en Gray-Scott: {e}")
        
# 2. KURAMOTO
print("\n--- Test Kuramoto-Sivashinsky ---")
ks_u = np.zeros((gs_h, gs_w), dtype=np.float32) + np.random.normal(0, 0.1, (gs_h, gs_w))
ks_u_next = np.zeros_like(ks_u)

try:
    for i in range(200):
        simulacion_ks(ks_u, ks_u_next, dt=0.05)
        ks_u, ks_u_next = ks_u_next, ks_u
        if i % 50 == 0 or i == 199:
            print(f"KS Frame {i}: u min={np.min(ks_u):.4f}, max={np.max(ks_u):.4f}")
except Exception as e:
    print(f"Error en Kuramoto: {e}")

print("Terminado.")
