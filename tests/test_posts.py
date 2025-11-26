import pytest

@pytest.mark.asyncio
async def test_create_post(client):
    await client.post("/api/auth/register", json={
        "username": "poster",
        "email": "poster@example.com",
        "password": "password123"
    })

    login = await client.post("/api/auth/login", data={
        "username": "poster",
        "password": "password123"
    })
    token = login.json()["access_token"]

    resp = await client.post(
        "/posts/",
        json={"title": "My Post", "content": "Hello world"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Post"
    assert data["content"] == "Hello world"


@pytest.mark.asyncio
async def test_get_posts(client):
    resp = await client.get("/posts/")
    assert resp.status_code == 200
