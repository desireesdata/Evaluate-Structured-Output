import json
import argparse
import csv
import sys
import os
import glob
from typing import Dict, List, Tuple
from entry import Entry
from matcher import Matcher

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
        # FORMAT 1 : plat
        if "nom" in item and "references_pages" in item:
            normalized_entries.append(Entry(item))

        # FORMAT 2 : structuré avec actions
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

        # FORMAT 3 : renvoi uniquement
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

def process_single_comparison(truth_file: str, predicted_file: str, output_dir: str, 
                            distance_method: str, base_name: str) -> Tuple[Dict[str, float], str, str]:
    """Traite une comparaison unique entre deux fichiers"""
    truth_entries = load_json_data(truth_file)
    predicted_entries = load_json_data(predicted_file)
    
    matcher = Matcher(truth_entries, predicted_entries, distance_method)
    
    stats_file = os.path.join(output_dir, f'{base_name}_stats.txt')
    matches_file = os.path.join(output_dir, f'{base_name}_matches.csv')
    
    stats = matcher.compute_all_statistics()
    write_stats_file(stats_file, stats, truth_file, predicted_file, distance_method, 
                     truth_entries, predicted_entries, len(matcher.matches))
    
    matcher.export_matches_to_csv(truth_entries, predicted_entries, matches_file)
    
    return stats, stats_file, matches_file

def main():
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        truth_file, predicted_files = validate_and_resolve_files(args.input[0], args.input[1])
        output_path = args.output
        create_folder = should_create_folder(output_path)
        
        if create_folder and len(predicted_files) > 1:
            process_batch_mode(truth_file, predicted_files, output_path, args.distance)
        elif create_folder:
            process_folder_mode(truth_file, predicted_files[0], output_path, args.distance)
        else:
            process_single_file_mode(truth_file, predicted_files[0], args.output, args.distance, args.matches)
                
    except FileNotFoundError as e:
        print(f"Erreur: Fichier non trouvé - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

def setup_argument_parser() -> argparse.ArgumentParser:
    """Configure et retourne le parser d'arguments"""
    parser = argparse.ArgumentParser(description='ESO - Evaluation de Sorties structurées')
    parser.add_argument('-i', '--input', nargs=2, required=True, 
                       help='Fichiers d\'entrée: vérité terrain et prédictions (pattern glob accepté pour le 2e)', 
                       metavar=('TRUTH', 'PREDICTED'))
    parser.add_argument('-o', '--output', required=True, 
                       help='Dossier de sortie ou fichier de sortie')
    parser.add_argument('-d', '--distance', choices=['levenshtein', 'ratcliff'], 
                       default='ratcliff', help='Méthode de calcul de distance')
    parser.add_argument('-m', '--matches', action='store_true', 
                       help='Exporter les appariements en CSV')
    return parser

def validate_and_resolve_files(truth_file: str, predicted_pattern: str) -> Tuple[str, List[str]]:
    """Valide et résout les fichiers d'entrée"""
    if not os.path.exists(truth_file):
        raise FileNotFoundError(f"Fichier de vérité terrain non trouvé: {truth_file}")
    
    predicted_files = glob.glob(predicted_pattern)
    if not predicted_files:
        predicted_files = [predicted_pattern]
    
    return truth_file, predicted_files

def should_create_folder(output_path: str) -> bool:
    """Détermine si on doit créer un dossier ou traiter comme un fichier unique"""
    basename = os.path.basename(output_path)
    has_extension = '.' in basename and len(basename.split('.')[-1]) <= 4
    return not has_extension

def write_stats_file(stats_file: str, stats: Dict[str, float], truth_file: str, predicted_file: str, 
                     distance_method: str, truth_entries: List[Entry], predicted_entries: List[Entry], 
                     num_matches: int) -> None:
    """Écrit les statistiques dans un fichier"""
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"Statistiques d'appariement (Distance: {distance_method})\n")
        f.write(f"Truth: {truth_file}\n")
        f.write(f"Predicted: {predicted_file}\n")
        f.write("=" * 50 + "\n\n")
        
        for key, value in stats.items():
            f.write(f"{key}: {value:.4f}\n")
        
        f.write(f"\nNombre d'entrées vérité terrain: {len(truth_entries)}\n")
        f.write(f"Nombre d'entrées prédites: {len(predicted_entries)}\n")
        f.write(f"Nombre d'appariements: {num_matches}\n")

def process_batch_mode(truth_file: str, predicted_files: List[str], output_path: str, distance_method: str) -> None:
    """Traite plusieurs fichiers en mode batch"""
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Traitement en lot de {len(predicted_files)} fichiers de prédiction...")
    print(f"Résultats dans le dossier: {output_path}")
    print("=" * 50)
    
    for predicted_file in sorted(predicted_files):
        if not os.path.exists(predicted_file):
            print(f"Attention: Fichier ignoré (inexistant): {predicted_file}")
            continue
        
        base_name = os.path.splitext(os.path.basename(predicted_file))[0]
        
        try:
            stats, stats_file, matches_file = process_single_comparison(
                truth_file, predicted_file, output_path, distance_method, base_name
            )
            
            print(f"\n{base_name}:")
            print(f"  Stats: {os.path.basename(stats_file)}")
            print(f"  Matches: {os.path.basename(matches_file)}")
            for key, value in stats.items():
                print(f"  {key}: {value:.4f}")
                
        except Exception as e:
            print(f"Erreur lors du traitement de {predicted_file}: {e}")
            continue

def process_folder_mode(truth_file: str, predicted_file: str, output_path: str, distance_method: str) -> None:
    """Traite un fichier unique en mode dossier"""
    base_name = os.path.splitext(os.path.basename(predicted_file))[0]
    
    os.makedirs(output_path, exist_ok=True)
    stats, stats_file, matches_file = process_single_comparison(
        truth_file, predicted_file, output_path, distance_method, base_name
    )
    
    print(f"Résultats générés dans le dossier: {output_path}")
    print(f"- Statistiques: {stats_file}")
    print(f"- Appariements: {matches_file}")
    
    for key, value in stats.items():
        print(f"{key}: {value:.4f}")

def process_single_file_mode(truth_file: str, predicted_file: str, output_file: str, 
                           distance_method: str, export_matches: bool) -> None:
    """Traite un fichier unique en mode fichier"""
    truth_entries = load_json_data(truth_file)
    predicted_entries = load_json_data(predicted_file)
    
    matcher = Matcher(truth_entries, predicted_entries, distance_method)
    
    if export_matches or output_file.endswith('.csv'):
        matcher.export_matches_to_csv(truth_entries, predicted_entries, output_file)
        print(f"Appariements exportés vers {output_file}")
    else:
        stats = matcher.compute_all_statistics()
        write_stats_file(output_file, stats, truth_file, predicted_file, distance_method,
                        truth_entries, predicted_entries, len(matcher.matches))
        
        print(f"Statistiques sauvegardées dans {output_file}")
        
        for key, value in stats.items():
            print(f"{key}: {value:.4f}")

if __name__ == "__main__":
    main()


