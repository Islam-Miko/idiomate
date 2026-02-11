import logging

from aiogram import F, Router, types
from aiogram.filters import Command

from src.infrastructure.settings import get_settings
from src.tracking.application.dto import CreateUserDTO, UpdateLocationDTO
from src.tracking.application.use_cases import CreateLocationUseCase, GetUserStatusUseCase, UpdateLocationUseCase

settings = get_settings()
logger = logging.getLogger(__name__)
router = Router()


@router.message(F.location)
async def handle_location(message: types.Message, create_location_use_case: CreateLocationUseCase):
    logger.info(f"Received location from user {message.from_user.id}")

    dto = UpdateLocationDTO(
        user_id=str(message.from_user.id),
        lat=message.location.latitude,
        lon=message.location.longitude,
        recorded_at=message.date,
    )
    user_dto = CreateUserDTO(
        user_id=str(message.from_user.id),
        username=message.from_user.username,
        link=message.from_user.url,
    )

    await create_location_use_case.execute(dto, user_dto)


@router.edited_message(F.location)
async def update_tracking(message: types.Message, update_location_use_case: UpdateLocationUseCase):
    logger.info(f"Received edited location from user {message.from_user.id}")

    dto = UpdateLocationDTO(
        user_id=str(message.from_user.id),
        lat=message.location.latitude,
        lon=message.location.longitude,
        recorded_at=message.edit_date,
    )

    await update_location_use_case.execute(dto)


@router.message(Command("status"))
async def cmd_status(message: types.Message, get_status_use_case: GetUserStatusUseCase):
    user_id = str(message.from_user.id)

    if user_id not in (settings.ADMIN_ONE, settings.ADMIN_TWO):
        await message.answer("Вы не авторизованы для использования этой команды.")
        return
    if user_id == settings.ADMIN_ONE:
        target_id = settings.ADMIN_TWO
    else:
        target_id = settings.ADMIN_ONE
    # 1. Вызываем Use Case
    status = await get_status_use_case.execute(target_id)
    await message.answer(status, parse_mode="HTML")
