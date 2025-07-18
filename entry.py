from typing import Dict, List, Union, Literal
from difflib import SequenceMatcher
import difflib
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

    def similarity_to(self, other: 'Entry') -> float:
        return difflib.SequenceMatcher(None, self.normalize_field("nom"), other.normalize_field("nom")).ratio()

    def distance_to(self, other: 'Entry') -> float:
        return 1.0 - self.similarity_to(other)
    
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

    def iou_distance_on_pages(self, other: 'Entry') -> float:
        """Calcule la distance entre les listes de pages en utilisant 1 - IoU."""
        pages_a = self.data.get("references_pages", [])
        pages_b = other.data.get("references_pages", [])

        # S'assurer que les données sont des listes
        if not isinstance(pages_a, list):
            pages_a = []
        if not isinstance(pages_b, list):
            pages_b = []

        set_a = set(pages_a)
        set_b = set(pages_b)

        intersection_size = len(set_a.intersection(set_b))
        union_size = len(set_a.union(set_b))

        if union_size == 0:
            return 0.0  # Deux listes vides sont identiques

        iou = intersection_size / union_size
        return 1.0 - iou

    def combined_distance_iou(self, other: 'Entry', name_weight: float = 0.5) -> float:
        """
        Calcule une distance combinée en pondérant la distance du nom (par défaut)
        et la distance IoU des pages.
        """
        if not (0.0 <= name_weight <= 1.0):
            raise ValueError("Le poids du nom (name_weight) doit être entre 0.0 et 1.0")

        page_weight = 1.0 - name_weight

        dist_name = self.distance_to(other)
        dist_pages = self.iou_distance_on_pages(other)

        return (name_weight * dist_name) + (page_weight * dist_pages)