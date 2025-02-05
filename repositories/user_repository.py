from repositories.repository_base import RepositoryBase


# noinspection PyTypeChecker
class UserRepository(RepositoryBase):
    async def user_exists(self, user_telegram_id) -> bool:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE UserTelegramID = %s)", (user_telegram_id,))
            user_exists = await cursor.fetchone()

        return user_exists[0]

    async def add_user(self, user_telegram_id: int, user_name: str) -> bool:
        result = True
        if await self.user_exists(user_telegram_id):
            result = False
        else:
            async with self._db_connection.cursor() as cursor:
                await cursor.execute("INSERT INTO Users (UserTelegramID, UserName)"
                                  "VALUES (%s, %s)",
                                  (user_telegram_id, user_name))
            await self._db_connection.commit()
        return result

    async def get_user_chats(self, user_telegram_id) -> list[str] | None:
        result: list[str] | None = None

        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT UserID FROM Users WHERE UserTelegramID = ?", (user_telegram_id,))
            user_id = (await cursor.fetchone())[0]
            if user_id:
                await cursor.execute("SELECT ChatName FROM Chats WHERE UserID = ?", (user_id,))
                result = await cursor.fetchall()

        return result
