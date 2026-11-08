import asyncio
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["API_KEY"] = "test-only-api-key-with-at-least-32-characters"
os.environ["CACHE_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import src.main as main
from src.models.database import Base, get_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def prepare():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_db():
        async with sessions() as session:
            yield session

    asyncio.run(prepare())
    monkeypatch.setattr(main, "engine", engine)
    main.app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(main.app) as test_client:
            test_client.headers["X-API-Key"] = os.environ["API_KEY"]
            yield test_client
    finally:
        main.app.dependency_overrides.clear()
        asyncio.run(engine.dispose())
