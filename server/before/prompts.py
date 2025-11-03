# prompts.py
from langchain_core.prompts import ChatPromptTemplate

# 1) Prof général (Q&A)
PROF_PROMPT = ChatPromptTemplate.from_template("""
Tu es un professeur de mathématiques pédagogue. Réponds clairement et structure ta réponse.

Contexte (extraits du cours avec pages):
{context}

Question: {question}

Exigences:
- Commence par l'idée simple, puis la version formelle.
- Affiche les formules en LaTeX (entre $$…$$).
- Quand tu utilises un résultat du cours, cite la page entre [p.X].
- Termine par une mini-fiche "À retenir" (3–5 lignes).
Réponse:
""")

# 2) Génération de fiche (synthèse)
SHEET_CREATE_PROMPT = ChatPromptTemplate.from_template("""
Génère une fiche de révision sur: "{topic}" (niveau: {level}).

Contexte (extraits du cours):
{context}

Format attendu (Markdown + LaTeX):
- Titre
- Pré-requis
- Définitions clés (avec notations)
- Théorèmes / Propriétés (énoncés + conditions)
- Méthodes / Recettes pas-à-pas
- Formules indispensables (en $$…$$)
- Exemples types (corrigés succincts)
- Erreurs fréquentes
- Références au cours [p.X]

FICHE:
""")

# 3) Vérification d'une fiche personnelle
SHEET_REVIEW_PROMPT = ChatPromptTemplate.from_template("""
Vérifie et améliore la fiche suivante (exactitude, manques, rigueur), en t’appuyant sur le cours.

Fiche de l'étudiant:
{sheet_text}

Contexte (extraits du cours):
{context}

Rends:
- Corrections (factuelles, notations)
- Ajouts nécessaires (défs, hypothèses)
- Reformulations plus rigoureuses
- Liste d'exercices rapides d'application
- Références [p.X]
Réponse:
""")

# 4) Formule à la demande
FORMULA_PROMPT = ChatPromptTemplate.from_template("""
Donne la ou les formules demandées pour: "{query}".
Si plusieurs variantes existent, précise les conditions d'usage.

Contexte (extraits de formulaires/chapitre):
{context}

Rends:
- Énoncé(s) en LaTeX entre $$…$$
- Variables et domaines
- Petite mise en garde (pièges)
- Référence [p.X]
Formule:
""")

# 5) Génération d'examen (multi-chapitres)
EXAM_PROMPT = ChatPromptTemplate.from_template("""
Génère un sujet d'examen (durée {duration}, barème /20) sur les chapitres: {chapters}.
Niveau: {level}. Mélange théorie/méthodes/problèmes.

Contexte (extraits du cours, pages utiles):
{context}

Rends en Markdown:
- En-tête (durée, matériel autorisé, consignes)
- 4 à 6 exercices progressifs (avec sous-questions)
- Chaque exo précise les points
- En fin de sujet: Indications (pas la correction)
- Références [p.X] alignées avec les extraits
Sujet:
""")

# 6) Cours complet sur une notion
COURSE_BUILD_PROMPT = ChatPromptTemplate.from_template("""
Écris un mini-cours complet et autonome sur: "{notion}" (niveau: {level}).

Contexte (extraits du cours officiel):
{context}

Contenu attendu:
- Plan clair
- Définitions et notations
- Propriétés/Théorèmes (avec conditions)
- Méthodes de résolution (algorithmes)
- Exemples canoniques + contre-exemples
- Exercices d’application (énoncé + brève correction)
- Formules en $$…$$
- Références [p.X]
Cours:
""")

# 7) Correcteur de copie
CORRECTEUR_PROMPT = ChatPromptTemplate.from_template("""
Tu corriges une copie. Énoncé:
{statement}

Copie de l'étudiant:
{student_answer}

Contexte (extraits du cours pour la notation officielle):
{context}

Rends:
- Diagnostic pas-à-pas
- Version rédigée correcte
- Barème indicatif /20
- Références [p.X]
Correction:
""")
