import csv
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import wasserstein_distance as scipy_wasserstein
from entry import Entry


class Matcher:
    def __init__(self, entries_a: List[Entry], entries_b: List[Entry], distance_method: str = "ratcliff"):
        """A Matcher is a comparator; he compares two sets of entry and produces a matrix"""
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
                elif distance_method == "iou_combined":
                    cost_matrix[i, j] = entry_a.combined_distance_iou(entry_b)
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
    
    def compute_integrated_matching_quality(self, steps: int = 1000) -> float:
        """
        IMQ. Approximation de l'aire sous la courbe qualité/couverture, c'est-à-dire
        la proportion de matches ayant une qualité supérieure à un seuil donné, intégrée sur tous les seuils.
        Renvoie une valeur entre 0 et 1 (plus elle est proche de 1, plus les matches sont nombreux et de bonne qualité).
        """
        if not self.matches:
            return 0.0

        qualities = np.array([1.0 - self.cost_matrix[i, j] for i, j in self.matches])
        thresholds = np.linspace(0, 1, steps)
        area = 0.0

        for t in thresholds:
            coverage = np.sum(qualities >= t) / len(self.entries_a)
            area += coverage

        return area / steps
    
    def compute_irq(self) -> float:
        if not self.matches:
            return 0.0

        # Mapping des index vérité vers leur match (si existant)
        matched_dict = {i: j for i, j in self.matches}
        total_quality = 0.0

        for i in range(len(self.entries_a)):
            if i in matched_dict:
                j = matched_dict[i]
                total_quality += 1.0 - self.cost_matrix[i, j]
            else:
                total_quality += 0.0  # Non apparié = qualité nulle

        return total_quality / len(self.entries_a)

    def compute_f1q(self) -> float:
        imq = self.compute_integrated_matching_quality()
        irq = self.compute_irq()

        if imq + irq == 0:
            return 0.0
        return 2 * (imq * irq) / (imq + irq)

    def wasserstein_distance(self) -> float:
        if not self.matches:
            return 0.0
        qualities = np.array([1.0 - self.cost_matrix[i, j] for i, j in self.matches])
        # Si tu compares à une distribution idéale (par ex. qualité parfaite = 1 pour tous)
        ideal = np.ones_like(qualities)
        return scipy_wasserstein(qualities, ideal)


    def compute_overall_matching_quality_imq(self) -> float:
        """
        Version de l'OMQ (Overall Matching Quality) basée sur l'IMQ (Integrated Matching Quality),
        qui remplace la précision pour tenir compte de la qualité de tous les appariements.
        """
        imq = self.compute_integrated_matching_quality()
        recall = self.compute_precision_recall_f1()["Recall"]
        avg_quality = self.compute_average_matching_quality()

        denom = (imq * recall + imq * avg_quality + recall * avg_quality)
        if denom == 0:
            return 0.0
        return 3 * (imq * recall * avg_quality) / denom


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

    # Modifié
    def compute_all_statistics(self) -> Dict[str, float]:
        metrics = self.compute_precision_recall_f1()
        avg_quality = self.compute_average_matching_quality()
        overall_quality = self.compute_overall_matching_quality()
        imq = self.compute_integrated_matching_quality()
        irq = self.compute_irq()
        f1q = self.compute_f1q()
        omq_imq = self.compute_overall_matching_quality_imq()
        wasserstein = self.wasserstein_distance()

        # tester les #ajouté
        return {
            **metrics,
            "Average Matching Quality": avg_quality,
            "Overall Matching Quality": overall_quality,
            "Integrated Matching Quality": imq,
            "Integrated Recall Quality": irq, #ajouté
            "F1Q":  f1q, #ajouté
            "Distance de Wasserstein 1D": wasserstein, #ajouté
            "Overall Matching Quality (IMQ-based)": omq_imq
        }

    def export_matches_to_csv(self, truth_entries: List[Entry], predicted_entries: List[Entry], output_file: str):
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            writer.writerow(['Truth_Index', 'Predicted_Index', 'Truth_Nom', 'Predicted_Nom',
                           'Truth_Pages', 'Predicted_Pages',
                           'Ratcliff_Obershelp_Distance', 'IoU_Distance', 'Combined_Distance',
                           'Ratcliff_Obershelp_Quality', 'IoU_Quality', 'Combined_Quality'])

            for i, j in self.matches:
                truth_entry = truth_entries[i]
                pred_entry = predicted_entries[j]
                
                t = truth_entry.get()
                p = pred_entry.get()

                name_dist = truth_entry.distance_to(pred_entry)
                iou_dist = truth_entry.iou_distance_on_pages(pred_entry)
                combined_dist = self.cost_matrix[i, j]

                writer.writerow([
                    i, j, t.get('nom', ''), p.get('nom', ''),
                    t.get('references_pages', ''), p.get('references_pages', ''),
                    f"{name_dist:.4f}", f"{iou_dist:.4f}", f"{combined_dist:.4f}",
                    f"{1.0 - name_dist:.4f}", f"{1.0 - iou_dist:.4f}", f"{1.0 - combined_dist:.4f}"
                ])

            # Ajout des faux négatifs (non appariés dans la vérité)
            matched_truth_indices = {i for i, j in self.matches}
            for i in range(len(truth_entries)):
                if i not in matched_truth_indices:
                    t = truth_entries[i].get()
                    writer.writerow([i, '', t.get('nom', ''), '', t.get('references_pages', ''), '',
                                   'FN', 'FN', 'FN', 'FN', 'FN', 'FN'])

            # Ajout des faux positifs (non appariés dans la prédiction)
            matched_pred_indices = {j for i, j in self.matches}
            for j in range(len(predicted_entries)):
                if j not in matched_pred_indices:
                    p = predicted_entries[j].get()
                    writer.writerow(['', j, '', p.get('nom', ''), '', p.get('references_pages', ''),
                                   'FP', 'FP', 'FP', 'FP', 'FP', 'FP'])
