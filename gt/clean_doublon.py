import json

def supprimer_doublons_references(chemin_fichier_json):
    """
    Supprime les références de pages en double pour chaque intervenant dans un fichier JSON.

    Args:
        chemin_fichier_json (str): Le chemin vers le fichier JSON à traiter.
    """
    try:
        with open(chemin_fichier_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "listes_des_intervenants" in data and isinstance(data["listes_des_intervenants"], list):
            for intervenant in data["listes_des_intervenants"]:
                if "references_pages" in intervenant and isinstance(intervenant["references_pages"], list):
                    # Convertit la liste en set pour supprimer les doublons, puis la reconvertit en liste et la trie
                    intervenant["references_pages"] = sorted(list(set(intervenant["references_pages"])))
                else:
                    print(f"Attention : 'references_pages' manquant ou n'est pas une liste pour l'intervenant '{intervenant.get('nom', 'Inconnu')}'.")
        else:
            print("Erreur : La clé 'listes_des_intervenants' est manquante ou n'est pas une liste dans le JSON.")

        with open(chemin_fichier_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Les doublons ont été supprimés avec succès dans le fichier : {chemin_fichier_json}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{chemin_fichier_json}' est introuvable.")
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier '{chemin_fichier_json}' n'est pas un JSON valide.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

# --- Utilisation du script ---
if __name__ == "__main__":
    # Crée un fichier JSON de test avec votre structure
    test_data = {
      "listes_des_intervenants": [
        {
          "nom": "Dentu",
          "references_pages": [
            1024,
            1560,
            1031,
            1560,
            1563,
            1564,
            1564
          ]
        },
        {
          "nom": "Desjardins (Charles)",
          "references_pages": [
            563
          ]
        },
        {
          "nom": "Dupont",
          "references_pages": [
            10,
            20,
            10,
            30
          ]
        },
        {
          "nom": "Durand",
          "references_pages": []
        },
        {
          "nom": "Martin",
          "references_pages": [700, 600, 700]
        }
      ]
    }

    test_file_name = "intervenants.json"
    with open(test_file_name, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"Fichier de test '{test_file_name}' créé.")

    # Appelle la fonction pour supprimer les doublons
    supprimer_doublons_references(test_file_name)

    # Pour vérifier le résultat, vous pouvez lire le fichier après l'exécution
    with open(test_file_name, 'r', encoding='utf-8') as f:
        resultat = json.load(f)
        print("\nContenu du fichier après suppression des doublons :")
        print(json.dumps(resultat, indent=2, ensure_ascii=False))