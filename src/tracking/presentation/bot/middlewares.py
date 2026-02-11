from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.infrastructure.database.setup import DatabaseHelper
from src.tracking.application.use_cases import CreateLocationUseCase, GetUserStatusUseCase, UpdateLocationUseCase
from src.tracking.infrastructure.database.repositories import TrackingRepo, UserRepo


class DependencyInjectionMiddleware(BaseMiddleware):
    def __init__(self, database: DatabaseHelper):
        self.db_helper = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # ОТКРЫВАЕМ СЕССИЮ (Transaction Script)
        async with self.db_helper.session_factory() as session:
            # 1. Создаем Infrastructure (Repo) и даем ему сессию
            repo = TrackingRepo(session)
            user_repo = UserRepo(session)

            # 2. Создаем Application (UseCase) и даем ему Repo
            # Обрати внимание: UseCase не знает про сессию, он знает про Repo
            create_location_use_case = CreateLocationUseCase(repo, user_repo)
            update_location_use_case = UpdateLocationUseCase(repo)
            get_status_use_case = GetUserStatusUseCase(repo, user_repo)

            # 3. Кладем готовый UseCase в data, чтобы хендлер мог его взять
            data["update_location_use_case"] = update_location_use_case
            data["create_location_use_case"] = create_location_use_case
            data["get_status_use_case"] = get_status_use_case

            # Вызываем хендлер
            return await handler(event, data)
