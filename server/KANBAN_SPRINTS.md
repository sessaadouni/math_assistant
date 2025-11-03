# 📋 KANBAN & ROADMAP - Assistant Mathématiques RAG

> **Projet**: Math Assistant RAG v3.1 → v4.0  
> **Date de début**: 3 novembre 2025  
> **Durée totale estimée**: 16 semaines (4 sprints majeurs)  
> **Méthodologie**: Agile avec sprints de 2-4 semaines

---

## 🎯 Vue d'Ensemble des Sprints

| Sprint | Durée | Focus Principal | Objectif |
|--------|-------|-----------------|----------|
| **Sprint 0** | 1 semaine | Setup & Infrastructure | Préparer l'environnement de développement |
| **Sprint 1** | 3 semaines | Core RAG Optimization | Maximiser la qualité du retrieval |
| **Sprint 2** | 4 semaines | Features Pédagogiques | Modes tuteur, vérification, citations |
| **Sprint 3** | 4 semaines | UX & Productivité | Historique, cache, exports, analytics |
| **Sprint 4** | 3 semaines | Qualité & Production | Tests, monitoring, déploiement |
| **Sprint 5** | 1 semaine | Polish & Documentation | Cleanup, docs, release notes |

**Total**: 16 semaines = 4 mois

---

## 📊 KANBAN BOARD

### 🔴 BACKLOG (Non Priorisé)

- [ ] Mode collaboratif / partage de sessions
- [ ] Assistant vocal (speech-to-text)
- [ ] Intégration multimédia (vidéos, animations)
- [ ] Système de plugins / extensions
- [ ] Support multi-langue (EN, FR, ES)
- [ ] Mobile app (React Native)
- [ ] Gamification (badges, achievements)
- [ ] Mode hors-ligne complet
- [ ] Integration Jupyter notebooks
- [ ] Export Anki/Quizlet automatique

---

### 🟡 TODO (Priorisé par Sprint)

#### Sprint 0: Setup & Infrastructure (Semaine 1)
**Objectif**: Préparer l'environnement de développement

- [ ] **S0.1** Mise en place environnement de dev
  - [ ] Config Git branches (dev, staging, main)
  - [ ] Pre-commit hooks (black, mypy, ruff)
  - [ ] CI/CD pipeline (GitHub Actions)
  - [ ] Docker Compose pour dev local
  
- [ ] **S0.2** Infrastructure de tests
  - [ ] Framework pytest + coverage
  - [ ] Tests unitaires baseline (router, chunking)
  - [ ] Tests d'intégration RAG
  - [ ] Fixtures & mocks
  
- [ ] **S0.3** Monitoring & Observabilité
  - [ ] OpenTelemetry setup
  - [ ] Prometheus metrics
  - [ ] Grafana dashboards
  - [ ] Structured logging (structlog)
  
- [ ] **S0.4** Documentation technique
  - [ ] Architecture Decision Records (ADR)
  - [ ] Setup CONTRIBUTING.md
  - [ ] API documentation (OpenAPI)

**Livrables**:
- ✅ Environnement dev reproductible
- ✅ Pipeline CI/CD fonctionnel
- ✅ Baseline tests (>60% coverage)
- ✅ Dashboards monitoring

**Critères de succès**:
- Build vert sur CI
- Tests passent localement et en CI
- Metrics visibles dans Grafana

---

#### Sprint 1: Core RAG Optimization (Semaines 2-4)
**Objectif**: Maximiser qualité retrieval et génération

##### Week 1: Query Understanding
- [ ] **S1.1** Query Expansion Multi-Reformulation
  - [ ] Classe `QueryExpander` 
  - [ ] Génération 3-5 reformulations
  - [ ] Parallel retrieval + RRF fusion
  - [ ] Tests A/B sur dataset eval
  
- [ ] **S1.2** Intent Classification
  - [ ] Classe `IntentClassifier`
  - [ ] Mapping intent → filtres adaptatifs
  - [ ] Integration dans router
  - [ ] Métriques intent accuracy

##### Week 2: Hybrid Retrieval Avancé
- [ ] **S1.3** Adaptive Fusion Weights
  - [ ] `AdaptiveHybridRetriever` class
  - [ ] Détection query technique vs sémantique
  - [ ] Poids BM25/Vector dynamiques
  - [ ] Eval précision vs baseline
  
- [ ] **S1.4** ColBERT Late Interaction
  - [ ] Installation colbert-ai
  - [ ] Classe `ColBERTReranker`
  - [ ] Token-level interactions
  - [ ] Benchmark vs CrossEncoder

##### Week 3: Context Optimization
- [ ] **S1.5** Relevance Filtering Dynamique
  - [ ] Classe `RelevanceFilter`
  - [ ] Cut-off adaptatif (min 2, max 8 docs)
  - [ ] Score threshold tuning
  
- [ ] **S1.6** Context Compression (LLMLingua)
  - [ ] Installation llmlingua
  - [ ] Classe `ContextCompressor`
  - [ ] Compression ratio 0.5-0.7
  - [ ] Tests latence vs qualité

**Livrables**:
- ✅ Query expansion fonctionnel (+20% rappel)
- ✅ Intent classification (85%+ accuracy)
- ✅ Hybrid retrieval optimisé
- ✅ ColBERT reranker intégré
- ✅ Context compression

**Critères de succès**:
- Rappel@5: >85% (vs 65% baseline)
- Précision@5: >90% (vs 75% baseline)
- Latence retrieval: <500ms p95

---

#### Sprint 2: Features Pédagogiques (Semaines 5-8)
**Objectif**: Enrichir expérience pédagogique

##### Week 1: Vérification Symbolique
- [ ] **S2.1** SymPy Verification Engine
  - [ ] Classe `SymbolicVerifier`
  - [ ] Parsing LaTeX → SymPy
  - [ ] Vérif dérivées/intégrales/limites
  - [ ] Cas de test mathématiques
  
- [ ] **S2.2** Contradiction Detection
  - [ ] Classe `ContradictionChecker`
  - [ ] NLI model (deberta-v3-base-mnli)
  - [ ] Score entailment/contradiction
  - [ ] Alertes utilisateur

##### Week 2: Citations Ancrées
- [ ] **S2.3** Citation System
  - [ ] Extraction page + offset précis
  - [ ] Classe `CitationManager`
  - [ ] Format: [Page X, §Y, ligne Z]
  - [ ] GUI: liens cliquables → PDF
  
- [ ] **S2.4** Source Validation
  - [ ] Vérif claims vs source
  - [ ] Score confidence par affirmation
  - [ ] Highlight zones pertinentes PDF

##### Week 3: Windowed RAG
- [ ] **S2.5** Dynamic Context Windowing
  - [ ] Classe `WindowedRetriever`
  - [ ] Chunks adjacents (±1, ±2)
  - [ ] Config window_size dynamique
  - [ ] Tests contexte enrichi
  
- [ ] **S2.6** Hierarchical Retrieval
  - [ ] Stage 1: BM25 sur chapitres
  - [ ] Stage 2: Vector sur chunks filtrés
  - [ ] Classe `HierarchicalRetriever`

##### Week 4: Modes Pédagogiques
- [ ] **S2.7** Pedagogy Modes Implementation
  - [ ] Mode Socratique (questions guidées)
  - [ ] Mode Examiner (éval sans aide)
  - [ ] Mode Rigor (preuve formelle)
  - [ ] Mode Casual (vulgarisation)
  
- [ ] **S2.8** Pack Révision Auto-Généré
  - [ ] Génération fiches synthèse
  - [ ] Extraction théorèmes clés
  - [ ] Exercices types + corrigés
  - [ ] Export PDF formaté LaTeX

**Livrables**:
- ✅ Vérification SymPy fonctionnelle
- ✅ Citations ancrées précises
- ✅ Windowed RAG (+15% contexte pertinent)
- ✅ 4 modes pédagogiques opérationnels
- ✅ Pack révision par chapitre

**Critères de succès**:
- SymPy: 90%+ formules vérifiées
- Citations: 100% traçables
- Modes péda: Tests utilisateurs positifs

---

#### Sprint 3: UX & Productivité (Semaines 9-12)
**Objectif**: Améliorer expérience utilisateur quotidienne

##### Week 1: Cache & Performance
- [ ] **S3.1** Semantic Cache
  - [ ] Classe `SemanticCache`
  - [ ] Similarité embeddings (threshold 0.95)
  - [ ] TTL configurable (24h default)
  - [ ] Metrics hit rate
  
- [ ] **S3.2** Response Streaming Optimisé
  - [ ] Chunked generation (SSE)
  - [ ] Progressive rendering GUI
  - [ ] Time-to-first-token < 500ms

##### Week 2: Historique Persistant
- [ ] **S3.3** Conversation History DB
  - [ ] SQLite schema (conversations, turns)
  - [ ] Classe `ConversationHistory`
  - [ ] FTS5 full-text search
  - [ ] Migration existant logs
  
- [ ] **S3.4** History Commands & GUI
  - [ ] CLI: `/history search|list|resume`
  - [ ] GUI: Sidebar conversations
  - [ ] Filtres: date, chapitre, rating
  - [ ] Export conversation (MD, JSON)

##### Week 3: Export & Documents
- [ ] **S3.5** Document Generator
  - [ ] Classe `DocumentGenerator`
  - [ ] Templates LaTeX professionnels
  - [ ] Export poly cours complet
  - [ ] Génération sujets examen
  
- [ ] **S3.6** Export Endpoints
  - [ ] API: `/export/course`, `/export/flashcards`
  - [ ] CLI: `/export cours|flashcards|mindmap`
  - [ ] Formats: PDF, LaTeX, MD, Anki

##### Week 4: Feedback & Analytics
- [ ] **S3.7** Feedback System
  - [ ] Classe `FeedbackSystem`
  - [ ] Rating 1-5 étoiles par réponse
  - [ ] Report issues (hallucination, erreur)
  - [ ] GUI: boutons 👍/👎
  
- [ ] **S3.8** Student Analytics
  - [ ] Classe `StudentAnalytics`
  - [ ] Tracking chapitres maîtrisés
  - [ ] Points forts / faibles
  - [ ] Dashboard progression GUI

**Livrables**:
- ✅ Cache sémantique (hit rate 40%+)
- ✅ Historique persistant + search FTS
- ✅ Exports documents pro (PDF, LaTeX)
- ✅ Système feedback complet
- ✅ Analytics étudiant

**Critères de succès**:
- Cache: 40%+ hit rate sur queries répétées
- History search: <100ms latence
- Export PDF: qualité publication
- Feedback: collecte sur 100% réponses

---

#### Sprint 4: Qualité & Production (Semaines 13-15)
**Objectif**: Production-ready avec monitoring

##### Week 1: Tests & Évaluation
- [ ] **S4.1** RAGAS Evaluation Pipeline
  - [ ] Classe `RAGEvaluator`
  - [ ] Métriques: faithfulness, answer_relevancy, context_recall
  - [ ] Dataset golden questions (50+)
  - [ ] CI: éval automatique sur PR
  
- [ ] **S4.2** Tests Unitaires Complets
  - [ ] Coverage >80% (pytest-cov)
  - [ ] Tests router, retriever, chunking
  - [ ] Tests modes pédagogiques
  - [ ] Tests regression

##### Week 2: Robustesse & Sécurité
- [ ] **S4.3** LaTeX Guardrails
  - [ ] Sanitization (whitelist commands)
  - [ ] Max length (100KB)
  - [ ] Timeout compilation (5s)
  - [ ] Tests injection
  
- [ ] **S4.4** Error Handling & Resilience
  - [ ] Retry logic (exponential backoff)
  - [ ] Circuit breaker pattern
  - [ ] Graceful degradation
  - [ ] Health checks endpoints

##### Week 3: Monitoring & Ops
- [ ] **S4.5** Production Monitoring
  - [ ] Prometheus metrics export
  - [ ] Grafana dashboards finaux
  - [ ] Alerting (PagerDuty/Slack)
  - [ ] SLO/SLI définition
  
- [ ] **S4.6** Versioning & Index Management
  - [ ] Classe `IndexVersion`
  - [ ] Manifeste version (schema, config, model)
  - [ ] Migration assistant
  - [ ] Rollback capability
  
- [ ] **S4.7** Performance Optimization
  - [ ] Profiling (cProfile, py-spy)
  - [ ] Bottlenecks identification
  - [ ] Optimizations ciblées
  - [ ] Load testing (Locust)

**Livrables**:
- ✅ RAGAS eval pipeline
- ✅ Coverage tests >80%
- ✅ LaTeX guardrails robustes
- ✅ Monitoring production complet
- ✅ Versioning index

**Critères de succès**:
- RAGAS faithfulness >0.85
- Tests: 80%+ coverage, 0 failing
- Latence p95: <1s end-to-end
- Monitoring: 100% endpoints tracés

---

#### Sprint 5: Polish & Release (Semaine 16)
**Objectif**: Finalisation et lancement v4.0

- [ ] **S5.1** Documentation Finale
  - [ ] User guide complet (FR/EN)
  - [ ] Developer docs (API, architecture)
  - [ ] Migration guide v3→v4
  - [ ] Video tutorials
  
- [ ] **S5.2** Code Cleanup
  - [ ] Refactoring debt
  - [ ] Type hints 100%
  - [ ] Docstrings complètes
  - [ ] Code review final
  
- [ ] **S5.3** Release Preparation
  - [ ] CHANGELOG.md détaillé
  - [ ] Release notes (features, breaking changes)
  - [ ] Semantic versioning (v4.0.0)
  - [ ] GitHub release + tags
  
- [ ] **S5.4** Déploiement Production
  - [ ] Staging deployment + smoke tests
  - [ ] Production deployment
  - [ ] Rollout progressif (canary)
  - [ ] Post-launch monitoring

**Livrables**:
- ✅ Documentation complète
- ✅ Code clean + typed
- ✅ Release v4.0.0 publiée
- ✅ Production stable

---

### 🟢 IN PROGRESS

> **Instructions**: Maximum 3 tâches en parallèle par personne

_Actuellement vide - démarrage Sprint 0_

---

### 🔵 IN REVIEW

> **Instructions**: Code review + tests avant merge

_Actuellement vide_

---

### ✅ DONE

#### Améliorations Récentes (Pré-Sprint 0)
- [x] **Filtering Bug Fix** (Implémenté 03/11/2025)
  - [x] HybridRetriever: loose vector filter + strict post-sort
  - [x] Fallback loose retrieval in `_do_rag_answer`
  - [x] CLI discovery commands: `/blocks`, `/find-bloc`, `/show`
  - [x] Accent normalization (`_norm_block_kind`)
  - [x] Ergonomic "preuve vs définition" handling

---

## 📈 METRICS & KPIs

### Sprint-level Metrics

| Metric | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Target v4.0 |
|--------|----------|----------|----------|----------|-------------|
| **Recall@5** | 75% → 85% | 85% | 85% | 85% | **≥85%** |
| **Precision@5** | 80% → 90% | 90% | 90% | 90% | **≥90%** |
| **Faithfulness** | - | 0.75 → 0.85 | 0.85 | 0.85 | **≥0.85** |
| **Latency p95** | 800ms → 600ms | 500ms | 400ms | <400ms | **<500ms** |
| **Test Coverage** | 40% → 60% | 70% | 75% | 80% | **≥80%** |
| **Cache Hit Rate** | - | - | 0% → 40% | 45% | **≥40%** |
| **User Satisfaction** | - | - | - | Survey | **≥4.5/5** |

### Definition of Done (DoD)

Pour qu'une story soit considérée **DONE**:

- [ ] Code implémenté selon spec
- [ ] Tests unitaires écrits (>80% coverage de la story)
- [ ] Tests d'intégration si applicable
- [ ] Documentation mise à jour (docstrings + README si nécessaire)
- [ ] Code review approuvé par 1+ reviewer
- [ ] CI/CD vert (build, tests, lint)
- [ ] Démo fonctionnelle (si feature visible)
- [ ] Merged dans `dev` branch

---

## 🏃 SPRINT PLANNING DÉTAILLÉ

### Sprint 0: Setup & Infrastructure (1 semaine)

**Dates**: Semaine 1 (4-8 nov 2025)  
**Capacity**: 40h (1 dev full-time)  
**Goal**: Infrastructure prête pour développement intensif

#### User Stories

**US-S0.1**: En tant que développeur, je veux un environnement de dev reproductible
- **Story Points**: 8
- **Tasks**:
  - [ ] Setup Docker Compose (Ollama, ChromaDB, FastAPI)
  - [ ] Makefile avec commandes dev (make install, make test, make run)
  - [ ] .env.example avec toutes les variables
  - [ ] Documentation setup dans README

**US-S0.2**: En tant que développeur, je veux des tests automatisés
- **Story Points**: 13
- **Tasks**:
  - [ ] Config pytest + pytest-cov + pytest-asyncio
  - [ ] Fixtures pour RAGEngine, Retriever, LLM mocks
  - [ ] Tests baseline router (50+ assertions)
  - [ ] Tests chunking (overlap, metadata)
  - [ ] CI: GitHub Actions workflow

**US-S0.3**: En tant que ops, je veux monitorer la santé du système
- **Story Points**: 13
- **Tasks**:
  - [ ] OpenTelemetry instrumentation
  - [ ] Prometheus exporter (metrics RAG)
  - [ ] Grafana provisioning (dashboards JSON)
  - [ ] Structured logging (structlog)

**US-S0.4**: En tant que dev, je veux une doc technique à jour
- **Story Points**: 5
- **Tasks**:
  - [ ] Architecture Decision Records (ADR template)
  - [ ] OpenAPI spec complète
  - [ ] CONTRIBUTING.md (workflow Git, conventions)

**Total Sprint 0**: 39 story points

**Sprint Goal**: ✅ Infrastructure prête, tests >60%, monitoring opérationnel

---

### Sprint 1: Core RAG Optimization (3 semaines)

**Dates**: Semaines 2-4 (11 nov - 29 nov 2025)  
**Capacity**: 120h (1 dev full-time)  
**Goal**: Retrieval precision/recall top-tier

#### User Stories

**US-S1.1**: En tant qu'utilisateur, je veux des réponses plus complètes (multi-query)
- **Story Points**: 13
- **Tasks**:
  - [ ] Classe `QueryExpander` avec LLM reformulation
  - [ ] Parallel retrieval (ThreadPoolExecutor)
  - [ ] RRF (Reciprocal Rank Fusion) implementation
  - [ ] Config `enable_query_expansion` dans .env
  - [ ] Eval dataset: +20% recall target

**US-S1.2**: En tant que système, je veux adapter le retrieval à l'intention
- **Story Points**: 8
- **Tasks**:
  - [ ] Classe `IntentClassifier` (keywords matching)
  - [ ] Mapping intent → filtres (définition, théorème, etc.)
  - [ ] Integration dans `MathAssistant.route_and_execute`
  - [ ] Tests: 85%+ intent accuracy

**US-S1.3**: En tant que système, je veux optimiser fusion BM25/Vector
- **Story Points**: 13
- **Tasks**:
  - [ ] `AdaptiveHybridRetriever` class
  - [ ] Heuristiques détection query technique (regex)
  - [ ] Poids dynamiques (0.7 BM25 si technique, 0.7 Vector sinon)
  - [ ] A/B test vs fixed weights

**US-S1.4**: En tant que système, je veux reranking token-level
- **Story Points**: 21
- **Tasks**:
  - [ ] Installation colbert-ai (+ index building)
  - [ ] Classe `ColBERTReranker`
  - [ ] Benchmark vs CrossEncoder (précision, latence)
  - [ ] Config `RERANKER_TYPE=colbert|crossencoder`

**US-S1.5**: En tant que système, je veux filtrer docs peu pertinents
- **Story Points**: 8
- **Tasks**:
  - [ ] Classe `RelevanceFilter` (cosine similarity)
  - [ ] Threshold adaptatif (min 2 docs, max 8)
  - [ ] Integration post-reranking

**US-S1.6**: En tant que système, je veux compresser contexte long
- **Story Points**: 13
- **Tasks**:
  - [ ] Installation llmlingua
  - [ ] Classe `ContextCompressor`
  - [ ] Config ratio compression (0.5-0.7)
  - [ ] Tests: latence vs qualité (ablation study)

**Total Sprint 1**: 76 story points (~120h estimé)

**Sprint Goal**: ✅ Recall@5 ≥85%, Precision@5 ≥90%, Latence <500ms p95

---

### Sprint 2: Features Pédagogiques (4 semaines)

**Dates**: Semaines 5-8 (2-27 déc 2025)  
**Capacity**: 160h (1 dev full-time)  
**Goal**: Modes tuteur enrichis, vérifications, citations

#### Epics

**EPIC-S2.1**: Vérification Symbolique (40h)
- US: En tant qu'étudiant, je veux vérifier mes calculs symboliquement
- Stories:
  - [ ] Parser LaTeX → SymPy (sympify with custom rules)
  - [ ] Vérification dérivées/intégrales/limites
  - [ ] Classe `SymbolicVerifier` avec error handling
  - [ ] Tests: 50+ formules mathématiques
  - [ ] GUI: badge ✅ "Vérifié symboliquement"

**EPIC-S2.2**: Citations Ancrées (30h)
- US: En tant qu'utilisateur, je veux tracer chaque affirmation
- Stories:
  - [ ] Extraction page + offset (via PDF coordinates)
  - [ ] Format citation: [Page X, §Y.Z, ligne N]
  - [ ] Classe `CitationManager`
  - [ ] GUI: liens cliquables → highlight PDF
  - [ ] API: `/api/citation/verify`

**EPIC-S2.3**: Windowed RAG (35h)
- US: En tant que système, je veux un contexte plus riche
- Stories:
  - [ ] Classe `WindowedRetriever` (±1, ±2 chunks)
  - [ ] Config `window_size` dynamique
  - [ ] Hierarchical: BM25 chapters → Vector chunks
  - [ ] Tests: +15% contexte pertinent vs baseline

**EPIC-S2.4**: Modes Pédagogiques (55h)
- US: En tant qu'enseignant, je veux différents styles pédagogiques
- Stories:
  - [ ] Mode Socratique (questions guidées, pas de réponse directe)
  - [ ] Mode Examiner (éval sans aide, chrono)
  - [ ] Mode Rigor (preuve formelle complète)
  - [ ] Mode Casual (vulgarisation simple)
  - [ ] Pack révision: synthèse + exercices + corrigés
  - [ ] CLI: `/mode socratique|examiner|rigor|casual`
  - [ ] GUI: sélecteur mode dans settings

**Total Sprint 2**: 160h

**Sprint Goal**: ✅ Vérif SymPy 90%+, Citations 100%, 4 modes péda opérationnels

---

### Sprint 3: UX & Productivité (4 semaines)

**Dates**: Semaines 9-12 (30 déc 2025 - 24 jan 2026)  
**Capacity**: 160h  
**Goal**: Historique, cache, exports, analytics

#### Epics

**EPIC-S3.1**: Cache Sémantique (25h)
- US: En tant qu'utilisateur, je veux des réponses instantanées
- Stories:
  - [ ] Classe `SemanticCache` (embeddings similarity)
  - [ ] Threshold 0.95 (95% similarité min)
  - [ ] TTL configurable (24h)
  - [ ] Metrics: hit rate, avg latency saved
  - [ ] Tests: warm cache vs cold

**EPIC-S3.2**: Historique Persistant (40h)
- US: En tant qu'utilisateur, je veux retrouver mes conversations
- Stories:
  - [ ] SQLite schema: conversations + turns
  - [ ] Classe `ConversationHistory` + FTS5
  - [ ] CLI: `/history search|list|resume|export`
  - [ ] GUI: sidebar avec liste conversations
  - [ ] Filtres: date, chapitre, rating
  - [ ] Migration logs existants

**EPIC-S3.3**: Export Documents (45h)
- US: En tant qu'étudiant, je veux exporter mes fiches
- Stories:
  - [ ] Classe `DocumentGenerator`
  - [ ] Templates LaTeX pro (poly, sujet exam)
  - [ ] API: `/export/course`, `/export/flashcards`, `/export/mindmap`
  - [ ] CLI: `/export cours|flashcards`
  - [ ] Formats: PDF (pdflatex), LaTeX, MD, Anki CSV
  - [ ] Tests: génération + compilation PDF

**EPIC-S3.4**: Feedback & Analytics (50h)
- US: En tant que système, je veux m'améliorer avec feedback
- Stories:
  - [ ] Classe `FeedbackSystem` (ratings, reports)
  - [ ] GUI: boutons 👍/👎 sous réponses
  - [ ] CLI: `/rate 1-5 [commentaire]`
  - [ ] API: `POST /api/feedback`
  - [ ] Classe `StudentAnalytics` (points forts/faibles)
  - [ ] Dashboard progression GUI
  - [ ] Export analytics JSON

**Total Sprint 3**: 160h

**Sprint Goal**: ✅ Cache 40%+ hit, Historique FTS, Exports pro, Analytics

---

### Sprint 4: Qualité & Production (3 semaines)

**Dates**: Semaines 13-15 (27 jan - 14 fév 2026)  
**Capacity**: 120h  
**Goal**: Production-ready

#### Epics

**EPIC-S4.1**: Évaluation RAGAS (30h)
- US: En tant que dev, je veux mesurer qualité RAG
- Stories:
  - [ ] Classe `RAGEvaluator` (RAGAS metrics)
  - [ ] Dataset golden questions (50+)
  - [ ] Métriques: faithfulness, answer_relevancy, context_recall
  - [ ] CI: éval automatique sur PRs
  - [ ] Dashboard Grafana: trends métriques

**EPIC-S4.2**: Tests Complets (35h)
- US: En tant que dev, je veux confiance dans le code
- Stories:
  - [ ] Coverage >80% (pytest-cov)
  - [ ] Tests unitaires: router, retriever, modes péda
  - [ ] Tests intégration: end-to-end RAG
  - [ ] Tests regression (golden dataset)
  - [ ] Property-based tests (Hypothesis)

**EPIC-S4.3**: Robustesse & Sécurité (25h)
- US: En tant que ops, je veux un système sûr
- Stories:
  - [ ] LaTeX guardrails (whitelist, max length, timeout)
  - [ ] Retry logic (exponential backoff)
  - [ ] Circuit breaker pattern
  - [ ] Health checks: `/health`, `/ready`
  - [ ] Rate limiting API

**EPIC-S4.4**: Production Monitoring (30h)
- US: En tant que ops, je veux observabilité complète
- Stories:
  - [ ] Prometheus metrics finaux (RED method)
  - [ ] Grafana dashboards (RAG, LLM, API)
  - [ ] Alerting (Slack/PagerDuty)
  - [ ] SLO/SLI: latence, availability, error rate
  - [ ] Versioning index (manifeste + migration)

**Total Sprint 4**: 120h

**Sprint Goal**: ✅ Tests 80%+, RAGAS >0.85, Monitoring 100%

---

### Sprint 5: Polish & Release (1 semaine)

**Dates**: Semaine 16 (17-21 fév 2026)  
**Capacity**: 40h  
**Goal**: Release v4.0.0

#### Tasks

- [ ] Documentation complète (user guide, dev docs)
- [ ] Code cleanup (refactoring, type hints)
- [ ] CHANGELOG.md détaillé
- [ ] Release notes (features, breaking changes)
- [ ] GitHub release + tags (v4.0.0)
- [ ] Déploiement staging → production
- [ ] Post-launch monitoring (24h)

**Sprint Goal**: ✅ v4.0.0 en production stable

---

## 🎯 PRIORITIZATION MATRIX

### MoSCoW Analysis

#### Must Have (v4.0 Blockers)
- ✅ Query expansion (recall boost)
- ✅ Intent classification
- ✅ SymPy verification
- ✅ Citations ancrées
- ✅ Windowed RAG
- ✅ Cache sémantique
- ✅ Historique persistant
- ✅ RAGAS evaluation
- ✅ Tests >80%
- ✅ Production monitoring

#### Should Have (v4.0 Nice-to-Have)
- ✅ ColBERT reranker
- ✅ Context compression
- ✅ Modes pédagogiques (tous)
- ✅ Export documents
- ✅ Student analytics
- ✅ LaTeX guardrails
- ✅ Versioning index

#### Could Have (v4.1+)
- ⏭️ Mode collaboratif
- ⏭️ Assistant vocal
- ⏭️ Intégration multimédia
- ⏭️ Système plugins

#### Won't Have (hors scope)
- ❌ Mobile app native
- ❌ Gamification complète
- ❌ Support multi-langue (hors FR/EN)

---

## 📅 TIMELINE VISUELLE

```
Nov 2025        Dec 2025              Jan 2026              Feb 2026
|-------|-------|-------|-------|-------|-------|-------|-------|
  S0      S1 (RAG Opt)      S2 (Péda)       S3 (UX)       S4    S5
  ██    ███████████████  ████████████████  ████████████████  ███████  ██
  
  S0: Infrastructure
  S1: Core RAG (Query expansion, ColBERT, compression)
  S2: Pédagogie (SymPy, citations, windowing, modes)
  S3: UX (Cache, historique, exports, analytics)
  S4: Qualité (RAGAS, tests, monitoring)
  S5: Release v4.0
```

---

## 🔄 SPRINT CEREMONIES

### Daily Standup (15 min)
- **Quand**: Chaque jour 10:00
- **Questions**:
  - Qu'ai-je fait hier ?
  - Que vais-je faire aujourd'hui ?
  - Y a-t-il des blockers ?

### Sprint Planning (4h)
- **Quand**: Premier jour du sprint
- **Outputs**:
  - Sprint goal défini
  - User stories sélectionnées
  - Tasks décomposées
  - Capacity confirmée

### Sprint Review (2h)
- **Quand**: Dernier jour du sprint
- **Outputs**:
  - Démo features complétées
  - Feedback stakeholders
  - Backlog update

### Sprint Retrospective (1h)
- **Quand**: Après review
- **Questions**:
  - Qu'est-ce qui a bien marché ?
  - Qu'est-ce qui peut être amélioré ?
  - Actions concrètes pour prochain sprint

---

## 🚀 QUICK START - Sprint 0

### Semaine 1 - Setup Immédiat

#### Jour 1: Infrastructure de base
```bash
# 1. Setup repo
git checkout -b dev
git push -u origin dev

# 2. Pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Docker Compose
cat > docker-compose.yml << EOF
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_models:/root/.ollama"]
  
  chromadb:
    image: chromadb/chroma:latest
    ports: ["8000:8000"]
    volumes: ["chroma_data:/chroma/chroma"]
  
  app:
    build: .
    ports: ["8080:8080"]
    volumes: [".:/app"]
    depends_on: [ollama, chromadb]

volumes:
  ollama_models:
  chroma_data:
EOF

docker-compose up -d
```

#### Jour 2: Tests & CI
```bash
# 1. Tests setup
pip install pytest pytest-cov pytest-asyncio pytest-mock

# 2. GitHub Actions
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << EOF
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
EOF
```

#### Jour 3: Monitoring
```bash
# 1. OpenTelemetry
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

# 2. Prometheus
pip install prometheus-client

# 3. Structlog
pip install structlog
```

#### Jours 4-5: Documentation & Polish
- Architecture Decision Records (ADR)
- OpenAPI spec update
- README improvements
- CONTRIBUTING.md

---

## 📊 SUCCESS CRITERIA - v4.0 Release

### Functional Requirements
- [ ] Query expansion: +20% recall vs v3.1
- [ ] SymPy verification: 90%+ formules vérifiées
- [ ] Citations: 100% traçables (page + offset)
- [ ] Cache: 40%+ hit rate
- [ ] Historique: FTS search <100ms
- [ ] 4 modes pédagogiques opérationnels
- [ ] Exports PDF qualité publication

### Non-Functional Requirements
- [ ] Latence p95 end-to-end: <500ms
- [ ] Test coverage: >80%
- [ ] RAGAS faithfulness: >0.85
- [ ] API availability: >99.5%
- [ ] Documentation complète (user + dev)

### Operational Requirements
- [ ] Monitoring: 100% endpoints tracés
- [ ] Alerting configuré (latence, errors)
- [ ] CI/CD pipeline stable
- [ ] Versioning index avec migration

---

## 🎉 CONCLUSION

Ce Kanban/Roadmap couvre **16 semaines de développement intensif** pour transformer l'assistant mathématiques RAG v3.1 en un système de classe mondiale (v4.0).

### Prochaines Étapes Immédiates

1. **Valider roadmap** avec équipe/stakeholders
2. **Démarrer Sprint 0** (setup infrastructure)
3. **Constituer dataset eval** (50+ questions golden)
4. **Configurer monitoring** (Grafana dashboards)

### Points de Décision Clés

- **Semaine 3**: Valider gains retrieval (rappel/précision)
- **Semaine 6**: User testing modes pédagogiques
- **Semaine 10**: Validation UX (historique, exports)
- **Semaine 14**: Go/No-Go production

---

**Version**: 1.0  
**Date**: 3 novembre 2025  
**Auteur**: Assistant Mathématiques Team  
**Status**: 🟢 Ready to Start

🚀 **Let's build something amazing!**
