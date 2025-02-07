import asyncio
import logging
import os

import psycopg
from aiogram import Dispatcher
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from bot_instance import BotSingleton
from handlers import commands, schedule
from scheduler import edit_schedule_messages_in_all_chats_job


async def main():
    logging.basicConfig(level=logging.INFO)

    async with await psycopg.AsyncConnection.connect(
        config.database_connection_string
    ) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute(open("sql/init.sql", "r", encoding="utf-8").read())

    bot = BotSingleton(token=os.getenv("TELEGRAM_TOKEN"))
    dp = Dispatcher()

    jobstores = {"default": SQLAlchemyJobStore(url=config.database_url)}

    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv", jobstores=jobstores)

    dp.include_routers(schedule.router, commands.router)

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.start()
    if not scheduler.get_job("edit_schedule_messages_in_all_chats_job"):
        scheduler.add_job(
            edit_schedule_messages_in_all_chats_job,
            trigger="cron",
            day_of_week="mon",
            hour=0,
            max_instances=1,
            misfire_grace_time=None,
            coalesce=True,
            id="edit_schedule_messages_in_all_chats_job",
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped")
