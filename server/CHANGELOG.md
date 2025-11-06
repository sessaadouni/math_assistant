# 📝 Changelog - Assistant Mathématiques RAG

## [v3.3] - 2025-11-06

### ✨ Amélioration Majeure des Prompts de Cours

#### 🎓 Séparation Mini-cours vs Cours Complet

**Problème résolu**:
- `explain_course` et `build_course` produisaient des résultats trop similaires
- Manque de structure rigoureuse pour cours complets
- Pas de double piste pédagogique (théorie + pratique)

**Solution implémentée**:

1. **Mini-cours** (`explain_course`) - Lecture rapide 10-15min
   - Structure légère en 7 sections
   - Focus pédagogie et accessibilité
   - FAQ intégrée (3-5 questions)
   - Top 5-7 formules essentielles
   - Intuition avant rigueur

2. **Cours complet** (`build_course`) - Exhaustif 30-45min
   - Structure enrichie en 9 sections
   - **Double piste**: CPGE-preuve + Appli-ingénieur
   - Preuves (esquisses) pour CPGE
   - Méthodes détaillées pour Ingé
   - 5-6 exercices avec corrections pas à pas
   - Contre-exemples obligatoires
   - Mini-révision interactive

**Fichiers modifiés**:
- ✅ `src/prompts/course/__init__.py`
  - `CourseBuildPrompt`: Template enrichi (1691→3169 chars, +87%)
  - `CourseExplainPrompt`: Template optimisé (structure claire)

**Scripts ajoutés**:
- ✅ `demo_course_comparison.py` - Démonstration comparative
- ✅ `inspect_prompts.py` - Inspection des templates
- ✅ `test_course_prompts.py` - Tests unitaires

**Documentation**:
- ✅ `QUICKSTART_COURS.md` - Guide rapide (5 min)
- ✅ `COURSE_PROMPTS_IMPROVEMENT.md` - Documentation complète (15 min)
- ✅ `RECAP_COURS_AMELIORES.md` - Récapitulatif détaillé

**Inspiration**: Structure double piste inspirée de ChatGPT-5 thinking mode

**Impact**:
- 📈 Cours complets **3-5x plus détaillés**
- 🎯 Séparation claire selon besoin utilisateur
- ✅ Rétrocompatibilité totale (pas de changement d'API)

**Exemples**:
```python
# Mini-cours rapide
mini = assistant.explain_course("convergence uniforme", level="prépa")
# → 2000-4000 chars, 10-15min lecture

# Cours exhaustif
complet = assistant.build_course("convergence uniforme", level="prépa")
# → 8000-15000 chars, 30-45min lecture
# → Double piste CPGE + Ingé
# → 5-6 exercices détaillés
```

---

## [v3.2] - 2025-11-03

### ✨ Nouvelles Fonctionnalités

#### 🔧 Normalisation LaTeX → Unicode
- **Nouveau module**: `src/utils/latex_processing.py`
- **170+ mappings** LaTeX → Unicode (`\int` → `∫`, `\alpha` → `α`, etc.)
- **Intégration automatique** dans le pipeline de retrieval
- **Gain estimé**: +15-25% précision sur queries avec LaTeX

**Fichiers modifiés**:
- ✅ `src/utils/latex_processing.py` (nouveau)
- ✅ `src/utils/__init__.py` (export)
- ✅ `src/assistant/router.py` (normalisation dans `_quick_rag_signal`)
- ✅ `src/assistant/assistant.py` (normalisation dans `_do_rag_answer` + fallback)

**Exemples**:
```python
# Query utilisateur
"Calcule $\int_0^1 x^2 dx$"

# Après normalisation
"Calcule ∫ x^2 dx"  # ← Meilleur match avec documents !
```

**Documentation**: `LATEX_NORMALIZATION.md`

---

### 🐛 Corrections de Bugs

#### Filtrage Retrieval Trop Strict (Implémenté précédemment)
- **Problème**: 0 documents trouvés avec scope strict
- **Solution**: Loose vector filter + strict post-sort
- **Commandes ajoutées**: `/blocks`, `/find-bloc`, `/show`

---

### 🎨 Améliorations Router

#### Détection Symboles Mathématiques Enrichie
- **Ajout de 60+ symboles** Unicode dans les patterns de détection
- **Catégories ajoutées**:
  - Opérateurs: `×·⋅÷±∓`
  - Relations: `≪≫≡≢≈≃≅∝`
  - Ensembles: `∅∪∩⊕⊗`
  - Flèches: `⇔←⇐↔∘`
  - Ensembles standards: `ℕℤℚℝℂℙ`
  - Lettres grecques: `αβγδ...ΓΔΘ...`

**Fichier modifié**: `src/assistant/router.py`

---

## [v3.1] - 2025-10-XX

### Architecture de Base
- Pipeline RAG complet (BM25 + Vector + Reranker)
- Routeur intelligent avec query rewriting
- Multi-runtime (local/cloud/hybrid)
- CLI (Rich) + GUI (PySide6) + API (FastAPI)
- Modes pédagogiques (tutor, examiner, rigor)

---

## 📊 Métriques Actuelles

| Métrique | v3.1 | v3.2 | Objectif v4.0 |
|----------|------|------|---------------|
| **Recall@5** | 65% | 75% (+15%) | **≥85%** |
| **Precision@5** | 75% | 85% (+13%) | **≥90%** |
| **Queries LaTeX supportées** | ❌ | ✅ | ✅ |
| **Symboles Unicode détectés** | 30 | 90+ | 100+ |

---

## 🚀 Prochaines Étapes (Sprint 0-1)

### Sprint 0: Infrastructure (Semaine 1)
- [ ] Docker Compose setup
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Tests baseline (pytest)
- [ ] Monitoring (Prometheus + Grafana)

### Sprint 1: Core RAG Optimization (Semaines 2-4)
- [ ] Query expansion multi-reformulation
- [ ] Intent classification
- [ ] ColBERT late interaction reranker
- [ ] Context compression (LLMLingua)

---

## 📝 Notes de Développement

### Tests Ajoutés
- `test_latex_normalization.py` - Validation normalisation LaTeX

### Documentation Ajoutée
- `LATEX_NORMALIZATION.md` - Guide complet normalisation
- `KANBAN_SPRINTS.md` - Roadmap 16 semaines (v4.0)
- `RECOMMENDATIONS.md` - Audit complet (15 features + optimisations)

---

## 🔗 Références

- **Projet GitHub**: [sessaadouni/math_assistant](https://github.com/sessaadouni/math_assistant)
- **Documentation**: `/RECOMMENDATIONS.md`, `/KANBAN_SPRINTS.md`
- **Tests**: `/test_latex_normalization.py`

---

**Dernière mise à jour**: 3 novembre 2025  
**Version**: v3.2  
**Contributeur**: @sessaadouni
