from sqlalchemy import func, select

from core.db.models import IdiomModel

from .base import BaseRepository


class IdiomRepository(BaseRepository[IdiomModel]):
    model = IdiomModel

    async def get_random_idioms(self, limit: int = 10) -> list[IdiomModel]:
        result = await self.session.execute(
            select(IdiomModel).order_by(func.random()).limit(limit)
        )
        return result.scalars().all()
