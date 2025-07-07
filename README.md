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

### Résultats

```

Source	Precision	Recall	F1	Average Matching Quality	Overall Matching Quality	Integrated Matching Quality	Overall Matching Quality (IMQ-based)	Nombre d'entrées vérité terrain	Nombre d'entrées prédites	Nombre d'appariements
page_03_03	1.0000	1.0000	1.0000	0.8997	0.9642	0.8996	0.9308	25	25	25
page_03_02	1.0000	1.0000	1.0000	0.9404	0.9793	0.9403	0.9594	25	25	25
page_03_01	1.0000	1.0000	1.0000	0.9441	0.9807	0.9441	0.9620	25	25	25
page_10_02	1.0000	1.0000	1.0000	0.8778	0.9556	0.8777	0.9150	23	23	23
page_10_03	1.0000	1.0000	1.0000	0.8179	0.9309	0.8177	0.8707	23	23	23
page_10_01	1.0000	1.0000	1.0000	0.8828	0.9576	0.8827	0.9187	23	23	23
page_04_03	1.0000	1.0000	1.0000	0.9616	0.9869	0.9615	0.9740	19	19	19
page_04_01	1.0000	1.0000	1.0000	0.9796	0.9931	0.9795	0.9863	19	19	19
page_04_02	1.0000	1.0000	1.0000	0.9767	0.9921	0.9766	0.9843	19	19	19
page_02_02_corpusense_boxes	1.0000	0.9130	0.9545	0.9928	0.9670	0.9064	0.9358	23	21	21
page_02_01_vt	1.0000	1.0000	1.0000	0.9554	0.9847	0.9553	0.9698	23	23	23
page_02_03_corpusense_raw	1.0000	0.9565	0.9778	0.9540	0.9697	0.9124	0.9406	23	22	22
page_05_01	1.0000	1.0000	1.0000	0.8546	0.9463	0.8544	0.8981	19	19	19
page_05_02	1.0000	1.0000	1.0000	0.8659	0.9509	0.8657	0.9063	19	19	19
page_05_03	1.0000	1.0000	1.0000	0.8463	0.9429	0.8461	0.8919	19	19	19

```

#### Moyenne

Precision                                1.000000
**Recall                                   0.991300**
F1                                       0.995487
**Average Matching Quality                 0.916640**
Overall Matching Quality                 0.966793
**Integrated Matching Quality              0.908000**
**Overall Matching Quality (IMQ-based)     0.936247**
Nombre d'entrées vérité terrain         21.800000
Nombre d'entrées prédites               21.600000
Nombre d'appariements                   21.600000
