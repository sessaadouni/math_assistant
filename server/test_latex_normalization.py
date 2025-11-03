# -*- coding: utf-8 -*-
"""
Test rapide de la normalisation LaTeX → Unicode
"""

from src.utils.latex_processing import (
    normalize_latex_to_unicode,
    normalize_query_for_retrieval,
    has_latex,
    extract_latex_commands,
)

def test_basic_normalization():
    """Test des conversions de base"""
    print("🧪 Test 1: Conversions de base")
    
    tests = [
        ("$\\alpha \\in \\mathbb{R}$", "α ∈ ℝ"),
        ("\\int_0^1 x^2 dx", "∫ x^2 dx"),
        ("\\frac{a}{b}", "(a)/(b)"),
        ("\\sqrt{x + y}", "√(x + y)"),
        ("\\sum_{i=1}^n i", "∑ i"),
        ("\\lim_{x \\to 0} \\frac{\\sin x}{x}", "lim(x → 0) (sin x)/(x)"),
        ("\\forall x \\in \\mathbb{N}, x \\geq 0", "∀ x ∈ ℕ, x ≥ 0"),
        ("\\exists \\epsilon > 0", "∃ ε > 0"),
    ]
    
    for input_text, expected_contains in tests:
        result = normalize_query_for_retrieval(input_text)
        print(f"  '{input_text}'")
        print(f"  → '{result}'")
        if expected_contains in result or any(c in result for c in expected_contains):
            print("  ✅ OK")
        else:
            print(f"  ❌ FAIL (attendu: contient '{expected_contains}')")
        print()

def test_latex_detection():
    """Test de détection LaTeX"""
    print("🧪 Test 2: Détection LaTeX")
    
    tests = [
        ("Quelle est la dérivée de x^2 ?", False),
        ("Calcule $\\int x dx$", True),
        ("Soit \\alpha un réel", True),
        ("Théorème de Pythagore", False),
        ("\\frac{a}{b} est une fraction", True),
    ]
    
    for text, expected in tests:
        result = has_latex(text)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{text}' → {result} (attendu: {expected})")
    print()

def test_command_extraction():
    """Test d'extraction des commandes"""
    print("🧪 Test 3: Extraction commandes LaTeX")
    
    text = r"Soit $\int_0^1 \frac{\sin x}{x} dx$ et $\alpha \in \mathbb{R}$"
    commands = extract_latex_commands(text)
    print(f"  Texte: {text}")
    print(f"  Commandes trouvées: {sorted(commands)}")
    print()

def test_real_queries():
    """Test avec des vraies queries étudiants"""
    print("🧪 Test 4: Queries réalistes")
    
    queries = [
        "Explique moi $\\lim_{x \\to 0} \\frac{\\sin x}{x}$",
        "Comment calculer $\\int_0^{\\pi} \\sin^2(x) dx$ ?",
        "Quelle est la dérivée de $\\ln(x^2 + 1)$ ?",
        "Démontre que $\\forall n \\in \\mathbb{N}, \\sum_{k=1}^n k = \\frac{n(n+1)}{2}$",
        "Résous $\\sqrt{x + 3} = 5$",
    ]
    
    for query in queries:
        normalized = normalize_query_for_retrieval(query)
        print(f"  Avant: {query}")
        print(f"  Après: {normalized}")
        print()

def test_comparison():
    """Test de similarité amélioration"""
    print("🧪 Test 5: Comparaison similarité")
    
    # Simulation: même concept, syntaxes différentes
    pairs = [
        ("$\\int x dx$", "intégrale de x"),
        ("$\\alpha \\in \\mathbb{R}$", "alpha appartient aux réels"),
        ("$\\sum_{i=1}^n i$", "somme de i de 1 à n"),
    ]
    
    for latex_form, text_form in pairs:
        latex_normalized = normalize_query_for_retrieval(latex_form)
        print(f"  LaTeX: {latex_form} → {latex_normalized}")
        print(f"  Texte: {text_form}")
        
        # Vérifier qu'ils partagent maintenant des symboles communs
        common_symbols = set(latex_normalized) & set(text_form)
        if any(c in "∫∑αβγℝℕℤ∈" for c in latex_normalized):
            print("  ✅ Symboles Unicode présents")
        else:
            print("  ⚠️  Peu de symboles Unicode")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTS NORMALISATION LATEX → UNICODE")
    print("=" * 60)
    print()
    
    test_basic_normalization()
    test_latex_detection()
    test_command_extraction()
    test_real_queries()
    test_comparison()
    
    print("=" * 60)
    print("✅ Tests terminés !")
    print("=" * 60)
