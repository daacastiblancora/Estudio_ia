from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Copiloto Core"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    
    # Qdrant (Optional if using FAISS Local)
    QDRANT_URL: Union[str, None] = None
    QDRANT_API_KEY: Union[str, None] = None
    QDRANT_COLLECTION_NAME: str = "copiloto_docs"
    
    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"
    
    # Embeddings
    # Switched to Multilingual model for better Spanish support
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # Ingestion
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 350

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
