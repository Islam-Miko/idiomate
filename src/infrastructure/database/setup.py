from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.settings import Settings, get_settings


class DatabaseHelper:
    def __init__(self, settings: Settings):
        self._engine = None
        self._session_factory = None
        self.settings = settings

    def setup(self, pool_size: int = 5, max_overflow: int = 10, echo: bool = False):
        self._engine = create_async_engine(
            self.settings.DATABASE_URL,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self):
        if self._engine:
            await self._engine.dispose()

    @property
    def session_factory(self):
        if self._session_factory is None:
            raise RuntimeError("Database is not initialized. Call db_helper.setup() first.")
        return self._session_factory


db_helper = DatabaseHelper(get_settings())


async def get_session() -> AsyncIterator[AsyncSession]:
    async with db_helper.session_factory() as s:
        yield s
