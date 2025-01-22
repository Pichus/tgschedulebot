import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
import sqlite3
import os
import utils
from db import ChatsDatabaseService, ChatModel
from handlers import commands, schedule
import time
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

connection = sqlite3.connect('schedulebot.db')
cursor = connection.cursor()

with open("./sql/init.sql", "r") as sql_file:
    sql_script = sql_file.read()

cursor.executescript(sql_script)
connection.commit()
connection.close()


async def main():
    load_dotenv()

    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()

    async def job():
        chats_service = ChatsDatabaseService()
        with chats_service as service:
            chats = service.get_chats_for_edit()

        if not chats:
            return

        is_high_week = utils.is_high_week(datetime.now().isocalendar().week)

        for chat in chats:
            text: str
            if is_high_week:
                text = chat.high_schedule
            else:
                text = chat.low_schedule

            text += f"\n\n останнє оновлення {datetime.now()}"

            await bot.edit_message_text(text=text,
                                        message_id=chat.schedule_message_id,
                                        chat_id=chat.chat_telegram_id,)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(job, "interval", minutes=1)

    dp.include_routers(schedule.router, commands.router)

    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())