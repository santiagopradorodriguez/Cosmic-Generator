# (C) Rebeldía Cósmica | Creado por Santiago Prado
import numpy as np
import cv2

class AlienGenerator:
    """
    Motor Matemático Procedimental basado en Pareidolia y Domain Warping.
    Diseñado para generar rostros y texturas alienígenas/biomecánicas a 60fps
    sin depender de redes neuronales (Deep Learning).
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.t = 0.0
        
        # Generar mapas de coordenadas estáticos
        self.xx, self.yy = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        
        # Buffer de reacción-difusión simplificado (Opcional para texturas vivas)
        self.rd_u = np.ones((h, w), dtype=np.float32)
        self.rd_v = np.zeros((h, w), dtype=np.float32)
        
        # Sembrar el centro para la reacción-difusión
        cy, cx = h//2, w//2
        r = 20
        self.rd_v[cy-r:cy+r, cx-r:cx+r] = np.random.uniform(0.5, 1.0, (2*r, 2*r))
        
    def _generar_ruido_fbm(self, scale, t_offset):
        """Genera una textura de ruido suave combinando resoluciones (Value Noise FBM)."""
        ruido = np.zeros((self.h, self.w), dtype=np.float32)
        amplitud = 0.5
        frecuencia = scale
        
        for _ in range(4): # 4 Octavas
            # Matriz de ruido pequeña
            w_small = max(1, int(self.w / frecuencia))
            h_small = max(1, int(self.h / frecuencia))
            small_noise = np.random.rand(h_small, w_small).astype(np.float32)
            
            # Animar el ruido desplazándolo ligeramente
            if t_offset > 0:
                shift_x = int(t_offset * frecuencia * 0.1) % w_small
                small_noise = np.roll(small_noise, shift_x, axis=1)
                
            # Escalar a tamaño completo con interpolación cúbica (crea suavidad orgánica)
            ruido_upscaled = cv2.resize(small_noise, (self.w, self.h), interpolation=cv2.INTER_CUBIC)
            
            ruido += ruido_upscaled * amplitud
            amplitud *= 0.5
            frecuencia *= 2.0
            
        return ruido
        
    def _esculpir_con_sdf(self, textura, boca_abierta):
        """
        Aplica Funciones de Distancia Firmada (SDF) para dar forma de cráneo/cabeza.
        """
        # Distancia al centro (Cráneo base)
        dist_centro = np.sqrt(self.xx**2 + self.yy**2)
        mascara_craneo = 1.0 - np.clip(dist_centro * 1.5, 0, 1)
        
        # Cavidades (Ojos)
        ojo_dist = np.sqrt((self.xx - 0.3)**2 + (self.yy + 0.2)**2)
        mascara_ojo = np.clip(ojo_dist * 4.0, 0, 1)
        
        # Cavidad (Boca) controlada por la música
        apertura = 0.1 + boca_abierta * 0.4
        boca_dist = np.sqrt(self.xx**2 + ((self.yy - 0.5) / apertura)**2)
        mascara_boca = np.clip(boca_dist * 3.0, 0, 1)
        
        # Multiplicar la textura orgánica por el cráneo y restar las cavidades
        forma = textura * mascara_craneo * mascara_ojo * mascara_boca
        return forma
        
    def _color_coseno(self, t, a, b, c, d):
        """Paleta generativa basada en Inigo Quilez cosine gradients."""
        t = t[..., np.newaxis] # Expandir dims para broadcasting RGB
        color = a + b * np.cos(6.28318 * (c * t + d))
        return color

    def procesar(self, energy, kick, snare):
        self.t += 0.05 + energy * 0.05
        
        # 1. Tejido Base (FBM Noise)
        # Re-generamos la base cada ciertos frames o la animamos suavemente
        np.random.seed(int(self.t)) # Pseudo-animación controlada por el tiempo
        tejido = self._generar_ruido_fbm(scale=32, t_offset=self.t)
        
        # 2. Domain Warping (Deformación)
        # Usamos el tejido para desplazar las coordenadas de otro ruido
        warp_y = cv2.Sobel(tejido, cv2.CV_32F, 0, 1, ksize=3) * 50.0
        warp_x = cv2.Sobel(tejido, cv2.CV_32F, 1, 0, ksize=3) * 50.0
        
        map_x = (np.arange(self.w) + warp_x).astype(np.float32)
        map_y = (np.arange(self.h).reshape(-1, 1) + warp_y).astype(np.float32)
        
        # Generar un segundo ruido suave
        np.random.seed(int(self.t * 0.5))
        tejido_secundario = self._generar_ruido_fbm(scale=16, t_offset=0)
        
        # Deformar el segundo ruido usando el primero
        tejido_warp = cv2.remap(tejido_secundario, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        # 3. Cráneo SDF
        forma_craneo = self._esculpir_con_sdf(tejido_warp, boca_abierta=kick)
        
        # 4. El Espejo Mágico (Simetría Bilateral de Pareidolia)
        # Cortamos la mitad y la reflejamos
        mitad = self.w // 2
        forma_craneo[:, mitad:] = cv2.flip(forma_craneo[:, :mitad], 1)
        
        # 5. Colorear (Giger / Psicodélico)
        if energy > 0.6:
            # Paleta DMT/Neon (Cyan, Magenta, Amarillo)
            A = np.array([0.5, 0.5, 0.5])
            B = np.array([0.5, 0.5, 0.5])
            C = np.array([1.0, 1.0, 1.0])
            D = np.array([0.00, 0.33, 0.67])
        else:
            # Paleta Biomecánica (H.R. Giger - Grises, Óxido, Verdes oscuros)
            A = np.array([0.3, 0.3, 0.3])
            B = np.array([0.2, 0.2, 0.2])
            C = np.array([1.0, 1.0, 0.5])
            D = np.array([0.0, 0.1, 0.2])
            
        color_img = self._color_coseno(forma_craneo, A, B, C, D)
        
        # 6. Iluminación 3D (Normal Mapping Falso)
        # Convertimos la intensidad en relieve
        forma_craneo_32f = forma_craneo.astype(np.float32)
        sobel_x = cv2.Sobel(forma_craneo_32f, cv2.CV_32F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(forma_craneo_32f, cv2.CV_32F, 0, 1, ksize=3)
        luz_dir = np.array([0.5, 0.5, 1.0]) # Luz viene de arriba a la derecha
        luz_dir = luz_dir / np.linalg.norm(luz_dir)
        
        normales = np.stack([-sobel_x, -sobel_y, np.ones_like(sobel_x)], axis=-1)
        normales_norm = np.linalg.norm(normales, axis=-1, keepdims=True) + 1e-5
        normales /= normales_norm
        
        # Producto punto para Diffuse Lighting
        iluminacion = np.maximum(0, np.sum(normales * luz_dir, axis=-1))
        iluminacion = iluminacion[..., np.newaxis]
        
        # Brillo especular
        view_dir = np.array([0, 0, 1])
        half_vector = luz_dir + view_dir
        half_vector = half_vector / np.linalg.norm(half_vector)
        specular = np.maximum(0, np.sum(normales * half_vector, axis=-1)) ** 16.0
        specular = specular[..., np.newaxis]
        
        # Combinar color + iluminación + especular
        final_img = (color_img * iluminacion + specular * 0.5) * 255.0
        
        # Destello de los ojos en el drop
        ojo_dist = np.sqrt((self.xx - 0.3)**2 + (self.yy + 0.2)**2)
        mascara_ojo = np.clip(ojo_dist * 4.0, 0, 1)
        mascara_ojo[:, mitad:] = cv2.flip(mascara_ojo[:, :mitad], 1)
        
        if kick > 0.8:
            final_img += (1.0 - mascara_ojo)[..., np.newaxis] * 255.0 * np.array([0.0, 0.8, 1.0]) # Ojos azules brillantes
            
        final_img = np.clip(final_img, 0, 255).astype(np.uint8)
        
        # Formato BGR de OpenCV
        return cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
