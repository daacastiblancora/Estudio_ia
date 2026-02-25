# Copiloto Core — Backend AI Microservice

> **Manual de Despliegue para Equipos de Integración (Frontend/Backend)**

Microservicio de Inteligencia Artificial (RAG) para procesar documentos y responder preguntas con citas a fuentes.

## 📋 Arquitectura Técnica

| Componente | Tecnología |
|---|---|
| **API** | FastAPI (REST) |
| **LLM** | Llama 3.3 70B (vía Groq API) |
| **Vector Store** | FAISS (Local) — preparado para migración a Qdrant Cloud |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` (Multilingüe) |
| **Retrieval** | Híbrido: FAISS + BM25 Reranking (`k=6`) |
| **Autenticación** | JWT (OAuth2 Bearer) — Register/Login con RBAC |
| **Rate Limiting** | SlowAPI (30 req/min en `/chat`) |
| **Memoria** | Sesiones conversacionales persistentes en SQLite |
| **Guardrails** | Anti-alucinación + anti-injection |
| **Chunks** | 500 chars, overlap 150, separadores semánticos |

### Diagrama de Flujo RAG

```
Usuario → /chat → JWT Auth → Rate Limit → Contextualize Question (reformula con historial)
    → Hybrid Retriever (FAISS + BM25, k=6) → QA Chain (Llama 3.3) → Citación [PDF - Pág X]
    → Guardrails (anti-alucinación) → Response + Sources
```

---

## 🚀 Pre-requisitos

1. **Python 3.10+**
2. **API Key de Groq:** Crear en [console.groq.com](https://console.groq.com) (plan Dev recomendado: 1M tokens/día)
3. **Git**

---

## ⚙️ Instalación

### 1. Clonar y preparar entorno
```bash
git clone <URL_DEL_REPO>
cd copiloto-core
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Variables de Entorno (`.env`)
```bash
cp .env.example .env
```

Editar `.env` con los valores requeridos:

```ini
# ┌─────────────────────────────────────────────────────┐
# │  OBLIGATORIO                                        │
# └─────────────────────────────────────────────────────┘
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL_NAME=llama-3.3-70b-versatile

# ┌─────────────────────────────────────────────────────┐
# │  SEGURIDAD — CAMBIAR EN PRODUCCIÓN                  │
# └─────────────────────────────────────────────────────┘
# ⚠️ SECRET_KEY DEBE ser un string aleatorio largo en producción.
# Generar con: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=change-me-in-production-use-a-long-random-string

# ┌─────────────────────────────────────────────────────┐
# │  OPCIONALES (valores por defecto válidos)           │
# └─────────────────────────────────────────────────────┘
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=150
MAX_UPLOAD_SIZE_MB=10
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# ┌─────────────────────────────────────────────────────┐
# │  QDRANT (para migración futura)                     │
# └─────────────────────────────────────────────────────┘
# QDRANT_URL=https://xxx.cloud.qdrant.io:6333
# QDRANT_API_KEY=your-qdrant-api-key
# QDRANT_COLLECTION_NAME=corporate_documents
```

---

## ▶️ Ejecución

### Modo Desarrollo
```bash
uvicorn app.main:app --reload --port 8001
```

### Modo Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

Verificar:  `http://localhost:8001/api/v1/health`

---

## 📚 API Endpoints

Swagger UI: **http://localhost:8001/docs**

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/v1/register` | Registrar usuario `{email, password}` → JWT |
| `POST` | `/api/v1/login` | Login (OAuth2 form) → JWT |

### Core

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| `POST` | `/api/v1/chat` | ✅ JWT | Preguntar al copiloto `{query, session_id?}` |
| `POST` | `/api/v1/ingest` | ✅ JWT | Subir documento (PDF/DOCX/XLSX/PPTX/TXT) |
| `GET` | `/api/v1/health` | ❌ | Health check (K8s probes) |
| `GET` | `/api/v1/stats` | ✅ Admin | Estadísticas de uso |
| `GET` | `/api/v1/audit-log` | ✅ Admin | Logs de auditoría |

### Ejemplo de flujo
```bash
# 1. Registrarse
curl -X POST localhost:8001/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@empresa.com","password":"MiPassword123!"}'

# 2. Preguntar (con el token JWT recibido)
curl -X POST localhost:8001/api/v1/chat \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"query":"¿Cuáles son los valores corporativos?"}'

# 3. Subir documento (requiere auth)
curl -X POST localhost:8001/api/v1/ingest \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@documento.pdf"
```

---

## 📂 Gestión de Documentos

### Carga Masiva
```bash
# 1. Poner archivos en documents/
# 2. (Opcional) Limpiar índice anterior
python reset_db.py

# 3. Cargar todo
python bulk_ingest.py
```

### Validación de Archivos (Hardening)
El endpoint `/ingest` valida:
- ✅ **Autenticación JWT** requerida
- ✅ **Extensiones permitidas:** `.pdf, .docx, .doc, .xlsx, .xls, .pptx, .txt, .csv, .eml, .msg`
- ✅ **Tamaño máximo:** 10MB (configurable con `MAX_UPLOAD_SIZE_MB`)
- ✅ **PDFs encriptados:** Rechaza automáticamente archivos protegidos con contraseña
- ✅ **Cabecera PDF:** Verifica que los archivos `.pdf` sean PDFs válidos

---

## 🧪 Calibración y Testing

### Ejecutar Suite de Calibración (20 preguntas)
```bash
# Con el servidor corriendo:
python run_calibration.py
```

Genera `informe_calibracion.md` con tabla de resultados.

**Último resultado:** 60/70 (85.7%) ✅ APROBADO

---

## 🔮 Migración a Qdrant (Pendiente)

El proyecto está preparado para migrar de FAISS local a Qdrant Cloud:

- `config.py` ya tiene campos `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_NAME`
- `qdrant-client` ya está en `requirements.txt`
- Solo requiere modificar `vector_db.py` y `retriever.py`
- Puede ejecutarse Qdrant local con Docker: `docker run -p 6333:6333 qdrant/qdrant`

---

## 🛠️ Solución de Problemas

| Error | Solución |
|---|---|
| Error 404 en /docs | Usar puerto `8001`: http://localhost:8001/docs |
| "Model Decommissioned" | Verificar `GROQ_MODEL_NAME=llama-3.3-70b-versatile` en `.env` |
| Rate limit Groq | Plan Dev ($10/mes) da 1M tokens/día |
| Error permisos Windows | Detener servidor antes de `reset_db.py` |
| 401 Unauthorized en /ingest | Se requiere token JWT — primero registrarse y hacer login |
| 415 en /ingest | Solo archivos permitidos: PDF, DOCX, XLSX, PPTX, TXT, CSV, EML |
| 413 en /ingest | Archivo excede 10MB — reducir tamaño o cambiar `MAX_UPLOAD_SIZE_MB` |

---

## 📧 Contacto
Equipo Backend IA
