# 🎨 Enciclopedia de Modos de Renderizado

Este documento detalla la arquitectura técnica, matemática y artística de cada motor de visualización.

---

## 🚀 1. God Mode (El Estándar de Oro)
**Archivo:** `src/render_standard.py`

Es el motor más completo y equilibrado. Funciona como un "Director de Orquesta" que alterna entre diferentes simulaciones físicas según una estructura de "Actos".

### ⚙️ Funcionamiento Interno
1.  **Multiverso Físico:** Mantiene en memoria buffers para 7 simulaciones simultáneas (Gray-Scott, KS, GPE, Ondas, Cahn-Hilliard, Partículas, KdV).
2.  **Sistema de Actos:** Divide la canción en segmentos temporales. Cada segmento activa un motor específico con parámetros predefinidos (`p1`, `p2`) y una paleta de color (`cmap`).
3.  **Capa Híbrida:**
    *   **Fondo:** Simulación de fluidos acelerada con `Numba` (Cálculo numérico).
    *   **Overlay:** Geometría sagrada y "Espíritus" (entidades que bailan) renderizados con `Matplotlib` sobre un lienzo transparente.
4.  **Homeostasis:** El sistema detecta si una simulación "muere" (se vuelve negra o estática) o "explota" (valores infinitos) y la reinicia automáticamente con nuevas semillas aleatorias.

### 🎛️ Reactividad al Audio
*   **Kick (Bombo):** Genera impulsos de fuerza, zoom de cámara y flashes de luz (Bloom).
*   **Armonía:** Controla la rotación de color y la aparición de hojas/vegetación procedural.
*   **Nota Dominante:** Tiñe sutilmente la escena con el color asociado a la nota musical (Cromestesia).

---

## 🧠 2. Neural (Inteligencia Artificial)
**Archivo:** `src/render_main_autoencoders.py`

El modo más vanguardista. No sigue reglas humanas, sino que una IA "aprende" la canción y controla la física.

### ⚙️ Arquitectura Neuronal
1.  **Entrenamiento (Overfitting):** Al iniciar, entrena una red neuronal (Autoencoder) específicamente con **tu canción** durante ~150 épocas.
2.  **Espacio Latente:** La red comprime el audio en solo 3 valores abstractos ($z_0, z_1, z_2$) que representan la "esencia" del momento musical.
3.  **Mapeo Físico:**
    *   **$z_0$ (Selector):** Decide qué motor activar (0.0-0.2: Gray-Scott, 0.2-0.45: KS, etc.).
    *   **$z_1$ (Parámetro A):** Controla variables primarias (ej. tasa de alimentación).
    *   **$z_2$ (Parámetro B):** Controla el caos o la viscosidad.

### 🧬 Resultado
La visualización fluye de manera orgánica. Las transiciones entre efectos no son cortes bruscos, sino interpolaciones suaves dictadas por la similitud matemática entre partes de la canción.

---

## 🏛️ 3. Clásico (Determinista)
**Archivo:** `src/render_main clasico.py`

La versión estable y predecible. Ideal cuando quieres control total sobre el resultado visual.

### ⚙️ Diferencias Clave
*   **Configuración Manual:** Se basa estrictamente en el archivo `src/config.py`. Tú defines qué pasa y cuándo.
*   **Sin Capa de Overlay:** Se enfoca puramente en la simulación de fluidos, sin espíritus ni geometría 3D superpuesta.
*   **Estabilidad:** Al tener menos capas de complejidad, es más rápido de renderizar y menos propenso a errores de memoria.

---

## 🧬 4. Lenia (Vida Artificial Matemática)
**Archivo:** `src/render_lenia.py`

Una simulación de biología digital basada en Autómatas Celulares Continuos (una versión avanzada del "Juego de la Vida").

### ⚙️ Matemática
*   **Kernel:** Usa un anillo suave en lugar de una cuadrícula de vecinos.
*   **Física:** Calcula la convolución (FFT) del estado actual con el kernel para determinar el "potencial" de crecimiento.
*   **Audio-Reactividad:**
    *   El volumen de la música altera la tasa de crecimiento ($\mu$) y la desviación estándar ($\sigma$).
    *   **Efecto:** La música actúa como "comida". Con el silencio, las criaturas mueren; con el ritmo, crecen y se reproducen explosivamente.

---

## 🌊 5. Fluidos LBM (Navier-Stokes)
**Archivo:** `src/render_lbm.py`

Simulación de Dinámica de Fluidos Computacional (CFD) de alta fidelidad.

### ⚙️ Método Lattice Boltzmann (D2Q9)
En lugar de resolver ecuaciones complejas directamente, simula partículas ficticias en una rejilla que chocan y fluyen.
*   **Paso 1 (Colisión):** Las partículas interactúan e intercambian momento.
*   **Paso 2 (Streaming):** Las partículas se mueven a las celdas vecinas.
*   **Inyección:** El audio actúa como una bomba de presión que inyecta velocidad en el centro del lienzo, creando vórtices y turbulencias reales (Humo/Tinta).

---

## 🌀 6. Caos (Atractores Extraños)
**Archivo:** `src/render_chaos.py`

Visualización de la Teoría del Caos mediante sistemas de ecuaciones diferenciales no lineales.

### ⚙️ Atractor de Aizawa
Utiliza el sistema de ecuaciones de Aizawa para generar trayectorias orbitales complejas.
*   **Partículas:** 10,000 puntos trazan la forma del atractor en 3D.
*   **Reactividad:**
    *   La energía de la canción deforma la geometría del atractor (parámetro `a`).
    *   Las notas musicales (Chroma) alteran la curvatura de las órbitas (parámetro `d`).
*   **Visual:** Renderiza estelas (trails) que se desvanecen, creando formas fantasmales.

---

## 📜 7. Legacy (La Navaja Suiza)
**Archivo:** `src/render_main_legacy.py`

La versión original del motor, mantenida por su robustez y características únicas.

### ⚙️ Características Únicas
*   **Colisión con Texto:** Es el único modo donde las letras de la canción actúan como **obstáculos físicos**. El fluido choca contra las palabras y genera turbulencia alrededor de ellas.
*   **Doble Búfer Explícito:** Implementación manual de buffers de lectura/escritura para máxima estabilidad matemática.
*   **Análisis HPSS:** Separa el audio en Percusión y Armonía para controlar diferentes aspectos de la simulación por separado.