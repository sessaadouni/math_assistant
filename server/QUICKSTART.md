# ⚡ Démarrage rapide - Math RAG Assistant v3.1

Ce guide vous permet de démarrer en **5 minutes** !

---

## 🚀 Installation express

```bash
# 1. Cloner le projet
git clone <url>
cd test_ollama_rag/server

# 2. Installer les dépendances (choisir une méthode)
# Avec uv (recommandé - plus rapide)
uv sync

# Avec pip
pip install -e .

# 3. Configurer l'environnement
cp .env.example .env
# Éditer .env si nécessaire (optionnel pour démarrage local)

# 4. Indexer le PDF (première fois uniquement, ~2-3 min)
python scripts/rebuild_db.py --force

# 5. C'est prêt ! 🎉
```

---

## 💻 Lancer l'application

### Option 1 : Script interactif (le plus simple)

```bash
./start_all.sh
```

Puis choisir dans le menu :
- `1` pour le CLI
- `3` pour le serveur API
- `5` pour tout lancer ensemble

### Option 2 : Makefile (raccourcis pratiques)

```bash
# CLI
make cli

# Serveur
make server

# Diagnostic
make check
```

### Option 3 : Scripts Python

```bash
# CLI
python scripts/run_cli.py

# Serveur
python server.py

# GUI (si PySide6 installé)
python scripts/run_gui.py
```

---

## 🎓 Premiers pas avec le CLI

### Questions simples

```
💬 Ta question: Quelle est la définition d'un espace vectoriel ?

💬 Ta question: Théorème de Bolzano-Weierstrass

💬 Ta question: Comment résoudre une équation différentielle ?
```

### Filtrer les résultats

```
💬 Ta question: /exercice application du théorème de Thalès

💬 Ta question: /méthode résolution d'équations

💬 Ta question: /théorie définition d'un anneau
```

### Définir un contexte (scope)

```
💬 Ta question: /ch 21
💬 Ta question: /bloc théorème 21.3
💬 Ta question: Explique-moi ce théorème
# → Cherche automatiquement dans chapitre 21, théorème 21.3
```

### Suivis de conversation

```
💬 Ta question: Théorème de Leibniz pour le barycentre
# → Affiche le théorème

💬 Ta question: Donne-moi un exemple
# → Avec auto-link activé, cherche automatiquement
#    un exemple du théorème précédent

💬 Ta question: Et la démonstration ?
# → Continue dans le même contexte
```

### Commandes utiles

```
/pin          # Épingler le contexte (reste actif pour toutes les questions suivantes)
/unpin        # Désépingler
/forget       # Tout oublier
/new-chat     # Nouveau chat isolé avec auto-link
/log save     # Sauvegarder l'historique
/link on      # Activer l'auto-link des questions de suivi
/debug on     # Voir les détails techniques
q             # Quitter
```

---

## 🌐 Utiliser l'API

### Démarrer le serveur

```bash
python server.py

# Ou avec uvicorn directement
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Accéder à la documentation

Ouvrir dans le navigateur : **http://localhost:8000/docs**

### Exemples de requêtes

```bash
# Question simple
curl "http://localhost:8000/api/chat?question=théorème%20de%20Leibniz"

# Avec filtres
curl "http://localhost:8000/api/chat?question=exercice&doc_type=exercice&chapter=21"

# Générer une fiche
curl "http://localhost:8000/api/sheet?topic=intégrales&level=Prépa"

# Chercher une formule
curl "http://localhost:8000/api/formula?query=formule%20de%20Taylor"

# Health check
curl "http://localhost:8000/api/health"
```

### Utiliser en streaming (SSE)

Les endpoints renvoient du texte en streaming. Exemple avec `fetch` (JavaScript) :

```javascript
const evtSource = new EventSource(
  'http://localhost:8000/api/chat?question=théorème%20de%20Leibniz'
);

evtSource.onmessage = (event) => {
  console.log('Token:', event.data);
};
```

---

## ⚙️ Configuration rapide

### Modèles Ollama

**Local** (gratuit) :
```bash
# .env
OLLAMA_HOST=http://localhost:11434
MATH_LLM_NAME=qwen2.5:32b  # ou llama3.3:70b
```

**Cloud** (nécessite clé API) :
```bash
# .env
OLLAMA_HOST=https://ollama.com
OLLAMA_API_KEY=votre_clé_api
MATH_LLM_NAME=deepseek-v3.1:671b-cloud  # ou kimi-k2:1t-cloud
```

### Activer/désactiver le reranker

```bash
# .env
MATH_USE_RERANKER=1  # Activé (recommandé, +qualité mais +lent)
MATH_USE_RERANKER=0  # Désactivé (plus rapide)
```

---

## 🔍 Diagnostic

### Vérifier l'installation

```bash
python scripts/diagnostic.py
```

Affiche :
- ✅ Python, dépendances, fichiers
- ✅ Configuration (modèles, chemins)
- ✅ Connexion Ollama
- ✅ État de la base vectorielle

### Vérifier le système RAG

```bash
make check

# ou
python -m src.core.rag_engine
```

### Reconstruire la base

```bash
make rebuild

# ou avec confirmation
python scripts/rebuild_db.py

# ou force (sans confirmation)
python scripts/rebuild_db.py --force
```

---

## 🎯 Exemples d'utilisation

### Scénario 1 : Réviser un chapitre

```
💬 Ta question: /scope set chapter=21 type=théorie
✅ Portée mise à jour: chapter=21, type=théorie

💬 Ta question: Liste les théorèmes principaux
# → Affiche les théorèmes du chapitre 21

💬 Ta question: Théorème 21.3
# → Affiche le théorème 21.3

💬 Ta question: /pin
📌 Contexte épinglé

💬 Ta question: Donne un exemple
# → Cherche un exemple du théorème 21.3

💬 Ta question: Et des exercices d'application ?
# → Cherche des exercices liés au théorème 21.3
```

### Scénario 2 : Préparer une fiche

```
# Via CLI
💬 Ta question: /ch 15
💬 Ta question: Fais-moi une synthèse complète sur les séries

# Via API
curl "http://localhost:8000/api/sheet?topic=séries&level=Prépa&chapter=15"
```

### Scénario 3 : Corriger un exercice

```
# Via API
curl -X POST "http://localhost:8000/api/grade" \
  -H "Content-Type: application/json" \
  -d '{
    "statement": "Résoudre : x² - 5x + 6 = 0",
    "student_answer": "x = 2 ou x = 3, car (x-2)(x-3) = 0"
  }'
```

---

## 🐛 Problèmes courants

### "PDF non trouvé"

```bash
# Vérifier le chemin dans .env
cat .env | grep MATH_PDF_PATH

# Corriger si besoin
MATH_PDF_PATH=./model/livre_2011.pdf
```

### "ModuleNotFoundError"

```bash
# Réinstaller les dépendances
uv sync
# ou
pip install -e .
```

### "Model not found" (Ollama)

```bash
# Lister les modèles installés
ollama list

# Tirer un modèle
ollama pull qwen2.5:32b
```

### Base vectorielle corrompue

```bash
# Supprimer et reconstruire
rm -rf db/chroma_db_math_v3_1
make rebuild
```

### Serveur ne démarre pas

```bash
# Vérifier le port
lsof -i :8000

# Tuer le processus existant
kill -9 $(lsof -t -i:8000)

# Ou utiliser un autre port
uvicorn server:app --port 8001
```

---

## 📚 Pour aller plus loin

- **Documentation complète** : [README_REFACTORED.md](./README_REFACTORED.md)
- **Guide de migration** : [MIGRATION.md](./MIGRATION.md)
- **Swagger API** : http://localhost:8000/docs
- **Configuration** : [.env.example](./.env.example)

---

## 💡 Astuces

1. **Auto-link** : Activez `/link on` pour des conversations fluides
2. **Pin** : Utilisez `/pin` pour fixer un contexte longtemps
3. **Scope** : Définissez un scope global pour filtrer toutes vos recherches
4. **Logs** : Sauvegardez vos sessions avec `/log save`
5. **Debug** : Activez `/debug on` si les résultats ne sont pas pertinents

---

## 🎉 C'est parti !

Vous êtes prêt à utiliser l'assistant. Bon apprentissage ! 🚀

```bash
# Lancer le CLI
make cli

# Ou tout démarrer
./start_all.sh
```

---

**Questions ? Problèmes ?**  
→ Lancez `python scripts/diagnostic.py` pour un diagnostic complet  
→ Consultez [README_REFACTORED.md](./README_REFACTORED.md) pour plus de détails