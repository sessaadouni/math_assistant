# Système RAG pour Cours de Mathématiques

## 📚 Description

Ce système RAG (Retrieval-Augmented Generation) permet d'interroger intelligemment un cours de mathématiques complet au format PDF. Il extrait et indexe automatiquement le contenu (sommaire, cours, exercices, méthodes) et permet de poser des questions en langage naturel.

## 🎯 Fonctionnalités

- **Chargement automatique de PDF** : Extraction complète du contenu
- **Découpage intelligent** : Segmentation en chunks avec contexte préservé
- **Classification automatique** : Détection du type de contenu (exercice, méthode, théorie, etc.)
- **Recherche vectorielle** : Récupération des passages les plus pertinents
- **Filtrage par type** : Recherche ciblée (exercices uniquement, méthodes, etc.)
- **Assistant IA** : Réponses pédagogiques adaptées au contexte mathématique

## 📋 Prérequis

```bash
# Installer les dépendances
pip install langchain-ollama langchain-chroma langchain-community pypdf chromadb
```

Vous devez également avoir Ollama installé avec les modèles :
- `mxbai-embed-large:latest` (pour les embeddings)
- `deepseek-v3.1:671b-cloud` (pour la génération de réponses)

## 🚀 Installation et utilisation

### Étape 1 : Préparer votre PDF

Placez votre fichier PDF de cours de mathématiques dans le dossier du projet et nommez-le `cours_mathematiques.pdf` (ou modifiez le chemin dans `math_course_rag.py`).

### Étape 2 : Indexer le cours

```bash
# Premier lancement : indexation du PDF
python math_course_rag.py
```

Cette étape :
- Charge toutes les pages du PDF
- Découpe le contenu en chunks intelligents
- Détecte automatiquement le type de chaque chunk (exercice, méthode, théorie, etc.)
- Crée une base vectorielle ChromaDB dans `./chroma_db_math`

### Étape 3 : Utiliser l'assistant interactif

```bash
python math_assistant.py
```

## 💡 Exemples d'utilisation

### Questions générales
```
💬 Votre question: Comment démontrer qu'une fonction est continue ?
```

### Recherche dans les exercices uniquement
```
💬 Votre question: /exercice limite de fonction
```

### Recherche dans les méthodes
```
💬 Votre question: /méthode résolution équation différentielle
```

### Recherche dans la théorie
```
💬 Votre question: /théorie théorème des valeurs intermédiaires
```

## 🏗️ Structure du projet

```
.
├── math_course_rag.py          # Configuration et indexation du PDF
├── math_assistant.py           # Interface interactive de questions/réponses
├── cours_mathematiques.pdf     # Votre cours (à placer ici)
└── chroma_db_math/            # Base vectorielle (créée automatiquement)
```

## 🎓 Types de contenu détectés automatiquement

Le système détecte et catégorise automatiquement :

- **Sommaire** : Tables des matières, chapitres
- **Théorie** : Théorèmes, définitions, propriétés, lemmes
- **Méthodes** : Techniques, procédures, méthodes de résolution
- **Exercices** : Problèmes, exercices d'application
- **Exemples** : Exemples et applications
- **Cours** : Contenu général du cours

## ⚙️ Configuration avancée

### Modifier la taille des chunks

Dans `math_course_rag.py` :

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Augmentez pour des chunks plus longs
    chunk_overlap=200,    # Chevauchement entre chunks
)
```

### Modifier le nombre de documents récupérés

Dans `math_assistant.py` :

```python
retriever = create_retriever(k=5)  # Changez k pour récupérer plus/moins de docs
```

### Changer le modèle LLM

Dans `math_assistant.py` :

```python
model = OllamaLLM(model="votre-modele-prefere")
```

## 🔧 API Python

Vous pouvez aussi utiliser le système programmatiquement :

```python
from math_course_rag import retriever, create_retriever
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Récupérer des documents pertinents
docs = retriever.invoke("Comment calculer une dérivée ?")

# Filtrer par type
exercice_retriever = create_retriever(k=3, doc_type="exercice")
exercices = exercice_retriever.invoke("équation du second degré")

# Utiliser avec un LLM
model = OllamaLLM(model="deepseek-v3.1:671b-cloud")
# ... votre logique
```

## 🎯 Cas d'usage typiques

1. **Révision avant un examen** : "Rappelle-moi les formules de trigonométrie"
2. **Aide aux devoirs** : "/exercice limite avec forme indéterminée"
3. **Compréhension de concepts** : "Explique-moi le théorème de Thalès"
4. **Méthodologie** : "/méthode comment étudier le signe d'une fonction"

## 📊 Avantages du système

- ✅ Pas besoin de parcourir tout le PDF manuellement
- ✅ Réponses contextualisées avec références aux pages
- ✅ Filtrage intelligent par type de contenu
- ✅ Réutilisable pour n'importe quel cours de maths
- ✅ Base vectorielle persistante (pas de réindexation à chaque fois)

## 🔄 Réindexer le cours

Si vous modifiez le PDF, supprimez le dossier de la base vectorielle :

```bash
rm -rf chroma_db_math
python math_course_rag.py
```

## 📝 Notes

- La première indexation peut prendre quelques minutes selon la taille du PDF
- La qualité des réponses dépend de la qualité et structure du PDF source
- Les métadonnées enrichies permettent un filtrage précis du contenu
