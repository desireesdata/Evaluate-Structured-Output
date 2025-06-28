from typing import Dict, List, Union, Literal
from difflib import SequenceMatcher
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