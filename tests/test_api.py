from unittest.mock import MagicMock
from app.services.llm import LLMService

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}

def test_chat_endpoint(client, monkeypatch):
    # Mock the LLM service to avoid real API calls during tests
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = {
        "answer": "This is a mocked answer for testing.",
        "context": []
    }
    
    mock_service = MagicMock(spec=LLMService)
    mock_service.get_rag_chain.return_value = mock_chain
    
    # Patch the global instance in the route module
    # Note: simple monkeypatching might handle the import in app.api.routes.chat
    monkeypatch.setattr("app.api.routes.chat.llm_service", mock_service)

    response = client.post("/api/v1/chat", json={"query": "Hello"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer for testing."
    assert data["sources"] == []
