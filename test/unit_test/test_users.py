import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from unittest.mock import patch, MagicMock
from src.routes.users import router
from src.schemas import CreateUser

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
@patch("src.routes.users.hash_password")
@patch("src.routes.users.User")
def test_create_user_success(mock_user, mock_hash_password, mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_hash_password.return_value = "hashedpass"
    mock_user_obj = MagicMock()
    mock_user_obj.name = "Test"
    mock_user_obj.email = "test@example.com"
    mock_user_obj.password = "hashedpass"
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    mock_user.return_value = mock_user_obj
    payload = {"name": "Test", "email": "test@example.com", "password": "password"}
    response = client.post("/users", json=payload)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@patch("src.dependencies.SessionLocal")
@patch("src.routes.users.hash_password")
@patch("src.routes.users.User")
def test_create_user_email_exists(mock_user, mock_hash_password, mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_hash_password.return_value = "hashedpass"
    mock_user_obj = MagicMock()
    mock_user_obj.name = "Test"
    mock_user_obj.email = "test@example.com"
    mock_user_obj.password = "hashedpass"
    mock_db.add.return_value = None
    mock_db.commit.side_effect = IntegrityError("IntegrityError", "Email already registered", None)
    mock_db.rollback.return_value = None
    mock_db.refresh.return_value = None
    mock_user.return_value = mock_user_obj
    payload = {"name": "Test", "email": "test@example.com", "password": "password"}
    response = client.post("/users", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@patch("src.dependencies.SessionLocal")
@patch("src.routes.users.User")
def test_get_users_success(mock_user, mock_sessionlocal, client, mock_db):
    mock_sessionlocal.return_value = mock_db
    mock_user_obj = MagicMock()
    mock_user_obj.name = "Test"
    mock_user_obj.email = "test@example.com"
    mock_user_obj.password = "hashedpass"
    mock_db.query.return_value.all.return_value = [mock_user_obj]
    mock_user.query = mock_db.query
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["email"] == "test@example.com"
