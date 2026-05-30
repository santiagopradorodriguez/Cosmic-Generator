import cv2

import numpy as np

import random

from numba import jit



class CamaraVirtual:

    def __init__(self, width, height):

        self.w = width

        self.h = height

        self.center = (width // 2, height // 2)

       

        # Estado físico (Mecánica Lagrangiana simplificada... ponele)

        self.zoom = 1.0

        self.angle = 0.0

        self.shake_x = 0

        self.shake_y = 0

        self.drift_x = 0

        self.drift_y = 0



    def update(self, energy, kick, snare):

        # Drift suave (movimiento de cámara en mano)

        self.drift_x += (random.random() - 0.5) * 2

        self.drift_y += (random.random() - 0.5) * 2

       

        # Zoom reactivo: Respira con la energía, golpea con el Kick

        target_zoom = 1.0 + (energy * 0.1) + (kick * 0.15)

        self.zoom += (target_zoom - self.zoom) * 0.1 # Suavizado (Lerp)



        # Rotación: Gira con el snare o hi-hats

        self.angle += 0.05 + (snare * 0.5)

       

        # Shake: Terremoto con graves fuertes

        if kick > 0.7:

            self.shake_x = random.randint(-20, 20) * kick

            self.shake_y = random.randint(-20, 20) * kick

        else:

            # Amortiguación (Damping)

            self.shake_x *= 0.8

            self.shake_y *= 0.8



    def aplicar(self, frame):

        # Matriz de rotación y escala

        M = cv2.getRotationMatrix2D(self.center, self.angle, self.zoom)

       

        # Añadir traslación (Drift + Shake)

        M[0, 2] += self.shake_x + self.drift_x

        M[1, 2] += self.shake_y + self.drift_y

       

        # Warp con bordes espejados (Efecto caleidoscopio infinito en los bordes)

        return cv2.warpAffine(frame, M, (self.w, self.h), borderMode=cv2.BORDER_REFLECT_101)



class PostFX:

    def __init__(self):

        self.buffer_anterior = None



    def feedback_temporal(self, frame, decay=0.80):

        """

        Crea estelas de luz mezclando el frame anterior.

        Da una sensación de fluidez y 'sueño'.

        """

        if self.buffer_anterior is None:

            self.buffer_anterior = frame.astype(float)

            return frame

       

        # Mezcla ponderada: Frame Actual + (Frame Anterior * Decay)

        # cv2.addWeighted es rápido, pero hacerlo en float evita banding

        frame_float = frame.astype(float)

        self.buffer_anterior = cv2.addWeighted(frame_float, 1.0, self.buffer_anterior, decay, 0)

       

        return np.clip(self.buffer_anterior, 0, 255).astype(np.uint8)



    @staticmethod

    def aberracion_cromatica(frame, intensidad=0.0):

        if intensidad < 1: return frame

        shift = int(intensidad)

       

        # Separar canales

        b, g, r = cv2.split(frame)

        rows, cols = frame.shape[:2]

       

        # Matrices de traslación

        M_r = np.float32([[1, 0, shift], [0, 1, 0]])   # Rojo a la derecha

        M_b = np.float32([[1, 0, -shift], [0, 1, 0]])  # Azul a la izquierda

       

        r_shifted = cv2.warpAffine(r, M_r, (cols, rows))

        b_shifted = cv2.warpAffine(b, M_b, (cols, rows))

       

        return cv2.merge((b_shifted, g, r_shifted))



    @staticmethod

    def bloom(frame, threshold=200, intensidad=1.5):

        """

        Brillo etéreo. Solo afecta a los píxeles más brillantes que el threshold.

        """

        # 1. Extraer partes brillantes

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

       

        bright_parts = cv2.bitwise_and(frame, frame, mask=mask)

       

        # 2. Desenfocar mucho (Gaussian Blur costoso, usar con cuidado o bajar resolución)

        blur = cv2.GaussianBlur(bright_parts, (21, 21), 0)

       

        # 3. Sumar

        return cv2.addWeighted(frame, 1.0, blur, intensidad, 0)



    @staticmethod

    def ruido_grain(frame, cantidad=0.0):

        if cantidad <= 0: return frame

        h, w, c = frame.shape

        # Generar ruido gaussiano

        noise = np.random.normal(0, cantidad * 50, (h, w, c)).astype(np.int16)

        frame_16 = frame.astype(np.int16)

        frame_final = np.clip(frame_16 + noise, 0, 255).astype(np.uint8)

        return frame_final