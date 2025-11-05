"""
Exercise Prompts - Prompts for exercise-related tasks
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import ExercisePrompt


class ExerciseGeneratorPrompt(ExercisePrompt):
    """Generate exercises on a topic"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Génère {count} exercices sur : "{topic}" (niveau {level}).

[Contexte du cours — style et contenus]
{context}

Paramètres :
- source = {source}   # "book_inspired" (s'inspirer du style du livre sans copier) ou "original"
- difficulté = {difficulty}   # facile / moyen / difficile / mixte
- format attendu :
  - **Énoncé** clair et autonome
  - **Objectif** (compétence ciblée)
  - **Indications** (0–2 lignes)
  - **Corrigé** (si {with_solutions} == true, sinon "Corrigé masqué")
  - **Références** [p.X] (quand applicable)

Je veux des exercices variés (calculs, preuve courte, application directe, petit problème).
Exercices :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "exercise_gen"


class ExerciseSolverPrompt(ExercisePrompt):
    """Solve an exercise step by step"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Résous l'exercice ci-dessous pas à pas.

[Énoncé]
{statement}

[Contexte du cours]
{context}

Exigences :
- Plan de résolution (1–3 lignes), puis solution détaillée.
- Vérifications / cas limites.
- Références [p.X].
- Si des données manquent, poser les questions minimales.

Solution :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "solver"


class ExerciseCorrectorPrompt(ExercisePrompt):
    """Correct and grade a student's exercise solution"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu corriges la copie d'un étudiant.

[Énoncé]
{statement}

[Copie de l'étudiant]
{copy}

[Contexte du cours — référence]
{context}

Instructions :
- Barème global : {max_points} points
- Identifie les étapes de résolution attendues (découpage)
- Pour chaque étape : justesse, rigueur, clarté → note partielle
- Points positifs, points négatifs, conseils
- Note globale /{max_points}
- Références [p.X] pour rappeler les règles

Correction :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "exo_corrector"


__all__ = [
    "ExerciseGeneratorPrompt",
    "ExerciseSolverPrompt",
    "ExerciseCorrectorPrompt",
]
