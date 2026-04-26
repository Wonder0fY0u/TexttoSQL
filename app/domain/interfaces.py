from abc import ABC, abstractmethod
from typing import List

class TextGenerator(ABC):
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """генерирует текст (SQL) по переданному промпту."""
        pass

class VectorStore(ABC):
    @abstractmethod
    async def add_embeddings(self, texts: List[str], metadata: List[dict], embeddings: List[List[float]]):
        pass

    @abstractmethod
    async def hybrid_search(self, query_embedding: List[float], query_text: str, top_k: int = 5) -> List[dict]:
        """гибридный поиск: по векторам и ключевым словам."""
        pass

class DatabaseConnector(ABC):
    @abstractmethod
    async def execute_query(self, sql: str) -> List[dict]:
        pass

    @abstractmethod
    async def get_table_schema(self, table_name: str) -> dict:
        pass