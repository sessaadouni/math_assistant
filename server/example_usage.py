"""
Exemple d'utilisation du MathAssistantFacade

Ce fichier montre comment utiliser le MathAssistant avec l'architecture SOLID.
"""

from src.application.facades import get_assistant
from src.domain.value_objects import Filters


def main():
    """
    Démonstration du MathAssistantFacade
    
    LE DI CONTAINER FAIT TOUT LE TRAVAIL AUTOMATIQUEMENT :
    ========================================================
    - Charge le vector store (Chroma)
    - Configure le retriever (BM25 + Vector + Reranker)
    - Configure le LLM (avec fallback)
    - Configure le router (avec intent detection)
    - Configure les prompts (17 prompts)
    - Crée les 16 use cases
    
    Vous n'avez qu'à appeler get_assistant() et c'est tout !
    """
    
    print("\n" + "="*70)
    print("MathAssistantFacade - Démonstration de structure")
    print("="*70 + "\n")
    
    # Obtenir l'assistant (le DI Container fait tout automatiquement !)
    print("📦 Initialisation du MathAssistant...")
    assistant = get_assistant()
    print("✅ Assistant initialisé !")
    print()
    
    # ========================================================================
    # Vérification de structure (sans appels LLM - trop lent pour démo)
    # ========================================================================
    print("🔍 Vérification de la structure de l'assistant...")
    print("-" * 70 + "\n")
    
    # Vérifier que le Container existe
    print("✓ DI Container créé")
    print(f"  - Retriever: {type(assistant.container._singletons.get('retriever')).__name__}")
    print(f"  - LLM Provider: {type(assistant.container._singletons.get('llm_provider')).__name__}")
    print(f"  - Router: {type(assistant.container._singletons.get('router')).__name__}")
    print(f"  - Prompts: {type(assistant.container._singletons.get('prompt_repository')).__name__}")
    print()
    
    # Vérifier les 17 méthodes du facade
    print("✓ MathAssistantFacade avec 17 méthodes disponibles:")
    methods = [
        "ask", "explain_course", "build_course", "summarize_course",
        "create_sheet", "review_sheet", 
        "generate_exercises", "solve_exercise", "correct_exercise",
        "generate_exam", "correct_exam", "generate_qcm", "generate_kholle",
        "explain_theorem", "explain_formula", "prove_statement", "run_task"
    ]
    for method in methods:
        has_method = hasattr(assistant, method) and callable(getattr(assistant, method))
        print(f"  - {method}(): {'✓' if has_method else '✗'}")
    print()
    
    # Vérifier les 16 use cases dans le container
    print("✓ 16 Use Cases enregistrés dans le DI Container:")
    use_case_keys = [
        "answer_question", "explain_course", "build_course", "summarize_course",
        "generate_exercise", "solve_exercise", "correct_exercise",
        "explain_theorem", "explain_formula", "prove_statement",
        "create_sheet", "review_sheet",
        "generate_exam", "correct_exam", "generate_qcm", "generate_kholle"
    ]
    for key in use_case_keys:
        factory_method = f"get_{key}_use_case"
        has_factory = hasattr(assistant.container, factory_method)
        print(f"  - {key}: {'✓' if has_factory else '✗'}")
    print()
    
    # Vérifier session management
    print("✓ Session Management:")
    print(f"  - Session ID actuel: {assistant.get_session_id()}")
    assistant.new_session()
    print(f"  - Nouvelle session créée: {assistant.get_session_id()}")
    print()
    
    # ========================================================================
    # Exemple d'utilisation (sans exécution LLM)
    # ========================================================================
    print("\n📚 Exemples d'utilisation (sans appels LLM):")
    print("-" * 70 + "\n")
    
    print("1️⃣  Question & Réponse:")
    print("   assistant.ask('C\\'est quoi une série de Fourier ?', chapter='8')")
    print()
    
    print("2️⃣  Génération d'exercices:")
    print("   assistant.generate_exercises('intégration par parties', count=3)")
    print()
    
    print("3️⃣  Explication de théorème:")
    print("   assistant.explain_theorem('théorème de convergence dominée')")
    print()
    
    print("4️⃣  Création d'examen:")
    print("   assistant.generate_exam(chapters='5,6,7', duration='3h')")
    print()
    
    print("5️⃣  API backward-compatible:")
    print("   assistant.run_task('qcm', 'séries entières', num_questions=5)")
    print()
    
    # ========================================================================
    # Résumé
    # ========================================================================
    print("\n" + "="*70)
    print("✅ RÉSUMÉ : Pourquoi le DI Container est essentiel")
    print("="*70)
    print("""
1. **Simplicité** : 
   ❌ Avant: ~100 lignes pour créer retriever, llm, router, prompts...
   ✅ Maintenant: 1 ligne → assistant = get_assistant()

2. **Performance** :
   - Objets lourds créés UNE SEULE FOIS (singletons automatiques)
   - Retriever, LLM, Store réutilisés entre les appels

3. **Maintenabilité** :
   - Configuration centralisée dans di_container.py
   - Changement de config = 1 seul endroit à modifier

4. **Testabilité** :
   - On peut injecter des mocks facilement
   - container.register_singleton("llm_provider", MockLLM())

5. **SOLID** :
   - Inversion de Dépendance (Dependency Inversion Principle)
   - Chaque composant ne connaît que les interfaces, pas les implémentations
""")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
