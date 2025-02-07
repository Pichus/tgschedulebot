from psycopg import AsyncConnection, AsyncCursor

import config


class RepositoryBase:
    def __init__(self):
        self._db_connection: AsyncConnection | None = None
        self._cursor: AsyncCursor | None = None

    async def __aenter__(self):
        self._db_connection = await AsyncConnection.connect(
            config.database_connection_string
        )
        self._cursor: AsyncCursor = self._db_connection.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._cursor:
            await self._cursor.close()
        if self._db_connection:
            await self._db_connection.close()
