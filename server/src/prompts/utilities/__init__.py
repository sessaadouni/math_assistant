"""
Utility Prompts - Prompts for specific utilities (formulas, theorems, proofs)
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import UtilityPrompt


class FormulaPrompt(UtilityPrompt):
    """Explain and provide a mathematical formula"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Donne la formule demandée : "{formula_name}" (niveau {level}).

[Contexte du cours]
{context}

Format :
- Énoncé de la formule en LaTeX $$…$$
- Conditions d'application / hypothèses
- Interprétation / signification
- Exemple d'utilisation (court)
- Erreurs courantes / pièges
- Références [p.X]

Formule :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "formula"


class TheoremPrompt(UtilityPrompt):
    """State and explain a theorem"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Énonce et explique le théorème : "{theorem_name}" (niveau {level}).

[Contexte du cours]
{context}

Structure :
- **Énoncé** (hypothèses, conclusion) en LaTeX $$…$$
- **Signification** (qu'est-ce que cela dit ?)
- **Conditions nécessaires** (sans lesquelles le théorème tombe)
- **Exemple** (application simple)
- **Contre-exemple** (si hypothèses non vérifiées)
- **Corollaires** / conséquences directes (optionnel)
- Références [p.X]

Théorème :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "theorem"


class ProofPrompt(UtilityPrompt):
    """Provide a mathematical proof"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Démontre : "{statement}" (niveau {level}).

[Contexte du cours]
{context}

Instructions :
- Rappel de l'énoncé (hypothèses, conclusion)
- Stratégie de preuve (1–2 lignes : méthode utilisée)
- Démonstration détaillée, rigoureuse, progressive
- Chaque étape justifiée (théorèmes, définitions, calculs)
- Conclusion claire
- Formules en LaTeX $$…$$
- Références [p.X]

Démonstration :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "proof"


__all__ = [
    "FormulaPrompt",
    "TheoremPrompt",
    "ProofPrompt",
]
