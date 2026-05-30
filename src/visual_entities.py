import numpy as np
import matplotlib.pyplot as plt
import cv2

class EspirituProcedural:
    def __init__(self, ax, seed_val):
        self.rng = np.random.RandomState(seed_val)
        self.parts = []
        self.num_brazos = self.rng.randint(2, 6)
        self.scale_var = self.rng.uniform(0.8, 1.5)
        self.speed_var = self.rng.uniform(0.5, 2.0)
        
        for _ in range(4 + self.num_brazos):
            l, = ax.plot([], [], lw=2, alpha=0.0, color='white')
            self.parts.append(l)
            
    def update(self, x, y, scale, t, kick, harm, color_rgb):
        if scale <= 0:
            for p in self.parts: p.set_data([], [])
            return

        scale *= self.scale_var
        t *= self.speed_var
        wobble = np.sin(t * 3) * 0.05 * scale
        
        theta = np.linspace(0, 2*np.pi, 20)
        hx = x + (0.15 * scale * np.cos(theta)) + wobble
        hy = y + (1.6 * scale) + (0.2 * scale * np.sin(theta)) + np.cos(t*2)*0.05
        self.parts[0].set_data(hx, hy)
        self.parts[0].set_color(color_rgb)
        self.parts[0].set_alpha(0.3 + harm*0.5)
        
        ty = np.linspace(y, y + 1.4*scale, 15)
        tx = x + np.sin(ty * 8 + t*4) * 0.08 * scale
        self.parts[1].set_data(tx, ty)
        self.parts[1].set_color(color_rgb)
        self.parts[1].set_alpha(0.2 + harm*0.4)

        for i in range(self.num_brazos):
            angle_base = (i / self.num_brazos) * 2 * np.pi + t * 0.2
            limb_len = np.linspace(0, 1.2*scale, 15)
            lx = x + np.sin(limb_len*3 + t*2 + i)*0.1*scale + np.cos(angle_base) * limb_len
            ly = (y + 0.8*scale) + np.cos(limb_len*3 + t*2 + i)*0.1*scale + np.sin(angle_base) * limb_len * 0.5
            
            idx_part = 2 + i
            self.parts[idx_part].set_data(lx, ly)
            self.parts[idx_part].set_color(color_rgb)
            self.parts[idx_part].set_alpha(0.15 + harm*0.25)

        idx_aura = 2 + self.num_brazos
        if harm > 0.2:
            num_puntos = 12
            angulos = np.linspace(0, 2*np.pi, num_puntos) + t*5
            radios = scale * (1.5 + np.random.uniform(-0.5, 1.0, num_puntos) * (1+kick))
            ax_aura = x + radios * np.cos(angulos)
            ay_aura = y + 0.5*scale + radios * np.sin(angulos)
            
            self.parts[idx_aura].set_data(ax_aura, ay_aura)
            self.parts[idx_aura].set_color(color_rgb)
            self.parts[idx_aura].set_alpha(0.3 * harm)
            self.parts[idx_aura].set_linestyle(':')
        else:
            self.parts[idx_aura].set_data([], [])

        idx_ojos = idx_aura + 1
        ex = [x - 0.06*scale, x + 0.06*scale]
        ey = [y + 1.65*scale, y + 1.65*scale]
        self.parts[idx_ojos].set_data(ex, ey)
        self.parts[idx_ojos].set_color('white') 
        self.parts[idx_ojos].set_marker('o')
        self.parts[idx_ojos].set_markersize(2 + kick * 3)
        self.parts[idx_ojos].set_linestyle('None')
        self.parts[idx_ojos].set_alpha(0.8 + np.sin(t*10)*0.2)

class SuperformaProcedural:
    def __init__(self, ax):
        self.line, = ax.plot([], [], lw=1.5, alpha=0.9)
        
    def update(self, t, kick, harm, color_rgb):
        m = 3 + (harm * 12)
        n1 = 0.5 + kick * 2
        n2 = 1.0 + np.sin(t) 
        n3 = 1.0 + np.cos(t)
        
        phi = np.linspace(0, 2*np.pi, 500)
        part1 = np.abs(np.cos(m * phi / 4.0)) ** n2
        part2 = np.abs(np.sin(m * phi / 4.0)) ** n3
        r = (part1 + part2) ** (-1.0 / n1)
        
        scale = 3.5
        x = r * np.cos(phi) * scale
        y = r * np.sin(phi) * scale
        
        self.line.set_data(x, y)
        self.line.set_color(color_rgb)
        self.line.set_linewidth(1.0 + kick * 3.0)

class LorenzSwarm:
    def __init__(self, ax, num_attractors=3):
        self.attractors = []
        colors = plt.cm.cool(np.linspace(0, 1, num_attractors))
        
        for i in range(num_attractors):
            line, = ax.plot([], [], lw=0.8, alpha=0.7)
            state = np.random.rand(3) * 20 
            offset_x = np.random.uniform(-4.0, 4.0)
            offset_y = np.random.uniform(-2.5, 2.5)
            sigma = 10 + np.random.uniform(-1, 1)
            rho = 28 + np.random.uniform(-2, 2)
            
            self.attractors.append({
                'line': line, 'state': state, 'hist': [[],[],[]], 
                'offset': (offset_x, offset_y), 'params': (sigma, rho, 8/3),
                'color_base': colors[i]
            })

    def update(self, dt_base, kick, cymbals, visible=True):
        if not visible:
            for attr in self.attractors: attr['line'].set_alpha(0.0)
            return

        theta = cymbals * 15.0 
        Ry = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
        
        for attr in self.attractors:
            x, y, z = attr['state']
            sigma, rho, beta = attr['params']
            dt = dt_base * (1 + cymbals * 3.0)
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            new_state = np.array([x + dx*dt, y + dy*dt, z + dz*dt])
            
            if np.max(np.abs(new_state)) > 1e4 or np.isnan(new_state).any():
                attr['state'] = np.random.rand(3) * 10
                attr['hist'] = [[],[],[]]
            else:
                attr['state'] = new_state
                
            attr['hist'][0].append(attr['state'][0])
            attr['hist'][1].append(attr['state'][1])
            attr['hist'][2].append(attr['state'][2])
            if len(attr['hist'][0]) > 80: 
                for k in range(3): attr['hist'][k].pop(0)
                
            pts = np.array(attr['hist']).T
            pts_rot = pts @ Ry
            scale = 0.04
            off_x, off_y = attr['offset']
            shake = np.random.uniform(-0.02, 0.02) * kick
            
            attr['line'].set_data(pts_rot[:, 0] * scale + off_x + shake, pts_rot[:, 2] * scale + off_y + shake)
            attr['line'].set_linewidth(0.5 + cymbals * 2.5)
            attr['line'].set_color(attr['color_base'])
            attr['line'].set_alpha(0.7)

class GeneradorHojas:
    def __init__(self, ax):
        self.ax = ax
        self.hojas = []
        self.max_hojas = 20
        
    def spawn(self, x, y, color):
        if len(self.hojas) >= self.max_hojas:
            oldest = self.hojas.pop(0)
            oldest['line'].remove()
        line, = self.ax.plot([], [], lw=2, color=color, alpha=0.0)
        t = np.linspace(0, 1, 40)
        self.hojas.append({'line': line, 'x': x, 'y': y, 'shape_x': t, 'shape_y': np.sin(t * np.pi) * (0.3 + np.random.rand()*0.2), 'scale': 0.01, 'target_scale': np.random.uniform(0.5, 1.5), 'age': 0, 'angle': np.random.uniform(0, 2*np.pi)})
        
    def update(self, kick, harm):
        for hoja in self.hojas[:]:
            growth_rate = 0.02 + (harm * 0.05)
            if hoja['scale'] < hoja['target_scale']: hoja['scale'] += growth_rate
            hoja['age'] += 1
            c, s = np.cos(hoja['angle']), np.sin(hoja['angle'])
            rx = hoja['shape_x'] * c - hoja['shape_y'] * s
            ry = hoja['shape_x'] * s + hoja['shape_y'] * c
            hoja['line'].set_data(hoja['x'] + rx * hoja['scale'], hoja['y'] + ry * hoja['scale'])
            alpha = 1.0
            if hoja['scale'] < 0.2: alpha = hoja['scale'] * 5
            if hoja['age'] > 150: alpha = max(0, 1.0 - (hoja['age']-150)*0.02)
            hoja['line'].set_alpha(alpha)
            if alpha <= 0:
                hoja['line'].remove()
                self.hojas.remove(hoja)

class TunelCuantico3D:
    """
    Sistema de partículas 3D que viajan hacia la cámara (Eje Z).
    Crea sensación de velocidad y profundidad (Warp Speed).
    """
    def __init__(self, width, height, num_stars=200):
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        self.stars = np.zeros((num_stars, 3), dtype=np.float32)
        self.init_stars(range(num_stars))
        # Colores precalculados para velocidad
        self.colors = np.random.randint(150, 255, (num_stars, 3), dtype=np.uint8)

    def init_stars(self, indices):
        # X, Y aleatorios entre -W y W
        self.stars[indices, 0] = np.random.uniform(-self.w, self.w, len(indices))
        self.stars[indices, 1] = np.random.uniform(-self.h, self.h, len(indices))
        # Z aleatorio (profundidad)
        self.stars[indices, 2] = np.random.uniform(10, 2000, len(indices))

    def update_and_draw(self, frame, speed_base, kick):
        # Velocidad reactiva al kick
        speed = speed_base * (1 + kick * 8.0)
        
        # Mover estrellas hacia la cámara (disminuir Z)
        self.stars[:, 2] -= speed
        
        # Reciclar estrellas que pasaron la cámara (Z <= 1)
        reset_indices = np.where(self.stars[:, 2] <= 1)[0]
        if len(reset_indices) > 0:
            self.init_stars(reset_indices)
            self.stars[reset_indices, 2] = 2000 # Reiniciar al fondo

        # Proyección 3D a 2D: x' = x * (focal_length / z)
        focal_length = 400.0
        # Evitar división por cero
        z_safe = np.maximum(self.stars[:, 2], 0.1)
        factor = focal_length / z_safe
        
        x_2d = (self.stars[:, 0] * factor) + self.cx
        y_2d = (self.stars[:, 1] * factor) + self.cy
        
        # Dibujar en el frame (OpenCV directo para velocidad)
        for i in range(len(self.stars)):
            px, py = int(x_2d[i]), int(y_2d[i])
            if 0 <= px < self.w and 0 <= py < self.h:
                # El tamaño crece al acercarse
                size = int(1 + (1000 - self.stars[i, 2]) / 200)
                size = max(1, min(size, 5))
                # El brillo depende del kick
                color = tuple(map(int, self.colors[i] * (0.5 + kick * 0.5)))
                cv2.circle(frame, (px, py), size, color, -1)

class AdveccionTextura:
    """
    Técnica de Fluidos: Usa un campo de vectores (velocidad) para deformar una imagen.
    Crea efectos de 'pintura líquida' o 'humo colorido'.
    """
    def __init__(self, width, height, image_path=None):
        self.w = width
        self.h = height
        # Malla de coordenadas para remap (Mapas de distorsión)
        self.map_x, self.map_y = np.meshgrid(np.arange(width), np.arange(height))
        self.map_x = self.map_x.astype(np.float32)
        self.map_y = self.map_y.astype(np.float32)
        
        # Imagen base (opcional, si no se usa el frame anterior)
        self.texture = None
        if image_path:
            img = cv2.imread(image_path)
            if img is not None:
                self.texture = cv2.resize(img, (width, height))

    def update(self, flow_x, flow_y, strength=5.0):
        # Redimensionar el campo de fuerza si viene de una simulación pequeña (ej: Gray-Scott)
        if flow_x.shape != (self.h, self.w):
            fx = cv2.resize(flow_x, (self.w, self.h))
            fy = cv2.resize(flow_y, (self.w, self.h))
        else:
            fx, fy = flow_x, flow_y
            
        # Desplazar las coordenadas de lectura (Advección inversa)
        self.map_x -= fx * strength
        self.map_y -= fy * strength

    def render(self, source_image):
        # cv2.remap es ultra optimizado para esto
        # BORDER_REFLECT crea un efecto caleidoscópico en los bordes
        return cv2.remap(source_image, self.map_x, self.map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
