from dataclasses import dataclass


@dataclass
class ChatModel:
    chat_telegram_id: int
    chat_name: str
    message_thread_id: int | None = None
    schedule_message_to_edit_id: int | None = None
