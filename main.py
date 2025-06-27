import json
import argparse
import csv
import sys
import os
import glob
from typing import Dict, List, Union, Literal, Tuple
from difflib import SequenceMatcher
import numpy as np
from scipy.optimize import linear_sum_assignment
import jellyfish

FieldName = Literal["nom", "references_pages"]
RawEntry = Dict[FieldName, Union[str, List[int]]]

class Entry:
    def __init__(self, data: RawEntry):
        """Initialization with data from json (object)"""
        self.data = data

    def get(self) -> RawEntry:
        """Return the entire object"""
        return self.data

    def normalize_field(self, field: FieldName) -> str:
        "Simple normalization"
        val = self.data.get(field, "")

        if field == "nom":
            return str(val).strip().lower()

        elif field == "references_pages":
            if isinstance(val, list):
                return ''.join(str(page) for page in val)
            elif isinstance(val, str):
                return ''.join(filter(str.isdigit, val))
            else:
                return ""

        return str(val)

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
    
    @staticmethod
    def normalized_levenshtein(s1: str, s2: str) -> float:
        if not s1 and not s2:
            return 0.0
        return jellyfish.levenshtein_distance(s1, s2) / max(len(s1), len(s2))
    
    def distance_to_levenshtein(self, other: 'Entry') -> float:
        """Return distance with an another entry"""
        """NB : based on Levenshtein distance (normalized)"""
        total = 0.0
        count = 0
        for field in ["nom", "references_pages"]:
            norm_self = self.normalize_field(field)
            norm_other = other.normalize_field(field)

            if norm_self or norm_other:
                dist = self.normalized_levenshtein(norm_self, norm_other)
                total += dist
                count += 1
        return total / count if count else 1.0
    
class Matcher:
    def __init__(self, entries_a: List[Entry], entries_b: List[Entry], distance_method: str = "ratcliff"):
        """A Matcher is comparator; he compares two sets of entry and produces a matrix"""
        self.entries_a = entries_a
        self.entries_b = entries_b
        self.distance_method = distance_method
        self.cost_matrix = self.compute_cost_matrix(distance_method)
        self.matches = self.match()

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

    def match(self) -> List[Tuple[int, int]]:
        """A faire : paramètre pour choisir la méthode d'assignement"""
        row_ind, col_ind = linear_sum_assignment(self.cost_matrix)
        return list(zip(row_ind, col_ind))

    def compute_precision_recall_f1(self) -> Dict[str, float]:
        tp = len(self.matches)
        fp = len(self.entries_b) - tp
        fn = len(self.entries_a) - tp

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        return {"Precision": precision, "Recall": recall, "F1": f1}

    def compute_average_matching_quality(self) -> float:
        if not self.matches:
            return 0.0
        total_quality = sum(1. - self.cost_matrix[i, j] for i, j in self.matches)
        return total_quality / len(self.matches)

    def compute_overall_matching_quality(self) -> float:
        metrics = self.compute_precision_recall_f1()
        avg_quality = self.compute_average_matching_quality()

        precision = metrics["Precision"]
        recall = metrics["Recall"]

        denom = (precision * recall + precision * avg_quality + recall * avg_quality)
        if denom == 0:
            return 0.0
        return 3 * (precision * recall * avg_quality) / denom

    def compute_all_statistics(self) -> Dict[str, float]:
        metrics = self.compute_precision_recall_f1()
        avg_quality = self.compute_average_matching_quality()
        overall_quality = self.compute_overall_matching_quality()

        return {
            **metrics,
            "Average Matching Quality": avg_quality,
            "Overall Matching Quality": overall_quality
        }

    def export_matches_to_csv(self, truth_entries: List[Entry], predicted_entries: List[Entry], output_file: str):
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            writer.writerow(['Truth_Index', 'Predicted_Index', 'Truth_Nom', 'Predicted_Nom', 
                           'Truth_Pages', 'Predicted_Pages', 'Distance', 'Quality'])
            
            for i, j in self.matches:
                t = truth_entries[i].get()
                p = predicted_entries[j].get()
                distance = self.cost_matrix[i, j]
                quality = 1.0 - distance
                
                writer.writerow([i, j, t.get('nom', ''), p.get('nom', ''), 
                               t.get('references_pages', ''), p.get('references_pages', ''), 
                               f"{distance:.4f}", f"{quality:.4f}"])

def load_json_data(file_path: str) -> List[Entry]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "listes_des_intervenants" in data:
        entries_data = data["listes_des_intervenants"]
    elif isinstance(data, list):
        entries_data = data
    else:
        raise ValueError(f"Format de fichier non reconnu dans {file_path}")
    
    return [Entry(e) for e in entries_data]

def process_single_comparison(truth_file, predicted_file, output_dir, distance_method, base_name):
    """Traite une comparaison unique entre deux fichiers"""
    truth_entries = load_json_data(truth_file)
    predicted_entries = load_json_data(predicted_file)
    
    matcher = Matcher(truth_entries, predicted_entries, distance_method)
    
    # Générer les fichiers stats et appariements avec le nom de base
    stats_file = os.path.join(output_dir, f'{base_name}_stats.txt')
    matches_file = os.path.join(output_dir, f'{base_name}_matches.csv')
    
    # Générer les statistiques
    stats = matcher.compute_all_statistics()
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write(f"Statistiques d'appariement (Distance: {distance_method})\n")
        f.write(f"Truth: {truth_file}\n")
        f.write(f"Predicted: {predicted_file}\n")
        f.write("=" * 50 + "\n\n")
        
        for key, value in stats.items():
            f.write(f"{key}: {value:.4f}\n")
        
        f.write(f"\nNombre d'entrées vérité terrain: {len(truth_entries)}\n")
        f.write(f"Nombre d'entrées prédites: {len(predicted_entries)}\n")
        f.write(f"Nombre d'appariements: {len(matcher.matches)}\n")
    
    # Générer les appariements
    matcher.export_matches_to_csv(truth_entries, predicted_entries, matches_file)
    
    return stats, stats_file, matches_file

def main():
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
    
    args = parser.parse_args()
    
    try:
        truth_file = args.input[0]
        predicted_pattern = args.input[1]
        
        # Vérifier si le fichier de vérité terrain existe
        if not os.path.exists(truth_file):
            raise FileNotFoundError(f"Fichier de vérité terrain non trouvé: {truth_file}")
        
        # Résoudre le pattern glob pour les fichiers de prédiction
        predicted_files = glob.glob(predicted_pattern)
        if not predicted_files:
            # Si pas de correspondance glob, traiter comme un fichier simple
            predicted_files = [predicted_pattern]
        
        # Déterminer si on crée un dossier ou un fichier unique
        output_path = args.output
        create_folder = not ('.' in os.path.basename(output_path) and len(os.path.basename(output_path).split('.')[-1]) <= 4)
        
        if create_folder and len(predicted_files) > 1:
            # Mode batch avec plusieurs fichiers
            os.makedirs(output_path, exist_ok=True)
            
            print(f"Traitement en lot de {len(predicted_files)} fichiers de prédiction...")
            print(f"Résultats dans le dossier: {output_path}")
            print("=" * 50)
            
            for predicted_file in sorted(predicted_files):
                if not os.path.exists(predicted_file):
                    print(f"Attention: Fichier ignoré (inexistant): {predicted_file}")
                    continue
                
                # Extraire le nom de base du fichier de prédiction
                base_name = os.path.splitext(os.path.basename(predicted_file))[0]
                
                try:
                    stats, stats_file, matches_file = process_single_comparison(
                        truth_file, predicted_file, output_path, args.distance, base_name
                    )
                    
                    print(f"\n{base_name}:")
                    print(f"  Stats: {os.path.basename(stats_file)}")
                    print(f"  Matches: {os.path.basename(matches_file)}")
                    for key, value in stats.items():
                        print(f"  {key}: {value:.4f}")
                        
                except Exception as e:
                    print(f"Erreur lors du traitement de {predicted_file}: {e}")
                    continue
                    
        elif create_folder:
            # Mode dossier avec un seul fichier
            predicted_file = predicted_files[0]
            base_name = os.path.splitext(os.path.basename(predicted_file))[0]
            
            os.makedirs(output_path, exist_ok=True)
            stats, stats_file, matches_file = process_single_comparison(
                truth_file, predicted_file, output_path, args.distance, base_name
            )
            
            print(f"Résultats générés dans le dossier: {output_path}")
            print(f"- Statistiques: {stats_file}")
            print(f"- Appariements: {matches_file}")
            
            for key, value in stats.items():
                print(f"{key}: {value:.4f}")
                
        else:
            # Mode original avec fichier unique
            predicted_file = predicted_files[0]
            truth_entries = load_json_data(truth_file)
            predicted_entries = load_json_data(predicted_file)
            
            matcher = Matcher(truth_entries, predicted_entries, args.distance)
            
            if args.matches or args.output.endswith('.csv'):
                matcher.export_matches_to_csv(truth_entries, predicted_entries, args.output)
                print(f"Appariements exportés vers {args.output}")
            else:
                stats = matcher.compute_all_statistics()
                
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"Statistiques d'appariement (Distance: {args.distance})\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for key, value in stats.items():
                        f.write(f"{key}: {value:.4f}\n")
                    
                    f.write(f"\nNombre d'entrées vérité terrain: {len(truth_entries)}\n")
                    f.write(f"Nombre d'entrées prédites: {len(predicted_entries)}\n")
                    f.write(f"Nombre d'appariements: {len(matcher.matches)}\n")
                
                print(f"Statistiques sauvegardées dans {args.output}")
                
                for key, value in stats.items():
                    print(f"{key}: {value:.4f}")
                
    except FileNotFoundError as e:
        print(f"Erreur: Fichier non trouvé - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


