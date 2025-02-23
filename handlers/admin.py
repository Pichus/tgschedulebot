import asyncio
import logging

from aiogram import Router, F
from aiogram.exceptions import AiogramError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import config
from repositories import UserRepository

admin_router = Router()
admin_router.message.filter(F.from_user.id.in_(config.admin_user_ids))


class NotifyUsers(StatesGroup):
    sending_notification_text = State()


@admin_router.message(StateFilter(None), Command("notify_users"))
async def cmd_notify_users(message: Message, state: FSMContext):
    print(config.admin_user_ids)
    await message.answer("Надішліть текст сповіщення")
    await state.set_state(NotifyUsers.sending_notification_text)


@admin_router.message(
    StateFilter(NotifyUsers.sending_notification_text),
)
async def notification_text_response(message: Message, state: FSMContext):
    await message.answer("текст сповіщення отримано, починаю розсилку")

    user_repository = UserRepository()
    async with user_repository:
        offset = 0
        limit = 10
        while True:
            users = await user_repository.get_all_users(limit, offset)
            if not users:
                break

            for user in users:
                try:
                    await message.bot.send_message(
                        chat_id=user.user_telegram_id, text=message.text
                    )
                    await asyncio.sleep(0.05)
                except AiogramError:
                    logging.error(
                        f"error sending message to {user.user_name} ; {user.user_telegram_id}"
                    )

            offset += limit
            await asyncio.sleep(1)

    await state.clear()
