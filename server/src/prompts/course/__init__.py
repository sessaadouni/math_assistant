"""
Course Prompts - Prompts for course-related tasks
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import CoursePrompt


class CourseBuildPrompt(CoursePrompt):
    """Build a complete mini-course on a topic"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu écris un mini-cours autonome et rigoureux sur : "{notion}"
Niveau : {level}.

[Contexte — extraits du cours officiel]
{context}

Structure :
1) Introduction / plan
2) Définitions + notations
3) Propriétés / théorèmes (conditions d'application)
4) Méthodes / algorithmes de résolution
5) Exemples canoniques + contre-exemples
6) Exercices d'application (énoncé + correction concise)
7) Formules clés en $$…$$
8) Références [p.X]

Remarques :
- Ne pas halluciner hors contexte ; si une partie manque, indiquer "Contexte insuffisant".
- Style clair, progressif, soigné.

Cours :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "course_build"


class CourseExplainPrompt(CoursePrompt):
    """Explain a course topic with pedagogy"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Explique le cours sur : "{topic}" au niveau {level}.

[Contexte du cours]
{context}

Attendus :
- Vulgarisation maîtrisée → puis montée en rigueur.
- Exemples concrets et analogies.
- Mini-visualisations textuelles si utile (axes, repères, tableaux).
- Brève FAQ (3–5 questions courantes) avec réponses.
- Références [p.X] pour les points clés.

Explication :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "course_explain"


class CourseSummaryPrompt(CoursePrompt):
    """Summarize a course topic"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Résume le cours : "{topic}" (niveau {level}) en un plan synthétique.

[Contexte du cours]
{context}

Format attendu (Markdown) :
- Idées-clés (bullet points courts)
- Définitions et notations indispensables
- Théorèmes/propriétés (énoncé court + conditions) avec [p.X]
- Formules essentielles en $$…$$
- Erreurs/pieges fréquents (liste)
- Mini-glossaire (termes → 1 ligne)
- 2–3 exercices rapides (énoncés courts)

Résumé :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "course_summary"


class SheetCreatePrompt(CoursePrompt):
    """Create a revision sheet"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Crée une fiche de révision claire et utile sur : "{topic}" (niveau {level}).

[Contexte du cours]
{context}

Format (1 page A4 simulée en Markdown) :
- Titre + plan rapide
- Définitions (encadrées) en $$…$$
- Propriétés/théorèmes (conditions, hypothèses) avec [p.X]
- Méthodes types (étapes) + exemples ultra-courts
- Formules clés (tableau ou liste)
- Pièges / erreurs à éviter
- 3 exercices flash (énoncés + réponses rapides)

Fiche :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "sheet_create"


class SheetReviewPrompt(CoursePrompt):
    """Review and improve an existing sheet"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Révise et améliore la fiche suivante sur "{topic}" (niveau {level}).

[Fiche actuelle]
{sheet}

[Contexte du cours de référence]
{context}

Actions :
- Corrige les erreurs/imprécisions
- Complète les définitions/théorèmes manquants (avec [p.X])
- Améliore la lisibilité (mise en forme, notations)
- Ajoute 1–2 méthodes ou exemples clés si pertinent
- Reformule les formules en LaTeX $$…$$

Fiche améliorée :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "sheet_review"


__all__ = [
    "CourseBuildPrompt",
    "CourseExplainPrompt",
    "CourseSummaryPrompt",
    "SheetCreatePrompt",
    "SheetReviewPrompt",
]
