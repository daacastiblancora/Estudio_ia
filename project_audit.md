# Auditoría del Proyecto vs Requisitos

A continuación se detalla el estado actual del proyecto **Copiloto Core** frente a los requisitos entregables definidos.

## 🟢 Cumplimiento Total (MVP IA Documental)

### 1. Resumen Ejecutivo & Stack Tecnológico
*   **Microservicio Python (FastAPI):** ✅ Implementado en `app/main.py`. Clases modulares y Pydantic schemas.
*   **Motor RAG Híbrido:** ✅ Implementado en `app/services/retriever.py` (Búsqueda Vectorial + BM25 Reranking).
*   **Pipeline de Ingesta:** ✅ Implementado en `app/services/ingestion.py` y `app/services/parser.py`. Script automático `bulk_ingest.py`.
*   **Sistema de Citación:** ✅ Implementado. Sistema de citación página precisa.
*   **Integración Groq:** ✅ Usando modelo `llama-3.3-70b-versatile`.

### 2. Componentes Técnicos
*   **Pipeline ETL:** ✅ Lectura robusta de PDF/DOCX.
*   **API de Inteligencia:** ✅ Endpoints `/chat`, `/ingest`.

## 🟡 Desviaciones Justificadas

*   **Base de Datos Vectorial:** FAISS Local en lugar de Qdrant Cloud (Justificado por Firewall/Red).

---

## 🔍 GAP ANALYSIS: Requisitos "Copiloto Operativo"
*Evaluación de brecha entre el sistema actual y la nueva definición de "Asistente que ejecuta acciones".*

### 1. Capacidades de Agente (Acciones)
*   **Requisito:** "Ejecuta acciones: crea tareas, redacta correos... Workflows (Jira, CRM)."
*   **Estado:** 🔴 **No Implementado (Backend Pasivo)**
*   **Brecha:** El backend actual es "Read-Only". Solo lee documentos y responde. No tiene capacidad de "Tool Calling" ni permisos para escribir en sistemas externos.
*   **Necesario:** Transformar el RAG en un **Agente ReAct** o usar **LangChain Tools** para conectar con APIs externas (Gmail API, Jira API).

### 2. Generación de Contenido
*   **Requisito:** "Redacta correos, resume reuniones, genera minutas, arma procedimientos."
*   **Estado:** 🟢 **Cumple (Nativo LLM)**
*   **Comentario:** El modelo actual (Llama 3.3) YA puede hacer esto si se le pide en el prompt.
*   **Mejora Sugerida:** Crear endpoints específicos o Templates de Prompt para estandarizar el formato de salida (ej: `/generate/email`, `/generate/minutes`).

### 3. Conectores de Fuentes (Data Sources)
*   **Requisito:** "Drive, Sharepoint, Notion, Confluence, Tickets, CRM."
*   **Estado:** 🔴 **No Implementado (Solo Local)**
*   **Brecha:** Solo ingesta archivos locales. No hay conexión a nubes.
*   **Necesario:** Implementar conectores OAuth2 y módulos de `LlamaIndex` o `LangChain` específicos para estas plataformas.

### 4. Seguridad y Roles
*   **Requisito:** "Acceso por área/rol, logs, auditoría. Roles básicos."
*   **Estado:** 🔴 **No Implementado (API Abierta)**
*   **Brecha:** La API es pública para cualquiera que llegue al puerto. No distingue usuarios ni áreas.
*   **Necesario:** Implementar Middleware de Autenticación (JWT), tabla de Usuarios, y Lógica de RLS (Row Level Security) en el vector store (filtrar documentos por rol).

### 5. Memoria y Contexto
*   **Requisito:** "Que recuerde la pregunta anterior."
*   **Estado:** � **Implementado (20/02/2026)**
*   **Detalle:** Sesiones persistentes en SQLite. El cliente envía `session_id` para continuar conversaciones. Historial se carga y pasa al agente como `chat_history` (últimos 20 mensajes).
*   **Endpoints:** `GET /sessions`, `GET /sessions/{id}/messages`, `DELETE /sessions/{id}`.

### 6. Auditoría Detallada
*   **Requisito:** "Auditoría: quién preguntó, qué respondió, qué fuentes usó."
*   **Estado:** 🟡 **Parcial (Logs de Texto)**
*   **Brecha:** Existen logs técnicos en consola, pero no hay una base de datos consultable de interacciones.
*   **Necesario:** Tabla `chat_logs` en base de datos persistente.

---

## Resumen de Esfuerzo para "Copiloto Operativo"

Para evolucionar del **MVP Documental** actual a un **Copiloto Operativo**, se requiere una **Fase 2 de Backend** enfocada en:
1.  **Agencia:** Habilitar "Tools" en el LLM.
2.  **Seguridad:** Capa de Auth y Roles.
3.  **Integraciones:** Conectores a APIs de terceros.

## 📝 Estado Actual (20/02/2026)

### ✅ Logros Destacados
*   **Recuperación de Contexto (Context Retrieval):** El sistema RAG está funcionando correctamente.
*   **Agente Operativo:** Se ha configurado el agente "Copiloto Operativo" con capacidad de usar herramientas.
*   **Memoria Conversacional:** El copiloto ahora recuerda conversaciones previas del mismo usuario (`session_id` + historial en DB).
*   **Gestión de Sesiones:** Endpoints para listar, consultar y eliminar sesiones de chat.
*   **Limpieza de Repo:** Eliminados scripts de debug/temp. Estructura consolidada.

### ⚠️ Puntos de Atención
*   **Precisión de Citación:** Ocasionalmente falla en el formato estricto `[Archivo.pdf, Pág. X]`.
    *   *Estado:* Se ha priorizado la estabilidad de la respuesta sobre la perfección del formato de cita.
*   **Seguridad:** `SECRET_KEY` aún usa `GROQ_API_KEY`. Separar en próxima iteración.
