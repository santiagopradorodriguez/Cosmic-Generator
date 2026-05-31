# (C) Rebeldía Cósmica | Creado por Santiago Prado
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
            # Stencil de 9 puntos (Laplaciano Isotrópico ESCALADO espacialmente)
            dx_g = 1.2 # Mayor a 1 = Estructuras más grandes y suaves
            lap_u = (0.8 * (U[r+1, c] + U[r-1, c] + U[r, c+1] + U[r, c-1]) + 0.2 * (U[r+1, c+1] + U[r+1, c-1] + U[r-1, c+1] + U[r-1, c-1]) - 4.0 * U[r, c]) / (dx_g**2)
            lap_v = (0.8 * (V[r+1, c] + V[r-1, c] + V[r, c+1] + V[r, c-1]) + 0.2 * (V[r+1, c+1] + V[r+1, c-1] + V[r-1, c+1] + V[r-1, c-1]) - 4.0 * V[r, c]) / (dx_g**2)
            
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
            # Stencil escalado espacialmente
            dx_g = 1.2
            lap = (0.8 * (u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1]) + 0.2 * (u[r+1, c+1] + u[r+1, c-1] + u[r-1, c+1] + u[r-1, c-1]) - 4.0 * u[r, c]) / (dx_g**2)
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
            # Grid scale (Estructuras más grandes y turbulentas)
            dx_g = 1.5
            
            # Laplaciano
            lap = (u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c]) / (dx_g**2)
            
            # Biharmónico (Stencil expandido para evitar buffer intermedio)
            bilap = (u[r+2,c] + u[r-2,c] + u[r,c+2] + u[r,c-2] + 
                     2*(u[r+1,c+1] + u[r+1,c-1] + u[r-1,c+1] + u[r-1,c-1]) - 
                     8*(u[r+1,c] + u[r-1,c] + u[r,c+1] + u[r,c-1]) + 20*u[r,c]) / (dx_g**4)
            
            # Gradiente al cuadrado
            dx = (u[r, c+1] - u[r, c-1]) * 0.5 / dx_g
            dy = (u[r+1, c] - u[r-1, c]) * 0.5 / dx_g
            grad_sq = dx*dx + dy*dy
            
            val = u[r, c] + dt * (-bilap - lap - grad_sq)
            
            # Estabilidad KS: Clamping suave con tanh (evita bloqueos numéricos)
            val = np.tanh(val / 20.0) * 20.0
            
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
            # Stencil escalado x4
            dx_g = 1.2
            lap_r = (0.8 * (psi_real[r+1, c] + psi_real[r-1, c] + psi_real[r, c+1] + psi_real[r, c-1]) + 0.2 * (psi_real[r+1, c+1] + psi_real[r+1, c-1] + psi_real[r-1, c+1] + psi_real[r-1, c-1]) - 4.0 * psi_real[r, c]) / (dx_g**2)
            lap_i = (0.8 * (psi_imag[r+1, c] + psi_imag[r-1, c] + psi_imag[r, c+1] + psi_imag[r, c-1]) + 0.2 * (psi_imag[r+1, c+1] + psi_imag[r+1, c-1] + psi_imag[r-1, c+1] + psi_imag[r-1, c-1]) - 4.0 * psi_imag[r, c]) / (dx_g**2)
            
            densidad = psi_real[r, c]**2 + psi_imag[r, c]**2
            potencial = V[r, c] + g * densidad
            
            H_real = -0.5 * lap_r + potencial * psi_real[r, c]
            H_imag = -0.5 * lap_i + potencial * psi_imag[r, c]
            
            # Clamping suave de la fase para evitar explosión numérica en Euler Explícito
            nr = psi_real[r, c] + np.tanh(H_imag * dt)
            ni = psi_imag[r, c] - np.tanh(H_real * dt)
            
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
# 5A. OHTA-KAWASAKI (FRUSTRACIÓN TOPOLÓGICA / ALLEN-CAHN EXTENDIDO)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_ohta_kawasaki(u, out_u, dt, gamma, mobility, sigma=0.08):
    rows, cols = u.shape
    
    # Calcular masa media para interacción no-local
    u_mean = 0.0
    for r in range(rows):
        for c in range(cols):
            u_mean += u[r, c]
    u_mean /= (rows * cols)

    for r in prange(2, rows - 2):
        for c in range(2, cols - 2):
            dx_g = 1.5
            lap_u = (u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c]) / (dx_g**2)
            
            # Potencial químico (doble pozo)
            mu = (u[r, c]**3 - u[r, c]) - gamma * lap_u
            
            # Evolución con repulsión de largo alcance (Frustración Topológica)
            val = u[r, c] - dt * mobility * mu - dt * sigma * (u[r, c] - u_mean)
            
            val = np.tanh(val) # Clamping suave
            out_u[r, c] = val

# ==========================================
# 5B. CAHN-HILLIARD (CLÁSICO / ACEITE Y AGUA)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_cahn_hilliard(u, out_u, dt, gamma, mobility):
    rows, cols = u.shape
    mu = np.zeros_like(u)
    
    # Paso 1: Calcular potencial químico (mu) en todo el grid
    for r in prange(1, rows - 1):
        for c in range(1, cols - 1):
            lap_u = u[r+1, c] + u[r-1, c] + u[r, c+1] + u[r, c-1] - 4*u[r, c]
            mu[r, c] = (u[r, c]**3 - u[r, c]) - gamma * lap_u
            
    # Paso 2: Evolucionar u usando el Laplaciano de mu (Conservación de masa)
    for r in prange(2, rows - 2):
        for c in range(2, cols - 2):
            lap_mu = mu[r+1, c] + mu[r-1, c] + mu[r, c+1] + mu[r, c-1] - 4*mu[r, c]
            # La verdadera ec. Cahn-Hilliard usa + Laplaciano(mu)
            val = u[r, c] + dt * mobility * lap_mu
            
            # Estabilidad visual: Clamping suave
            val = np.tanh(val)
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
            
            # Clamping suave (evita saltos bruscos en los solitones)
            val = np.tanh(val / 15.0) * 15.0
            
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

# ==========================================
# 7. CAOS 3D (ATRACTOR DE LORENZ)
# ==========================================
@jit(nopython=True, parallel=True, fastmath=True)
def simulacion_lorenz(particulas, dt, sigma=10.0, rho=28.0, beta=8.0/3.0):
    n = particulas.shape[0]
    for i in prange(n):
        x = particulas[i, 0]
        y = particulas[i, 1]
        z = particulas[i, 2]
        
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        
        particulas[i, 0] += dx
        particulas[i, 1] += dy
        particulas[i, 2] += dz
    return particulas

# ==========================================
# 8. FRACTALES IFS (GEOMETRÍA SAGRADA)
# ==========================================
@jit(nopython=True, fastmath=True)
def simulacion_ifs(grid, iters, transform_matrix, prob, cx, cy):
    h, w = grid.shape
    x, y = 0.0, 0.0
    N = transform_matrix.shape[0]
    
    for i in range(iters):
        r = np.random.random()
        acum = 0.0
        idx = 0
        for j in range(N):
            acum += prob[j]
            if r <= acum:
                idx = j
                break
                
        a = transform_matrix[idx, 0]
        b = transform_matrix[idx, 1]
        c = transform_matrix[idx, 2]
        d = transform_matrix[idx, 3]
        e = transform_matrix[idx, 4]
        f = transform_matrix[idx, 5]
        
        nx = a*x + b*y + e
        ny = c*x + d*y + f
        x, y = nx, ny
        
        px = int(x * cx + w/2)
        py = int(y * cy + h/2)
        
        if 0 <= px < w and 0 <= py < h:
            grid[py, px] += 1.0