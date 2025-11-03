# -*- coding: utf-8 -*-
"""
src/utils/latex_processing.py
Normalisation des commandes LaTeX vers Unicode pour améliorer le retrieval.
"""

from __future__ import annotations
import re
from typing import Dict

# Mapping LaTeX → Unicode (symboles les plus courants)
LATEX_TO_UNICODE: Dict[str, str] = {
    # Opérateurs calcul différentiel/intégral
    r'\\int': '∫',
    r'\\iint': '∬',
    r'\\iiint': '∭',
    r'\\oint': '∮',
    r'\\sum': '∑',
    r'\\prod': '∏',
    r'\\sqrt': '√',
    r'\\partial': '∂',
    r'\\nabla': '∇',
    r'\\Delta': 'Δ',
    r'\\infty': '∞',
    
    # Opérateurs arithmétiques
    r'\\cdot': '·',
    r'\\times': '×',
    r'\\pm': '±',
    r'\\mp': '∓',
    r'\\div': '÷',
    
    # Relations et équivalences
    r'\\leq': '≤',
    r'\\le': '≤',
    r'\\geq': '≥',
    r'\\ge': '≥',
    r'\\neq': '≠',
    r'\\ne': '≠',
    r'\\equiv': '≡',
    r'\\approx': '≈',
    r'\\sim': '≃',
    r'\\simeq': '≃',
    r'\\cong': '≅',
    r'\\ll': '≪',
    r'\\gg': '≫',
    r'\\propto': '∝',
    
    # Ensembles et appartenance
    r'\\in': '∈',
    r'\\notin': '∉',
    r'\\ni': '∋',
    r'\\emptyset': '∅',
    r'\\varnothing': '∅',
    r'\\cap': '∩',
    r'\\cup': '∪',
    r'\\subset': '⊂',
    r'\\subseteq': '⊆',
    r'\\subsetneq': '⊊',
    r'\\supset': '⊃',
    r'\\supseteq': '⊇',
    r'\\supsetneq': '⊋',
    r'\\oplus': '⊕',
    r'\\ominus': '⊖',
    r'\\otimes': '⊗',
    r'\\odot': '⊙',
    
    # Logique
    r'\\forall': '∀',
    r'\\exists': '∃',
    r'\\nexists': '∄',
    r'\\land': '∧',
    r'\\wedge': '∧',
    r'\\lor': '∨',
    r'\\vee': '∨',
    r'\\neg': '¬',
    r'\\lnot': '¬',
    r'\\implies': '⟹',
    r'\\iff': '⟺',
    
    # Flèches
    r'\\to': '→',
    r'\\rightarrow': '→',
    r'\\Rightarrow': '⇒',
    r'\\implies': '⟹',
    r'\\leftrightarrow': '↔',
    r'\\Leftrightarrow': '⇔',
    r'\\iff': '⟺',
    r'\\mapsto': '↦',
    r'\\longmapsto': '⟼',
    r'\\leftarrow': '←',
    r'\\Leftarrow': '⇐',
    r'\\uparrow': '↑',
    r'\\downarrow': '↓',
    r'\\circ': '∘',
    
    # Géométrie
    r'\\perp': '⟂',
    r'\\parallel': '∥',
    r'\\angle': '∠',
    r'\\triangle': '△',
    r'\\degree': '°',
    r'\\prime': '′',
    
    # Autres symboles
    r'\\therefore': '∴',
    r'\\because': '∵',
    
    # Lettres grecques minuscules
    r'\\alpha': 'α',
    r'\\beta': 'β',
    r'\\gamma': 'γ',
    r'\\delta': 'δ',
    r'\\epsilon': 'ε',
    r'\\varepsilon': 'ε',
    r'\\zeta': 'ζ',
    r'\\eta': 'η',
    r'\\theta': 'θ',
    r'\\vartheta': 'θ',
    r'\\iota': 'ι',
    r'\\kappa': 'κ',
    r'\\lambda': 'λ',
    r'\\mu': 'μ',
    r'\\nu': 'ν',
    r'\\xi': 'ξ',
    r'\\pi': 'π',
    r'\\varpi': 'π',
    r'\\rho': 'ρ',
    r'\\varrho': 'ρ',
    r'\\sigma': 'σ',
    r'\\varsigma': 'ς',
    r'\\tau': 'τ',
    r'\\upsilon': 'υ',
    r'\\phi': 'φ',
    r'\\varphi': 'φ',
    r'\\chi': 'χ',
    r'\\psi': 'ψ',
    r'\\omega': 'ω',
    
    # Lettres grecques majuscules
    r'\\Gamma': 'Γ',
    r'\\Delta': 'Δ',
    r'\\Theta': 'Θ',
    r'\\Lambda': 'Λ',
    r'\\Xi': 'Ξ',
    r'\\Pi': 'Π',
    r'\\Sigma': 'Σ',
    r'\\Upsilon': 'Υ',
    r'\\Phi': 'Φ',
    r'\\Psi': 'Ψ',
    r'\\Omega': 'Ω',
    
    # Ensembles standards (mathbb)
    r'\\mathbb\{N\}': 'ℕ',
    r'\\mathbb\{Z\}': 'ℤ',
    r'\\mathbb\{Q\}': 'ℚ',
    r'\\mathbb\{R\}': 'ℝ',
    r'\\mathbb\{C\}': 'ℂ',
    r'\\mathbb\{P\}': 'ℙ',
    r'\\mathbb\{H\}': 'ℍ',
    r'\\N': 'ℕ',
    r'\\Z': 'ℤ',
    r'\\Q': 'ℚ',
    r'\\R': 'ℝ',
    r'\\C': 'ℂ',
}


def normalize_latex_to_unicode(text: str, aggressive: bool = False) -> str:
    """
    Convertit les commandes LaTeX simples en symboles Unicode.
    Améliore la similarité des embeddings pour le retrieval.
    
    Args:
        text: Texte pouvant contenir du LaTeX
        aggressive: Si True, supprime aussi les délimiteurs $ et les structures complexes
    
    Returns:
        Texte avec symboles Unicode
    
    Examples:
        >>> normalize_latex_to_unicode("Soit $\\alpha \\in \\mathbb{R}$")
        'Soit α ∈ ℝ'
        
        >>> normalize_latex_to_unicode("\\int_0^1 x^2 dx")
        '∫ x^2 dx'
        
        >>> normalize_latex_to_unicode("\\frac{a}{b}")
        'a/b'
    """
    if not text:
        return text
    
    # Sauvegarder le texte original pour comparaison
    original = text
    
    # Étape 1: Remplacer les commandes LaTeX par Unicode
    for latex_cmd, unicode_char in LATEX_TO_UNICODE.items():
        # Utiliser word boundary pour éviter les faux positifs
        # (ex: \int ne match pas \integer)
        pattern = latex_cmd + r'(?![a-zA-Z])'
        text = re.sub(pattern, unicode_char, text)
    
    if aggressive:
        # Étape 2: Traiter les structures complexes
        
        # \frac{a}{b} → (a)/(b)
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
        
        # \sqrt{x} → √(x)
        text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
        
        # \lim_{x \to a} → lim(x→a)
        text = re.sub(r'\\lim_\{([^}]+)\}', r'lim(\1)', text)
        text = re.sub(r'\\lim', 'lim', text)
        
        # Indices et exposants: x_{i} → x_i, x^{2} → x^2
        text = re.sub(r'_\{([^}]+)\}', r'_\1', text)
        text = re.sub(r'\^\{([^}]+)\}', r'^\1', text)
        
        # Supprimer les délimiteurs $ et $$
        text = re.sub(r'\$+', ' ', text)
        
        # Supprimer \left, \right
        text = re.sub(r'\\left|\\right', '', text)
        
        # Supprimer les commandes de formatage courantes
        text = re.sub(r'\\(text|mathrm|mathbf|mathit|mathcal|mathfrak|mathsf|mathtt)\{([^}]+)\}', r'\2', text)
        
        # Supprimer les espaces LaTeX
        text = re.sub(r'\\[,;:!]', ' ', text)
        text = re.sub(r'\\quad|\\qquad', ' ', text)
        
        # Supprimer les accolades restantes et backslashes isolés
        text = re.sub(r'[{}]', ' ', text)
        text = re.sub(r'\\(?![a-zA-Z])', '', text)
        
        # Nettoyer les backslashes restants (commandes non reconnues)
        text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    
    # Étape 3: Normaliser les espaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def extract_latex_commands(text: str) -> set[str]:
    """
    Extrait toutes les commandes LaTeX d'un texte.
    Utile pour debugging ou statistiques.
    
    Args:
        text: Texte avec LaTeX
    
    Returns:
        Ensemble des commandes trouvées (ex: {'\\int', '\\alpha', '\\frac'})
    """
    commands = set()
    
    # Pattern: backslash suivi de lettres
    for match in re.finditer(r'\\([a-zA-Z]+)', text):
        commands.add(f"\\{match.group(1)}")
    
    return commands


def has_latex(text: str) -> bool:
    """
    Détecte si un texte contient du LaTeX.
    
    Args:
        text: Texte à analyser
    
    Returns:
        True si LaTeX détecté
    """
    if not text:
        return False
    
    # Délimiteurs LaTeX
    if re.search(r'\$+', text):
        return True
    
    # Commandes LaTeX courantes
    if re.search(r'\\(frac|int|sum|prod|sqrt|alpha|beta|gamma|mathbb|text)', text):
        return True
    
    return False


def normalize_query_for_retrieval(query: str) -> str:
    """
    Normalise une query utilisateur pour le retrieval.
    Wrapper spécifique pour les queries (mode aggressive).
    
    Args:
        query: Query utilisateur (peut contenir du LaTeX)
    
    Returns:
        Query normalisée
    
    Examples:
        >>> normalize_query_for_retrieval("Calcule $\\int_0^1 x^2 dx$")
        'Calcule ∫ x^2 dx'
    """
    return normalize_latex_to_unicode(query, aggressive=True)


def normalize_document_for_indexing(document: str) -> str:
    """
    Normalise un document pour l'indexation.
    Mode moins agressif pour préserver la structure.
    
    Args:
        document: Texte du document
    
    Returns:
        Document normalisé
    """
    return normalize_latex_to_unicode(document, aggressive=False)


# Export des fonctions principales
__all__ = [
    'normalize_latex_to_unicode',
    'normalize_query_for_retrieval',
    'normalize_document_for_indexing',
    'extract_latex_commands',
    'has_latex',
    'LATEX_TO_UNICODE',
]
