"""
Course Prompts - Prompts for course-related tasks
"""

from langchain_core.prompts import ChatPromptTemplate
from ..base import CoursePrompt


class CourseBuildPrompt(CoursePrompt):
    """Build a complete, rigorous course on a topic (double track: CPGE-proof + Applied-Engineering)"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu écris un COURS COMPLET et rigoureux sur : "{topic}"
Niveau : {level}.

[Contexte — extraits du cours officiel]
{context}

IMPORTANT : Ce n'est PAS un mini-cours, mais un cours EXHAUSTIF avec deux pistes parallèles :
- Piste CPGE-preuve : définitions ε-δ, énoncés précis, esquisses de preuves
- Piste Appli-ingé : procédures opérationnelles, heuristiques, erreurs courantes

Structure OBLIGATOIRE :
═══════════════════════

1) Introduction / plan
   - But du cours (objectifs pédagogiques)
   - Plan détaillé avec articulation des parties
   - Niveau visé et prérequis

2) Définitions + notations
   - Définitions formelles (ε-δ si pertinent)
   - Notations standards avec explications
   - Domaines de définition, conditions d'existence
   - Conventions utilisées

3) Propriétés / théorèmes (conditions d'application)
   - Énoncés PRÉCIS avec toutes les hypothèses
   - **Piste CPGE** : Esquisses de preuves (idées-clés, pas de détails exhaustifs sauf si crucial)
   - **Piste Ingé** : Critères pratiques d'application
   - Conditions nécessaires vs suffisantes
   - Cas particuliers importants

4) Méthodes / algorithmes de résolution
   - **Piste CPGE** : Justifications théoriques des méthodes
   - **Piste Ingé** : Checklists étape par étape
   - Organigrammes décisionnels ("quand utiliser telle méthode ?")
   - Optimisations et astuces de calcul
   - Pièges et erreurs fréquentes à chaque étape

5) Exemples canoniques + contre-exemples
   - Au moins 3-4 exemples standards DÉTAILLÉS avec calculs complets
   - Au moins 2-3 contre-exemples pathologiques (avec explication du piège)
   - Progression : simple → complexe → cas-limites
   - Annotations pédagogiques ("Pourquoi cette étape ?", "Attention ici...")

6) Exercices d'application (énoncé + correction DÉTAILLÉE)
   - Minimum 5-6 exercices de difficulté croissante
   - Pour chaque exercice :
     * Énoncé clair avec indications de difficulté
     * Indices progressifs (si l'étudiant bloque)
     * Correction PAS À PAS avec justifications
     * Points de vigilance et variantes possibles
   - Mélange : calculs directs, démonstrations, problèmes ouverts

7) Formules clés en $$…$$
   - Toutes les formules essentielles en LaTeX
   - Conditions d'application pour chaque formule
   - Cas particuliers et limites
   - Liens entre les formules (dérivations, équivalences)

8) Références [p.X]
   - Citations précises du contexte fourni [p.X]
   - Si une partie manque, indiquer clairement "Contexte insuffisant pour..."
   - Bibliographie conseillée (si dans le contexte)

9) **NOUVEAU** : Mini-révision interactive
   - 3-5 questions de compréhension rapides
   - Checkpoints pour auto-évaluation
   - Suggestions de révisions ciblées selon les lacunes

Remarques CRITIQUES :
━━━━━━━━━━━━━━━━━━━━
✓ Style : clair, progressif, RIGOUREUX mais pédagogique
✓ LaTeX : $...$ inline, $$...$$ pour les équations importantes
✓ Ne JAMAIS halluciner : si le contexte ne suffit pas, le dire explicitement
✓ Alterner théorie (CPGE) et pratique (Ingé) dans chaque section
✓ Exemples et contre-exemples aussi importants que la théorie
✓ Corrections d'exercices détaillées avec pédagogie explicite

Cours complet :
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "course_build"


class CourseExplainPrompt(CoursePrompt):
    """Explain a course topic with pedagogy (quick mini-course, 10-15min read)"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu écris un MINI-COURS ciblé et pédagogique sur : "{topic}"
Niveau : {level}.

[Contexte du cours]
{context}

OBJECTIF : Explication rapide (10-15min de lecture) pour comprendre l'essentiel.
Ce N'EST PAS un cours complet, mais une introduction claire et efficace.

Structure CONCISE :
═══════════════════

1) L'essentiel en 3 phrases
   - Qu'est-ce que c'est ?
   - Pourquoi c'est important ?
   - Où ça s'utilise ?

2) Définitions clés (seulement les indispensables)
   - Notations standards
   - Définitions intuitives PUIS formelles
   - Analogies / visualisations textuelles si utile

3) Propriétés principales (top 3-4)
   - Théorèmes essentiels (énoncé simple)
   - Conditions d'application (vulgarisées)
   - Intuition "pourquoi ça marche ?"

4) Méthode type (1 algorithme clé)
   - Checklist pratique étape par étape
   - UN exemple détaillé représentatif
   - Les 2-3 pièges les plus fréquents

5) Mini-FAQ (3-5 questions courantes)
   Q: [question typique d'étudiant]
   R: [réponse claire et concise]

6) Formules à retenir (tableau compact)
   - Top 5-7 formules en $$...$$
   - Conditions d'utilisation en 1 ligne

7) Pour aller plus loin
   - Références [p.X] pour approfondir
   - Liens avec d'autres notions du cours

Ton et style :
━━━━━━━━━━━
✓ Pédagogique et accessible (vulgarisation maîtrisée)
✓ Progression : intuition → rigueur
✓ Exemples concrets avant abstraction
✓ Langage clair, phrases courtes
✓ Encourageant et motivant

Contraintes :
━━━━━━━━━━
✗ PAS de preuves détaillées (juste l'idée si nécessaire)
✗ PAS d'exhaustivité (privilégier clarté > complétude)
✗ PAS d'hallucination : si info manque, le dire
✓ Rester fidèle au contexte fourni [p.X]

Mini-cours :
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
