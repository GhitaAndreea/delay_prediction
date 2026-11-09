import json
import pandas as pd

with open("..c", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data["flights"])
print("API total:", data["total"])
print("Rows:", len(df))
print("Unique ids:", df["id"].nunique())