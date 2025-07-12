import argparse
import os
import json
import numpy as np
from typing import List, Dict, Union

# Assuming Entry and Matcher are in the same directory or accessible via PYTHONPATH
from entry import Entry
from matcher import Matcher

# Re-implement load_json_data or import it if possible without circular dependencies
# For simplicity, I'll re-implement a minimal version here, assuming the structure
# is always a list of entries or a dict with "listes_des_intervenants"
def load_json_data(file_path: str) -> List[Entry]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and "listes_des_intervenants" in data:
        entries_data = data["listes_des_intervenants"]
    elif isinstance(data, list):
        entries_data = data
    else:
        raise ValueError(f"Format de fichier non reconnu dans {file_path}")

    normalized_entries = []
    for item in entries_data:
        # This part needs to match the logic in main.py's load_json_data
        # For now, assuming the simplest format for Entry creation
        if "nom" in item and "references_pages" in item:
            normalized_entries.append(Entry(item))
        elif "nom_de_famille" in item and "actions_relatives_a_l_intervenant" in item:
            nom = item.get("nom_de_famille", "")
            prenom = item.get("prenom", "")
            full_name = f"{nom} ({prenom})" if prenom else nom

            actions = item.get("actions_relatives_a_l_intervenant", [])
            if isinstance(actions, str):  # Exemple : "<renvoi d'index>"
                references = actions
            else:
                pages = []
                for action_wrapper in actions:
                    try:
                        action = action_wrapper["action"]
                        pages += action.get("references_page", [])
                    except (KeyError, TypeError):
                        continue
                references = sorted(set(pages))

            normalized_entries.append(Entry({
                "nom": full_name,
                "references_pages": references
            }))
        elif "nom_entree_du_renvoi" in item and "nom_de_famille" in item:
            nom = item.get("nom_de_famille", "")
            prenom = item.get("prenom", "")
            full_name = f"{nom} ({prenom})" if prenom else nom

            normalized_entries.append(Entry({
                "nom": full_name,
                "references_pages": "<renvoi d'index>"
            }))
        else:
            raise ValueError(f"Entrée au format non reconnu : {item}")

    return normalized_entries

def main():
    parser = argparse.ArgumentParser(description='Generate symmetric cost matrices.')
    parser.add_argument('-g', '--gt-file', required=True,
                        help='Path to the Ground Truth JSON file.')
    parser.add_argument('-p', '--predictions-file', required=True,
                        help='Path to the Predicted JSON file.')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='Output directory for the .npy matrices.')
    parser.add_argument('-d', '--distance', choices=['levenshtein', 'ratcliff'],
                        default='ratcliff', help='Distance calculation method.')

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading Ground Truth data from: {args.gt_file}")
    gt_entries = load_json_data(args.gt_file)
    print(f"Loaded {len(gt_entries)} GT entries.")

    print(f"Loading Predicted data from: {args.predictions_file}")
    predicted_entries = load_json_data(args.predictions_file)
    print(f"Loaded {len(predicted_entries)} Predicted entries.")

    # Generate GT vs GT cost matrix
    print("Generating Ground Truth vs Ground Truth cost matrix...")
    gt_matcher = Matcher(gt_entries, gt_entries, args.distance)
    gt_cost_matrix = gt_matcher.cost_matrix
    gt_output_path = os.path.join(args.output_dir, "gt_gt_cost_matrix.npy")
    np.save(gt_output_path, gt_cost_matrix)
    print(f"Saved GT vs GT cost matrix to: {gt_output_path}")

    # Generate Predicted vs Predicted cost matrix
    print("Generating Predicted vs Predicted cost matrix...")
    predicted_matcher = Matcher(predicted_entries, predicted_entries, args.distance)
    predicted_cost_matrix = predicted_matcher.cost_matrix
    predicted_output_path = os.path.join(args.output_dir, "predicted_predicted_cost_matrix.npy")
    np.save(predicted_output_path, predicted_cost_matrix)
    print(f"Saved Predicted vs Predicted cost matrix to: {predicted_output_path}")

    print("Cost matrix generation complete.")

if __name__ == "__main__":
    main()
