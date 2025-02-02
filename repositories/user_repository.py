from repositories.repository_base import RepositoryBase


# noinspection PyTypeChecker
class UserRepository(RepositoryBase):
    async def user_exists(self, user_telegram_id) -> bool:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE UserTelegramID = %s)", (user_telegram_id,))
            user_exists = await cursor.fetchone()

        return user_exists[0]

    async def add_user(self, user_telegram_id, username):
        if await self.user_exists(user_telegram_id):
            return

        async with self._db_connection.cursor() as cursor:
            await cursor.execute("INSERT INTO Users (UserTelegramID, UserName)"
                              "VALUES (%s, %s)",
                              (user_telegram_id, username))
        await self._db_connection.commit()

    async def get_user_chats(self, user_telegram_id) -> list[str] | None:
        async with self._db_connection.cursor() as cursor:
            await cursor.execute("SELECT UserID FROM Users WHERE UserTelegramID = ?", (user_telegram_id,))
            user_id = (await cursor.fetchone())[0]
            if user_id:
                await cursor.execute("SELECT ChatName FROM Chats WHERE UserID = ?", (user_id,))
                user_chats = await cursor.fetchall()
                return user_chats
            else:
                print("user not found")
                return
