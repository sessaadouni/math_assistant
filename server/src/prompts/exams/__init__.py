"""
Exam Prompts - Prompts for exam-related tasks
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import ExamPrompt


class ExamGeneratorPrompt(ExamPrompt):
    """Generate a complete exam subject"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Rédige un sujet d'examen complet.
Durée : {duration} — Barème total : {total_points}  
Niveau : {level}  
Chapitres : {chapters}

[Contexte du cours]
{context}

Attendus :
- En-tête (durée, matériel autorisé, consignes)
- {num_exercises} exercices progressifs avec **barème partiel** explicite
- Mélange : théorie (déf/énoncé), méthodes, problème de synthèse
- Section **Indications** en fin
- Références [p.X] quand pertinent

Sujet :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "exam"


class ExamCorrectorPrompt(ExamPrompt):
    """Correct and grade an exam copy"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu corriges une copie d'examen.

[Sujet]
{subject}

[Copie de l'étudiant]
{copy}

[Contexte du cours]
{context}

Consignes :
- Barème global : {total_points} points
- Pour chaque exercice :
  * Découpages du barème (sous-questions, étapes)
  * Points obtenus / points possibles
  * Commentaires (justesse, rigueur, erreurs, bonnes idées)
- Récapitulatif global : note totale, points forts, axes d'amélioration
- Références [p.X] pour les rappels théoriques

Correction :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "exam_corrector"


class QCMPrompt(ExamPrompt):
    """Generate a QCM (multiple choice quiz)"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Génère un QCM de {num_questions} questions sur : {topics} (niveau {level}).

[Contexte du cours]
{context}

Format :
- Pour chaque question : 1 ou plusieurs bonnes réponses
- 4–5 propositions par question
- Mélange : définitions, propriétés, calculs simples, vrai/faux justifié
- En fin : **Corrigé** (justifications + références [p.X])

QCM :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "qcm"


class KhollePrompt(ExamPrompt):
    """Generate an oral exam (khôlle) subject"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Prépare un sujet de khôlle (interrogation orale) — durée {duration}.
Chapitres : {chapters} — Niveau : {level}

[Contexte du cours]
{context}

Structure :
- **Question de cours** (définition + énoncé d'un théorème) → références [p.X]
- **Exercice** (résolution au tableau en ~10 min) avec indications
- **Questions complémentaires** (2–3 questions rapides pour tester compréhension)

Attendus :
- Énoncé clair, autonome
- Difficulté adaptée à un oral (pas trop calculatoire)
- Permettre discussion et extension

Sujet de khôlle :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "kholle"


__all__ = [
    "ExamGeneratorPrompt",
    "ExamCorrectorPrompt",
    "QCMPrompt",
    "KhollePrompt",
]
