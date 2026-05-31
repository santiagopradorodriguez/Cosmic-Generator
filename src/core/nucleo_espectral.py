# (C) Rebeldía Cósmica | Creado por Santiago Prado
# nucleo_espectral.py - Métodos Pseudo-Espectrales para EDPS (Cero Estabilidad Numérica / Zero CFL Stiffness)
import numpy as np

class NucleoEspectral:
    def __init__(self, w, h, dx=1.0, dy=1.0):
        self.w = w
        self.h = h
        self.dx = dx
        self.dy = dy
        
        # Frecuencias espaciales (kx, ky)
        kx = np.fft.fftfreq(w) * 2.0 * np.pi / dx
        ky = np.fft.fftfreq(h) * 2.0 * np.pi / dy
        
        self.KX, self.KY = np.meshgrid(kx, ky)
        self.K_sq = self.KX**2 + self.KY**2
        self.K_quad = self.K_sq**2
        
        # Máscara Anti-Aliasing (Regla de los 2/3 de Orszag)
        k_max_x = np.pi / dx
        k_max_y = np.pi / dy
        # Máscara esférica suave para evitar artefactos de ringing (suavizado espectral)
        self.mask_dealias = np.exp(-((self.K_sq) / (0.8 * (k_max_x**2 + k_max_y**2)))**6)
        
        # Operador Lineal de Kuramoto-Sivashinsky: L = k^2 - k^4
        # Escalar el operador para controlar el tamaño de las células
        self.scale_ks = 0.5
        self.L_KS = (self.K_sq * self.scale_ks) - (self.K_quad * self.scale_ks**2)
        
        # Cachés
        self.dt_cache_ks = -1.0
        self.exp_L_KS_dt = None
        self.NL_KS = None
        self.hyper_visc = None
        
        # Cachés GPE
        self.dt_cache_gpe = -1.0
        self.propagador_k = None
        
    def simulacion_ks_espectral(self, u_hat, dt, kick_intensity=0.0):
        """
        Integrador Pseudo-Espectral para Kuramoto-Sivashinsky (ETD1 Scheme)
        u_t = -(nabla^2 + nabla^4)u - 0.5 |nabla u|^2
        """
        # Actualizar integrador exponencial si el paso de tiempo cambia
        if abs(self.dt_cache_ks - dt) > 1e-6:
            self.dt_cache_ks = dt
            self.exp_L_KS_dt = np.exp(self.L_KS * dt)
            
            # Operador inverso para ETD1: (exp(L dt) - 1) / L
            with np.errstate(divide='ignore', invalid='ignore'):
                self.NL_KS = (self.exp_L_KS_dt - 1.0) / self.L_KS
            # Limite lim_{L->0} (exp(L dt) - 1)/L = dt
            self.NL_KS[self.L_KS == 0] = dt
            
            # Filtro Hiper-Viscoso para matar inestabilidades salvajes a altas frecuencias
            # exp(-nu * k^6 * dt)
            nu = 1e-4
            self.hyper_visc = np.exp(-nu * (self.K_sq**3) * dt)

        # 1. Gradientes en espacio de Fourier (Exactos)
        u_x_hat = 1j * self.KX * u_hat
        u_y_hat = 1j * self.KY * u_hat
        
        # 2. Espacio Real para evaluar |nabla u|^2
        u_x = np.real(np.fft.ifft2(u_x_hat))
        u_y = np.real(np.fft.ifft2(u_y_hat))
        
        # Optimización In-Place para reducir memory leaks de arrays temporales
        u_x **= 2
        u_y **= 2
        u_x += u_y
        u_x *= 0.5
        nonlin_real = u_x
        
        # Inyectar caos musical impulsivo (Kicks)
        if kick_intensity > 0.5:
            # Añadir ruido aleatorio local que altere la no linealidad
            ruido = (np.random.rand(self.h, self.w) - 0.5) * kick_intensity * 10.0
            nonlin_real += ruido
            
        # 3. Volver a Fourier
        nonlin_hat = np.fft.fft2(nonlin_real) * self.mask_dealias
        
        # 4. Integración Exacta ETD1
        u_hat *= self.exp_L_KS_dt
        u_hat -= nonlin_hat * self.NL_KS
        
        # Aplicar estabilización adicional hiperviscosa
        u_hat *= self.hyper_visc
        
        return u_hat
        
    def simulacion_gpe_espectral(self, psi, V, g, dt):
        """
        Integrador Split-Step Fourier Method (SSFM) para Gross-Pitaevskii.
        psi_t = (i/2) nabla^2 psi - i V psi - i g |psi|^2 psi
        Estabilidad incondicional y conservación unitaria cuasi-perfecta.
        """
        # Actualizar propagador si el paso de tiempo cambia
        if abs(self.dt_cache_gpe - dt) > 1e-6:
            self.dt_cache_gpe = dt
            self.propagador_k = np.exp(-0.5j * self.K_sq * dt)

        # --- PASO 1: Potencial y No linealidad en el Espacio Real (Medio dt) ---
        densidad = np.abs(psi)**2
        fase_nl = np.exp(-1j * (V + g * densidad) * (dt / 2.0))
        psi_half = psi * fase_nl
        
        # --- PASO 2: Término Cinético en Espacio de Fourier (dt completo) ---
        psi_hat = np.fft.fft2(psi_half)
        # Operador evolutivo cinético exacto exp(-i/2 * k^2 * dt) cacheado
        psi_hat *= self.propagador_k
        psi_half_2 = np.fft.ifft2(psi_hat)
        
        # --- PASO 3: Potencial y No linealidad en el Espacio Real (Medio dt) ---
        densidad2 = np.abs(psi_half_2)**2
        fase_nl2 = np.exp(-1j * (V + g * densidad2) * (dt / 2.0))
        psi_next = psi_half_2 * fase_nl2
        
        # Renormalización Conservativa (Garantizar |psi|^2 = 1.0)
        norma = np.sum(np.abs(psi_next)**2)
        if norma > 1e-10:
            psi_next /= np.sqrt(norma)
            
        return psi_next
