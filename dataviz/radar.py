import plotly.graph_objects as go
import pandas as pd

# Charger les données
df = pd.read_csv("../evaluations/overview.csv", sep="\t", encoding="utf-8")

# Catégories pour l'axe polaire
categories = ['Precision', 'Recall', 'F1', "Average Matching Quality", "Overall Matching Quality"]

# Appliquer une transformation exponentielle
exponent = 10  # Ajustez cet exposant pour accentuer les différences
df_transformed = df.copy()
for category in categories:
    df_transformed[category] = df[category] ** exponent

# Créer une figure
fig = go.Figure()

# Ajouter une trace pour chaque ligne du DataFrame transformé
for index, row in df_transformed.iterrows():
    valeurs = row[categories].tolist()
    fig.add_trace(go.Scatterpolar(
        r=valeurs,
        theta=categories,
        fill='toself',
        name=row['Source']
    ))

# Mettre à jour la disposition
fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]  # Ajustez cette plage en fonction des valeurs transformées
        )),
    showlegend=True
)

# Afficher la figure
fig.show()
