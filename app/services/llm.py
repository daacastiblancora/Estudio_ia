from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.core.config import settings
from app.services.vector_db import vector_db_service

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=0
        )
        self.vector_store = vector_db_service.get_vector_store()
        self.retriever = self.vector_store.as_retriever()
        
        # Define the system prompt with strict rules
        system_prompt = (
            "You are an expert operational assistant for Antigravity (Google)."
            "Answer questions based ONLY on the provided context."
            "If the answer is not in the context, say 'I don't know based on the provided documents'."
            "Cite the document name and page number for each fact."
            "\n\n"
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
