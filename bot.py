import asyncio
import logging
import os

import psycopg
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import config
from handlers import commands, schedule


async def main():
    logging.basicConfig(level=logging.INFO)

    async with await psycopg.AsyncConnection.connect(
        config.database_connection_string
    ) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute(open("sql/init.sql", "r", encoding="utf-8").read())

    load_dotenv()

    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()

    # async def job():
    #     with ChatRepository() as service:
    #         chats = service.get_chats_for_edit()
    #
    #     if not chats:
    #         return
    #
    #     is_high_week = utils.is_high_week(datetime.now().isocalendar().week)
    #
    #     for chat in chats:
    #         text: str
    #         if is_high_week:
    #             text = chat.high_schedule
    #         else:
    #             text = chat.low_schedule
    #
    #         text += f"\n\n останнє оновлення {datetime.now()}"
    #
    #         await bot.edit_message_text(text=text,
    #                                     message_id=chat.schedule_message_id,
    #                                     chat_id=chat.chat_telegram_id,)
    #
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(job, "interval", minutes=1)

    dp.include_routers(schedule.router, commands.router)

    await bot.delete_webhook(drop_pending_updates=True)
    # scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
