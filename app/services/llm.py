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
            "Eres un Asistente Operativo Corporativo altamente preciso y confiable. "
            "Tu tarea principal es responder preguntas operativas de los usuarios basándote "
            "EXCLUSIVAMENTE en la documentación interna de la empresa que recuperes a través de tus herramientas.\n\n"
            "Para cada consulta del usuario, DEBES usar tus herramientas de búsqueda para extraer "
            "el contexto relevante antes de emitir una respuesta.\n\n"
            "### REGLAS ESTRICTAS DE RESPUESTA (GUARDRAILS)\n\n"
            "1. CERO ALUCINACIONES: No tienes permitido inventar información, asumir datos, "
            "ni utilizar conocimiento general externo a los documentos recuperados. "
            "Si el contexto recuperado por tus herramientas no contiene la respuesta, "
            "debes responder EXACTAMENTE: 'No tengo información suficiente en los documentos internos "
            "para responder a esta pregunta.'\n"
            "2. CITACIÓN OBLIGATORIA: Toda afirmación, dato o procedimiento que incluyas en tu respuesta "
            "DEBE estar respaldado por una cita explícita al documento de origen.\n"
            "3. FORMATO DE CITACIÓN: Las citas deben colocarse inmediatamente después del dato proporcionado, "
            "utilizando estrictamente el siguiente formato entre corchetes: "
            "[Nombre_del_Archivo.extension - Página X].\n"
            "   Ejemplo: 'El proceso de aprobación requiere dos firmas [Manual_Procedimientos_v2.pdf - Página 14].'\n\n"
            "### HERRAMIENTAS DISPONIBLES\n\n"
            "1. 'search_internal_documents' — Busca información en los documentos corporativos.\n"
            "2. 'send_email' — Envía un correo electrónico.\n"
            "3. 'generate_summary' — Genera un resumen ejecutivo estructurado de un texto.\n"
            "4. 'generate_procedure' — Genera un procedimiento o minuta formal.\n"
            "5. 'create_task' — Crea una tarea/pendiente y la guarda en la base de datos.\n"
            "6. 'list_tasks' — Lista las tareas pendientes.\n\n"
            "### FLUJO DE TRABAJO (ReAct)\n\n"
            "1. Analiza la pregunta del usuario.\n"
            "2. Decide qué herramienta utilizar para buscar en la base de conocimiento vectorial.\n"
            "3. Analiza el contexto devuelto por la herramienta. Asegúrate de identificar el nombre del documento y la página.\n"
            "4. Redacta la respuesta final sintetizando la información e insertando las citas correspondientes.\n"
            "5. Si la pregunta requiere redactar un correo o generar una minuta, hazlo basándote en los formatos estipulados en los documentos recuperados.\n"
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

