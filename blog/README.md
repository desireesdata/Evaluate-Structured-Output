> *[Dans le billet précédent](https://desireesdata.fr/deblais-et-remblais-textuels-sur-levaluation-des-llms-pour-des-taches-dindexation-documentaire-avec-le-transport-optimal-et-la-sortie-structuree-1-2/), j'ai établi les problématiques de l'évaluation de la sortie structurée pour des tâches de type indexation. Mais beaucoup de questions restaient en suspens, à commencer par l'analyse au niveau de la structure des objets et la métrique à utiliser. Dans cette partie -- la dernière ? -- il s'agira donc d'exposer des résultats avec des métriques "classiques" et deux autres, issues et adaptée du travail de deux chercheurs à l'EPITA, qui établissent la qualité des appariements.*

## Mesurer pour savoir, savoir ce qu'il faut mesurer (et mesurer ce que l'on tient à savoir)

Il est question ici de continuer sur les aspects techniques de ce qui a été amorcé la dernière fois autour de cette problématique : *comment justifier en SHS un usage scientifique des données générées par un LLM ?* Autrement dit, *quoi et comment mesurer les données qu'il a produites pour telle question de recherche* ? Cette problématique mériterait sans doute un article à part entière et on ne fera que l'aborder en filigrane. Il est cependant honnête d'en dispenser un fond de sauce ici, même brièvement, pour ne pas servir cru les résultats obtenus. On va tenter de prendre au sérieux l'idée de *mesure* car elle concerne aussi bien des résultats quantitatifs que les pratiques qui les font émerger.

![](https://desireesdata.fr/wp-content/uploads/2025/06/Human-Locomotion-Chronophotography-Composite-c-1886-Etienne-Jules-Marey.png)

Human Locomotion Chronophotography Composite, c. 1886. Étienne-Jules Marey.

### Valuation, évaluation

En histoire, par exemple, on pourrait employer les modèles génératifs (comme Chat GPT ou Mistral) pour extraire les entités nommées d'archives numérisées. Avec ces données, on pourrait constituer des bases de données dans un format standard afin de répondre avec une question de recherche ou à des besoins prosopographiques. Ici, on s'intéresse à la dimension technique de l'évaluation de ces LLMs afin de savoir *dans quelle mesure ses résultats sont exploitables*. Derrière des enjeux très pragmatiques de l'utilisation de données pour un besoin contingent, il y a le décor aux allures épistémologiques de la "valuation". La *valuation* est ce qui justifie le choix *a priori* de telles méthodes pour enquêter sur les données "en vue de".

> La *valuation* est un terme que j'emploie en pensant au philosophe pragmatiste John Dewey : la *valuation* prépare *l'évaluation*. **Tout dispositif de savoir implique des choix de design**, souvent tacites : **formats, métriques, seuils, ontologies, visualisations**… Et que ces choix ne sont pas neutres, mais **porteurs de modèles du monde**.

L'exploitabilité des données peut être exprimée par des métriques qui indiquent *combien* on peut donner créance au travail du LLM. Le choix des métriques n'est pas un absolu objectif car tout dépend de ce qu'on veut analyser, de ce à quoi on tient à savoir. Il y a alors une sorte de diplomatie entre des besoins concrets exigés par une question de recherche "SHS" et de la traduction technique des valuations qui déterminent les moyens d’évaluation appropriés. En somme, pour faire parler l'ami philosophique Gaston Bachelard, "les instruments sont de la théorie réifiée". On a besoin de mesurer pour savoir si des données sont exploitables; mais il faut aussi savoir ce qu'il faudrait mesurer par rapport à ce que l'on désire savoir (et comment). Il y a là une sorte de co-détermination de la prémisse et de la conclusion -- ou des moyens et des fins -- qu'il ne faudrait malgré tout ne pas confondre avec une contradiction logique indépassable, laquelle empêcherait toute installation de prétentions scientifiques. C'est justement sachant cela -- et sans jamais dire que tout se vaudrait parce qu'il n'y a effectivement pas de faits sans valeurs -- qu'il faut entrer dans une démarche de rectification, démarche d'ailleurs parfaitement participante aux critères de scientificité.

![](https://desireesdata.fr/wp-content/uploads/2025/06/splashofdrop00wortuoft_0055-855x1024.jpeg)

Professor A. M. Worthington, *The Splash of a Drop* (London: S.P.C.K., 1895). Idée d'illustration soufflée par le livre "Objectivité" de Lorraine Daston et Peter Galison.

### La question prépare la mesure

Cela étant dit, il faut se mettre maintenant à la place de l'historien.ne, travaillé par une question de recherche ou cherchant à en formuler une : **je veux avoir un aperçu (voire une cartographie) de l'activité parlementaire des sénateurs pour l'année 1931**. (Car je veux avoir une photographie d'une période critique.) Je veux savoir *qui* parle et *quand* (et on pourrait imaginer de *quoi*). Sachant que le Journal Officiel restitue l'activité parlementaire et que le Journal Officiel a une pagination annuelle continue (la page 1 correspond au premier jour d'activité de l'année qui tombe en janvier, et la dernière page à la dernière séance, en décembre), il m'importe donc de collecter l'ensemble des activités datées (ou "datables") de chaque intervenant au sénat (sénateurs, mais aussi ministres interpellés). Les tables du Sénat m'offrent une telle liste, mais sans les dates -- qui sont donc supposées avec la pagination. Pour ce faire, je veux extraire automatiquement des données issues des tables du Sénat (disponibles sur Gallica). Mais, comme on s'imagine en historien sérieux, je veux être sûr que ces données soient vraies -- ou suffisamment fiables pour en dire quelque chose avec prudence -- car je les exploite pour ma thèse. Ma valeur de référence ce sont bien les entrées car chacune d'elle représente un acteur de l'activité de la Chambre Haute.

![](https://desireesdata.fr/wp-content/uploads/2025/06/Table_annuelle_du_Journal_officiel_._bpt6k65430703_1614-1024x728.jpg)

Fragment des Tables du JO de 1931. Sur [Gallica](https://gallica.bnf.fr/ark:/12148/bpt6k65430703/f161.item.zoom#).

Ce que l'on tient à savoir : les entrées générées par le LLM contiennent-elles des données bien structurées et "solidaires" ? (Par exemple, on veut être sûr que telle page concerne bien tel sénateur afin de ne pas lui attribuer une activité qui ne lui appartient pas.) De "combien" dévient-elles par rapport à une vérité terrain ? peut-on ainsi faire confiance aux données générées ?

### Traduction quantitative des besoins énoncés

Autrement dit, en faisant un parallèle avec les exemples classiques de la statistique, on cherche à évaluer un système de traitement selon les critères suivants :

- *Sa précision* : les données générées sont-elles fiables ?  
  *(« Y a-t-il eu un bon diagnostic ? »)*  
  → Puis-je légitimement me fier aux données produites, en considérant un "taux de justesse" parmi les appariements réalisés ?
- *Son rappel* : est-ce que les données produites couvrent l’ensemble des cas ou seulement une partie ?  
  *(« A-t-on diagnostiqué tous les patients ou seulement certains ? »)*  
  → Puis-je dire que les résultats sont globalement représentatifs de l'ensemble des cas à traiter ?
- *Son F-score* : une moyenne harmonique entre précision et rappel qui combine ces deux dimensions.  
  *(« La méthodologie de diagnostic est-elle globalement satisfaisante ? »)*  
  → Un compromis entre justesse et couverture.

On veut appliquer ces idées au niveau des entrées qu'on a appariés. D'après le travail de chercheurs à l'EPITA[1](#18778ef4-b4a5-4d4a-ac98-d938768b15ce), il est utile de proposer une métrique sur la qualité des appariements en eux-mêmes, car ces scores s'y basent:

- *La qualité moyenne des appariements* qui mesure la fidélité des appariements individuels (par exemple via une distance de similarité). "*(Les appariements sont-ils chacun de bonne qualité, même si leur nombre est limité ?)*"
- *La qualité globale des appariements* qui tient compte à la fois de la qualité des appariements et de leur couverture. ("*En combinant justesse et exhaustivité, à quel point peut-on dire que l’ensemble du travail est fiable ?")*

![](https://desireesdata.fr/wp-content/uploads/2025/06/17-Brossa_Poema-visual-980-1-980x762-1.jpg)

Joan Brossa, *Poema Visual* (19/25).

On peut aller encore plus loin pour estimer les limitations inhérentes à la méthode d'appariement choisie qui peut fragiliser la légitimité des scores, à savoir ici le transport optimal. C'est une méthode qui a été *choisie* parmi d'autres possibles.

On pourrait imaginer d'autres méthodes d'appariements, en effet. Par exemple, étant donné que les données se suivent, avec un algorithme glouton : il choisirait, pour chaque vérité terrain, et dans l'ordre où sa vient, la donnée prédite avec la distance de Levenshtein la plus faible. Mais à mesure que l'on avance dans les appariements, on prive potentiellement les derniers des appariements qui pourraient leur être dûs.

> *Et... on pourrait aller encore plus loin en déterminant si la notion de distance, sur laquelle se base des appariements et le score de qualité panotpique est la plus judicieuse possible en étudiant la "métricité" des matrices de coût (leur "topologie"). Ici, c'est une hypothèse personnelle très spéculative, assez peu utile en pratique mais que je trouve intéressante. Je la mentionnerai aussi plus bas juste pour le plaisir de la spéculation.*

Dans le billet précédent, on a tout mis à plat : on a comparé chaque nœud textuel et fait des appariements sans se soucier du rapport hiérarchique entre les données. Cela a permis d'exposer "à plat" la notion de distance (notamment de Levenshtein) et celle de transport optimal. Mais notre véritable valeur, ce sont les *entrées* et tout ce qu'elles encapsulent. Ces entrées, ce sont donc les objets JSON :

e![](http://desireesdata.fr/wp-content/uploads/2025/06/exemple_JO-1024x636.jpg)

Exemple d'entrée, pour "Babin-Chavaye" qui équivaut à un objet JSON.

Comme mentionné la dernière fois, le transport optimal n'est pas vraiment une méthode "diachronique" elle peut apparier des éléments très loin pour peu que ça soit mathématiquement justifié ("peu couteux"). En comparant avec une matrice de similarité et en appariant *à plat* les éléments les plus proches on peut fragiliser la dimension hiérarchique du JSON.

> *De fait, sur mes données de test, ça n'est pas arrivé : mais rien n'indique, étant donné la nature "permutative" du transport optimal, qu'on ait un jour localement une mauvaise combine, même si ça assure un bon match global. C'est une approche solide et qui peut-être appliquée à d'autres corpus avec des mises en page plus exotique, moins linéaires*.

Comme on veut garder la solidarité des entrées pour les évaluer, c'est donc elles qui faut comparer en vue d'apparier, et même si une des informations, côté données générées par le LLM, est manquant ou faux car on veut justement en évaluer la précision.

![](https://desireesdata.fr/wp-content/uploads/2025/06/Typo2-grand-1024x657.jpg)

*Typologie 1*, la boule de pétanque, éd. B42, 2017

> *A noter : on aurait aussi très bien pu utiliser une moyenne des distances des éléments appariés à plat en redécoupant par dessus avec une Regex puisque nos entrées commencent par des lettres et finissent pas un nombre. On aurait pu réengager le travail de la dernière fois. De fait, c'est une approche risquée (car on ne sait pas a priori à quoi peuvent ressembler nos données) et absolument pas applicables à l'échelle. Comme on le voit déjà, il y a plusieurs façons de faire, et elles ont leurs raisons selon moi. Je crois cependant que l'heuristique de la manipulation directe d'entrée "as objects" est plus expressive. C'est un meilleur "design" sachant notre question de recherche.*

## Mise en pratique : mesurer en Python la qualité des sorties structurées

> *Pour cette partie, je remercie bien sûr Joseph de m'avoir proposé un script à partir duquel j'ai pu broder des classes et comprendre toutes les métriques !*

### Passage à la POO (programmation orientée objet)

On va réadapter ce qu'on a fait la dernière fois en POO. Traduit en Python, on peut représenter chaque entrée (donc chaque acteur) comme l'instance d'une classe `Entry` dans laquelle on injectera les éléments du JSON:

```
class Entry:
    def __init__(self, data: RawEntry):
        """Initialization with data from json (object)"""
        self.data = data

    def get(self) -> RawEntry:
        """Return the entire object"""
        return self.data
```

On pourra utiliser cette classe aussi bien pour la vérité terrain que pour les données prédites. Cette classe représente donc les données qui vont être comparées. On peut lui ajouter une méthode qui permet d'afficher ce qu'elle contient (`.get()`).

On aura aussi une seconde classe dédiée à la comparaison de ces entrées, la classe ``Matcher``:

```
class Matcher:
    def __init__(self, entries_a: List[Entry], entries_b: List[Entry], distance_method: str = "ratcliff"):
        """A Matcher is a comparator; he compares two sets of entry and produces a matrix"""
        self.entries_a = entries_a
        self.entries_b = entries_b
        self.distance_method = distance_method
        self.cost_matrix = self.compute_cost_matrix(distance_method)
        self.matches = self.match()
```

Elle prend donc comme paramètre une entrée A (la vérité terrain par exemple) et une entrée B (les données générées); et également un paramètre pour choisir la distance sur laquelle se basera la matrice de coût. Je n'ai pas encore, à ce stade, fait de paramètre pour choisir la méthode d'appariement, n'utilisant que le transport optimal pour l'instant.

On va maintenant implémenter ce qu'on a vu la dernière fois, à commencer par la matrice de coût qui est une prérogative du Matcher. On ajoute cette méthode à la classe `Matcher` :

```
#Méthode de la classe Matcher
def compute_cost_matrix(self, distance_method: str = "ratcliff") -> np.ndarray:
        n, m = len(self.entries_a), len(self.entries_b)
        cost_matrix = np.zeros((n, m))

        for i, entry_a in enumerate(self.entries_a):
            for j, entry_b in enumerate(self.entries_b):
                if distance_method == "levenshtein":
                    cost_matrix[i, j] = entry_a.distance_to_levenshtein(entry_b)
                else:
                    cost_matrix[i, j] = entry_a.distance_to(entry_b)

        return cost_matrix
```

Ici, on peut choisir d'utiliser soit la distance de Levensthein -- soit celle de Ratcliff/Obershelp. Cette option peut être utile si on veut faire une CLI à partir du script. J'ai fait ici le choix de retourner les distances depuis une méthode "distance_to" de '`Entry`'. C'est un choix discutable, mais l'idée est que chaque entrée "sache" à quelle distance elle peut se trouver d'un autre entrée. Et c'est Matcher qui peut la demander :

```
# Méthode de la classe Entry
def distance_to(self, other: 'Entry') -> float:
        """Return distance between him and an another object"""
        """NB : ==> average field-to-field distances (Ratcliff/Obershelp)"""
        def field_distance(f1: str, f2: str) -> float:
            return 1 - SequenceMatcher(None, f1, f2).ratio()

        total = 0.0
        count = 0

        # Compare fields with the same label
        for field in ["nom", "references_pages"]:
            norm_self = self.normalize_field(field)
            norm_other = other.normalize_field(field)

            if norm_self or norm_other:
                total += field_distance(norm_self, norm_other)
                count += 1

        return total / count if count else 1.0
```

On va maintenant implémenter le travail d'appariement qui, pour le coup, revient de droit au Matcher :

```
# Méthode de Matcher
def match(self) -> List[Tuple[int, int]]:
        """A faire : paramètre pour choisir la méthode d'assignement"""
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return list(zip(row_ind, col_ind))
```

Il n'y a ici qu'une seule façon d'apparier. Mais, dans l'optique de développement d'une CLI, on pourrait imaginer une option qui permet de choisir d'autres algorithmes d'appairage.

### Des statistiques "opaques" : précision, rappel, F1

Maintenant que l'on peut sortir des appariements, il ne reste plus qu'à les évaluer ! Ici, on va calculer la précision ("les données générées sont elles fidèles ?"), le rappel ("a-t-on toutes les données ?" et le F-score (F1, "un score qui combine précision et rappel"). C'est encore une prérogative du Matcher :

```
# Méthode de MAtcher
def compute_precision_recall_f1(self) -> Dict[str, float]:
        tp = len(self.matches)
        fp = len(self.entries_b) - tp
        fn = len(self.entries_a) - tp

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        return {"Precision": precision, "Recall": recall, "F1": f1}
```

C'est ici qu'il faut prendre un peu de temps. La *précision*, le *rappel* et le *F1* reposent sur le calcul de trois valeurs : $TP, FP, FN$ (True Positive, False Positive, False Negative):

- $TP$ représente le nombre d'appariements trouvés;
- $FP$ représente nombre total de prédictions moins le nombre de vrais positifs. Cela représente les prédictions qui ne correspondent à aucune entrée de la vérité terrain;
- $FN$ représente le nombre total d'entrées de la vérité terrain moins le nombre de vrais positifs (de matchs). Cela représente les entrées de la vérité terrain qui n'ont pas été correctement prédites.

On le voit : ces valeurs reposent sur la cardinalité (le nombre total) de différents ensembles. Cela veut dire qu'on ne regarde pas la "qualité" des appariements, juste leur quantité. Cela a ses limites car on pourrait très bien avoir des doublons et des éléments manqués qui se compensent quantitativement. Ainsi, la fonction Python `compute_precision_recal_f1` dit :

- “J’ai `len(self.matches)` appariements que je considère comme *vrais positifs* ($TP$).”
- Puis elle suppose que tout ce qui n’est pas apparié est un faux négatif (FN) ou un faux positif (FP).

... Et pour terminer, elle applique ensuite les formules classiques de précision / rappel / F1 que je ne détaille pas ici puisque le code Python est assez explicite.

### Premiers résultats "opaques" de la sortie structurée

Dans mon cas, j'ai testé la sortie structurée à partir de trois différents textes OCRisés :

1. un OCR corrigé à main, réputé sans fautes (un OCR "parfait");
2. un OCR obtenu via un outil de zoning manuel développé par le projet Mezanno ("Corpusense", en développement);
3. et un OCR plus "brutal", via Corpusense qui couvre toute la page, sans se soucier des zones d'intérêts (capte par exemple le foliotage)

Voici les résultats (sur une échelle de 0 à 1):

| Source                                                | Precision | Recall | F1     |
| ----------------------------------------------------- | --------- | ------ | ------ |
| 1. Sortie structurée à partir d’un OCR réputé parfait | 1.0000    | 1.0000 | 1.0000 |
| 2. Sortie structurée via zoning manuel                | 1.0000    | 0.9565 | 0.9778 |
| 3. Sortie structurée via OCR brut (toute la page)     | 1.0000    | 0.9565 | 0.9778 |

![](https://desireesdata.fr/wp-content/uploads/2025/06/Capture-decran-du-2025-06-29-18-55-29-1024x488.png)

Capture d'écran (fragment) du tableau généré lors de l'évaluation. Ici, le cas n°1. On voit que les données prédites (Predicted_Nom) ne sont pas toujours identiques à la vérité terrain (rien de grave, certes). Le F1 ne montre pas ces différences qualitatives.

On a donc, *semble-t-il*, de bons résultats. Il est d'ailleurs parfait pour un OCR propre (F1 100%). Globalement, la sortie structurée semble faire toujours les bons appariements (précision à 100%). On a cependant quelques oublis du côté de la sortie structurée via Corpusense, mais rien de critique puisqu'on a 95,6% du corpus qui est pris en compte. Cela fait un score global très correct, de 97,7%.

> *A noter que ma vérité terrain ne couvre pour l'instant environ que 10% du corpus que je veux extraire automatiquement -- c'est un premier pas, et l'idéal sera de monter à 20%. A noter également que j'utilise un "petit" modèle : Ministral 8b.*

Plusieurs objections : comme je l'ai dit, ce sont des statistiques "opaques", basées sur un comptage "rudimentaire". On voit par exemple dans l'image ci-dessus que les données prédites (Predicted_Nom) ne sont pas toujours identiques à la vérité terrain (Truth_Nom). Rien de grave, certes, d'autant plus que les données en plus ne sont pas fausses -- elle ne conviennent pas à la vérité terrain. C'est une bonne illustration que le F1, basé sur le précision et le rappel, ne montre pas ces différences qualitatives. On remarque également que 2) et 3) ont le même score... mais on peut se demander si *qualitativement* -- c'est-à-dire en regardant de plus près les appariements -- l'un est meilleur que l'autre. A ajouter que cette évaluation ne prend pas en compte le contenu des interventions (à venir, mais la méthode reste la même).

Il y aurait aussi d'autres dimensions à tester comme les différentes façons d'apparier (même si ici, il semble bien faire le travail); mais aussi avec les différents modèles et différents prompts. La qualité de l'image, bien sûr, joue beaucoup. Toutes les pages ne bénéficient pas de la même qualité de numérisation. Le petit fond n'est pas assez large si bien que les pages centrales du recueil sont engouffrées dans la courbure du livre, ce qui nuit à la qualité de l'OCR.

> *Le code complet est disponible sur mon Github (projet encore en cours) : [GitHub - desireesdata/Evaluate-Structured-Output](https://github.com/desireesdata/Evaluate-Structured-Output/tree/main)*

## De la transparence : évaluer les appariements avec l'AMQ et l'OMQ

On va se pencher sur une dimension plus qualitative : est-ce que malgré ce protocole d'extraction des informations -- l'OCR, le prompt, la sortie structurée et l'appariement -- nos données d'arrivées sont bonnes ? Quand on match un objet, est-ce qu'on le match bien ?

[...]

### Résultats

| Source                                             | Average Matching Quality | Overall Matching Quality |
| -------------------------------------------------- | ------------------------ | ------------------------ |
| Sortie structurée à partir d’un OCR réputé parfait | 0.9592                   | 0.9860                   |
| Sortie structurée via l’outil Mezanno              | 0.9923                   | 0.9826                   |
| Sortie structurée via l’OCR brut                   | 0.9568                   | 0.9553                   |

> à terminer

## Limites

Basée sur un appariement qui n'est pas la seule solution ! Peut être faudrait il dans certains cas, selon la question de recherche, un appariement avec moins de précision (99% de précision) mais un rappel de 100% pour avoir une vue d'ensemble plus globale d'un phénomène. Peut être faut il un autre appariement; d'autres distances, d'autres indicateurs pour des données agrégées que la moyenne.

> à terminer

## Comment valoriser ou employer les données sachant tel ou tel résultat?

> à terminer

Mettre des warnings qui exposent les limitations des résultats pour motiver des façons d'interpréter des extractions via sortie structurée. 

Comme sur data.ina.fr ?

![](https://desireesdata.fr/wp-content/uploads/2025/06/Capture-decran-du-2025-06-30-09-34-16.png)
