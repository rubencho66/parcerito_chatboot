import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.security.auth import create_access_token
from datetime import timedelta

client = TestClient(app)

@pytest.fixture
def valid_token():
    data = {"id": 1, "sub": "test@example.com"}
    return create_access_token(data, expires_delta=timedelta(minutes=15))

@pytest.mark.contract
def test_chat_external_question(valid_token):
    response = client.post(
        "/chat",
        json={"message": "¿Cómo puedo aprender ingles?", "conversation_id": "abc123"},
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert "creo que su dinero está en el lugar equivocado, eso no es conmigo" in response.json()["reply"]
