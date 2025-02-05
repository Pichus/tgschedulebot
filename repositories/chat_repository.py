from models import ChatModel
from repositories.repository_base import RepositoryBase
from psycopg import sql


class ChatRepository(RepositoryBase):
    async def chat_exists(self, chat_telegram_id: int) -> bool:
        query = sql.SQL("SELECT EXISTS(SELECT 1 FROM chats WHERE chat_telegram_id = %s)")
        await self._cursor.execute(query, (chat_telegram_id,))
        user = await self._cursor.fetchone()

        return user[0]

    async def add_chat(self, chat_model: ChatModel, user_telegram_id: int) -> bool:
        if await self.chat_exists(chat_model.chat_telegram_id):
            return False

        query1 = sql.SQL("SELECT user_id FROM users WHERE user_telegram_id = %s")
        await self._cursor.execute(query1, (user_telegram_id,))
        user_id = await self._cursor.fetchone()["user_id"]

        query2 = sql.SQL(
            "INSERT INTO chats (chat_telegram_id, message_thread_id, chat_name, user_id) VALUES (%s, %s, %s, %s)")
        await self._cursor.execute(query2,(chat_model.chat_telegram_id, chat_model.message_thread_id,
                                           chat_model.chat_name, int(user_id)))

        await self._db_connection.commit()

        return True

    async def add_schedule_message_id(self, schedule_message_id, chat_telegram_id):
        query = sql.SQL("UPDATE chats SET schedule_message_id = %s WHERE chat_telegram_id = %s")
        await self._cursor.execute(query,(schedule_message_id, chat_telegram_id))
        await self._db_connection.commit()

    async def get_chats_for_edit(self) -> list[ChatModel]:
        query = sql.SQL("SELECT * FROM chats WHERE schedule_message_id IS NOT NULL")
        await self._cursor.execute(query)
        chats = await self._cursor.fetchall()
        result = []
        for chat in chats:
            result.append(ChatModel(*chat))

        return result
