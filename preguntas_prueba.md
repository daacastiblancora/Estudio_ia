# Preguntas de Prueba — Copiloto Operativo

Documento de referencia: `TARIFAS 11 MAYO.pdf`
Fecha de test: 20/02/2026

---

## Pregunta 1: Chequera de 30 cheques

**Pregunta:**
> ¿Cuánto cuesta solicitar una chequera de 30 cheques para una persona natural?

### Respuesta esperada (Gemini / Validación manual)
- **Valor:** $275.700
- **Fuente:** TARIFAS 11 MAYO.pdf, Página 2 (Tabla de "Chequeras")

### Respuesta del Copiloto (Agente RAG)

**Pre-fix (sin refuerzo de citaciones):**
> El costo de solicitar una chequera de 30 cheques para una persona natural es de $275.700, según la información proporcionada en el documento [TARIFAS PRODUCTOS Y SERVICIOS BANCARIOS A partir del 11 de Mayo de 2025, Pág. 1].
- ✅ **Dato correcto:** $275.700
- ⚠️ **Página incorrecta:** Dijo Pág. 1, debería ser Pág. 2
- ✅ **Citación:** Sí incluyó referencia

**Post-fix (con refuerzo de citaciones):**
> El costo de solicitar una chequera de 30 cheques para una persona natural es de $275.700 [TARIFAS PRODUCTOS Y SERVICIOS BANCARIOS, Pág. 2].
- ✅ **Dato correcto:** $275.700
- ✅ **Página correcta:** Pág. 2
- ✅ **Citación:** Formato limpio y correcto

| Criterio | Esperado | Copiloto | Match |
| :--- | :--- | :--- | :--- |
| Valor | $275.700 | $275.700 | ✅ |
| Página | 2 | 2 | ✅ |
| Citación | Sí | Sí | ✅ |

---

## Resumen de Cambios Aplicados

Para mejorar las citaciones se hicieron 2 cambios:

1. **`llm.py`** — Prompt reforzado: las citaciones pasaron de "intenta usar" a "SIEMPRE cita tus fuentes"
2. **`chat.py`** — Regex ampliado: ahora captura `Pág.`, `Página`, y formatos alternativos
