import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL_NAME")

print(f"Testing Groq access with model: {model}")

try:
    llm = ChatGroq(
        groq_api_key=key,
        model_name=model,
        temperature=0
    )
    print("Invoking LLM...")
    response = llm.invoke("Hello, are you working?")
    print(f"Response: {response.content}")
    print("✅ Groq Connection Successful!")
except Exception as e:
    print(f"❌ Groq Error: {e}")
