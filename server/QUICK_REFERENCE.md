# 🚀 MathAssistant - Guide de Référence Rapide

## Installation / Démarrage

```python
from src.application.facades import get_assistant

# C'est tout ! Le DI Container fait le reste
assistant = get_assistant()
```

---

## 📚 Toutes les opérations disponibles

### 1. Questions & Réponses (Q&A)

```python
# Question simple
result = assistant.ask("C'est quoi une série de Fourier ?")

# Question avec filtre de chapitre
result = assistant.ask("Expliquez l'intégrale de Riemann", chapter="5")

# Question avec filtre de type
result = assistant.ask("Donnez-moi un théorème", block_types=["theorem"])
```

**Retour :** `{ "answer": str, "sources": List[Document], "metadata": dict }`

---

### 2. Cours (Course)

#### a) Explication de cours

```python
result = assistant.explain_course(
    topic="séries de Fourier",
    chapter="8",
    level="débutant"  # ou "intermédiaire" ou "avancé"
)
```

#### b) Construction de cours complet

```python
result = assistant.build_course(
    topic="intégration de Riemann",
    chapter="5",
    level="intermédiaire"
)
# Retourne : définitions, théorèmes, exemples, exercices
```

#### c) Résumé de cours

```python
result = assistant.summarize_course(
    topic="séries entières",
    chapter="12"
)
# Retourne : points clés, formules essentielles, glossaire, exercices rapides
```

---

### 3. Fiches de révision (Sheets)

#### a) Créer une fiche

```python
result = assistant.create_sheet(
    topic="théorème de convergence dominée",
    chapter="10"
)
# Retourne : fiche structurée avec essentiel, formules, pièges
```

#### b) Réviser une fiche étudiante

```python
result = assistant.review_sheet(
    sheet_text="""
    Ma fiche sur les séries :
    - Critère de d'Alembert
    - ...
    """,
    chapter="11"
)
# Retourne : feedback, erreurs détectées, suggestions
```

---

### 4. Exercices

#### a) Générer des exercices

```python
result = assistant.generate_exercises(
    topic="intégration par parties",
    count=5,
    difficulty="moyen",  # ou "facile" ou "difficile"
    chapter="6"
)
```

#### b) Résoudre un exercice

```python
result = assistant.solve_exercise(
    exercise_text="Calculer ∫ x·sin(x) dx",
    chapter="6"
)
# Retourne : solution détaillée étape par étape
```

#### c) Corriger un exercice

```python
result = assistant.correct_exercise(
    exercise_text="Calculer ∫ x·sin(x) dx",
    student_answer="""
    Ma réponse :
    J'ai utilisé u=x, v'=sin(x)
    Donc u'=1, v=-cos(x)
    ...
    """,
    chapter="6"
)
# Retourne : notation, points forts, points à améliorer, correction détaillée
```

---

### 5. Examens et Évaluations

#### a) Générer un examen

```python
result = assistant.generate_exam(
    chapters="5,6,7",              # Chapitres concernés
    duration="3h",                  # Durée
    total_points=100,               # Total de points
    difficulty="difficile"          # Niveau de difficulté
)
# Retourne : examen complet avec plusieurs exercices, points par question
```

#### b) Corriger un examen

```python
result = assistant.correct_exam(
    exam_text="...",                # Énoncé de l'examen
    student_answers="...",          # Réponses de l'étudiant
    chapter="5,6,7"
)
# Retourne : notation détaillée, barème, feedback par question
```

#### c) Générer un QCM

```python
result = assistant.generate_qcm(
    topic="séries entières",
    num_questions=10,
    chapter="12"
)
# Retourne : QCM avec questions, choix multiples, réponses
```

#### d) Générer une kholle (oral)

```python
result = assistant.generate_kholle(
    topic="espaces vectoriels normés",
    duration="20min",
    chapter="3"
)
# Retourne : questions d'oral, pistes de discussion
```

---

### 6. Théorèmes, Formules, Preuves

#### a) Expliquer un théorème

```python
result = assistant.explain_theorem(
    theorem_name="théorème de convergence dominée",
    chapter="10"
)
# Retourne : énoncé, hypothèses, conséquences, applications
```

#### b) Expliquer une formule

```python
result = assistant.explain_formula(
    formula_name="formule de Stokes",
    chapter="9"
)
# Retourne : formule, conditions d'application, exemples
```

#### c) Prouver un énoncé

```python
result = assistant.prove_statement(
    statement="théorème de Cauchy-Lipschitz",
    chapter="14"
)
# Retourne : preuve rigoureuse, étapes détaillées
```

---

## 🔄 API Backward-Compatible

Si vous avez du vieux code qui utilisait `run_task()`, il fonctionne toujours :

```python
result = assistant.run_task(
    task="qcm",                      # Type de tâche
    question_or_payload="séries entières",
    num_questions=5,
    chapter="12"
)
```

**Tasks disponibles :**
- `"qa"` → ask()
- `"explain"` → explain_course()
- `"exercises"` → generate_exercises()
- `"theorem"` → explain_theorem()
- `"qcm"` → generate_qcm()
- `"exam"` → generate_exam()
- etc.

---

## 📝 Format de retour standard

Toutes les méthodes retournent :

```python
{
    "answer": str,              # Réponse générée par le LLM
    "sources": List[Document],  # Documents sources utilisés
    "metadata": {
        "task": str,            # Type de tâche effectuée
        "chapter": str,         # Chapitre(s) filtré(s)
        "filters": Filters,     # Filtres appliqués
        ...                     # Autres métadonnées spécifiques
    }
}
```

---

## 🎯 Cas d'usage typiques

### Étudiant préparant un examen

```python
assistant = get_assistant()

# 1. Générer une fiche de révision
fiche = assistant.create_sheet("séries de Fourier", chapter="8")

# 2. S'exercer avec des problèmes
exercices = assistant.generate_exercises(
    "séries de Fourier", 
    count=5, 
    difficulty="moyen"
)

# 3. Vérifier sa compréhension avec un QCM
qcm = assistant.generate_qcm("séries de Fourier", num_questions=10)
```

### Professeur créant un contrôle

```python
assistant = get_assistant()

# 1. Générer un examen
exam = assistant.generate_exam(
    chapters="8,9,10",
    duration="2h",
    total_points=100,
    difficulty="moyen"
)

# 2. Corriger les copies
for student_copy in copies:
    correction = assistant.correct_exam(
        exam_text=exam["answer"],
        student_answers=student_copy,
        chapter="8,9,10"
    )
```

### Chercheur explorant un théorème

```python
assistant = get_assistant()

# 1. Comprendre le théorème
explication = assistant.explain_theorem(
    "théorème de Cauchy-Lipschitz",
    chapter="14"
)

# 2. Voir la preuve complète
preuve = assistant.prove_statement(
    "théorème de Cauchy-Lipschitz",
    chapter="14"
)

# 3. Explorer les applications
applications = assistant.ask(
    "Quelles sont les applications du théorème de Cauchy-Lipschitz ?",
    chapter="14"
)
```

---

## 🧰 Gestion de session

```python
# Créer une nouvelle session
assistant.new_session()

# Obtenir l'ID de session actuel
session_id = assistant.get_session_id()
```

---

## 🔧 Troubleshooting

### Problème : "No results found"

**Solution :** Vérifiez les filtres (chapter, block_types)

```python
# ❌ Trop restrictif
result = assistant.ask(
    "série de Fourier",
    chapter="99",  # Ce chapitre n'existe pas !
    block_types=["code"]  # Il n'y a pas de code dans ce cours
)

# ✅ Plus permissif
result = assistant.ask("série de Fourier", chapter="8")
```

### Problème : Réponse trop courte

**Solution :** Soyez plus précis dans votre question

```python
# ❌ Trop vague
result = assistant.ask("Fourier")

# ✅ Plus précis
result = assistant.ask("Expliquez la définition d'une série de Fourier et donnez un exemple")
```

### Problème : Performances lentes

**Solution :** Le DI Container crée les singletons au premier appel
- Premier appel : lent (charge vector store, LLM, etc.)
- Appels suivants : rapides (réutilisation des singletons)

---

## 📚 Ressources

- **Documentation complète** : `PHASE4_COMPLETE.md`
- **Architecture** : `README_REFACTORED.md`
- **Exemple détaillé** : `example_usage.py`
- **Tests** : `test_solid_phase4_fast.py`

---

## 🎉 En résumé

**1 ligne pour tout faire :**

```python
assistant = get_assistant()
```

**16 use cases, 17 méthodes, 0 configuration manuelle !**

Le DI Container gère automatiquement :
- ✅ Retriever (BM25 + Vector + Reranker)
- ✅ LLM Provider (avec fallback)
- ✅ Router (intent detection)
- ✅ Prompts (17 prompts spécialisés)
- ✅ Tous les use cases

**Vous n'avez qu'à appeler les méthodes !** 🚀
