# app/api/dependencies.py
# Currently we are using singletons in services/, but dependency injection
# can be set up here if we want per-request lifecycles.

def get_vector_db():
    from app.services.vector_db import vector_db_service
    return vector_db_service

def get_llm():
    from app.services.llm import llm_service
    return llm_service
