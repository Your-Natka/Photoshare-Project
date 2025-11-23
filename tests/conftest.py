import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.database.models import Base, User
from app.database.connect_db import get_db
from app.main import app

# --- Додаємо корінь проекту до sys.path ---
sys.path.append(os.getcwd())

# --- Синхронна тестова база для TestClient ---
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test.db"
)
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Асинхронна тестова база для репозиторіїв ---
ASYNC_TEST_DATABASE_URL = TEST_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
async_engine = create_async_engine(
    ASYNC_TEST_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in ASYNC_TEST_DATABASE_URL else {}
)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

# ------------------ Фікстури ------------------

# Асинхронна сесія для репозиторіїв
@pytest.fixture()
async def session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Синхронна сесія для TestClient
@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)

# Redis mock для всіх тестів
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    from app.main import redis
    mock_redis_instance = AsyncMock()
    mock_redis_instance.ping.return_value = True
    monkeypatch.setattr("app.main.redis.from_url", lambda *args, **kwargs: mock_redis_instance)
    yield

# FastAPI TestClient із заміною get_db
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

# User для авторизації в синхронних тестах
@pytest.fixture(scope="function")
def create_user(db_session):
    user = User(
        username="artur4ik",
        email="artur4ik@example.com",
        password="123456789",
        role="Administrator",
        avatar="url-avatar"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# User для асинхронних тестів репозиторія
@pytest.fixture()
async def user(session):
    test_user = User(
        username="second_user",
        email="second_user@example.com",
        password="password123",
        avatar="url-avatar"
    )
    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)
    return test_user

# Мок для функцій email
@pytest.fixture
def mock_send_email(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("app.routes.auth.confirmed_email", mock)
    return mock
