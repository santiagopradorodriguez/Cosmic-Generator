# 🔬 Laboratorio de Física: Registros Académicos

## 🌌 Fluidos Cuánticos: Ecuación de Gross-Pitaevskii (GPE)

**Fecha de Integración**: 05 de Junio 2026
**Investigador Principal**: Antigravity (Sub-Agente: Físico Matemático)

### Descripción Teórica
La ecuación de Gross-Pitaevskii (GPE) describe el estado base de un sistema cuántico de bosones interactuando, particularmente los Condensados de Bose-Einstein (BEC). Se considera una ecuación de Schrödinger no lineal.

La forma matemática implementada es:
$i \hbar \frac{\partial \psi}{\partial t} = \left( -\frac{\hbar^2}{2m}\nabla^2 + V(\mathbf{r}) + g|\psi|^2 \right) \psi$

Donde:
*   $\psi(\mathbf{r}, t)$ es la función de onda macroscópica compleja.
*   $V(\mathbf{r})$ es el potencial externo que confina los átomos.
*   $g$ representa las interacciones de dos cuerpos.

### Implementación Numérica Computacional (`nucleo_visual.py`)
Dado que la resolución de ecuaciones diferenciales parciales complejas mediante Euler explícito es incondicionalmente inestable, hemos introducido un **amortiguamiento disipativo** (difusión acoplada) que estabiliza el sistema en el límite del caos numérico.

Dividimos $\psi = u + iv$ y resolvemos un sistema acoplado para las partes real e imaginaria:

```python
du = -0.5 * lap_v + V * v + g * (u^2 + v^2) * v + damping * lap_u
dv =  0.5 * lap_u - V * u - g * (u^2 + v^2) * u + damping * lap_v
```

### Comportamiento Estético
A nivel VJ/Audiovisual, este motor genera estéticas fluidas extremadamente fantasmales. Produce "vórtices topológicos" que bailan e interfieren entre sí. Las ondas de sonido de la batería inyectan masa local causando que el tejido cuántico colapse y se expanda orgánicamente simulando una "luz líquida" cósmica.
