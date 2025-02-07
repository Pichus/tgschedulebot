from psycopg import sql

from models import UserModel, ChatModel
from repositories.repository_base import RepositoryBase


class UserRepository(RepositoryBase):
    async def user_exists(self, user_telegram_id) -> bool:
        query = sql.SQL(
            "SELECT EXISTS(SELECT 1 FROM users WHERE user_telegram_id = %s)"
        )
        await self._cursor.execute(query, (user_telegram_id,))
        user_exists = await self._cursor.fetchone()

        return user_exists[0]

    async def add_user(self, user: UserModel) -> bool:
        result = True

        query = sql.SQL(
            "INSERT INTO users (user_telegram_id, user_name) VALUES (%s, %s)"
        )

        if await self.user_exists(user.user_telegram_id):
            result = False
        else:
            await self._cursor.execute(query, (user.user_telegram_id, user.user_name))
            await self._db_connection.commit()

        return result

    async def get_user_db_id_by_telegram_id(self, user_telegram_id: int) -> int:
        query = sql.SQL("SELECT user_id FROM users WHERE user_telegram_id = %s")
        await self._cursor.execute(query, (user_telegram_id,))
        result = await self._cursor.fetchone()
        user_id = result[0]
        return user_id

    async def get_user_chats(self, user_telegram_id: int) -> list[ChatModel] | None:
        chats: list[ChatModel] = []

        user_id = await self.get_user_db_id_by_telegram_id(user_telegram_id)
        if user_id:
            query = sql.SQL(
                """
                SELECT chat_telegram_id, chat_name, message_thread_id, schedule_message_to_edit_id
                FROM chats WHERE user_id = %s
            """
            )
            await self._cursor.execute(query, (user_id,))
            results = await self._cursor.fetchall()
            for chat in results:
                chat_model = ChatModel(
                    chat_telegram_id=chat[0],
                    chat_name=chat[1],
                    message_thread_id=chat[2],
                    schedule_message_to_edit_id=chat[3],
                )
                chats.append(chat_model)

        return chats
