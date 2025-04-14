import json
import os

from aiogram.types import BotCommand
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv("TELEGRAM_TOKEN")
database_connection_string = os.getenv("DATABASE_CONNECTION_STRING")
database_url = os.getenv("DATABASE_URL_")
cron_day_of_week = int(os.getenv("CRON_DAY_OF_WEEK"))
cron_hour = int(os.getenv("CRON_HOUR"))
cron_minute = int(os.getenv("CRON_MINUTE"))
cron_timezone = os.getenv("CRON_TIMEZONE")
admin_user_ids = list(map(int, os.getenv("ADMIN_USER_IDS").split(", ")))
google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

commands_list = [
    BotCommand(command="start", description="додати себе в базу даних бота"),
    # BotCommand(command="add_chat", description="додати чат, в якому ви зараз перебуваєте, в базу даних бота"),
    BotCommand(
        command="one_command",
        description="додати автоматичний розклад у ваш чат однією командою",
    ),
    BotCommand(
        command="add_update_schedule",
        description="додати / оновити розклад одного з ваших чатів",
    ),
    BotCommand(
        command="send_schedule",
        description="надіслати розклад у чат, в якому ви зараз перебуваєте, а також увімкнути автоматичне оновлення чату, залежно від тижня",
    ),
    BotCommand(
        command="get_schedule",
        description="отримати розклад групи",
    ),
]
