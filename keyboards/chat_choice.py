from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def chat_choice_keyboard(chat_names: list[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for chat_name in chat_names:
        keyboard.button(text=chat_name)

    return keyboard.as_markup(
        resize_keyyboard=True, input_field_placeholder="Виберіть чат"
    )
