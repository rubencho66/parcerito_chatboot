import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.constants import MODEL_NOT_DEFINED
from src.routes.chat import router
from src.schemas import SecurityContext

_MOCK_TOKEN_PAYLOAD = {"id": "1", "sub": "test@example.com"}

@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@patch("src.security.auth.jwt")
@patch("src.routes.chat.model")
def test_chat_success(mock_model, mock_jwt, client):
    # Use a MagicMock or a real SecurityContext instance
    mock_jwt.return_value = MagicMock()
    mock_jwt.decode.return_value = _MOCK_TOKEN_PAYLOAD
    mock_model.ask_to_model.return_value = MagicMock(content="Hello!")
    payload = {"message": "Hi!", "conversation_id": "abc123"}
    response = client.post("/chat", json=payload, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Hello!"
    assert response.json()["conversation_id"] == "abc123"
    assert response.json()["statusCode"] == 200



@patch("src.security.auth.jwt")
@patch("src.routes.chat.model")
def test_chat_model_not_defined(mock_model, mock_jwt, client):
    mock_jwt.return_value = MagicMock()
    mock_jwt.decode.return_value = _MOCK_TOKEN_PAYLOAD
    mock_model.ask_to_model.return_value = None
    payload = {"message": "Hi!", "conversation_id": "abc123"}
    response = client.post("/chat", json=payload, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 500
    assert response.json()["detail"] == MODEL_NOT_DEFINED
