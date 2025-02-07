from aiogram import Bot


class BotSingleton:
    _instance = None

    def __new__(cls, token=None):
        if cls._instance is None:
            cls._instance = Bot(token)
        return cls._instance
