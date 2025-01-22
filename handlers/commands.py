import json
import logging
import datetime

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import utils
from db import UsersDatabaseService, ChatsDatabaseService

router = Router()

def get_schedule(date_arg: datetime.datetime) -> str:
    with open("./resources/schedules.json", "r", encoding="utf8") as file:
        data = json.load(file)


    if utils.is_high_week(date_arg.isocalendar().week):
        return data["schedules"]["high"]
    else:
        return data["schedules"]["low"]

logging.basicConfig(level=logging.INFO)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привіт!")

    users_service = UsersDatabaseService()
    with users_service as service:
        service.add_user(message.from_user.id, message.from_user.first_name)


@router.message(Command("get_chat_id"))
async def cmd_get_chat_id(message: Message):
    chat_id = message.chat.id
    await message.answer(f"ID чату - \"{chat_id}\"")


# @router.message(Command("add_chat"))
# async def cmd_add_chat(message: Message, command: CommandObject):
#     if command.args is None:
#         await message.answer("Помилка: ви не передали усіх потрібних аргументів. Приклад\n"
#                              "/add_chat <ID чату> <ID теми чату>")
#         return
#
#     try:
#         chat_id, message_thread_id, chat = command.args.split(" ", maxsplit=1)
#     except ValueError:
#         await message.answer(
#             "Помилка: неправильний формат команди. Приклад:\n"
#             "/add_chat <ID чату> <ID теми чату>"
#         )
#         return
#
#     chats_service = ChatsDatabaseService()
#     chat_info = await message.bot.get_chat(chat_id=chat_id)
#     with chats_service as service:
#         service.add_chat(chat_id, message_thread_id, chat_info.full_name, message.from_user.id)
#
#     await message.answer("Успішно додано чат")
#     await message.answer(message.chat.username)

@router.message(Command("add_chat"))
async def cmd_add_chat(message: Message):
    chats_service = ChatsDatabaseService()
    users_service = UsersDatabaseService()

    with users_service as service:
        service.add_user(message.from_user.id, message.from_user.first_name)

    with chats_service as service:
        result = service.add_chat(message.chat.id,
                                  message.message_thread_id,
                                  message.chat.full_name,
                                  message.from_user.id)


    if result:
        await message.answer("Успішно додано чат\n"
                         "Інформація про доданий чат:\n"
                         f"chat_id={message.chat.id}"
                         f"thread_id={message.message_thread_id}"
                         f"chat_name={message.chat.full_name}"
                         f"user_id={message.from_user.id}"
                         f"user={message.from_user.first_name}")
    else:
        await message.answer("Цей чат вже було додано раніше")


# @dp.message(Command("send_schedule"))
# async def cmd_send_schedule(message: Message, command: CommandObject):
#     if command.args is None:
#         await message.answer("Помилка: ви не передали усіх потрібних аргументів. Приклад\n"
#                              "/send_schedule <ID чату> <ID теми чату>")
#         return
#
#     try:
#         chat_id, message_thread_id = command.args.split(" ", maxsplit=1)
#     except ValueError:
#         await message.answer(
#             "Помилка: неправильний формат команди. Приклад:\n"
#             "/send_schedule <ID чату> <ID теми чату>"
#         )
#         return
#
#     await bot.send_message(chat_id=chat_id,
#                            message_thread_id=int(message_thread_id),
#                            text=get_schedule(datetime.datetime.now()))