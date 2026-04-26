from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "text_to_sql"
    db_user: str = "readonly_user"
    db_password: str = ""

    # LLM
    llm_provider: str = "ollama"
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-coder"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-coder:6.7b"

    embedding_model: str = "intfloat/multilingual-e5-large"

    vector_store_provider: str = "chromadb"
    chroma_persist_dir: str = "./chroma_data"

    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()