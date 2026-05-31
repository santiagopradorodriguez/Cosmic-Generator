# REGLA OBLIGATORIA: COMUNICACIÓN FRONTEND/BACKEND

Es una obligación inquebrantable que el equipo de UI/Frontend (`src/ui/`, `app.py`) y el equipo de Motores/Backend (`src/render/`) mantengan una comunicación constante durante el desarrollo.

1. **Coordinación de Estructuras de Datos:** Las estructuras de datos (diccionarios, listas, nomenclaturas) deben coordinarse rigurosamente entre ambas partes.
2. **Nomenclaturas Compatibles:** Si el frontend envía una configuración, debe usar exactamente los mismos "strings" o "keys" que el motor matemático espera (ej. enviar `['GS', 'KS']` y no `{'gray_scott': True, 'ks': False}`).
3. **Validación de Pasos de Argumentos:** Siempre validar el paso de parámetros desde `app.py` hasta la llamada interna del motor de renderizado. No asumir conversiones automáticas.

Cualquier PR o código generado que no respete la sincronización de tipos entre frontend y backend será automáticamente penalizado por la Asamblea.
