import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv("../evaluations/overview.csv", sep="\t", encoding="utf-8")
categories = ['Precision', 'Recall', 'F1', "Average Matching Quality", "Overall Matching Quality"]

fig = px.bar(df, x="Source", y=categories)
fig.show()