import asyncio, csv, aiomysql
from app.config import settings

async def main():
    conn = await aiomysql.connect(
        host=settings.db_host, port=settings.db_port,
        user=settings.db_user, password=settings.db_password,
        db=settings.db_name
    )
    async with conn.cursor() as cur:
        await cur.execute("""
            CREATE TABLE IF NOT EXISTS generated_data (
                id INTEGER, firstName VARCHAR(100), lastName VARCHAR(100), patronym VARCHAR(100),
                gender VARCHAR(20), age INTEGER, birthdate VARCHAR(20), email VARCHAR(100),
                phone VARCHAR(30), country VARCHAR(50), city VARCHAR(50), address VARCHAR(200),
                zip VARCHAR(20), position VARCHAR(100), company VARCHAR(100), salary INTEGER,
                productName VARCHAR(200), price INTEGER, category VARCHAR(100),
                description TEXT, ip VARCHAR(30), registered VARCHAR(20), login VARCHAR(100)
            )
        """)
    with open("generated_data.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [tuple(row.values()) for row in reader]
    async with conn.cursor() as cur:
        await cur.executemany(
            "INSERT INTO generated_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            rows
        )
    await conn.commit()
    conn.close()

if __name__ == "__main__":
    asyncio.run(main())