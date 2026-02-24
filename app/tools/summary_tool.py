from langchain_core.tools import tool
from langchain_groq import ChatGroq
from app.core.config import settings


@tool
def generate_summary(text: str) -> str:
    """
    Generates a structured executive summary from the given text.
    Use this when the user asks to summarize a meeting, document, or any text.
    The input should be the full text to summarize.
    """
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0.2,
    )

    prompt = (
        "Eres un asistente profesional. Genera un resumen ejecutivo estructurado "
        "del siguiente texto. El resumen debe incluir:\n"
        "1. **Resumen General** (2-3 oraciones)\n"
        "2. **Puntos Clave** (lista con viñetas)\n"
        "3. **Decisiones** (si aplica)\n"
        "4. **Acciones Pendientes** (si aplica)\n\n"
        "Responde en Español.\n\n"
        f"TEXTO:\n{text}"
    )

    response = llm.invoke(prompt)
    return response.content


tools = [generate_summary]
