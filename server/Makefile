# Makefile pour Math RAG Assistant v3.1
# Usage: make <commande>

.PHONY: help install cli gui server check rebuild clean test format

# Couleurs pour l'affichage
BOLD := \033[1m
GREEN := \033[32m
CYAN := \033[36m
YELLOW := \033[33m
RESET := \033[0m

# Configuration
PYTHON := python3
UV := uv
PORT := 8000
HOST := 0.0.0.0

help: ## Affiche cette aide
	@echo "$(BOLD)$(CYAN)Math RAG Assistant v3.1$(RESET)"
	@echo ""
	@echo "$(BOLD)Commandes disponibles:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}'

install: ## Installe les dépendances
	@echo "$(BOLD)$(GREEN)📦 Installation des dépendances...$(RESET)"
	@if command -v $(UV) > /dev/null; then \
		$(UV) sync; \
	else \
		$(PYTHON) -m pip install -e .; \
	fi
	@echo "$(GREEN)✅ Installation terminée$(RESET)"

install-dev: ## Installe les dépendances de développement
	@echo "$(BOLD)$(GREEN)📦 Installation dev...$(RESET)"
	@$(PYTHON) -m pip install -e ".[dev]"
	@echo "$(GREEN)✅ Installation dev terminée$(RESET)"

cli: ## Lance l'interface CLI
	@echo "$(BOLD)$(CYAN)🖥️  Lancement du CLI...$(RESET)"
	@$(PYTHON) scripts/run_cli.py

gui: ## Lance l'interface GUI
	@echo "$(BOLD)$(CYAN)🎨 Lancement du GUI...$(RESET)"
	@$(PYTHON) scripts/run_gui.py

server: ## Lance le serveur FastAPI
	@echo "$(BOLD)$(CYAN)🚀 Lancement du serveur...$(RESET)"
	@$(PYTHON) -m uvicorn server:app --host $(HOST) --port $(PORT) --reload

server-prod: ## Lance le serveur en mode production
	@echo "$(BOLD)$(CYAN)🚀 Lancement du serveur (production)...$(RESET)"
	@$(PYTHON) -m uvicorn server:app --host $(HOST) --port $(PORT) --workers 4

check: ## Vérifie l'état du système RAG
	@echo "$(BOLD)$(CYAN)🔍 Vérification du système...$(RESET)"
	@$(PYTHON) scripts/rebuild_db.py --check-only

rebuild: ## Reconstruit la base vectorielle
	@echo "$(BOLD)$(YELLOW)🔨 Reconstruction de la base...$(RESET)"
	@$(PYTHON) scripts/rebuild_db.py --force

rebuild-interactive: ## Reconstruit la base (avec confirmation)
	@echo "$(BOLD)$(YELLOW)🔨 Reconstruction interactive...$(RESET)"
	@$(PYTHON) scripts/rebuild_db.py

clean: ## Nettoie les fichiers temporaires
	@echo "$(BOLD)$(YELLOW)🧹 Nettoyage...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(RESET)"

clean-db: ## Supprime la base vectorielle
	@echo "$(BOLD)$(YELLOW)⚠️  Suppression de la base vectorielle...$(RESET)"
	@read -p "Êtes-vous sûr ? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -rf db/chroma_db_math_v3_1
	@echo "$(GREEN)✅ Base supprimée$(RESET)"

clean-all: clean clean-db ## Nettoyage complet (fichiers + DB)
	@echo "$(GREEN)✅ Nettoyage complet terminé$(RESET)"

test: ## Lance les tests
	@echo "$(BOLD)$(CYAN)🧪 Lancement des tests...$(RESET)"
	@$(PYTHON) -m pytest tests/ -v

test-cov: ## Lance les tests avec coverage
	@echo "$(BOLD)$(CYAN)🧪 Tests avec coverage...$(RESET)"
	@$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

format: ## Formate le code (black + isort)
	@echo "$(BOLD)$(CYAN)🎨 Formatage du code...$(RESET)"
	@$(PYTHON) -m black src/ scripts/
	@$(PYTHON) -m isort src/ scripts/
	@echo "$(GREEN)✅ Formatage terminé$(RESET)"

lint: ## Vérifie le code (flake8 + mypy)
	@echo "$(BOLD)$(CYAN)🔍 Vérification du code...$(RESET)"
	@$(PYTHON) -m flake8 src/ scripts/
	@$(PYTHON) -m mypy src/ scripts/

docs: ## Génère la documentation
	@echo "$(BOLD)$(CYAN)📚 Génération de la documentation...$(RESET)"
	@cd docs && make html
	@echo "$(GREEN)✅ Documentation générée dans docs/_build/html/$(RESET)"

env: ## Crée un fichier .env depuis .env.example
	@if [ ! -f .env ]; then \
		echo "$(BOLD)$(CYAN)📝 Création du fichier .env...$(RESET)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Fichier .env créé. N'oubliez pas de le personnaliser !$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  Le fichier .env existe déjà$(RESET)"; \
	fi

status: ## Affiche le statut du projet
	@echo "$(BOLD)$(CYAN)📊 Statut du projet$(RESET)"
	@echo ""
	@echo "$(BOLD)Configuration:$(RESET)"
	@if [ -f .env ]; then \
		echo "  ✅ .env présent"; \
	else \
		echo "  ❌ .env manquant (lancez: make env)"; \
	fi
	@echo ""
	@echo "$(BOLD)Base de données:$(RESET)"
	@if [ -d db/chroma_db_math_v3_1 ]; then \
		echo "  ✅ Base vectorielle présente"; \
		@du -sh db/chroma_db_math_v3_1 | awk '{print "  📊 Taille: " $$1}'; \
	else \
		echo "  ❌ Base vectorielle manquante (lancez: make rebuild)"; \
	fi
	@echo ""
	@echo "$(BOLD)PDF:$(RESET)"
	@if [ -f model/livre_2011.pdf ]; then \
		echo "  ✅ PDF présent"; \
		@du -sh model/livre_2011.pdf | awk '{print "  📊 Taille: " $$1}'; \
	else \
		echo "  ❌ PDF manquant"; \
	fi

logs: ## Affiche les derniers logs
	@echo "$(BOLD)$(CYAN)📋 Derniers logs:$(RESET)"
	@if [ -d logs ]; then \
		find logs -name "*.jsonl" -type f -exec ls -lh {} \; | tail -10; \
	else \
		echo "$(YELLOW)⚠️  Aucun log trouvé$(RESET)"; \
	fi

logs-clean: ## Nettoie les anciens logs
	@echo "$(BOLD)$(YELLOW)🧹 Nettoyage des logs...$(RESET)"
	@find logs -name "*.jsonl" -type f -mtime +30 -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Logs nettoyés (>30 jours)$(RESET)"

shell: ## Lance un shell Python avec imports
	@echo "$(BOLD)$(CYAN)🐍 Shell Python interactif$(RESET)"
	@$(PYTHON) -i -c "\
from src.core.rag_engine import get_engine; \
from src.assistant.assistant import get_assistant; \
from src.core.config import rag_config; \
engine = get_engine(); \
assistant = get_assistant(); \
print('✅ Imports chargés: engine, assistant, rag_config')"

watch-logs: ## Surveille les logs en temps réel
	@echo "$(BOLD)$(CYAN)👁️  Surveillance des logs (Ctrl+C pour quitter)$(RESET)"
	@tail -f logs/*/*.jsonl 2>/dev/null || echo "$(YELLOW)⚠️  Aucun log actif$(RESET)"

# Aliases
c: cli ## Alias pour cli
g: gui ## Alias pour gui
s: server ## Alias pour server
h: help ## Alias pour help