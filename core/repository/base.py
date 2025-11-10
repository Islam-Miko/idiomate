from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models.base import Base

Model = TypeVar("Model", bound=Base)


class BaseRepository(Generic[Model]):
    model: Type[Model]

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    @property
    def session(self) -> AsyncSession:
        return self.__session

    async def get_by_id(self, id: int) -> Model | None:
        return await self.session.get(self.model, id)

    async def delete_instance(self, instance: Model) -> None:
        await self.session.delete(instance)

    async def all(self) -> list[Model]:
        return await self.session.scalars(select(self.model))

    def add(self, instance: Model) -> None:
        self.__session.add(instance)
