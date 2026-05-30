import numpy as np
import cv2

try:
    from numba import jit, prange
except ImportError:
    # Fallback dummy si no hay numba
    def jit(*args, **kwargs):
        def decorator(func): return func
        return decorator
    def prange(*args): return range(*args)

# ==========================================
# 1. GRAY-SCOTT (OPTIMIZADO + INYECCIÓN)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_gray_scott(U, V, out_U, out_V, Du, Dv, f, k, dt, seed_mask=None, tension=0.0):
    rows, cols = U.shape
    
    # Modulación de parámetros por tensión (Anticipación)
    k_mod = k + (tension * 0.015)
    
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            # Stencil de 5 puntos
            lap_u = (U[r+1, c] + U[r-1, c] + U[r, c+1] + U[r, c-1] - 4*U[r, c])
            lap_v = (V[r+1, c] + V[r-1, c] + V[r, c+1] + V[r, c-1] - 4*V[r, c])
            
            uvv = U[r, c] * V[r, c] * V[r, c]
            
            # Reacción-Difusión
            du = Du * lap_u - uvv + f * (1 - U[r, c])
            dv = Dv * lap_v + uvv - (f + k_mod) * V[r, c]
            
            val_u = U[r, c] + du * dt
            val_v = V[r, c] + dv * dt
            
            # --- INYECCIÓN SEMÁNTICA (TEXTO) ---
            if seed_mask is not None:
                mask_val = seed_mask[r, c]
                if mask_val > 0.1:
                    val_v += mask_val * 0.5 * dt
                    val_u -= mask_val * 0.1 * dt

            # Clamping seguro
            if val_u > 1.0: val_u = 1.0
            elif val_u < 0.0: val_u = 0.0
            if val_v > 1.0: val_v = 1.0
            elif val_v < 0.0: val_v = 0.0
            
            out_U[r, c] = val_u
            out_V[r, c] = val_v

# ==========================================
# 2. ONDAS (OPTIMIZADO)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_ondas(u, u_prev, out_u, damping, c2_dt2, seed_mask=None):
    rows, cols = u.shape
    
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            lap = (u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c])
            val = 2*u[r, c] - u_prev[r, c] + c2_dt2 * lap
            val *= damping
            
            if seed_mask is not None:
                if seed_mask[r, c] > 0.1:
                    val += np.sin(r * 0.5) * 0.1
            
            out_u[r, c] = val

# ==========================================
# 3. KURAMOTO-SIVASHINSKY (ESTABILIZADO)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_ks(u, out_u, dt):
    rows, cols = u.shape
    
    for r in prange(2, rows - 2):
        for c in range(2, cols - 2):
            # Laplaciano
            lap = u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c]
            
            # Biharmónico (Stencil expandido para evitar buffer intermedio)
            bilap = (u[r+2,c] + u[r-2,c] + u[r,c+2] + u[r,c-2] + 
                     2*(u[r+1,c+1] + u[r+1,c-1] + u[r-1,c+1] + u[r-1,c-1]) - 
                     8*(u[r+1,c] + u[r-1,c] + u[r,c+1] + u[r,c-1]) + 20*u[r,c])
            
            # Gradiente al cuadrado
            dx = (u[r, c+1] - u[r, c-1]) * 0.5
            dy = (u[r+1, c] - u[r-1, c]) * 0.5
            grad_sq = dx*dx + dy*dy
            
            val = u[r, c] + dt * (-bilap - lap - grad_sq)
            
            # Estabilidad KS
            if val > 50.0: val = 50.0
            elif val < -50.0: val = -50.0
            
            out_u[r, c] = val
            
    out_u[0:2, :] = 0; out_u[-2:, :] = 0
    out_u[:, 0:2] = 0; out_u[:, -2:] = 0

# ==========================================
# 4. GROSS-PITAEVSKII (RENORMALIZADO)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_gpe(psi_real, psi_imag, out_r, out_i, V, g, dt):
    rows, cols = psi_real.shape
    total_prob = 0.0
    
    # Paso 1: Evolución
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            lap_r = psi_real[r+1, c] + psi_real[r-1, c] + psi_real[r, c+1] + psi_real[r, c-1] - 4*psi_real[r, c]
            lap_i = psi_imag[r+1, c] + psi_imag[r-1, c] + psi_imag[r, c+1] + psi_imag[r, c-1] - 4*psi_imag[r, c]
            
            densidad = psi_real[r, c]**2 + psi_imag[r, c]**2
            potencial = V[r, c] + g * densidad
            
            H_real = -0.5 * lap_r + potencial * psi_real[r, c]
            H_imag = -0.5 * lap_i + potencial * psi_imag[r, c]
            
            nr = psi_real[r, c] + H_imag * dt
            ni = psi_imag[r, c] - H_real * dt
            
            out_r[r, c] = nr
            out_i[r, c] = ni
            
    # Paso 2: Renormalización de Probabilidad (Fórmula: Psi = Psi / sqrt(sum(|Psi|^2)))
    for r in range(rows):
        for c in range(cols):
            total_prob += out_r[r, c]**2 + out_i[r, c]**2
            
    if total_prob > 1e-6:
        norm_factor = 1.0 / np.sqrt(total_prob)
        for r in prange(rows):
            for c in range(cols):
                out_r[r, c] *= norm_factor
                out_i[r, c] *= norm_factor

# ==========================================
# 5. CAHN-HILLIARD (OPTIMIZADO)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_cahn_hilliard(u, out_u, dt, gamma, mobility):
    rows, cols = u.shape
    # Simplificación para evitar buffer intermedio 'mu'
    # Usamos pseudo-difusión directa para visualización
    for r in prange(2, rows - 2):
        for c in range(2, cols - 2):
            lap_u = u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c]
            mu = (u[r, c]**3 - u[r, c]) - gamma * lap_u
            
            val = u[r, c] - dt * mobility * mu
            
            if val > 1.0: val = 1.0
            elif val < -1.0: val = -1.0
            out_u[r, c] = val


# ==========================================
# 6. KORTEWEG-DE VRIES (ZK EQUATION 2D)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_kdv(u, out_u, dt, alpha, beta):
    rows, cols = u.shape
    
    for r in prange(2, rows - 2):
        for c in range(2, cols - 2):
            # Derivada primera en X (u_x)
            ux = 0.5 * (u[r, c+1] - u[r, c-1])
            
            # Derivada tercera en X (u_xxx)
            uxxx = 0.5 * (u[r, c+2] - 2*u[r, c+1] + 2*u[r, c-1] - u[r, c-2])
            
            # Derivada mixta (u_xyy) -> (u_y)_y_x approx D_x(D_yy(u))
            # D_yy en c+1
            uyy_right = u[r+1, c+1] - 2*u[r, c+1] + u[r-1, c+1]
            # D_yy en c-1
            uyy_left = u[r+1, c-1] - 2*u[r, c-1] + u[r-1, c-1]
            uxyy = 0.5 * (uyy_right - uyy_left)
            
            # Ecuación ZK: u_t + alpha*u*u_x + beta*(u_xxx + u_xyy) = 0
            du = - (alpha * u[r, c] * ux + beta * (uxxx + uxyy))
            
            val = u[r, c] + dt * du
            
            # Clamping para estabilidad visual
            if val > 10.0: val = 10.0
            elif val < -10.0: val = -10.0
            
            out_u[r, c] = val
            
    # Condiciones de frontera
    out_u[0:2, :] = 0; out_u[-2:, :] = 0
    out_u[:, 0:2] = 0; out_u[:, -2:] = 0

@jit(nopython=True, parallel=True, fastmath=True)
def update_particles(pos, vel, force_field, width, height, damp, max_speed, seed_mask=None):
    n = pos.shape[0]
    for i in prange(n):
        x, y = int(pos[i, 0]), int(pos[i, 1])
        
        if 0 <= x < width and 0 <= y < height:
            fx = force_field[y, x, 0]
            fy = force_field[y, x, 1]
            
            if seed_mask is not None:
                if seed_mask[y, x] > 0.1:
                    fx += np.random.normal(0, 1.0)
                    fy -= 2.0 # Hacia arriba
            
            vel[i, 0] += fx
            vel[i, 1] += fy
        
        speed = np.sqrt(vel[i, 0]**2 + vel[i, 1]**2)
        if speed > max_speed:
            vel[i] = (vel[i] / speed) * max_speed
            
        pos[i] += vel[i]
        vel[i] *= damp
        
        if pos[i, 0] < 0: pos[i, 0] += width
        if pos[i, 0] >= width: pos[i, 0] -= width
        if pos[i, 1] < 0: pos[i, 1] += height
        if pos[i, 1] >= height: pos[i, 1] -= height

    return pos, vel