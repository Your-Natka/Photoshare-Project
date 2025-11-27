import pytest
from unittest.mock import AsyncMock
from app.cache import redis_cache
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    class FakeRedis:
        storage = {}

        async def set(self, key, value):
            self.storage[key] = value

        async def get(self, key):
            value = self.storage.get(key, None)
            if value is not None:
                return value.encode()   
            return None

        async def ping(self):
            return True

    fake = FakeRedis()

    monkeypatch.setattr(redis_cache, "set", fake.set)
    monkeypatch.setattr(redis_cache, "get", fake.get)
    monkeypatch.setattr(redis_cache, "ping", fake.ping)

    return fake


@pytest.mark.asyncio
async def test_redis_ping(monkeypatch):
    mock_ping = AsyncMock(return_value=True)
    monkeypatch.setattr(redis_cache, "ping", mock_ping)
    result = await redis_cache.ping()
    assert result is True
    
@pytest.mark.asyncio
async def test_redis_connection():
    # Встановлюємо ключ
    await redis_cache.set("test_key", "value")
    val = await redis_cache.get("test_key")
    
    # Redis повертає bytes, тому декодуємо
    assert val.decode() == "value"