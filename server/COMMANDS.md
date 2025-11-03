# 📝 Commandes Utiles - Math RAG v3.1

## 🚀 Démarrage rapide

```bash
# Test complet de l'installation
./test_installation.sh

# Lancer le script interactif
./start_all.sh

# Diagnostic système
python scripts/diagnostic.py
```

## 📦 Installation

```bash
# Cloner/naviguer vers le projet
cd /path/to/test_ollama_rag/server

# Installer les dépendances avec uv
uv pip install -e .

# Ou avec pip classique
pip install -e .

# Installer les dépendances GUI (optionnel)
uv pip install PySide6 PySide6-WebEngine

# Créer le fichier .env
cp .env.example .env
nano .env  # Éditer avec vos valeurs

# Migration automatique
python scripts/migrate.py
```

## 🔧 Configuration

```bash
# Variables d'environnement principales
export MATH_PDF_PATH="./model/livre_2011.pdf"
export MATH_DB_DIR="./db/chroma_db_math_v3_1"
export OLLAMA_HOST="http://localhost:11434"
export MATH_LLM_NAME="deepseek-v3.1:671b-cloud"
export EMBED_MODEL_NAME="mxbai-embed-large:latest"

# Ou éditer .env
nano .env
```

## 🗃️ Base de données

```bash
# Reconstruire la base de données
python scripts/rebuild_db.py --force

# Reconstruire avec des paramètres personnalisés
python scripts/rebuild_db.py --chunk-size 800 --chunk-overlap 100

# Analyser la base existante
python debug/analyze_vectorstore.py

# Diagnostic d'extraction PDF
python debug/diagnostic_pdf.py
```

## 💻 Interface CLI

```bash
# Lancer le CLI
python scripts/run_cli.py

# Avec Makefile
make cli

# Commandes dans le CLI :
# /help              - Aide
# /quit ou /exit     - Quitter
# /newchat           - Nouveau chat isolé
# /forget            - Oublier le contexte
# /pin               - Épingler le contexte
# /unpin             - Désépingler
# /scope <args>      - Définir la portée (ex: /scope chapter=21)
# /scope clear       - Réinitialiser la portée
# /debug on|off      - Mode debug
# /log <file>        - Sauvegarder le log
```

## 🖥️ Interface GUI

```bash
# Lancer le GUI
python scripts/run_gui.py

# Avec Makefile
make gui

# Vérifier que PySide6 est installé
python -c "from PySide6 import QtWidgets; print('OK')"
```

## 🌐 Serveur API

```bash
# Lancer le serveur FastAPI
python server.py

# Avec Makefile
make server

# Accéder à la documentation Swagger
open http://localhost:8000/docs

# Tester l'API avec curl
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Quest-ce quun groupe?", "filter_type": null}'

# Avec streaming SSE
curl -N http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique les groupes"}'
```

## 🐳 Ollama

```bash
# Démarrer Ollama
ollama serve

# Lister les modèles installés
ollama list

# Télécharger les modèles nécessaires
ollama pull deepseek-v3.1:671b-cloud
ollama pull mxbai-embed-large:latest

# Tester un modèle
ollama run deepseek-v3.1:671b-cloud "Test"

# Voir les modèles en cours d'exécution
ollama ps

# Supprimer un modèle
ollama rm <model_name>

# Vérifier l'API Ollama
curl http://localhost:11434/api/tags
```

## 🧪 Tests et validation

```bash
# Test d'installation complet
./test_installation.sh

# Diagnostic système
python scripts/diagnostic.py

# Test des imports
python -c "from src.core.config import rag_config; print('OK')"
python -c "from src.core.rag_engine import RAGEngine; print('OK')"
python -c "from src.assistant.assistant import MathAssistant; print('OK')"

# Vérifier la structure
tree src/ -L 2

# Lister les dépendances installées
uv pip list
# ou
pip list | grep -E "(langchain|ollama|chroma|rich|pyside)"
```

## 🔍 Débogage

```bash
# Activer le mode debug dans CLI
python scripts/run_cli.py
# Puis : /debug on

# Logs détaillés
tail -f logs/session.jsonl

# Analyser les logs JSONL avec jq
cat logs/session.jsonl | jq '.question, .answer'

# Vérifier les métadonnées ChromaDB
python debug/analyze_vectorstore.py

# Test d'extraction PDF
python debug/diagnostic_pdf.py
```

## 🧹 Nettoyage

```bash
# Nettoyer les fichiers Python compilés
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Nettoyer les logs
rm -rf logs/*.jsonl

# Réinitialiser la base de données
rm -rf db/chroma_db_math_v3_1/
python scripts/rebuild_db.py --force

# Nettoyer tout (ATTENTION : perte de données)
make clean
```

## 📊 Scripts utilitaires

```bash
# Générer des paires contrastives
python scripts/gen_contrastive_pairs.py

# Générer des données SFT/QA
python scripts/gen_sft_qa.py

# Entraîner un reranker (avancé)
python scripts/train_reranker.py
```

## 🔐 Permissions

```bash
# Rendre les scripts exécutables
chmod +x test_installation.sh
chmod +x start_all.sh
chmod +x start_backend.sh
chmod +x scripts/*.py

# Vérifier les permissions
ls -l test_installation.sh
ls -l scripts/
```

## 📝 Git

```bash
# Initialiser Git (si pas déjà fait)
git init

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Commit initial
git commit -m "Refactoring v3.1: Architecture MVC, GUI moderne, CLI amélioré"

# Vérifier le statut
git status

# Voir l'historique
git log --oneline
```

## 🎨 Développement

```bash
# Formater le code avec black
black src/ scripts/

# Vérifier le style avec flake8
flake8 src/ scripts/

# Type checking avec mypy
mypy src/ scripts/

# Lancer les tests (si configurés)
pytest tests/

# Coverage
pytest --cov=src tests/
```

## 📚 Documentation

```bash
# Générer la documentation (si configurée)
sphinx-build -b html docs/ docs/_build/

# Lire les READMEs
cat README_REFACTORED.md
cat QUICKSTART.md
cat MIGRATION.md
cat GUI_IMPROVEMENTS.md
cat TROUBLESHOOTING.md
cat FINAL_CHECKLIST.md

# Ouvrir dans le navigateur
open README_REFACTORED.md  # macOS
xdg-open README_REFACTORED.md  # Linux
```

## 🚢 Déploiement

```bash
# Build pour production (futur)
python -m build

# Docker (futur)
docker build -t math-rag:v3.1 .
docker run -p 8000:8000 math-rag:v3.1

# Export de l'environnement
uv pip freeze > requirements.txt
```

## ⚙️ Makefile (si disponible)

```bash
# Voir toutes les commandes
make help

# Installation
make install

# Tests
make check
make test

# Lancer les applications
make cli
make gui
make server

# Reconstruire la DB
make rebuild

# Nettoyage
make clean

# Format du code
make format

# Linting
make lint
```

## 🔗 URLs utiles

```bash
# Serveur FastAPI local
http://localhost:8000

# Documentation Swagger
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# Ollama API
http://localhost:11434

# KaTeX CDN
https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css
```

## 📋 Variables d'environnement complètes

```bash
# Fichier .env complet

# === Chemins ===
MATH_PDF_PATH=./model/livre_2011.pdf
MATH_DB_DIR=./db/chroma_db_math_v3_1
MATH_LOG_DIR=./logs

# === Collection ChromaDB ===
MATH_COLLECTION_NAME=math_course_v3_1

# === Chunking ===
MATH_CHUNK_SIZE=1000
MATH_CHUNK_OVERLAP=150

# === Modèles ===
EMBED_MODEL_NAME=mxbai-embed-large:latest
MATH_LLM_NAME=deepseek-v3.1:671b-cloud

# === Reranker ===
MATH_USE_RERANKER=1
MATH_RERANKER_MODEL=BAAI/bge-reranker-base

# === Query Rewriting ===
MATH_REWRITE=1
MATH_REWRITE_LLM_NAME=  # Vide = utilise le modèle principal

# === Ollama ===
OLLAMA_HOST=http://localhost:11434
OLLAMA_API_KEY=  # Optionnel

# === UI CLI ===
MATH_CLI_RICH=1
MATH_CLI_AUTO_LINK=0
MATH_CLI_DEBUG=0

# === UI GUI ===
MATH_GUI_WIDTH=1200
MATH_GUI_HEIGHT=800
MATH_GUI_SIDEBAR_WIDTH=330
MATH_GUI_DARK_THEME=1

# === Divers ===
PYTHONPATH=${PYTHONPATH}:$(pwd)
```

## 🎯 Workflows courants

### Workflow 1 : Premier lancement
```bash
# 1. Installation
cp .env.example .env
uv pip install -e .
python scripts/migrate.py

# 2. Vérification
./test_installation.sh
python scripts/diagnostic.py

# 3. Initialisation
ollama pull deepseek-v3.1:671b-cloud
ollama pull mxbai-embed-large:latest
python scripts/rebuild_db.py --force

# 4. Test
python scripts/run_cli.py
```

### Workflow 2 : Développement quotidien
```bash
# Lancer Ollama
ollama serve &

# Lancer le CLI en mode debug
python scripts/run_cli.py
# /debug on

# Ou lancer le GUI
python scripts/run_gui.py
```

### Workflow 3 : Mise à jour du code
```bash
# Sauvegarder le log
# Dans CLI : /log logs/backup.jsonl

# Pull des changements
git pull

# Réinstaller les dépendances
uv pip install -e .

# Relancer les tests
./test_installation.sh
```

### Workflow 4 : Problèmes/Bugs
```bash
# 1. Diagnostic
python scripts/diagnostic.py > diagnostic.txt

# 2. Mode debug
python scripts/run_cli.py
# /debug on

# 3. Consulter le troubleshooting
cat TROUBLESHOOTING.md

# 4. Reconstruire si nécessaire
python scripts/rebuild_db.py --force
```

---

**Dernière mise à jour** : 2025-01-30  
**Version** : 3.1