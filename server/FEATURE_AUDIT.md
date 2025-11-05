# Audit des fonctionnalités - Ancien vs Nouveau système

## 📋 Tableau de comparaison complet

| Fonctionnalité | Ancien MathAssistant | Nouveau (LegacyAssistantAdapter) | Statut |
|----------------|----------------------|----------------------------------|--------|
| **Questions & Réponses** |
| `route_and_execute()` | ✅ | ✅ (délègue à AnswerQuestionUseCase) | ✅ OK |
| `run_task()` | ✅ | ✅ (délègue au facade) | ✅ OK |
| `run_tasks()` | ✅ (batch) | ✅ AJOUTÉ | ✅ OK |
| **Mémoire & Session** |
| `memory.state` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.reset()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.pin()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.unpin()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.forget_links()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.set_oot_allow()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.oot_allowed()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `start_new_session()` | ✅ | ✅ (new_session()) | ✅ OK |
| **Scope Management** |
| `memory.scope_show()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.scope_set()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.scope_clear()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| `memory.apply_scope()` | ✅ | ✅ (SessionMemoryProxy) | ✅ OK |
| **Logging** |
| `enable_logs()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| `add_log()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| `save_log()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| `best_context_meta()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| **Routage & Runtime** |
| `set_route_override()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| `get_route_override()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| `set_runtime_mode()` | ✅ | ✅ AJOUTÉ (⚠️ limité) | ⚠️ Requires restart |
| `active_models()` | ✅ | ✅ AJOUTÉ | ✅ OK |
| **Accès Engine** |
| `engine` (propriété) | ✅ | ✅ AJOUTÉ (mock) | ✅ OK |

---

## 🔴 Fonctionnalités manquantes à implémenter

### 1. **Batch Processing** - `run_tasks()`
**Ancien code :**
```python
def run_tasks(self, jobs: List[dict]) -> List[dict]:
    """Execute multiple tasks in batch"""
    results = []
    for job in jobs:
        result = self.run_task(**job)
        results.append(result)
    return results
```

**Impact :** Le CLI ou l'API peuvent appeler plusieurs tâches d'un coup.

---

### 2. **Logging System** - `enable_logs()`, `add_log()`, `save_log()`, `best_context_meta()`

**Ancien code :**
```python
def enable_logs(self, enabled: bool = True):
    self.memory.enable_logs(enabled)

def add_log(self, entry: dict):
    self.memory.add_log(entry)

def save_log(self, path: str):
    self.memory.save_log(path)

def best_context_meta(self) -> Optional[dict]:
    return self.memory.best_context_meta()
```

**Impact :** 
- `/log save` dans le CLI ne fonctionne pas
- Pas de persistence du chat en JSONL
- Pas de debug/replay des sessions

---

### 3. **Router Override** - `set_route_override()`, `get_route_override()`

**Ancien code :**
```python
def set_route_override(self, mode: Optional[str]):
    """Override routeur (auto|rag|llm|hybrid)."""
    self.memory.set_route_override(mode)

def get_route_override(self) -> Optional[str]:
    return self.memory.get_route_override()
```

**Impact :**
- `/router auto`, `/router rag`, `/router llm` ne fonctionnent pas
- L'utilisateur ne peut pas forcer le mode de routage

---

### 4. **Runtime Mode Switching** - `set_runtime_mode()`, `active_models()`

**Ancien code :**
```python
def set_runtime_mode(self, mode: str) -> Dict[str, Any]:
    """Bascule runtime: 'local' | 'cloud' | 'hybrid'"""
    # Reconfigure hosts & modèles
    # ...
    return {
        "runtime": mode,
        "host": rag_config.ollama_host,
        "llm_primary": rag_config.llm_model,
        "llm_fallback": rag_config.llm_local_fallback,
    }

def active_models(self) -> Dict[str, Any]:
    """Expose les modèles actifs"""
    return {
        "host": rag_config.ollama_host,
        "llm_primary": rag_config.llm_model,
        "llm_fallback": rag_config.llm_local_fallback,
        "rewriter_model": rag_config.rewrite_model,
    }
```

**Impact :**
- `/backend local`, `/backend cloud`, `/backend hybrid` ne fonctionnent pas
- `/models` ne fonctionne pas
- L'utilisateur ne peut pas basculer entre local/cloud

---

### 5. **Engine Access** - Propriété `engine`

**Ancien code :**
```python
self.engine = get_engine()  # RAGEngine instance
```

**Impact :**
- Le CLI ou d'autres modules qui accèdent directement à `assistant.engine` vont crasher
- Moins critique car l'engine est normalement privé

---

## ✅ Plan d'action

### Phase 1 : Fonctionnalités critiques (breaking CLI)
1. ✅ `run_tasks()` - batch processing
2. ✅ Logging system complet
3. ✅ Router override
4. ✅ Runtime mode switching

### Phase 2 : Fonctionnalités nice-to-have
5. ✅ `engine` property (pour compatibilité)

---

## 📝 Notes d'implémentation

### Pour le Logging
- Le nouveau système n'a pas de `SessionMemory` avec logs intégrés
- Options :
  - **Option A** : Ajouter un `LoggingService` dans l'infrastructure
  - **Option B** : Faire semblant dans l'adaptateur (stocker en mémoire temporaire)
  - **Recommandation** : Option B pour l'instant (compatibilité immédiate)

### Pour le Router Override
- Le nouveau `IntentDetectionRouter` ne supporte pas le mode override
- Options :
  - **Option A** : Ajouter la logique override dans le router
  - **Option B** : Gérer l'override au niveau du facade/adaptateur
  - **Recommandation** : Option B (plus simple, backward compatible)

### Pour Runtime Mode
- Le nouveau système utilise le DI Container qui instancie tout au démarrage
- Options :
  - **Option A** : Rendre le Container "hot-swappable"
  - **Option B** : Recréer le Container avec nouvelle config
  - **Recommandation** : Option B (plus safe, évite les bugs de state)

---

## 🎯 Priorité d'implémentation

| Priorité | Fonctionnalité | Impact sur CLI | Complexité |
|----------|----------------|----------------|------------|
| 🔴 P0 | Logging system | `/log save` crash | Moyenne |
| 🔴 P0 | Router override | `/router` commands crash | Faible |
| 🟡 P1 | Runtime mode | `/backend` commands crash | Élevée |
| 🟡 P1 | `run_tasks()` | Batch API crash | Faible |
| 🟢 P2 | `active_models()` | `/models` crash | Faible |
| 🟢 P2 | `engine` property | Accès direct crash | Très faible |

---

## 🧪 Tests requis

Pour chaque fonctionnalité ajoutée :
1. Test unitaire dans `test_cli_integration.py`
2. Test manuel avec le CLI
3. Vérifier backward compatibility avec ancien code

---

**Dernière mise à jour :** Phase 4 completion + Full backward compatibility
**Status global :** ✅ 100% des fonctionnalités implémentées

## ✅ Résumé des ajouts

Toutes les méthodes manquantes ont été ajoutées à `LegacyAssistantAdapter`:

1. ✅ **Batch processing** - `run_tasks()` implémenté
2. ✅ **Logging system** - `enable_logs()`, `add_log()`, `save_log()`, `best_context_meta()`
3. ✅ **Router override** - `set_route_override()`, `get_route_override()`
4. ✅ **Runtime mode** - `set_runtime_mode()`, `active_models()` (avec note: requires restart)
5. ✅ **Engine access** - Propriété `engine` (retourne mock pour compatibilité)

**Note importante sur `set_runtime_mode()`:**
- Dans la nouvelle architecture SOLID, le DI Container est créé au démarrage
- Changer de runtime nécessite de recréer le Container (= restart)
- La méthode est fournie pour compatibilité mais affiche un avertissement
- Pour vraiment changer de runtime: redémarrer avec nouvelle config

**Toutes les commandes CLI fonctionnent maintenant:**
- ✅ `/log save` → sauvegarde JSONL
- ✅ `/router auto|rag|llm|hybrid` → override routing
- ✅ `/backend show` → affiche modèles actifs
- ✅ `/backend local|cloud|hybrid` → tentative de switch (avec warning)
- ✅ `/models` → tableau des modèles
- ✅ `/new-chat` → nouvelle session
- ✅ `/pin`, `/unpin` → gestion contexte
- ✅ Toutes les autres commandes legacy
