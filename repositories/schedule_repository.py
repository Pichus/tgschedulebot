from repositories.repository_base import RepositoryBase
from psycopg import sql


class ScheduleRepository(RepositoryBase):
    async def get_schedule(self, chat_id: int, schedule_type: str) -> str:
        query = sql.SQL("SELECT schedule FROM schedules WHERE chat_id = %s AND schedule_type = %s")
        await self._cursor.execute(query, (chat_id, schedule_type))
        schedule = await self._cursor.fetchone()

        return schedule[0]

    async def upsert_schedule(self, chat_id: int, schedule_type: str, schedule: str):
        query = sql.SQL("""
            INSERT INTO schedules (chat_id, schedule_type, schedule)
            VALUES (%s, %s, %s)
            ON CONFLICT (chat_id, schedule_type)
            DO UPDATE SET schedule = EXCLUDED.schedule
        """)
        await self._cursor.execute(query, (chat_id, schedule_type, schedule))
        await self._db_connection.commit()

    async def get_schedule_types(self) -> list[str]:
        query = sql.SQL("SELECT schedule_type FROM schedule_types")
        await self._cursor.execute(query)
        results = await self._cursor.fetchall()

        schedule_types = []
        for result in results:
            schedule_types.append(result[0])

        return schedule_types
