
# tgschedulebot

Telegram bot for automatically updating a telegram message containing a schedule according to week pairity.

https://t.me/fcsc_schedulebot

![Logo](https://raw.githubusercontent.com/Pichus/tgschedulebot/refs/heads/main/bot.png)


## Tech Stack

- **Python 3.13.3**  
- **Aiogram**  
- **PostgreSQL**  
- **Docker**  

## Features

- Supports multiple chats, schedules, and schedule types
- Automatically updates the schedule message every week
- Ensures stable schedule updates by storing CRON jobs in a PostgreSQL database

## Run Locally

1. Create a Telegram bot

    Use [BotFather](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) to create a bot and obtain a token.

2. Clone the project

    ```bash
      git clone https://github.com/Pichus/tgschedulebot.git
    ```

3. Go to the project directory

    ```bash
      cd tgschedulebot
    ```

4. To run this project, add the following environment variables to your .env file (use .env.example as a reference):
    ``` env
    TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 // your telegram bot token retrieved from botfather
    DATABASE_CONNECTION_STRING="host=localhost port=5432 dbname=mydb user=some_user password=somepassword"
    DATABASE_URL_="postgresql+psycopg://user:password@localhost:5432/database_name"
    CRON_DAY_OF_WEEK=0 // int 0-6
    CRON_HOUR = 0      // int 0-23
    CRON_MINUTE = 0    // int 0-59
    CRON_TIMEZONE = "Europe/Kyiv" // https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    ADMIN_USER_IDS = "12345678910, 932483203, 2347234983" // telegram user ids of admins separated with commas; use https://t.me/userinfobot to get your user id
    ```

5. Ensure Docker and Docker Compose are installed, then start the bot:

    ```bash
      docker compose up
    ```

Now the bot should be up and running

## Deployment

The bot is designed for deployment on Heroku, but it can be deployed on other platforms as well.


## Roadmap

- Improve code quality and maintainability

- Add a feature for automatically fetching schedules from a Google Spreadsheet


## License

[MIT](https://choosealicense.com/licenses/mit/)

