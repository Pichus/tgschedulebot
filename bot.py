import asyncio
import logging
import os

import psycopg
from aiogram import Dispatcher
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

import config
from bot_instance import BotSingleton
from handlers import (
    commands,
    send_schedule,
    admin,
    one_command,
    add_update_schedule,
    get_schedule,
)
from models import CronDate
from scheduler import edit_schedule_messages_in_all_chats_job
from utils import convert_cron_date_to_utc


async def main():
    logging.basicConfig(level=logging.INFO)

    async with await psycopg.AsyncConnection.connect(
        config.database_connection_string
    ) as aconn:
        async with aconn.cursor() as cur:
            await cur.execute(open("sql/init.sql", "r", encoding="utf-8").read())

    bot = BotSingleton(token=os.getenv("TELEGRAM_TOKEN"))
    await bot.set_my_commands(config.commands_list)

    dp = Dispatcher()

    jobstores = {"default": SQLAlchemyJobStore(url=config.database_url)}

    scheduler = AsyncIOScheduler(timezone=timezone("UTC"), jobstores=jobstores)

    dp.include_routers(
        send_schedule.router,
        commands.router,
        admin.admin_router,
        one_command.router,
        add_update_schedule.router,
        get_schedule.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)

    cron_date = CronDate(
        day_of_week=config.cron_day_of_week,
        hour=config.cron_hour,
        minute=config.cron_minute,
    )
    utc_cron_date = convert_cron_date_to_utc(
        from_timezone=config.cron_timezone, cron_date=cron_date
    )

    scheduler.start()
    if not scheduler.get_job("edit_schedule_messages_in_all_chats_job"):
        scheduler.add_job(
            edit_schedule_messages_in_all_chats_job,
            trigger="cron",
            day_of_week=utc_cron_date.day_of_week,
            hour=utc_cron_date.hour,
            minute=utc_cron_date.minute,
            max_instances=1,
            misfire_grace_time=None,
            coalesce=True,
            id="edit_schedule_messages_in_all_chats_job",
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped")
