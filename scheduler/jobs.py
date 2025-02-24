import asyncio
import logging
from datetime import datetime

from aiogram.client.bot import Bot
import psycopg
from aiogram.exceptions import AiogramError
from aiogram.types import MessageEntity
from pytz import timezone

import config
import utils
from bot_instance import BotSingleton
from exceptions import ScheduleNotFoundError, SameScheduleError
from models import ScheduleModel, ChatModel
from repositories import ChatRepository
from repositories.schedule_repository import ScheduleRepository


async def edit_messages_in_chats(bot: Bot, chats_for_edit: list[ChatModel]):
    current_week_type = utils.get_current_week_type()

    schedule_repository = ScheduleRepository()
    for chat in chats_for_edit:
        schedule: ScheduleModel

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
        finally:
            await asyncio.sleep(0.05)


async def edit_schedule_messages_in_all_chats_job():
    bot = BotSingleton(config.telegram_token)

    chat_repository = ChatRepository()
    try:
        async with chat_repository:
            offset = 0
            limit = 10
            while True:
                chats_for_edit = await chat_repository.get_chats_for_edit(offset, limit)

                if not chats_for_edit:
                    break

                await edit_messages_in_chats(bot, chats_for_edit)

                offset += limit
                await asyncio.sleep(1)
    except psycopg.Error as exception:
        logging.error(f"Database error in chat_repository: {exception}")
        return


async def update_schedule_message_in_specific_chat_job(
    chat_telegram_id: int,
    schedule_text: str,
    schedule_message_entities: list[MessageEntity],
) -> bool:
    bot = BotSingleton(config.telegram_token)

    schedule_exists: bool

    schedule_repository = ScheduleRepository()
    async with schedule_repository:
        try:
            schedule = await schedule_repository.get_schedule(
                chat_telegram_id, utils.get_current_week_type()
            )
        except ScheduleNotFoundError:
            return False

    chat_repository = ChatRepository()
    async with chat_repository:
        chat = await chat_repository.get_chat(chat_telegram_id=chat_telegram_id)
        if not chat.schedule_message_to_edit_id:
            return False

    same_schedule_text = schedule_text == schedule.schedule
    same_schedule_formatting = set(schedule.message_entities) == set(
        schedule_message_entities
    )

    if same_schedule_text and same_schedule_formatting:
        raise SameScheduleError

    await bot.edit_message_text(
        text=schedule.schedule,
        message_id=chat.schedule_message_to_edit_id,
        chat_id=chat_telegram_id,
        entities=schedule.message_entities,
    )

    return True
