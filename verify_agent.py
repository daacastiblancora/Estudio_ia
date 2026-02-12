from app.services.llm import llm_service
from app.tools.email_tool import send_email

# Mock input to test Agent
print("🤖 Testing Agent Capabilities...")

# Test 1: Retrieval
print("\n[Test 1] Asking about documents...")
query_1 = "What is the maximum deadline for response?"
response_1 = llm_service.agent_executor.invoke({"input": query_1, "chat_history": []})
print(f"Agent Output: {response_1['output']}")

# Test 2: Tool Usage (Email)
print("\n[Test 2] Asking to send email...")
query_2 = "Send an email to boss@company.com saying 'The report is ready'."
response_2 = llm_service.agent_executor.invoke({"input": query_2, "chat_history": []})
print(f"Agent Output: {response_2['output']}")
