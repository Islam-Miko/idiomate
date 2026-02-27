import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import BinaryIO
from zoneinfo import ZoneInfo

from src.infrastructure.settings import get_settings
from src.tracking.application.dto import CreateUserDTO, UpdateLocationDTO
from src.tracking.application.protocols import IGeoService, IMapGenerator, INotifier
from src.tracking.domain.entities import Coordinates, Tracking, User
from src.tracking.domain.protocols import ILocationRepository, IUserRepository, IUserStatusRepository

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
    def __init__(self, repo: ILocationRepository, user_status_repo: IUserStatusRepository, notifier: INotifier):
        self.repo = repo
        self.user_status_repo = user_status_repo
        self.notifier = notifier

    async def execute(self, dto: UpdateLocationDTO):
        logger.info(f"Updating location for user {dto.user_id}")

        user_status = await self.user_status_repo.get_by_user_id(dto.user_id)

        if user_status:
            last_sent = user_status.last_sent
            logger.debug(f"Last sent time for user {dto.user_id}: {last_sent}")
            logger.debug(f"Current recorded_at time: {dto.recorded_at}")
            delta = dto.recorded_at - last_sent
            logger.debug(f"Time since last location: {delta}")
            if delta > timedelta(minutes=10):
                if dto.user_id == settings.ADMIN_ONE:
                    target_id = settings.ADMIN_TWO
                else:
                    target_id = settings.ADMIN_ONE
                location_link = f"https://2gis.kg/geo/{dto.lon},{dto.lat}"
                await self.notifier.notify(
                    target_id,
                    f"User {dto.user_id} has not sent location for more than 10 minutes. Last location: {location_link}",
                )
        await self.user_status_repo.update_last_sent(dto.user_id, dto.recorded_at)

        new_coords = Coordinates(dto.lat, dto.lon)
        recorded_at = dto.recorded_at

        last_entity = await self.repo.get_last_tracking(dto.user_id)

        if last_entity:
            dist = last_entity.location.distance_to(new_coords)
            logger.debug(f"Distance from last location: {dist:.2f}m")

            time_delta = recorded_at - last_entity.recorded_at
            logger.debug(f"Time delta: {recorded_at}")
            logger.debug(f"Last time delta: {last_entity.recorded_at}")

            if time_delta < timedelta(minutes=5):
                required_dist = STRICT_DISTANCE_METERS
                mode = "strict"
            else:
                required_dist = RELAXED_DISTANCE_METERS
                mode = "relaxed"

            logger.debug(
                f"Check: UserId={dto.user_id}, Mode={mode}, "
                f"TimeDelta={time_delta.total_seconds()}s, Dist={dist:.1f}m, Required={required_dist}m"
            )

            if dist < required_dist:
                logger.info(
                    f"Skipping update for {dto.user_id}: "
                    f"moved {dist:.1f}m (limit {required_dist}m) in {time_delta.total_seconds()}s"
                )
                await self.repo.commit()
                return

        new_entity = Tracking(user_id=dto.user_id, location=new_coords, recorded_at=recorded_at)
        await self.repo.add(new_entity)
        await self.repo.commit()

        logger.info(f"Location updated for user {dto.user_id}")


class GetUserStatusUseCase:
    def __init__(
        self,
        location_repo: ILocationRepository,
        user_repo: IUserRepository,
        geo_service: IGeoService,
        map_generator: IMapGenerator,
    ):
        self.location_repo = location_repo
        self.user_repo = user_repo
        self.geo_service = geo_service
        self.map_generator = map_generator

    async def execute(self, user_id: str) -> tuple[str, BinaryIO]:
        trackings = await self.location_repo.get_locations(user_id)
        user = await self.user_repo.get_by_user_id(user_id)

        username = user.username if user else "Unknown"

        if not trackings:
            return f"👤 <b>User:</b> @{username}\n🚫 <b>Status:</b> No location data found.", BytesIO()

        current = trackings[0]

        recorded_at_utc = current.recorded_at
        if recorded_at_utc.tzinfo is None:
            recorded_at_utc = recorded_at_utc.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)
        duration = now_utc - recorded_at_utc
        duration_str = str(duration).split(".")[0]

        curr_time_bishkek = recorded_at_utc.astimezone(BISHKEK_TZ)
        curr_time_str = curr_time_bishkek.strftime("%d.%m.%Y %H:%M")
        # --------------------------------------

        address = await self.geo_service.get_address(current.location.latitude, current.location.longitude)
        address = self._clean_address(address)

        curr_link = f"https://2gis.kg/geo/{current.location.longitude},{current.location.latitude}"

        text_lines = [
            f"👤 <b>User:</b> @{username}",
            "",
            f"📍 <b>Address:</b> {address}",
            f"⏳ <b>Duration:</b> {duration_str}",
            f"🔗 <a href='{curr_link}'>Open in 2GIS</a>",
            f"🕒 Since: <code>{curr_time_str}</code>",
        ]

        map_bytes = self.map_generator.generate_map(trackings)
        if len(trackings) > 1:
            text_lines.append("")
            text_lines.append("📋 <b>Previous History:</b>")
            for i in range(1, len(trackings)):
                t_old = trackings[i]
                t_newer = trackings[i - 1]

                dist_meters = t_old.location.distance_to(t_newer.location)

                time_diff = (t_newer.recorded_at - t_old.recorded_at).total_seconds()

                motion_status = self._get_motion_status(dist_meters, time_diff)

                t_utc = t_old.recorded_at.replace(tzinfo=timezone.utc)
                hist_time_str = t_utc.astimezone(BISHKEK_TZ).strftime("%d.%m.%Y %H:%M")
                line = f"{i} <code>{hist_time_str}</code> — " f"{motion_status} (↘️ {int(dist_meters)}m)"
                text_lines.append(line)

        return "\n".join(text_lines), map_bytes

    def _clean_address(self, raw_address: str) -> str:
        # Пример входа: "Kurchatova kochosu, Bishkek, Bishkek 720038, KGZ"
        if not raw_address:
            return "Unknown"

        parts = raw_address.split(",")

        # Фильтруем части
        clean_parts = []
        seen = set()

        for part in parts:
            p = part.strip()
            # Убираем индексы (числа) и коды стран
            if p.isdigit() or p in ["KGZ", "KG", "Kyrgyzstan"]:
                continue
            # Убираем дубликаты (Bishkek, Bishkek)
            if p in seen:
                continue

            clean_parts.append(p)
            seen.add(p)

        # Берем только первые 2-3 части (Улица, Город), остальное обычно лишнее
        return ", ".join(clean_parts[:2])

    def _get_motion_status(self, dist_meters: float, time_diff_seconds: float) -> str:
        if time_diff_seconds == 0:
            return "🛑 0 km/h"

        speed_mps = dist_meters / time_diff_seconds
        speed_kmh = speed_mps * 3.6

        speed_fmt = f"{speed_kmh:.1f} km/h"

        if speed_kmh < 1.0:
            return f"🛑 {speed_fmt}"
        if speed_kmh < 6.0:
            return f"🚶 {speed_fmt}"
        if speed_kmh < 20.0:
            return f"🏃 {speed_fmt}"
        return f"🚗 {speed_fmt}"


class GetUserStatusUseCase2:
    def __init__(
        self,
        location_repo: ILocationRepository,
    ):
        self.location_repo = location_repo

    async def execute(self, user_id: str) -> tuple[int, int]:
        tracking = await self.location_repo.get_last_tracking(user_id)

        current = tracking
        return current.location.latitude, current.location.longitude
