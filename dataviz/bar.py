import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Charger les données
df = pd.read_csv("../evaluations/overview.csv", sep="\t", encoding="utf-8")

# Catégories pour les barres
categories = ['Precision', 'Recall', 'F1', "Average Matching Quality", "Overall Matching Quality"]

# Appliquer une transformation exponentielle
exponent = 10  # Ajustez cet exposant pour accentuer les différences
df_transformed = df.copy()
for category in categories:
    df_transformed[category] = df[category] ** exponent

# Créer une figure avec des barres empilées
fig = go.Figure()

# Ajouter des barres pour chaque catégorie
for category in categories:
    fig.add_trace(go.Bar(
        x=df_transformed['Source'],
        y=df_transformed[category],
        name=category
    ))

# Mettre à jour la disposition pour des barres empilées
fig.update_layout(barmode='stack')

# Afficher la figure
fig.show()
