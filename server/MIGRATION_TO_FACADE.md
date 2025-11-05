# 🔄 Migration vers MathAssistantFacade

Guide de migration du code ancien vers la nouvelle architecture SOLID avec Facade.

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Migration rapide](#migration-rapide)
3. [Avant/Après par cas d'usage](#avantaprès-par-cas-dusage)
4. [Avantages de la migration](#avantages-de-la-migration)
5. [Compatibilité backward](#compatibilité-backward)
6. [Tests après migration](#tests-après-migration)

---

## Vue d'ensemble

### Ancien code (Before)

```python
from before.model.math_course_rag import MathCourseRAG

# Création manuelle avec beaucoup de paramètres
rag = MathCourseRAG(
    pdf_path="model/livre_2011.pdf",
    db_path="./db/chroma_db_math_v3_1",
    collection_name="math_docs",
    embedding_model="bge-m3:latest",
    ollama_model="qwen2.5:14b",
    reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    use_bm25=True,
    use_reranker=True,
    top_k_semantic=10,
    top_k_bm25=10,
    top_k_rerank=6
)

# Appel verbeux
response = rag.query(
    question="C'est quoi une série de Fourier ?",
    chapter="8",
    doc_type="theory"
)
```

### Nouveau code (Phase 4 - Facade)

```python
from src.application.facades import get_assistant

# 1 ligne pour tout créer !
assistant = get_assistant()

# Appel simple
result = assistant.ask("C'est quoi une série de Fourier ?", chapter="8")
```

**Réduction : ~15 lignes → 3 lignes (80% de code en moins)**

---

## Migration rapide

### Étape 1 : Remplacer l'import

```python
# ❌ Ancien
from before.model.math_course_rag import MathCourseRAG

# ✅ Nouveau
from src.application.facades import get_assistant
```

### Étape 2 : Remplacer l'initialisation

```python
# ❌ Ancien
rag = MathCourseRAG(
    pdf_path="...",
    db_path="...",
    # ... 10+ paramètres
)

# ✅ Nouveau
assistant = get_assistant()  # Le DI Container fait tout !
```

### Étape 3 : Adapter les appels de méthodes

Voir la section [Avant/Après](#avantaprès-par-cas-dusage) ci-dessous.

---

## Avant/Après par cas d'usage

### 1. Question & Réponse

#### ❌ Ancien code

```python
response = rag.query(
    question="Qu'est-ce qu'une série de Fourier ?",
    chapter="8",
    doc_type="theory",
    k=6
)

# Accès complexe au résultat
answer_text = response.get("answer", "")
sources = response.get("sources", [])
```

#### ✅ Nouveau code

```python
result = assistant.ask(
    question="Qu'est-ce qu'une série de Fourier ?",
    chapter="8"
)

# Accès simple
answer_text = result["answer"]
sources = result["sources"]
```

---

### 2. Génération d'exercices

#### ❌ Ancien code

```python
response = rag.generate_exercises(
    topic="intégration par parties",
    num_exercises=5,
    difficulty="moyen",
    chapter="6"
)
```

#### ✅ Nouveau code

```python
result = assistant.generate_exercises(
    topic="intégration par parties",
    count=5,  # Paramètre renommé pour cohérence
    difficulty="moyen",
    chapter="6"
)
```

**Changement principal :** `num_exercises` → `count`

---

### 3. Explication de cours

#### ❌ Ancien code

```python
response = rag.explain_course(
    notion="convergence uniforme",
    level="prépa",
    chapter="5"
)
```

#### ✅ Nouveau code

```python
result = assistant.explain_course(
    topic="convergence uniforme",  # Paramètre renommé
    level="prépa",
    chapter="5"
)
```

**Changement principal :** `notion` → `topic`

---

### 4. Génération d'examen

#### ❌ Ancien code

```python
response = rag.generate_exam(
    chapters="5,6,7",
    duration="3h",
    points=100,
    level="prépa"
)
```

#### ✅ Nouveau code

```python
result = assistant.generate_exam(
    chapters="5,6,7",
    duration="3h",
    total_points=100,  # Paramètre renommé
    difficulty="difficile"  # Remplace 'level'
)
```

**Changements :**
- `points` → `total_points`
- `level` → `difficulty`

---

### 5. Correction d'exercice

#### ❌ Ancien code

```python
response = rag.correct_exercise(
    exercise="Calculer ∫ x·sin(x) dx",
    student_answer="Ma solution...",
    chapter="6"
)
```

#### ✅ Nouveau code

```python
result = assistant.correct_exercise(
    exercise_text="Calculer ∫ x·sin(x) dx",  # Paramètre renommé
    student_answer="Ma solution...",
    chapter="6"
)
```

**Changement principal :** `exercise` → `exercise_text`

---

### 6. Explication de théorème

#### ❌ Ancien code

```python
response = rag.explain_theorem(
    theorem_name="théorème de convergence dominée",
    chapter="10"
)
```

#### ✅ Nouveau code

```python
result = assistant.explain_theorem(
    theorem_name="théorème de convergence dominée",
    chapter="10"
)
```

**Aucun changement !** ✅

---

### 7. Génération de QCM

#### ❌ Ancien code

```python
response = rag.generate_qcm(
    topic="séries entières",
    num_questions=10,
    chapter="12"
)
```

#### ✅ Nouveau code

```python
result = assistant.generate_qcm(
    topic="séries entières",
    num_questions=10,
    chapter="12"
)
```

**Aucun changement !** ✅

---

### 8. Création de fiche de révision

#### ❌ Ancien code

```python
response = rag.create_sheet(
    topic="théorème de convergence dominée",
    level="prépa",
    chapter="10"
)
```

#### ✅ Nouveau code

```python
result = assistant.create_sheet(
    topic="théorème de convergence dominée",
    level="prépa",
    chapter="10"
)
```

**Aucun changement !** ✅

---

## Avantages de la migration

### 1. Moins de code

| Aspect | Ancien | Nouveau | Gain |
|--------|--------|---------|------|
| Initialisation | ~15 lignes | 1 ligne | **93%** |
| Appel de méthode | ~5 lignes | 2-3 lignes | **40-50%** |
| Import | 1-2 imports | 1 import | **50%** |

### 2. Moins d'erreurs

#### ❌ Ancien (facile de se tromper)

```python
# Oups, j'ai oublié use_reranker=True
rag = MathCourseRAG(
    pdf_path="...",
    db_path="...",
    # ... beaucoup de paramètres à se rappeler
)
```

#### ✅ Nouveau (configuration automatique)

```python
# Configuration optimale automatique
assistant = get_assistant()
```

### 3. Performance automatique

Le DI Container crée les objets lourds **UNE SEULE FOIS** :

```python
# Ancien : chaque MathCourseRAG() crée son propre vector store (lourd !)
rag1 = MathCourseRAG(...)  # Charge la DB
rag2 = MathCourseRAG(...)  # Re-charge la DB (duplication !)

# Nouveau : singleton automatique
assistant1 = get_assistant()  # Charge la DB
assistant2 = get_assistant()  # Réutilise la même DB (pas de duplication !)
assert assistant1 is assistant2  # True !
```

### 4. Testabilité

```python
# Facile d'injecter des mocks pour les tests
from src.config.di_container import DIContainer

container = DIContainer()
container.register_singleton("llm_provider", MockLLM())
container.register_singleton("retriever", MockRetriever())

assistant = MathAssistantFacade(container)
# Les tests ne touchent pas le vrai LLM ni la vraie DB !
```

### 5. Évolutivité

Ajout de fonctionnalités **sans casser le code existant** :

```python
# Le facade peut évoluer en interne
# Votre code reste identique !
result = assistant.ask("question")  # Fonctionne toujours

# Nouvelles fonctionnalités disponibles instantanément
result = assistant.new_feature(...)  # Ajouté par le maintainer
```

---

## Compatibilité backward

Le facade supporte l'**ancienne API** via `run_task()` :

```python
# Ancien code qui utilisait run_task()
result = assistant.run_task(
    task="qcm",
    question_or_payload="séries entières",
    num_questions=5,
    chapter="12"
)

# Fonctionne toujours ! ✅
```

**Tasks supportées :**
- `"qa"` → `ask()`
- `"explain"` → `explain_course()`
- `"exercises"` → `generate_exercises()`
- `"theorem"` → `explain_theorem()`
- `"qcm"` → `generate_qcm()`
- `"exam"` → `generate_exam()`
- `"sheet"` → `create_sheet()`
- `"formula"` → `explain_formula()`
- `"prove"` → `prove_statement()`

**→ Migration progressive possible !** Vous pouvez migrer une méthode à la fois.

---

## Tests après migration

### Test simple

```python
from src.application.facades import get_assistant

def test_migration():
    """Test que le nouveau code fonctionne"""
    assistant = get_assistant()
    
    # Test Q&A
    result = assistant.ask("Test question", chapter="1")
    assert "answer" in result
    assert "sources" in result
    
    # Test exercices
    result = assistant.generate_exercises("test topic", count=3)
    assert "answer" in result
    
    print("✅ Migration réussie !")

test_migration()
```

### Tests complets

Lancez les tests Phase 4 :

```bash
python3 test_solid_phase4_fast.py
```

**Résultat attendu : 8/8 tests passent**

---

## Récapitulatif

### Checklist de migration

- [ ] Remplacer `from before.model.math_course_rag import MathCourseRAG` par `from src.application.facades import get_assistant`
- [ ] Remplacer `rag = MathCourseRAG(...)` par `assistant = get_assistant()`
- [ ] Adapter les noms de paramètres si nécessaire (voir tableau ci-dessous)
- [ ] Vérifier que `result["answer"]` et `result["sources"]` fonctionnent
- [ ] Lancer les tests

### Tableau de correspondance des paramètres

| Méthode | Ancien paramètre | Nouveau paramètre |
|---------|-----------------|-------------------|
| `generate_exercises()` | `num_exercises` | `count` |
| `explain_course()` | `notion` | `topic` |
| `generate_exam()` | `points` | `total_points` |
| `generate_exam()` | `level` | `difficulty` |
| `correct_exercise()` | `exercise` | `exercise_text` |

### Bénéfices

✅ **-80% de code d'initialisation**  
✅ **-50% de code d'appel**  
✅ **Singletons automatiques** (performance)  
✅ **Configuration centralisée** (maintenabilité)  
✅ **Tests simplifiés** (mock injection)  
✅ **Compatibilité backward** (via `run_task()`)

---

## Besoin d'aide ?

- **Documentation complète :** `PHASE4_COMPLETE.md`
- **Guide de référence :** `QUICK_REFERENCE.md`
- **Exemple :** `example_usage.py`
- **Tests :** `test_solid_phase4_fast.py`

🎉 **Bonne migration !**
