# Copiloto Core — Backend AI Microservice

> **Manual de Despliegue para Equipos de Integración (Frontend/Backend)**

Microservicio de Inteligencia Artificial (RAG) para procesar documentos y responder preguntas con citas a fuentes.

## 📋 Arquitectura Técnica

| Componente | Tecnología |
|---|---|
| **API** | FastAPI (REST) |
| **LLM** | Llama 3.3 70B (vía Groq API) |
| **Vector Store** | **Qdrant (Cloud-Native)** — Contenedor Docker o Cloud |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2` (Multilingüe) |
| **Retrieval** | Híbrido: **Qdrant Dense + BM25 Reranking** (`k=6`) |
| **Autenticación** | JWT (OAuth2 Bearer) — Register/Login con RBAC |
| **Rate Limiting** | SlowAPI (30 req/min en `/chat`) |
| **Memoria** | Sesiones conversacionales persistentes en SQLite |
| **Guardrails** | Anti-alucinación + anti-injection |
| **Chunks** | 500 chars, overlap 150, separadores semánticos |

### Diagrama de Flujo RAG

```
Usuario → /chat → JWT Auth → Rate Limit → Contextualize Question (reformula con historial)
    → Hybrid Retriever (Qdrant + BM25, k=6) → QA Chain (Llama 3.3) → Citación [PDF - Pág X]
    → Guardrails (anti-alucinación) → Response + Sources
```

---

## 🚀 Pre-requisitos

1. **Python 3.10+**
2. **Docker** (para correr Qdrant localmente)
3. **API Key de Groq:** Crear en [console.groq.com](https://console.groq.com)
4. **Git**

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

### 2. Levantar Vector Store (Qdrant)
```bash
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant-copiloto qdrant/qdrant
```

### 3. Variables de Entorno (`.env`)
```bash
cp .env.example .env
```

Editar `.env` con los valores requeridos (especialmente `GROQ_API_KEY` y `SECRET_KEY`).

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

---

## 📂 Gestión de Documentos

### Carga Masiva
```bash
# 1. Poner archivos en documents/
# 2. Limpiar colección anterior en Qdrant
python reset_db.py

# 3. Cargar todo (requiere que el servidor esté corriendo)
python bulk_ingest.py
```

### Validación de Archivos (Hardening)
El endpoint `/ingest` valida:
- ✅ **Autenticación JWT** requerida
- ✅ **Extensiones permitidas:** `.pdf, .docx, .doc, .xlsx, .xls, .pptx, .txt, .csv, .eml, .msg`
- ✅ **Tamaño máximo:** 10MB (configurable)
- ✅ **PDFs encriptados:** Rechaza archivos protegidos
- ✅ **Cabecera PDF:** Verifica integridad estructural del archivo

---

## 🧪 Calibración y Testing

El sistema ha sido calibrado exhaustivamente usando un corpus de 20 documentos reales.

### Ejecutar Suite Automatizada
```bash
python run_calibration.py
```

**Resultado Final (R10):** 60/70 (**85.7%**) ✅ **APROBADO**

Categorías evaluadas:
- **Exactitud (BM25):** 87%
- **Semántica (RAG):** 87%
- **Citación:** 87%
- **Memoria:** 84%

---

## 🛠️ Solución de Problemas

| Error | Solución |
|---|---|
| Conexión Qdrant | Asegurar que Docker esté corriendo y puerto `6333` abierto. |
| Error 401 en /ingest | Registrarse y usar el token en el header `Authorization: Bearer <TOKEN>`. |
| 415 en /ingest | El archivo no está en la lista de permitidos. |
| "Model Decommissioned" | Actualizar `GROQ_MODEL_NAME` en `.env`. |

---

## 📧 Contacto
Equipo Backend IA — Copiloto Operativo
