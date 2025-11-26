import pytest
from unittest.mock import AsyncMock
from app.cache import redis_cache

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