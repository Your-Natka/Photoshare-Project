import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app
from app.services.auth import auth_service

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
        
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
mock_user_data = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "hashedpassword",
    "is_verify": False,
    "is_active": True,
    "refresh_token": None,
}
# ---------------------------------------------------------
# SIGNUP
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_register_user(async_client, mocker):
    # Мок репозиторію для створення користувача
    mock_user = {"email": "test@example.com", "username": "testuser", "password": "hashed", "is_verify": False}
    mocker.patch(
        "app.repository.users.create_user",
        return_value=mock_user
    )
    mocker.patch(
        "app.repository.users.get_user_by_email",
        return_value=None
    )

    body = {"email": "test@example.com", "username": "testuser", "password": "123456"}
    response = await async_client.post("/auth/signup", json=body)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    
    
# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_login_user(async_client, mocker):
    user = mock_user_data.copy()
    user["is_verify"] = True

    mocker.patch(
        "app.repository.users.get_user_by_email",
        new=AsyncMock(return_value=user)
    )
    mocker.patch(
        "app.services.auth.auth_service.verify_password",
        return_value=True
    )
    mocker.patch(
        "app.services.auth.auth_service.create_access_token",
        new=AsyncMock(return_value="access_token")
    )
    mocker.patch(
        "app.services.auth.auth_service.create_refresh_token",
        new=AsyncMock(return_value="refresh_token")
    )
    mocker.patch(
        "app.repository.users.update_token",
        new=AsyncMock(return_value=None)
    )

    body = {"username": "test@example.com", "password": "123456"}
    response = await async_client.post("/auth/login", data=body)

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "access_token"
    assert data["refresh_token"] == "refresh_token"

@pytest.mark.asyncio
async def test_login_wrong_password(monkeypatch, client, user_data):
    """Невірний пароль"""

    fake_user = {
        "email": user_data["email"],
        "password": "OTHER_PASSWORD",  # відмінний від введеного
        "is_verify": True,
        "is_active": True
    }

    monkeypatch.setattr(
        "app.repository.users.get_user_by_email",
        AsyncMock(return_value=fake_user)
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password."


# ---------------------------------------------------------
# REFRESH TOKEN
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_refresh_token(monkeypatch, client, user_data):
    """Оновлення access та refresh токена"""
    fake_user = {
        "email": "test@example.com",
        "refresh_token": "OLD_REFRESH",
        "is_active": True,
        "is_verify": True
    }

    # repository mocks
    monkeypatch.setattr(
        "app.repository.users.get_user_by_email",
        AsyncMock(return_value=fake_user)
    )
    monkeypatch.setattr(
        "app.repository.users.update_token",
        AsyncMock(return_value=True)
    )

    # auth_service mocks
    monkeypatch.setattr(
        "app.services.auth.auth_service.decode_refresh_token",
        AsyncMock(return_value="test@example.com")
    )

    headers = {"Authorization": "Bearer OLD_REFRESH"}
    response = await client.get("/api/auth/refresh_token", headers=headers)

    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_logout(monkeypatch, client, user_data):
    """Тест логауту"""

    fake_user = {"email": "test@example.com"}

    monkeypatch.setattr(
        "app.services.auth.auth_service.get_current_user",
        AsyncMock(return_value=fake_user)
    )
    monkeypatch.setattr(
        "app.repository.users.add_to_blacklist",
        AsyncMock(return_value=True)
    )

    headers = {"Authorization": "Bearer TESTTOKEN"}

    response = await client.post("/api/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "User has been logged out."
