# Evaluation sortie structurée

{explanation files blabla}

## CLI

Exemple :

```bash
python main.py -i "gt/low_vt.json" "predictions/low_without_incomplete_entry/*.json" -o "low_granularity_without_incomplete_entry"

# This one don't work (not yet)
python main.py -i "gt/medium_vt.json" "predictions/medium_with_incomplete_entry/*.json" -o "evaluations/medium_granularity_with_incomplete_entry"
```

## Stats

```
# First try
Matching (index T -> index P):
T[0] ⇄ P[0]  — Babin-Chevaye ⇄ Babin-Chevaye
T[1] ⇄ P[1]  — Bachelet Alexandre ⇄ Bachelet (Alexandre)
T[2] ⇄ P[2]  — Barthou (Louis) ⇄ Barthou (Louis), ministre de la guerre
T[3] ⇄ P[3]  — Barthou (Louis) ⇄ Barthou (Louis)
T[4] ⇄ P[4]  — Bazile (Gaston) ⇄ Bazile (Gaston)
T[5] ⇄ P[5]  — Beaumont (Jean) ⇄ Beaumont (Jean)
T[6] ⇄ P[6]  — Bénard (Léonus) ⇄ Bénard (Léonus)
T[7] ⇄ P[7]  — Bender ⇄ Bender
T[8] ⇄ P[8]  — Bérard (Léon) ⇄ Bérard (Léon), garde des sceaux, ministre de la justice
T[9] ⇄ P[9]  — Bérard (Victor) ⇄ Bérard (Victor)
T[10] ⇄ P[10]  — Bérenger (Henry) ⇄ Bérenger (Henry)
T[11] ⇄ P[11]  — Bergeon (Benoît-Charles) ⇄ Bergeon (Benoît-Charles)
T[12] ⇄ P[12]  — Betoulle (Léon) ⇄ Betoulle (Léon)
T[13] ⇄ P[13]  — Blaignan (Raymond) ⇄ Blaignan (Raymond)
T[14] ⇄ P[14]  — Blaisot ⇄ Blaisot, ministre de la santé publique
T[15] ⇄ P[15]  — Blois (comte Louis de) ⇄ Blois (comte Louis de)
T[16] ⇄ P[16]  — Boivin-Champeaux ⇄ Boivin-Champeaux
T[17] ⇄ P[17]  — Bompard (Maurice) ⇄ Bompard (Maurice)
T[18] ⇄ P[18]  — Bon ⇄ Bon
T[19] ⇄ P[19]  — Borgeot (Charles) ⇄ Borgeot (Charles)
T[20] ⇄ P[20]  — Borrel (Antoine) ⇄ Borrel (Antoine)
T[21] ⇄ P[21]  — Bosc (Jean) ⇄ Bosc (Jean)
T[22] ⇄ P[22]  — Bourdeaux (Henry) ⇄ Bourdeaux (Henry)
Matching stats:
Precision: 1.0000
Recall: 1.0000
F1: 1.0000
Average Matching Quality: 0.9569
Overall Matching Quality: 0.9852
``` 

Utilisation :

  #### Générer des statistiques
  python main.py -i "truth.json" "predicted.json" -o "stats.txt"

  #### Avec distance Levenshtein
  python main.py -i "truth.json" "predicted.json" -d "levenshtein" -o "stats.txt"

  #### Exporter les appariements en CSV  
  python main.py -i "truth.json" "predicted.json" -m -o "matches.csv"

  #### Ou automatiquement si l'extension de sortie est .csv
  python main.py -i "truth.json" "predicted.json" -o "matches.csv"

  Fonctionnalités :
  - -i : 2 fichiers d'entrée (vérité terrain + prédictions)
  - -o : fichier de sortie (.txt pour stats, .csv pour appariements)
  - -d : choix distance (levenshtein ou ratcliff)
  - -m : forcer export CSV des appariements

  Les fichiers JSON sont automatiquement détectés (format avec listes_des_intervenants ou liste
  directe).
