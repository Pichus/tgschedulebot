from aiogram.types import MessageEntity
from psycopg import sql

import utils
from exceptions import ScheduleNotFoundError
from models import ScheduleModel
from repositories.repository_base import RepositoryBase


class ScheduleRepository(RepositoryBase):
    async def get_schedule(
        self, chat_telegram_id: int, schedule_type: str
    ) -> ScheduleModel:
        query = sql.SQL(
            """
            SELECT schedule, message_entities_json FROM schedules 
            WHERE chat_id = (SELECT chat_id FROM chats WHERE chat_telegram_id = %s)  
            AND schedule_type = %s;
        """
        )
        await self._cursor.execute(query, (chat_telegram_id, schedule_type))
        schedule = await self._cursor.fetchone()

        if not schedule:
            raise ScheduleNotFoundError

        return ScheduleModel(
            schedule_type,
            schedule[0],
            utils.json_string_to_message_entities(schedule[1]),
        )

    async def upsert_schedule(
        self,
        chat_telegram_id: int,
        schedule_type: str,
        schedule: str,
        message_entities: list[MessageEntity] = None,
    ) -> None:
        message_entities_json = utils.message_entities_to_json_string(message_entities)
        query = sql.SQL(
            """
            INSERT INTO schedules (chat_id, schedule_type, schedule, message_entities_json)
            VALUES (
                (SELECT chat_id FROM chats WHERE chat_telegram_id = %s), 
                %s,
                %s,
                %s
            )
            ON CONFLICT (chat_id, schedule_type)
            DO UPDATE SET
                schedule = EXCLUDED.schedule,
                message_entities_json = EXCLUDED.message_entities_json;
        """
        )
        await self._cursor.execute(
            query, (chat_telegram_id, schedule_type, schedule, message_entities_json)
        )
        await self._db_connection.commit()

    async def get_schedule_types(self) -> list[str]:
        query = sql.SQL("SELECT schedule_type FROM schedule_types")
        await self._cursor.execute(query)
        results = await self._cursor.fetchall()

        schedule_types = []
        for result in results:
            schedule_types.append(result[0])

        return schedule_types
