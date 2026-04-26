from app.repositories.database import MySQLConnector

class SchemaService:
    def __init__(self, db: MySQLConnector):
        self.db = db

    async def get_schema_text(self) -> str:
        tables = ["employees", "products", "purchases"]   # можно просканировать список таблиц
        lines = []
        for tbl in tables:
            s = await self.db.get_table_schema(tbl)
            if not s:
                continue
            cols = [f"{c['name']} ({c['type']})" for c in s["columns"]]
            lines.append(f"Таблица {tbl}: {', '.join(cols)}.")
        return "\n".join(lines)