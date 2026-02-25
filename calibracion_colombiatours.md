# Calibración ColombiaTours — Set de 20 Preguntas de Control

**Objetivo:** Validar que el Copiloto Operativo responde correctamente con datos del corpus de colombiatours.travel, cita las fuentes adecuadas, y mantiene la memoria conversacional.

**Criterio de aprobación:** ≥ 85% de aciertos (17/20).

---

## A. Búsqueda por Dato Exacto (BM25 Test)

| # | Pregunta | Respuesta Esperada | PDF Fuente |
|---|---|---|---|
| 1 | ¿Cuánto cuesta el tour "Colombia Corazón" de 15 días? | $3.000 USD (o $13.950.000 COP) | 01_colombia_corazon_15dias.pdf |
| 2 | ¿Cuántos días dura el plan "Colombia Armonía"? | 8 días | 04_colombia_armonia_8dias.pdf |
| 3 | ¿Cuál es el precio del Plan Eje Cafetero Extremo? | $3.720.000 COP | 07_eje_cafetero_extremo.pdf |
| 4 | ¿Qué aerolíneas vuelan de México a Colombia? | Aeroméxico, Avianca, Copa Airlines, Interjet, VivaAerobus | 15_homepage_faq.pdf |
| 5 | ¿Cuál es el requisito de vigencia del pasaporte para entrar a Colombia? | Al menos 6 meses de vigencia | 13_requisitos_viaje_espana.pdf |

## B. Búsqueda Semántica (RAG Test)

| # | Pregunta | Respuesta Esperada (resumen) | PDF Fuente |
|---|---|---|---|
| 6 | ¿Qué actividades turísticas puedo hacer en Cartagena de Indias? | Ciudad Amurallada, Castillo San Felipe, playas, Islas del Rosario, gastronomía | 15_homepage_faq.pdf |
| 7 | ¿Qué se incluye en el paquete Colombia Corazón? | Vuelos internos, traslados, alojamiento 14 noches (3-5★), desayunos, guías locales, asistencia médica | 01_colombia_corazon_15dias.pdf |
| 8 | ¿Cuál es la mejor época para visitar Caño Cristales? | Junio a noviembre (temporada de lluvias moderadas) | 10_guia_cano_cristales.pdf |
| 9 | ¿Dónde puedo ver ballenas en Colombia? | Costa Pacífica (Bahía Málaga, Nuquí, Buenaventura) | 11_guia_ballenas.pdf |
| 10 | ¿Qué destinos puedo visitar en 8 días? | Bogotá, Cartagena, Medellín, Guatapé, Eje Cafetero (itinerario día-a-día) | 15_homepage_faq.pdf o 04_colombia_armonia_8dias.pdf |

## C. Citación Correcta (Test de Fuentes)

| # | Pregunta | Debe citar | Dato clave |
|---|---|---|---|
| 11 | ¿Cuáles son las normas ambientales para visitar Caño Cristales? | 10_guia_cano_cristales.pdf | No usar protector solar, no tocar algas |
| 12 | ¿Qué es el formulario Check-Mig y cuándo se debe llenar? | 13_requisitos_viaje_espana.pdf o 15_homepage_faq.pdf | 72 horas antes del viaje o máximo 3 horas |
| 13 | ¿Qué incluye y qué NO incluye el tour Colombia Corazón? | 01_colombia_corazon_15dias.pdf | No incluye: vuelos internacionales |
| 14 | ¿Cuánto cuesta un vuelo México-Bogotá con Aeroméxico? | 15_homepage_faq.pdf | $2,500 a $4,500 MXN |
| 15 | ¿Qué ciudades se visitan en el plan Ritmo y Sabor? | 03_colombia_ritmo_sabor_11dias.pdf | Cali, Medellín, Cartagena |

## D. Memoria Conversacional (Test Multi-Turno)

| # | Turno 1 | Turno 2 | Respuesta esperada T2 |
|---|---|---|---|
| 16 | ¿Qué tours tienen para 4 días? | ¿Cuánto cuesta el más barato de esos? | $3.380.550 COP (Eje Cafetero Parques) |
| 17 | ¿Quién es Ana Echavarria? | ¿En qué se especializa? | (Perfil de travel planner) |
| 18 | Quiero ir a Medellín | ¿Qué paquetes incluyen esa ciudad? | Colombia Corazón, Esencia, Ritmo y Sabor, Armonía, 6 días Medellín-Cartagena |
| 19 | ¿Cómo llego desde México? | ¿Cuál es la aerolínea más barata? | VivaAerobus ($2,500-$5,000 MXN) o Aeroméxico ($2,500-$4,500 MXN) |
| 20 | ¿Qué requisitos necesito desde España? | ¿Necesito visa? | No, para estancias menores a 90 días no se necesita visa |
