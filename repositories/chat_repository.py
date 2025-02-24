from psycopg import sql

from models import ChatModel
from repositories.repository_base import RepositoryBase


class ChatRepository(RepositoryBase):
    async def get_chat(self, chat_telegram_id: int) -> ChatModel:
        query = sql.SQL(
            """
            SELECT chat_telegram_id, chat_name, message_thread_id, schedule_message_to_edit_id FROM chats 
            WHERE chat_telegram_id = %s;
        """
        )

        await self._cursor.execute(query, (chat_telegram_id,))
        chat = await self._cursor.fetchone()

        return ChatModel(
            chat_telegram_id=chat[0],
            chat_name=chat[1],
            message_thread_id=chat[2],
            schedule_message_to_edit_id=chat[3],
        )

    async def chat_exists(self, chat_telegram_id: int) -> bool:
        query = sql.SQL(
            "SELECT EXISTS(SELECT 1 FROM chats WHERE chat_telegram_id = %s)"
        )
        await self._cursor.execute(query, (chat_telegram_id,))
        chat = await self._cursor.fetchone()

        return chat[0]

    async def add_chat(self, chat_model: ChatModel, user_telegram_id: int) -> bool:
        result = True
        if await self.chat_exists(chat_model.chat_telegram_id):
            result = False
        else:
            query1 = sql.SQL("SELECT user_id FROM users WHERE user_telegram_id = %s")
            await self._cursor.execute(query1, (user_telegram_id,))
            user_id = (await self._cursor.fetchone())[0]

            query2 = sql.SQL(
                "INSERT INTO chats (chat_telegram_id, message_thread_id, chat_name, user_id) VALUES (%s, %s, %s, %s)"
            )
            await self._cursor.execute(
                query2,
                (
                    chat_model.chat_telegram_id,
                    chat_model.message_thread_id,
                    chat_model.chat_name,
                    int(user_id),
                ),
            )

            await self._db_connection.commit()

        return result

    async def add_update_schedule_message_to_edit_id(
        self, schedule_message_id: int, chat_telegram_id: int
    ):
        query = sql.SQL(
            "UPDATE chats SET schedule_message_to_edit_id = %s WHERE chat_telegram_id = %s"
        )
        await self._cursor.execute(query, (schedule_message_id, chat_telegram_id))
        await self._db_connection.commit()

    async def get_chats_for_edit(self, offset: int, limit: int = 10) -> list[ChatModel]:
        query = sql.SQL(
            """
                SELECT chat_telegram_id, chat_name, message_thread_id, schedule_message_to_edit_id
                FROM chats
                WHERE schedule_message_to_edit_id IS NOT NULL
                LIMIT %s OFFSET %s
            """
        )
        await self._cursor.execute(query, (limit, offset))
        results = await self._cursor.fetchall()

        chats = [ChatModel(*result) for result in results]

        return chats

    async def get_chat_telegram_id_by_name_and_user_telegram_id(
        self, chat_name: str, user_telegram_id: int
    ) -> int:
        query = sql.SQL(
            """
            SELECT chat_telegram_id 
            FROM chats 
            JOIN users on users.user_id = chats.user_id
            WHERE chats.chat_name = %s AND users.user_telegram_id = %s"""
        )
        await self._cursor.execute(query, (chat_name, user_telegram_id))
        result = await self._cursor.fetchone()
        result_chat_telegram_id = result[0]

        return result_chat_telegram_id
