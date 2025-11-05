# 🎓 Assistant Mathématiques RAG v3.1 - Architecture SOLID

Système RAG (Retrieval-Augmented Generation) pour l'assistance en mathématiques, avec **architecture SOLID complète**, DI Container, et Facade Pattern.

## 🚀 Démarrage rapide (Phase 4 - NOUVEAU)

```python
from src.application.facades import get_assistant

# Le DI Container fait tout automatiquement !
assistant = get_assistant()

# Poser une question
result = assistant.ask("C'est quoi une série de Fourier ?", chapter="8")

# Générer des exercices
result = assistant.generate_exercises("intégration par parties", count=5)

# Créer un examen
result = assistant.generate_exam(chapters="5,6,7", duration="3h")
```

📖 **[Guide de référence rapide](QUICK_REFERENCE.md)** | 📚 **[Phase 4 complète](PHASE4_COMPLETE.md)**

---

## ✨ Nouveautés v3.1 (Phase 4 - Architecture SOLID)

### Phase 4 : COMPLETE ✅ (8/8 tests passent)

- ✅ **DI Container** : Gestion automatique des dépendances (retriever, llm, router, prompts, 16 use cases)
- ✅ **16 Use Cases** : Toutes les fonctionnalités organisées en use cases (Q&A, Course, Sheets, Exercises, Exams, Utilities)
- ✅ **Facade Pattern** : Point d'entrée unique via `MathAssistantFacade`
- ✅ **Architecture SOLID** : Domain-Driven Design + tous les principes SOLID
- ✅ **Singletons automatiques** : Objets lourds créés UNE SEULE FOIS
- ✅ **Testabilité** : 8 tests fast (100% pass rate)

### Phase 0-3 : Architecture de base

- ✅ **Architecture modulaire** : Code organisé en modules réutilisables
- ✅ **Configuration centralisée** : Gestion propre via dataclasses et `.env`
- ✅ **CLI amélioré** : Interface Rich moderne avec thème GitHub Dark
- ✅ **API FastAPI** : Serveur avec endpoints dédiés (chat, fiches, examens...)
- ✅ **Reranker intégré** : CrossEncoder pour améliorer la qualité du retrieval
- ✅ **Query rewriting** : Réécriture intelligente des requêtes de suivi
- ✅ **Mémoire de session** : Contexte persistant avec pin/unpin
- ✅ **Routage canonique** : Gestion spécifique de requêtes (ex: Leibniz)

---

## 📁 Structure du projet (Phase 4 - SOLID Architecture)

```
.
├── README_REFACTORED.md          # Ce fichier
├── PHASE4_COMPLETE.md            # 🆕 Documentation Phase 4 complète
├── QUICK_REFERENCE.md            # 🆕 Guide de référence rapide
├── example_usage.py              # 🆕 Exemple d'utilisation
├── test_solid_phase4_fast.py     # 🆕 Tests Phase 4 (8/8 pass)
├── .env.example                  # Configuration exemple
├── pyproject.toml                # Dépendances (uv/pip)
├── server.py                     # Serveur FastAPI
│
├── src/                          # Code source SOLID
│   │
│   ├── domain/                   # 🆕 DOMAIN LAYER (Phase 1)
│   │   ├── entities/             # Entités métier
│   │   │   ├── query_context.py  # QueryContext (query, filters, session)
│   │   │   └── session_context.py # SessionContext (chat history)
│   │   ├── interfaces/           # Interfaces (abstractions)
│   │   │   ├── llm.py            # ILLMProvider (LLM abstraction)
│   │   │   ├── retriever.py      # IRetriever (retrieval abstraction)
│   │   │   └── router.py         # IRouter (routing abstraction)
│   │   └── value_objects/        # Value Objects (immutables)
│   │       ├── document.py       # Document (source data)
│   │       └── filters.py        # Filters (chapter, block_types)
│   │
│   ├── application/              # 🆕 APPLICATION LAYER (Phase 2-4)
│   │   ├── interfaces/           # Use Case interfaces
│   │   │   └── use_case.py       # IUseCase[TRequest, TResponse]
│   │   ├── services/             # Services applicatifs
│   │   │   ├── prompt_repository.py  # PromptRepository (17 prompts)
│   │   │   └── query_rewriter.py     # QueryRewriter (reformulation)
│   │   ├── use_cases/            # 🆕 16 USE CASES (Phase 4)
│   │   │   ├── answer_question.py      # Q&A
│   │   │   ├── explain_course.py       # Course explain
│   │   │   ├── build_course.py         # Course build
│   │   │   ├── summarize_course.py     # Course summary
│   │   │   ├── generate_exercise.py    # Exercise generation
│   │   │   ├── solve_exercise.py       # Exercise solution
│   │   │   ├── correct_exercise.py     # Exercise correction
│   │   │   ├── explain_theorem.py      # Theorem explanation
│   │   │   ├── explain_formula.py      # Formula explanation
│   │   │   ├── prove_statement.py      # Proof generation
│   │   │   ├── sheets_and_exercises.py # Sheets (4 use cases)
│   │   │   └── exams_and_assessments.py # Exams (4 use cases)
│   │   └── facades/              # 🆕 FACADE PATTERN (Phase 4)
│   │       └── math_assistant_facade.py # Point d'entrée unique
│   │
│   ├── infrastructure/           # 🆕 INFRASTRUCTURE LAYER (Phase 3)
│   │   ├── llm/                  # LLM implementations
│   │   │   └── fallback_llm_provider.py # Fallback LLM
│   │   ├── retrieval/            # Retrieval implementations
│   │   │   └── hybrid_retriever.py      # BM25 + Vector + Reranker
│   │   └── routing/              # Routing implementations
│   │       └── intent_detection_router.py # Intent router
│   │
│   ├── config/                   # 🆕 CONFIGURATION (Phase 3)
│   │   └── di_container.py       # DI Container (factory methods)
│   │
│   ├── core/                     # Cœur du système (legacy)
│   │   ├── config.py             # Configuration centralisée
│   │   └── rag_engine.py         # Moteur RAG
│   │
│   ├── assistant/                # Logique métier (legacy)
│   │   ├── assistant.py          # Assistant principal
│   │   └── prompts.py            # Templates de prompts
│   │
│   ├── controllers/              # Contrôleurs API
│   │   └── math_assistant_controller.py
│   │
│   ├── utils/                    # Utilitaires
│   │   ├── ollama.py             # Client Ollama
│   │   └── text_processing.py   # Traitement texte/LaTeX
│   │
│   └── ui/                       # Interfaces utilisateur
│       ├── cli/                  # Interface CLI
│       │   ├── app.py            # Application CLI
│       │   └── styles.py         # Styles Rich
│       └── gui/                  # Interface GUI (WIP)
│
├── scripts/                      # Scripts de lancement
│   ├── run_cli.py                # Lancer CLI
│   ├── run_gui.py                # Lancer GUI
│   ├── gen_sft_qa.py             # Génération données SFT
│   └── train_reranker.py         # Entraînement reranker
│
├── before/                       # Code legacy (référence)
│   ├── math_assistant_cli.py
│   ├── math_assistant_gui.py
│   └── model/
│
├── data/                         # Données
├── db/                           # Base vectorielle Chroma
└── model/                        # Modèles et PDFs
    └── livre_2011.pdf
```

### 🏗️ Architecture en couches (SOLID)

```
┌─────────────────────────────────────────┐
│  UI Layer (CLI, GUI, FastAPI)          │  ← Utilisateurs
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Application Layer (Use Cases + Facade) │  ← Logique métier
│  • 16 Use Cases                         │
│  • MathAssistantFacade (point unique)   │
│  • Services (PromptRepository, etc.)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Domain Layer (Entities + Interfaces)   │  ← Abstractions pures
│  • QueryContext, SessionContext         │
│  • IRetriever, ILLMProvider, IRouter    │
│  • Document, Filters                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Infrastructure Layer (Implémentations) │  ← Détails techniques
│  • HybridRetriever (BM25+Vector)        │
│  • FallbackLLMProvider (Ollama)         │
│  • IntentDetectionRouter                │
└─────────────────────────────────────────┘
               ▲
               │
┌──────────────┴──────────────────────────┐
│  DI Container (di_container.py)         │  ← Gestion dépendances
│  • Singletons automatiques              │
│  • Factory methods                      │
└─────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prérequis

- Python 3.12+ (pour dataclasses et type hints avancés)
- Ollama (local ou compte cloud)
- [uv](https://github.com/astral-sh/uv) (recommandé) ou pip

### Étapes

```bash
# 1. Cloner le repo
git clone <url>
cd test_ollama_rag/server

# 2. Installer les dépendances
uv sync
# ou avec pip:
# pip install -e .

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 4. (Optionnel) Installer le reranker
pip install sentence-transformers

# 5. Indexer le PDF (première fois uniquement)
python -m src.core.rag_engine
```

---

## 💻 Utilisation

### 🆕 Phase 4 : Nouvelle API avec Facade Pattern (RECOMMANDÉ)

```python
from src.application.facades import get_assistant

# Initialisation automatique via DI Container
assistant = get_assistant()

# Q&A simple
result = assistant.ask("C'est quoi une série de Fourier ?", chapter="8")
print(result["answer"])

# Génération d'exercices
result = assistant.generate_exercises(
    topic="intégration par parties",
    count=5,
    difficulty="moyen",
    chapter="6"
)

# Génération d'examen
result = assistant.generate_exam(
    chapters="5,6,7",
    duration="3h",
    total_points=100,
    difficulty="difficile"
)

# Explication de formule
result = assistant.explain_formula("formule de Stokes", chapter="9")

# Preuve de théorème
result = assistant.prove_statement("théorème de Cauchy-Lipschitz", chapter="14")

# Créer une fiche de révision
result = assistant.create_sheet("séries de Fourier", chapter="8")

# QCM
result = assistant.generate_qcm("séries entières", num_questions=10, chapter="12")
```

📖 **[Guide de référence complet](QUICK_REFERENCE.md)** avec toutes les 17 méthodes disponibles.

---

### CLI (Legacy - toujours supporté)

```bash
# Lancer le CLI
python scripts/run_cli.py

# ou directement
uv run src.ui.cli.app
```

**Commandes principales :**

```
# Questions simples
Quelle est la définition d'un espace vectoriel ?

# Filtres rapides
/exercice application du théorème de Thalès
/méthode résolution d'équations différentielles
/théorie théorème de Bolzano-Weierstrass

# Portée (scope)
/scope set chapter=21 type=théorie
/ch 28
/bloc théorème 28.7

# Mémoire
/pin                # Épingler le contexte
/unpin              # Désépingler
/forget             # Tout oublier
/new-chat           # Nouveau chat isolé

# Autres
/link on            # Activer auto-link follow-up
/debug on           # Mode debug
/log save           # Sauvegarder en JSONL
q                   # Quitter
```

### API FastAPI

```bash
# Lancer le serveur
python server.py

# ou avec uvicorn
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Endpoints disponibles :**

```
GET  /                     # Infos API
GET  /docs                 # Documentation Swagger
GET  /api/health           # Health check
GET  /api/rag_check        # Diagnostic RAG

# Questions & Réponses
GET  /api/chat?question=...&k=6&doc_type=exercice&chapter=21

# Fiches de révision
GET  /api/sheet?topic=...&level=Prépa&chapter=21
POST /api/sheet_review     # Vérifier une fiche

# Formules
GET  /api/formula?query=...

# Examens
GET  /api/exam?chapters=1,5,7&duration=3h&level=Prépa

# Cours complet
GET  /api/course?notion=...&level=Prépa

# Correction de copie
POST /api/grade
```

**Exemple avec curl :**

```bash
curl "http://localhost:8000/api/chat?question=théorème%20de%20Leibniz&chapter=28"
```

### GUI (WIP)

```bash
python scripts/run_gui.py
```

_Note : Le GUI est en cours de refactoring. Pour l'instant, il utilise l'ancienne version._

---

## ⚙️ Configuration

Toutes les options sont dans `.env` :

```bash
# Modèles
MATH_LLM_NAME=deepseek-v3.1:671b-cloud
EMBED_MODEL_NAME=mxbai-embed-large:latest

# Chemins
MATH_PDF_PATH=./model/livre_2011.pdf
MATH_DB_DIR=./db/chroma_db_math_v3_1

# Features
MATH_USE_RERANKER=1           # 1=actif, 0=désactivé
MATH_REWRITE=1                # Query rewriting

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_API_KEY=                # Pour Ollama Cloud
```

---

## 🏗️ Architecture

### Flux de traitement

```
Question utilisateur
    ↓
[Query Rewriter] ← Contexte session
    ↓
[Canonical Router] ← Routes prédéfinies
    ↓
[Hybrid Retriever] (BM25 + Vectoriel)
    ↓
[Reranker] (optionnel)
    ↓
[LLM] + Context
    ↓
Réponse formatée
```

### Composants clés

- **RAGEngine** : Orchestration générale (loading, splitting, indexing, retrieval)
- **HybridRetriever** : Fusion BM25 + vectoriel + reranking
- **MathAssistant** : Logique métier (mémoire, routes, génération)
- **SessionMemory** : Gestion du contexte et de la portée
- **QueryRewriter** : Réécriture intelligente des requêtes

---

## 🎨 Styles

### CLI (Rich)

- **Thème** : GitHub Dark
- **Tableaux** : Bordures arrondies, lignes alternées
- **Panneaux** : Colorés par type (info/success/warning/error)
- **Markdown** : Support natif dans les réponses

### GUI (Qt)

- **Palette** : GitHub Dark moderne
- **Composants** : States hover/pressed/disabled
- **KaTeX** : Rendu LaTeX via WebEngine
- **Scrollbars** : Custom, discrètes

---

## 📊 Fonctionnalités avancées

### Auto-link & Mémoire

```bash
# Question initiale
> Théorème de Leibniz pour le barycentre
[Contexte détecté: chapitre 28, théorème 28.7]

# Question de suivi (auto-link activé)
> Peux-tu me donner un exemple ?
# → Cherche dans chapitre 28, théorème 28.7 automatiquement

# Épingler le contexte
> /pin
# → Toutes les questions suivantes utiliseront ce contexte

# Désépingler
> /unpin
```

### Portée (Scope)

```bash
# Définir une portée globale
> /scope set chapter=21 type=exercice
# → Toutes les recherches filtrent sur chapitre 21, exercices

# Voir la portée
> /scope show

# Réinitialiser
> /scope clear
```

### Routes canoniques

Gestion spécifique de requêtes ambiguës :

```python
"fonction de leibniz (barycentre)" → chapitre 28, théorème 28.7
"formule de leibniz (dérivées)" → chapitre 12
```

Ajoutables dans `src/assistant/assistant.py : CanonicalRouter.ROUTES`

---

## 🔧 Développement

### Ajouter un nouveau prompt

1. Éditer `src/assistant/prompts.py`
2. Créer un template LangChain
3. Ajouter une fonction chain dans `src/controllers/math_assistant_controller.py`
4. Créer une route FastAPI

### Ajouter une commande CLI

1. Éditer `src/ui/cli/app.py : MathCLI.handle_command()`
2. Ajouter la logique
3. Mettre à jour l'aide dans `styles.py : CLIFormatter.command_help()`

### Tests

```bash
# Self-check du RAG
python -m src.core.rag_engine

# Test du serveur
python server.py
# Ouvrir http://localhost:8000/docs
```

---

## 🐛 Dépannage

### Erreur "PDF non trouvé"

```bash
# Vérifier le chemin dans .env
MATH_PDF_PATH=./model/livre_2011.pdf

# Ou mettre le chemin absolu
MATH_PDF_PATH=/home/user/projet/model/livre_2011.pdf
```

### Erreur "Model not found" (Ollama)

```bash
# Lister les modèles disponibles
ollama list

# Tirer un modèle
ollama pull deepseek-v3.1:671b-cloud
```

### Reranker lent

Le reranker améliore la qualité mais ralentit le retrieval (~1-2s).

```bash
# Désactiver dans .env
MATH_USE_RERANKER=0
```

### Base vectorielle corrompue

```bash
# Supprimer et réindexer
rm -rf db/chroma_db_math_v3_1
python -m src.core.rag_engine
```

---

## 📚 Ressources

- [LangChain](https://python.langchain.com/)
- [Ollama](https://ollama.com/)
- [Chroma](https://www.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)
- [PySide6](https://doc.qt.io/qtforpython-6/)

---

## 📝 TODO

- [ ] Refactoriser le GUI (PySide6)
- [ ] Ajouter tests unitaires
- [ ] Support multi-PDF
- [ ] Export réponses en Markdown/LaTeX
- [ ] Historique de conversation persistant
- [ ] Interface web (Streamlit/Gradio)
- [ ] Fine-tuning du reranker sur données cours

---

## 📄 Licence

Projet personnel / Académique

---

## 👤 Auteur

Refactoring par Claude AI Assistant & Utilisateur

---

## 🙏 Remerciements

- Anthropic pour Claude
- Communauté LangChain
- Équipe Ollama