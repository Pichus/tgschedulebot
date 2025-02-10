import os
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv("TELEGRAM_TOKEN")
database_connection_string = os.getenv("DATABASE_CONNECTION_STRING")
database_url = os.getenv("DATABASE_URL_")
cron_day_of_week = os.getenv("CRON_DAY_OF_WEEK")
cron_hour = os.getenv("CRON_HOUR")
cron_minute = os.getenv("CRON_MINUTE")
cron_timezone = os.getenv("CRON_TIMEZONE")
