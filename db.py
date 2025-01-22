import sqlite3
from dataclasses import dataclass


@dataclass
class ChatModel:
    chat_id: int
    chat_telegram_id: str
    message_thread_id: str
    chat_name: str
    high_schedule: str
    low_schedule: str
    schedule_message_id: int
    user_id: int

class ChatsDatabaseService:
    def __init__(self):
        pass

    def __enter__(self):
        self.__db_connection = sqlite3.connect('schedulebot.db')
        self.__cursor = self.__db_connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__db_connection.close()

    def chat_exists(self, chat_telegram_id) -> bool:
        self.__cursor.execute("SELECT ChatTelegramID FROM Chats WHERE ChatTelegramID = ?", (chat_telegram_id,))
        user = self.__cursor.fetchone()

        return user

    def add_chat(self, chat_telegram_id, message_thread_id, chat_name, user_telegram_id) -> bool:
        if self.chat_exists(chat_telegram_id):
            return False

        self.__cursor.execute("SELECT UserID FROM Users WHERE UserTelegramID = ?", (user_telegram_id,))
        user_id = self.__cursor.fetchone()[0]
        self.__cursor.execute("INSERT INTO Chats (ChatTelegramID, MessageThreadID, ChatName, UserID)"
                                  "VALUES (?, ?, ?, ?)",
                                  (chat_telegram_id, message_thread_id, chat_name, int(user_id)))
        self.__db_connection.commit()
        return True

    def update_low_schedule(self, low_schedule: str, chat_name):
        self.__cursor.execute("UPDATE Chats SET LowSchedule = ? WHERE ChatName = ?",
                                  (low_schedule, chat_name))
        self.__db_connection.commit()

    def update_high_schedule(self, high_schedule, chat_name):
        self.__cursor.execute("UPDATE Chats SET HighSchedule = ? WHERE ChatName = ?",
                                     (high_schedule, chat_name))
        self.__db_connection.commit()

    def get_schedules(self, chat_telegram_id) -> dict[str, str]:
        self.__cursor.execute("SELECT HighSchedule, LowSchedule FROM Chats WHERE ChatTelegramID = ?",
                              (chat_telegram_id,))
        result = self.__cursor.fetchone()
        return {"high": result[0], "low": result[1]}

    def add_schedule_message_id(self, schedule_message_id, chat_telegram_id):
        self.__cursor.execute("UPDATE Chats "
                              "SET ScheduleMessageID = ?"
                              "WHERE ChatTelegramID = ?",
                              (schedule_message_id, chat_telegram_id))
        self.__db_connection.commit()

    def get_chats_for_edit(self) -> list[ChatModel]:
        self.__cursor.execute("SELECT * "
                              "FROM Chats "
                              "WHERE ScheduleMessageID IS NOT NULL")
        chats = self.__cursor.fetchall()
        result = []
        for chat in chats:
            result.append(ChatModel(*chat))

        return result


class UsersDatabaseService:
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