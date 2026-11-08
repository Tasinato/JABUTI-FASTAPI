from unittest.mock import AsyncMock

import pytest
from redis.exceptions import ConnectionError

import src.cache.redis_client as cache


@pytest.mark.asyncio
async def test_redis_failure_is_optional(monkeypatch):
    fake = AsyncMock()
    fake.get.side_effect = ConnectionError("offline")
    fake.set.side_effect = ConnectionError("offline")
    fake.delete.side_effect = ConnectionError("offline")
    monkeypatch.setattr(cache, "redis", fake)
    monkeypatch.setattr(cache, "CACHE_ENABLED", True)
    assert await cache.cache_get("test") is None
    await cache.cache_set("test", {"value": 1})
    await cache.cache_delete("test")


@pytest.mark.asyncio
async def test_cached_json_and_ttl(monkeypatch):
    fake = AsyncMock()
    fake.get.return_value = '{"value": 1}'
    monkeypatch.setattr(cache, "redis", fake)
    monkeypatch.setattr(cache, "CACHE_ENABLED", True)
    assert await cache.cache_get("test") == {"value": 1}
    await cache.cache_set("test", {"value": 1}, ttl=25)
    fake.set.assert_awaited_once_with("test", '{"value": 1}', ex=25)
    fake.get.return_value = "invalid JSON"
    assert await cache.cache_get("test") is None
