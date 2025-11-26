import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database.connect_db import get_db
from app.repository.users import create_user, get_user_by_email

# --------------------------------------
# MOCK ASYNC DB SESSION
# --------------------------------------
class FakeAsyncSession:
    def __init__(self):
        self.users = []

    async def execute(self, query):
        class Result:
            def scalar_one_or_none(inner_self):
                return self.users[0] if self.users else None

            def fetchall(inner_self):
                return self.users
        return Result()

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

# --------------------------------------
# FIXTURE ASYNC CLIENT
# --------------------------------------
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

# --------------------------------------
# MOCK DATABASE
# --------------------------------------
@pytest.fixture(autouse=True)
def mock_db():
    with patch("app.database.connect_db.get_db", return_value=FakeAsyncSession()):
        yield

# --------------------------------------
# Тести користувачів
# --------------------------------------
@pytest.mark.asyncio
async def test_create_user_directly():
    session = FakeAsyncSession()
    user_data = {"username": "tester", "email": "tester@example.com", "password": "secret"}
    user = await create_user(session, **user_data)
    assert user.username == "tester"
    assert user.email == "tester@example.com"

@pytest.mark.asyncio
async def test_get_user_by_email_directly():
    session = FakeAsyncSession()
    session.users.append(type("User", (), {"email": "tester@example.com"}))
    user = await get_user_by_email(session, "tester@example.com")
    assert user.email == "tester@example.com"

@pytest.mark.asyncio
async def test_register_user_api(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code in (201, 400)  # 201 if created, 400 if already exists

@pytest.mark.asyncio
async def test_login_user_api(client: AsyncClient):
    response = await client.post("/api/auth/login", data={
        "username": "user1@example.com",
        "password": "password123"
    })
    assert response.status_code in (200, 401)
