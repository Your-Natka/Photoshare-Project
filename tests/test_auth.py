import pytest
from httpx import AsyncClient

# Тепер client береться з fixtures
@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_register_existing_email(client: AsyncClient):
    # Створимо юзера для перевірки
    await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Спершу реєструємо
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login", data={
        "username": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    response = await client.post("/api/auth/login", data={
        "username": "user1@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    login = await client.post("/api/auth/login", data={
        "username": "user1@example.com",
        "password": "password123"
    })
    refresh_token = login.json()["access_token"]
    response = await client.post("/api/auth/refresh", headers={
        "Authorization": f"Bearer {refresh_token}"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
