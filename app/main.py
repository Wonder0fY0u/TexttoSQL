from fastapi import FastAPI
from app.api import routes
from app.config import settings
from app.repositories.database import MySQLConnector
from app.repositories.vector_store import get_vector_store
from app.repositories.embedding_provider import EmbeddingProvider
from app.domain.interfaces import TextGenerator


class OllamaGenerator(TextGenerator):
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def generate(self, prompt: str, max_tokens: int = 512) -> str:
        import aiohttp
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0}
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/generate", json=data) as resp:
                resp.raise_for_status()
                result = await resp.json()
                return result["response"].strip()


app = FastAPI(title="Text-to-SQL Ollama Ассистент")

@app.on_event("startup")
async def startup():
    db = MySQLConnector()
    await db.connect()
    routes.db_conn = db

    routes.vector_store = get_vector_store()

    routes.embedder = EmbeddingProvider()

    routes.llm_gen = OllamaGenerator()

@app.on_event("shutdown")
async def shutdown():
    await routes.db_conn.disconnect()

app.include_router(routes.router, prefix="/api")