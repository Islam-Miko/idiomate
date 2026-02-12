from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.infrastructure.database.setup import DatabaseHelper
from src.tracking.application.use_cases import CreateLocationUseCase, GetUserStatusUseCase, UpdateLocationUseCase
from src.tracking.infrastructure.database.repositories import TrackingRepo, UserRepo, UserStatusRepo
from src.tracking.infrastructure.services.geocoding import ArcGISGeoService
from src.tracking.infrastructure.services.telegram_notifier import TelegramNotifier


class DependencyInjectionMiddleware(BaseMiddleware):
    def __init__(self, database: DatabaseHelper):
        self.db_helper = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.db_helper.session_factory() as session:
            repo = TrackingRepo(session)
            user_repo = UserRepo(session)
            user_status_repo = UserStatusRepo(session)
            telegram_notifier = TelegramNotifier(data["bot"])
            geo_service = ArcGISGeoService()

            create_location_use_case = CreateLocationUseCase(repo, user_repo)
            update_location_use_case = UpdateLocationUseCase(repo, user_status_repo, telegram_notifier)
            get_status_use_case = GetUserStatusUseCase(repo, user_repo, geo_service)

            data["update_location_use_case"] = update_location_use_case
            data["create_location_use_case"] = create_location_use_case
            data["get_status_use_case"] = get_status_use_case

            return await handler(event, data)
