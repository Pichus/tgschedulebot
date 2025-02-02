from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def schedule_type_choice_keyboard(schedule_types: list[str]) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for schedule_type in schedule_types:
        keyboard.button(text=schedule_type)

    return keyboard.as_markup(resize_keyyboard=True, input_field_placeholder="Виберіть тип розкладу")
