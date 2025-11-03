# -*- coding: utf-8 -*-
"""
src/ui/cli/styles.py
Styles Rich pour le CLI (GitHub Dark inspired)
"""

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
  • [command]/cours[/] <notion>         → Mini-cours structuré
  • [command]/corrige-exo[/] <texte>    → Correction d’exercice
  • [command]/corrige-exam[/] <texte>   → Correction d’examen

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
            "cours": """
[title]/cours[/]

[subtitle]Description:[/]
Génère un mini-cours structuré sur une notion ou recherche dans tout le cours
(selon le contexte d'utilisation).

[subtitle]Usage:[/]
  [command]/cours[/] <notion>  → Génère un mini-cours
  [command]/cours[/] <q>       → Recherche filtrée (après question)

[subtitle]Exemples:[/]
  [command]/cours séries de Fourier[/]
  [command]/cours limites et continuité[/]

[subtitle]Structure du mini-cours:[/]
  • Introduction
  • Définitions
  • Théorèmes
  • Exemples
  • Applications
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
    def prompt(text: str = "Ta question", tutor_mode: bool = False, tutor_strict: bool = False, tutor_explain: bool = False) -> str:
        badges = []
        
        if tutor_mode:
            if tutor_strict:
                badges.append("[dim][[/][value]🎓 TUTEUR[/][dim]][/] [dim][[/][warning]strict[/][dim]][/]")
            else:
                badges.append("[dim][[/][value]🎓 TUTEUR[/][dim]][/] [dim][[/][info]smart[/][dim]][/]")
        
        if tutor_explain:
            badges.append("[dim][[/][value]🧠 EXPLAIN[/][dim]][/]")
        
        if badges:
            badge_str = " ".join(badges) + " "
            return console.input(f"\n{badge_str}[prompt]💬 {text}[/]: ").strip()
        
        return console.input(f"\n[prompt]💬 {text}[/]: ").strip()

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
