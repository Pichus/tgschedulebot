from dataclasses import dataclass

from aiogram.types import MessageEntity


@dataclass
class ScheduleModel:
    schedule_type: str
    schedule: str
    message_entities: list[MessageEntity]
