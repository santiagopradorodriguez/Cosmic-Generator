# 🌌 MANUAL MAESTRO V2.0: LA ENCICLOPEDIA DEFINITIVA DE REBELDÍA CÓSMICA

> **"Todo está conectado. La música no solo se escucha, ahora tiene masa, gravedad y luz propia."**

Bienvenido, Arquitecto del Sonido, a la enciclopedia técnica definitiva del **Cosmic Generator V2**, el motor de renderizado oficial de *Rebeldía Cósmica*. Este documento detalla exhaustivamente los secretos alquímicos, la física matemática y la infraestructura de Inteligencia Artificial que alimentan nuestro ecosistema de creación audiovisual. 

Esta obra está diseñada para democratizar la producción audiovisual de alto nivel, permitiendo que artistas independientes generen mundos reactivos hiper-profesionales basados en ecuaciones en derivadas parciales (EDPs) y sistemas complejos.

---

## 🏛️ PARTE I: LA ARQUITECTURA DEL SISTEMA (BACKEND & DATAFLOW)

El sistema está orquestado mediante un patrón modular avanzado en el que la interfaz gráfica (UI) invoca pipelines pesados en el backend, desacoplando el análisis semántico y acústico del motor de renderizado numérico de alta frecuencia.

### 1.1 Topología del Sistema
- **`app.py`**: El puente de control (Dashboard). Construido en *Streamlit*, orquesta hilos (Threads) para no bloquear la UI y utiliza una redirección segura (`StreamlitLogRedirector`) para la inyección de logs desde simuladores en C/Numba de bajo nivel. Lanza modos como: Generador Estable, Director IA, Laboratorio de Física y Separador neuronal.
- **`src/core`**: El corazón matemático del proyecto.
  - `nucleo_visual.py`: Integradores numéricos basados en diferencias finitas, altamente paralelizados y compilados Just-In-Time (JIT) vía **Numba** (`@jit(nopython=True, parallel=True)`).
  - `nucleo_espectral.py`: Integradores Pseudo-Espectrales (FFT) para ecuaciones rígidas (Stiff PDEs) usando ETD1 para Kuramoto-Sivashinsky y SSFM (Split-Step Fourier Method) para Gross-Pitaevskii.
  - `efectos_visuales.py`: Subsistema de shaders y cámara computacional en OpenCV.
  - `config.py`: Definición de perfiles de energía (Low/Mid/High) y mapas de Cromestesia.
- **`src/audio`**: Extracción inteligente de *features* y DSP avanzado usando Librosa.
- **`src/ai`**: Sistema de montaje automatizado impulsado por métricas de inferencia visual en PyTorch.

### 1.2 El Pipeline Audiovisual (Dataflow)
El viaje de los datos desde un `.wav` estático hasta una simulación física termodinámica ocurre en una cascada de 4 fases:

1. **Deconstrucción Acústica**: Se utiliza **Librosa HPSS** para bifurcar la señal en armónicos (tonos) y percusivos (transientes). Se extraen vectores de características por fotograma: *RMS Energy*, *Spectral Centroid*, y *Chroma STFT*. Se calcula la **"Tonalidad Reina"** para definir la paleta cromestésica maestra.
2. **Inyección Termodinámica**: Un bucle itera sobre la matriz de características. El audio altera las constantes físicas en tiempo real. Un control dinámico de paso de tiempo (`dt_dynamic`) mantiene la **condición CFL** estable ante picos de caos musical.
3. **Cinemática Computacional**: Aplicación de transformaciones afines usando matrices de rotación/zoom. Un "pumping" elástico se acopla directamente al Sub-bajo (Bass RMS).
4. **Post-Procesamiento Acumulativo**: Mapeo de color, acumulación de feedback temporal en HDR flotante, Luma Tone Mapping tipo Reinhard, *God Rays* iterativos y aberración cromática.

---

## 🔬 PARTE II: LA FÍSICA MATEMÁTICA DEL MOTOR

Cada píxel en este software es un agente sujeto al cálculo tensorial de espacios curvos, mecánica cuántica y estocástica de fluidos. La música es la entropía inyectada que evita que estos sistemas alcancen el aburrido equilibrio termodinámico.

### 2.1 Ecuación de Reacción-Difusión (Gray-Scott Puro)
Simula la creación de vida biológica y formación de patrones de Turing.
$$ \frac{\partial u}{\partial t} = D_u \nabla^2 u - u v^2 + F(1-u) $$
$$ \frac{\partial v}{\partial t} = D_v \nabla^2 v + u v^2 - (F+k)v $$
- **Reactividad**: El bajo y la textura engordan el plasma (alterando $F$ y $k$), causando que la biología mute orgánicamente.

### 2.2 Caos de Fuego: Kuramoto-Sivashinsky (KS)
La ecuación que gobierna frentes de llama turbulentos.
$$ u_t = -\nabla^2 u - \nabla^4 u - \frac{1}{2}|\nabla u|^2 $$
- **Resolución Espectral**: Se resuelve en el espacio de Fourier $\mathcal{F}$ utilizando el método ETD1. Los *kicks* actúan como ráfagas de viento sobre la llama de neón.

### 2.3 Fluido Cuántico de Gross-Pitaevskii (Condensado de Bose-Einstein)
Mecánica cuántica y superfluidos a temperaturas cercanas al cero absoluto.
$$ i\frac{\partial \psi}{\partial t} = \left(-\frac{1}{2}\nabla^2 + V(\mathbf{x}) + g|\psi|^2\right)\psi $$
- **Reactividad**: Forma vórtices cuánticos de fase hiperbólica que interactúan con las bajas frecuencias de la pista.

### 2.4 Ecuación de Ondas Estocástica (Líquido)
$$ \frac{\partial^2 u}{\partial t^2} = c^2 \nabla^2 u - \gamma \frac{\partial u}{\partial t} $$
- **Reactividad**: Genera perturbaciones acuáticas masivas en sincronía con los picos de percusión.

### 2.5 Allen-Cahn / Ohta-Kawasaki (Frustración Topológica)
$$ \frac{\partial u}{\partial t} = M(\nabla^2 \mu) - \sigma(u - \bar{u}) $$
$$ \mu = u^3 - u - \gamma \nabla^2 u $$
- **Efecto**: Modela laberintos repulsivos, simulando membranas celulares estabilizadas por fuerzas de repulsión de largo alcance.

### 2.6 Cahn-Hilliard Clásico (Aceite y Agua)
$$ \frac{\partial u}{\partial t} = \nabla \cdot (M \nabla \mu) $$
Modela procesos de separación espinodal termodinámica, creando manchas fluidas gigantes.

### 2.7 Solitones Dispersivos: Korteweg-De Vries (KdV)
Generalizado en 2D mediante la Ecuación ZK (Zakharov-Kuznetsov). Modela tsunamis y solitones que preservan su forma al chocar.

### 2.8 Caos 3D y Atractor de Clifford (Lorenz)
Simulación de atractores extraños y sistemas de ecuaciones diferenciales ordinarias donde trayectorias de partículas se proyectan en planos de texturas.

### 2.9 Geometría Sagrada (Fractales IFS)
Sistemas de Funciones Iteradas regidas por cadenas de Markov probabilísticas.
$$ W_i(\mathbf{x}) = A_i \mathbf{x} + \mathbf{b}_i $$
Se combina con espejos tensoriales para obtener mandalas con simetría $D_4$.

### 2.10 Relatividad General (Lentes Gravitacionales y Agujeros Negros)
Motor inyectando métrica de Kerr/Schwarzschild.
- **Deflexión Radial**: $r' = r + \frac{R_s^2}{r}$
- **Lense-Thirring (Arrastre de Marco)**: $\Delta\theta = \frac{\text{spin} \cdot R_s^3}{r^3 + \epsilon}$
- Cuando un *kick* percusivo extremo golpea, el campo invierte su gravedad, estallando como una supernova estocástica.

### 2.11 Mecánica de Fluidos: Lattice Boltzmann Method (LBM D2Q9)
Autómata celular termodinámico aplicando colisiones BGK (Bhatnagar-Gross-Krook) para emular ecuaciones complejas de Navier-Stokes. Inyecta *momentum* direccional directamente en la distribución de equilibrio de Maxwell-Boltzmann.

---

## 🎨 PARTE III: ESTÉTICA, CROMESTESIA Y CINEMÁTICA VIRTUAL

La magia ocurre en `MotorFX` y `CamaraVirtual`. El renderizado no es simplemente dibujar píxeles; es aplicar filtros fotónicos en un entorno HDR.

### 3.1 Sinergia Cromática Global (La Tonalidad Reina)
El color no es aleatorio. Se calcula una matriz espectral de *chroma features* para extraer la "Tonalidad Reina". A cada nota le corresponde una paleta sinestésica de matplotlib:
- **Do (C)**: `inferno` (Fuego, Acción, Energía en rojos).
- **Mi (E)**: `copper` (Dorado épico y brillante).
- **Sol (G)**: `ocean` (Azul, Paz, Fluidez de agua).
- **Si (B)**: `winter` (Cian y Cristalino).

### 3.2 Cinematografía Virtual Reactiva
- **Cámara Computacional**: Modos de Paneo clásico, Vértigo rítmico, y Caleidoscopio. La cámara aplica *Snap & Smooth* y hace un *shake* violento sincronizado al bombo.
- **Bloom Multicapa y God Rays**: Procesamiento de altas luces (highlights) con pirámides gaussianas. Genera *flashes* blancos y estroboscopios.
- **Aberración Cromática y Time-Slice Glitch**: Desplazamiento de canales Rojo y Azul (bombo y caja) e inyección de fotogramas pasados en cintas estilo VHS (glitches).
- **Datamoshing Biológico**: Las luces literalmente gotean por un mapa de gravedad falso acoplado al *Sub-bass*, generando estelas radiactivas.

---

## 📱 PARTE IV: EL MONOLITO VERTICAL (MODO REEL NATIVO)

Lejos de ser un recorte (*crop*) en post-producción, el nuevo **Modo Reel** re-arquitectura el motor numérico en caliente:
- Sobrescribe tensores a `WIDTH, HEIGHT = 1080, 1920`.
- Gravedad de partículas, dispersión de onda, atractores de IFS, y fluidos de Navier-Stokes re-calculan sus derivadas de bordes (*Boundary Conditions*) para un universo vertical.
- Tipografía (*LyricsEngine*) ajusta dinámicamente interlineados y envolventes elásticas para brillar sin cruzar los márgenes de TikTok o Instagram Reels.

---

## 🧠 PARTE V: MÓDULOS INTELIGENTES Y NEURONALES

### 5.1 Motor de Letras Cibernéticas (OpenAI Whisper)
El motor de letras utiliza la librería `stable-ts` acoplada a *Whisper* en modo alineación (*forced alignment*).
- **Re-segmentación Inteligente**: En vez de mostrar largos párrafos, orquesta la letra de forma rítmica (máximo 4 palabras, máximo 2 segundos), adaptándose a lectura rápida.
- **Reacción Física**: Las letras renderizadas operan como fuentes escalares de luz. Brillan con la voz, rebotan con el bombo y derraman su tinta a través de distorsiones senoidales 2D.

### 5.2 Modo Sinestesia (Separación Multiverso por Demucs)
Al activar la separación por stems (`htdemucs`):
- **Bajo (Bass)** modula biologías pesadas como *Gray-Scott*.
- **Voces (Vocals)** controla el agua turquesa en la *Ecuación de Ondas*.
- **Batería (Drums)** dispara explosiones cuánticas en *Sistemas de Partículas*.
- **Otros (Sintes)** perturba el atractor de fuego *Kuramoto-Sivashinsky*.
- Todos confluyen mediante *Additive Blending HDR*.

### 5.3 Director IA (Montaje Profundo PyTorch)
El `director_ai.py` ensambla escenas largas offline:
- Mide "Energía Visual" mediante derivadas de fotogramas y contrastes tensoriales en PyTorch.
- **Pacing Automático**: Corta rápidamente en zonas de clímax sonoro (1-2 beats) y se toma su tiempo en los valles (4-8 beats).
- Evalúa distancia Euclidiana para acoplar la pieza visual exacta al estado de ánimo del audio, generando una obra final épica con contrastes y *drops* en `moviepy`.

---

> *"Aquí culmina la enciclopedia. Utiliza estas herramientas con la sabiduría matemática de los Antiguos y la agresividad artística del Cosmos."* — Rebeldía Cósmica
