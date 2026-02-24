from langchain_core.tools import tool
from langchain_groq import ChatGroq
from app.core.config import settings


@tool
def generate_procedure(topic: str, context: str = "") -> str:
    """
    Generates a formal procedure or minute document on the given topic.
    Use this when the user asks to create a procedure, protocol, minute, or formal document.
    Args:
        topic: The subject of the procedure (e.g. "solicitar una chequera")
        context: Optional additional context or information to include
    """
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0.2,
    )

    prompt = (
        "Eres un asistente corporativo experto en documentación de procesos bancarios.\n"
        "Genera un procedimiento formal y profesional sobre el tema indicado.\n\n"
        "El documento debe incluir:\n"
        "1. **Título del Procedimiento**\n"
        "2. **Objetivo**\n"
        "3. **Alcance**\n"
        "4. **Responsables**\n"
        "5. **Pasos del Procedimiento** (numerados)\n"
        "6. **Documentos Requeridos** (si aplica)\n"
        "7. **Observaciones**\n\n"
        "Responde en Español. Usa formato profesional.\n\n"
        f"TEMA: {topic}\n"
    )

    if context:
        prompt += f"CONTEXTO ADICIONAL:\n{context}\n"

    response = llm.invoke(prompt)
    return response.content


tools = [generate_procedure]
