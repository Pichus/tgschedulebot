from models import ChatModel
from repositories.repository_base import RepositoryBase


class ChatRepository(RepositoryBase):
    async def chat_exists(self, chat_telegram_id) -> bool:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT EXISTS(SELECT 1 FROM Chats WHERE ChatTelegramID = %s)", (chat_telegram_id,))
            user = await cursor.fetchone()

        return user[0]

    # noinspection PyTypeChecker,PyArgumentList,SqlInsertValues
    async def add_chat(self, chat_telegram_id, message_thread_id, chat_name, user_telegram_id) -> bool:
        if await self.chat_exists(chat_telegram_id):
            return False

        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT UserID FROM Users WHERE UserTelegramID = %s", (user_telegram_id,))
            user_id = await cursor.fetchone()["UserID"]
            await cursor.execute(
                "INSERT INTO Chats (ChatTelegramID, MessageThreadID, ChatName, UserID)"
                "VALUES (%s, %s, %s, %s)",
                (chat_telegram_id, message_thread_id, chat_name, int(user_id)))
        await self._db_connection.commit()

        return True

    async def update_low_schedule(self, low_schedule: str, chat_name):
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("UPDATE Chats SET LowSchedule = ? WHERE ChatName = ?",
                                  (low_schedule, chat_name))
        await self._db_connection.commit()

    async def update_high_schedule(self, high_schedule, chat_name):
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("UPDATE Chats SET HighSchedule = ? WHERE ChatName = ?",
                                     (high_schedule, chat_name))
        await self._db_connection.commit()

    async def get_schedules(self, chat_telegram_id) -> dict[str, str]:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT HighSchedule, LowSchedule FROM Chats WHERE ChatTelegramID = ?",
                              (chat_telegram_id,))
            result = await cursor.fetchone()

        return {"high": result[0], "low": result[1]}

    # noinspection SqlResolve,PyTypeChecker
    async def add_schedule_message_id(self, schedule_message_id, chat_telegram_id):
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("UPDATE Chats "
                              "SET ScheduleMessageID = ?"
                              "WHERE ChatTelegramID = ?",
                              (schedule_message_id, chat_telegram_id))
        await self._db_connection.commit()

    # noinspection PyTypeChecker
    async def get_chats_for_edit(self) -> list[ChatModel]:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT * "
                              "FROM Chats "
                              "WHERE ScheduleMessageID IS NOT NULL")
            chats = await cursor.fetchall()
        result = []
        for chat in chats:
            result.append(ChatModel(*chat))

        return result
