# Text-to-SQL AI Assistant

Проект преобразует вопросы на естественном языке в SQL-запросы и выполняет их в базе данных MySQL.  
Используется локальная модель DeepSeek Coder 6.7B, работающая через Ollama — без подключения к интернету и сторонних API.  
Архитектура разделена на независимые слои (domain, repositories, services, api), что упрощает замену отдельных компонентов.

## Функциональность

- Права пользователя MySQL ограничены операцией SELECT — база данных отклоняет любые попытки изменения или удаления данных.
- Приложение разрешает только SELECT-запросы на уровне кода; тип запроса проверяется с помощью sqlparse.
- Автоматическое добавление `LIMIT 100`, если оператор LIMIT отсутствует — предотвращает полную выгрузку таблиц.
- В состав схемы входят три нормализованные таблицы (`employees`, `products`, `purchases`) с внешними ключами, что позволяет генерировать запросы с JOIN.
- Компоненты LLM, базы данных и векторного хранилища реализованы через абстракции, что даёт возможность переключаться между разными реализациями (OpenAI API / DeepSeek API / Ollama, MySQL / SQLite, ChromaDB / Qdrant).
- Описания таблиц и столбцов преобразуются в эмбеддинги (модель intfloat/multilingual-e5-large) и сохраняются в ChromaDB; при поиске используется гибридный подход (векторный поиск + ключевые слова), уточняющий релевантный контекст схемы.
- Сгенерированный SQL проверяется валидатором: контролируется существование таблиц, допустимость типа запроса и наличие LIMIT.

## Технологический стек

| Компонент               | Технология                         |
|------------------------|------------------------------------|
| API                    | FastAPI + Uvicorn                  |
| LLM (генерация SQL)    | Ollama (deepseek-coder:6.7b)      |
| База данных            | MySQL 8.0                          |
| Векторное хранилище    | ChromaDB                           |
| Эмбеддинги             | sentence-transformers (intfloat/multilingual-e5-large) |
| Валидация SQL          | sqlparse                           |
| Язык реализации        | Python 3.10+                       |


## Требования к окружению

- Python 3.10 или выше
- Установленный и запущенный сервер MySQL 8.0+
- Установленный Ollama с загруженной моделью `deepseek-coder:6.7b`
- Виртуальное окружение Python (рекомендуется)

## Установка и настройка

### Установка зависимостей

```bash
cd путь/к/проекту
python -m venv .venv
.venv\Scripts\activate           
pip install -r requirements.txt
```
- Создать в корне проекта файл .env со следующим содержимым, подставив свои значения:
```Python
DB_HOST=localhost
DB_PORT=3306
DB_NAME=text_to_sql
DB_USER=readonly_user
DB_PASSWORD=ваш_пароль

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

EMBEDDING_MODEL=intfloat/multilingual-e5-large
VECTOR_STORE_PROVIDER=chromadb
CHROMA_PERSIST_DIR=./chroma_data
```

### Создание базы данных(MySQL):

```SQL
CREATE DATABASE text_to_sql CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
python -m app.data.import_csv
```

```SQL
USE text_to_sql;

DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    firstName VARCHAR(100),
    lastName VARCHAR(100),
    patronym VARCHAR(100),
    gender VARCHAR(20),
    age INT,
    birthdate VARCHAR(20),
    email VARCHAR(100),
    phone VARCHAR(30),
    country VARCHAR(50),
    city VARCHAR(50),
    address VARCHAR(200),
    zip VARCHAR(20),
    position VARCHAR(100),
    company VARCHAR(100),
    salary INT,
    login VARCHAR(100)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO employees (employee_id, firstName, lastName, patronym, gender, age, birthdate, email, phone, country, city, address, zip, position, company, salary, login)
SELECT DISTINCT id, firstName, lastName, patronym, gender, age, birthdate, email, phone, country, city, address, zip, position, company, salary, login
FROM generated_data;

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    productName VARCHAR(200),
    price INT,
    category VARCHAR(100),
    description TEXT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO products (productName, price, category, description)
SELECT DISTINCT productName, price, category, description
FROM generated_data;

CREATE TABLE purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    product_id INT NOT NULL,
    registered VARCHAR(20),
    ip VARCHAR(30),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO purchases (employee_id, product_id, registered, ip)
SELECT gd.id, p.product_id, gd.registered, gd.ip
FROM generated_data gd
JOIN products p ON gd.productName = p.productName
               AND gd.price = p.price
               AND gd.category = p.category
               AND gd.description = p.description;

CREATE USER 'readonly_user'@'localhost' IDENTIFIED BY 'надёжный_пароль';
GRANT SELECT ON text_to_sql.employees TO 'readonly_user'@'localhost';
GRANT SELECT ON text_to_sql.products TO 'readonly_user'@'localhost';
GRANT SELECT ON text_to_sql.purchases TO 'readonly_user'@'localhost';
FLUSH PRIVILEGES;
```
- Для наполнения векторного хранилища:
```bash
python -m app.data.schema_indexer
```
## Запуск:
```bash
uvicorn app.main:app --reload
```
- После запуска доступна интерактивная документация по адресу http://localhost:8000/docs
нажать POST /api/ask и try out

- пример запроса:

{
  "question": "Выведи имена сотрудников и названия купленных ими товаров"
}