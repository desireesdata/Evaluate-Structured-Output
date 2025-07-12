import gudhi
import numpy as np

a = np.load('cost_matrices_output/gt.npy')
b = np.load('cost_matrices_output/predicted.npy')

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
