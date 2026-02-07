import asyncio
from pathlib import Path

import aiosqlite

from config import DB_NAME


async def init_database():
    """Инициализирует БД из SQL файла"""

    sql_file = Path(__file__).parent / "init_sql.sql"
    sql_script = sql_file.read_text(encoding="utf-8")

    try:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.executescript(sql_script)
            await db.commit()
            print(f"База данных {DB_NAME} создана")

    except Exception as e:
        print(f"Ошибка при создании БД: {e}")


if __name__ == "__main__":
    asyncio.run(init_database())
