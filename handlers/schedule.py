import datetime
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import utils
from keyboards.chat_choice import chat_choice_keyboard

from keyboards.schedule_choice import schedule_type_choice_keyboard
from repositories import UserRepository, ChatRepository

router = Router()


class ChooseScheduleType(StatesGroup):
    choosing_chat = State()
    choosing_schedule_type = State()
    sending_schedule = State()


@router.message(StateFilter(None), Command("add_schedule"))
async def cmd_add_schedule(message: Message, state: FSMContext):
    with UserRepository as user_repository:
        user_chats = user_repository.get_user_chats(message.from_user.id)

    chat_names = []
    for chat in user_chats:
        chat_names.append(chat["chat_name"])

    await message.answer("В якому чаті ви бажаєте оновити розклад?",
                         reply_markup=chat_choice_keyboard(chat_names))
    await state.set_state(ChooseScheduleType.choosing_chat)


@router.message(ChooseScheduleType.choosing_chat, F.text)
async def choose_schedule_type(message: Message, state: FSMContext):
    await message.answer(f"Ви обрали чат \"{message.text.lower()}\"")
    await state.update_data(chosen_chat=message.text.lower())

    await message.answer("Який розклад ви бажаєте додати?",
                         reply_markup=schedule_type_choice_keyboard(['Нижній', 'Верхній']))
    await state.set_state(ChooseScheduleType.choosing_schedule_type)

@router.message(ChooseScheduleType.choosing_schedule_type, F.text.in_(['нижній', 'верхній']))
async def enter_schedule(message: Message, state: FSMContext):
    await state.update_data(chosen_schedule_type=message.text.lower())
    await message.answer(f"Ви обрали {message.text.lower()} розклад. "
                         f"Тепер надішліть розклад у вигляді повідомлення",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChooseScheduleType.sending_schedule)


@router.message(ChooseScheduleType.sending_schedule, F.text)
async def response(message: Message, state: FSMContext):
    user_data = await state.get_data()
    with ChatRepository() as chat_repository:
        if user_data["chosen_schedule_type"] == "нижній":
            print(message.text)
            chat_repository.update_low_schedule(message.text, user_data["chosen_chat"])
        elif user_data["chosen_schedule_type"] == "верхній":
            print(message.text)
            chat_repository.update_high_schedule(message.text, user_data["chosen_chat"])

    await message.answer("Успішно додано розклад")
    await state.clear()


@router.message(Command("send_schedule"))
async def cmd_send_schedule(message: Message):
    with ChatRepository() as chat_repository:
        if not chat_repository.chat_exists(message.chat.id):
            await message.answer("Цього чату немає в базі даних бота. Додайте його командою /add_chat")
            return

        schedules = chat_repository.get_schedules(message.chat.id)
        current_schedule: str

        if utils.is_high_week(datetime.datetime.now().isocalendar().week):
            current_schedule = schedules["high"]
        else:
            current_schedule = schedules["low"]

        bot_message = await message.answer(current_schedule)
        chat_repository.add_schedule_message_id(bot_message.message_id, message.chat.id)
