from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str

class SQLValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    fixed_sql: Optional[str] = None

class SQLResponse(BaseModel):
    question: str
    sql: str
    validation: SQLValidationResult
    result: Optional[List[dict]] = None
    execution_time_ms: Optional[float] = None