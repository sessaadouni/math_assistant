# Amélioration des Prompts de Cours

## 📋 Vue d'ensemble

Séparation claire entre **mini-cours pédagogique** et **cours complet exhaustif**.

---

## 🎯 Objectifs

### Avant
- `course_explain` et `course_build` étaient trop similaires
- Manque de structure rigoureuse
- Pas de distinction pédagogique claire

### Après
- ✅ **Séparation nette** : mini-cours vs cours complet
- ✅ **Structure enrichie** inspirée de ChatGPT-5 thinking
- ✅ **Double piste** : CPGE-preuve + Appli-ingénieur
- ✅ **Pédagogie explicite** avec checkpoints

---

## 📚 Les Deux Types de Cours

### 1. `course_explain` — Mini-cours rapide (10-15min)

**Usage**: Explication rapide et accessible d'une notion

**Caractéristiques**:
- ⏱️ Lecture rapide (10-15 minutes)
- 🎓 Pédagogique et accessible
- 🎯 Focus sur l'essentiel
- 💡 Intuition avant rigueur
- ❓ FAQ intégrée

**Structure**:
```
1. L'essentiel en 3 phrases
2. Définitions clés (indispensables uniquement)
3. Propriétés principales (top 3-4)
4. Méthode type (1 algorithme clé + exemple)
5. Mini-FAQ (3-5 questions courantes)
6. Formules à retenir (top 5-7)
7. Pour aller plus loin
```

**Exemple d'utilisation**:
```python
assistant = MathAssistantFacade()
result = assistant.explain_course(
    topic="convergence uniforme",
    level="prépa",
    chapter="5"
)
```

---

### 2. `course_build` — Cours complet exhaustif

**Usage**: Traitement rigoureux et complet d'une notion (style "manuel de référence")

**Caractéristiques**:
- 📖 Exhaustif et rigoureux
- 🔬 Double piste : **CPGE-preuve** + **Appli-ingénieur**
- 🎯 Preuves (esquisses) + méthodes pratiques
- 📝 Exercices détaillés avec corrections pas à pas
- ⚠️ Contre-exemples et pièges

**Structure enrichie**:
```
1. Introduction / plan
   - Objectifs pédagogiques
   - Plan détaillé
   - Prérequis

2. Définitions + notations
   - Définitions formelles (ε-δ si pertinent)
   - Notations standards
   - Domaines et conditions

3. Propriétés / théorèmes
   - Énoncés PRÉCIS avec hypothèses
   - Piste CPGE: Esquisses de preuves
   - Piste Ingé: Critères pratiques

4. Méthodes / algorithmes
   - Piste CPGE: Justifications théoriques
   - Piste Ingé: Checklists étape par étape
   - Organigrammes décisionnels
   - Pièges fréquents

5. Exemples canoniques + contre-exemples
   - 3-4 exemples DÉTAILLÉS
   - 2-3 contre-exemples pathologiques
   - Progression simple → complexe

6. Exercices (5-6 minimum)
   - Énoncé + difficulté
   - Indices progressifs
   - Correction PAS À PAS
   - Points de vigilance

7. Formules clés
   - Toutes les formules en LaTeX
   - Conditions d'application
   - Liens entre formules

8. Références [p.X]
   - Citations précises
   - Bibliographie

9. Mini-révision interactive
   - Questions de compréhension
   - Checkpoints auto-évaluation
```

**Exemple d'utilisation**:
```python
assistant = MathAssistantFacade()
result = assistant.build_course(
    topic="fonctions à plusieurs variables",
    level="L2-L3/CPGE",
    chapter="10"
)
```

---

## 🎨 Inspiration ChatGPT-5 Thinking

### Éléments intégrés

1. **Double piste pédagogique**
   - CPGE : rigueur, preuves, formalisme
   - Ingénieur : procédures, heuristiques, erreurs courantes

2. **Structure progressive**
   ```
   Intuition → Définition formelle → Propriétés → Méthodes → Exemples
   ```

3. **Exercices avec pédagogie explicite**
   - Indices progressifs
   - Corrections détaillées avec "Pourquoi cette étape ?"
   - Variantes et généralisations

4. **Mini-révision interactive**
   - Questions checkpoint
   - Auto-évaluation
   - Suggestions de révision ciblées

5. **Formules en contexte**
   - Pas juste une liste
   - Conditions d'application
   - Liens et dérivations

---

## 🔄 Changements dans le Code

### Fichiers modifiés

1. **`src/prompts/course/__init__.py`**
   - `CourseBuildPrompt` : Prompt enrichi (double piste)
   - `CourseExplainPrompt` : Prompt optimisé (mini-cours)

### Compatibilité

✅ **Rétrocompatibilité totale**
- L'API du facade reste identique
- Pas de changement dans les use cases
- Seuls les prompts sont améliorés

---

## 🧪 Tests

### Script de test
```bash
python test_course_prompts.py
```

### Tests inclus
1. Mini-cours (explain_course)
2. Cours complet (build_course)
3. Comparaison des deux approches

---

## 📊 Résultats Attendus

### Longueur

| Type | Longueur attendue | Ratio |
|------|------------------|-------|
| `explain_course` | 2 000 - 4 000 chars | 1x |
| `build_course` | 8 000 - 15 000 chars | 3-5x |

### Qualité

**Mini-cours (explain)**:
- ✅ Accessible et motivant
- ✅ Lecture rapide
- ✅ FAQ intégrée
- ✅ Focus essentiel

**Cours complet (build)**:
- ✅ Exhaustif et rigoureux
- ✅ Double piste CPGE/Ingé
- ✅ Preuves + méthodes
- ✅ Exercices détaillés
- ✅ Contre-exemples

---

## 🎯 Cas d'Usage

### Quand utiliser `explain_course` ?
- 👨‍🎓 Découverte rapide d'une notion
- ⏰ Révision express avant un DS
- 🆘 Besoin de clarification pédagogique
- 🔍 Vue d'ensemble avant approfondissement

### Quand utiliser `build_course` ?
- 📚 Apprentissage approfondi
- 🎓 Préparation examen/concours
- 🔬 Besoin de rigueur et preuves
- 📝 Travail sur exercices variés
- 🏗️ Construction solide des fondations

---

## 🚀 Exemples Concrets

### Exemple 1: Étudiant en découverte
```python
# Découvrir rapidement une notion
result = assistant.explain_course(
    topic="séries entières",
    level="prépa",
    chapter="9"
)
# → Mini-cours 10-15min, FAQ, formules essentielles
```

### Exemple 2: Préparation concours
```python
# Approfondir pour concours
result = assistant.build_course(
    topic="séries entières",
    level="prépa",
    chapter="9"
)
# → Cours exhaustif, preuves, exercices détaillés
```

### Exemple 3: Flow pédagogique optimal
```python
# 1. Découverte (mini-cours)
mini = assistant.explain_course(topic="intégrales à paramètre")

# 2. Approfondissement (cours complet)
complet = assistant.build_course(topic="intégrales à paramètre")

# 3. Exercices ciblés
exos = assistant.generate_exercises(topic="intégrales à paramètre", count=5)
```

---

## 📝 Notes de Développement

### Contraintes respectées
- ✅ Pas d'hallucination (contexte insuffisant → explicite)
- ✅ Références [p.X] systématiques
- ✅ LaTeX pour toutes les formules
- ✅ Style clair et progressif

### Améliorations futures possibles
- [ ] Mode "ultra-rapide" (5min, flashcard style)
- [ ] Mode "recherche" (focus preuves complètes)
- [ ] Génération de mindmaps textuelles
- [ ] Liens interactifs entre notions

---

## 🔗 Liens avec l'Architecture

### Use Cases concernés
- `ExplainCourseUseCase` → `course_explain` prompt
- `BuildCourseUseCase` → `course_build` prompt

### Facade
- `MathAssistantFacade.explain_course()` → Mini-cours
- `MathAssistantFacade.build_course()` → Cours complet

### Principe SOLID respecté
- **Single Responsibility**: Chaque prompt a un rôle précis
- **Open/Closed**: Extension sans modification (nouveaux prompts)
- **Dependency Inversion**: Prompts injectés via registry

---

## ✅ Checklist de Migration

Pour les utilisateurs existants:

- [x] Prompts améliorés
- [x] Rétrocompatibilité garantie
- [x] Tests fournis
- [x] Documentation complète
- [ ] Migration des anciens appels (si nécessaire)

### Pas d'action requise si:
- Vous utilisez déjà `MathAssistantFacade`
- Vous appelez `explain_course()` ou `build_course()`
- → Les prompts améliorés sont automatiquement utilisés !

---

## 📚 Références

**Inspiration**:
- Exemple ChatGPT-5 thinking (mode study & learn)
- Structure "fonctions à plusieurs variables"
- Double piste CPGE + Ingénieur

**Documentation liée**:
- `ARCHITECTURE_SOLID_PROPOSAL.md`
- `MIGRATION_TO_FACADE.md`
- `QUICK_REFERENCE.md`

---

*Dernière mise à jour: 2025-11-06*
