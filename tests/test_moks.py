import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from app.main import app
from app.schemas import PostResponse, CommentResponse

# --- Фейковий користувач ---
class MockUser:
    id = 1
    role = "user"
    username = "testuser"
    email = "test@example.com"

# --- Фейкові дані ---
def fake_post(id=1, title="Title"):
    return PostResponse(
        id=id, title=title, descr="Content", hashtags=[],
        avg_rating=0.0, image_url=None, transform_url=None,
        created_at="2025-01-01T00:00:00",
        updated_at="2025-01-01T00:00:00"
    )

def fake_comment(id=1, content="Comment"):
    return CommentResponse(
        id=id, content=content, user_id=1, post_id=1,
        created_at="2025-01-01T00:00:00"
    )

# --- Мокання auth_service для всіх тестів ---
@pytest.fixture(autouse=True)
def mock_auth_service(mocker):
    mocker.patch(
        "app.services.auth.auth_service.get_current_user",
        new=AsyncMock(return_value=MockUser())
    )

# --- Мокання репозиторіїв ---
@pytest.fixture
def mock_posts_repo(mocker):
    mocker.patch(
        "app.repository.posts.create_post", new=AsyncMock(return_value=fake_post())
    )
    mocker.patch(
        "app.repository.posts.get_all_posts", new=AsyncMock(return_value=[fake_post(), fake_post(id=2)])
    )
    mocker.patch(
        "app.repository.posts.get_my_posts", new=AsyncMock(return_value=[fake_post()])
    )
    mocker.patch(
        "app.repository.posts.update_post", new=AsyncMock(return_value=fake_post())
    )
    mocker.patch(
        "app.repository.posts.remove_post", new=AsyncMock(return_value=fake_post())
    )
    return mocker

@pytest.fixture
def mock_comments_repo(mocker):
    mocker.patch(
        "app.repository.comments.create_comment", new=AsyncMock(return_value=fake_comment())
    )
    mocker.patch(
        "app.repository.comments.get_post_comments", new=AsyncMock(return_value=[fake_comment()])
    )
    mocker.patch(
        "app.repository.comments.update_comment", new=AsyncMock(return_value=fake_comment())
    )
    mocker.patch(
        "app.repository.comments.remove_comment", new=AsyncMock(return_value=fake_comment())
    )
    return mocker

@pytest.fixture
def async_client():
    return AsyncClient(app=app, base_url="http://test")
