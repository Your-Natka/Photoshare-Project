import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient
from fastapi import status
from datetime import datetime

from app.main import app
from app.database.models import User
from app.schemas import CommentResponse


# ----------------------------------------------------
# Фікстури
# ----------------------------------------------------
@pytest.fixture
def mock_user():
    return User(id=1, role="user")


@pytest.fixture
def now():
    return datetime.utcnow()


def build_comment(id=1, text="Text", user_id=1, post_id=1, now=None):
    return CommentResponse(
        id=id,
        text=text,
        user_id=user_id,
        post_id=post_id,
        created_at=now or datetime.utcnow(),
        updated_at=now or datetime.utcnow()
    )


# ----------------------------------------------------
# Тести
# ----------------------------------------------------
@pytest.mark.asyncio
async def test_create_comment(mocker, mock_user, now):
    # Мокаємо поточного користувача асинхронно
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    # Мокаємо репозиторій
    mocker.patch(
        "app.repository.comments.create_comment",
        new=AsyncMock(return_value=build_comment(text="Test comment", now=now))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        body = {"text": "Test comment"}
        response = await ac.post("/api/comments/new/1", json=body)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "Test comment"


@pytest.mark.asyncio
async def test_edit_comment(mocker, mock_user, now):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.comments.edit_comment",
        new=AsyncMock(return_value=build_comment(text="Updated", now=now))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        body = {"text": "Updated"}
        response = await ac.put("/api/comments/edit/1", json=body)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "Updated"


@pytest.mark.asyncio
async def test_delete_comment(mocker, mock_user, now):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.comments.delete_comment",
        new=AsyncMock(return_value=build_comment(text="Deleted", now=now))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/comments/delete/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "Deleted"


@pytest.mark.asyncio
async def test_single_comment(mocker, mock_user, now):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.comments.show_single_comment",
        new=AsyncMock(return_value=build_comment(text="Single", now=now))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/comments/single/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == "Single"


@pytest.mark.asyncio
async def test_by_user_comments(mocker, mock_user, now):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.comments.show_user_comments",
        new=AsyncMock(return_value=[
            build_comment(id=1, text="C1", now=now),
            build_comment(id=2, text="C2", now=now)
        ])
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/comments/by_author/1")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["text"] == "C1"


@pytest.mark.asyncio
async def test_by_user_post_comments(mocker, mock_user, now):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.comments.show_user_post_comments",
        new=AsyncMock(return_value=[build_comment(text="Post comment", now=now)])
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/comments/post_by_author/1/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["text"] == "Post comment"
