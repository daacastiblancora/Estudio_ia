from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.core.config import settings
from app.services.retriever import get_hybrid_retriever

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=0.1 # Low temp for factual accuracy
        )
        
        # Use Hybrid Retriever
        self.retriever = get_hybrid_retriever(k=6)
        
        # Improved System Prompt for Citations
        system_prompt = (
            "Eres V.E.T.A. (Virtual Especialista en Trámites y Asesoría), un asistente experto en operativa corporativa.\n"
            "Tu misión es responder preguntas basándote ÚNICAMENTE en el contexto proporcionado.\n\n"
            
            "Reglas de Oro:\n"
            "1. NO INVENTES información. Si la respuesta no está en el contexto, di 'No encuentro esa información en los documentos disponibles'.\n"
            "2. CITAS OBLIGATORIAS: Cada afirmación debe llevar su cita exacta entre corchetes al final de la frase.\n"
            "   Formato: [NombreArchivo, Pág. X]\n"
            "   Ejemplo: 'El plazo es de 30 días [poliza_seguros.pdf, Pág. 12].'\n"
            "3. IDIOMA: Responde siempre en Español formal y corporativo.\n"
            "4. ESTRUCTURA: Usa listas y negritas para mejorar la legibilidad.\n\n"
            
            "Contexto:\n"
            "{context}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

    def get_rag_chain(self):
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)
        return rag_chain

llm_service = LLMService()
