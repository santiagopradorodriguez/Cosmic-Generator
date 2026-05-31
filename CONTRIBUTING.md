# 🤝 Guía de Contribución para Cosmic Generator

¡Gracias por tu interés en unirte a la **Cooperativa "Rebeldía Cósmica"**! Tu talento es la chispa que mantiene vivo nuestro motor de democratización artística.

## ✊ Cómo Contribuir

Toda contribución a nuestro ecosistema es un acto de rebeldía creativa y una celebración del talento colectivo. Nos regimos por el **consenso democrático de la asamblea**, garantizando que cada línea de código refleje nuestros valores de apoyo incondicional a los músicos emergentes.

1. **Reporta bugs** abriendo un "Issue". Tu voz ayuda a pulir nuestro ecosistema.
2. **Propón mejoras** en la carpeta `/sugerencias/` o abriendo un PR (Pull Request).
3. **Motores Nuevos:** Si diseñas un motor matemático nuevo, debe ir inicialmente a la carpeta `src/render/experimental/`.
4. **Asamblea de Consenso:** Toda sugerencia, PR o nueva implementación será sometida a una revisión rigurosa. El equipo de agentes de la Cooperativa (Programación, Física/IA, Arte y Gerencia) debatirá y votará la propuesta. Ningún código se integrará al programa sin el consenso democrático de nuestra asamblea.
5. **Comunicación Estricta Frontend/Backend:** Es una obligación inquebrantable que el equipo de UI/Frontend (`src/ui/`, `app.py`) y el equipo de Motores/Backend (`src/render/`) mantengan una comunicación constante durante el desarrollo. Las estructuras de datos (diccionarios, listas, nomenclaturas) deben coordinarse rigurosamente entre ambas partes para evitar que parámetros o interfaces queden desconectados (ej. evitar que la UI envíe un diccionario cuando el motor espera una lista).
6. **Documentación Pública:** TODOS los reportes de auditoría, planes de implementación y seguimientos de tareas generados por la Cooperativa o Antigravity deben guardarse SIEMPRE como archivos Markdown (`.md`) dentro de la carpeta `/reportes` en la raíz del proyecto para visibilidad absoluta de la comunidad.

## Arquitectura de Código
- `src/ai/`: Lógica de LLM, Director de IA, Autoencoders.
- `src/audio/`: Procesamiento de Fourier, RMS, Extracción de letras.
- `src/render/`: Ecuaciones de Física y renderizado.
- `src/ui/`: UI de Streamlit y Estilos CSS (Neón).

¡Bienvenidas todas las matemáticas creativas!
