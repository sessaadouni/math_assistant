# -*- coding: utf-8 -*-
from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate

# =====================#
#   POLITIQUE GÉNÉRALE #
# =====================#
# À incorporer implicitement dans tous les prompts :
# - Français clair, structuré, niveau adapté.
# - LaTeX en $$…$$ (affichage KaTeX/MathJax OK).
# - Citer les sources du cours sous la forme [p.X].
# - S’en tenir au contexte fourni. Si le contexte est insuffisant:
#   écrire "Contexte insuffisant pour répondre avec rigueur." + dire ce qui manque.
# - Quand pertinent: donner conditions d’application, notations, pièges fréquents.

# ============ Q&A professeur (par défaut) ============
PROF_PROMPT = ChatPromptTemplate.from_template("""
Tu es un professeur de mathématiques pédagogue, rigoureux et clair.
Tu dois répondre en t’appuyant exclusivement sur le contexte ci-dessous.

[Contexte du cours — extraits avec pages]
{context}

[Question de l'étudiant]
{question}

Exigences :
- Commence par l’intuition simple, puis donne la version rigoureuse.
- Toutes les formules en LaTeX entre $$…$$.
- Cite les résultats empruntés au contexte sous la forme [p.X].
- Ajoute une courte section **"À retenir"** (3–6 lignes).

Réponse :
""")

# ============ Cours complet (construction) ============
COURSE_BUILD_PROMPT = ChatPromptTemplate.from_template("""
Tu écris un mini-cours autonome et rigoureux sur : "{notion}"
Niveau : {level}.

[Contexte — extraits du cours officiel]
{context}

Structure :
1) Introduction / plan
2) Définitions + notations
3) Propriétés / théorèmes (conditions d’application)
4) Méthodes / algorithmes de résolution
5) Exemples canoniques + contre-exemples
6) Exercices d’application (énoncé + correction concise)
7) Formules clés en $$…$$
8) Références [p.X]

Remarques :
- Ne pas halluciner hors contexte ; si une partie manque, indiquer "Contexte insuffisant".
- Style clair, progressif, soigné.

Cours :
""")

# ============ Explication d’un cours (mode “expliquer”) ============
COURSE_EXPLAIN_PROMPT = ChatPromptTemplate.from_template("""
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

# ============ Résumé de cours ============
COURSE_SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
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

# ============ Fiche de révision (création) ============
SHEET_CREATE_PROMPT = ChatPromptTemplate.from_template("""
Crée une fiche de révision claire et utile sur : "{topic}" (niveau {level}).

[Contexte du cours]
{context}

Format :
1. **Pré-requis**
2. **Définitions clés** (notations)
3. **Théorèmes / Propriétés** (conditions) + [p.X]
4. **Méthodes / Recettes** pas-à-pas
5. **Formules $$…$$** (+ signification des variables)
6. **Exemples types** (solution concise)
7. **Pièges fréquents / conseils**
8. **Références** [p.X]
""")

# ============ Fiche de révision (revue) ============
SHEET_REVIEW_PROMPT = ChatPromptTemplate.from_template("""
Évalue la fiche de révision ci-dessous.

[Fiche de l’étudiant]
{sheet_text}

[Contexte du cours]
{context}

Attendus :
- Corrections (erreurs, imprécisions, notations)
- Ajouts nécessaires (défs, hypothèses, cas limites)
- Reformulations pour plus de clarté/rigueur
- 3–5 Exercices d’application rapides (énoncés)
- Références [p.X]
- Optionnel : Diff "avant → après" sur 2–4 segments critiques.

Revue :
""")

# ============ Formules ============
FORMULA_PROMPT = ChatPromptTemplate.from_template("""
Donne les formules associées à : "{query}" à partir du contexte.

[Contexte]
{context}

Exigences :
- Chaque formule en $$…$$, avec signification des variables et domaines.
- Conditions d’usage, variantes notables.
- Mise en garde (pièges).
- Références [p.X].

Formules :
""")

# ============ Théorème (énoncé) ============
THEOREM_PROMPT = ChatPromptTemplate.from_template("""
Donne l’énoncé (propre et complet) du théorème lié à : "{query}".

[Contexte]
{context}

Exigences :
- Énoncé formel (hypothèses → conclusion), LaTeX $$…$$ si utile.
- Nom usuel du théorème si présent dans le contexte.
- Références [p.X].

Énoncé :
""")

# ============ Démonstration ============
PROOF_PROMPT = ChatPromptTemplate.from_template("""
Rédige une démonstration rigoureuse pour : "{statement}".

[Contexte]
{context}

Attendus :
- Plan de preuve (idée directrice).
- Preuve détaillée (étapes numérotées), $$…$$ pour expressions.
- Point(s) d’attention (le(s) lemme(s) utilisé(s)).
- Références [p.X].
- Si la preuve n’est pas couverte par le contexte, préciser "Contexte insuffisant" et proposer un **schéma de preuve** plausible (sans inventer de résultat non cité).

Démonstration :
""")

# ============ Génération d’exercices (depuis le livre / hors livre) ============
EXERCISE_GEN_PROMPT = ChatPromptTemplate.from_template("""
Génère {count} exercices sur : "{topic}" (niveau {level}).

[Contexte du cours — style et contenus]
{context}

Paramètres :
- source = {source}   # "book_inspired" (s’inspirer du style du livre sans copier) ou "original"
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

# ============ Génération d’examen (avec barème) ============
EXAM_PROMPT = ChatPromptTemplate.from_template("""
Rédige un sujet d’examen complet.
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

# ============ Résolution d’un exercice ============
SOLVER_PROMPT = ChatPromptTemplate.from_template("""
Résous l’exercice ci-dessous pas à pas.

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

# ============ Aide guidée (Socratic / Learn & Study) ============
TUTOR_PROMPT = ChatPromptTemplate.from_template("""
Tu joues un tuteur "Learn & Study" : tu guides sans donner la solution complète.

[Énoncé]
{statement}

[Contexte du cours]
{context}

Règles :
- 1 seule question à la fois (Socratic).
- Donne un **indice** puis pose une **question ciblée**.
- Si l’étudiant bloque, propose un sous-objectif plus simple.
- Ne pas dévoiler la solution ; seulement **étapes** et **critères de vérification**.
- Références [p.X].

Réponse (indice + question à l’étudiant) :
""")

# ============ Correcteur d’exercice (copie) ============
EXO_CORRECTOR_PROMPT = ChatPromptTemplate.from_template("""
Corrige la copie d’exercice ci-dessous.

[Énoncé]
{statement}

[Copie de l’étudiant]
{student_answer}

[Contexte du cours]
{context}

Attendus :
- Diagnostic par étapes (correct/incorrect/incomplet).
- Version rédigée correcte.
- Barème indicatif /{points} (répartition claire).
- Références [p.X].
- Conseils ciblés (2–4).

Correction :
""")

# ============ Correcteur d’examen ============
EXAM_CORRECTOR_PROMPT = ChatPromptTemplate.from_template("""
Corrige ce sujet d’examen (copie complète).

[Énoncé(s)]
{statement}

[Copie]
{student_answer}

[Contexte]
{context}

Exigences :
- Barème par exercice et sous-questions → note finale sur {total_points}.
- Tableau récapitulatif (exercice → points obtenus / attendus).
- Remarques globales (forces/faiblesses) + conseils.
- Références [p.X] si possible.

Correction :
""")

# ============ QCM théorie ============
QCM_PROMPT = ChatPromptTemplate.from_template("""
Construit un QCM de théorie sur : "{topic}" (niveau {level}).

[Contexte du cours]
{context}

Spécifications :
- {num_questions} questions.
- Chaque question : 4 propositions (A–D), **une seule** correcte.
- Indiquer ensuite le **corrigé** avec une courte justification.
- Références [p.X] à la fin.

QCM :
""")

# ============ Khôlle (oral) ============
KHOLLE_PROMPT = ChatPromptTemplate.from_template("""
Prépare une khôlle de mathématiques (oral).
Durée : {duration} — Niveau : {level} — Chapitres : {chapters}

[Contexte du cours]
{context}

Attendus :
- Plan minute par minute (accueil, rappel, questions de cours, exercices, conclusion)
- 3–5 **questions de cours** (déf/énoncés démonstrations courtes) avec [p.X]
- 2 **exercices** progressifs (énoncé + attentes orales)
- **Barème oral** (présentation, rigueur, initiative, résultat)
- Questions pièges / relances
- Conseils express pour réussir

Khôlle :
""")
