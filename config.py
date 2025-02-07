import os
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.getenv("TELEGRAM_TOKEN")
database_connection_string = os.getenv("DATABASE_CONNECTION_STRING")
database_url = os.getenv("DATABASE_URL_")
