from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def yer_or_no_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text="Так")
    keyboard.button(text="Ні")

    return keyboard.as_markup(
        resize_keyyboard=True,
        input_field_placeholder="Бажаєте додати у свій час автоматично згенерований розклад?",
    )
