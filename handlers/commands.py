from aiogram import Router
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import Message, ChatMemberUpdated

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


# deprecated
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


@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    user_telegram_id = event.from_user.id
    user_name = event.from_user.full_name
    chat_telegram_id = event.chat.id
    chat_name = event.chat.full_name

    chat_to_add = ChatModel(chat_telegram_id, chat_name)

    user_repository = UserRepository()
    async with user_repository:
        user_to_add = UserModel(user_telegram_id, user_name)
        await user_repository.add_user(user_to_add)

    chat_repository = ChatRepository()
    async with chat_repository:
        await chat_repository.add_chat(chat_to_add, user_telegram_id)
