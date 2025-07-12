import numpy as np
import plotly.graph_objects as go
import argparse
import os
import json
import sys
from typing import List, Dict, Union

# Add the parent directory to the Python path to import Entry
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entry import Entry

# Re-implement load_json_data from main.py/generate_cost_matrices.py
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
        if "nom" in item and "references_pages" in item:
            normalized_entries.append(Entry(item))
        elif "nom_de_famille" in item and "actions_relatives_a_l_intervenant" in item:
            nom = item.get("nom_de_famille", "")
            prenom = item.get("prenom", "")
            full_name = f"{nom} ({prenom})" if prenom else nom

            actions = item.get("actions_relatives_a_l_intervenant", [])
            if isinstance(actions, str):
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

def plot_cost_matrix(matrix: np.ndarray, title: str, output_path: str, 
                     x_labels: List[str] = None, y_labels: List[str] = None):
    fig = go.Figure(data=go.Heatmap(z=matrix, colorscale='Viridis'))
    
    fig.update_layout(
        title=title,
        xaxis_title="Entry",
        yaxis_title="Entry",
        yaxis=dict(autorange='reversed'), # Invert y-axis for matrix-like display
        xaxis=dict(tickmode='array', tickvals=list(range(len(x_labels))) if x_labels else [], ticktext=x_labels if x_labels else []),
        yaxis_tickmode='array', yaxis_tickvals=list(range(len(y_labels))) if y_labels else [], yaxis_ticktext=y_labels if y_labels else []
    )
    fig.write_image(output_path)
    print(f"Visualization saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Visualize cost matrices.')
    parser.add_argument('-g', '--gt-matrix', required=True,
                        help='Path to the GT vs GT cost matrix (.npy file).')
    parser.add_argument('-p', '--predicted-matrix', required=True,
                        help='Path to the Predicted vs Predicted cost matrix (.npy file).')
    parser.add_argument('-gt_json', '--gt-json-file', required=True,
                        help='Path to the original Ground Truth JSON file.')
    parser.add_argument('-pred_json', '--predicted-json-file', required=True,
                        help='Path to the original Predicted JSON file.')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='Output directory for the visualizations.')

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Load matrices
    gt_matrix = np.load(args.gt_matrix)
    predicted_matrix = np.load(args.predicted_matrix)

    # Load original JSON data to get labels
    gt_entries = load_json_data(args.gt_json_file)
    predicted_entries = load_json_data(args.predicted_json_file)

    gt_labels = [entry.normalize_field("nom") for entry in gt_entries]
    predicted_labels = [entry.normalize_field("nom") for entry in predicted_entries]

    # Plot GT vs GT matrix
    gt_output_path = os.path.join(args.output_dir, "gt_gt_cost_matrix_heatmap.png")
    plot_cost_matrix(gt_matrix, "Ground Truth vs Ground Truth Cost Matrix", gt_output_path, 
                     x_labels=gt_labels, y_labels=gt_labels)

    # Plot Predicted vs Predicted matrix
    predicted_output_path = os.path.join(args.output_dir, "predicted_predicted_cost_matrix_heatmap.png")
    plot_cost_matrix(predicted_matrix, "Predicted vs Predicted Cost Matrix", predicted_output_path, 
                     x_labels=predicted_labels, y_labels=predicted_labels)

    print("Visualization complete.")

if __name__ == "__main__":
    main()
