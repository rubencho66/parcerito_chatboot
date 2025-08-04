import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.routes.auth import router
from src.schemas import LoginRequest

@pytest.fixture
def client():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


@patch("src.dependencies.SessionLocal")
@patch("src.routes.auth.create_access_token")
@patch("src.routes.auth.verify_password")
def test_create_token_success(mock_verify_password, mock_create_access_token, mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_user_obj = MagicMock()
    mock_user_obj.id = 1
    mock_user_obj.email = "test@example.com"
    # Mock db.query(User).filter().first()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_obj
    mock_verify_password.return_value = True
    mock_create_access_token.return_value = "testtoken"

    payload = {"email": "test@example.com", "password": "password"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] == "testtoken"
    assert response.json()["token_type"] == "bearer"


@patch("src.dependencies.SessionLocal")
def test_create_token_user_not_found(mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None
    payload = {"email": "notfound@example.com", "password": "password"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"


@patch("src.dependencies.SessionLocal")
@patch("src.routes.auth.verify_password")
def test_create_token_wrong_password(mock_verify_password, mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_user_obj = MagicMock()
    mock_user_obj.id = 1
    mock_user_obj.email = "test@example.com"
    mock_verify_password.return_value = False
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user_obj
    payload = {"email": "test@example.com", "password": "wrongpass"}
    response = client.post("/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect password"
