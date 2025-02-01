import psycopg
import config


class RepositoryBase:
    def __enter__(self):
        self._db_connection = psycopg.AsyncConnection.connect(config.database_connection_string)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db_connection.close()
