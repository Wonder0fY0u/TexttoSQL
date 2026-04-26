import aiomysql
from app.config import settings
from app.domain.interfaces import DatabaseConnector

class MySQLConnector(DatabaseConnector):
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            minsize=1,
            maxsize=10,
            autocommit=True
        )

    async def disconnect(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def execute_query(self, sql: str) -> list:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql)
                rows = await cur.fetchall()
                return rows

    async def get_table_schema(self, table_name: str) -> dict:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"DESCRIBE {table_name}")
                columns = await cur.fetchall()
                if not columns:
                    return {}
                return {
                    "table_name": table_name,
                    "columns": [
                        {"name": col[0], "type": col[1], "nullable": col[2]}
                        for col in columns
                    ]
                }