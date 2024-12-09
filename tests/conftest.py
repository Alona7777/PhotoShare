import asyncio
import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from unittest.mock import AsyncMock, patch


from main import app

from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter

from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.entity.models import Base, User, Photo
from src.database.db import get_db
from src.services.auth import auth_service

from src.repository import users as repositories_users
from src.repository import photos as repositories_photos


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user_admin = {"username": "deadpool", "email": "deadpool@example.com", "password": "12345678"}
test_user_new = {"username": "newuser", "email": "newuser@example.com", "password": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_test_users():
    async def init_users():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user_admin["password"])
            admin_user = User(username=test_user_admin["username"], email=test_user_admin["email"], password=hash_password,
                                verified=True, role="admin")
            session.add(admin_user)
            await session.commit()

            new_user = User(username=test_user_new["username"], email=test_user_new["email"], password=auth_service.get_password_hash(test_user_new["password"]),
                            verified=True, role="user")
            session.add(new_user)
            await session.commit()

            new_user = await repositories_users.get_user_by_email(test_user_new["email"], session)
            for i in range(5):
                photo = Photo(title=f"Photo {i}", description=f"Description {i}", file_path=f"file_path_{i}", user_id=new_user.id)
                session.add(photo)
            await session.commit()

    asyncio.run(init_users())

    return {
        "admin_user": test_user_admin["email"],
        "new_user": test_user_new["email"]
    }


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
async def admin_user(init_test_users):
    async with TestingSessionLocal() as db:
        admin_user = await repositories_users.get_user_by_email(init_test_users["admin_user"], db)
        return admin_user


@pytest_asyncio.fixture()
async def new_user_with_photos(init_test_users):
    async with TestingSessionLocal() as db:
        new_user = await repositories_users.get_user_by_email(init_test_users["new_user"], db)
        return new_user


@pytest_asyncio.fixture()
async def get_token(admin_user):
    token = await auth_service.create_access_token(data={"sub": admin_user.email})
    return token

async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(scope="function", autouse=True)
async def mock_limiter():
    redis_mock = AsyncMock()
    with patch.object(FastAPILimiter, "redis", redis_mock):
        with patch.object(FastAPILimiter, "identifier", AsyncMock(return_value="test_identifier")):
            yield
