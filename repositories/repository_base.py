from psycopg import AsyncConnection
import config


class RepositoryBase:
    async def __aenter__(self):
        self._db_connection: AsyncConnection = await AsyncConnection.connect(config.database_connection_string)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._db_connection:
            await self._db_connection.close()
