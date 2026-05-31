# (C) Rebeldía Cósmica | Creado por Santiago Prado
import numpy as np

class CPPNEngine:
    """
    Compositional Pattern Producing Network (CPPN)
    Un motor de inteligencia artificial hiper-rápido basado en NumPy.
    No se entrena; se inicializa con pesos aleatorios y el audio manipula sus parámetros latentes.
    """
    def __init__(self, width, height, hidden_size=32, num_layers=4, seed=42):
        self.width = width
        self.height = height
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        np.random.seed(seed)
        
        # Generar cuadrícula de coordenadas espaciales normalizadas (-1 a 1)
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x, y)
        
        # Flatten para vectorizar el cálculo (N, 1)
        self.X = xv.flatten().reshape(-1, 1)
        self.Y = yv.flatten().reshape(-1, 1)
        self.R = np.sqrt(self.X**2 + self.Y**2)
        
        self.N = len(self.X) # Total de píxeles
        
        # Inicializar estado de Lorenz (Caos)
        self.lorenz_state = np.array([1.0, 1.0, 1.0])
        
        # Inicializar pesos de la red
        self.weights = []
        self.biases = []
        
        # Input layer: x, y, r, lx, ly, lz (6 entradas)
        input_dim = 6
        self.weights.append(np.random.randn(input_dim, hidden_size) * 1.5)
        self.biases.append(np.random.randn(hidden_size))
        
        # Hidden layers
        for _ in range(num_layers - 1):
            self.weights.append(np.random.randn(hidden_size, hidden_size) * np.sqrt(2.0/hidden_size))
            self.biases.append(np.random.randn(hidden_size))
            
        # Output layer: 1 valor (Densidad, que luego se mapea a color)
        self.weights.append(np.random.randn(hidden_size, 1))
        self.biases.append(np.random.randn(1))
        
        # Funciones de activación aleatorias para cada capa para máxima psicodelia
        self.activations = [np.sin, np.cos, np.tanh, self._gaussian]
        self.layer_acts = [np.random.choice(self.activations) for _ in range(num_layers)]

    def _gaussian(self, x):
        return np.exp(-(x**2))

    def _step_lorenz(self, dt=0.01):
        # Resolver inestabilidad de Euler mediante sub-pasos dinámicos
        num_steps = int(max(1, dt / 0.005))
        sub_dt = dt / num_steps
        
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        
        for _ in range(num_steps):
            x, y, z = self.lorenz_state
            dx = sigma * (y - x) * sub_dt
            dy = (x * (rho - z) - y) * sub_dt
            dz = (x * y - beta * z) * sub_dt
            self.lorenz_state += np.array([dx, dy, dz])
            
            # Clip de seguridad hiper-estricto para evitar Overflow/NaN en la Red Neuronal
            self.lorenz_state = np.clip(self.lorenz_state, -100.0, 100.0)
            
        return self.lorenz_state / 20.0 # Normalizado a un rango latente estable

    def generate_frame(self, time_t, audio_z):
        """
        Genera un fotograma completo basado en la integración caótica.
        """
        # El audio empuja la velocidad de integración del fractal
        lx, ly, lz = self._step_lorenz(dt=0.01 + audio_z * 0.05)
        
        LX = np.full((self.N, 1), lx)
        LY = np.full((self.N, 1), ly)
        LZ = np.full((self.N, 1), lz)
        
        # Ensamblar input (N, 6)
        layer_input = np.hstack([self.X, self.Y, self.R, LX, LY, LZ])
        
        # Forward Pass
        for i in range(self.num_layers):
            layer_input = np.dot(layer_input, self.weights[i]) + self.biases[i]
            layer_input = self.layer_acts[i](layer_input)
            
        # Output Pass
        output = np.dot(layer_input, self.weights[-1]) + self.biases[-1]
        
        # Normalizar a 0-1
        output = (np.sin(output) + 1.0) * 0.5
        
        return output.reshape((self.height, self.width)).astype(np.float32)

