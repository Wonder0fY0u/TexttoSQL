from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingProvider:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)

    def encode(self, texts: list) -> list:
        return self.model.encode(texts).tolist()