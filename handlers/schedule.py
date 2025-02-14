from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

import utils
from exceptions import ScheduleNotFoundError
from keyboards.chat_choice import chat_choice_keyboard
from keyboards.schedule_choice import schedule_type_choice_keyboard
from models import UserModel
from repositories import UserRepository, ChatRepository
from repositories.schedule_repository import ScheduleRepository
from scheduler.jobs import update_schedule_message_in_specific_chat_job

router = Router()


class ChooseScheduleType(StatesGroup):
    choosing_chat = State()
    choosing_schedule_type = State()
    sending_schedule = State()


@router.message(StateFilter(None), Command("add_update_schedule"))
async def cmd_add_schedule(message: Message, state: FSMContext):
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

        user_chats = await user_repository.get_user_chats(message.from_user.id)

    if not user_chats:
        await message.answer(
            "Схоже, у вас немає доданих чатів. Щоб додати чат, скористайтесь командою /add_chat у потрібному чаті"
        )
    else:
        user_chat_names = []
        for user_chat in user_chats:
            user_chat_names.append(user_chat.chat_name)

        await message.answer(
            "В якому чаті ви бажаєте додати/оновити розклад?",
            reply_markup=chat_choice_keyboard(user_chat_names),
        )
        await state.set_state(ChooseScheduleType.choosing_chat)


@router.message(ChooseScheduleType.choosing_chat, F.text)
async def choose_schedule_type(message: Message, state: FSMContext):
    await message.answer(f'Ви обрали чат "{message.text}"')
    await state.update_data(chosen_chat_name=message.text)

    schedule_repository = ScheduleRepository()
    async with schedule_repository:
        schedule_types = await schedule_repository.get_schedule_types()

    await message.answer(
        "Який розклад ви бажаєте додати/оновити?",
        reply_markup=schedule_type_choice_keyboard(schedule_types),
    )
    await state.set_state(ChooseScheduleType.choosing_schedule_type)


@router.message(
    ChooseScheduleType.choosing_schedule_type, F.text.in_(["нижній", "верхній"])
)
async def enter_schedule(message: Message, state: FSMContext):
    await state.update_data(chosen_schedule_type=message.text.lower())
    await message.answer(
        f"Ви обрали {message.text.lower()} розклад. "
        f"Тепер надішліть розклад у вигляді повідомлення",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ChooseScheduleType.sending_schedule)


@router.message(ChooseScheduleType.sending_schedule, F.text)
async def response(message: Message, state: FSMContext):
    user_data = await state.get_data()

    schedule_repository = ScheduleRepository()
    chat_repository = ChatRepository()

    async with chat_repository:
        chat_telegram_id = (
            await chat_repository.get_chat_telegram_id_by_name_and_user_telegram_id(
                user_data["chosen_chat_name"], message.from_user.id
            )
        )

    async with schedule_repository:
        await schedule_repository.upsert_schedule(
            chat_telegram_id,
            user_data["chosen_schedule_type"],
            message.text,
            message.entities,
        )

    await update_schedule_message_in_specific_chat_job(chat_telegram_id)
    await message.answer("Успішно додано/оновлено розклад")
    await state.clear()


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
            schedule.schedule, entities=schedule.message_entities
        )
        await chat_repository.add_update_schedule_message_to_edit_id(
            bot_message.message_id, message.chat.id
        )
