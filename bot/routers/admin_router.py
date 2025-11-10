import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.services import AdminService
from core.settings import get_settings

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class AddIdiomsState(StatesGroup):
    textfile = State()


@router.message(Command("add_idioms"))
async def start_command(
    message: Message,
    state: FSMContext,
):
    admin_id = get_settings().ADMIN_ID
    logger.debug(f"Admin IDs: {admin_id}, User ID: {message.from_user.id}")
    if message.from_user.id != admin_id:
        return
    await state.set_state(AddIdiomsState.textfile)
    await message.answer("Send a text file with idioms, one per line.")


@router.message(F.document.mime_type == "text/plain", AddIdiomsState.textfile)
async def handle_file(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await AdminService.save_file(file_id=message.document.file_id, bot=bot)
    await message.answer("Thank you! The idioms are being processed.")
