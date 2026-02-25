from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.core.config import settings
from app.services.retriever import get_hybrid_retriever


class LLMService:
    def __init__(self):
        # Temperature 0.1 for precision with minimal creativity
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=0.1
        )

        # Hybrid Retriever (FAISS + BM25 reranking)
        self.retriever = get_hybrid_retriever(k=6)

        # 1. Contextualize Question Prompt
        # Reformulates the question based on history so the retriever understands it
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is. "
            "Always respond in Spanish."
        )
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # 2. QA Prompt (System Prompt)
        qa_system_prompt = (
            "Eres un Asistente de Viajes de ColombiaTours.Travel, altamente preciso y confiable.\n"
            "Tu tarea es responder preguntas basándote en el contexto proporcionado.\n\n"
            "### INSTRUCCIONES DE RESPUESTA\n\n"
            "1. USA TODO EL CONTEXTO: Analiza cuidadosamente TODOS los documentos proporcionados. "
            "Extrae y presenta TODOS los datos relevantes que encuentres (precios, fechas, duraciones, "
            "nombres, listas, requisitos, etc.).\n"
            "2. CITACIÓN OBLIGATORIA: Cada dato o afirmación DEBE tener una cita al documento fuente "
            "inmediatamente después, en el formato: [Nombre_del_Archivo.pdf - Página X].\n"
            "   Ejemplo: 'El costo es de $3.000 USD [01_colombia_corazon_15dias.pdf - Página 1].'\n"
            "3. PRECISIÓN: Incluye números exactos, precios en COP y USD, duraciones en días, "
            "y todos los datos tal como aparecen en el contexto. No omitas datos numéricos.\n"
            "4. ESTRUCTURA: Usa listas con viñetas y negritas para datos clave.\n"
            "5. IDIOMA: Responde SIEMPRE en Español.\n"
            "6. SOLO si el contexto verdaderamente NO contiene información relevante, responde: "
            "'No tengo información suficiente en los documentos internos para responder.'\n\n"
            "Contexto:\n"
            "{context}"
        )

        self.qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

    def get_rag_chain(self):
        # 1. Create History-Aware Retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, self.contextualize_q_prompt
        )

        # 2. Create QA Chain
        question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)

        # 3. Create Final RAG Chain
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return rag_chain


llm_service = LLMService()
