import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from src.infrastructure.settings import get_settings
from src.tracking.application.dto import CreateUserDTO, UpdateLocationDTO
from src.tracking.domain.entities import Coordinates, Tracking, User
from src.tracking.domain.protocols import ILocationRepository, IUserRepository

settings = get_settings()
STRICT_DISTANCE_METERS = settings.STRICT_DISTANCE_METERS
RELAXED_DISTANCE_METERS = settings.RELAXED_DISTANCE_METERS
BISHKEK_TZ = ZoneInfo("Asia/Bishkek")

logger = logging.getLogger(__name__)


class CreateLocationUseCase:
    def __init__(self, location_repo: ILocationRepository, user_repo: IUserRepository):
        self.location_repo = location_repo
        self.user_repo = user_repo

    async def execute(self, location_dto: UpdateLocationDTO, user_dto: CreateUserDTO) -> None:
        user = await self.user_repo.get_by_user_id(user_dto.user_id)

        if not user:
            # Опционально: создаем юзера на лету, если его нет
            logger.info(f"New user detected: {user_dto.user_id}")
            await self.user_repo.create(
                User(
                    user_id=user_dto.user_id,
                    username=user_dto.username,
                    link=user_dto.link,
                )
            )
        logger.info(f"Creating location for user {location_dto.user_id} at ({location_dto.lat}, {location_dto.lon})")
        tracking = Tracking(
            user_id=location_dto.user_id,
            location=Coordinates(location_dto.lat, location_dto.lon),
            recorded_at=location_dto.recorded_at,
        )

        await self.location_repo.add(tracking)
        await self.location_repo.commit()

        logger.debug(f"Location saved for user {location_dto.user_id}")


class UpdateLocationUseCase:
    def __init__(self, repo: ILocationRepository):
        self.repo = repo

    async def execute(self, dto: UpdateLocationDTO):
        logger.info(f"Updating location for user {dto.user_id}")

        # 1. Конвертируем входные данные в Доменные объекты
        new_coords = Coordinates(dto.lat, dto.lon)
        recorded_at = dto.recorded_at

        # 2. Получаем последнюю позицию
        last_entity = await self.repo.get_last_tracking(dto.user_id)

        # 3. БИЗНЕС-ЛОГИКА: Фильтр шума
        if last_entity:
            dist = last_entity.location.distance_to(new_coords)
            logger.debug(f"Distance from last location: {dist:.2f}m")

            time_delta = recorded_at - last_entity.recorded_at
            logger.debug(f"Time delta: {recorded_at}")
            logger.debug(f"Last time delta: {last_entity.recorded_at}")

            # В. Определяем порог (Threshold)
            if time_delta < timedelta(minutes=3):
                required_dist = STRICT_DISTANCE_METERS
                mode = "strict"
            else:
                required_dist = RELAXED_DISTANCE_METERS
                mode = "relaxed"

            logger.debug(
                f"Check: UserId={dto.user_id}, Mode={mode}, "
                f"TimeDelta={time_delta.total_seconds()}s, Dist={dist:.1f}m, Required={required_dist}m"
            )

            # Г. Принимаем решение
            if dist < required_dist:
                logger.info(
                    f"Skipping update for {dto.user_id}: "
                    f"moved {dist:.1f}m (limit {required_dist}m) in {time_delta.total_seconds()}s"
                )
                return  # <-- ВЫХОДИМ, НЕ СОХРАНЯЕМ

        # 4. Если проверка прошла - сохраняем
        new_entity = Tracking(user_id=dto.user_id, location=new_coords, recorded_at=recorded_at)
        await self.repo.add(new_entity)
        await self.repo.commit()

        logger.info(f"Location updated for user {dto.user_id}")


class GetUserStatusUseCase:
    def __init__(self, location_repo: ILocationRepository, user_repo: IUserRepository):
        self.location_repo = location_repo
        self.user_repo = user_repo

    async def execute(self, user_id: str) -> str:
        # 1. Достаем последнюю запись
        trackings = await self.location_repo.get_locations(user_id)

        user = await self.user_repo.get_by_user_id(user_id)

        if not trackings:
            return f"👤 <b>User:</b> @{user.username or 'Unknown'}\n 🚫 <b>Status:</b> No location data found."

        # 2. Текущая (самая свежая) запись
        current = trackings[0]

        # Формируем правильную ссылку для Google Maps
        # q=lat,lon открывает пин в приложении
        curr_link = (
            f"https://www.google.com/maps/search/?api=1&query={current.location.latitude},{current.location.longitude}"
        )

        # Конвертируем в Bishkek timezone перед форматированием
        curr_time_bishkek = current.recorded_at.astimezone(BISHKEK_TZ)
        curr_time = curr_time_bishkek.strftime("%d.%m.%Y %H:%M")

        text_lines = [
            f"👤 <b>User:</b> @{user.username or 'Unknown'}",
            "",  # Пустая строка для отступа
            "📍 <b>Current Location:</b>",
            f"🔗 <a href='{curr_link}'>Open in Google Maps</a>",
            f"🕒 Since: <code>{curr_time}</code>",  # code делает шрифт моноширинным (красиво для цифр)
        ]

        # 3. История (остальные 4 записи)
        if len(trackings) > 1:
            text_lines.append("")  # Отступ
            text_lines.append("📋 <b>Previous History:</b>")

            for i, t in enumerate(trackings[1:], 1):
                # Ссылка на точку истории
                hist_link = (
                    f"https://www.google.com/maps/search/?api=1&query={t.location.latitude},{t.location.longitude}"
                )

                # Конвертируем в Bishkek timezone
                hist_time_bishkek = t.recorded_at.astimezone(BISHKEK_TZ)
                hist_time = hist_time_bishkek.strftime("%d.%m %H:%M")  # Тут год можно убрать для краткости

                # Формат: "1. 🔗 11.02 14:00" (Ссылка прямо на времени или иконке)
                line = f"{i}️⃣ <a href='{hist_link}'>Map</a> " f"— <code>{hist_time}</code>"
                text_lines.append(line)

        return "\n".join(text_lines)
