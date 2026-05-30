import numpy as np
import cv2
from numba import jit, prange

# ==========================================
# 1. MOTOR DE REACCIÓN-DIFUSIÓN (GRAY-SCOTT)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_gray_scott(U, V, Du, Dv, f, k, dt):
    """
    Modelado de patrones de Turing y Morfogénesis.
    """
    rows, cols = U.shape
    new_U = np.empty_like(U)
    new_V = np.empty_like(V)
    
    # Laplaciano optimizado (Stencil de 5 puntos)
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            uvv = U[r, c] * V[r, c] * V[r, c]
            
            lap_u = (U[r+1, c] + U[r-1, c] + U[r, c+1] + U[r, c-1] - 4*U[r, c])
            lap_v = (V[r+1, c] + V[r-1, c] + V[r, c+1] + V[r, c-1] - 4*V[r, c])
            
            new_U[r, c] = U[r, c] + (Du * lap_u - uvv + f * (1 - U[r, c])) * dt
            new_V[r, c] = V[r, c] + (Dv * lap_v + uvv - (f + k) * V[r, c]) * dt
            
    return new_U, new_V

# ==========================================
# 2. ECUACIÓN DE ONDAS 2D (ACÚSTICA/INTERFERENCIA)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_ondas(u, u_prev, damping, c2_dt2):
    """
    Resuelve la ecuación de ondas discretizada: U_tt = c^2 * Lap(U)
    Ideal para visualizar interferencias y acústica visual.
    """
    rows, cols = u.shape
    u_next = np.empty_like(u)
    
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            lap = (u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c])
            # Verlet integration
            val = 2*u[r, c] - u_prev[r, c] + c2_dt2 * lap
            u_next[r, c] = val * damping
            
    return u_next

# ==========================================
# 3. MODELO DE KURAMOTO (SINCRONIZACIÓN)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_kuramoto(phases, omega, K, dt, width, height):
    """
    Simulación de osciladores acoplados en una red (Lattice).
    dθ_i/dt = ω_i + K * Σ sin(θ_j - θ_i)
    """
    rows, cols = phases.shape
    new_phases = np.empty_like(phases)
    
    for r in prange(rows):
        for c in range(cols):
            # Acoplamiento con vecinos (Local coupling)
            # Usamos lógica toroidal (borde conecta con borde opuesto)
            r_up, r_down = (r - 1) % rows, (r + 1) % rows
            c_left, c_right = (c - 1) % cols, (c + 1) % cols
            
            # Suma de senos de diferencias de fase
            interaction = (np.sin(phases[r_up, c] - phases[r, c]) +
                           np.sin(phases[r_down, c] - phases[r, c]) +
                           np.sin(phases[r, c_left] - phases[r, c]) +
                           np.sin(phases[r, c_right] - phases[r, c]))
            
            new_phases[r, c] = phases[r, c] + (omega[r, c] + K * interaction) * dt
            
            # Normalizar entre -pi y pi
            if new_phases[r, c] > np.pi: new_phases[r, c] -= 2*np.pi
            if new_phases[r, c] < -np.pi: new_phases[r, c] += 2*np.pi
            
    return new_phases

# ==========================================
# CLASES DE EFECTOS VISUALES (FX)
# ==========================================

class MotorFX:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.prev_frame = np.zeros((h, w, 3), dtype=np.float32)
        
        # Pre-calcular mapas para distorsión de lente (Vignette/Aberración)
        X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        self.radius = np.sqrt(X**2 + Y**2)
        
    def aplicar_bloom(self, img, intensity, threshold=200):
        # Extraer brillos
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        bright = cv2.bitwise_and(img, img, mask=mask)
        
        # Blur agresivo
        blur = cv2.GaussianBlur(bright, (0, 0), sigmaX=15, sigmaY=15)
        return cv2.addWeighted(img, 1.0, blur, intensity, 0)

    def aberracion_cromatica(self, img, strength):
        if strength <= 0: return img
        b, g, r = cv2.split(img)
        
        # Desplazar canales basado en la distancia al centro
        rows, cols = img.shape[:2]
        M = np.float32([[1, 0, strength], [0, 1, 0]])
        r_shift = cv2.warpAffine(r, M, (cols, rows))
        M = np.float32([[1, 0, -strength], [0, 1, 0]])
        b_shift = cv2.warpAffine(b, M, (cols, rows))
        
        return cv2.merge((b_shift, g, r_shift))

    def noise_grain(self, img, amount=0.05):
        noise = np.random.normal(0, amount * 255, img.shape).astype(np.int16)
        img_16 = img.astype(np.int16) + noise
        return np.clip(img_16, 0, 255).astype(np.uint8)

    def feedback_temporal(self, current_frame, decay=0.92):
        self.prev_frame = cv2.addWeighted(current_frame.astype(float), 1.0, 
                                          self.prev_frame, decay, 0)
        return np.clip(self.prev_frame, 0, 255).astype(np.uint8)