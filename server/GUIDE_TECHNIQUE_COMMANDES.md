# 🔧 Guide Technique - Ajout de Nouvelles Commandes de Cours

**Public**: Développeurs souhaitant comprendre ou étendre le système  
**Date**: 2025-11-06

---

## 🎯 Vue d'Ensemble

Ce guide explique comment les commandes `/mini-cours` et `/cours` ont été intégrées,
et comment ajouter de nouvelles commandes similaires.

---

## 📐 Architecture en Couches

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI (Interface)                          │
│  src/ui/cli/app.py + styles.py                             │
│  • Parsing commandes                                        │
│  • Extraction paramètres (notion, niveau)                  │
│  • Affichage résultats                                      │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Facade (Orchestration)                     │
│  src/application/facades/math_assistant_facade.py           │
│  • explain_course(topic, level, ...)                       │
│  • build_course(topic, level, ...)                         │
│  • Routage vers use cases                                  │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Use Cases (Logique)                        │
│  src/application/use_cases/explain_course.py                │
│  src/application/use_cases/build_course.py                  │
│  • Récupération documents RAG                              │
│  • Formatage contexte                                       │
│  • Appel LLM avec prompt                                   │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Prompts (Templates)                        │
│  src/prompts/course/__init__.py                             │
│  • CourseExplainPrompt (mini-cours)                        │
│  • CourseBuildPrompt (cours complet)                       │
│  • Variables: {topic}, {level}, {context}                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Détail de l'Implémentation

### 1. Prompts (Couche Template)

**Fichier**: `src/prompts/course/__init__.py`

#### A. Mini-cours (`CourseExplainPrompt`)
```python
class CourseExplainPrompt(CoursePrompt):
    """Explain a course topic with pedagogy (quick mini-course, 10-15min read)"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu écris un MINI-COURS ciblé et pédagogique sur : "{topic}"
Niveau : {level}.

[Contexte du cours]
{context}

OBJECTIF : Explication rapide (10-15min de lecture) pour comprendre l'essentiel.
...
Structure CONCISE :
═══════════════════
1) L'essentiel en 3 phrases
2) Définitions clés (seulement les indispensables)
...
7) Pour aller plus loin
""")
```

**Variables attendues**:
- `topic` (str): La notion à expliquer
- `level` (str): Le niveau (prépa, L2, terminale, etc.)
- `context` (str): Documents RAG formatés

**Sortie**: Texte Markdown structuré (10-15min lecture)

#### B. Cours complet (`CourseBuildPrompt`)
```python
class CourseBuildPrompt(CoursePrompt):
    """Build a complete, rigorous course (double track: CPGE-proof + Applied-Engineering)"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu écris un COURS COMPLET et rigoureux sur : "{topic}"
Niveau : {level}.

IMPORTANT : Ce n'est PAS un mini-cours, mais un cours EXHAUSTIF avec deux pistes parallèles :
- Piste CPGE-preuve : définitions ε-δ, énoncés précis, esquisses de preuves
- Piste Appli-ingé : procédures opérationnelles, heuristiques, erreurs courantes

Structure OBLIGATOIRE :
═══════════════════════
1) Introduction / plan
...
9) Mini-révision interactive
""")
```

**Variables attendues**: Identiques au mini-cours  
**Sortie**: Texte Markdown exhaustif (30-45min lecture)

---

### 2. Use Cases (Couche Logique)

**Fichier**: `src/application/use_cases/explain_course.py`

```python
class ExplainCourseUseCase:
    """
    Use case for explaining course topics.
    
    Flow:
    1. Retrieve relevant course documents based on topic
    2. Get CourseExplainPrompt from registry
    3. Generate pedagogical explanation
    """
    
    def execute(self, request: ExplainCourseRequest) -> Answer:
        # 1. Récupération documents RAG
        docs = self.retriever.retrieve(
            query=request.topic,
            filters=filters_dict,
            k=8  # Moins de docs pour mini-cours
        )
        
        # 2. Formatage contexte
        context = self._format_context(docs)
        
        # 3. Récupération prompt
        prompt_template = self.prompts.get_prompt("course_explain")
        
        # 4. Préparation variables
        variables = {
            "topic": request.topic,
            "level": request.level,
            "context": context,
        }
        
        # 5. Génération LLM
        explanation_text = self.llm.generate(
            prompt_template=prompt_template,
            variables=variables
        )
        
        return Answer(text=explanation_text, sources=docs, ...)
```

**Point clé**: Le use case reçoit `topic` ET `level` via la Request.

---

### 3. Facade (Couche Orchestration)

**Fichier**: `src/application/facades/math_assistant_facade.py`

```python
class MathAssistantFacade:
    def explain_course(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Mini-cours rapide (10-15min)"""
        use_case = self._get_use_case("explain_course")
        
        request = ExplainCourseRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def build_course(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Cours complet exhaustif (30-45min)"""
        use_case = self._get_use_case("build_course")
        
        request = BuildCourseRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
```

**Point clé**: La façade expose une API simple qui cache la complexité des use cases.

---

### 4. CLI (Couche Interface)

**Fichier**: `src/ui/cli/app.py`

```python
def handle_command(self, command: str) -> bool:
    """Traite les commandes spéciales"""
    
    # ----- Mini-cours (explain_course) -----
    if cmd.startswith("/mini-cours ") or cmd.startswith("/mini "):
        rest = cmd.split(" ", 1)[1].strip()
        
        # Extraction du niveau (optionnel)
        parts = rest.rsplit(maxsplit=1)
        levels = {"prépa", "terminale", "l1", "l2", "l3", ...}
        
        if len(parts) == 2 and parts[1].lower() in levels:
            notion, level = parts[0], parts[1]
        else:
            notion, level = rest, "prépa/terminale+"
        
        # Appel façade
        self.formatter.info(f"📚 Mini-cours (10-15min) - Niveau: {level}")
        payload = self.assistant.run_task("course_explain", notion, level=level)
        
        # Affichage
        self.formatter.sources_table(payload["docs"])
        self.formatter.answer(payload["answer"])
        return True
    
    # ----- Cours complet (build_course) -----
    if cmd.startswith("/cours "):
        # Même logique que mini-cours
        ...
```

**Points clés**:
1. **Parsing**: Séparer notion et niveau
2. **Extraction**: Détecter si le dernier mot est un niveau reconnu
3. **Appel façade**: Via `run_task()` qui route vers `explain_course()` ou `build_course()`
4. **Affichage**: Sources + Réponse formatées

---

## 🎨 Extraction du Niveau (Algorithme)

```python
# Entrée: "/mini-cours convergence uniforme prépa"
rest = "convergence uniforme prépa"

# Liste des niveaux reconnus
levels = {"prépa", "terminale", "l1", "l2", "l3", "licence", "cpge", ...}

# Split par la fin (rsplit)
parts = rest.rsplit(maxsplit=1)
# → ["convergence uniforme", "prépa"]

# Vérification
if len(parts) == 2 and parts[1].lower() in levels:
    notion = parts[0]    # "convergence uniforme"
    level = parts[1]     # "prépa"
else:
    notion = rest        # Tout le texte
    level = "prépa/terminale+"  # Défaut
```

**Cas particuliers**:
```python
"convergence uniforme"           → notion="convergence uniforme", level="prépa/terminale+"
"convergence uniforme prépa"     → notion="convergence uniforme", level="prépa"
"intégrales L2"                  → notion="intégrales", level="L2"
"séries de Fourier terminale"    → notion="séries de Fourier", level="terminale"
"espaces vectoriels"             → notion="espaces vectoriels", level="prépa/terminale+"
```

---

## 🆕 Ajouter une Nouvelle Commande

### Étape 1: Créer le Prompt

**Fichier**: `src/prompts/<category>/__init__.py`

```python
class MyNewPrompt(BasePrompt):
    """Description de votre nouveau prompt"""
    
    def __init__(self):
        template = ChatPromptTemplate.from_template("""
Tu génères : "{query}"
Niveau : {level}.

[Contexte]
{context}

Instructions:
...
""")
        super().__init__(template)
    
    def get_task_name(self) -> str:
        return "my_new_task"
```

### Étape 2: Créer le Use Case

**Fichier**: `src/application/use_cases/my_new_task.py`

```python
@dataclass
class MyNewTaskRequest:
    query: str
    level: str = "prépa/terminale+"
    filters: Optional[Filters] = None
    session_context: Optional[SessionContext] = None


class MyNewTaskUseCase:
    def __init__(self, retriever, llm, router, prompt_provider):
        self.retriever = retriever
        self.llm = llm
        self.prompts = prompt_provider
    
    def execute(self, request: MyNewTaskRequest) -> Answer:
        # 1. Récupération documents
        docs = self.retriever.retrieve(query=request.query, ...)
        
        # 2. Formatage contexte
        context = self._format_context(docs)
        
        # 3. Génération
        prompt = self.prompts.get_prompt("my_new_task")
        result = self.llm.generate(prompt, {
            "query": request.query,
            "level": request.level,
            "context": context
        })
        
        return Answer(text=result, sources=docs, ...)
```

### Étape 3: Ajouter à la Façade

**Fichier**: `src/application/facades/math_assistant_facade.py`

```python
def my_new_task(
    self,
    query: str,
    level: str = "prépa/terminale+",
    **kwargs
) -> Dict[str, Any]:
    """Description de la nouvelle tâche"""
    use_case = self._get_use_case("my_new_task")
    
    request = MyNewTaskRequest(
        query=query,
        level=level,
        session_context=self.session_context
    )
    
    answer = use_case.execute(request)
    return self._answer_to_dict(answer)
```

### Étape 4: Ajouter au CLI

**Fichier**: `src/ui/cli/app.py`

```python
def handle_command(self, command: str) -> bool:
    ...
    
    # ----- Ma nouvelle commande -----
    if cmd.startswith("/mon-cmd "):
        rest = cmd.split(" ", 1)[1].strip()
        
        # Extraction niveau (optionnel)
        parts = rest.rsplit(maxsplit=1)
        levels = {"prépa", "terminale", "l1", "l2", "l3", ...}
        
        if len(parts) == 2 and parts[1].lower() in levels:
            query, level = parts[0], parts[1]
        else:
            query, level = rest, "prépa/terminale+"
        
        self.formatter.info(f"🎯 Ma nouvelle tâche - Niveau: {level}")
        payload = self.assistant.run_task("my_new_task", query, level=level)
        
        self.formatter.sources_table(payload["docs"])
        self.formatter.answer(payload["answer"])
        return True
    
    ...
```

### Étape 5: Ajouter Documentation

**Fichier**: `src/ui/cli/styles.py`

```python
# Dans command_help():
"""
  • [command]/mon-cmd[/] <query> [niveau]  → Description courte
"""

# Dans manuals dict:
"mon-cmd": """
[title]/mon-cmd[/]

[subtitle]Description:[/]
Description détaillée de votre commande.

[subtitle]Usage:[/]
  [command]/mon-cmd[/] <query>                → Niveau par défaut
  [command]/mon-cmd[/] <query> <niveau>       → Avec niveau spécifique

[subtitle]Exemples:[/]
  [command]/mon-cmd exemple 1[/]
  [command]/mon-cmd exemple 2 prépa[/]
""",
```

---

## ✅ Checklist Nouvelle Commande

- [ ] Prompt créé dans `src/prompts/`
- [ ] Use Case créé dans `src/application/use_cases/`
- [ ] Méthode ajoutée au Facade
- [ ] Commande ajoutée au CLI (`handle_command`)
- [ ] Aide mise à jour (`command_help`)
- [ ] Manuel ajouté (`manuals` dict)
- [ ] Tests écrits
- [ ] Documentation écrite

---

## 🧪 Tests

### Test Unitaire Prompt
```python
from src.prompts.course import CourseExplainPrompt

prompt = CourseExplainPrompt()
template = prompt.template.messages[0].prompt.template

# Vérifier variables
assert "{topic}" in template
assert "{level}" in template
assert "{context}" in template
```

### Test Use Case
```python
from src.application.use_cases.explain_course import ExplainCourseUseCase, ExplainCourseRequest

# Mock dependencies
request = ExplainCourseRequest(
    topic="convergence uniforme",
    level="prépa"
)

answer = use_case.execute(request)
assert answer.text
assert answer.sources
```

### Test CLI
```bash
# Lancer CLI
python3 scripts/run_cli.py

# Tester commandes
/mini-cours convergence uniforme
/mini séries de Fourier prépa
/cours intégrales L2
```

---

## 📚 Ressources

### Fichiers clés
- `src/prompts/course/__init__.py` - Templates prompts
- `src/application/use_cases/explain_course.py` - Logique métier
- `src/application/facades/math_assistant_facade.py` - API unifiée
- `src/ui/cli/app.py` - Interface CLI
- `src/ui/cli/styles.py` - Aide et manuels

### Documentation
- `QUICKSTART_COURS.md` - Guide rapide utilisateur
- `COURSE_PROMPTS_IMPROVEMENT.md` - Doc complète architecture
- `INTEGRATION_CLI_COMPLETE.md` - Récapitulatif intégration

---

**Résumé**: Cette architecture en couches facilite l'ajout de nouvelles fonctionnalités
tout en maintenant une séparation claire des responsabilités (SOLID).

---

*Guide écrit le 2025-11-06*  
*Version v3.3*
