# 🚀 Démarrage rapide - Math RAG (Version modulaire)

## ✅ Prérequis

- Python 3.11+
- Node.js 18+
- Ollama installé avec les modèles :
  - `deepseek-v3.1:671b-cloud` (génération)
  - `mxbai-embed-large:latest` (embeddings)

## 📦 Installation

### 1. Backend Python
```bash
# Retour au dossier racine
cd /home/se/test_ollama_rag

# Activer l'environnement virtuel (si nécessaire)
# python -m venv venv
# source venv/bin/activate

# Installer les dépendances (si pas déjà fait)
pip install fastapi uvicorn langchain langchain-ollama langchain-chroma chromadb sse-starlette pymupdf pypdf python-multipart
```

### 2. Frontend Next.js
```bash
cd client

# Installer les dépendances
npm install

# Dépendances principales déjà dans package.json :
# - next, react, react-dom
# - @tanstack/react-query (ajouté manuellement par l'utilisateur)
# - framer-motion
# - react-markdown, remark-math, remark-gfm, rehype-katex
# - katex
# - tailwindcss
```

## 🎬 Lancement

### Terminal 1 : Backend FastAPI
```bash
cd /home/se/test_ollama_rag
python server.py
```

Attendre le message :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 : Frontend Next.js
```bash
cd /home/se/test_ollama_rag/client
npm run dev
```

Attendre le message :
```
✓ Ready in 2.3s
➜ Local:   http://localhost:3000
```

## 🌐 Accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Health check** : http://localhost:8000/health

## 🧪 Test rapide

### 1. Vérifier le backend
```bash
curl http://localhost:8000/health
```

Réponse attendue :
```json
{"ok":true,"model":"deepseek-v3.1:671b-cloud"}
```

### 2. Ouvrir le frontend
```
http://localhost:3000
```

Vous devriez voir :
- ✅ Header avec "Backend OK" (point vert)
- ✅ Onglets de navigation (Chat, Fiche, etc.)
- ✅ Panel Chat par défaut

### 3. Tester le streaming
1. Aller dans l'onglet **Chat** 💬
2. Saisir : "Comment démontrer qu'une suite converge ?"
3. Cliquer sur "Poser la question"
4. Observer le streaming en temps réel

## 📁 Structure du projet (nouvelle version)

```
/home/se/test_ollama_rag/
├── server.py                  # 🔴 Backend FastAPI
├── math_course_rag_v2.py      # 🔴 RAG avec ChromaDB
├── prompts.py                 # 🔴 Prompts pour le LLM
├── livre_2011.pdf             # 📖 PDF du cours (1268 pages)
├── chroma_db_math_v2/         # 💾 Vector store (2994 chunks)
│
└── client/                    # 🟢 Frontend Next.js
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx     # Layout avec Providers
    │   │   ├── page.tsx       # Page principale
    │   │   └── MathRagApp.tsx # Composant principal (55 lignes)
    │   │
    │   ├── components/
    │   │   ├── Providers.tsx  # TanStack Query Provider
    │   │   ├── ui/            # 7 composants UI réutilisables
    │   │   └── features/      # 9 composants métier (panels)
    │   │
    │   ├── hooks/             # 3 custom hooks
    │   ├── lib/               # 4 utilitaires
    │   ├── types/             # Définitions TypeScript
    │   └── styles/            # CSS markdown + math
    │
    ├── tsconfig.json          # Config TypeScript (@/ alias)
    ├── package.json
    │
    ├── ARCHITECTURE.md        # 📘 Documentation architecture
    ├── MIGRATION.md           # 📗 Guide de migration
    └── DEMARRAGE.md           # 📙 Guide démarrage (ancien)
```

## 🎯 Fonctionnalités disponibles

### 7 Panels interactifs

1. **💬 Chat** - Q&A avec filtres (doc type, chapitre, k)
2. **📝 Fiche** - Génération de fiches d'exercices (thème, niveau)
3. **✅ Révision** - Correction de fiches complétées
4. **🧮 Formule** - Recherche de formules mathématiques
5. **📋 Examen** - Génération d'examens (multi-chapitres, durée)
6. **📖 Cours** - Résumés de cours (notion, niveau de détail)
7. **🎯 Note** - Évaluation de travaux d'élèves

### Caractéristiques techniques

- ✅ **Streaming SSE** - Réponses en temps réel
- ✅ **TanStack Query** - Gestion cache et API
- ✅ **Persistance** - Formulaires sauvegardés dans localStorage
- ✅ **Health check** - Vérification backend toutes les 30s
- ✅ **Markdown + KaTeX** - Rendu formules mathématiques
- ✅ **Animations** - Framer Motion pour les transitions
- ✅ **Dark UI** - Interface sombre moderne
- ✅ **Responsive** - Design adaptatif

## 🐛 Debugging

### Backend ne démarre pas
```bash
# Vérifier les ports
lsof -i :8000

# Vérifier Ollama
ollama list

# Lancer Ollama si nécessaire
ollama serve
```

### Frontend ne démarre pas
```bash
# Nettoyer et réinstaller
cd client
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

### Point rouge "Backend hors ligne"
1. Vérifier que `server.py` tourne bien
2. Tester : `curl http://localhost:8000/health`
3. Vérifier les logs du backend dans le terminal
4. Vérifier que les modèles Ollama sont téléchargés

### Pas de streaming
1. Ouvrir la console navigateur (F12)
2. Chercher les logs avec emojis (🚀 📡 📥)
3. Vérifier l'URL construite
4. Vérifier la réponse réseau dans l'onglet Network

## 📊 Performance

- **Vector store** : 2994 chunks indexés
- **Embedding model** : mxbai-embed-large (334M)
- **LLM** : deepseek-v3.1:671b-cloud
- **Chunk size** : 1000 caractères (overlap 150)
- **Réponse moyenne** : 5-15 secondes selon complexité

## 🔄 Comparaison versions

| Version | Fichiers | Lignes (composant principal) | Architecture |
|---------|----------|------------------------------|--------------|
| **Ancienne** | 1 | 747 | Monolithique |
| **Nouvelle** | 35+ | 55 | Modulaire |

## 📚 Documentation complète

- **ARCHITECTURE.md** - Structure détaillée du code
- **MIGRATION.md** - Guide de migration de l'ancien code
- **DEBUG.md** - Guide de débogage approfondi
- **IMPROVEMENTS.md** - Historique des améliorations

## 💡 Conseils

### Pour développer
```bash
# Terminal 1 : Backend avec auto-reload
cd /home/se/test_ollama_rag
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 : Frontend avec fast refresh
cd client
npm run dev
```

### Pour tester
```bash
# Tester un endpoint spécifique
curl "http://localhost:8000/chat?question=test&k=3" -N

# Vérifier le RAG
curl http://localhost:8000/rag_check
```

### Pour optimiser
- Ajuster `k` (nombre de chunks) selon le besoin
- Utiliser les filtres `doc_type` et `chapter` pour cibler
- Activer MMR pour diversifier les résultats

## ✨ Nouveautés de la version modulaire

1. **Architecture professionnelle** - Code organisé par responsabilité
2. **TypeScript strict** - Types partout
3. **Composants réutilisables** - UI library interne
4. **TanStack Query** - Cache et optimisations
5. **Hooks customs** - Logique encapsulée
6. **Imports propres** - Alias `@/` partout
7. **Debug amélioré** - Logs structurés

## 🎉 Prêt !

Lancez le backend, lancez le frontend, et profitez de votre assistant Math RAG ! 🚀

Pour toute question, consultez les autres fichiers de documentation.

Bon dev ! 💻
