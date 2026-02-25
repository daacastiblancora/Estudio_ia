# Estudio IA — Copiloto Operativo

Este repositorio documenta el proceso de desarrollo de un **Copiloto Operativo con IA**, construido como un microservicio Python (FastAPI) con capacidades de RAG (Retrieval-Augmented Generation).

---

## ¿Qué es este proyecto?

Un asistente de IA empresarial que:
- Responde preguntas basadas en documentos corporativos (PDFs, DOCX, XLSX, PPTX, etc.)
- Recuerda conversaciones previas (memoria por sesión)
- Cita las fuentes exactas (nombre de archivo y página)
- Está protegido con autenticación JWT y validación de archivos

---

## Stack Tecnológico

| Componente | Tecnología |
|:---|:---|
| API Backend | FastAPI + Uvicorn |
| LLM | Groq — Llama 3.3 70B Versatile |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | **Qdrant** (Cloud-Native, vía Docker o Cloud) |
| Búsqueda | RAG Híbrido (Vectorial + BM25 Reranking) |
| Base de datos | SQLite + SQLModel (async) |
| Autenticación | JWT (python-jose + bcrypt) |
| Pipeline | RAG Chain con History (LangChain) |

---

## Arquitectura

```
Cliente (curl / Frontend)
    │
    ▼
FastAPI (puerto 8001)
    ├── /api/v1/register   → Registro de usuarios
    ├── /api/v1/login      → Autenticación JWT
    ├── /api/v1/ingest     → Subida de documentos (JWT + validación)
    ├── /api/v1/chat       → Chat con el copiloto (RAG + Memoria)
    ├── /api/v1/sessions   → Gestión de sesiones de conversación
    ├── /api/v1/health     → Estado del servicio
    ├── /api/v1/stats      → Estadísticas (admin)
    └── /api/v1/audit-log  → Logs de auditoría (admin)
         │
         ▼
    RAG Chain (Contextualize + QA)
         ├── Hybrid Retriever (Qdrant Dense + BM25 Reranking)
         └── QA System Prompt (citaciones obligatorias)
         │
         ▼
    Groq API (Llama 3.3 70B)
         │
         ▼
    SQLite (sesiones + mensajes + usuarios)
```

---

## Lo que se construyó / aprendió en este estudio

### Fase 1: MVP RAG Documental
- Pipeline de ingesta de PDFs: parsing con `pdfplumber`, chunking con `RecursiveCharacterTextSplitter`, embeddings con HuggingFace, almacenamiento en FAISS
- API de chat básica con recuperación de contexto
- Búsqueda híbrida: vectorial + BM25

### Fase 2: Migración a Qdrant (Cloud-Native)
- Migración completa de FAISS local a **Qdrant** (contenedor Docker)
- `vector_db.py` reescrito para usar `QdrantVectorStore` de `langchain_qdrant`
- Calibración R10 post-migración: **60/70 (85.7%) ✅ APROBADO** — sin pérdida de precisión

### Fase 3: Hardening y Seguridad
- Endpoint `/ingest` protegido con JWT (`get_current_active_user`)
- Validación de archivos: extensiones permitidas, tamaño máximo (10MB), detección de PDFs encriptados
- Rate limiting (30 requests/minuto por IP)
- Sistema de guardrails (sanitización de inputs, validación de respuestas)

### Fase 4: Autenticación y Roles
- Sistema de registro y login con **JWT** (HS256)
- Middleware de autenticación en todos los endpoints protegidos
- Modelo de usuarios en SQLite con roles (`user`, `admin`)
- Hash de contraseñas con bcrypt

### Fase 5: Memoria Conversacional
- Persistencia de sesiones de chat en SQLite (`ChatSession`, `ChatMessage`)
- El cliente envía `session_id` para continuar conversaciones
- El historial se carga de la DB y se pasa como `chat_history` a la cadena RAG
- Límite de últimos 20 mensajes para evitar overflow de tokens

### Fase 6: Calibración y Benchmark
- Suite automatizada de 20 preguntas (`run_calibration.py`)
- 4 categorías: Dato Exacto (BM25), Semántica (RAG), Citación, Memoria
- 10 rondas de iteración: 0% → 85.7% ✅
- Informe contractual `informe_calibracion.md`

---

## Lecciones aprendidas

1. **RAG Chain > Agent para Groq** — Groq no soporta tool-calling confiablemente. La arquitectura RAG Chain con `create_stuff_documents_chain` produce resultados más estables.
2. **Las citaciones requieren prompt engineering explícito** — Un prompt que diga "intenta citar" no es suficiente. Debe ser "SIEMPRE cita, formato exacto: [Archivo.pdf - Página X]".
3. **FAISS vs Qdrant** — FAISS es más fácil de arrancar localmente, pero Qdrant es Cloud-Native y la migración fue transparente (mismo score de calibración).
4. **El retrieval afecta más que el LLM** — La calidad del chunk y del embedding es crítica. Reducir CHUNK_SIZE de 1000→500 mejoró la precisión de 70%→80%.
5. **Memoria conversacional cambia el UX completamente** — Con solo agregar `session_id` + cargar `chat_history`, el copiloto pasa de ser una herramienta de búsqueda a un asistente conversacional real.
6. **Calibración iterativa es clave** — 10 rondas de calibración permitieron identificar y corregir fallos específicos del retriever y del prompt, alcanzando 85.7% de precisión.
