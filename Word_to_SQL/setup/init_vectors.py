import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from app.vector_store.chroma_store import ChromaVectorStore

df = pd.read_csv("data/generated_data.csv")
store = ChromaVectorStore()
store.add_schema("sales", df)
print("Векторная база данных (ChromaDB) обновлена.")