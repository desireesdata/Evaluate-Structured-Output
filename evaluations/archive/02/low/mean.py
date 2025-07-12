import pandas as pd
data = pd.read_csv("summary_table.csv", sep='\t')
df = pd.DataFrame(data)
moyennes = df.mean(numeric_only=True)
print(moyennes)
