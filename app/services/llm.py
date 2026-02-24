from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from app.core.config import settings
from app.services.retriever import get_hybrid_retriever
from app.tools.email_tool import tools as email_tools
from app.tools.summary_tool import tools as summary_tools
from app.tools.procedure_tool import tools as procedure_tools
from app.tools.task_tool import tools as task_tools
from langchain.tools.retriever import create_retriever_tool

class LLMService:
    def __init__(self):
        # RESTORED CONFIGURATION: Temperature 0.1 for balance
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL_NAME,
            temperature=0.1
        )
        
        # 1. Tools Setup
        self.retriever = get_hybrid_retriever(k=6)
        retriever_tool = create_retriever_tool(
            self.retriever,
            "search_internal_documents",
            "Searches for information in the corporate documents. Always use this first."
        )
        
        self.tools = [retriever_tool] + email_tools + summary_tools + procedure_tools + task_tools
        
        # 2. Agent Prompt (Copiloto Operativo Persona)
        system_prompt = (
            "Eres el Copiloto Operativo, un asistente experto en procesos bancarios y operativos.\n"
            "Tienes acceso a las siguientes herramientas:\n\n"
            "HERRAMIENTAS DISPONIBLES:\n"
            "1. 'search_internal_documents' — Busca información en los documentos corporativos. SIEMPRE úsala primero para consultas sobre tarifas, procesos o normativas.\n"
            "2. 'send_email' — Envía un correo. Solo úsala si el usuario lo pide explícitamente.\n"
            "3. 'generate_summary' — Genera un resumen ejecutivo estructurado de un texto. Úsala cuando pidan resumir algo.\n"
            "4. 'generate_procedure' — Genera un procedimiento o minuta formal. Úsala cuando pidan armar un procedimiento, protocolo o minuta.\n"
            "5. 'create_task' — Crea una tarea/pendiente y la guarda en la base de datos. Úsala cuando pidan crear una tarea, recordatorio o acción.\n"
            "6. 'list_tasks' — Lista las tareas pendientes. Úsala cuando pregunten por tareas, pendientes o to-dos.\n\n"
            "REGLAS OBLIGATORIAS:\n"
            "1. SIEMPRE usa 'search_internal_documents' ANTES de responder cualquier pregunta sobre procesos, tarifas o normativas.\n"
            "2. SIEMPRE cita tus fuentes al final de cada dato usando el formato exacto: [NombreArchivo.pdf, Pág. X].\n"
            "3. Si el documento no tiene nombre de archivo claro, usa el título del documento como nombre.\n"
            "4. Si no encuentras la información en los documentos, di explícitamente: 'No encontré esta información en los documentos disponibles.'\n"
            "5. NUNCA inventes datos. Solo responde con información que encuentres en los documentos.\n"
            "6. Responde siempre en Español.\n"
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

