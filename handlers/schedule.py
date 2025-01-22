import datetime

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
import utils

from db import ChatsDatabaseService, UsersDatabaseService

router = Router()


class ChooseScheduleType(StatesGroup):
    choosing_chat = State()
    choosing_schedule_type = State()
    sending_schedule = State()


available_schedule_types = ["Нижній", "Верхній"]


@router.message(StateFilter(None), Command("add_schedule"))
async def cmd_add_schedule(message: Message, state: FSMContext):
    keyboard_buttons = []

    users_service = UsersDatabaseService()
    with users_service as service:
        user_chats = service.get_user_chats(message.from_user.id)

    for chat in user_chats:
        chat_name = chat[0]
        keyboard_buttons.append([KeyboardButton(text=chat_name)])

    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True,
        input_field_placeholder="Виберіть чат")

    await message.answer("В якому чаті ви бажаєте оновити розклад?", reply_markup=keyboard)
    await state.set_state(ChooseScheduleType.choosing_chat)


@router.message(ChooseScheduleType.choosing_chat, F.text)
async def choose_schedule_type(message: Message, state: FSMContext):
    await message.answer(f"Ви обрали чат \"{message.text.lower()}\"")
    await state.update_data(chosen_chat=message.text.lower())

    keyboard_buttons = [
        [KeyboardButton(text="Нижній")],
        [KeyboardButton(text="Верхній")]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True,
        input_field_placeholder="Виберіть тип розкладу")

    await message.answer("Який розклад ви бажаєте додати?", reply_markup=keyboard)
    await state.set_state(ChooseScheduleType.choosing_schedule_type)

@router.message(ChooseScheduleType.choosing_schedule_type, F.text.in_(available_schedule_types))
async def enter_schedule(message: Message, state: FSMContext):
    await state.update_data(chosen_schedule_type=message.text.lower())
    await message.answer(f"Ви обрали {message.text.lower()} розклад. Тепер надішліть розклад у вигляді повідомлення", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChooseScheduleType.sending_schedule)


@router.message(ChooseScheduleType.sending_schedule, F.text)
async def response(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chats_service = ChatsDatabaseService()
    with chats_service as service:
        if user_data["chosen_schedule_type"] == "нижній":
            print(message.text)
            service.update_low_schedule(message.text, user_data["chosen_chat"])
        elif user_data["chosen_schedule_type"] == "верхній":
            print(message.text)
            service.update_high_schedule(message.text, user_data["chosen_chat"])

    await message.answer("Успішно додано розклад")
    await state.clear()


@router.message(Command("send_schedule"))
async def cmd_send_schedule(message: Message):
    chats_service = ChatsDatabaseService()

    with chats_service as service:
        if not service.chat_exists(message.chat.id):
            await message.answer("Цього чату немає в базі даних бота. Додайте його командою /add_chat")
            return

        schedules = service.get_schedules(message.chat.id)
        current_schedule: str

        if utils.is_high_week(datetime.datetime.now().isocalendar().week):
            current_schedule = schedules["high"]
        else:
            current_schedule = schedules["low"]

        bot_message = await message.answer(current_schedule)
        service.add_schedule_message_id(bot_message.message_id, message.chat.id)
