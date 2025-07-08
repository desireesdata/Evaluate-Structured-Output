import json
import argparse
import csv
import sys
import os
import glob
from typing import Dict, List, Tuple
from entry import Entry
from matcher import Matcher
import jellyfish

def compute_concordance_expressive(imq: float, irq: float, epsilon: float = 0.001) -> float:
    """
    Calcule la concordance expressive entre IMQ et IRQ.

    Args:
        imq (float): Integrated Matching Quality
        irq (float): Integrated Recall Quality
        epsilon (float): Petite constante pour éviter la division par zéro

    Returns:
        float: Score de concordance expressive (entre 0 et 1)
    """
    moyenne = (imq + irq) / 2.0
    ecart = abs(imq - irq)
    concordance = 1.0 - (ecart / (moyenne + epsilon))
    return concordance


def test_concordance_cases():
    examples = [
        {"imq": 0.95, "irq": 0.95, "label": "Cas idéal (égalité parfaite)"},
        {"imq": 0.92, "irq": 0.90, "label": "Écart faible"},
        {"imq": 0.8177, "irq": 0.8179, "label": "PAGE"},
        {"imq": 0.80, "irq": 0.60, "label": "Écart modéré"},
        {"imq": 0.95, "irq": 0.50, "label": "Déséquilibre fort"},
        {"imq": 0.30, "irq": 0.20, "label": "Faibles scores"},
        {"imq": 0.001, "irq": 0.001, "label": "Scores quasi nuls"},
    ]

    print("Test du score de Concordance Expressive")
    print("=" * 45)
    for ex in examples:
        score = compute_concordance_expressive(ex["imq"], ex["irq"])
        print(f"{ex['label']:<30} | IMQ = {ex['imq']:.3f}, IRQ = {ex['irq']:.3f} => Concordance = {score:.4f}")


if __name__ == "__main__":
    test_concordance_cases()
