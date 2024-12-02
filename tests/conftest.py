import asyncio
import pytest
import pytest_asyncio

from unittest.mock import AsyncMock, patch

from main import app

from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter

from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.entity.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service
from httpx import AsyncClient, ASGITransport

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "deadpool", "email": "deadpool@example.com", "password": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                                verified=True, role="admin")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest_asyncio.fixture(scope="module")
async def client():
    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(scope="function", autouse=True)
async def mock_limiter():
    redis_mock = AsyncMock()
    with patch.object(FastAPILimiter, "redis", redis_mock):
        with patch.object(FastAPILimiter, "identifier", AsyncMock(return_value="test_identifier")):
            yield

