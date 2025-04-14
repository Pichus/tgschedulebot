# One Command to
# rule them all
# One Command to
# find them
# One Command to
# Bring them all
# and in the darkness
# Bind them

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

import utils
from exceptions import ScheduleNotFoundError
from keyboards.chat_choice import chat_choice_keyboard
from models import UserModel
from repositories import (
    GeneratedScheduleRepository,
    ScheduleRepository,
    ChatRepository,
    UserRepository,
)
from utils import parse_group_index

router = Router()


class OneCommandStatesGroup(StatesGroup):
    choosing_chat = State()
    entering_group_index = State()


@router.message(StateFilter(None), Command("one_command"))
async def cmd_one_command(message: Message, state: FSMContext):
    user_chat_names: list[str] = []

    user_repository = UserRepository()
    async with user_repository:
        user_exists = await user_repository.user_exists(message.from_user.id)

        if not user_exists:
            await user_repository.add_user(
                UserModel(
                    user_telegram_id=message.from_user.id,
                    user_name=message.from_user.full_name,
                )
            )

        offset = 0
        limit = 10
        while True:
            user_chats = await user_repository.get_user_chats(
                message.from_user.id, offset=offset, limit=limit
            )

            if not user_chats:
                break

            user_chat_names += [chat.chat_name for chat in user_chats]

            offset += limit

    if not user_chat_names:
        await message.answer(
            "Схоже, у вас немає доданих чатів. Щоб додати чат, скористайтесь командою /add_chat у потрібному чаті"
        )
    else:
        await message.answer(
            "В якому чаті ви бажаєте додати/оновити розклад?",
            reply_markup=chat_choice_keyboard(user_chat_names),
        )
        await state.set_state(OneCommandStatesGroup.choosing_chat)


@router.message(OneCommandStatesGroup.choosing_chat)
async def one_command_enter_group_index(message: Message, state: FSMContext):
    chosen_chat_name = message.text
    await state.update_data(chosen_chat_name=chosen_chat_name)

    calendar_emoji_id = "5433614043006903194"

    chat_repository = ChatRepository()
    async with chat_repository:
        chat_telegram_id = (
            await chat_repository.get_chat_telegram_id_by_name_and_user_telegram_id(
                chosen_chat_name, message.from_user.id
            )
        )

    chat = await message.bot.get_chat(chat_telegram_id)
    is_forum = chat.is_forum
    await state.update_data(is_forum=is_forum, chat_telegram_id=chat_telegram_id)

    if is_forum:
        try:
            created_topic = await message.bot.create_forum_topic(
                chat_telegram_id, "Авторозклад", icon_custom_emoji_id=calendar_emoji_id
            )
            await state.update_data(message_thread_id=created_topic.message_thread_id)
        except TelegramBadRequest as e:
            print(e)
            await message.answer(
                "Схоже, у бота немає дозволу створювати нові теми/топіки/треди :(\n"
            )
            return

    await message.answer(
        "Для якої групи потрібен розклад? (наприклад, к228, К228 або К-228)",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OneCommandStatesGroup.entering_group_index)
    return


@router.message(OneCommandStatesGroup.entering_group_index)
async def one_command_final_response(message: Message, state: FSMContext):
    user_data = await state.get_data()
    group_index = parse_group_index(message.text)

    generated_schedule_repository = GeneratedScheduleRepository()
    async with generated_schedule_repository:
        try:
            high_schedule = await generated_schedule_repository.get_schedule(
                group_index, "верхній"
            )
            low_schedule = await generated_schedule_repository.get_schedule(
                group_index, "нижній"
            )
        except ScheduleNotFoundError:
            await message.answer("Упс, щось пішло не так")
            await state.clear()
            return

    chat_telegram_id = user_data["chat_telegram_id"]

    schedule_repository = ScheduleRepository()
    async with schedule_repository:
        await schedule_repository.upsert_schedule(
            chat_telegram_id, "верхній", high_schedule.schedule
        )
        await schedule_repository.upsert_schedule(
            chat_telegram_id, "нижній", low_schedule.schedule
        )

    if utils.get_current_week_type() == "верхній":
        message_text = high_schedule.schedule
    else:
        message_text = low_schedule.schedule

    if user_data["is_forum"]:
        sent_message = await message.bot.send_message(
            chat_telegram_id,
            message_text,
            message_thread_id=user_data["message_thread_id"],
            parse_mode=ParseMode.HTML,
        )
    else:
        sent_message = await message.bot.send_message(
            chat_telegram_id,
            message_text,
            parse_mode=ParseMode.HTML,
        )

    chat_repository = ChatRepository()
    async with chat_repository:
        await chat_repository.add_update_schedule_message_to_edit_id(
            sent_message.message_id, chat_telegram_id
        )

    await message.answer("Успішно створено гілку для авторозкладу та надіслано розклад")
    await message.answer("Нижній розклад")
    await message.answer(low_schedule.schedule, parse_mode=ParseMode.HTML)
    await message.answer("Верхній розклад")
    await message.answer(high_schedule.schedule, parse_mode=ParseMode.HTML)

    await state.clear()
