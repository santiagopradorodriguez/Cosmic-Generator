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
        self.t = 0.0
        self.base_zoom = 1.0
        
        # Máquina de estados cinemática
        self.mode = 0
        self.mode_timer = 0.0
        self.target_angle = 0.0
        
        # Matriz para lente psicodélico
        f = min(width, height)
        cx, cy = width / 2, height / 2
        self.K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float32)

    def randomize_mode(self, is_chorus=False):
        import random
        if is_chorus:
            # En el estribillo forzamos modos frenéticos o de zoom (Modo 1 o 3)
            self.mode = random.choice([1, 3])
        else:
            # Versos: Cualquier plano aleatorio
            self.mode = random.choice([0, 1, 2, 3])
            
        # Pequeño salto aleatorio de ángulo al cambiar de plano
        self.angle += random.uniform(-10.0, 10.0)

    def update(self, energy, kick, snare, bass=0.0):
        self.t += 0.033 # asume ~30fps
        
        # Pumping del Sub-Bajo (Añade una elasticidad al zoom base)
        pumping_elasticity = bass * 0.45
            
        # MODO 0: Clásico (Paneo y respiración suave)
        if self.mode == 0:
            self.drift_x = np.sin(self.t * 0.5) * 30.0 + np.sin(self.t * 0.1) * 20.0
            self.drift_y = np.cos(self.t * 0.4) * 30.0 + np.sin(self.t * 0.2) * 20.0
            self.base_zoom = 1.05 + np.sin(self.t * 0.2) * 0.05
            target_zoom = self.base_zoom + (energy * 0.1) + (kick * 0.2) + pumping_elasticity
            self.zoom += (target_zoom - self.zoom) * 0.15
            self.target_angle = np.sin(self.t * 0.15) * 5.0 + (snare * 2.0)
            self.angle += (self.target_angle - self.angle) * 0.1

        # MODO 1: Vértigo Rítmico (Objetivo Cinético)
        elif self.mode == 1:
            self.drift_x = np.sin(self.t) * 10.0
            self.drift_y = np.cos(self.t) * 10.0
            target_zoom = 1.25 + (kick * 0.4) + pumping_elasticity
            self.zoom += (target_zoom - self.zoom) * 0.1
            
            # Snap & Smooth en los ángulos
            umbral_kick = 0.7
            umbral_snare = 0.7
            
            if kick > umbral_kick:
                self.target_angle += 45.0  # Salto de 45 grados a la derecha
            elif snare > umbral_snare:
                self.target_angle -= 90.0  # Salto de 90 grados a la izquierda
                
            friccion = 0.15 + (energy * 0.15)
            self.angle += (self.target_angle - self.angle) * friccion

        # MODO 2: Alejamiento (Caleidoscopio de espejos)
        elif self.mode == 2:
            self.drift_x = np.sin(self.t * 0.2) * 80.0
            self.drift_y = np.cos(self.t * 0.3) * 80.0
            target_zoom = 0.5 - (kick * 0.15) # Zoom Out extremo
            self.zoom += (target_zoom - self.zoom) * 0.05
            self.target_angle = np.sin(self.t * 0.1) * 20.0
            self.angle += (self.target_angle - self.angle) * 0.05
            
        # MODO 3: Curvatura Extrema Psicodélica (Derretimiento)
        elif self.mode == 3:
            self.drift_x = np.sin(self.t * 2.0) * 15.0 * kick
            self.drift_y = np.cos(self.t * 2.0) * 15.0 * kick
            target_zoom = 1.1 + (kick * 0.6)
            self.zoom += (target_zoom - self.zoom) * 0.2
            self.angle *= 0.9 # Retornar suavemente al centro
        
        # Shake violento universal
        if kick > 0.6:
            self.shake_x = random.uniform(-40, 40) * kick
            self.shake_y = random.uniform(-40, 40) * kick
        else:
            self.shake_x *= 0.7
            self.shake_y *= 0.7

    def aplicar(self, frame):
        # 1. Distorsión Ojo de pez (Solo en Modo 3)
        if self.mode == 3:
            k1 = -0.3 - (self.zoom * 0.3) # Deformación ligada a la intensidad
            D = np.array([k1, 0.0, 0.0, 0.0], dtype=np.float32)
            map1, map2 = cv2.initUndistortRectifyMap(self.K, D, None, self.K, (self.w, self.h), cv2.CV_32FC1)
            frame = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
            
        # 2. Transformación Afín 2D (Rotación, Escala, Traslación)
        M = cv2.getRotationMatrix2D(self.center, self.angle, self.zoom)
        M[0, 2] += self.shake_x + self.drift_x
        M[1, 2] += self.shake_y + self.drift_y
        
        # INTER_CUBIC previene la borrosidad extrema al hacer zoom in digital
        return cv2.warpAffine(frame, M, (self.w, self.h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)

class MotorFX:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # Buffer inicializado explícitamente como float32
        self.prev_frame = np.zeros((h, w, 3), dtype=np.float32)
        # Buffer circular para Time-Slice Glitch
        self.frame_buffer = []
        
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
        
        # 4. Mezcla aditiva con el frame original (Intensidad suavizada para evitar quemado radiactivo)
        safe_intensity = intensity * 0.4 # Reducción drástica del bloom
        return cv2.addWeighted(img, 1.0, final_glow, safe_intensity, 0)

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
        # Convertimos el frame actual a float32 para acumulación HDR real
        curr_32 = current_frame.astype(np.float32)
        # Combinar ambos trucos: np.maximum evita suma explosiva, Tone Mapping da el toque cinemático
        blend = np.maximum(curr_32, self.prev_frame * decay)
        self.prev_frame = blend # Conservar float32
        
        # --- LUMA TONE MAPPING HDR ---
        b, g, r = cv2.split(blend)
        L = 0.114 * b + 0.587 * g + 0.299 * r
        L_safe = np.maximum(L, 1e-5)
        L_mapped = L_safe / (L_safe + 255.0)
        ratio = (L_mapped * 260.0) / L_safe
        
        out_frame = cv2.merge((b * ratio, g * ratio, r * ratio))
        return np.clip(out_frame, 0, 255).astype(np.uint8)

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
        
        # Combinar ambos trucos: np.maximum limita la luz extra
        blend = np.maximum(curr_32, prev_zoomed * decay)
        self.prev_frame = blend
        
        # --- LUMA TONE MAPPING HDR ---
        b, g, r = cv2.split(blend)
        L = 0.114 * b + 0.587 * g + 0.299 * r
        L_safe = np.maximum(L, 1e-5)
        L_mapped = L_safe / (L_safe + 255.0)
        ratio = (L_mapped * 260.0) / L_safe
        
        out_frame = cv2.merge((b * ratio, g * ratio, r * ratio))
        return np.clip(out_frame, 0, 255).astype(np.uint8)

    def datamosh_biologico(self, current_frame, energy, kick):
        """
        Simula Pixel Sorting / Datamoshing usando el gradiente de luminancia
        como mapa de desplazamiento para 'derretir' los píxeles hacia abajo.
        """
        if energy < 0.1 and kick < 0.2:
            return current_frame
            
        h, w = current_frame.shape[:2]
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        # Calcular el gradiente Y de la luminancia (bordes horizontales)
        grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        
        # Crear mapas de coordenadas
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        
        # El desplazamiento ocurre donde el gradiente es fuerte (los bordes 'gotean')
        desplazamiento = np.abs(grad_y) * (0.005 + kick * 0.08)
        
        # Aplicamos un umbral para que solo las áreas más brillantes goteen
        _, mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        mask_f = (mask.astype(np.float32) / 255.0)
        
        # map_y = y - algo: toma pixeles de más arriba y los pone aquí (gravedad)
        map_y = map_y - (desplazamiento * mask_f)
        
        # Interpolación Nearest Neighbor da el look crudo y pixelado del Datamoshing
        moshed = cv2.remap(current_frame, map_x, map_y, interpolation=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
        
        return moshed

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
        
        # Acumulación pura HDR sin límite de 255. La luz puede llegar a infinitos teóricos.
        # El decay geométrico controla que el límite superior converja.
        blend = cv2.addWeighted(curr_32, 1.0, prev_warped, decay, 0)
        self.prev_frame = blend  # Conservamos float32 para el siguiente frame
        
        # --- LUMA TONE MAPPING HDR ---
        # 1. Extraer canales (Opencv usa BGR por defecto)
        b, g, r = cv2.split(blend)
        
        # 2. Calcular Luminancia (Luma = 0.299*R + 0.587*G + 0.114*B)
        L = 0.114 * b + 0.587 * g + 0.299 * r
        L_safe = np.maximum(L, 1e-5) # Prevenir división por cero
        
        # 3. Aplicar Reinhard HDR SOLO a la matriz Luma
        kappa = 255.0  # Punto de semi-saturación
        L_mapped = L_safe / (L_safe + kappa)
        
        # 4. Escalar los canales BGR originales por el ratio de compresión Luma
        # Esto preserva el 'True Neon Glow' (la saturación original) sin que converja a blanco
        ratio = (L_mapped * 260.0) / L_safe # Multiplicamos por 260 para mantener intensidad de brillo
        
        b_mapped = b * ratio
        g_mapped = g * ratio
        r_mapped = r * ratio
        
        # Reensamblar canales y clipear suavemente
        out_frame = cv2.merge((b_mapped, g_mapped, r_mapped))
        out_frame = np.clip(out_frame, 0, 255).astype(np.uint8)
        return out_frame

    def aplicar_vhs_noise(self, img, intensity=0.2):
        """Añade ruido analógico sutil para evitar la crudeza digital pura."""
        if intensity <= 0: return img
        # Ruido de baja frecuencia (escala reducida y muy difuminada)
        h, w = img.shape[:2]
        noise_w, noise_h = max(w // 4, 1), max(h // 4, 1)
        noise = np.random.randint(-15, 15, (noise_h, noise_w, 3), dtype=np.int16) * intensity
        noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
        noisy = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        return cv2.GaussianBlur(noisy, (5, 5), 0)

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

    def agujero_negro_remap(self, img, phase, trigger=False):
        """Efecto Gravitacional: Absorbe la imagen y la escupe como onda expansiva en el kick."""
        h, w = self.h, self.w
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        cx, cy = w / 2, h / 2
        
        dx = map_x - cx
        dy = map_y - cy
        r = np.sqrt(dx**2 + dy**2) + 1e-5
        
        if trigger:
            # Expulsión (Supernova)
            fuerza = -50.0 * np.exp(-r / 150.0)
        else:
            # Absorción lenta (Agujero Negro)
            fuerza = 20.0 * phase * np.exp(-r / 300.0)
            
        map_x_dist = map_x + (dx / r) * fuerza
        map_y_dist = map_y + (dy / r) * fuerza
        
        return cv2.remap(img, map_x_dist.astype(np.float32), map_y_dist.astype(np.float32), 
                         interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def time_slice_glitch(self, img, trigger):
        """Rebana la pantalla horizontalmente mostrando fotogramas del pasado."""
        self.frame_buffer.append(img.copy())
        if len(self.frame_buffer) > 15:
            self.frame_buffer.pop(0)
            
        if not trigger or len(self.frame_buffer) < 5:
            return img
            
        h, w = self.h, self.w
        sliced_img = np.zeros_like(img)
        franjas = 10
        alto_franja = h // franjas
        
        for i in range(franjas):
            y_start = i * alto_franja
            y_end = (i + 1) * alto_franja if i < franjas - 1 else h
            
            # Elegir un fotograma aleatorio del pasado
            frame_idx = np.random.randint(0, len(self.frame_buffer))
            sliced_img[y_start:y_end, :] = self.frame_buffer[frame_idx][y_start:y_end, :]
            
        return sliced_img

    def vision_infrarroja_neon(self, img, trigger):
        """Convierte la imagen a alambres brillantes Canny en los picos de intensidad."""
        if not trigger: return img
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(img_gray, 50, 150)
        
        neon = np.zeros_like(img)
        # Borde color rojo/naranja infrarrojo
        neon[edges == 255] = [50, 50, 255]
        
        # Aplicar el propio motor de bloom a estos bordes
        return self.aplicar_bloom(neon, intensity=2.0, threshold=10)

    def aberracion_cromatica_ritmica(self, img, kick_val, snare_val):
        """Separa el canal Rojo y Azul en función del kick y el snare."""
        if kick_val < 0.1 and snare_val < 0.1: return img
        
        b, g, r = cv2.split(img)
        rows, cols = self.h, self.w
        
        # El kick desplaza el rojo a la derecha
        shift_r = int(kick_val * 40.0)
        if shift_r > 0:
            M_r = np.float32([[1, 0, shift_r], [0, 1, 0]])
            r = cv2.warpAffine(r, M_r, (cols, rows))
            
        # El snare desplaza el azul a la izquierda
        shift_b = int(snare_val * 40.0)
        if shift_b > 0:
            M_b = np.float32([[1, 0, -shift_b], [0, 1, 0]])
            b = cv2.warpAffine(b, M_b, (cols, rows))
            
        return cv2.merge((b, g, r))
