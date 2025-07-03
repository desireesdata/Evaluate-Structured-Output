import json
import os

def trier_references_pages_non_destructif(chemin_fichier_original, chemin_fichier_sortie):
    """
    Trie les références de pages de chaque intervenant par ordre croissant,
    sans supprimer les doublons et sans modifier l'ordre des intervenants.
    Les données triées sont sauvegardées dans un nouveau fichier, laissant l'original intact.

    Args:
        chemin_fichier_original (str): Le chemin vers le fichier JSON source.
        chemin_fichier_sortie (str): Le chemin où sauvegarder le nouveau fichier JSON trié.
    """
    try:
        # Vérifie si le fichier original existe
        if not os.path.exists(chemin_fichier_original):
            print(f"Erreur : Le fichier original '{chemin_fichier_original}' est introuvable. Veuillez vérifier le chemin.")
            return

        # 1. Lire le fichier JSON original
        with open(chemin_fichier_original, 'r', encoding='utf-8') as f_in:
            data = json.load(f_in)

        # 2. Parcourir la structure JSON et trier les listes de références
        if "listes_des_intervenants" in data and isinstance(data["listes_des_intervenants"], list):
            for intervenant in data["listes_des_intervenants"]:
                if "references_pages" in intervenant and isinstance(intervenant["references_pages"], list):
                    # Tri la liste des références de pages en place (pour cette copie des données)
                    # Les doublons sont conservés, seul l'ordre est modifié.
                    intervenant["references_pages"].sort()
                else:
                    print(f"Attention : La clé 'references_pages' est manquante ou n'est pas une liste pour l'intervenant '{intervenant.get('nom', 'Inconnu')}'. Elle n'a pas pu être triée.")
        else:
            print("Erreur : La clé 'listes_des_intervenants' est manquante ou n'est pas une liste valide dans le JSON. Aucun tri effectué.")

        # 3. Sauvegarder les données modifiées dans un nouveau fichier
        with open(chemin_fichier_sortie, 'w', encoding='utf-8') as f_out:
            json.dump(data, f_out, indent=2, ensure_ascii=False)
        
        print(f"Les références de pages ont été triées et sauvegardées avec succès dans : {chemin_fichier_sortie}")
        print(f"Votre fichier original '{chemin_fichier_original}' n'a PAS été modifié.")

    except json.JSONDecodeError:
        print(f"Erreur : Le fichier '{chemin_fichier_original}' n'est pas un JSON valide. Impossible de le traiter.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")


# --- Utilisation du script ---
if __name__ == "__main__":
    # Définissez le chemin de votre fichier JSON original ici
    fichier_json_source = "page_10_low_vt.json" 
    
    # Définissez le nom du nouveau fichier où le résultat sera sauvegardé
    fichier_json_tri_securise = "page_05_low_vt_sorted.json" 

    # Appelle la fonction pour trier et sauvegarder
    trier_references_pages_non_destructif(fichier_json_source, fichier_json_tri_securise)

    # Pour vérifier le résultat (optionnel, mais recommandé)
    # Lisez le fichier de sortie pour s'assurer que tout est correct
    try:
        with open(fichier_json_tri_securise, 'r', encoding='utf-8') as f:
            resultat_verifie = json.load(f)
            print(f"\nVoici un aperçu du contenu du nouveau fichier '{fichier_json_tri_securise}' :")
            # N'affichons qu'une partie pour ne pas surcharger la console
            # Par exemple, les 2 premières entrées, ou un extrait significatif.
            if "listes_des_intervenants" in resultat_verifie and len(resultat_verifie["listes_des_intervenants"]) > 0:
                print(json.dumps(resultat_verifie["listes_des_intervenants"][0:2], indent=2, ensure_ascii=False))
                if len(resultat_verifie["listes_des_intervenants"]) > 2:
                    print("...")
            else:
                print("La structure attendue n'est pas présente ou la liste est vide dans le fichier de sortie.")
    except FileNotFoundError:
        print(f"Le fichier de sortie '{fichier_json_tri_securise}' n'a pas été trouvé après l'opération.")
    except json.JSONDecodeError:
        print(f"Erreur lors de la lecture du fichier de sortie '{fichier_json_tri_securise}'. Il pourrait être corrompu ou mal formaté.")