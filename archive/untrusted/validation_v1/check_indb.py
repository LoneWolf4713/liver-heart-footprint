import pandas as pd

df = pd.read_excel("research_log/data/indb_repo/INDB.xlsx")
print(df.columns)
print(df.head(2))
