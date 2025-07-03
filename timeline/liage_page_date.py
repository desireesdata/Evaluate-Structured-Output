import pandas as pd
import json
from datetime import date

# 1. Charger le CSV
df = pd.read_csv("data/data_1931.csv", sep="\t")

# 2. Créer le mapping page → date
page_to_date = {}

for _, row in df.iterrows():
    jour, mois = int(row['jour']), int(row['mois'])
    pages = eval(row['pages'])  # ou ast.literal_eval
    for page in pages:
        page_to_date[int(page)] = date(1931, mois, jour)

# 3. Charger le JSON
with open("data/p_02.json", "r") as f:
    data = json.load(f)

# 4. Associer les intervenants à leurs dates d’intervention
intervenant_dates = {}

for personne in data["listes_des_intervenants"]:
    nom = personne["nom"]
    refs = personne["references_pages"]
    
    if isinstance(refs, list):
        dates = sorted(set(
            page_to_date.get(page) for page in refs if page in page_to_date
        ))
    else:
        dates = []  # ou ['<renvoi d\'index>'] si tu veux le garder
    
    intervenant_dates[nom] = dates

# 5. Affichage de l’extrait
for nom, dates in intervenant_dates.items():
    print(nom, ":", dates)
