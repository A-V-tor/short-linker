import logging
from abc import ABC, abstractmethod
from typing import Any

import aiosqlite

LOGGER = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Абстрактный базовый класс для репозиториев"""

    @abstractmethod
    async def execute_read_query(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def execute_write_query(self, query: str, params: tuple = ()) -> bool:
        pass


class AsyncSqliteRepository(BaseRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def execute_read_query(self, query: str, params: tuple | dict = ()):
        conn = await self.get_connection()
        async with conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def execute_write_query(self, query: str, params: tuple = ()) -> bool:
        conn = await self.get_connection()
        try:
            await conn.execute(query, params)
            await conn.commit()
            return False
        except Exception as e:
            await conn.rollback()
            LOGGER.exception(f"Database error: {e}")
            return True
