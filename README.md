# Evaluation sortie structurée

{explanation files blabla}

### Générer JSON structured output

```
python3 predictions/low_with_incomplete_entry/output_design.py 
```

## CLI

Exemple :

```bash
python run_evaluations.py -p predictions/low_with_incomplete_entry -o evaluations_/low

#caduque  :
python main.py -i "gt/low_vt.json" "predictions/low_with_incomplete_entry/*.json" -o "evaluations_delete/low_granularity_with_incomplete_entry"

# This one don't work (not yet)
python main.py -i "gt/medium_vt.json" "predictions/medium_with_incomplete_entry/*.json" -o "evaluations/medium_granularity_with_incomplete_entry"
```

## Stats
> Dans `/evaluations`

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
