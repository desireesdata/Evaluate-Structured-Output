import random

def bruiter_texte(texte, probabilite_modification=0.03):
    """
    Bruite le texte en ajoutant, supprimant ou modifiant des caractères aléatoirement.

    :param texte: Le texte à bruiter.
    :param probabilite_modification: Probabilité de modification pour chaque caractère.
    :return: Le texte bruité.
    """
    lettres = list(texte)
    i = 0
    while i < len(lettres):
        if random.random() < probabilite_modification:
            operation = random.choice(['ajouter', 'supprimer', 'modifier'])
            if operation == 'ajouter':
                # Ajouter une lettre 
                lettres.insert(i, random.choice('abcdefghijklmnopqrstuvwxyz'))
                i += 1  # Sauter le nouvel élément ajouté
            elif operation == 'supprimer':
                # Supprimer la lettre actuelle
                lettres.pop(i)
                # Ne pas incrémenter i car nous devons vérifier le nouvel élément à cet index
                continue
            elif operation == 'modifier':
                # Modifier la lettre actuelle
                lettres[i] = random.choice('abcdefghijklmnopqrstuvwxyz')
        i += 1

    return ''.join(lettres)

def bruiter_fichier(chemin_entree, chemin_sortie):
    """
    Lit un fichier texte, bruite son contenu et écrit le résultat dans un nouveau fichier.

    :param chemin_entree: Chemin du fichier d'entrée.
    :param chemin_sortie: Chemin du fichier de sortie.
    """
    with open(chemin_entree, 'r', encoding='utf-8') as fichier:
        contenu = fichier.read()

    contenu_bruite = bruiter_texte(contenu)

    with open(chemin_sortie, 'w', encoding='utf-8') as fichier:
        fichier.write(contenu_bruite)

chemin_entree = '01_vt.txt'
chemin_sortie = '04_noisy.txt'
bruiter_fichier(chemin_entree, chemin_sortie)
