import chromadb
from app.config import settings
from app.domain.interfaces import VectorStore

class ChromaStore(VectorStore):
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="schema_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_embeddings(self, texts, metadata, embeddings):
        ids = [str(i) for i in range(len(texts))]
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadata,
            embeddings=embeddings
        )

    async def hybrid_search(self, query_embedding, query_text, top_k=5):
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        docs = []
        if results["documents"]:
            for i in range(len(results["documents"][0])):
                docs.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # косинусное расстояние -> близость
                })
        return docs

# фабрика
def get_vector_store() -> VectorStore:
    if settings.vector_store_provider == "chromadb":
        return ChromaStore()
    raise ValueError("Неподдерживаемое векторное хранилище")