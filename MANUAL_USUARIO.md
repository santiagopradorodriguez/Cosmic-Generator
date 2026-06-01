# 📖 Manual Avanzado de Usuario y Herramientas

Este documento es la guía definitiva para operar el **Launcher** (`lanzador.py`) y dominar las herramientas de Inteligencia Artificial integradas.

---

## 🚀 Interfaz del Launcher (Paso a Paso)

El `lanzador.py` es el centro de control de todo el proyecto. Desde aquí configuras y ejecutas los renders.

### 1. 🧠 Director IA y Pestaña Oficial (Panel Superior)
Aquí interactúas con el cerebro del sistema y la esencia de nuestra cooperativa.
*   **Pestaña "Nihil Morari":** Una sección promocional dedicada a nuestro álbum estandarte. Encontrarás su arte conceptual inmersivo y el enlace directo a Bandcamp. ¡Nuestra música es la que inspira el motor!
*   **Entrada de Texto:** Escribe qué quieres ver (ej. "Un océano de neón con tormenta").
*   **Micrófono (🎤):** Dicta tu idea por voz. Requiere conexión a internet para Google Speech Recognition.
*   **Botón `✨ APLICAR ESTILO`:** Envía tu descripción a la IA local (Llama 3.2) para que configure los motores automáticamente.
*   **Botón `💅 LINDA LETRA`:** Activa el agente de corrección de subtítulos.

### 2. ⚙️ Configuración Técnica
*   **Duración (s):** Tiempo de renderizado.
    *   *Vacío:* Renderiza toda la canción.
    *   *Número:* Solo los primeros X segundos (útil para pruebas).
*   **Res:** Resolución de salida. Afecta directamente al rendimiento. `1280x720` es el equilibrio ideal.

### 3. ⚛️ Motores Físicos & Semilla
Control manual de los algoritmos.
*   **Motores (GS, KS, WAVE...):** Determina qué simulaciones están permitidas en el "God Mode".
*   **Seed:** Número semilla para el generador aleatorio. Si usas el mismo Seed, obtendrás exactamente el mismo video.
*   **Estilos Especiales (Optimizados en V2.0):**
    *   `👻 Espíritus`: Activa entidades procedurales que bailan.
    *   `🔮 Caleido`: Activa simetría radial (mandalas).
    *   `⚡ Flash y Bloom (Suavizados)`: Vinculado al bombo (kick). Hemos afinado la fotometría para mantener el impacto visual pero protegiendo los ojos de los espectadores.
    *   `🎬 Luma Tone Mapping HDR (Modo Mix)`: ¡Novedad absoluta! Mantiene los colores en rangos cinemáticos durante la retroalimentación analógica, impidiendo el quemado de blancos.
    *   `🎨 Nota`: Activa la **Cromestesia** (el color cambia según la nota musical detectada).

### 4. 📂 Gestión de Archivos
*   `📂 SELECCIONAR`: Elige tu archivo de audio (.mp3, .flac, .wav).
*   `📦 MOVER VIDEOS`: Mueve todos los .mp4 generados a la carpeta `RENDERS/` para limpiar.
*   `🧠 EXTRAER LETRA`: Usa Whisper para generar el archivo `.json` de tiempos.
*   `📝 EDITAR LETRA`: Abre un editor visual para corregir tiempos y textos manualmente.
*   `🔥 ALINEACIÓN FORZADA (Forced Alignment)`: ¡Nueva función! Pega tu letra oficial exacta para eludir los errores de transcripción de la IA. El motor calculará el tiempo en milisegundos de cada sílaba. Para mantenerte al tanto, la UI muestra una **Barra de Progreso Fluida** rediseñada.

---

## 🤖 Herramientas de Inteligencia Artificial

### A. Modo "Poner Linda Letra" (Beautify Lyrics)
**Problema:** Whisper transcribe bien las palabras, pero entrega bloques de texto gigantes, sin puntuación y con cortes de tiempo extraños.
**Solución:** Este modo envía la transcripción cruda a **Llama 3.2** con instrucciones de ser un "Editor de Video Musical".

**Proceso Interno:**
1.  Lee el `.json` generado por Whisper.
2.  Pide a la IA que:
    *   Corrija ortografía y gramática.
    *   Añada signos (¿? ¡! , .).
    *   **Re-segmente** las frases para que sean cortas y estéticas (estilo TikTok/Reels).
3.  Sobrescribe el archivo `.json` con la versión mejorada.

### B. Modo "Aplicar Estilo" (Director IA)
Traduce lenguaje natural a parámetros técnicos.

**Ejemplo de Flujo:**
1.  **Usuario:** "Quiero algo como el espacio exterior, muy lento y con estrellas."
2.  **IA (Pensamiento):**
    *   *Conceptos:* Espacio -> Oscuridad, Partículas. Lento -> Baja reactividad.
    *   *Motores:* `PARTICLES` (estrellas), `GPE` (nebulosas cuánticas).
    *   *Color:* `twilight` o `magma`.
3.  **Acción:** El Launcher marca automáticamente los checkboxes `PARTICLES` y `GPE`, y establece la paleta de color interna.

---

## 🚀 Flujo de Trabajo Recomendado (Botón Grande)

El botón **`🚀 PROCESAR CANCIÓN`** ejecuta un asistente paso a paso:

1.  **Extracción:** ¿Quieres sacar la letra con Whisper?
2.  **Embellecimiento:** ¿Quieres que la IA mejore la letra?
3.  **Edición:** ¿Quieres revisar los tiempos manualmente?
4.  **Estilo:** ¿Cómo quieres que se vea el video? (Prompt para la IA).
5.  **Render:** Selecciona qué modos renderizar (puedes marcar varios).
6.  **Resultado:** Crea una carpeta `Session_X` con todos los videos generados y un montaje final editado por el Director IA.

---

## 🧪 Solución de Problemas

*   **El video sale negro:** Probablemente el umbral de audio es muy alto. Intenta normalizar el audio antes.
*   **Error de Memoria (OOM):** Baja la resolución a `1280x720` o reduce el número de motores activos en God Mode.
*   **La IA no responde:** Asegúrate de tener **Ollama** ejecutándose en segundo plano (`ollama serve`) y el modelo `llama3.2` descargado (`ollama pull llama3.2`).
*   **Diagnóstico:** Usa el botón `🧪 DIAGNÓSTICO` para correr una prueba rápida de 15s de cada motor y ver cuál falla.