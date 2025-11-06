# 🎓 Guide Rapide: Cours améliorés

## ✅ Ce qui a été fait

### 1. Séparation claire des prompts

| Fonction | Type | Objectif | Temps lecture |
|----------|------|----------|---------------|
| `explain_course` | Mini-cours | Pédagogique, rapide | 10-15min |
| `build_course` | Cours complet | Exhaustif, rigoureux | 30-45min |

### 2. Structure inspirée ChatGPT-5

**Mini-cours** (`explain_course`):
```
1. L'essentiel en 3 phrases
2. Définitions clés
3. Propriétés principales (top 3-4)
4. Méthode type + exemple
5. Mini-FAQ (3-5 questions)
6. Formules à retenir
7. Pour aller plus loin
```

**Cours complet** (`build_course`):
```
1. Introduction / plan détaillé
2. Définitions + notations formelles
3. Propriétés / théorèmes (CPGE + Ingé)
4. Méthodes / algorithmes (double piste)
5. Exemples + contre-exemples (3-4 + 2-3)
6. Exercices (5-6 avec corrections détaillées)
7. Formules clés en contexte
8. Références [p.X]
9. Mini-révision interactive
```

---

## 🚀 Utilisation

### Exemple 1: Mini-cours rapide
```python
from src.application.facades.math_assistant_facade import MathAssistantFacade

assistant = MathAssistantFacade()

# Explication rapide et pédagogique
result = assistant.explain_course(
    topic="séries de Fourier",
    level="prépa",
    chapter="8"
)

print(result["answer"])
```

### Exemple 2: Cours complet exhaustif
```python
# Cours rigoureux avec double piste CPGE + Ingé
result = assistant.build_course(
    topic="séries de Fourier",
    level="prépa",
    chapter="8"
)

print(result["answer"])
```

### Exemple 3: Flow pédagogique optimal
```python
# 1. Découverte (mini-cours)
mini = assistant.explain_course(topic="intégrales à paramètre")

# 2. Approfondissement (cours complet)
complet = assistant.build_course(topic="intégrales à paramètre")

# 3. Pratique (exercices)
exos = assistant.generate_exercises(
    topic="intégrales à paramètre",
    count=5,
    difficulty="mixte"
)
```

---

## 🧪 Tests

### Test rapide
```bash
cd /home/se/test_ollama_rag/server

# Vérifier les imports
python3 -c "from src.prompts.course import CourseBuildPrompt, CourseExplainPrompt; print('✅ OK')"
```

### Démonstration complète
```bash
# Comparaison mini-cours vs cours complet
python3 demo_course_comparison.py
```

### Tests unitaires
```bash
# Tests automatisés
python3 test_course_prompts.py
```

---

## 📊 Différences attendues

### Longueur
- **Mini-cours**: 2 000 - 4 000 caractères
- **Cours complet**: 8 000 - 15 000 caractères
- **Ratio**: 3-5x

### Contenu

| Élément | Mini-cours | Cours complet |
|---------|------------|---------------|
| Preuves | ❌ Non | ✅ Esquisses |
| Exercices | 0-1 | 5-6 détaillés |
| Exemples | 1 représentatif | 3-4 + contre-exemples |
| FAQ | ✅ Oui (3-5) | ❌ Non (dans révision) |
| Formules | Top 5-7 | Toutes + contexte |
| Double piste | ❌ Non | ✅ CPGE + Ingé |

---

## 🎯 Quand utiliser quoi ?

### `explain_course` (mini-cours) ✨
- ✅ Première découverte d'une notion
- ✅ Révision express avant un DS/exam
- ✅ Besoin de clarification rapide
- ✅ Vue d'ensemble avant approfondissement
- ✅ Manque de temps

### `build_course` (cours complet) 📚
- ✅ Apprentissage approfondi
- ✅ Préparation concours/exam important
- ✅ Besoin de rigueur et preuves
- ✅ Travail sur exercices variés
- ✅ Construction solide des fondations
- ✅ Révision exhaustive

---

## 📝 Fichiers modifiés

```
src/prompts/course/__init__.py
  ├─ CourseBuildPrompt    → Enrichi (double piste)
  └─ CourseExplainPrompt  → Optimisé (mini-cours)

✅ Rétrocompatibilité: TOTALE (pas de changement d'API)
```

---

## 🔍 Vérification rapide

```python
# Vérifier que tout fonctionne
from src.application.facades.math_assistant_facade import MathAssistantFacade

assistant = MathAssistantFacade()

# Mini-cours
mini = assistant.explain_course("convergence uniforme", level="prépa")
print(f"Mini-cours: {len(mini['answer'])} chars")

# Cours complet
complet = assistant.build_course("convergence uniforme", level="prépa")
print(f"Cours complet: {len(complet['answer'])} chars")

# Le cours complet doit être ~3-5x plus long
ratio = len(complet['answer']) / len(mini['answer'])
print(f"Ratio: {ratio:.1f}x")
assert ratio >= 2.0, "Le cours complet devrait être plus détaillé"
print("✅ Tout fonctionne !")
```

---

## 📚 Documentation complète

Voir `COURSE_PROMPTS_IMPROVEMENT.md` pour:
- Structure détaillée des prompts
- Inspiration ChatGPT-5
- Cas d'usage avancés
- Architecture SOLID

---

## ✅ Checklist

- [x] Prompts améliorés
- [x] Séparation mini-cours / cours complet
- [x] Structure enrichie (9 sections)
- [x] Double piste CPGE + Ingénieur
- [x] Tests fournis
- [x] Documentation complète
- [x] Rétrocompatibilité garantie

---

**Prêt à utiliser ! 🚀**

Les nouveaux prompts sont automatiquement utilisés via `MathAssistantFacade`.
Aucune migration nécessaire pour le code existant.
