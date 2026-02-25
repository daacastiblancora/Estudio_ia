# Informe de Calibración — Copiloto Operativo

**Fecha:** 2026-02-25 11:37
**Corpus:** 20 PDFs de colombiatours.travel
**Resultado:** 60/70 (85.7%)
**Estado:** ✅ APROBADO

---

## Resultados por Pregunta

| # | Categoría | Pregunta | Valores | Citación | Score |
|---|---|---|---|---|---|
| 1 | A. Dato Exacto (BM25) | ¿Cuánto cuesta el tour 'Colombia Corazón' de 15 días? | 4/4 | ✅ | ✅ 3/3 |
| 2 | A. Dato Exacto (BM25) | ¿Cuántos días dura el plan 'Colombia Armonía'? | 1/2 | ✅ | ⚠️ 2/3 |
| 3 | A. Dato Exacto (BM25) | ¿Cuál es el precio del Plan Eje Cafetero Extremo? | 2/2 | ✅ | ✅ 3/3 |
| 4 | A. Dato Exacto (BM25) | ¿Qué aerolíneas vuelan de México a Colombia? | 3/3 | ✅ | ✅ 3/3 |
| 5 | A. Dato Exacto (BM25) | ¿Cuál es el requisito de vigencia del pasaporte para entrar ... | 2/3 | ✅ | ⚠️ 2/3 |
| 6 | B. Semántica (RAG) | ¿Qué actividades turísticas puedo hacer en Cartagena de Indi... | 3/3 | ✅ | ✅ 3/3 |
| 7 | B. Semántica (RAG) | Según el tour Colombia Corazón de 15 días, ¿qué incluye el p... | 1/3 | ✅ | ❌ 1/3 |
| 8 | B. Semántica (RAG) | ¿Cuál es la mejor época para visitar Caño Cristales? | 2/2 | ✅ | ✅ 3/3 |
| 9 | B. Semántica (RAG) | ¿Dónde puedo ver ballenas en Colombia? | 4/4 | ✅ | ✅ 3/3 |
| 10 | B. Semántica (RAG) | ¿Qué destinos puedo visitar en 8 días en Colombia? | 3/3 | ✅ | ✅ 3/3 |
| 11 | C. Citación | ¿Cuáles son las normas ambientales para visitar Caño Cristal... | 2/2 | ✅ | ✅ 3/3 |
| 12 | C. Citación | ¿Qué es el formulario Check-Mig y cuándo se debe llenar? | 3/3 | ✅ | ✅ 3/3 |
| 13 | C. Citación | ¿Qué incluye y qué NO incluye el tour Colombia Corazón? | 1/2 | ✅ | ⚠️ 2/3 |
| 14 | C. Citación | ¿Cuánto cuesta un vuelo de México a Bogotá con Aeroméxico? | 2/3 | ✅ | ⚠️ 2/3 |
| 15 | C. Citación | ¿Qué ciudades se visitan en el plan Ritmo y Sabor? | 3/3 | ✅ | ✅ 3/3 |
| 16 | D. Memoria | ¿Qué tours tienen disponibles para 4 días? | 1/1 | ✅ | ✅ 4/5 |
| 17 | D. Memoria | ¿Quién es Ana Echavarria? | 3/3 | ✅ | ✅ 5/5 |
| 18 | D. Memoria | Quiero ir a Medellín, ¿qué puedo hacer allá? | 1/1 | ✅ | ✅ 5/5 |
| 19 | D. Memoria | ¿Cómo llego a Colombia desde México? | 1/2 | ✅ | ⚠️ 3/5 |
| 20 | D. Memoria | ¿Qué requisitos necesito para viajar a Colombia desde España... | 2/2 | ✅ | ✅ 4/5 |

---

## Análisis por Categoría

- **A. Dato Exacto (BM25)**: 13/15 (87%)
- **B. Semántica (RAG)**: 13/15 (87%)
- **C. Citación**: 13/15 (87%)
- **D. Memoria**: 21/25 (84%)

---

## Detalle de Respuestas

### Pregunta 1: ¿Cuánto cuesta el tour 'Colombia Corazón' de 15 días?

**Respuesta IA:**
> El costo del tour 'Colombia Corazón' de 15 días es de **$3.000 USD** por pasajero (en acomodación doble) o **$13.950.000 COP** [01_colombia_corazon_15dias.pdf - Página 1]. Este tour incluye destinos como Cartagena de Indias, Cali, Medellín y Bogotá, y ofrece una variedad de actividades y experiencias culturales y gastronómicas. 

Algunos de los lugares y actividades que se incluyen en este tour son:
* **Cartagena**: City Tour (Torre del Reloj, Castillo de San Felipe, Monumento de los Zapatos Vie

- Valores encontrados: 3.000, USD, 13.950.000, COP
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 2: ¿Cuántos días dura el plan 'Colombia Armonía'?

**Respuesta IA:**
> El plan 'Colombia Armonía' dura **8 días** [14_paquetes_viajes.pdf - Página 1].

- Valores encontrados: 8 días
- Valores faltantes: 8 dias
- ¿Citó fuente?: Sí

---

### Pregunta 3: ¿Cuál es el precio del Plan Eje Cafetero Extremo?

**Respuesta IA:**
> El precio del **Plan Eje Cafetero Extremo** es de **$3.720.000 COP** (pesos colombianos) [07_eje_cafetero_extremo.pdf - Página 1]. Este tour tiene una duración de **4 días y 3 noches** y ofrece actividades como parapente, rafting, canopy, caminatas ecológicas y visita a fincas cafeteras en el Eje Cafetero (Armenia, Salento, Valle de Cocora) [07_eje_cafetero_extremo.pdf - Página 1].

- Valores encontrados: 3.720.000, COP
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 4: ¿Qué aerolíneas vuelan de México a Colombia?

**Respuesta IA:**
> Las aerolíneas que vuelan de México a Colombia son:
* **Aeroméxico**: Vuelos directos Ciudad de México a Bogotá y Medellín. Precio promedio ida y vuelta clase económica: $2,500 a $4,500 MXN [13 Requisitos Viaje Espana - Página 1].
* **Avianca**: Vuelos directos Ciudad de México a Bogotá, Medellín y Cali. Precio promedio: $3,000 a $6,000 MXN [13 Requisitos Viaje Espana - Página 1].
* **Copa Airlines**: Vuelos con escala en Panamá. Precio promedio: $3,500 a $7,000 MXN [13 Requisitos Viaje Espana -

- Valores encontrados: Aeroméxico, Avianca, Copa
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 5: ¿Cuál es el requisito de vigencia del pasaporte para entrar a Colombia?

**Respuesta IA:**
> El requisito de vigencia del pasaporte para entrar a Colombia es que debe tener una vigencia de al menos **seis (6) meses** a partir de la fecha de ingreso a Colombia [13 Requisitos Viaje Espana - Página 1]. Esto significa que el pasaporte debe ser válido por al menos 6 meses después de la fecha de entrada planeada en el país.

- Valores encontrados: 6 meses, seis (6)
- Valores faltantes: seis meses
- ¿Citó fuente?: Sí

---

### Pregunta 6: ¿Qué actividades turísticas puedo hacer en Cartagena de Indias?

**Respuesta IA:**
> En Cartagena de Indias, puedes realizar varias actividades turísticas, como:

* **City Tour**: Visita la Torre del Reloj, el Castillo de San Felipe y el Monumento de los Zapatos Viejos [01_colombia_corazon_15dias.pdf - Página 1].
* **Visita al Museo del Chocolate** [01_colombia_corazon_15dias.pdf - Página 1].
* **Excursión a las Islas del Rosario**, donde puedes practicar **snorkel** y **buceo** [15_homepage_faq.pdf - Página 2] y [01_colombia_corazon_15dias.pdf - Página 1].
* **Noche Blanca** [0

- Valores encontrados: Castillo, San Felipe, Islas del Rosario
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 7: Según el tour Colombia Corazón de 15 días, ¿qué incluye el paquete?

**Respuesta IA:**
> Según el tour Colombia Corazón de 15 días, el paquete incluye:

* **Vuelos internos** [01_colombia_corazon_15dias.pdf - Página 1]
* **Traslados en vehículos autorizados de turismo** [01_colombia_corazon_15dias.pdf - Página 1]

Además, el itinerario del tour incluye visitas a los siguientes lugares:

* **Cartagena**: City Tour (Torre del Reloj, Castillo de San Felipe, Monumento de los Zapatos Viejos), Museo del Chocolate, Islas del Rosario, Noche Blanca [01_colombia_corazon_15dias.pdf - Página 1]

- Valores encontrados: vuelos
- Valores faltantes: alojamiento, desayuno
- ¿Citó fuente?: Sí

---

### Pregunta 8: ¿Cuál es la mejor época para visitar Caño Cristales?

**Respuesta IA:**
> La mejor época para visitar Caño Cristales es de **junio a noviembre**, durante la temporada de lluvias moderadas, cuando las algas están en su máximo esplendor [10_Guia_Cano_Cristales - Página 1]. Es importante tener en cuenta que el río cierra a visitantes entre **diciembre y mayo** para proteger el ecosistema [10_Guia_Cano_Cristales - Página 1].

- Valores encontrados: junio, noviembre
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 9: ¿Dónde puedo ver ballenas en Colombia?

**Respuesta IA:**
> En Colombia, puedes ver ballenas en las siguientes ubicaciones principales:

* **Bahía Málaga (Valle del Cauca)**: Es el principal punto de avistamiento, cercano a Buenaventura [11 Guia Ballenas - Página 1].
* **Nuquí (Chocó)**: Ubicado en la costa pacífica, se puede acceder por avión desde Medellín [11 Guia Ballenas - Página 1].
* **Bahía Solano (Chocó)**: Se encuentra en la costa pacífica norte [11 Guia Ballenas - Página 1].
* **Tumaco (Nariño)**: Ubicado en la costa pacífica sur [11 Guia Ball

- Valores encontrados: Pacífico, Nuquí, Bahía Málaga, Buenaventura
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 10: ¿Qué destinos puedo visitar en 8 días en Colombia?

**Respuesta IA:**
> En 8 días, puedes visitar varios destinos en Colombia. A continuación, te presento algunas opciones:

* **Colombia Armonía**: Puedes visitar el Eje Cafetero y Medellín en 8 días y 7 noches, con un precio de $6.975.000 COP ($1.500 USD) por pasajero [04_colombia_armonia_8dias.pdf - Página 1].
* **Itinerario en 8 días**: Otra opción es visitar los siguientes destinos en 8 días:
 + Día 1: Llegada a Bogotá, explorar La Candelaria, Plaza de Bolívar, Museo del Oro, Museo Botero.
 + Día 2: Villa de Leyv

- Valores encontrados: Bogotá, Medellín, Cartagena
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 11: ¿Cuáles son las normas ambientales para visitar Caño Cristales?

**Respuesta IA:**
> Las normas ambientales para visitar Caño Cristales son las siguientes:
* **No usar protector solar, bloqueador ni repelente con químicos**, ya que dañan las algas [10 Guia Cano Cristales - Página 1].
* **No tocar ni pisar las algas rojas (Macarenia clavigera)** [10 Guia Cano Cristales - Página 1].
* **No arrojar basura** [10 Guia Cano Cristales - Página 1].
* **No extraer fauna ni flora** [10 Guia Cano Cristales - Página 1].
* **Solo se permite el acceso con guías autorizados** [10 Guia Cano Cri

- Valores encontrados: protector solar, alga
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 12: ¿Qué es el formulario Check-Mig y cuándo se debe llenar?

**Respuesta IA:**
> El formulario Check-Mig es un requisito para todos los viajeros (colombianos o extranjeros) que ingresan a Colombia [13_requisitos_viaje_espana.pdf - Página 1]. 

Este formulario **debe completarse** en un plazo de **72 horas antes del viaje** o como máximo **3 horas antes de la salida** [13_requisitos_viaje_espana.pdf - Página 1] y [15_homepage_faq.pdf - Página 2]. 

El documento se entrega en las áreas de migración de los aeropuertos internacionales [13_requisitos_viaje_espana.pdf - Página 1].

- Valores encontrados: 72 horas, migra, Check-Mig
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 13: ¿Qué incluye y qué NO incluye el tour Colombia Corazón?

**Respuesta IA:**
> El tour **Colombia Corazón** incluye lo siguiente:
* Vuelos internos [01_colombia_corazon_15dias.pdf - Página 1]
* Traslados en vehículos autorizados de turismo [01_colombia_corazon_15dias.pdf - Página 1]

No incluye:
* No se especifican otros servicios o actividades que no estén incluidas, pero se menciona que el precio es por pasajero en acomodación doble [01_colombia_corazon_15dias.pdf - Página 1]

Es importante tener en cuenta que el documento proporcionado no menciona explícitamente qué otr

- Valores encontrados: No incluye
- Valores faltantes: vuelos internacionales
- ¿Citó fuente?: Sí

---

### Pregunta 14: ¿Cuánto cuesta un vuelo de México a Bogotá con Aeroméxico?

**Respuesta IA:**
> El costo de un vuelo de México a Bogotá con Aeroméxico es de $2,500 a $4,500 MXN en clase económica [AEROLÍNEAS QUE VUELAN DE MÉXICO A COLOMBIA - Página no especificada]. 

Es importante tener en cuenta que este es un precio promedio y puede variar dependiendo de la temporada, la disponibilidad y otros factores. Te recomiendo verificar con Aeroméxico o un agente de viajes para obtener el precio más actualizado y preciso.

- Valores encontrados: 2,500, MXN
- Valores faltantes: 2.500
- ¿Citó fuente?: Sí

---

### Pregunta 15: ¿Qué ciudades se visitan en el plan Ritmo y Sabor?

**Respuesta IA:**
> En el plan **Colombia Ritmo y Sabor**, se visitan tres ciudades principales de Colombia: 
* **Cali** (la capital mundial de la salsa) 
* **Medellín** (la ciudad de la eterna primavera) 
* **Cartagena** (ciudad amurallada Patrimonio de la Humanidad) [03_colombia_ritmo_sabor_11dias.pdf - Página 1].

- Valores encontrados: Cali, Medellín, Cartagena
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

---

### Pregunta 16: ¿Qué tours tienen disponibles para 4 días?

**Respuesta IA:**
> Tenemos los siguientes tours disponibles para 4 días:
* **Plan Eje Cafetero Extremo**: $3.720.000 COP, 4 días y 3 noches, incluye actividades como parapente, rafting, canopy, caminatas ecológicas y visita a fincas cafeteras [07_eje_cafetero_extremo.pdf - Página 1].
* **Plan Eje Cafetero Parques Temáticos**: $3.380.550 COP, 4 días y 3 noches, incluye visitas a parques como el Parque Nacional del Café, Parque de la Cultura Cafetera y Panaca [08_eje_cafetero_parques.pdf - Página 1].
* **Tour Eje Ca

- Valores encontrados: Eje Cafetero
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

**Followup:** El tour más barato de 4 días es el **Plan Eje Cafetero Parques Temáticos** y el **Tour Eje Cafetero Disfruta**, ambos con un precio de $3.380.550 COP [09_eje_cafetero_disfruta.pdf - Página 1].
- Valores followup encontrados: 3.380

---

### Pregunta 17: ¿Quién es Ana Echavarria?

**Respuesta IA:**
> **Ana Echavarría** es una **Travel Planner** en **ColombiaTours.Travel**. Se especializa en diseñar experiencias personalizadas de viaje a Colombia, ayudando a los viajeros a planificar itinerarios a medida con su amplio conocimiento de los destinos colombianos [16_travel_planner_ana.pdf - Página 1]. También está disponible para asesoría personalizada a través de **WhatsApp** [16_travel_planner_ana.pdf - Página 1].

- Valores encontrados: travel planner, planner, Travel Planner
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

**Followup:** **Ana Echavarría** se especializa en diseñar **experiencias personalizadas de viaje a Colombia**, ayudando a los viajeros a planificar **itinerarios a medida** con su amplio conocimiento de los destinos colombianos [16_travel_planner_ana.pdf - Página 1].
- Valores followup encontrados: especiali

---

### Pregunta 18: Quiero ir a Medellín, ¿qué puedo hacer allá?

**Respuesta IA:**
> Medellín es una ciudad con una gran variedad de actividades y lugares para visitar. Algunas de las opciones son:

* **Visitar la Plaza Botero**: Un lugar emblemático de la ciudad, donde podrás encontrar obras del famoso artista Fernando Botero [15_homepage_faq.pdf - Página 2].
* **Parque Explora**: Un parque que ofrece una variedad de actividades, como un acuario, un planetario y un museo de ciencias [15_homepage_faq.pdf - Página 2].
* **Metrocable**: Un sistema de transporte por cable que te pe

- Valores encontrados: Medellín
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

**Followup:** Medellín es una ciudad que se incluye en varios paquetes de viaje ofrecidos por ColombiaTours.Travel. A continuación, te presento algunos de los paquetes que incluyen Medellín:

* **Colombia Corazón**: 15 días, incluye Medellín, Cartagena, Cali y Bogotá, con un precio de $13.950.000 COP ($3.000 USD)
- Valores followup encontrados: Colombia

---

### Pregunta 19: ¿Cómo llego a Colombia desde México?

**Respuesta IA:**
> Para llegar a Colombia desde México, hay varias opciones de vuelos y aerolíneas que ofrecen servicios directos o con escalas. A continuación, te proporciono algunos detalles sobre cómo llegar a Colombia desde México:

* **Aerolíneas que vuelan de México a Colombia:** 
 + Aeroméxico: Ofrece vuelos directos desde la Ciudad de México a Bogotá y Medellín. El precio promedio ida y vuelta no está especificado en el contexto proporcionado [13 Requisitos Viaje Espana].
* **Requisitos para viajar a Colom

- Valores encontrados: Aeroméxico
- Valores faltantes: Avianca
- ¿Citó fuente?: Sí

**Followup:** Según la información proporcionada, la aerolínea más barata para viajar de México a Colombia es Aeroméxico, con un precio promedio ida y vuelta de $2,500 a $4,500 MXN en clase económica [13 Requisitos Viaje Espana]. Sin embargo, también se menciona que VivaAerobus ofrece vuelos directos de Monterrey
- Valores followup encontrados: 2,500, VivaAerobus, Viva

---

### Pregunta 20: ¿Qué requisitos necesito para viajar a Colombia desde España?

**Respuesta IA:**
> Para viajar a Colombia desde España, necesitas cumplir con los siguientes requisitos:

* **PASAPORTE VÁLIDO**: Debe tener una vigencia de al menos seis (6) meses a partir de la fecha de ingreso a Colombia [13_Requisitos_Viaje_Espana - Página 1].
* **VISA**: Los ciudadanos españoles NO necesitan visa para ingresar a Colombia como turistas si su estancia es menor a 90 días [13_Requisitos_Viaje_Espana - Página 1].
* **TIQUETE DE REGRESO**: Es posible que soliciten un tiquete de avión o transporte q

- Valores encontrados: pasaporte, visa
- Valores faltantes: Ninguno
- ¿Citó fuente?: Sí

**Followup:** No, como ciudadano español, **NO necesitas visa** para ingresar a Colombia como turista si tu estancia es menor a 90 días [13_Requisitos_Viaje_Espana - Página 1]. Sin embargo, es importante cumplir con los demás requisitos, como tener un pasaporte válido con una vigencia de al menos seis meses, un t
- Valores followup encontrados: no necesit, 90 días, no

---
