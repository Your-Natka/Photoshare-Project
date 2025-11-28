import pytest
from io import BytesIO
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.schemas import PostResponse 

# Фейковий користувач для тестів
class MockUser:
    id = 1
    email = "test@example.com"
    role = "user"

@pytest.mark.asyncio
async def test_create_post(mocker):
    mock_user = MockUser()

    # Мокаємо поточного користувача
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    # Мокаємо репозиторій
    mocker.patch(
        "app.repository.posts.create_post",
        new=AsyncMock(return_value=PostResponse(
            id=1,
            title="Test Post",
            descr="Content",
            hashtags=[],
            avg_rating=0.0,
            image_url=None,
            transform_url=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
            user_id=mock_user.id
        ))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "title": "Test Post",
            "descr": "Content",
            "hashtags": ["tag1", "tag2"]
        }
        files = {"file": ("test.jpg", BytesIO(b"dummy content"), "image/jpeg")}
        response = await ac.post("/api/posts/new/", data=data, files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["descr"] == "Content"

@pytest.mark.asyncio
async def test_update_post(mocker):
    mock_user = MockUser()
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.posts.update_post",
        new=AsyncMock(return_value=PostResponse(
            id=1,
            title="Updated",
            descr="Updated Content",
            hashtags=[],
            avg_rating=0.0,
            image_url=None,
            transform_url=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-02T00:00:00"
        ))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        body = {"title": "Updated", "descr": "Updated Content", "hashtags": []}
        response = await ac.put("/api/posts/1", json=body)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["descr"] == "Updated Content"

@pytest.mark.asyncio
async def test_delete_post(mocker):
    mock_user = MockUser()
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=mock_user)
    )

    mocker.patch(
        "app.repository.posts.remove_post",
        new=AsyncMock(return_value=PostResponse(
            id=1,
            title="Deleted",
            descr="Deleted Content",
            hashtags=[],
            avg_rating=0.0,
            image_url=None,
            transform_url=None,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-02T00:00:00",
            user_id=mock_user.id
        ))
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/posts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Deleted"

@pytest.mark.asyncio
async def test_read_all_posts(mocker):
    mocker.patch(
        "app.repository.posts.get_all_posts",
        new=AsyncMock(return_value=[
            PostResponse(
                id=1, title="Post 1", descr="Content 1", hashtags=[], avg_rating=0.0,
                image_url=None, transform_url=None, created_at="2025-01-01T00:00:00", updated_at="2025-01-01T00:00:00",
                user_id=1
            ),
            PostResponse(
                id=2, title="Post 2", descr="Content 2", hashtags=[], avg_rating=0.0,
                image_url=None, transform_url=None, created_at="2025-01-01T00:00:00", updated_at="2025-01-01T00:00:00",
                user_id=1
            ),
        ])
    )

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/posts/all")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Post 1"
    assert data[1]["title"] == "Post 2"
