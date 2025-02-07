from datetime import datetime

from aiogram.types import Message, MessageEntity


def get_current_week_type() -> str:
    if datetime.now().isocalendar().week % 2 == 0:
        return "верхній"
    else:
        return "нижній"
