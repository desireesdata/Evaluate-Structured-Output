import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv("../evaluations/overview.csv", sep="\t", encoding="utf-8")
categories = ['Precision', 'Recall', 'F1', "Average Matching Quality", "Overall Matching Quality"]
fig = go.Figure()

for index, row in df.iterrows():
    valeurs = row[categories].tolist()
    
    fig.add_trace(go.Scatterpolar(
        r=valeurs,
        theta=categories,
        fill='toself',
        name=row['Source']  
    ))


fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]  
        )),
    showlegend=True
)

fig.show()
