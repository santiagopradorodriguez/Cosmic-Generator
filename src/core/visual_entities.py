"""
(C) Rebeldía Cósmica | Creado por Santiago Prado
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt

class EspirituProcedural:
    """
    Clase que representa un espíritu procedural dentro del ecosistema de Rebeldía Cósmica.
    Se encarga de generar y actualizar sistemas de partículas que simulan humo volumétrico 
    con comportamiento dinámico y reactivo a la música, creando formas orgánicas y etéreas.
    """
    def __init__(self, w, h, seed_val):
        """
        Inicializa la instancia de EspirituProcedural, configurando las dimensiones de la pantalla
        y preparando el sistema de partículas vectorizado mediante NumPy para máxima eficiencia.
        
        Parámetros:
        -----------
        w : int
            Ancho del área de renderizado o pantalla en píxeles.
        h : int
            Alto del área de renderizado o pantalla en píxeles.
        seed_val : int
            Semilla para el generador de números aleatorios (RandomState), asegurando que el comportamiento 
            sea determinista y reproducible si se requiere la misma semilla.
        """
        self.w = w
        self.h = h
        self.rng = np.random.RandomState(seed_val)
        self.scale_var = self.rng.uniform(0.8, 1.5)
        self.speed_var = self.rng.uniform(0.5, 2.0)
        
        # Volumetric smoke particles (NumPy vectorized)
        self.num_particles = 1500
        # Columns: [x, y, vx, vy, life, max_life, size]
        self.particles = np.zeros((self.num_particles, 7), dtype=np.float32)
        self.noise_offset = self.rng.uniform(0, 1000)

    def _to_screen(self, x, y):
        """
        Transforma coordenadas lógicas del plano cartesiano 2D al sistema de coordenadas de la pantalla (píxeles).
        
        Parámetros:
        -----------
        x : float
            Coordenada lógica X en el plano.
        y : float
            Coordenada lógica Y en el plano.
            
        Retorna:
        --------
        tuple[int, int]
            Una tupla (px, py) que representa las coordenadas transformadas en píxeles listas para dibujar.
        """
        aspect = self.w / self.h
        logical_w = 8.0 * aspect
        logical_h = 8.0
        px = int((x + logical_w/2) / logical_w * self.w)
        py = int((-y + logical_h/2) / logical_h * self.h)
        return px, py

    def update(self, frame, x, y, scale, t, kick, harm, color_rgb):
        """
        Actualiza y dibuja el sistema de partículas de humo volumétrico en el fotograma actual. 
        Reacciona en tiempo real a las métricas musicales, calculando la emisión de nuevas partículas,
        aplicando turbulencia (Browniana) y reduciendo su vida progresivamente para crear un efecto de humo etéreo.

        Parámetros:
        -----------
        frame : numpy.ndarray
            El fotograma (imagen BGR de OpenCV) actual donde se dibujará la entidad.
        x : float
            Posición lógica X base del espíritu procedural.
        y : float
            Posición lógica Y base del espíritu procedural.
        scale : float
            Factor de escala base que determina el tamaño del espíritu. Si es <= 0, no se dibuja.
        t : float
            Tiempo o fase temporal actual de la animación, usado para el movimiento oscilante.
        kick : float
            Intensidad de los graves (bombos) en el momento actual, entre 0 y 1. Impacta la cantidad y explosividad del humo.
        harm : float
            Intensidad del contenido armónico de la música. Afecta el tiempo de vida de las partículas.
        color_rgb : tuple[float, float, float] o list[float]
            Color base RGB de las partículas (cada canal entre 0 y 1).
        """
        color_bgr = np.array([color_rgb[2]*255, color_rgb[1]*255, color_rgb[0]*255], dtype=np.float32)
        if scale <= 0: return

        scale *= self.scale_var
        t *= self.speed_var
        wobble = np.sin(t * 3) * 0.05 * scale
        
        hx = x + wobble
        hy = y + (1.6 * scale)
        px, py = self._to_screen(hx, hy)
        
        # 1. EMITIR NUEVAS PARTÍCULAS (Humo volumétrico)
        emision_rate = int(30 + kick * 100) # Más partículas si hay kick
        
        # Encontrar slots libres (life <= 0)
        dead_indices = np.where(self.particles[:, 4] <= 0)[0]
        emit_count = min(emision_rate, len(dead_indices))
        
        if emit_count > 0:
            idx = dead_indices[:emit_count]
            
            # Posición inicial: px, py + pequeña dispersión
            self.particles[idx, 0] = px + self.rng.normal(0, 5 * scale, emit_count)
            self.particles[idx, 1] = py + self.rng.normal(0, 5 * scale, emit_count)
            
            # Velocidad: Movimiento orgánico ascendente/aleatorio
            base_vx = np.sin(t * 2 + self.noise_offset) * 2.0
            base_vy = -2.0 - kick * 3.0 # Hacia arriba
            
            self.particles[idx, 2] = base_vx + self.rng.normal(0, 1.5, emit_count)
            self.particles[idx, 3] = base_vy + self.rng.normal(0, 1.5, emit_count)
            
            # Vida
            vidas = self.rng.uniform(20.0, 60.0 + harm * 40.0, emit_count)
            self.particles[idx, 4] = vidas
            self.particles[idx, 5] = vidas # Max life
            
            # Tamaño
            self.particles[idx, 6] = self.rng.uniform(2.0, 8.0 * scale, emit_count)
            
        # 2. ACTUALIZAR PARTÍCULAS ACTIVAS
        alive = self.particles[:, 4] > 0
        if not np.any(alive):
            cv2.circle(frame, (int(px), int(py)), max(1, int(4+kick*5)), (255,255,255), -1)
            return
            
        # Turbulencia (Movimiento Browniano / Curl noise simulado)
        self.particles[alive, 2] += np.sin(self.particles[alive, 1] * 0.05 + t) * 0.2
        self.particles[alive, 3] += np.cos(self.particles[alive, 0] * 0.05 + t) * 0.2
        
        # Fricción (Air drag)
        self.particles[alive, 2] *= 0.95
        self.particles[alive, 3] *= 0.95
        
        # Integrar posición
        self.particles[alive, 0] += self.particles[alive, 2]
        self.particles[alive, 1] += self.particles[alive, 3]
        
        # Reducir vida
        self.particles[alive, 4] -= 1.0
        
        # Crecimiento del tamaño del humo (se expande al disiparse)
        self.particles[alive, 6] *= 1.02
        
        # 3. RENDERIZADO HIPER-REALISTA
        # Obtener posiciones, vida y tamaño de las vivas
        pos_x = self.particles[alive, 0].astype(np.int32)
        pos_y = self.particles[alive, 1].astype(np.int32)
        vidas_norm = self.particles[alive, 4] / self.particles[alive, 5] # 1.0 a 0.0
        sizes = self.particles[alive, 6].astype(np.int32)
        
        # Pre-filtrar por límites de pantalla
        valid = (pos_x >= 0) & (pos_x < self.w) & (pos_y >= 0) & (pos_y < self.h)
        pos_x = pos_x[valid]
        pos_y = pos_y[valid]
        vidas_norm = vidas_norm[valid]
        sizes = sizes[valid]
        
        # Crear capa de humo local para additive blending optimizado
        for px_val, py_val, vn, s in zip(pos_x, pos_y, vidas_norm, sizes):
            if s < 1: continue
            alpha = vn * 0.6  # Transparencia
            # Color interpolado: Núcleo blanco -> Color -> Disipación oscura
            if vn > 0.8:
                c = (255, 255, 255) # Blanco caliente
            else:
                c = (int(color_bgr[0] * alpha), int(color_bgr[1] * alpha), int(color_bgr[2] * alpha))
            
            # Smoke dot
            cv2.circle(frame, (px_val, py_val), s, c, -1)
            
        # Añadir un resplandor al núcleo emisor
        cv2.circle(frame, (int(px), int(py)), max(1, int(6 * scale + kick * 10)), (255,255,255), -1, cv2.LINE_AA)
        glow_r = max(1, int(15 * scale + kick * 20))
        cv2.circle(frame, (int(px), int(py)), glow_r, (int(color_bgr[0]*0.5), int(color_bgr[1]*0.5), int(color_bgr[2]*0.5)), 2, cv2.LINE_AA)

class SuperformaProcedural:
    """
    Clase que genera geometría y curvas 2D extremas mediante la fórmula de las Superformas 
    (Superformula), un sistema matemático capaz de modelar una gran cantidad de formas orgánicas 
    y naturales. Reacciona a parámetros musicales para mutar su forma a lo largo del tiempo.
    """
    def __init__(self, w, h):
        """
        Inicializa la clase SuperformaProcedural con el ancho y alto del fotograma de renderizado.

        Parámetros:
        -----------
        w : int
            Ancho del área de renderizado o pantalla en píxeles.
        h : int
            Alto del área de renderizado o pantalla en píxeles.
        """
        self.w = w
        self.h = h
        
    def _to_screen(self, x, y):
        """
        Transforma coordenadas lógicas a coordenadas de pantalla (píxeles) manteniendo 
        la relación de aspecto correcta del área visual.

        Parámetros:
        -----------
        x : float
            Coordenada lógica X a transformar.
        y : float
            Coordenada lógica Y a transformar.

        Retorna:
        --------
        tuple[int, int]
            Las coordenadas X e Y correspondientes en píxeles de la pantalla.
        """
        aspect = self.w / self.h
        logical_w = 8.0 * aspect
        logical_h = 8.0
        px = int((x + logical_w/2) / logical_w * self.w)
        py = int((-y + logical_h/2) / logical_h * self.h)
        return px, py

    def update(self, frame, t, kick, harm, color_rgb):
        """
        Calcula la Superforma (Superformula) evaluando la fórmula para una serie de ángulos, y dibuja
        el polígono resultante en el frame. La silueta y detalles geométricos mutan 
        con el tiempo y los impulsos rítmicos.

        Parámetros:
        -----------
        frame : numpy.ndarray
            El fotograma o lienzo (imagen BGR) donde se renderizará la superforma.
        t : float
            Tiempo o fase de la animación; influye directamente en las potencias y componentes armónicos de la forma.
        kick : float
            Impulso de batería/bombo (0 a 1). Engrosa los bordes de la figura e influye en parámetros geométricos.
        harm : float
            Nivel de contenido armónico o melódico musical (0 a 1). Modifica la variable 'm' (simetría) de la ecuación.
        color_rgb : tuple[float, float, float] o list[float]
            Color interno de relleno RGB (cada canal entre 0 y 1). El borde será dibujado en blanco brillante.
        """
        color_bgr = (int(color_rgb[2]*255), int(color_rgb[1]*255), int(color_rgb[0]*255))
        m = 3 + (harm * 12)
        n1 = 0.5 + kick * 2
        n2 = 1.0 + np.sin(t) 
        n3 = 1.0 + np.cos(t)
        
        phi = np.linspace(0, 2*np.pi, 200)
        part1 = np.abs(np.cos(m * phi / 4.0)) ** n2
        part2 = np.abs(np.sin(m * phi / 4.0)) ** n3
        r = (part1 + part2) ** (-1.0 / n1)
        
        scale = 3.5
        x = r * np.cos(phi) * scale
        y = r * np.sin(phi) * scale
        
        pts = []
        for i in range(len(x)):
            pts.append(self._to_screen(x[i], y[i]))
            
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        thickness = max(1, int(3.0 + kick * 2.0))
        
        # Superforma Premium: Relleno sólido + Núcleo Blanco
        cv2.fillPoly(frame, [pts], color_bgr, cv2.LINE_AA)
        cv2.polylines(frame, [pts], True, (255, 255, 255), thickness, cv2.LINE_AA)

class LorenzSwarm:
    def __init__(self, w, h, num_attractors=3):
        self.w = w
        self.h = h
        self.attractors = []
        colors = plt.cm.cool(np.linspace(0, 1, num_attractors))
        
        for i in range(num_attractors):
            state = np.random.rand(3) * 20 
            offset_x = np.random.uniform(-4.0, 4.0)
            offset_y = np.random.uniform(-2.5, 2.5)
            sigma = 10 + np.random.uniform(-1, 1)
            rho = 28 + np.random.uniform(-2, 2)
            c = colors[i]
            c_bgr = (int(c[2]*255), int(c[1]*255), int(c[0]*255))
            
            self.attractors.append({
                'state': state, 'hist': [[],[],[]], 
                'offset': (offset_x, offset_y), 'params': (sigma, rho, 8/3),
                'color_bgr': c_bgr
            })

    def _to_screen(self, x, y):
        aspect = self.w / self.h
        logical_w = 8.0 * aspect
        logical_h = 8.0
        px = int((x + logical_w/2) / logical_w * self.w)
        py = int((-y + logical_h/2) / logical_h * self.h)
        return px, py

    def update(self, frame, dt_base, kick, cymbals, visible=True):
        if not visible: return

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
                
            pts_3d = np.array(attr['hist']).T
            if len(pts_3d) > 1:
                pts_rot = pts_3d @ Ry
                scale = 0.04
                off_x, off_y = attr['offset']
                shake = np.random.uniform(-0.02, 0.02) * kick
                
                screen_pts = []
                for i in range(len(pts_rot)):
                    xx = pts_rot[i, 0] * scale + off_x + shake
                    yy = pts_rot[i, 2] * scale + off_y + shake
                    screen_pts.append(self._to_screen(xx, yy))
                
                for i in range(1, len(screen_pts)):
                    pt1 = screen_pts[i-1]
                    pt2 = screen_pts[i]
                    thick = max(1, int((i / 80) * 4 * (1 + cymbals)))
                    cv2.line(frame, pt1, pt2, attr['color_bgr'], thick, cv2.LINE_AA)

class GeneradorHojas:
    """
    Clase encargada de la generación y gestión procedural de figuras con forma de hoja de plantas.
    Emite "hojas" que crecen con el tiempo y forman patrones rotatorios orgánicos, simétricos e intrincados,
    cuyo comportamiento y ritmo de desarrollo responde a los componentes armónicos de la música.
    """
    def __init__(self, w, h):
        """
        Inicializa el generador, definiendo límites de pantalla y estableciendo la capacidad 
        máxima de la lista de hojas en memoria.

        Parámetros:
        -----------
        w : int
            Ancho de la pantalla / resolución en píxeles.
        h : int
            Alto de la pantalla / resolución en píxeles.
        """
        self.w = w
        self.h = h
        self.hojas = []
        self.max_hojas = 20
        
    def _to_screen(self, x, y):
        """
        Convierte una posición 2D expresada en unidades lógicas del sistema de coordenadas a la 
        correspondiente posición de píxeles en pantalla con el aspect ratio corregido.

        Parámetros:
        -----------
        x : float
            Posición X en el sistema lógico.
        y : float
            Posición Y en el sistema lógico.

        Retorna:
        --------
        tuple[int, int]
            Posición X, Y en píxeles como enteros.
        """
        aspect = self.w / self.h
        logical_w = 8.0 * aspect
        logical_h = 8.0
        px = int((x + logical_w/2) / logical_w * self.w)
        py = int((-y + logical_h/2) / logical_h * self.h)
        return px, py

    def spawn(self, x, y, color_rgb):
        """
        Añade (instancia) una nueva hoja procedural (representada por un diccionario de propiedades) en 
        las coordenadas dadas. Si se supera el límite máximo, elimina la más vieja. Genera de forma 
        aleatoria la forma base de la hoja, su rotación, y su objetivo de escala máxima.

        Parámetros:
        -----------
        x : float
            Posición inicial X en el plano lógico.
        y : float
            Posición inicial Y en el plano lógico.
        color_rgb : tuple[float, float, float] o list[float]
            Color RGB (cada canal de 0 a 1) base para esta hoja.
        """
        color_bgr = (int(color_rgb[2]*255), int(color_rgb[1]*255), int(color_rgb[0]*255))
        if len(self.hojas) >= self.max_hojas:
            self.hojas.pop(0)
        t = np.linspace(0, 1, 40)
        shape_x = t
        shape_y = np.sin(t * np.pi) * (0.3 + np.random.rand()*0.2)
        self.hojas.append({
            'x': x, 'y': y, 'shape_x': shape_x, 'shape_y': shape_y, 
            'scale': 0.01, 'target_scale': np.random.uniform(0.5, 1.5), 
            'age': 0, 'angle': np.random.uniform(0, 2*np.pi),
            'color_bgr': color_bgr
        })
        
    def update(self, frame, kick, harm):
        """
        Itera sobre todas las hojas activas, actualizando sus tamaños (escalado o 'crecimiento'), 
        edades y calculando sus transformaciones afines (rotación y simetría bilateral). 
        Finalmente, dibuja los polígonos generados de cada hoja sobre el fotograma, aplicando
        efectos de 'fade in/out' basados en su vida útil.

        Parámetros:
        -----------
        frame : numpy.ndarray
            El fotograma BGR actual en el que se pintarán las geometrías de las hojas.
        kick : float
            Valor del impulso rítmico (bombo) (0 a 1). En la versión actual no tiene uso directo, 
            pero se pasa por compatibilidad con el pipeline de renderizado reactivo a sonido.
        harm : float
            Contenido armónico de la música (0 a 1), que actúa como un fertilizante sonoro. 
            A mayor valor, más rápido crecen las hojas en la pantalla.
        """
        for hoja in self.hojas[:]:
            growth_rate = 0.02 + (harm * 0.05)
            if hoja['scale'] < hoja['target_scale']: hoja['scale'] += growth_rate
            hoja['age'] += 1
            
            c, s = np.cos(hoja['angle']), np.sin(hoja['angle'])
            rx = hoja['shape_x'] * c - hoja['shape_y'] * s
            ry = hoja['shape_x'] * s + hoja['shape_y'] * c
            
            gx = hoja['x'] + rx * hoja['scale']
            gy = hoja['y'] + ry * hoja['scale']
            
            pts = []
            for i in range(len(gx)):
                pts.append(self._to_screen(gx[i], gy[i]))
            
            rx_sym = hoja['shape_x'] * c - (-hoja['shape_y']) * s
            ry_sym = hoja['shape_x'] * s + (-hoja['shape_y']) * c
            gx_sym = hoja['x'] + rx_sym * hoja['scale']
            gy_sym = hoja['y'] + ry_sym * hoja['scale']
            
            pts_sym = []
            for i in range(len(gx_sym)-1, -1, -1):
                pts_sym.append(self._to_screen(gx_sym[i], gy_sym[i]))
                
            full_pts = pts + pts_sym
            poly = np.array(full_pts, np.int32).reshape((-1, 1, 2))
            
            alpha_mult = 1.0
            if hoja['scale'] < 0.2: alpha_mult = hoja['scale'] * 5
            if hoja['age'] > 150: alpha_mult = max(0, 1.0 - (hoja['age']-150)*0.02)
            
            if alpha_mult <= 0:
                self.hojas.remove(hoja)
                continue
                
            c_bgr = tuple(int(ch * alpha_mult) for ch in hoja['color_bgr'])
            cv2.fillPoly(frame, [poly], c_bgr, cv2.LINE_AA)
            cv2.polylines(frame, [poly], True, (255,255,255), 1, cv2.LINE_AA)

class TunelCuantico3D:
    def __init__(self, width, height, num_stars=200):
        self.w = width
        self.h = height
        self.cx = width // 2
        self.cy = height // 2
        self.stars = np.zeros((num_stars, 3), dtype=np.float32)
        self.init_stars(range(num_stars))
        self.colors = np.random.randint(150, 255, (num_stars, 3), dtype=np.uint8)

    def init_stars(self, indices):
        self.stars[indices, 0] = np.random.uniform(-self.w, self.w, len(indices))
        self.stars[indices, 1] = np.random.uniform(-self.h, self.h, len(indices))
        self.stars[indices, 2] = np.random.uniform(10, 2000, len(indices))

    def update_and_draw(self, frame, speed_base, kick):
        speed = speed_base * (1 + kick * 8.0)
        self.stars[:, 2] -= speed
        reset_indices = np.where(self.stars[:, 2] <= 1)[0]
        if len(reset_indices) > 0:
            self.init_stars(reset_indices)
            self.stars[reset_indices, 2] = 2000 
        focal_length = 400.0
        z_safe = np.maximum(self.stars[:, 2], 0.1)
        factor = focal_length / z_safe
        x_2d = (self.stars[:, 0] * factor) + self.cx
        y_2d = (self.stars[:, 1] * factor) + self.cy
        for i in range(len(self.stars)):
            px, py = int(x_2d[i]), int(y_2d[i])
            if 0 <= px < self.w and 0 <= py < self.h:
                size = int(1 + (1000 - self.stars[i, 2]) / 200)
                size = max(1, min(size, 5))
                color = tuple(map(int, self.colors[i] * (0.5 + kick * 0.5)))
                cv2.circle(frame, (px, py), size, color, -1)

class AdveccionTextura:
    def __init__(self, width, height, image_path=None):
        self.w = width
        self.h = height
        self.map_x, self.map_y = np.meshgrid(np.arange(width), np.arange(height))
        self.map_x = self.map_x.astype(np.float32)
        self.map_y = self.map_y.astype(np.float32)
        self.texture = None
        if image_path:
            img = cv2.imread(image_path)
            if img is not None:
                self.texture = cv2.resize(img, (width, height))

    def update(self, flow_x, flow_y, strength=5.0):
        if flow_x.shape != (self.h, self.w):
            fx = cv2.resize(flow_x, (self.w, self.h))
            fy = cv2.resize(flow_y, (self.w, self.h))
        else:
            fx, fy = flow_x, flow_y
        self.map_x -= fx * strength
        self.map_y -= fy * strength

    def render(self, source_image):
        return cv2.remap(source_image, self.map_x, self.map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
