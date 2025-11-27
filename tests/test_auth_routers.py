import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from datetime import datetime
from app.main import app
from app.schemas import UserDb
from app.database.models import User

@pytest.mark.asyncio
@patch("app.routers.auth.send_email", new_callable=AsyncMock)
@patch("app.repository.users.create_user", new_callable=AsyncMock)
@patch("app.repository.users.get_user_by_email", new_callable=AsyncMock)
async def test_register_user(mock_add_task, mock_create_user, mock_send_email):
    mock_get_user.return_value = None

    class MockUser:
        id = 1
        username = "testuser"
        email = "test@example.com"
        avatar = None
        role = "user"
        created_at = "2024-01-01"

    mock_create_user.return_value = MockUser()

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "12345678"
        }
        response = await ac.post("/api/auth/signup", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["detail"] == "User successfully created"

    # ключове!
    mock_send_email.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.repository.users.get_user_by_email", new_callable=AsyncMock)
@patch("app.repository.users.update_token", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.create_access_token", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.create_refresh_token", new_callable=AsyncMock)
async def test_login_user(mock_refresh, mock_access, mock_update_token, mock_get_user):
    # Мок: існуючий користувач
    class User:
        email = "test@example.com"
        password = "hashed"
        is_verify = True
        is_active = True
        refresh_token = None

    mock_get_user.return_value = User()
    mock_access.return_value = "access123"
    mock_refresh.return_value = "refresh123"

    # Перевірка хешування пароля
    patch("app.services.auth.auth_service.verify_password", return_value=True).start()

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/api/auth/login", data={"username": "test@example.com", "password": "12345678"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "access123"
    assert data["refresh_token"] == "refresh123"


@pytest.mark.asyncio
@patch("app.repository.users.get_user_by_email", new_callable=AsyncMock)
@patch("app.repository.users.update_token", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.decode_refresh_token", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.create_access_token", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.create_refresh_token", new_callable=AsyncMock)
async def test_refresh_token(mock_create_refresh, mock_create_access, mock_decode, mock_update_token, mock_get_user):
    class User:
        email = "test@example.com"
        refresh_token = "refresh123"

    mock_decode.return_value = "test@example.com"
    mock_get_user.return_value = User()
    mock_create_access.return_value = "new_access"
    mock_create_refresh.return_value = "new_refresh"

    headers = {"Authorization": "Bearer refresh123"}
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.get("/api/auth/refresh_token", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "new_access"
    assert data["refresh_token"] == "new_refresh"


@pytest.mark.asyncio
@patch("app.repository.users.add_to_blacklist", new_callable=AsyncMock)
@patch("app.services.auth.auth_service.get_current_user", new_callable=AsyncMock)
async def test_logout(mock_current_user, mock_blacklist):
    class User:
        email = "test@example.com"
    mock_current_user.return_value = User()

    headers = {"Authorization": "Bearer access123"}
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        response = await ac.post("/api/auth/logout", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User successfully logged out" or "USER_IS_LOGOUT"
    mock_blacklist.assert_awaited_once()
