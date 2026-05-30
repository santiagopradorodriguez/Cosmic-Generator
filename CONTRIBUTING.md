# Guía de Contribución para Cosmic Generator

¡Gracias por tu interés en contribuir al "Generador de videos musicales de Rebeldía Cósmica"!

## Cómo Contribuir

Toda contribución a la Cooperativa es una celebración del talento colectivo. Nos regimos por el **consenso democrático de la asamblea**, garantizando que cada línea de código refleje nuestros valores de democratización artística para los músicos emergentes.

1. **Reporta bugs** abriendo un "Issue". Tu voz ayuda a pulir nuestro ecosistema.
2. **Propón mejoras** en la carpeta `/sugerencias/` o abriendo un PR (Pull Request).
3. **Motores Nuevos:** Si diseñas un motor matemático nuevo, debe ir inicialmente a la carpeta `src/render/experimental/`.
4. **Asamblea de Consenso:** Toda sugerencia, PR o nueva implementación será sometida a una revisión rigurosa. El equipo de agentes de la Cooperativa (Programación, Física/IA, Arte y Gerencia) debatirá y votará la propuesta. Ningún código se integrará al programa sin el consenso democrático de nuestra asamblea.

## Arquitectura de Código
- `src/ai/`: Lógica de LLM, Director de IA, Autoencoders.
- `src/audio/`: Procesamiento de Fourier, RMS, Extracción de letras.
- `src/render/`: Ecuaciones de Física y renderizado.
- `src/ui/`: UI de Streamlit y Estilos CSS (Neón).

¡Bienvenidas todas las matemáticas creativas!
