from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import utils
from exceptions import ScheduleNotFoundError
from repositories import (
    ChatRepository,
    ScheduleRepository,
)

router = Router()


@router.message(Command("send_schedule"))
async def cmd_send_schedule(message: Message):
    chat_repository = ChatRepository()
    async with chat_repository:
        if not await chat_repository.chat_exists(message.chat.id):
            await message.answer(
                "Цього чату немає в базі даних бота. Додайте його командою /add_chat"
            )
            return

        current_week_type = utils.get_current_week_type()

        schedule_repository = ScheduleRepository()
        async with schedule_repository:
            try:
                schedule = await schedule_repository.get_schedule(
                    message.chat.id, current_week_type
                )
            except ScheduleNotFoundError:
                await message.answer(
                    "Розкладу для цього чату немає в базі даних. Перед надсиланням розкладу ви маєте додати нижній та верхній його варіанти за допомогою команди /add_update_schedule"
                )
                return

        bot_message = await message.answer(
            schedule.schedule,
            entities=schedule.message_entities,
            parse_mode=ParseMode.HTML,
        )
        await chat_repository.add_update_schedule_message_to_edit_id(
            bot_message.message_id, message.chat.id
        )
