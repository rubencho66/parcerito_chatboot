import pytest
from fastapi.testclient import TestClient
from src.constants import NOT_AUTHENTICATED_MESSAGE
from src.main import app
from src.schemas import LoginRequest, SecurityContext
from src.security.auth import create_access_token
from datetime import timedelta

client = TestClient(app)

@pytest.fixture
def valid_token():
    data = {"id": 1, "sub": "test@example.com"}
    return create_access_token(data, expires_delta=timedelta(minutes=15))

@pytest.fixture
def invalid_token():
    return "invalid.token.value"

@pytest.mark.contract
def test_get_security_context_valid(valid_token):
    response = client.post(
        "/chat",
        json={"message": "Hello", "conversation_id": "abc123"},
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert "reply" in response.json()
    assert "conversation_id" in response.json()
    assert response.json()["statusCode"] == 200

@pytest.mark.contract
def test_get_security_context_invalid(invalid_token):
    response = client.post(
        "/chat",
        json={"message": "Hello", "conversation_id": "abc123"},
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == NOT_AUTHENTICATED_MESSAGE
