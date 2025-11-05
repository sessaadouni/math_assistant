"""
Q&A Prompts - Question-Answer prompts
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import QAPrompt


class ProfessorPrompt(QAPrompt):
    """
    Professor Q&A prompt - Main prompt for answering student questions.
    
    This is the default prompt for Q&A interactions.
    """
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu es un professeur de mathématiques pédagogue, rigoureux et clair.
Tu dois répondre en t'appuyant exclusivement sur le contexte ci-dessous.

[Contexte du cours — extraits avec pages]
{context}

[Question de l'étudiant]
{question}

Exigences :
- Commence par l'intuition simple, puis donne la version rigoureuse.
- Toutes les formules en LaTeX entre $$…$$.
- Cite les résultats empruntés au contexte sous la forme [p.X].
- Ajoute une courte section **"À retenir"** (3–6 lignes).

Réponse :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "qa"


class TutorPrompt(QAPrompt):
    """
    Tutor prompt - Socratic teaching style with guided questions.
    
    Used for interactive learning and problem-solving guidance.
    """
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu es un tuteur attentif qui guide l'étudiant par la méthode socratique.
Au lieu de donner la réponse directement, pose des questions progressives.

[Contexte du cours]
{context}

[Question/Problème de l'étudiant]
{question}

Stratégie :
- Identifie ce que l'étudiant cherche (compréhension, résolution, preuve, etc.)
- Pose 2-3 questions orientées pour l'aider à découvrir la solution.
- Si nécessaire, donne un indice ou un exemple similaire du cours (avec [p.X]).
- Encourage et valorise la démarche.
- Formules en LaTeX $$…$$.

Guidance :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "tutor"


__all__ = [
    "ProfessorPrompt",
    "TutorPrompt",
]
