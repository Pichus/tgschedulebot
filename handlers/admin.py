import asyncio
import logging

import gspread
from aiogram import Router, F
from aiogram.exceptions import AiogramError
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import config
import utils
from parser import apply_merges
from parser import fetch_schedules_dictionary, ScheduleDict, process_schedule_dictionary
from parser.parser import get_links_matrix
from repositories import UserRepository, GeneratedScheduleRepository

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


@admin_router.message(Command("generate_schedule"))
async def cmd_generate_schedule(message: Message, command: CommandObject):
    command_usage = "/generate_schedule <посилання_на_розклад> <назва_аркуша> <№ рядка з назвами груп> <буква стовпця з днями тижня> <буква стовпця з часом> <буква стовпця, де починаються назви груп>"

    if command.args is None:
        await message.answer("немає параметрів\n" + command_usage)
        return

    try:
        (
            spreadsheet_url,
            sheet_name,
            group_index_row,
            days_col,
            time_interval_col,
            group_indexes_start_col,
        ) = command.args.split(" ")
    except ValueError:
        await message.answer("неправильний формат команди\n" + command_usage)
        return

    schedules_dictionary: dict[str, ScheduleDict] = fetch_schedules_dictionary(
        config.google_credentials,
        spreadsheet_url,
        sheet_name,
        int(group_index_row) - 1,
        utils.char_to_num(days_col) - 1,
        utils.char_to_num(time_interval_col) - 1,
        utils.char_to_num(group_indexes_start_col) - 1,
    )

    links_matrix = get_links_matrix(
        config.google_credentials, spreadsheet_url, sheet_name
    )
    client = gspread.service_account_from_dict(
        config.google_credentials,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    metadata = client.http_client.fetch_sheet_metadata(
        gspread.utils.extract_id_from_url(spreadsheet_url)
    )["sheets"][0]["merges"]
    apply_merges(links_matrix, metadata)

    generated_schedule_repository = GeneratedScheduleRepository()
    async with generated_schedule_repository:
        for group_index, schedule_dict in schedules_dictionary.items():
            schedules = process_schedule_dictionary(schedule_dict, links_matrix)
            try:
                await generated_schedule_repository.upsert_schedule(
                    group_index, "верхній", schedules[0]
                )
                await generated_schedule_repository.upsert_schedule(
                    group_index, "нижній", schedules[1]
                )
            except Exception as e:
                logging.error(e)
                await message.answer("Упс, щось пішло не так")
                return

    await message.answer("Розклади успішно додано в базу даних")
