import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock
from datetime import datetime
from app.main import app
from app.database.models import User, UserRoleEnum
from app.schemas import RatingModel
from app.repository import ratings as repository_ratings


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_user():
    return User(id=1, username="john", role=UserRoleEnum.user)


@pytest.fixture
def mock_admin():
    return User(id=2, username="admin", role=UserRoleEnum.admin)


# Мок auth_service
@pytest.fixture(autouse=True)
def mock_auth(monkeypatch, mock_user):
    monkeypatch.setattr(
        "app.routers.ratings.auth_service.get_current_user",
        lambda: AsyncMock(return_value=mock_user)()
    )


# -----------------------------
# TESTS
# -----------------------------
@pytest.mark.asyncio
async def test_create_rate_success(monkeypatch, mock_user):
    # Мок repository
    monkeypatch.setattr(
        repository_ratings,
        "create_rate",
        AsyncMock(return_value=RatingModel(
            id=1,
            post_id=10,
            user_id=mock_user.id,
            rate=5,
            created_at=datetime.utcnow()  
        ))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/ratings/posts/10/5")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] == mock_user.id
    assert response.json()["rate"] == 5


@pytest.mark.asyncio
async def test_edit_rate_success(monkeypatch, mock_user):
    monkeypatch.setattr(
        repository_ratings,
        "edit_rate",
        AsyncMock(return_value=RatingModel(id=1, post_id=10, user_id=mock_user.id, rate=4))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/ratings/edit/1/4")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rate"] == 4


@pytest.mark.asyncio
async def test_delete_rate_success(monkeypatch, mock_user):
    monkeypatch.setattr(
        repository_ratings,
        "delete_rate",
        AsyncMock(return_value=RatingModel(id=1, post_id=10, user_id=mock_user.id, rate=4))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/ratings/delete/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_all_rates_success(monkeypatch, mock_user):
    monkeypatch.setattr(
        repository_ratings,
        "show_ratings",
        AsyncMock(return_value=[
            RatingModel(id=1, post_id=10, user_id=mock_user.id, rate=5)
        ])
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ratings/all")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert response.json()[0]["rate"] == 5


@pytest.mark.asyncio
async def test_all_my_rates_success(monkeypatch, mock_user):
    monkeypatch.setattr(
        repository_ratings,
        "show_my_ratings",
        AsyncMock(return_value=[
            RatingModel(id=1, post_id=10, user_id=mock_user.id, rate=5)
        ])
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ratings/all_my")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["user_id"] == mock_user.id


@pytest.mark.asyncio
async def test_user_rate_post_success(monkeypatch, mock_user):
    monkeypatch.setattr(
        repository_ratings,
        "user_rate_post",
        AsyncMock(return_value=RatingModel(id=1, post_id=10, user_id=mock_user.id, rate=5))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/ratings/user_post/1/10")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["post_id"] == 10
