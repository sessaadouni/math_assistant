# 🔧 Guide de dépannage - Math RAG v3.1

## 🚨 Problèmes courants et solutions

### 1. Erreur : `ModuleNotFoundError: No module named 'src'`

**Symptômes** :
```
ModuleNotFoundError: No module named 'src'
```

**Causes** :
- PYTHONPATH non configuré
- Script lancé depuis le mauvais répertoire

**Solutions** :

**Option A** : Ajouter le répertoire racine au PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python scripts/run_cli.py
```

**Option B** : Lancer depuis le répertoire racine
```bash
cd /path/to/test_ollama_rag/server
python scripts/run_cli.py
```

**Option C** : Utiliser les scripts fournis
```bash
./start_all.sh  # ou make cli / make gui
```

---

### 2. Erreur : `FileNotFoundError: PDF introuvable`

**Symptômes** :
```
FileNotFoundError: PDF introuvable: ./model/livre_2011.pdf
```

**Causes** :
- Le PDF n'est pas au bon endroit
- Le chemin dans .env est incorrect

**Solutions** :

**1. Vérifier l'emplacement du PDF** :
```bash
ls -lh model/livre_2011.pdf
```

**2. Si le PDF est ailleurs, mettre à jour .env** :
```bash
# .env
MATH_PDF_PATH="/chemin/absolu/vers/livre_2011.pdf"
```

**3. Ou créer un lien symbolique** :
```bash
ln -s /chemin/vers/pdf/livre_2011.pdf model/livre_2011.pdf
```

---

### 3. Erreur : `chromadb.errors.InvalidCollectionException`

**Symptômes** :
```
chromadb.errors.InvalidCollectionException: Collection not found
```

**Causes** :
- La base de données ChromaDB n'existe pas
- La base est corrompue

**Solutions** :

**1. Reconstruire la base de données** :
```bash
python scripts/rebuild_db.py --force
```

**2. Vérifier que le répertoire db existe** :
```bash
ls -lh db/chroma_db_math_v3_1/
```

**3. Si la corruption persiste** :
```bash
# Supprimer et recréer
rm -rf db/chroma_db_math_v3_1/
python scripts/rebuild_db.py --force
```

---

### 4. Erreur : `ConnectionError: Ollama not responding`

**Symptômes** :
```
ConnectionError: [Errno 111] Connection refused
```

**Causes** :
- Ollama n'est pas lancé
- Ollama écoute sur un port différent
- Le modèle n'est pas téléchargé

**Solutions** :

**1. Vérifier qu'Ollama est lancé** :
```bash
ollama list
```

**2. Si Ollama n'est pas lancé** :
```bash
ollama serve
```

**3. Vérifier les modèles disponibles** :
```bash
ollama list
```

**4. Télécharger les modèles nécessaires** :
```bash
ollama pull deepseek-v3.1:671b-cloud
ollama pull mxbai-embed-large:latest
```

**5. Vérifier le host dans .env** :
```bash
# .env
OLLAMA_HOST=http://localhost:11434  # Adapter si besoin
```

---

### 5. Erreur : `ImportError: cannot import name 'QWebEngineView'`

**Symptômes** :
```
ImportError: cannot import name 'QWebEngineView' from 'PySide6.QtWebEngineWidgets'
```

**Causes** :
- PySide6-WebEngine n'est pas installé

**Solutions** :

**1. Installer PySide6-WebEngine** :
```bash
uv pip install PySide6-WebEngine
# ou
pip install PySide6-WebEngine
```

**2. Fallback automatique** :
Le GUI utilise automatiquement `QTextBrowser` si WebEngine n'est pas disponible (pas de rendu LaTeX).

---

### 6. GUI : Fenêtre noire ou styles incorrects

**Symptômes** :
- Fenêtre entièrement noire
- Texte illisible
- Styles Qt non appliqués

**Causes** :
- Thème système incompatible
- Problème de Qt StyleSheets

**Solutions** :

**1. Forcer le thème dark** :
```bash
# .env
MATH_GUI_DARK_THEME=1
```

**2. Réinitialiser les styles** :
Dans `src/ui/gui/styles.py`, vérifier que `GLOBAL_STYLE` est bien appliqué.

**3. Tester avec un thème Qt différent** :
```python
# Dans app.py, ajouter avant MainWindow()
app.setStyle('Fusion')
```

---

### 7. CLI : Caractères bizarres ou couleurs absentes

**Symptômes** :
```
←[94m▶←[0m Question:
```

**Causes** :
- Terminal ne supporte pas les codes ANSI
- Variable `TERM` incorrecte

**Solutions** :

**1. Vérifier le terminal** :
```bash
echo $TERM
# Devrait être xterm-256color ou similaire
```

**2. Forcer les couleurs** :
```bash
export TERM=xterm-256color
python scripts/run_cli.py
```

**3. Désactiver Rich si problème persiste** :
Dans `src/core/config.py` :
```python
ui_config.cli_rich_enabled = False
```

---

### 8. Erreur : `PermissionError` lors de la sauvegarde de logs

**Symptômes** :
```
PermissionError: [Errno 13] Permission denied: './logs/session.jsonl'
```

**Causes** :
- Dossier logs inexistant ou sans permissions

**Solutions** :

**1. Créer le dossier logs** :
```bash
mkdir -p logs
chmod 755 logs
```

**2. Vérifier les permissions** :
```bash
ls -ld logs/
```

**3. Utiliser un autre chemin** :
```bash
# .env
MATH_LOG_DIR=/tmp/math_rag_logs
```

---

### 9. Performance : Réponses très lentes

**Symptômes** :
- Chaque réponse prend plus de 30 secondes
- Le système freeze pendant la génération

**Causes** :
- Modèle trop gros pour le hardware
- Pas de GPU disponible
- Trop de documents à retriever

**Solutions** :

**1. Utiliser un modèle plus petit** :
```bash
# .env
MATH_LLM_NAME=llama3.2:3b
```

**2. Réduire le nombre de documents** :
Dans `src/core/config.py` :
```python
rag_config.top_k = 3  # Au lieu de 5
```

**3. Désactiver le reranker** :
```bash
# .env
MATH_USE_RERANKER=0
```

**4. Utiliser un GPU si disponible** :
```bash
# Vérifier que Ollama utilise le GPU
ollama ps
```

---

### 10. Erreur : `UnicodeDecodeError` lors de la lecture du PDF

**Symptômes** :
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Causes** :
- Le PDF contient des caractères spéciaux
- Problème d'encodage lors de l'extraction

**Solutions** :

**1. Forcer un encodage** :
Dans `src/core/rag_engine.py`, modifier l'extraction PDF pour gérer les erreurs :
```python
# Ajouter errors='ignore' lors de la lecture
text = extract_pdf_text(pdf_path, errors='ignore')
```

**2. Nettoyer le PDF** :
```bash
# Utiliser pdftk ou similaire pour nettoyer
pdftk livre_2011.pdf output livre_2011_clean.pdf
```

---

### 11. GUI : LaTeX ne s'affiche pas

**Symptômes** :
- Les formules mathématiques s'affichent en texte brut
- Pas de rendu KaTeX

**Causes** :
- QWebEngineView non disponible
- CDN KaTeX bloqué
- JavaScript désactivé

**Solutions** :

**1. Vérifier que WebEngine est installé** :
```bash
python -c "from PySide6.QtWebEngineWidgets import QWebEngineView; print('OK')"
```

**2. Vérifier la connexion internet** :
```bash
curl -I https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css
```

**3. Utiliser un CDN local (avancé)** :
Télécharger KaTeX localement et modifier `KATEX_HTML_TEMPLATE` dans `styles.py`.

---

### 12. Erreur : `TypeError: argument of type 'NoneType' is not iterable`

**Symptômes** :
```
TypeError: argument of type 'NoneType' is not iterable
```

**Causes** :
- Métadonnées manquantes dans les documents
- Réponse vide du LLM

**Solutions** :

**1. Ajouter des vérifications nulles** :
Dans le code concerné, ajouter :
```python
if metadata is None:
    metadata = {}
```

**2. Vérifier que le LLM répond** :
```bash
ollama run deepseek-v3.1:671b-cloud "Test"
```

**3. Relancer avec debug activé** :
```bash
python scripts/run_cli.py
# Puis dans le CLI
/debug on
```

---

## 🔍 Diagnostic automatique

Pour un diagnostic complet, lancer :
```bash
python scripts/diagnostic.py
```

Ce script vérifie :
- ✅ Configuration de l'environnement
- ✅ Dépendances installées
- ✅ Ollama disponible et modèles présents
- ✅ Base de données ChromaDB
- ✅ PDF du cours
- ✅ Imports Python
- ✅ Permissions des fichiers

---

## 📝 Logs et debugging

### Activer le mode debug

**CLI** :
```bash
python scripts/run_cli.py
# Dans le CLI
/debug on
```

**GUI** :
Cocher la case "Mode debug" dans les options.

**Programmatique** :
```python
from src.core.config import ui_config
ui_config.cli_debug = True
```

### Consulter les logs

**Emplacement par défaut** :
```bash
ls -lh logs/
```

**Lire le dernier log** :
```bash
tail -f logs/session.jsonl
# ou
jq . logs/session.jsonl
```

---

## 🆘 Obtenir de l'aide

Si aucune solution ci-dessus ne fonctionne :

1. **Consulter la documentation** :
   - `README_REFACTORED.md`
   - `QUICKSTART.md`
   - `MIGRATION.md`
   - `GUI_IMPROVEMENTS.md`

2. **Lancer le diagnostic** :
   ```bash
   python scripts/diagnostic.py > diagnostic_output.txt
   ```

3. **Créer un rapport de bug** avec :
   - Sortie du diagnostic
   - Message d'erreur complet
   - Commande exacte exécutée
   - Système d'exploitation et version Python
   - Contenu du fichier .env (sans les secrets)

---

## ✅ Checklist de vérification rapide

Avant de chercher de l'aide, vérifier :

- [ ] Python 3.10+ installé : `python --version`
- [ ] Dépendances installées : `uv pip list`
- [ ] Ollama lancé : `ollama list`
- [ ] Modèles téléchargés : `ollama list | grep deepseek`
- [ ] PDF présent : `ls model/livre_2011.pdf`
- [ ] Base de données présente : `ls db/chroma_db_math_v3_1/`
- [ ] Fichier .env créé et configuré : `cat .env`
- [ ] Scripts exécutables : `ls -l scripts/*.py`
- [ ] Imports fonctionnent : `python -c "from src.core.config import rag_config"`

Si tout est ✅, le système devrait fonctionner !

---

**Dernière mise à jour** : 2025-01-30  
**Version** : 3.1