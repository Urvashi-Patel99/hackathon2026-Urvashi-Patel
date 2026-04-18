import json
import pandas as pd

with open("data/tickets.json") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print(df.head())