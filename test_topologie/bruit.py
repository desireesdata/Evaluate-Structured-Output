import numpy as np

# Paramètres
nombre_intervenants = 10  # nombre "d'entités"
nombre_pages = 15         # nombre de références pages par intervenant (fictif)
taille_matrice = nombre_intervenants * nombre_pages

# Générer une matrice de similarité bruitée
# Ici on simule une matrice carrée taille_matrice x taille_matrice
# avec des valeurs aléatoires entre 0 et 1
matrice_bruit = np.random.rand(taille_matrice, taille_matrice)

# On force la matrice à être symétrique (comme une matrice de distances/similitudes)
matrice_bruit = (matrice_bruit + matrice_bruit.T) / 2

# On met des 0 sur la diagonale (distance ou dissimilarité parfaite avec soi-même)
np.fill_diagonal(matrice_bruit, 0)

# Sauvegarder la matrice dans un fichier .npy
np.save('cost_matrices_output/noisy.npy', matrice_bruit)

print(f"Matric de bruit générée et sauvegardée dans 'cost_matrices_output/noisy.npy' avec taille {matrice_bruit.shape}")
