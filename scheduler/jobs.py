import logging
from datetime import datetime

import psycopg
from aiogram.exceptions import AiogramError
from pytz import timezone

import config
import utils
from bot_instance import BotSingleton
from models import ScheduleModel
from repositories import ChatRepository
from repositories.schedule_repository import ScheduleRepository


async def update_schedule_messages_in_all_chats_job():
    bot = BotSingleton(config.telegram_token)

    chat_repository = ChatRepository()
    try:
        async with chat_repository:
            chats_for_edit = await chat_repository.get_chats_for_edit()
    except psycopg.Error as exception:
        logging.error(f"Database error in chat_repository: {exception}")
        return

    if not chats_for_edit:
        return

    current_week_type = utils.get_current_week_type()

    for chat in chats_for_edit:
        schedule: ScheduleModel

        schedule_repository = ScheduleRepository()
        try:
            async with schedule_repository:
                schedule = await schedule_repository.get_schedule(
                    chat.chat_telegram_id, current_week_type
                )
        except psycopg.Error as exception:
            logging.error(
                f"Database error in schedule_repository for chat {chat.chat_telegram_id}: {exception}"
            )
            continue

        schedule.schedule += f"\n\nостаннє оновлення {datetime.now(timezone(config.cron_timezone)).strftime("%H:%M %d-%m-%Y")}"

        try:
            await bot.edit_message_text(
                text=schedule.schedule,
                message_id=chat.schedule_message_to_edit_id,
                chat_id=chat.chat_telegram_id,
                entities=schedule.message_entities,
            )
        except AiogramError as exception:
            logging.error(
                f"Failed to edit message for chat {chat.chat_telegram_id}: {exception}"
            )


async def update_schedule_message_in_specific_chat_job(chat_telegram_id: int) -> bool:
    bot = BotSingleton(config.telegram_token)

    schedule_exists: bool

    schedule_repository = ScheduleRepository()
    async with schedule_repository:
        schedule = await schedule_repository.get_schedule(
            chat_telegram_id, utils.get_current_week_type()
        )
        schedule_exists = bool(schedule.schedule)

    if schedule_exists:
        return False

    chat_repository = ChatRepository()
    async with chat_repository:
        chat = await chat_repository.get_chat(chat_telegram_id=chat_telegram_id)

    await bot.edit_message_text(
        text=schedule.schedule,
        message_id=chat.schedule_message_to_edit_id,
        chat_id=chat_telegram_id,
        entities=schedule.message_entities,
    )
