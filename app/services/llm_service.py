import time
from app.domain.interfaces import TextGenerator, VectorStore
from app.services.validation_service import ValidationService
from app.services.schema_service import SchemaService
from app.repositories.embedding_provider import EmbeddingProvider

# примеры чтобы промт был более сильным
FEW_SHOT_EXAMPLES = """
Примеры запросов к таблице generated_data:

Вопрос: Сколько всего записей в таблице?
SQL: SELECT COUNT(*) FROM generated_data;

Вопрос: Покажи всех сотрудников из Москвы старше 50 лет.
SQL: SELECT * FROM generated_data WHERE city = 'Москва' AND age > 50;

Вопрос: Какие должности имеют самую высокую среднюю зарплату?
SQL: SELECT position, AVG(salary) as avg_salary FROM generated_data GROUP BY position ORDER BY avg_salary DESC LIMIT 5;

Вопрос: Найди товары дороже 100000 рублей.
SQL: SELECT * FROM generated_data WHERE price > 100000;

Вопрос: Выведи имена и фамилии сотрудников, работающих в компании АО «Вектор».
SQL: SELECT firstName, lastName FROM generated_data WHERE company = 'АО «Вектор»';

Примеры запросов к базе данных (таблицы: employees, products, purchases).

Вопрос: Сколько сотрудников в каждой компании?
SQL: SELECT company, COUNT(*) FROM employees GROUP BY company;

Вопрос: Покажи имена сотрудников и названия купленных ими товаров.
SQL: SELECT e.firstName, e.lastName, p.productName FROM employees e JOIN purchases pu ON e.employee_id = pu.employee_id JOIN products p ON pu.product_id = p.product_id;

Вопрос: Выведи товары дороже 100000, купленные сотрудниками из Москвы.
SQL: SELECT DISTINCT p.productName, p.price FROM products p JOIN purchases pu ON p.product_id = pu.product_id JOIN employees e ON pu.employee_id = e.employee_id WHERE p.price > 100000 AND e.city = 'Москва';
"""

class LLMService:
    def __init__(self, llm: TextGenerator, vector_store: VectorStore,
                 schema_service: SchemaService, embedding_provider: EmbeddingProvider):
        self.llm = llm
        self.vector_store = vector_store
        self.schema_service = schema_service
        self.embedding_provider = embedding_provider

    async def generate_sql(self, question: str) -> dict:
        # векторизация вопроса
        query_emb = self.embedding_provider.encode([question])[0]

        # гибридный поиск по схеме
        similar_docs = await self.vector_store.hybrid_search(query_emb, question, top_k=3)
        schema_context = "\n".join([doc["text"] for doc in similar_docs])
        full_schema = await self.schema_service.get_schema_text()

        # сборка промпта
        prompt = f"""
Ты — очень опытный SQL-ассистент для базы данных MySQL но ты можешь только читать ,добавлять ,придумывать и удалять ничего нельзя!
Схема базы данных:
{schema_context}

Вот несколько примеров правильных запросов:
{FEW_SHOT_EXAMPLES}

Напиши ТОЛЬКО SQL-запрос (без комментариев и пояснений), который ответит на следующий вопрос.
Вопрос: {question}
SQL:"""

        start = time.time()
        sql = await self.llm.generate(prompt)
        exec_time = (time.time() - start) * 1000

        schema_text = await self.schema_service.get_schema_text()
        validation = ValidationService(schema_text).validate(sql)

        return {
            "sql": sql.strip(),
            "validation": validation,
            "execution_time_ms": exec_time
        }