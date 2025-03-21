from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from models import UserModel, ChatModel
from repositories import UserRepository, ChatRepository

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привіт!")

    user_repository = UserRepository()
    async with user_repository:
        user_to_add = UserModel(
            user_telegram_id=message.from_user.id, user_name=message.from_user.full_name
        )
        await user_repository.add_user(user_to_add)


@router.message(Command("add_chat"))
async def cmd_add_chat(message: Message):
    chat_repository = ChatRepository()
    user_repository = UserRepository()

    async with user_repository:
        user_to_add = UserModel(message.from_user.id, message.from_user.full_name)
        await user_repository.add_user(user_to_add)

    async with chat_repository:
        chat_to_add = ChatModel(
            chat_telegram_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            chat_name=message.chat.full_name,
        )
        result = await chat_repository.add_chat(chat_to_add, message.from_user.id)

    if result:
        await message.answer("Успішно додано чат\n")
    else:
        await message.answer("Цей чат вже було додано раніше")
