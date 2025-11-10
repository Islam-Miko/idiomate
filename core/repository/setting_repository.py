from core.db.models import SettingModel

from .base import BaseRepository


class SettingRepository(BaseRepository[SettingModel]):
    model = SettingModel

    async def get_by_key(self, key: int) -> SettingModel:
        result = await self.session.get(self.model, key)
        return result
