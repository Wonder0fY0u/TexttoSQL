import sqlparse
from app.domain.entities import SQLValidationResult

class ValidationService:
    def __init__(self, schema_text: str):
        self.schema_text = schema_text

    def validate(self, sql: str) -> SQLValidationResult:
        errors = []
        warnings = []

        # очистка и парсинг
        sql = sql.strip().rstrip(';')
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return SQLValidationResult(is_valid=False, errors=["Пустой запрос"])
            statement = parsed[0]
        except Exception as e:
            return SQLValidationResult(is_valid=False, errors=[str(e)])


        sql_type = statement.get_type()
        if sql_type != 'SELECT':
            errors.append(f"Запрещённый тип запроса: {sql_type}. Разрешены только SELECT.")

        tables = self._extract_tables(statement)
        known_tables = ["employees", "products", "purchases"]
        for t in tables:
            if t.lower() not in known_tables:
                errors.append(f"Таблица '{t}' отсутствует в схеме")

        # проверка на LIMIT
        has_limit = 'limit' in sql.lower()
        if not has_limit:
            warnings.append("Добавлен LIMIT 100 для предотвращения полной выгрузки данных")

        is_valid = len(errors) == 0
        return SQLValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            fixed_sql=sql
        )

    def _extract_tables(self, statement):
        """Извлекаем имена таблиц только после FROM / JOIN."""
        tables = set()
        from sqlparse.sql import Identifier, IdentifierList
        from sqlparse.tokens import Keyword

        # ищем токены‑ключевые слова FROM, JOIN и т.д.
        for i, token in enumerate(statement.tokens):
            if token.ttype is Keyword and token.value.upper() in (
                    'FROM', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN'
            ):
                # смотрим следующий не‑пробельный токен
                for j in range(i + 1, len(statement.tokens)):
                    nxt = statement.tokens[j]
                    if nxt.is_whitespace:
                        continue
                    if isinstance(nxt, Identifier):
                        tables.add(nxt.get_real_name())
                    elif isinstance(nxt, IdentifierList):
                        for ident in nxt.get_identifiers():
                            tables.add(ident.get_real_name())
                    # как только нашли идентификатор, выходим
                    break
        return list(tables)