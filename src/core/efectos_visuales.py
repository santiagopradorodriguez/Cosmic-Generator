"""
(C) Rebeldía Cósmica | Creado por Santiago Prado
"""
import cv2
import numpy as np
import random

class CamaraVirtual:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.center = (width // 2, height // 2)
       
        # Estado físico
        self.zoom = 1.0
        self.angle = 0.0
        self.shake_x = 0
        self.shake_y = 0
        self.drift_x = 0
        self.drift_y = 0

    def update(self, energy, kick, snare):
        self.drift_x += (random.random() - 0.5) * 2
        self.drift_y += (random.random() - 0.5) * 2
        target_zoom = 1.0 + (energy * 0.1) + (kick * 0.15)
        self.zoom += (target_zoom - self.zoom) * 0.1
        self.angle += 0.05 + (snare * 0.5)
        if kick > 0.7:
            self.shake_x = random.randint(-20, 20) * kick
            self.shake_y = random.randint(-20, 20) * kick
        else:
            self.shake_x *= 0.8
            self.shake_y *= 0.8

    def aplicar(self, frame):
        M = cv2.getRotationMatrix2D(self.center, self.angle, self.zoom)
        M[0, 2] += self.shake_x + self.drift_x
        M[1, 2] += self.shake_y + self.drift_y
        return cv2.warpAffine(frame, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT_101)

class MotorFX:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # Buffer inicializado explícitamente como float32
        self.prev_frame = np.zeros((h, w, 3), dtype=np.float32)
        
    def aplicar_bloom(self, img, intensity, threshold=200):
        """
        Aplica un efecto de resplandor (Bloom / Neon Glow) multi-capa a las áreas brillantes de la imagen.

        Este método aísla los píxeles que superan un umbral de luminosidad y genera un halo difuso
        alrededor de ellos mediante una técnica piramidal (downsampling iterativo). Esto permite
        crear un resplandor masivo de forma matemáticamente eficiente sin comprometer la tasa de fotogramas (FPS).

        Parámetros:
        -----------
        img : numpy.ndarray
            La imagen (fotograma) de entrada en formato BGR (tipo uint8) proveniente de OpenCV.
        intensity : float
            Factor de multiplicación para la capa de resplandor final al mezclarla aditivamente
            con la imagen original. Valores más altos (ej. 1.5, 2.0) saturan la luz intensamente.
            Si intensity <= 0, se devuelve la imagen original sin procesar.
        threshold : int, opcional
            Umbral de luminosidad (0 a 255).
        """
        if intensity <= 0: return img
        
        # 1. Extraer altas luces
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        bright = cv2.bitwise_and(img, img, mask=mask)
        
        # 2. Multi-Layer Glow (Pirámide de baja resolución)
        h, w = bright.shape[:2]
        
        w1, h1 = max(w // 2, 1), max(h // 2, 1)
        l1 = cv2.resize(bright, (w1, h1), interpolation=cv2.INTER_LINEAR)
        b1 = cv2.GaussianBlur(l1, (5, 5), 0)
        
        w2, h2 = max(w1 // 2, 1), max(h1 // 2, 1)
        l2 = cv2.resize(b1, (w2, h2), interpolation=cv2.INTER_LINEAR)
        b2 = cv2.GaussianBlur(l2, (11, 11), 0)
        
        w3, h3 = max(w2 // 2, 1), max(h2 // 2, 1)
        l3 = cv2.resize(b2, (w3, h3), interpolation=cv2.INTER_LINEAR)
        b3 = cv2.GaussianBlur(l3, (21, 21), 0)
        # 3. Sumar capas y recomponer (Upsampling de vuelta)
        up3 = cv2.resize(b3, (w2, h2), interpolation=cv2.INTER_LINEAR)
        mix2 = cv2.add(b2, up3)
        
        up2 = cv2.resize(mix2, (w1, h1), interpolation=cv2.INTER_LINEAR)
        mix1 = cv2.add(b1, up2)
        
        final_glow = cv2.resize(mix1, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # 4. Mezcla aditiva con el frame original
        return cv2.addWeighted(img, 1.0, final_glow, intensity, 0)

    def melting_world_fisheye(self, frame, kick_intensity):
        """
        Fase 12: Shader 'Melting World'. Distorsiona el cuadro simulando
        un lente ojo de pez que se infla y desinfla con los subgraves (kick).
        """
        if kick_intensity < 0.1:
            return frame
            
        h, w = frame.shape[:2]
        
        # Parámetros de distorsión
        # k1 negativo = fisheye barrel distortion (se abomba hacia afuera)
        k1 = -0.5 * kick_intensity
        
        # Matriz intrínseca de cámara falsa
        f = min(w, h)
        cx, cy = w / 2, h / 2
        K = np.array([
            [f, 0, cx],
            [0, f, cy],
            [0, 0,  1]
        ], dtype=np.float32)
        
        D = np.array([k1, 0.0, 0.0, 0.0], dtype=np.float32)
        
        # Calcular mapa de distorsión
        map1, map2 = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_32FC1)
        
        # Aplicar deformación con interpolación lineal
        frame_distorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return frame_distorted
        
    def mandelbrot_overlay(self, frame, time_sec, intensity):
        """
        Fase 12: Inyecta un patrón fractal de interferencia usando
        una simplificación matemática rápida compatible con OpenCV.
        (Efecto de ruido estático geométrico).
        """
        if intensity < 0.2:
            return frame
            
        h, w = frame.shape[:2]
        # Generar ruido fractal básico
        noise = np.zeros((h, w), dtype=np.uint8)
        cv2.randn(noise, 128, 50)
        
        # Suavizado para simular las manchas fractales gruesas
        noise = cv2.GaussianBlur(noise, (15, 15), 0)
        
        # Umbralizar basado en el tiempo para crear patrones pulsantes
        threshold_val = 128 + int(np.sin(time_sec * 5.0) * 50)
        _, fractal_mask = cv2.threshold(noise, threshold_val, 255, cv2.THRESH_BINARY)
        
        # Colorear la máscara de un púrpura/magenta tóxico
        fractal_layer = np.zeros_like(frame)
        fractal_layer[fractal_mask == 255] = [200, 50, 200]
        
        # Mezclar con la imagen original
        alpha = intensity * 0.4
        return cv2.addWeighted(frame, 1.0 - alpha, fractal_layer, alpha, 0)

    def aberracion_cromatica(self, img, strength):
        """
        Aplica un desplazamiento de los canales de color (Aberración Cromática) simulando imperfecciones ópticas o fallos VHS.

        Separa los canales B (Azul), G (Verde) y R (Rojo) de la imagen, manteniendo el Verde intacto
        como ancla espacial. El canal Rojo se traslada horizontalmente hacia la derecha, y el Azul 
        se traslada hacia la izquierda mediante transformaciones afines.

        Parámetros:
        -----------
        img : numpy.ndarray
            La imagen (fotograma) de entrada en formato BGR (tipo uint8).
        strength : float o int
            Magnitud del desplazamiento horizontal en píxeles. Representa la distancia que se separarán
            los canales cromáticos. A mayor valor, mayor es el efecto "Glitch" o defecto de lente.
            Si strength <= 0, se devuelve la imagen original sin procesar.

        Retorna:
        --------
        numpy.ndarray
            La imagen procesada tras recombinar los canales desplazados (R y B) con el canal G original.
        """
        if strength <= 0: return img
        b, g, r = cv2.split(img)
        rows, cols = img.shape[:2]
        M = np.float32([[1, 0, strength], [0, 1, 0]])
        r_shift = cv2.warpAffine(r, M, (cols, rows))
        M = np.float32([[1, 0, -strength], [0, 1, 0]])
        b_shift = cv2.warpAffine(b, M, (cols, rows))
        return cv2.merge((b_shift, g, r_shift))

    def feedback_temporal(self, current_frame, decay=0.92):
        # Convertimos el frame actual a float32 para coincidir con self.prev_frame
        curr_32 = current_frame.astype(np.float32)
        self.prev_frame = cv2.addWeighted(curr_32, 1.0, self.prev_frame, decay, 0)
        return np.clip(self.prev_frame, 0, 255).astype(np.uint8)

    def feedback_zoom(self, current_frame, decay=0.92, zoom=1.01):
        """
        Crea un efecto de túnel psicodélico escalando el frame anterior.
        """
        h, w = self.h, self.w
        curr_32 = current_frame.astype(np.float32)
        
        # Escalar el buffer anterior (Zoom)
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, 0, zoom)
        prev_zoomed = cv2.warpAffine(self.prev_frame, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
        
        # Mezclar: Frame Actual + (Frame Anterior con Zoom * Decay)
        self.prev_frame = cv2.addWeighted(curr_32, 1.0, prev_zoomed, decay, 0)
        return np.clip(self.prev_frame, 0, 255).astype(np.uint8)

    def apply_god_rays(self, img, intensity, threshold=200):
        """
        Genera rayos volumétricos (Radial Blur Aditivo) desde el centro.
        Reactivo a la energía de la música.
        """
        if intensity <= 0.05: return img
        # Extraer luces altas
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        bright = cv2.bitwise_and(img, img, mask=mask)
        
        h, w = bright.shape[:2]
        center = (w // 2, h // 2)
        
        rays = np.zeros_like(img, dtype=np.float32)
        bright_float = bright.astype(np.float32)
        
        # Radial blur iterativo
        decay = 0.90
        weight = 1.0
        
        # 10 iteraciones de zoom in aditivo
        for i in range(1, 11):
            scale = 1.0 + (i * 0.015 * intensity)
            M = cv2.getRotationMatrix2D(center, 0, scale)
            warped = cv2.warpAffine(bright_float, M, (w, h))
            rays += warped * weight
            weight *= decay
            
        rays = np.clip(rays, 0, 255).astype(np.uint8)
        return cv2.addWeighted(img, 1.0, rays, 0.6 * intensity, 0)

    def plasma_melt_feedback(self, current_frame, decay=0.90, kick=0.0):
        """
        Mezcla el cuadro actual con el historial, desplazando el historial
        hacia arriba y difuminándolo para crear estelas de plasma derritiéndose.
        """
        h, w = current_frame.shape[:2]
        curr_32 = current_frame.astype(np.float32)
        
        # Efecto de derretimiento (drift hacia arriba y leve zoom)
        scale = 1.002 + (kick * 0.003)
        dy = -1.0 - (kick * 3.0)
        M = cv2.getRotationMatrix2D((w//2, h//2), 0, scale)
        M[1, 2] += dy
        
        prev_warped = cv2.warpAffine(self.prev_frame, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
        
        # Blur ligero para que la estela de plasma se disipe orgánicamente
        prev_warped = cv2.GaussianBlur(prev_warped, (3, 3), 0)
        
        # Screen / Additive blend
        self.prev_frame = cv2.addWeighted(curr_32, 1.0, prev_warped, decay, 0)
        return np.clip(self.prev_frame, 0, 255).astype(np.uint8)

    def shift_hue(self, img, shift_amount):
        """Rota los colores de la imagen (Ciclo HSV)."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Convertir a int16 para evitar overflow
        h_channel = hsv[:, :, 0].astype(np.int16)
        h_channel = (h_channel + shift_amount) % 180
        hsv[:, :, 0] = h_channel.astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    def kaleidoscopio(self, img, active=True):
        """
        Convierte la imagen en un mandala psicodélico usando espejos (4-way symmetry).
        """
        if not active: return img
        
        h, w = img.shape[:2]
        # Asegurar dimensiones pares para evitar errores de concatenación
        h, w = h - (h % 2), w - (w % 2)
        img = img[:h, :w]
        
        cx, cy = w // 2, h // 2
        
        # 1. Tomamos el cuadrante superior izquierdo como semilla
        seed = img[:cy, :cx]
        
        # 2. Espejar Horizontalmente
        top = np.hstack((seed, cv2.flip(seed, 1)))
        
        # 3. Espejar Verticalmente
        full = np.vstack((top, cv2.flip(top, 0)))
        
        return full

    def aplicar_caleidoscopio(self, img, slices=6, intensity=1.0):
        """
        Wrapper de compatibilidad para legacy.
        Usa la implementación de espejos (kaleidoscopio) con blending.
        """
        if intensity <= 0.01:
            return img
            
        # Generar efecto mandala (usando la implementación optimizada de 4 espejos)
        k_img = self.kaleidoscopio(img, active=True)
        
        # Mezclar con original según intensidad
        if intensity >= 1.0:
            return k_img
        else:
            return cv2.addWeighted(img, 1.0 - intensity, k_img, intensity, 0)
