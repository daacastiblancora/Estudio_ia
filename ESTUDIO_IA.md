# Estudio IA — Copiloto Operativo

Este repositorio documenta el proceso de desarrollo de un **Copiloto Operativo con IA**, construido como un microservicio Python (FastAPI) con capacidades de RAG (Retrieval-Augmented Generation).

---

## ¿Qué es este proyecto?

Un asistente de IA empresarial que:
- Responde preguntas basadas en documentos corporativos (PDFs, DOCX)
- Recuerda conversaciones previas (memoria por sesión)
- Cita las fuentes exactas (nombre de archivo y página)
- Está protegido con autenticación JWT

---

## Stack Tecnológico

| Componente | Tecnología |
|:---|:---|
| API Backend | FastAPI + Uvicorn |
| LLM | Groq — Llama 3.3 70B Versatile |
| Embeddings | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | FAISS (local) |
| Búsqueda | RAG Híbrido (Vectorial + BM25 Reranking) |
| Base de datos | SQLite + SQLModel (async) |
| Autenticación | JWT (python-jose + passlib/bcrypt) |
| Agente | LangChain AgentExecutor con Tool Calling |

---

## Arquitectura

```
Cliente (curl / Frontend)
    │
    ▼
FastAPI (puerto 8001)
    ├── /api/v1/register   → Registro de usuarios
    ├── /api/v1/login      → Autenticación JWT
    ├── /api/v1/ingest     → Subida y procesamiento de PDFs
    ├── /api/v1/chat       → Chat con el copiloto (RAG + Agente)
    ├── /api/v1/sessions   → Gestión de sesiones de conversación
    └── /api/v1/health     → Estado del servicio
         │
         ▼
    LangChain AgentExecutor
         ├── Tool: search_internal_documents (FAISS + BM25)
         └── Tool: send_email (email_tool.py)
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

### Fase 2: Copiloto Operativo (Agente)
- Transformación de RAG simple → **Agente ReAct** con `create_tool_calling_agent`
- Herramienta de búsqueda interna (`search_internal_documents`)
- Herramienta de email (`email_tool.py`)
- Sistema de guardrails (sanitización de inputs, validación de respuestas)
- Rate limiting (5 requests/minuto por IP)

### Fase 3: Autenticación y Seguridad
- Sistema de registro y login con **JWT** (HS256)
- Middleware de autenticación en todos los endpoints de chat
- Modelo de usuarios en SQLite con roles (`user`, `admin`)
- Hash de contraseñas con bcrypt

### Fase 4: Memoria Conversacional
- Persistencia de sesiones de chat en SQLite (`ChatSession`, `ChatMessage`)
- El cliente envía `session_id` para continuar conversaciones
- El historial se carga de la DB y se pasa como `chat_history` al agente
- Límite de últimos 20 mensajes para evitar overflow de tokens
- Endpoints de gestión: `GET /sessions`, `GET /sessions/{id}/messages`, `DELETE /sessions/{id}`

### Fase 5: Citaciones y Benchmark
- Refuerzo del prompt del agente para hacer las citaciones **obligatorias**
- Regex ampliado para capturar múltiples formatos de cita (`Pág.`, `Página`, `.pdf`)
- Retry logic (3 intentos) para errores intermitentes de Groq tool calling
- Documento de benchmark `preguntas_prueba.md` con preguntas reales y comparación de respuestas

### Limpieza y Organización del Repositorio
- Eliminación de archivos de debug/temp (31 archivos)
- Consolidación de la estructura: eliminación del prototipo viejo `src/app/`
- `.gitignore` actualizado para excluir `*.db`, `faiss_index/`, datos temporales

---

## Cómo ejecutar

### 1. Requisitos
```bash
pip install -r requirements.txt
```

### 2. Variables de entorno
Crear un archivo `.env` en la raíz:
```env
GROQ_API_KEY=tu_api_key_de_groq
```

### 3. Iniciar el servidor
```bash
uvicorn app.main:app --reload --port 8001
```

### 4. Ingestar documentos
```bash
# Subir un PDF
curl -X POST http://localhost:8001/api/v1/ingest -F "file=@tu_documento.pdf"

# O usar el script masivo
python bulk_ingest.py
```

### 5. Usar el copiloto
```bash
# Registrarse
curl -X POST http://localhost:8001/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email":"tumail@ejemplo.com","password":"tupassword"}'

# Chatear (usar el token recibido)
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"¿Cuál es la tarifa por retiro en cajero?"}'
```

---

## Estructura del proyecto

```
copiloto-operativo/
├── app/
│   ├── api/routes/         # Endpoints: auth, chat, health, ingest, sessions
│   ├── core/               # Config, database, guardrails, logging, security
│   ├── models/             # Schemas Pydantic y modelos SQLite
│   ├── services/           # LLM, ingestion, parser, retriever, vector_db
│   ├── tools/              # email_tool
│   └── main.py
├── documents/              # PDFs ingestados
├── tests/
├── bulk_ingest.py
├── preguntas_prueba.md     # Benchmark de preguntas y respuestas
├── project_audit.md        # GAP Analysis del proyecto
└── requirements.txt
```

---

## Lecciones aprendidas

1. **Tool Calling con Groq es intermitente** — Se necesita retry logic. El modelo a veces genera JSON de herramienta malformado.
2. **Las citaciones requieren prompt engineering explícito** — Un prompt que diga "intenta citar" no es suficiente. Debe ser "SIEMPRE cita, formato exacto: [Archivo, Pág. X]".
3. **FAISS vs Qdrant** — FAISS es más fácil de arrancar localmente (sin servidor externo), ideal para prototipos. Qdrant escala mejor en producción.
4. **El retrieval afecta más que el LLM** — La pregunta 2 del benchmark respondió mal porque el retriever encontró el chunk equivocado, no porque el LLM "inventara". La calidad del chunk y del embedding es crítica.
5. **Memoria conversacional cambia el UX completamente** — Con solo agregar `session_id` + cargar `chat_history`, el copiloto pasa de ser una herramienta de búsqueda a un asistente conversacional real.
