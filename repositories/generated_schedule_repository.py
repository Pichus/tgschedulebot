from aiogram.types import MessageEntity
from psycopg import sql

import utils
from exceptions import ScheduleNotFoundError
from models import ScheduleModel
from repositories.repository_base import RepositoryBase


class GeneratedScheduleRepository(RepositoryBase):
    async def get_schedule(self, group_index, schedule_type: str) -> ScheduleModel:
        query = sql.SQL(
            """
            SELECT schedule FROM generated_schedules 
            WHERE group_index = %s  
            AND schedule_type = %s;
        """
        )
        await self._cursor.execute(query, (group_index, schedule_type))
        schedule = await self._cursor.fetchone()

        if not schedule:
            raise ScheduleNotFoundError

        return ScheduleModel(
            schedule_type,
            schedule[0],
            utils.json_string_to_message_entities(schedule[1]),
        )

    async def get_schedules(self, group_index) -> (ScheduleModel, ScheduleModel):
        query = sql.SQL(
            """
            SELECT schedule_type, schedule FROM generated_schedules 
            WHERE group_index = %s;
        """
        )
        await self._cursor.execute(query, (group_index,))
        schedules = await self._cursor.fetchall()

        if not schedules:
            raise ScheduleNotFoundError

        result = []

        for schedule in schedules:
            result.append(ScheduleModel(schedule[0], schedule[1]))

        return tuple(result)

    async def upsert_schedule(
        self, group_index: str, schedule_type: str, schedule: str
    ) -> None:
        query = sql.SQL(
            """
            INSERT INTO generated_schedules (group_index, schedule_type, schedule)
            VALUES (
                %s,
                %s,
                %s
            )
            ON CONFLICT (group_index, schedule_type)
            DO UPDATE SET
                schedule = EXCLUDED.schedule;
        """
        )
        await self._cursor.execute(query, (group_index, schedule_type, schedule))
        await self._db_connection.commit()
