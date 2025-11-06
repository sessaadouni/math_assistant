# -*- coding: utf-8 -*-
"""
src/ui/cli/styles.py
Styles Rich pour le CLI (GitHub Dark inspired)
"""

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.theme import Theme
from rich.markdown import Markdown
from rich.columns import Columns
from rich.json import JSON

# ===== Thème personnalisé =====

GITHUB_DARK_THEME = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "highlight": "magenta bold",
    "dim": "dim",
    "title": "bold cyan",
    "subtitle": "italic dim cyan",
    "prompt": "bold bright_cyan",
    "command": "yellow",
    "value": "green",
    "key": "blue",
    "path": "italic bright_black",
})

# ===== Console globale =====

console = Console(theme=GITHUB_DARK_THEME)


class CLIFormatter:
    """Formatteur unifié pour l'interface CLI"""

    # --- Header / Footer / Messages ---------------------------------------
    @staticmethod
    def title(text: str):
        console.print(Panel.fit(f"[title]{text}[/]", border_style="cyan"))

    @staticmethod
    def subtitle(text: str):
        console.print(f"\n[subtitle]{text}[/]")

    @staticmethod
    def info(text: str):
        console.print(f"[info]ℹ️  {text}[/]")

    @staticmethod
    def success(text: str):
        console.print(f"[success]✅ {text}[/]")

    @staticmethod
    def warning(text: str):
        console.print(f"[warning]⚠️  {text}[/]")

    @staticmethod
    def error(text: str):
        console.print(Panel(f"[error]{text}[/]", title="❌ Erreur", border_style="red"))
    
    @staticmethod
    def processing_step(step: str, detail: str = "", status: str = "⏳"):
        """
        Display a processing step in real-time.
        
        Parameters
        ----------
        step : str
            Step name (e.g., "Router", "RAG", "LLM")
        detail : str
            Optional detail about the step
        status : str
            Status icon: ⏳ (in progress), ✅ (done), ⚠️ (warning), ❌ (error)
        """
        if detail:
            console.print(f"{status} [cyan]{step}[/]: [dim]{detail}[/]")
        else:
            console.print(f"{status} [cyan]{step}[/]")

    # --- Aide --------------------------------------------------------------
    @staticmethod
    def command_help():
        help_text = """
[title]Commandes disponibles:[/]

[subtitle]📦 Tâches rapides:[/]
  • [command]/qcm[/] <notion>           → Génère un QCM de théorie
  • [command]/exam[/] <1,5,7>           → Génère un sujet d'examen (barème inclus)
  • [command]/fiche[/] <notion>         → Fiche de révision
  • [command]/kholle[/] <notion>        → Sujet de khôlle (oral)
  • [command]/tutor on[/] [strict|smart]  → Mode tuteur persistant (exos/démos)
  • [command]/tutor explain on[/]       → Mode explain (compréhension cours/théorèmes)
  • [command]/tutor[/] <énoncé>         → Mode tuteur ponctuel pour une question
  • [command]/formule[/] <description>  → Recherche/citation de formules
  • [command]/resume[/] <notion>        → Résumé / synthèse de cours
  • [command]/mini-cours[/] <notion>    → Mini-cours rapide (10-15min)
  • [command]/cours[/] <notion>         → Cours complet exhaustif (30-45min)
  • [command]/level[/] [niveau]         → Définit le niveau d'études (mpsi, L3, collège...)
  • [command]/corrige-exo[/] <texte>    → Correction d'exercice
  • [command]/corrige-exam[/] <texte>   → Correction d'examen

[subtitle]🔍 Questions & Filtres:[/]
  • Question normale        → Pose ta question directement
  • [command]/exercice[/] <q>      → Filtre sur les exercices
  • [command]/méthode[/] <q>       → Filtre sur les méthodes
  • [command]/théorie[/] <q>       → Filtre sur la théorie
  • [command]/cours[/] <q>         → Recherche dans tout le cours

[subtitle]⚙️  Portée (scope):[/]
  • [command]/show[/]              → Affiche la portée actuelle (alias de /scope show)
  • [command]/scope show[/]        → Affiche la portée actuelle
  • [command]/scope clear[/]       → Réinitialise la portée
  • [command]/scope set[/] k=v ... → Définit la portée (chapter, block_kind, block_id, type)
  • [command]/ch[/] <num>          → Définit le chapitre
  • [command]/bloc[/] <kind> <id>  → Définit le bloc (théorème, définition...)
  • [command]/type[/] <t>          → Définit le type (exercice, méthode...)
  • [command]/reset[/]             → Réinitialise la portée

[subtitle]🧭 Routeur & Hors-programme:[/]
  • [command]/router show[/]                → Affiche le mode de routage + OOT
  • [command]/router[/] <auto|rag|llm|hybrid> → Force le routeur
  • [command]/oot on|off[/]                 → Autoriser / interdire hors-programme
  • [command]/passport[/] [save]            → Affiche/Enregistre le dernier passport

[subtitle]🔌 Backend & Modèles:[/]
  • [command]/backend show[/]               → Affiche runtime + modèles actifs
  • [command]/backend[/] <local|cloud|hybrid> → Bascule le runtime (si supporté)
  • [command]/models[/]                     → Tableau des modèles actifs
  • [command]/where[/]                      → Répertoires (logs/debug/DB/PDF)

[subtitle]🛠️  Divers:[/]
  • [command]/debug on|off[/]      → Active/désactive le mode debug
  • [command]/log save[/]          → Sauvegarde le chat en JSONL
  • [command]/help[/]              → Affiche cette aide
  • [command]/man[/] <cmd>         → Manuel détaillé d'une commande
  • [command]q[/]                  → Quitter

[dim]Astuce: /backend hybrid + /oot on est idéal pour "RAG→LLM" quand le livre est partiel.[/]
[dim]Utilise /man <commande> pour plus de détails sur une commande spécifique.[/]
"""
        console.print(Panel(help_text.strip(), border_style="blue", padding=(1, 2)))

    @staticmethod
    def command_manual(cmd: str):
        """Affiche le manuel détaillé d'une commande"""
        
        manuals = {
            "show": """
[title]/show[/]

[subtitle]Description:[/]
Affiche la portée (scope) actuelle du contexte de recherche.
C'est un alias pratique de [command]/scope show[/].

[subtitle]Usage:[/]
  [command]/show[/]

[subtitle]Exemple:[/]
  [command]/show[/]
  → Portée actuelle: chapter=3, type=exercice

[subtitle]Voir aussi:[/]
  • [command]/scope[/] - Gestion complète de la portée
  • [command]/ch[/] - Définir le chapitre
  • [command]/reset[/] - Réinitialiser la portée
""",
            "scope": """
[title]/scope[/]

[subtitle]Description:[/]
Gère la portée (scope) du contexte de recherche. La portée définit les filtres
appliqués lors de la recherche dans le cours (chapitre, type de contenu, bloc spécifique).

[subtitle]Usage:[/]
  [command]/scope show[/]              → Affiche la portée actuelle
  [command]/scope clear[/]             → Réinitialise tous les filtres
  [command]/scope set k=v ...[/]       → Définit des filtres (chapter, block_kind, block_id, type)

[subtitle]Filtres disponibles:[/]
  • [key]chapter[/] - Numéro de chapitre (ex: 3, 12)
  • [key]block_kind[/] - Type de bloc (théorème, définition, proposition, corollaire)
  • [key]block_id[/] - ID du bloc (ex: 3.2, 1.5)
  • [key]type[/] - Type de contenu (exercice, méthode, théorie, cours)

[subtitle]Exemples:[/]
  [command]/scope show[/]
  [command]/scope set chapter=3 type=exercice[/]
  [command]/scope set block_kind=théorème block_id=3.2[/]
  [command]/scope clear[/]

[subtitle]Voir aussi:[/]
  • [command]/show[/] - Alias de /scope show
  • [command]/ch[/] - Raccourci pour définir le chapitre
  • [command]/bloc[/] - Raccourci pour définir un bloc
""",
            "ch": """
[title]/ch[/]

[subtitle]Description:[/]
Définit rapidement le chapitre actif dans la portée. Toutes les recherches
seront limitées à ce chapitre jusqu'à modification ou réinitialisation.

[subtitle]Usage:[/]
  [command]/ch[/] <numéro>

[subtitle]Exemples:[/]
  [command]/ch 3[/]     → Limite les recherches au chapitre 3
  [command]/ch 12[/]    → Limite les recherches au chapitre 12

[subtitle]Voir aussi:[/]
  • [command]/scope[/] - Gestion complète de la portée
  • [command]/bloc[/] - Définir un bloc spécifique
  • [command]/reset[/] - Réinitialiser la portée
""",
            "bloc": """
[title]/bloc[/]

[subtitle]Description:[/]
Définit un bloc spécifique (théorème, définition, etc.) dans la portée.
Les recherches seront limitées à ce bloc précis.

[subtitle]Usage:[/]
  [command]/bloc[/] <kind> <id>

[subtitle]Types de blocs:[/]
  • théorème, définition, proposition, corollaire

[subtitle]Exemples:[/]
  [command]/bloc théorème 3.2[/]
  [command]/bloc définition 1.5[/]

[subtitle]Voir aussi:[/]
  • [command]/scope[/] - Gestion complète de la portée
  • [command]/ch[/] - Définir le chapitre
""",
            "type": """
[title]/type[/]

[subtitle]Description:[/]
Filtre les recherches par type de contenu (exercice, méthode, théorie).

[subtitle]Usage:[/]
  [command]/type[/] <type>

[subtitle]Types disponibles:[/]
  • [value]exercice[/] - Exercices et problèmes
  • [value]méthode[/] - Méthodes et techniques
  • [value]théorie[/] - Théorèmes, définitions, propriétés
  • [value]cours[/] - Contenu de cours général

[subtitle]Exemples:[/]
  [command]/type exercice[/]
  [command]/type théorie[/]

[subtitle]Voir aussi:[/]
  • [command]/exercice[/], [command]/méthode[/], [command]/théorie[/] - Filtres directs sur questions
""",
            "reset": """
[title]/reset[/]

[subtitle]Description:[/]
Réinitialise complètement la portée (scope). Équivalent à [command]/scope clear[/].

[subtitle]Usage:[/]
  [command]/reset[/]

[subtitle]Effet:[/]
Supprime tous les filtres actifs (chapitre, type, bloc).
""",
            "router": """
[title]/router[/]

[subtitle]Description:[/]
Contrôle le routage des requêtes entre RAG (recherche dans le cours)
et LLM (génération autonome).

[subtitle]Usage:[/]
  [command]/router show[/]                → Affiche le mode actuel
  [command]/router[/] <mode>              → Force un mode de routage

[subtitle]Modes disponibles:[/]
  • [value]auto[/] - Décision automatique intelligente (recommandé)
  • [value]rag[/] - Toujours chercher dans le cours (RAG strict)
  • [value]llm[/] - Toujours réponse autonome (sans cours)
  • [value]hybrid[/] - RAG d'abord, puis LLM si besoin

[subtitle]Exemples:[/]
  [command]/router show[/]
  [command]/router auto[/]
  [command]/router hybrid[/]

[subtitle]Voir aussi:[/]
  • [command]/oot[/] - Autoriser/interdire le hors-programme
""",
            "oot": """
[title]/oot[/]

[subtitle]Description:[/]
Active ou désactive le mode "hors programme" (Out Of Topic).
Quand activé, le LLM peut répondre de façon autonome si le cours ne contient
pas l'information. Quand désactivé, seul le contenu du cours est utilisé.

[subtitle]Usage:[/]
  [command]/oot on[/]     → Autorise le hors-programme
  [command]/oot off[/]    → RAG strict (cours uniquement)

[subtitle]Exemples:[/]
  [command]/oot on[/]
  [command]/oot off[/]

[subtitle]Recommandation:[/]
  • [value]on[/] - Pour exploration ou sujets partiellement couverts
  • [value]off[/] - Pour garantir la rigueur et l'alignement au cours
""",
            "debug": """
[title]/debug[/]

[subtitle]Description:[/]
Active ou désactive le mode debug qui affiche des informations détaillées
sur le traitement des requêtes (réécriture, filtres, clause WHERE Chroma, etc.).

[subtitle]Usage:[/]
  [command]/debug on[/]     → Active le mode debug
  [command]/debug off[/]    → Désactive le mode debug

[subtitle]Informations affichées en mode debug:[/]
  • Requête réécrite (query rewriting)
  • Requête avec hints
  • Paramètres de recherche (kwargs)
  • Clause WHERE Chroma (filtres vectoriels)
  • Passport de routage détaillé
  • Trace LLM avec temps d'exécution

[subtitle]Exemples:[/]
  [command]/debug on[/]
  [command]/debug off[/]
""",
            "passport": """
[title]/passport[/]

[subtitle]Description:[/]
Affiche ou sauvegarde le "passport" de routage de la dernière question.
Le passport contient toutes les décisions prises par le routeur intelligent.

[subtitle]Usage:[/]
  [command]/passport[/]         → Affiche le passport
  [command]/passport save[/]    → Sauvegarde en JSON
  [command]/passport json[/]    → Sauvegarde en JSON (alias)

[subtitle]Contenu du passport:[/]
  • Décision de routage (rag_first, llm_only, hybrid)
  • Niveau de confiance RAG
  • Raison de la décision
  • Signaux et poids utilisés
  • Stats de recherche (hits, similarité max)
  • Métadonnées du top document

[subtitle]Exemples:[/]
  [command]/passport[/]
  [command]/passport save[/]
""",
            "backend": """
[title]/backend[/]

[subtitle]Description:[/]
Gère le runtime backend (local/cloud/hybrid) et affiche les modèles actifs.

[subtitle]Usage:[/]
  [command]/backend show[/]               → Affiche la config actuelle
  [command]/backend[/] <mode>             → Bascule le runtime

[subtitle]Modes runtime:[/]
  • [value]local[/] - Ollama local uniquement
  • [value]cloud[/] - APIs cloud (OpenAI, Anthropic, etc.)
  • [value]hybrid[/] - Combinaison local + cloud

[subtitle]Exemples:[/]
  [command]/backend show[/]
  [command]/backend hybrid[/]

[subtitle]Voir aussi:[/]
  • [command]/models[/] - Tableau détaillé des modèles
""",
            "models": """
[title]/models[/]

[subtitle]Description:[/]
Affiche un tableau détaillé de tous les modèles actifs (LLM, embeddings, reranker).

[subtitle]Usage:[/]
  [command]/models[/]

[subtitle]Informations affichées:[/]
  • Runtime mode (local/cloud/hybrid)
  • Ollama host
  • LLM primaire et fallback
  • Modèle de réécriture (rewriter)
  • Modèles d'embeddings (primaire + alternatif)
  • Reranker

[subtitle]Voir aussi:[/]
  • [command]/backend[/] - Gestion du runtime
  • [command]/where[/] - Chemins des répertoires
""",
            "where": """
[title]/where[/]

[subtitle]Description:[/]
Affiche les chemins des répertoires importants (logs, debug, DB, PDF source).

[subtitle]Usage:[/]
  [command]/where[/]

[subtitle]Répertoires affichés:[/]
  • Chat logs - Historique des conversations
  • Debug dumps - Fichiers de debug et passports
  • Vector DB - Base de données vectorielle Chroma
  • PDF source - Fichier PDF du cours

[subtitle]Voir aussi:[/]
  • [command]/log save[/] - Sauvegarder le chat
""",
            "log": """
[title]/log[/]

[subtitle]Description:[/]
Sauvegarde l'historique du chat actuel en format JSONL.

[subtitle]Usage:[/]
  [command]/log save[/]

[subtitle]Format JSONL:[/]
Chaque ligne est un objet JSON représentant une interaction
(question, réponse, documents trouvés, métadonnées).

[subtitle]Exemple:[/]
  [command]/log save[/]
  → Log sauvegardé: /path/to/logs/chat_id/timestamp.jsonl

[subtitle]Voir aussi:[/]
  • [command]/where[/] - Voir les chemins des répertoires
""",
            "qcm": """
[title]/qcm[/]

[subtitle]Description:[/]
Génère un QCM (questionnaire à choix multiples) de théorie sur une notion donnée.

[subtitle]Usage:[/]
  [command]/qcm[/] <notion>

[subtitle]Exemples:[/]
  [command]/qcm intégration par parties[/]
  [command]/qcm théorème de Rolle[/]
  [command]/qcm séries entières[/]

[subtitle]Contenu généré:[/]
  • Questions théoriques
  • 4 choix de réponses par question
  • Niveau adapté (prépa/terminale+)
""",
            "exam": """
[title]/exam[/]

[subtitle]Description:[/]
Génère un sujet d'examen complet avec barème pour les chapitres spécifiés.

[subtitle]Usage:[/]
  [command]/exam[/] <chapitres>

[subtitle]Format chapitres:[/]
Liste de numéros séparés par des virgules (ex: 1,5,7)

[subtitle]Exemples:[/]
  [command]/exam 3,5,7[/]
  [command]/exam 1,2[/]

[subtitle]Contenu généré:[/]
  • Exercices progressifs
  • Barème détaillé
  • Durée estimée
  • Points par exercice
""",
            "fiche": """
[title]/fiche[/]

[subtitle]Description:[/]
Génère une fiche de révision synthétique sur une notion.

[subtitle]Usage:[/]
  [command]/fiche[/] <notion>

[subtitle]Exemples:[/]
  [command]/fiche intégrales généralisées[/]
  [command]/fiche suites convergentes[/]

[subtitle]Contenu de la fiche:[/]
  • Définitions clés
  • Théorèmes principaux
  • Formules essentielles
  • Points d'attention
""",
            "kholle": """
[title]/kholle[/]

[subtitle]Description:[/]
Génère un sujet de khôlle (interrogation orale) sur une notion.

[subtitle]Usage:[/]
  [command]/kholle[/] <notion>

[subtitle]Exemples:[/]
  [command]/kholle dérivation[/]
  [command]/kholle espaces vectoriels[/]

[subtitle]Contenu généré:[/]
  • Question de cours
  • Exercice d'application
  • Niveau oral prépa
""",
            "tutor": """
[title]/tutor[/]

[subtitle]Description:[/]
Mode "learn & study" - Guide l'étudiant sans donner directement la solution.
Encourage la réflexion et l'apprentissage actif. Comprend 2 modes complémentaires:
  • [value]Tuteur classique[/] : Exercices, démonstrations, calculs
  • [value]Explain (🧠)[/] : Compréhension de cours, théorèmes, intuitions

[subtitle]Modes disponibles:[/]
  [key]1) Mode ponctuel:[/] [command]/tutor <énoncé>[/]
    → Guidage structuré pour une seule question/exercice

  [key]2) Mode persistant SMART:[/] [command]/tutor on[/] [dim](recommandé)[/dim]
    → Détection automatique intelligente:
      • [value]Exercices/démonstrations[/] → Guidage structuré (étapes, méthode)
      • [value]Questions de compréhension[/] → Guidage socratique (si explain actif)
      • [value]Rappels théoriques purs[/] → Réponse normale directe
    
  [key]3) Mode persistant STRICT:[/] [command]/tutor on strict[/]
    → TOUT en mode guidage pédagogique (exercices + théorie)

  [key]4) Mode EXPLAIN:[/] [command]/tutor explain on[/]
    → Guidage socratique pour comprendre cours/théorèmes
    → Questions pour faire réfléchir à l'intuition, pas juste réciter
    → Combinable avec /tutor on pour couvrir exercices + compréhension

  [key]Désactiver:[/] [command]/tutor off[/] | [command]/tutor explain off[/]

  [key]Vérifier status:[/] [command]/tutor[/]
    → Affiche si modes actifs (tuteur + explain)

[subtitle]Détection automatique (mode smart):[/]
  [key]Catégorie 1 - Exercices/Démonstrations:[/]
    Mots-clés: démontrer, montrer, calculer, résoudre, prouver, justifier
    → [value]Guidage structuré[/] (étapes, hints, méthode)
  
  [key]Catégorie 2 - Compréhension:[/] [dim](nécessite /tutor explain on)[/dim]
    Mots-clés: explique, comprendre, pourquoi, comment ça marche, intuition
    → [value]Guidage socratique[/] (questions pour réfléchir)
  
  [key]Catégorie 3 - Rappels théoriques:[/]
    Mots-clés: définition de, formule de, énoncé du théorème, rappel
    → [value]Réponse directe[/] (pas de guidage, juste l'info)

[subtitle]Exemples d'utilisation:[/]
  [dim]# Mode ponctuel (exercice unique)[/dim]
  [command]/tutor calculer l'intégrale de x²e^x[/]
  [command]/tutor explain pourquoi le théorème de Rolle fonctionne[/]
  
  [dim]# Session complète avec smart + explain[/dim]
  [command]/tutor on[/]           [dim]← active smart[/dim]
  [command]/tutor explain on[/]   [dim]← active explain[/dim]
  
  [dim][[/][value]🎓 TUTEUR[/][dim]] [[/][info]smart[/][dim]] [[/][value]🧠 EXPLAIN[/][dim]][/] 💬 Ta question:
  💬 Qu'est-ce qu'une intégrale ?
     → Réponse directe (rappel théorique) ✓
  
  💬 Explique-moi l'intuition derrière les intégrales
     🧠 Mode tuteur - Guidage socratique (compréhension)
     → "Que représente une aire sous la courbe ?" ✓
  
  💬 Calculer ∫ x²e^x dx
     🎓 Mode tuteur - Guidage pédagogique (exercice/démo)
     → Étapes: "Quelle méthode pour produit de fonctions ?" ✓
  
  💬 Démontrer le théorème de Rolle
     🎓 Mode tuteur - Guidage pédagogique (exercice/démo)
     → Guidage par les hypothèses ✓
  
  [command]/tutor off[/]
  [command]/tutor explain off[/]
  
  [dim]# Mode strict (tout en guidage)[/dim]
  [command]/tutor on strict[/]
  💬 Même "Qu'est-ce qu'une intégrale ?" sera en guidage

[subtitle]Combinaisons possibles:[/]
  • [command]/tutor on[/] seul → Exos en guidage, théorie normale
  • [command]/tutor explain on[/] seul → Compréhension en socratique, reste normal
  • [command]/tutor on[/] + [command]/tutor explain on[/] → Exos + compréhension (idéal!)
  • [command]/tutor on strict[/] → Tout en guidage (intensif)

[subtitle]Approches pédagogiques:[/]
  [key]Guidage structuré (exercices):[/]
    • Étapes méthodiques
    • Hints progressifs
    • Vérification à chaque étape
    • Pas de solution complète
  
  [key]Guidage socratique (explain):[/]
    • Questions pour faire réfléchir
    • Construction de l'intuition
    • Analogies et exemples
    • Compréhension profonde

[subtitle]Notes importantes:[/]
  • Modes désactivés automatiquement avec [command]/forget[/] ou [command]/new-chat[/]
  • En mode [value]smart[/], détection par mots-clés (très précise)
  • Mode [value]explain[/] parfait pour réviser théorèmes/démos
  • Combine [command]/tutor on[/] + [command]/tutor explain on[/] pour session complète d'apprentissage
""",
            "formule": """
[title]/formule[/]

[subtitle]Description:[/]
Recherche et cite des formules mathématiques du cours.

[subtitle]Usage:[/]
  [command]/formule[/] <description>

[subtitle]Exemples:[/]
  [command]/formule intégration par parties[/]
  [command]/formule dérivée de ln[/]
  [command]/formule Taylor reste intégral[/]

[subtitle]Résultat:[/]
  • Formule en LaTeX
  • Contexte d'utilisation
  • Références au cours
""",
            "resume": """
[title]/resume[/]

[subtitle]Description:[/]
Génère un résumé ou une synthèse de cours sur une notion.

[subtitle]Usage:[/]
  [command]/resume[/] <notion>

[subtitle]Exemples:[/]
  [command]/resume continuité et dérivabilité[/]
  [command]/resume espaces de Banach[/]

[subtitle]Contenu:[/]
  • Vue d'ensemble
  • Points clés
  • Liens entre concepts
""",
            "mini-cours": """
[title]/mini-cours[/] (alias: /mini)

[subtitle]Description:[/]
Génère un mini-cours rapide et pédagogique (10-15 min de lecture).
Idéal pour découverte rapide ou révision express.

[subtitle]Usage:[/]
  [command]/mini-cours[/] <notion>                → Niveau par défaut (prépa/terminale+)
  [command]/mini-cours[/] <notion> <niveau>       → Avec niveau spécifique

[subtitle]Niveaux reconnus:[/]
  prépa, terminale, L1, L2, L3, licence, CPGE, MP, PC, PSI, PT, BCPST

[subtitle]Exemples:[/]
  [command]/mini-cours convergence uniforme[/]
  [command]/mini-cours séries de Fourier prépa[/]
  [command]/mini intégrales L2[/]
  [command]/mini espaces vectoriels L1[/]

[subtitle]Structure (7 sections):[/]
  1. L'essentiel en 3 phrases
  2. Définitions clés (indispensables)
  3. Propriétés principales (top 3-4)
  4. Méthode type + 1 exemple
  5. Mini-FAQ (3-5 questions courantes)
  6. Formules à retenir (top 5-7)
  7. Pour aller plus loin

[subtitle]Durée lecture: 10-15 minutes[/]

[subtitle]Différence avec /cours:[/]
  • [command]/mini-cours[/] → Rapide, pédagogique, FAQ
  • [command]/cours[/] → Exhaustif, rigoureux, exercices détaillés

[subtitle]Voir aussi:[/]
  • [command]/cours[/] - Cours complet exhaustif
  • [command]/resume[/] - Résumé synthétique
""",
            "cours": """
[title]/cours[/]

[subtitle]Description:[/]
Génère un cours COMPLET et rigoureux (30-45 min de lecture).
Double piste pédagogique: CPGE-preuve + Appli-ingénieur.
Idéal pour apprentissage approfondi ou préparation concours.

[subtitle]Usage:[/]
  [command]/cours[/] <notion>                → Niveau par défaut (prépa/terminale+)
  [command]/cours[/] <notion> <niveau>       → Avec niveau spécifique

[subtitle]Niveaux reconnus:[/]
  prépa, terminale, L1, L2, L3, licence, CPGE, MP, PC, PSI, PT, BCPST

[subtitle]Exemples:[/]
  [command]/cours convergence uniforme[/]
  [command]/cours séries de Fourier prépa[/]
  [command]/cours intégrales L2[/]
  [command]/cours espaces vectoriels L3[/]

[subtitle]Structure (9 sections):[/]
  1. Introduction / plan détaillé
  2. Définitions + notations formelles
  3. Propriétés / théorèmes (CPGE + Ingé)
  4. Méthodes / algorithmes (double piste)
  5. Exemples (3-4) + contre-exemples (2-3)
  6. Exercices détaillés (5-6 avec corrections)
  7. Formules clés en contexte
  8. Références [p.X]
  9. Mini-révision interactive

[subtitle]Double piste pédagogique:[/]
  [key]Piste CPGE:[/]
    • Définitions formelles (ε-δ si pertinent)
    • Esquisses de preuves
    • Justifications théoriques
    • Conditions nécessaires vs suffisantes

  [key]Piste Ingénieur:[/]
    • Critères pratiques d'application
    • Checklists étape par étape
    • Heuristiques et astuces
    • Erreurs fréquentes

[subtitle]Durée lecture: 30-45 minutes[/]

[subtitle]Différence avec /mini-cours:[/]
  • [command]/mini-cours[/] → Rapide (10-15min), pédagogique
  • [command]/cours[/] → Exhaustif (30-45min), rigoureux

[subtitle]Cas d'usage:[/]
  • Préparation examen/concours
  • Apprentissage approfondi
  • Besoin de preuves et rigueur
  • Travail sur exercices variés

[subtitle]Voir aussi:[/]
  • [command]/mini-cours[/] - Mini-cours rapide
  • [command]/resume[/] - Résumé synthétique
""",
            "level": """
[title]/level[/]

[subtitle]Description:[/]
Définit le niveau d'études de manière persistante pour toutes les commandes 
[command]/cours[/] et [command]/mini-cours[/] qui suivent, jusqu'à reset.

Plus besoin de spécifier le niveau à chaque fois ! Définissez-le une fois, 
et il sera automatiquement utilisé pour tous les cours générés.

[subtitle]Usage:[/]
  [command]/level[/]                → Affiche le niveau actuel
  [command]/level[/] <niveau>       → Définit le niveau persistant
  [command]/level reset[/]          → Réinitialise au défaut (prépa/terminale+)

[subtitle]Niveaux reconnus:[/]
  [info]Collège:[/] sixième, cinquième, quatrième, troisième
  [info]Lycée:[/] seconde, première, terminale
  [info]Classes prépa (SUP):[/] sup, mpsi, pcsi, ptsi, bcpst, ecs, ecg
  [info]Classes prépa (SPE):[/] spe, mp, mp*, pc, pc*, psi, psi*, pt, pt*
  [info]Université:[/] L1, L2, L3, licence, M1, M2, master
  [info]Ingénieur:[/] école d'ingénieur

[subtitle]Accès au RAG (livre):[/]
  ✅ [value]Disponible pour:[/] SUP, MPSI, PCSI, PTSI (1ère année prépa)
  ⚠️  [warning]Hors livre:[/] Autres niveaux utilisent le LLM uniquement

[subtitle]Exemples:[/]
  [command]/level mpsi[/]
  [command]/cours intégrales[/]          ← utilise niveau MPSI + RAG
  [command]/mini-cours séries[/]         ← utilise niveau MPSI + RAG
  [command]/level L3[/]
  [command]/cours algèbre linéaire[/]    ← utilise niveau L3, LLM seul
  [command]/level reset[/]               ← retour au défaut

[subtitle]Persistance:[/]
  • Le niveau reste actif pour toute la session
  • Réinitialisé automatiquement par [command]/forget[/] ou [command]/new-chat[/]
  • Badge visible dans le prompt: [dim][[/][value]📚 MPSI[/][dim]][/]

[subtitle]Cas d'usage:[/]
  • Étudiant prépa: [command]/level mpsi[/] puis génération de cours/mini-cours
  • Étudiant universitaire: [command]/level L3[/] pour adapter le vocabulaire
  • Collégien: [command]/level cinquième[/] pour contenu simplifié
  • Préparation concours: [command]/level mp*[/] pour niveau avancé

[subtitle]Voir aussi:[/]
  • [command]/cours[/] - Cours complet exhaustif
  • [command]/mini-cours[/] - Mini-cours rapide
  • [command]/router[/] - Force RAG ou LLM manuellement
""",
            "exercice": """
[title]/exercice[/]

[subtitle]Description:[/]
Filtre la recherche sur les exercices uniquement lors d'une question.

[subtitle]Usage:[/]
  [command]/exercice[/] <question>

[subtitle]Exemples:[/]
  [command]/exercice intégration par parties[/]
  [command]/exercice calcul de limites[/]

[subtitle]Effet:[/]
La recherche RAG ne retournera que des chunks de type "exercice".

[subtitle]Voir aussi:[/]
  • [command]/méthode[/] - Filtre sur les méthodes
  • [command]/théorie[/] - Filtre sur la théorie
""",
            "méthode": """
[title]/méthode[/]

[subtitle]Description:[/]
Filtre la recherche sur les méthodes et techniques uniquement.

[subtitle]Usage:[/]
  [command]/méthode[/] <question>

[subtitle]Exemples:[/]
  [command]/méthode résoudre une équation différentielle[/]
  [command]/méthode étudier la convergence[/]

[subtitle]Effet:[/]
La recherche RAG ne retournera que des chunks de type "méthode".

[subtitle]Voir aussi:[/]
  • [command]/exercice[/] - Filtre sur les exercices
  • [command]/théorie[/] - Filtre sur la théorie
""",
            "théorie": """
[title]/théorie[/]

[subtitle]Description:[/]
Filtre la recherche sur la théorie (théorèmes, définitions, propriétés).

[subtitle]Usage:[/]
  [command]/théorie[/] <question>

[subtitle]Exemples:[/]
  [command]/théorie théorème des valeurs intermédiaires[/]
  [command]/théorie définition de la continuité[/]

[subtitle]Effet:[/]
La recherche RAG ne retournera que des chunks de type "théorie".

[subtitle]Voir aussi:[/]
  • [command]/exercice[/] - Filtre sur les exercices
  • [command]/méthode[/] - Filtre sur les méthodes
""",
            "help": """
[title]/help[/]

[subtitle]Description:[/]
Affiche l'aide générale avec la liste de toutes les commandes disponibles.

[subtitle]Usage:[/]
  [command]/help[/]

[subtitle]Voir aussi:[/]
  • [command]/man[/] <cmd> - Manuel détaillé d'une commande
""",
            "man": """
[title]/man[/]

[subtitle]Description:[/]
Affiche le manuel détaillé d'une commande spécifique avec des exemples
et des explications complètes.

[subtitle]Usage:[/]
  [command]/man[/] <commande>

[subtitle]Exemples:[/]
  [command]/man scope[/]
  [command]/man router[/]
  [command]/man qcm[/]

[subtitle]Commandes documentées:[/]
Toutes les commandes du système disposent d'un manuel.
Tape [command]/help[/] pour voir la liste complète.
""",
            "new-chat": """
[title]/new-chat[/]

[subtitle]Description:[/]
Démarre une nouvelle conversation en réinitialisant l'historique et les contextes.
Peut optionnellement nommer le chat pour une meilleure organisation.

[subtitle]Usage:[/]
  [command]/new-chat[/]              → Nouveau chat (ID généré automatiquement)
  [command]/new-chat[/] <nom>        → Nouveau chat avec nom personnalisé

[subtitle]Effets:[/]
  • Réinitialise l'historique de conversation
  • Active auto-link (liaison automatique au contexte)
  • Active auto-pin pour le prochain contexte
  • Désactive le mode tuteur
  • Conserve les logs (si activés)

[subtitle]Exemples:[/]
  [command]/new-chat[/]
  [command]/new-chat chapitre3[/]
  [command]/new-chat révisions-examen[/]

[subtitle]Voir aussi:[/]
  • [command]/forget[/] - Oublier les liens du contexte actuel
  • [command]/log save[/] - Sauvegarder avant de changer de chat
""",
            "pin": """
[title]/pin[/]

[subtitle]Description:[/]
Épingle le contexte actuel pour le réutiliser dans les prochaines questions.
Le contexte épinglé reste actif jusqu'à désépinglage explicite.

[subtitle]Usage:[/]
  [command]/pin[/]

[subtitle]Effets:[/]
  • Mémorise les documents du dernier contexte
  • Réutilise ce contexte pour les questions suivantes
  • Biaise la recherche vers les documents épinglés
  • Visible dans [command]/show[/]

[subtitle]Cas d'usage:[/]
Quand plusieurs questions portent sur les mêmes théorèmes/exercices,
épingler permet de maintenir la cohérence contextuelle.

[subtitle]Exemples:[/]
  💬 C'est quoi le théorème de Rolle ?
  [... réponse avec sources ...]
  [command]/pin[/]
  💬 Donne un exemple d'application
  [... utilisera le même contexte ...]
  💬 Et les conditions ?
  [... toujours le même contexte ...]
  [command]/unpin[/]

[subtitle]Voir aussi:[/]
  • [command]/unpin[/] - Désépingler le contexte
  • [command]/show[/] - Voir si un contexte est épinglé
""",
            "unpin": """
[title]/unpin[/]

[subtitle]Description:[/]
Désépingle le contexte mémorisé pour revenir à une recherche libre.

[subtitle]Usage:[/]
  [command]/unpin[/]

[subtitle]Effet:[/]
Supprime le contexte épinglé et permet une nouvelle recherche sans biais.

[subtitle]Voir aussi:[/]
  • [command]/pin[/] - Épingler un contexte
""",
            "link": """
[title]/link[/]

[subtitle]Description:[/]
Active ou désactive l'auto-link (liaison automatique au contexte précédent).
Quand activé, chaque question réutilise automatiquement le contexte de la question précédente.

[subtitle]Usage:[/]
  [command]/link on[/]     → Active l'auto-link
  [command]/link off[/]    → Désactive l'auto-link

[subtitle]Effets:[/]
  • [value]on[/] - Les questions sont liées automatiquement (mode conversation)
  • [value]off[/] - Chaque question est indépendante (mode questions isolées)

[subtitle]Différence avec /pin:[/]
  • [command]/link[/] - Liaison automatique question après question (dynamique)
  • [command]/pin[/] - Épinglage manuel d'un contexte spécifique (statique)

[subtitle]Exemples:[/]
  [command]/link on[/]      → Active (par défaut au démarrage)
  [command]/link off[/]     → Questions indépendantes

[subtitle]Voir aussi:[/]
  • [command]/pin[/], [command]/unpin[/] - Contrôle manuel du contexte
  • [command]/forget[/] - Oublier les liens sans désactiver l'auto-link
""",
            "forget": """
[title]/forget[/]

[subtitle]Description:[/]
Oublie les liens du contexte actuel (dernière question, derniers documents)
sans désactiver l'auto-link. Utile pour "recommencer à zéro" sans changer de chat.

[subtitle]Usage:[/]
  [command]/forget[/]

[subtitle]Effets:[/]
  • Efface la dernière question mémorisée
  • Efface les derniers documents contextuels
  • Conserve l'historique du chat
  • Ne désactive PAS l'auto-link (contrairement à [command]/link off[/])

[subtitle]Cas d'usage:[/]
Quand tu veux changer de sujet complètement sans créer un nouveau chat.

[subtitle]Exemples:[/]
  💬 Questions sur les séries...
  [command]/forget[/]
  💬 Questions sur les intégrales (contexte vierge)

[subtitle]Voir aussi:[/]
  • [command]/new-chat[/] - Recommencer avec un nouveau chat
  • [command]/unpin[/] - Désépingler le contexte (plus ciblé)
  • [command]/link off[/] - Désactiver complètement l'auto-link
""",
        }
        
        # Normalisation de la commande
        cmd_clean = cmd.strip().lower().lstrip("/")
        
        # Gestion des alias
        aliases = {
            "methode": "méthode",
            "theorie": "théorie",
            "route": "router",
        }
        cmd_clean = aliases.get(cmd_clean, cmd_clean)
        
        if cmd_clean in manuals:
            console.print(Panel(manuals[cmd_clean].strip(), border_style="cyan", padding=(1, 2)))
        else:
            console.print(f"[warning]⚠️  Commande '{cmd}' non documentée.[/]")
            console.print(f"[info]Tape [command]/help[/] pour voir toutes les commandes ou [command]/man man[/] pour l'aide sur /man.[/]")

    # --- UI widgets --------------------------------------------------------
    @staticmethod
    def separator():
        console.print("\n" + "─" * 70)

    @staticmethod
    def prompt(
        text: str = "Ta question", 
        tutor_mode: bool = False, 
        tutor_strict: bool = False, 
        tutor_explain: bool = False,
        allow_oot: bool = True,
        router_mode: str = "auto",
        backend: str = "local",
        level: Optional[str] = None
    ) -> str:
        """
        Display prompt with system status badges and separate input line.
        
        Parameters
        ----------
        text : str
            Prompt text
        tutor_mode : bool
            Whether tutor mode is enabled
        tutor_strict : bool
            Whether strict tutor mode (vs smart)
        tutor_explain : bool
            Whether explain mode is enabled
        allow_oot : bool
            Whether out-of-topic is allowed
        router_mode : str
            Router mode: auto/rag/llm/hybrid
        backend : str
            Backend mode: local/cloud/hybrid
        level : Optional[str]
            Current academic level (e.g., 'mpsi', 'L3', etc.)
        """
        # Build status badges (like a real system)
        badges = []
        
        # Router badge
        if router_mode == "auto":
            badges.append("[dim][[/][info]🧭 AUTO[/][dim]][/]")
        elif router_mode == "rag":
            badges.append("[dim][[/][value]🧭 RAG[/][dim]][/]")
        elif router_mode == "llm":
            badges.append("[dim][[/][warning]🧭 LLM[/][dim]][/]")
        else:
            badges.append(f"[dim][[/][highlight]🧭 {router_mode.upper()}[/][dim]][/]")
        
        # OOT badge
        if allow_oot:
            badges.append("[dim][[/][value]� OOT[/][dim]][/]")
        else:
            badges.append("[dim][[/][dim]🌍 OOT[/dim][dim]][/]")
        
        # Backend badge
        if backend == "local":
            badges.append("[dim][[/][info]🖥️  LOCAL[/][dim]][/]")
        elif backend == "cloud":
            badges.append("[dim][[/][warning]☁️  CLOUD[/][dim]][/]")
        else:
            badges.append("[dim][[/][highlight]⚡ HYBRID[/][dim]][/]")
        
        # Tutor mode badges
        if tutor_mode:
            if tutor_strict:
                badges.append("[dim][[/][value]🎓 STRICT[/][dim]][/]")
            else:
                badges.append("[dim][[/][value]🎓 SMART[/][dim]][/]")
        
        if tutor_explain:
            badges.append("[dim][[/][value]🧠 EXPLAIN[/][dim]][/]")
        
        # Level badge
        if level:
            # Check if RAG is available for this level
            rag_levels = {"sup", "math sup", "maths sup", "mpsi", "pcsi", "ptsi"}
            if level.lower() in rag_levels:
                badges.append(f"[dim][[/][value]📚 {level.upper()}[/][dim]][/]")
            else:
                badges.append(f"[dim][[/][info]📚 {level.upper()}[/][dim]][/]")
        
        # Display status line with badges (non-editable)
        badge_str = " ".join(badges)
        console.print(f"\n{badge_str}")
        console.print(f"[prompt]💬 {text}[/]:")
        
        # Input line - use plain input() to avoid backspace eating the prompt
        # KeyboardInterrupt (Ctrl+C) should propagate to allow clean exit
        user_input = input("> ")
        return user_input.strip()

    @staticmethod
    def sources_table(docs: list):
        if not docs:
            return

        table = Table(
            title="📖 Sources trouvées",
            show_lines=True,
            border_style="dim",
            title_style="title",
            header_style="bold cyan"
        )

        table.add_column("#", style="bold", width=3)
        table.add_column("Bloc", style="magenta")
        table.add_column("Chap/Sec", style="cyan")
        table.add_column("Page", justify="right", width=6)
        table.add_column("Aperçu")

        for i, d in enumerate(docs, 1):
            blk = ("{} {}".format(
                d.metadata.get("block_kind", "") or "",
                d.metadata.get("block_id", "") or ""
            )).strip()

            chapsec = f"{d.metadata.get('chapter','?')} / {d.metadata.get('section','?')}"
            page = str(d.metadata.get("page", "?"))
            prev = (d.page_content[:120].replace("\n", " ") + "...") if d.page_content else ""

            table.add_row(
                str(i),
                blk or d.metadata.get("type", "?"),
                chapsec,
                page,
                prev
            )

        console.print(table)

    @staticmethod
    def answer(text: str):
        console.print(Panel.fit("[title]📝 Réponse[/]", border_style="green"))
        try:
            md = Markdown(text)
            console.print(md)
        except Exception:
            console.print(text)

    # --- Status & diagnostics ---------------------------------------------
    @staticmethod
    def scope_status(scope_text: str):
        console.print(f"[key]🔧 Portée actuelle:[/] [value]{scope_text}[/]")

    @staticmethod
    def router_status(mode: str, allow_oot: bool):
        oot = "autorisé" if allow_oot else "désactivé (RAG strict)"
        console.print(f"[key]🧭 Routeur:[/] [value]{mode}[/]   [key]Hors programme:[/] [value]{oot}[/]")

    @staticmethod
    def backend_status(snapshot: dict):
        rows = [
            f"[key]Runtime:[/] [value]{snapshot.get('runtime','?')}[/]",
            f"[key]Ollama host:[/] [path]{snapshot.get('ollama_host','?')}[/]",
            f"[key]LLM primaire:[/] [value]{snapshot.get('llm_primary','?')}[/]",
            f"[key]LLM fallback:[/] [value]{snapshot.get('llm_fallback','(aucun)')}[/]",
            f"[key]Rewriter:[/] [value]{snapshot.get('rewrite_model','(désactivé)')}[/]",
            f"[key]Embeddings:[/] [value]{snapshot.get('embed_primary','?')}[/]  (alt: {snapshot.get('embed_alt','—')})",
            f"[key]Reranker:[/] [value]{snapshot.get('reranker','(désactivé)')}[/]",
        ]
        console.print(Panel("\n".join(rows), title="🔌 Backend & Modèles", border_style="cyan"))

    @staticmethod
    def models_table(snapshot: dict):
        table = Table(title="🔧 Modèles actifs", show_lines=True, border_style="dim")
        table.add_column("Catégorie", style="cyan", width=16)
        table.add_column("Valeur", style="value")
        table.add_row("Runtime", snapshot.get("runtime","?"))
        table.add_row("Ollama host", snapshot.get("ollama_host","?"))
        table.add_row("LLM primaire", snapshot.get("llm_primary","?"))
        table.add_row("LLM fallback", snapshot.get("llm_fallback","(aucun)") or "(aucun)")
        table.add_row("Rewriter", snapshot.get("rewrite_model","(désactivé)") or "(désactivé)")
        table.add_row("Embeddings", f"{snapshot.get('embed_primary','?')}  | alt: {snapshot.get('embed_alt','—')}")
        table.add_row("Reranker", snapshot.get("reranker","(désactivé)") or "(désactivé)")
        console.print(table)

    @staticmethod
    def paths(p: dict):
        rows = [
            f"[key]Chat logs:[/] [path]{p.get('log_dir')}[/]",
            f"[key]Debug dumps:[/] [path]{p.get('debug_dir')}[/]",
            f"[key]Vector DB:[/] [path]{p.get('db_dir')}[/]",
            f"[key]PDF source:[/] [path]{p.get('pdf_path')}[/]",
        ]
        console.print(Panel("\n".join(rows), title="📁 Répertoires", border_style="blue"))

    @staticmethod
    def debug_info(rewritten: str, hinted: str, kwargs: dict):
        final_where = kwargs.get("final_where")
        debug_panel = f"""[dim]
[key]Rewritten query:[/] {rewritten}
[key]Hinted query:[/] {hinted}
[key]Kwargs:[/] {kwargs}
[key]Where (Chroma):[/] {final_where}
[/dim]"""
        console.print(Panel(debug_panel.strip(), title="🐞 Debug Query", border_style="yellow"))

    @staticmethod
    def passport(passport: dict):
        """Affichage compact (lisible) du dernier passport."""
        rout = passport.get("routing", {})
        filters = passport.get("filters", {})
        meta = passport.get("top_meta") or {}
        left = [
            f"[key]Décision:[/] [value]{rout.get('decision')}[/]",
            f"[key]RAG conf:[/] [value]{rout.get('rag_conf')}[/]",
            f"[key]Raison:[/] {rout.get('reason')}",
        ]
        if rout.get("matched_special"):
            left.append(f"[key]Intent spécial:[/] {rout.get('matched_special')}")
        left.append(f"[key]Seuils:[/] rag_first={rout.get('thresholds',{}).get('rag_first')} · llm_first={rout.get('thresholds',{}).get('llm_first')}")

        right = [
            f"[key]Filtres:[/] {filters or '(aucun)'}",
            f"[key]Top meta:[/] {meta or '(n/a)'}",
        ]
        panels = [
            Panel("\n".join(left), title="🧭 Routing", border_style="magenta"),
            Panel("\n".join(right), title="🔖 Contexte", border_style="green"),
        ]
        console.print(Columns(panels, expand=True))

    @staticmethod
    def debug_passport(passport: dict):
        """Affichage détaillé: poids/signaux/pénalités + stats RAG."""
        rout = passport.get("routing", {})
        stats = rout.get("rag_stats", {}) or {}
        weights = stats.get("weights", {})
        signals = stats.get("signals", {})
        penalties = stats.get("penalties", {})

        left = [
            "[key]Poids (normalisés):[/]",
            f"  sim={round(weights.get('sim',0.0),3)}  struct={round(weights.get('struct',0.0),3)}  kw={round(weights.get('kw',0.0),3)}  pin={round(weights.get('pin',0.0),3)}",
            "",
            "[key]Signaux:[/]",
            f"  sim={round(signals.get('sim',0.0),3)}  struct={round(signals.get('struct',0.0),3)}  kw={signals.get('kw_signal')}  pin={signals.get('pin_signal')}",
            f"  weak_ctx={signals.get('weak_ctx')}",
        ]
        right = [
            "[key]Stats RAG:[/]",
            f"  hits={stats.get('hits')}  k={stats.get('k')}  sim_max={round(stats.get('sim_max',0.0),3)}  struct_hits={stats.get('struct_hits')}",
            "",
            "[key]Pénalités:[/]",
            f"  weak_penalty={penalties.get('weak_penalty')}  focus_penalty={penalties.get('weak_penalty_focus')}",
        ]
        console.print(Columns([
            Panel("\n".join(left), title="⚖️ Scores & Signaux", border_style="yellow"),
            Panel("\n".join(right), title="📊 RAG Stats", border_style="cyan"),
        ], expand=True))

    @staticmethod
    def debug_trace(debug_record: dict):
        """
        Affiche la trace LLM si fournie par l'assistant:
        {
          "llm_primary": "...", "llm_fallback": "...",
          "rewriter": "...",
          "events": [{"name": "...", "model": "...", "t": 123, "ms": 42, "meta": {...}}, ...]
        }
        """
        header = [
            f"[key]Primary:[/] {debug_record.get('llm_primary','?')}",
            f"[key]Fallback:[/] {debug_record.get('llm_fallback','(aucun)')}",
            f"[key]Rewriter:[/] {debug_record.get('rewriter','(désactivé)')}",
        ]
        table = Table(title="⏱️  LLM Trace", show_lines=True, border_style="dim")
        table.add_column("#", justify="right", width=3)
        table.add_column("Étape", style="cyan", width=18)
        table.add_column("Modèle", style="value")
        table.add_column("Durée (ms)", justify="right", width=10)
        table.add_column("Meta", style="dim")

        events = debug_record.get("events") or []
        for i, ev in enumerate(events, 1):
            meta = ev.get("meta") or {}
            table.add_row(
                str(i),
                ev.get("name","?"),
                ev.get("model","?"),
                str(ev.get("ms","?")),
                JSON.from_data(meta, indent=0).text if meta else ""
            )
        console.print(Panel("\n".join(header), title="🧪 LLMs", border_style="green"))
        if events:
            console.print(table)

    @staticmethod
    def searching():
        console.print("\n[info]🔍 Recherche en cours...[/]")

    @staticmethod
    def goodbye():
        console.print("\n[success]👋 Au revoir![/]")

# ===== Export =====

__all__ = ["console", "CLIFormatter", "GITHUB_DARK_THEME"]
