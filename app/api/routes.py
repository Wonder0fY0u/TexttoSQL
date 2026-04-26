from fastapi import APIRouter
from app.domain.entities import QuestionRequest, SQLResponse
from app.services.llm_service import LLMService
from app.services.schema_service import SchemaService

router = APIRouter()

db_conn = None
llm_gen = None
vector_store = None
embedder = None

@router.post("/ask", response_model=SQLResponse)
async def ask_question(request: QuestionRequest):
    schema_svc = SchemaService(db_conn)
    llm_svc = LLMService(llm_gen, vector_store, schema_svc, embedder)

    gen = await llm_svc.generate_sql(request.question)
    sql = gen["sql"]
    validation = gen["validation"]

    result = None
    if not validation.errors:
        final_sql = sql.rstrip(';')
        if 'limit' not in final_sql.lower():
            final_sql += " LIMIT 100"
            validation.warnings.append("Добавлен LIMIT 100 безопасности")
        try:
            result = await db_conn.execute_query(final_sql)
        except Exception as e:
            validation.errors.append(f"Ошибка выполнения: {str(e)}")
            validation.is_valid = False

    return SQLResponse(
        question=request.question,
        sql=sql,
        validation=validation,
        result=result,
        execution_time_ms=gen["execution_time_ms"]
    )