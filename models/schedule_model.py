from dataclasses import dataclass


@dataclass
class ScheduleModel:
    schedule_id: int
    chat_id: int
    schedule_type: str
    schedule: str
