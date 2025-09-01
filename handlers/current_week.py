from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import get_current_week_type

router = Router()


@router.message(Command("current_week"))
async def cmd_get_schedule(message: Message):
    await message.answer(get_current_week_type())
