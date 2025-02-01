import sqlite3


class UserRepository:
    def __init__(self):
        pass

    def __enter__(self):
        self.__db_connection = sqlite3.connect('schedulebot.db')
        self.__cursor = self.__db_connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__db_connection.close()

    def user_exists(self, user_telegram_id) -> bool:
        self.__cursor.execute("SELECT UserTelegramID FROM Users WHERE UserTelegramID = ?", (user_telegram_id,))
        user = self.__cursor.fetchone()

        return user

    def add_user(self, user_telegram_id, username):
        if self.user_exists(user_telegram_id):
            return

        self.__cursor.execute("INSERT INTO Users (UserTelegramID, UserName)"
                              "VALUES (?, ?)",
                              (user_telegram_id, username))
        self.__db_connection.commit()

    def get_user_chats(self, user_telegram_id) -> list[str] | None:
        self.__cursor.execute("SELECT UserID FROM Users WHERE UserTelegramID = ?", (user_telegram_id,))
        user_id = self.__cursor.fetchone()[0]
        if user_id:
            self.__cursor.execute("SELECT ChatName FROM Chats WHERE UserID = ?", (user_id,))
            user_chats = self.__cursor.fetchall()
            return user_chats
        else:
            print("user not found")
            return
