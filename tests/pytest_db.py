import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from src.database.db import DatabaseSessionManager, get_db
from src.conf.config import config

TEST_DB_URL = config.DB_URL


@pytest.fixture
def db_session_manager():
    return DatabaseSessionManager(TEST_DB_URL)


@pytest.mark.asyncio
async def test_session_manager_initialization(db_session_manager):
    assert db_session_manager._engine is not None
    assert db_session_manager._session_maker is not None


@pytest.mark.asyncio
async def test_session_context_manager_success(db_session_manager):
    async with db_session_manager.session() as session:
        assert session is not None


@pytest.mark.asyncio
async def test_get_db():
    mock_session = AsyncMock()

    mock_session_manager = AsyncMock()
    mock_session_manager.__aenter__.return_value = mock_session
    mock_session_manager.__aexit__.return_value = AsyncMock()

    with patch("src.database.db.sessionmanager.session", return_value=mock_session_manager):
        async for session in get_db():
            assert session is mock_session

    mock_session_manager.__aenter__.assert_called_once()
    mock_session_manager.__aexit__.assert_called_once()