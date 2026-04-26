import asyncio
from app.repositories.database import MySQLConnector
from app.repositories.embedding_provider import EmbeddingProvider
from app.repositories.vector_store import get_vector_store

async def index_schema():
    db = MySQLConnector()
    await db.connect()
    vs = get_vector_store()
    emb = EmbeddingProvider()

    table_names = ["employees", "products", "purchases"]
    texts = []
    metadata = []

    for table_name in table_names:
        table_schema = await db.get_table_schema(table_name)
        #описание всей таблицы
        col_desc = ", ".join([f"{c['name']} ({c['type']})" for c in table_schema["columns"]])
        texts.append(f"Таблица {table_name} содержит: {col_desc}")
        metadata.append({"type": "table", "name": table_name})\

        for c in table_schema["columns"]:
            texts.append(f"Колонка {c['name']} типа {c['type']} в таблице {table_name}.")
            metadata.append({"type": "column", "column_name": c["name"], "table": table_name})

    embeddings = emb.encode(texts)
    await vs.add_embeddings(texts, metadata, embeddings)
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(index_schema())