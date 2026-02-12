from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from app.core.config import settings
from app.services.retriever import get_hybrid_retriever
from app.tools.email_tool import tools as email_tools
from langchain.tools.retriever import create_retriever_tool

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=0.1
        )
        
        # 1. Tools Setup
        # Wrap Retriever as a Tool so the Agent can decide when to search
        self.retriever = get_hybrid_retriever(k=6)
        retriever_tool = create_retriever_tool(
            self.retriever,
            "search_internal_documents",
            "Searches for information in the corporate documents (policies, procedures, manuals). Always use this first to answer questions."
        )
        
        self.tools = [retriever_tool] + email_tools
        
        # 2. Agent Prompt
        system_prompt = (
            "Eres V.E.T.A. (Virtual Especialista en Trámites y Asesoría), un agente operativo corporativo.\n"
            "Tienes acceso a herramientas para buscar información y enviar correos.\n"
            "Reglas:\n"
            "1. Usa 'search_internal_documents' para responder preguntas sobre procesos.\n"
            "2. Usa 'send_email' solo si el usuario te lo pide explícitamente.\n"
            "3. Si encuentras información en los documentos, CITA LA FUENTE [Archivo, Pág. X].\n"
            "4. Responde siempre en Español.\n"
        )
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        
        # 3. Create Agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def get_rag_chain(self):
        # We return the agent executor which mimics the chain interface (invoke)
        return self.agent_executor

llm_service = LLMService()
