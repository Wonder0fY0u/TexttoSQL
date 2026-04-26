import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from app.repositories.database import get_engine

df = pd.read_csv("data/generated_data.csv")
engine = get_engine("sqlite", path="data/sales.db")
df.to_sql("sales", engine, index=False, if_exists="replace")
print("База данных SQLite готова.")