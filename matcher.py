import csv
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from entry import Entry


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