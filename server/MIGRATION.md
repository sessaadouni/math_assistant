# 📦 Guide de migration v3.0 → v3.1

Ce guide t'aide à migrer du code legacy (`before/`) vers l'architecture refactorisée (`src/`).

---

## 🎯 Changements principaux

### Structure

```
AVANT (before/)                    APRÈS (src/)
├── math_assistant_cli.py      →  ui/cli/app.py
├── math_assistant_gui.py      →  ui/gui/app.py
├── model/math_course_rag.py   →  core/rag_engine.py
├── utils/math_assistant_lib.py →  assistant/assistant.py
├── utils/lib.py               →  utils/ollama.py
└── prompts.py                 →  assistant/prompts.py
```

### Imports

```python
# AVANT
from model.math_course_rag import create_retriever
from utils.math_assistant_lib import retrieve_and_answer

# APRÈS
from src.core.rag_engine import get_engine
from src.assistant.assistant import get_assistant

# Usage
engine = get_engine()
retriever = engine.create_retriever(k=8, chapter="21")

assistant = get_assistant()
result = assistant.retrieve_and_answer("question")
```

### Configuration

```python
# AVANT
import os
MODEL_NAME = os.environ.get("MATH_LLM_NAME", "default")
PDF_PATH = pathlib.Path(os.environ.get("MATH_PDF_PATH", "./model/livre.pdf"))

# APRÈS
from src.core.config import rag_config
model = rag_config.llm_model
pdf = rag_config.pdf_path
```

---

## 🔄 Équivalences API

### RAG Engine

```python
# AVANT
from model.math_course_rag import (
    build_or_load_store,
    create_retriever,
    rag_self_check
)

store = build_or_load_store()
retriever = create_retriever(k=8, doc_type="exercice", chapter="21")
check = rag_self_check()

# APRÈS
from src.core.rag_engine import get_engine

engine = get_engine()
store = engine.build_or_load_store()
retriever = engine.create_retriever(k=8, doc_type="exercice", chapter="21")
check = engine.self_check()
```

### Assistant

```python
# AVANT
from utils.math_assistant_lib import (
    retrieve_and_answer,
    scope_set,
    scope_clear,
    reset_state
)

result = retrieve_and_answer(
    "question",
    filter_type="exercice",
    auto_link=True
)
scope_set(chapter="21", type="théorie")
scope_clear()
reset_state()

# APRÈS
from src.assistant.assistant import get_assistant

assistant = get_assistant()

result = assistant.retrieve_and_answer(
    "question",
    filter_type="exercice",
    auto_link=True
)

assistant.memory.scope_set(chapter="21", type="théorie")
assistant.memory.scope_clear()
assistant.memory.reset()
```

### Mémoire de session

```python
# AVANT
from utils.math_assistant_lib import LAST_STATE, SESSION_SCOPE

pinned = LAST_STATE.get("pinned_meta")
chapter = SESSION_SCOPE.get("chapter")

# APRÈS
from src.assistant.assistant import get_assistant

assistant = get_assistant()

pinned = assistant.memory.state["pinned_meta"]
chapter = assistant.memory.scope["chapter"]
```

---

## 🎨 Styles CLI

### Affichage Rich

```python
# AVANT
from model.math_course_rag import console, print_sources

console.print("[bold]Titre[/]")
print_sources(docs)

# APRÈS
from src.ui.cli.styles import console, CLIFormatter

formatter = CLIFormatter()
formatter.title("Titre")
formatter.sources_table(docs)
```

### Messages formatés

```python
# AVANT
console.print("[green]✅ Succès[/]")
console.print("[red]❌ Erreur[/]")
console.print("[yellow]⚠️  Attention[/]")

# APRÈS
from src.ui.cli.styles import CLIFormatter

formatter = CLIFormatter()
formatter.success("Succès")
formatter.error("Erreur")
formatter.warning("Attention")
formatter.info("Information")
```

---

## 🖥️ Serveur FastAPI

### Routes

```python
# AVANT (server.py)
from model.math_course_rag import create_retriever
from prompts import PROF_PROMPT

retriever = create_retriever(k=k, doc_type=doc_type)
chain = prof_chain(retriever)

# APRÈS
from src.core.rag_engine import get_engine
from src.assistant.prompts import PROF_PROMPT

engine = get_engine()
retriever = engine.create_retriever(k=k, doc_type=doc_type)
chain = prof_chain(retriever)
```

### Contrôleurs

```python
# AVANT (routes dans server.py)
@app.get("/chat")
async def chat(question: str, k: int = 6):
    # logique ici
    pass

# APRÈS (controller séparé)
# Importer le router
from src.controllers.math_assistant_controller import router
app.include_router(router, prefix="/api")

# Les routes sont dans src/controllers/math_assistant_controller.py
```

---

## 📝 Checklist de migration

### Pour un script existant

- [ ] Mettre à jour les imports
  ```python
  # Remplacer
  from model.math_course_rag import ...
  from utils.math_assistant_lib import ...
  
  # Par
  from src.core.rag_engine import get_engine
  from src.assistant.assistant import get_assistant
  from src.core.config import rag_config
  ```

- [ ] Adapter les appels de fonctions
  ```python
  # Anciens appels directs → Méthodes d'instance
  create_retriever(...) → engine.create_retriever(...)
  retrieve_and_answer(...) → assistant.retrieve_and_answer(...)
  ```

- [ ] Migrer la configuration
  ```python
  # Variables d'environnement → Config centralisée
  os.environ.get("MATH_LLM_NAME") → rag_config.llm_model
  ```

- [ ] Mettre à jour les styles
  ```python
  # Affichages Rich → CLIFormatter
  console.print("[green]✅[/]") → formatter.success("...")
  ```

### Pour le serveur

- [ ] Déplacer les routes vers `src/controllers/`
- [ ] Utiliser les prompts de `src/assistant/prompts.py`
- [ ] Importer le router dans `server.py`
- [ ] Tester tous les endpoints

### Pour le CLI

- [ ] Utiliser `src/ui/cli/app.py` comme base
- [ ] Adapter les commandes custom
- [ ] Intégrer les nouveaux styles
- [ ] Tester toutes les commandes

---

## 🧪 Tests de compatibilité

### 1. Vérifier les imports

```bash
python -c "from src.core.rag_engine import get_engine; print('✅ rag_engine OK')"
python -c "from src.assistant.assistant import get_assistant; print('✅ assistant OK')"
python -c "from src.core.config import rag_config; print('✅ config OK')"
```

### 2. Tester le RAG

```bash
python -m src.core.rag_engine
```

### 3. Tester le CLI

```bash
python scripts/run_cli.py
# Lancer quelques commandes de test
```

### 4. Tester le serveur

```bash
python server.py
# Ouvrir http://localhost:8000/docs
# Tester /api/health et /api/rag_check
```

---

## 🐛 Problèmes courants

### Import Error

```
ImportError: No module named 'model.math_course_rag'
```

**Solution :** Mettre à jour les imports vers `src.core.rag_engine`

### Config non trouvée

```
FileNotFoundError: PDF introuvable
```

**Solution :** Créer `.env` depuis `.env.example` et ajuster les chemins

### Attribut manquant

```
AttributeError: 'RAGEngine' object has no attribute 'create_retriever'
```

**Solution :** Utiliser `get_engine()` au lieu d'instancier directement

---

## 📚 Ressources

- [README_REFACTORED.md](./README_REFACTORED.md) - Documentation complète
- [.env.example](./.env.example) - Configuration exemple
- [src/](./src/) - Code source refactorisé
- [before/](./before/) - Code legacy (référence)

---

## 💡 Conseils

1. **Migrer progressivement** : Commencer par un script, puis généraliser
2. **Garder `before/`** : Utile comme référence pendant la migration
3. **Tester souvent** : Vérifier après chaque changement majeur
4. **Utiliser le singleton** : `get_engine()` et `get_assistant()` évitent les instanciations multiples
5. **Lire les docstrings** : Le nouveau code est bien documenté

---

## ✅ Validation finale

Une fois la migration terminée :

```bash
# 1. Reconstruire la DB
python scripts/rebuild_db.py --check-only

# 2. Tester le CLI
python scripts/run_cli.py
# Essayer : /scope set chapter=21, question, /log save

# 3. Tester le serveur
python server.py
# Ouvrir http://localhost:8000/docs
# Essayer : /api/chat?question=test

# 4. Vérifier les logs
ls -la logs/

# 5. Si tout fonctionne → Supprimer before/ (optionnel)
```

---

Bon courage pour la migration ! 🚀