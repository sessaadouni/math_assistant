#!/usr/bin/env python3
"""Quick test for anaphoric reference detection"""

from src.infrastructure.routing.intent_detector import IntentDetector

detector = IntentDetector()

test_cases = [
    ("Qu'est-ce que la dérivée?", False),
    ("donne moi des exo pour m'entrainer dessus", True),
    ("explique moi ça", True),
    ("peux tu approfondir ce sujet", True),
    ("montre moi la formule", False),
    ("des exercices sur les dérivées", False),
    ("en lien avec cette notion", True),
]

print("Test de détection de références anaphoriques:\n")
for query, expected in test_cases:
    result = detector.has_anaphoric_reference(query)
    status = "✅" if result == expected else "❌"
    print(f"{status} '{query}' → {result} (attendu: {expected})")
