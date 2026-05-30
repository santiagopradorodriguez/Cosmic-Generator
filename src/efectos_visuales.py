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
        if intensity <= 0: return img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        bright = cv2.bitwise_and(img, img, mask=mask)
        blur = cv2.GaussianBlur(bright, (0, 0), sigmaX=15, sigmaY=15)
        return cv2.addWeighted(img, 1.0, blur, intensity, 0)

    def aberracion_cromatica(self, img, strength):
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

    def shift_hue(self, img, shift_amount):
        """Rota los colores de la imagen (Ciclo HSV)."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Convertir a int16 para evitar overflow (ej: 179 + 100 = 279, que rompe uint8)
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
