import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and sessionmaker, which will be used for all queries.

        :param self: Represent the instance of the class
        :param url: str: Create the engine
        :return: A new instance of the class
        :doc-author: Trelent
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(autoflush=False, autocommit=False,
                                                                     bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a coroutine that returns an async context manager.
        The context manager yields a session, and then closes it when the block ends.
        If there's an exception in the block, it rolls back any uncommitted changes to the database.

        :param self: Represent the instance of the class
        :return: A context manager, which is an object that has __enter__ and __exit__ methods
        :doc-author: Naboka Artem
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    The get_db function is a coroutine that returns an open database session.
    It will run the async with block, which ensures that the session will be closed when we are done with it.
    The yield from expression is similar to return in that it gives a value back to the caller of this function;
    the difference is that yield from delegates to another generator.

    :return: A context manager that can be used to interact with the database
    :doc-author: Naboka Artem
    """
    async with sessionmanager.session() as session:
        yield session
