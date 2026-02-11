# Copiloto Core - Backend AI Microservice

> **Manual de Despliegue para Equipos de Integración (Frontend/Backend)**

Este repositorio contiene el microservicio de Inteligencia Artificial (RAG) encargado de procesar documentos y responder preguntas operativas con citas precisas.

## 📋 Descripción Técnica

*   **Arquitectura:** REST API (FastAPI)
*   **LLM:** Llama 3.3 70B (vía Groq)
*   **Vector Store:** FAISS (Local) con Embeddings Multilingües (`paraphrase-multilingual-MiniLM-L12-v2`)
*   **Ingesta:** Script ETL para PDF/DOCX con inyección de metadatos.

---

## 🚀 Pre-requisitos

1.  **Python 3.10+** instalado.
2.  **API Key de Groq:** Solicitar al Tech Lead o crear en [console.groq.com](https://console.groq.com).
3.  **Git** instalado.

---

## ⚙️ Instalación (Paso a Paso)

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPO>
cd copiloto-core
```

### 2. Configurar Entorno Virtual
Se recomienda usar un entorno aislado para evitar conflictos.
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno (.env)
Copiar el ejemplo y configurar la llave.
```bash
cp .env.example .env
```
Editar `.env` y establecer:
```ini
GROQ_API_KEY=gsk_xxxxxxxxxxxx
GROQ_MODEL_NAME=llama-3.3-70b-versatile
# El resto de variables pueden dejarse por defecto para desarrollo local
```

---

## ▶️ Ejecución del Servicio

### Modo Desarrollo (con Hot-Reload)
El servicio corre por defecto en el puerto **8001** para evitar conflictos con otros procesos.

```bash
uvicorn app.main:app --reload --port 8001
```

Una vez iniciado, verás: `INFO: Uvicorn running on http://0.0.0.1:8001`

---

## 📚 Documentación de API (Swagger)

La documentación interactiva para el Equipo Frontend está disponible en:
👉 **[http://localhost:8001/docs](http://localhost:8001/docs)**

### Endpoints Principales

#### 1. Chat (`POST /api/v1/chat`)
Recibe una pregunta y devuelve respuesta + fuentes.
*   **Body:** `{"query": "¿Cuáles son los valores?"}`
*   **Response:**
    ```json
    {
      "answer": "Los valores son...",
      "sources": [
        { "document_name": "Manual.pdf", "page_number": 5, ... }
      ]
    }
    ```

#### 2. Ingesta (`POST /api/v1/ingest`)
Carga un archivo PDF/DOCX al sistema.
*   **Form-Data:** `file` (Binary)

#### 3. Health (`GET /api/v1/health`)
Para verificar estado (K8s probes).

---

## 📂 Gestión de Documentos (Pipeline ETL)

El sistema incluye scripts de utilidad para operaciones masivas.

### 1. Carga Masiva (Reset & Ingest)
Si desean cargar un set inicial de documentos:
1.  Poner archivos PDF en la carpeta `documents/`.
2.  Ejecutar el script de limpieza y carga:
    ```bash
    # (Opcional) Borrar base de datos anterior
    python reset_db.py
    
    # Cargar todo lo que esté en documents/
    python bulk_ingest.py
    ```

### 2. Demo CLI
Para probar el cerebro sin frontend:
```bash
python demo.py
```

---

## 🛠️ Solución de Problemas Frecuentes

*   **Error 404 en /docs:** Asegúrate de estar usando el puerto `8001` (http://localhost:8001/docs).
*   **"Model Decommissioned":** Verificar que en `.env` el modelo sea `llama-3.3-70b-versatile`.
*   **Error de Permisos (Windows):** Si `reset_db.py` falla borrar la carpeta, detener el servidor `uvicorn` primero.

---

## 📧 Contacto
Equipo Backend IA - [tu-email@empresa.com]
