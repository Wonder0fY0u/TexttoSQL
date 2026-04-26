import pandas as pd
from app.vector_store.chroma_store import ChromaVectorStore

df = pd.read_csv("data/generated_data.csv")
store = ChromaVectorStore()
store.add_schema("sales", df)
print("Векторная база пересоздана")