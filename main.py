import json
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
        """NB : ==> average field-to-field distances """
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
    def __init__(self, entries_a: List[Entry], entries_b: List[Entry]):
        self.entries_a = entries_a
        self.entries_b = entries_b
        self.cost_matrix = self.compute_cost_matrix()
        self.matches = self.match()

    def compute_cost_matrix(self) -> np.ndarray:
        n, m = len(self.entries_a), len(self.entries_b)
        cost_matrix = np.zeros((n, m))

        for i, entry_a in enumerate(self.entries_a):
            for j, entry_b in enumerate(self.entries_b):
                cost_matrix[i, j] = entry_a.distance_to(entry_b)
                # cost_matrix[i, j] = entry_a.distance_to_levenshtein(entry_b)

        return cost_matrix

    def match(self) -> List[Tuple[int, int]]:
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

if __name__ == "__main__":
    v = "01_vt"
    with open("gt/low_vt.json") as f:
        truth_file = json.load(f)

    with open(f"predictions/low_without_incomplete_entry/{v}.json") as f:
        predicted_file = json.load(f)

    truth = truth_file["listes_des_intervenants"]
    predicted = predicted_file["listes_des_intervenants"]

    truth_entries = [Entry(e) for e in truth]
    predicted_entries = [Entry(e) for e in predicted]

    matcher = Matcher(truth_entries, predicted_entries)
    stats = matcher.compute_all_statistics()

    print("Matching (index T -> index P):")
    for i, j in matcher.matches:
        print(f"T[{i}] ⇄ P[{j}]  — {truth_entries[i].get()['nom']} ⇄ {predicted_entries[j].get()['nom']}")

    print("Matching stats:")
    for k, v in stats.items():
        print(f"{k}: {v:.4f}")


