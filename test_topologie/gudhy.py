import gudhi
import numpy as np
import ot
from gudhi.wasserstein import wasserstein_distance
from tslearn.metrics import dtw

a = np.load('cost_matrices_output/gt.npy')
b = np.load('cost_matrices_output/predicted.npy')
# b = a
c = np.load('cost_matrices_output/noisy.npy')


# Pour la Vérité Terrain
rips_complex_gt = gudhi.RipsComplex(distance_matrix=a, max_edge_length=1.0) # max_edge_length est le rayon max de la filtration
simplex_tree_gt = rips_complex_gt.create_simplex_tree(max_dimension=1) # Calcule H0 (connexité) et H1 (trous)
diagram_gt = simplex_tree_gt.persistence()

print("\n\n diagramme de persistance VT (ex: (dimension, (naissance, mort))):")
for dim, (birth, death) in diagram_gt:
    print(f"Dim {dim}: [{birth:.3f}, {death:.3f})")

# Pour les données prédites 
rips_complex_pred = gudhi.RipsComplex(distance_matrix=b, max_edge_length=1.0)
simplex_tree_pred = rips_complex_pred.create_simplex_tree(max_dimension=1)
diagram_pred = simplex_tree_pred.persistence()

print("\n\n diagramme de persistance PRED:")
for dim, (birth, death) in diagram_pred:
    print(f"Dim {dim}: [{birth:.3f}, {death:.3f})")


# Extraction des diagrammes par dimension
diagram_H0_gt = np.array([pt[1] for pt in diagram_gt if pt[0] == 0])
diagram_H0_pred = np.array([pt[1] for pt in diagram_pred if pt[0] == 0])

diagram_H1_gt = np.array([pt[1] for pt in diagram_gt if pt[0] == 1])
diagram_H1_pred = np.array([pt[1] for pt in diagram_pred if pt[0] == 1])


dist_bottleneck_H0 = gudhi.bottleneck_distance(
        diagram_H0_gt, diagram_H0_pred
    )
print("distance de bottleneck : ", dist_bottleneck_H0)

dist_bottleneck_H1 = gudhi.bottleneck_distance(
        diagram_H1_gt, diagram_H1_pred
    )
print("distance de bottleneck d1: ", dist_bottleneck_H1)

n = float(a.shape[0])
# Calculer ls distances entre les diagrammes
# Bottleneck distance pour H0
if len(diagram_H0_gt) > 0 and len(diagram_H0_pred) > 0:
    # Correction ici !
    dist_bottleneck_H0 = gudhi.bottleneck_distance(
        diagram_H0_gt, diagram_H0_pred
    )
    print(f"\nDistance de Bottleneck (H0) : {dist_bottleneck_H0:.4f}")
else:
    print("\nPas assez de points en H0 pour calculer la distance de Bottleneck.")

# Wasserstein distance pour H1
if len(diagram_H1_gt) > 0 and len(diagram_H1_pred) > 0:
    # Correction ici !
    dist_wasserstein_H1 = gudhi.wasserstein_distance(
        diagram_H1_gt, diagram_H1_pred
    )
    print(f"Distance de Wasserstein (H1): {dist_wasserstein_H1:.4f}")
else:
    print("Pas assez de point en H1 pour calculer la dist de Wassershtein.")

# Wasserstein distance pour H0 (qualité globale)
if len(diagram_H0_gt) > 0 and len(diagram_H0_pred) > 0:
    dist_wasserstein_H0 = wasserstein_distance(
        diagram_H0_gt, diagram_H0_pred, order=1.0, internal_p=2.0
    )
    print(f"Distance de Wasserstein (H0): {1 - (dist_wasserstein_H0 / n)}")
else:
    print("Pas assez de points en H0 pour calculer la distance de Wasserstein.")

exit()

def safe_point_distance(pt1, pt2):
    # Gérer les infinis pour la distance L2 entre points de persistance
    b1, d1 = pt1
    b2, d2 = pt2

    # Si les deux morts sont infinies, la distance est juste la différence des naissances
    if np.isinf(d1) and np.isinf(d2):
        return abs(b1 - b2)
    # Si l'une est infinie et l'autre finie, la distance est "infinie" ou très grande
    # Cela pénalise fortement les appariements entre un point persistant à l'infini
    # et un point qui meurt (ce qui est généralement souhaité).
    elif np.isinf(d1) or np.isinf(d2):
        return np.inf # Ou un très grand nombre comme 1000.0 * np.max(abs(b1), abs(b2))
    # Sinon, les deux sont finis, utiliser la norme L2 standard
    else:
        return np.linalg.norm(pt1 - pt2)

def topological_recall(diag_gt, diag_pred, epsilon=0.01):
    if len(diag_gt) == 0:
        return 0.0
    count_match = 0
    for pt_gt in diag_gt:
        matched = False
        for pt_pred in diag_pred:
            # Utiliser la fonction safe_point_distance
            dist = safe_point_distance(pt_gt, pt_pred)
            if dist <= epsilon:
                matched = True
                break
        if matched:
            count_match += 1
    return count_match / len(diag_gt)

def topological_precision(diag_pred, diag_gt, epsilon=0.01):
    if len(diag_pred) == 0:
        return 0.0
    count_match = 0
    for pt_pred in diag_pred:
        matched = False
        for pt_gt in diag_gt:
            # Utiliser la fonction safe_point_distance
            dist = safe_point_distance(pt_pred, pt_gt) # Note: l'ordre n'importe pas pour symetrique
            if dist <= epsilon:
                matched = True
                break
        if matched:
            count_match += 1
    return count_match / len(diag_pred)

# Extraction des diagrammes H0 (comme avant)
diagram_H0_gt = np.array([pt[1] for pt in diagram_gt if pt[0] == 0])
diagram_H0_pred = np.array([pt[1] for pt in diagram_pred if pt[0] == 0])

# Calcul recall avec epsilon choisi (à ajuster selon ton problème)
epsilon = 0.01
recall_H0 = topological_recall(diagram_H0_gt, diagram_H0_pred, epsilon)

# Calculer la précision
precision_H0 = topological_precision(diagram_H0_pred, diagram_H0_gt, epsilon)
print(f"Précision topologique (H0) avec epsilon={epsilon}: {precision_H0:.4f}")

print(f"Recall topologique (H0) avec epsilon={epsilon}: {recall_H0:.4f}")

import matplotlib.pyplot as plt

def plot_two_diagrams(diag1, diag2, label1="Ground Truth", label2="Prediction", dim=0):
    # Extraire les points de la bonne dimension
    points1 = np.array([pt[1] for pt in diag1 if pt[0] == dim])
    points2 = np.array([pt[1] for pt in diag2 if pt[0] == dim])

    # Affichage
    plt.figure(figsize=(6, 6))
    plt.plot([0, 1], [0, 1], 'k--', label='Diag')  # diagonale
    if len(points1) > 0:
        plt.scatter(points1[:, 0], points1[:, 1], c='blue', marker='o', label=label1)
    if len(points2) > 0:
        plt.scatter(points2[:, 0], points2[:, 1], c='red', marker='x', label=label2)
    plt.xlabel("Naissance")
    plt.ylabel("Mort")
    plt.title(f"Diagramme de Persistance - H{dim}")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

# Afficher pour H0
# plot_two_diagrams(diagram_gt, diagram_pred, dim=0)

# # Afficher pour H1
# plot_two_diagrams(diagram_gt, diagram_pred, dim=1)
D_max_a = np.max(a)
D_max_b = np.max(b)
D_max = max(D_max_a, D_max_b)
N_max = max(a.shape[0], b.shape[0])
borne_max = D_max * N_max
w_normalise = 1 - (dist_wasserstein_H0 / borne_max)
w_normalise = max(0, min(1, w_normalise))  # clipper entre 0 et 1, au cas où

print("wasserstein", w_normalise)




max_finite_val_H0 = 0
if len(diagram_H0_gt) > 0:
    max_finite_val_H0 = max(max_finite_val_H0, np.max(diagram_H0_gt[np.isfinite(diagram_H0_gt)]))
if len(diagram_H0_pred) > 0:
    max_finite_val_H0 = max(max_finite_val_H0, np.max(diagram_H0_pred[np.isfinite(diagram_H0_pred)]))

# Si tout est infini (ce qui est rare pour H0), fixons une valeur par défaut ou utilisons max_edge_length
if max_finite_val_H0 == 0:
    max_finite_val_H0 = 1.0 # Ou la valeur de max_edge_length utilisée pour RipsComplex

n_steps = 100 # Nombre de points sur la courbe
filtration_values = np.linspace(0, max_finite_val_H0 * 1.1, n_steps) # Allez un peu au-delà du max pour voir la fin de la persistance

# --- Fonction pour calculer une courbe de Betti à partir d'un diagramme ---
def compute_betti_curve(diagram, filtration_values):
    betti_curve = []
    for t in filtration_values:
        count = 0
        for birth, death in diagram:
            # Un point est "vivant" si sa naissance est <= t et sa mort est > t
            if birth <= t and death > t:
                count += 1
        betti_curve.append(count)
    return np.array(betti_curve)

# --- Calculer les courbes de Betti pour H0 ---
betti_H0_gt = compute_betti_curve(diagram_H0_gt, filtration_values)
betti_H0_pred = compute_betti_curve(diagram_H0_pred, filtration_values)

# --- Afficher les courbes de Betti H0 ---
plt.figure(figsize=(8, 6))
plt.plot(filtration_values, betti_H0_gt, label="H0 Ground Truth", color='blue')
plt.plot(filtration_values, betti_H0_pred, label="H0 Prediction", color='red', linestyle='--')
plt.xlabel("Valeur de Filtration (epsilon)")
plt.ylabel("Nombre de Composantes Connexes (Betti 0)")
plt.title("Courbes de Betti (H0)")
plt.legend()
plt.grid(True)
plt.show()

# --- Quantifier la distance entre les courbes ---
# Par exemple, distance L2
distance_L2_H0 = np.linalg.norm(betti_H0_gt - betti_H0_pred)
print(f"Distance L2 entre les courbes de Betti H0 : {distance_L2_H0:.4f}")



if len(diagram_H0_gt) > 0 and len(diagram_H0_pred) > 0:
    # Calcul de la distance de Wasserstein H0 non normalisée (vous l'avez déjà)
    dist_wasserstein_H0 = wasserstein_distance(
        diagram_H0_gt, diagram_H0_pred, order=2.0, internal_p=2.0
    )
    print(f"Distance de Wasserstein (H0): {dist_wasserstein_H0:.4f}")

    # 1. Collecter toutes les valeurs de "naissance" finies des points H0
    all_finite_births_H0 = []
    # Parcourir les points de persistance H0 de la Vérité Terrain
    for birth, death in diagram_H0_gt:
        if np.isfinite(birth): # S'assurer que la naissance est finie
            all_finite_births_H0.append(birth)
    # Parcourir les points de persistance H0 des Prédictions
    for birth, death in diagram_H0_pred:
        if np.isfinite(birth): # S'assurer que la naissance est finie
            all_finite_births_H0.append(birth)

    # 2. Trouver la valeur de naissance maximale
    max_birth_value_H0 = 1.0 # Valeur par défaut pour éviter la division par zéro si aucune naissance n'est trouvée
    if all_finite_births_H0: # S'assurer que la liste n'est pas vide
        max_birth_value_H0 = max(all_finite_births_H0)

    # Si max_birth_value_H0 est toujours 0 (toutes les naissances sont 0, ou liste vide),
    # cela signifie qu'il n'y a pas de "gamme" significative de naissances à normaliser.
    # Dans ce cas, la normalisation est soit impossible, soit le résultat est trivialement 0 ou 1.
    if max_birth_value_H0 > 0:
        dist_wasserstein_H0_normalized_by_birth = dist_wasserstein_H0 / max_birth_value_H0
        # Clipper la valeur entre 0 et 1 (optionnel, mais souvent désiré pour l'interprétation)
        dist_wasserstein_H0_normalized_by_birth = max(0, min(1, dist_wasserstein_H0_normalized_by_birth))
        print(f"Distance de Wasserstein normalisée (H0) par max_birth_value: {dist_wasserstein_H0_normalized_by_birth:.4f}")
    else:
        print("Normalisation de Wasserstein (H0) par max_birth_value non significative (toutes naissances à 0 ou pas de points).")
else:
    print("Pas assez de points en H0 pour calculer la distance de Wasserstein et la normalisation.")

# ... (Le reste de votre code pour les fonctions recall/precision, plot_two_diagrams, etc. est correct)

# Votre ancien calcul de normalisation que vous pouvez supprimer ou commenter, car il est ambigu pour H0
# print("wasserstein", w_normalise)

# Assume diagram_H0_gt and diagram_H0_pred are already computed as numpy arrays

# Définir la plage d'epsilon
# On peut aller de 0 à la valeur maximale de la filtration utilisée,
# ou le maximum des coordonnées finies des diagrammes.
# Pour H0, les morts peuvent être inf. On peut prendre le max des naissances ou max_edge_length.
# Prenons le max_edge_length pour une cohérence avec la filtration.
max_filtration_value = 1.0 # Correspond à votre max_edge_length du RipsComplex

# Nombre de points pour l'intégration
n_epsilon_steps = 100
epsilon_values = np.linspace(0.0, max_filtration_value, n_epsilon_steps)

# Listes pour stocker les valeurs de précision et de rappel pour chaque epsilon
precision_curve_H0 = []
recall_curve_H0 = []

# Assurez-vous que safe_point_distance est définie comme précédemment
def safe_point_distance_alternative(pt1, pt2, max_filtration_scale=1.0):
    # Normalisation des coordonnées pour les rendre comparables
    # L'idée est de limiter les coordonnées à max_filtration_scale
    # et de remplacer inf par une grande valeur ou max_filtration_scale
    # C'est une heuristique, pas une solution mathématiquement rigoureuse pour inf.
    b1, d1 = pt1
    b2, d2 = pt2

    d1_mapped = d1 if np.isfinite(d1) else max_filtration_scale * 1.5 # Une valeur un peu au-dessus de la max filtration
    d2_mapped = d2 if np.isfinite(d2) else max_filtration_scale * 1.5

    # Assurez-vous que les naissances sont aussi traitées si elles peuvent être inf (rare pour H0)
    b1_mapped = b1 if np.isfinite(b1) else max_filtration_scale * 1.5
    b2_mapped = b2 if np.isfinite(b2) else max_filtration_scale * 1.5

    return np.linalg.norm(np.array([b1_mapped, d1_mapped]) - np.array([b2_mapped, d2_mapped]))

def topological_recall(diag_gt, diag_pred, epsilon=0.1):
    if len(diag_gt) == 0:
        return 0.0
    count_match = 0
    for pt_gt in diag_gt:
        matched = False
        for pt_pred in diag_pred:
            dist = safe_point_distance(pt_gt, pt_pred) # Use the safe distance
            if dist <= epsilon: # np.inf <= epsilon will be False, which is desired
                matched = True
                break
        if matched:
            count_match += 1
    return count_match / len(diag_gt)

def topological_precision(diag_pred, diag_gt, epsilon=0.1):
    if len(diag_pred) == 0:
        return 0.0
    count_match = 0
    for pt_pred in diag_pred:
        matched = False
        for pt_gt in diag_gt:
            dist = safe_point_distance(pt_pred, pt_gt) # Use the safe distance
            if dist <= epsilon: # np.inf <= epsilon will be False, which is desired
                matched = True
                break
        if matched:
            count_match += 1
    return count_match / len(diag_pred)


for eps in epsilon_values:
    # Rappel: Nous utilisons diagram_H0_gt et diagram_H0_pred qui sont des NumPy arrays.
    # Assurez-vous que ces arrays contiennent les paires (naissance, mort).
    # Exemple de construction:
    # diagram_H0_gt = np.array([pt[1] for pt in diagram_gt if pt[0] == 0])

    recall_curve_H0.append(topological_recall(diagram_H0_gt, diagram_H0_pred, eps))
    precision_curve_H0.append(topological_precision(diagram_H0_pred, diagram_H0_gt, eps))

precision_curve_H0 = np.array(precision_curve_H0)
recall_curve_H0 = np.array(recall_curve_H0)

# Aire sous la courbe de Précision
auc_precision_H0 = np.trapezoid(precision_curve_H0, epsilon_values)
print(f"\nAire sous la courbe de Précision (H0): {auc_precision_H0:.4f}")

# Aire sous la courbe de Rappel
auc_recall_H0 = np.trapezoid(recall_curve_H0, epsilon_values)
print(f"Aire sous la courbe de Rappel (H0): {auc_recall_H0:.4f}")

plt.figure(figsize=(10, 6))
plt.plot(epsilon_values, precision_curve_H0, label="Précision H0", color='green')
plt.plot(epsilon_values, recall_curve_H0, label="Rappel H0", color='purple', linestyle='--')
plt.xlabel("Seuil de Proximité (epsilon)")
plt.ylabel("Score")
plt.title("Précision et Rappel Topologiques (H0) en fonction d'epsilon")
plt.legend()
plt.grid(True)
plt.show()



# Convertir les courbes de Betti en format compatible avec tslearn (si ce n'est pas déjà fait)
# Souvent, tslearn attend des arrays 2D (n_samples, n_timestamps) ou (n_timestamps, n_features)
# Pour une seule courbe, assure-toi qu'elle est bien 1D ou 2D avec 1 feature.
curve_gt = betti_H0_gt.reshape(-1, 1) # Assure-toi que c'est une colonne de données
curve_pred = betti_H0_pred.reshape(-1, 1)

# Calcul de la distance DTW
distance_dtw_H0 = dtw(curve_gt, curve_pred)
print(f"\nDistance DTW entre les courbes de Betti H0 : {distance_dtw_H0:.4f}")

# --- Normalisation de la distance DTW ---
# La normalisation de la DTW est un peu plus délicate car elle n'a pas de borne supérieure fixe
# ou intuitive comme la L2. Voici quelques approches possibles :

# 1. Normalisation par la longueur de l'alignement (path length)
# C'est une normalisation "interne" à la DTW. La DTW donne souvent une distance cumulée.
# Pour une normalisation simple entre 0 et 1, on peut utiliser des heuristiques.

# 2. Normalisation par la somme des normes des deux courbes (similaire à ta L2 normalisée par GT)
# Cette méthode n'est pas garantie de donner un résultat entre 0 et 1 sans clipping.
norm_gt = np.linalg.norm(curve_gt) # Ou np.sum(curve_gt)
norm_pred = np.linalg.norm(curve_pred) # Ou np.sum(curve_pred)

if norm_gt + norm_pred > 0:
    # Une forme simple de normalisation. L'idée est que plus les courbes sont grandes,
    # plus la DTW pourrait être grande.
    normalized_dtw_sum_norm = distance_dtw_H0 / (norm_gt + norm_pred)
    # Il faudra probablement cliper le résultat entre 0 et 1 si ce n'est pas le cas
    normalized_dtw_sum_norm = max(0, min(1, normalized_dtw_sum_norm))
    print(f"Distance DTW normalisée (somme normes) : {normalized_dtw_sum_norm:.4f}")
else:
    print("Normalisation DTW par somme des normes non significative.")

# 3. Normalisation par la DTW maximale théorique (similaire à L2 max théorique)
# C'est la plus complexe car elle dépend de la fonction de coût.
# Une borne supérieure "brute" pourrait être la distance entre une courbe et une courbe nulle (si pertinente)
# ou une courbe maximale, multipliée par la longueur de la séquence.
# Par exemple, si la valeur max d'un point est N_points, et la min est 1.
# La DTW entre une courbe de N_points et une courbe de 1 pourrait être très grande.
# Pour être praticable, il faudrait faire des simulations ou avoir une connaissance a priori.
# Sans une borne supérieure claire et universelle, la normalisation DTW est souvent contextuelle.

# 4. Utilisation du chemin d'alignement pour une interprétation visuelle
# La fonction dtw de tslearn peut aussi retourner le chemin d'alignement.
# Si tu veux une visualisation plus avancée, tu peux l'explorer.
# from tslearn.metrics import dtw_path
# path, dist = dtw_path(curve_gt, curve_pred)
# print(f"DTW path length: {len(path)}")
