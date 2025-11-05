"""
Test toutes les commandes CLI pour vérifier qu'elles sont reconnues.

Ce test vérifie que TOUTES les commandes de l'ancien système sont disponibles
dans le nouveau système avec l'adaptateur.
"""

import sys
from io import StringIO
from unittest.mock import Mock, patch, MagicMock

# Import du CLI
from src.ui.cli.app import MathCLI
from src.application.adapters.legacy_assistant_adapter import LegacyAssistantAdapter


def test_all_commands_recognized():
    """
    Test que toutes les commandes CLI sont reconnues.
    """
    print("\n" + "="*70)
    print("TEST: Vérification de toutes les commandes CLI")
    print("="*70 + "\n")
    
    # Liste de TOUTES les commandes du CLI
    commands_to_test = [
        # Aide
        ("/help", "Aide générale"),
        ("/aide", "Aide (alias)"),
        ("/?", "Aide (alias)"),
        ("/man /qcm", "Manuel d'une commande"),
        
        # Gestion de mémoire
        ("/pin", "Épingler contexte"),
        ("/pin on", "Épingler contexte (avec arg)"),
        ("/unpin", "Désépingler contexte"),
        ("/unpin off", "Désépingler contexte (avec arg)"),
        ("/forget", "Oublier tout"),
        ("/new-chat", "Nouveau chat"),
        
        # Scope
        ("/show", "Afficher scope"),
        ("/scope show", "Afficher scope"),
        ("/scope clear", "Effacer scope"),
        ("/scope set chapter=5", "Définir scope"),
        ("/ch 5", "Définir chapitre"),
        ("/bloc théorème 5.7", "Définir bloc"),
        ("/type exercice", "Définir type"),
        ("/reset", "Reset scope"),
        
        # Router
        ("/router show", "Afficher router"),
        ("/router auto", "Router auto"),
        ("/router rag", "Forcer RAG"),
        ("/router llm", "Forcer LLM"),
        ("/router hybrid", "Router hybrid"),
        ("/oot on", "Autoriser hors-programme"),
        ("/oot off", "Interdire hors-programme"),
        
        # Backend
        ("/backend show", "Afficher backend"),
        ("/backend local", "Backend local"),
        ("/backend cloud", "Backend cloud"),
        ("/backend hybrid", "Backend hybrid"),
        ("/models", "Liste modèles"),
        ("/where", "Répertoires"),
        
        # Tâches rapides
        ("/qcm séries de Fourier", "Générer QCM"),
        ("/exam 5,6,7", "Générer examen"),
        ("/fiche intégration", "Fiche de révision"),
        ("/kholle espaces vectoriels", "Sujet de khôlle"),
        ("/tutor on", "Activer tuteur"),
        ("/tutor explain on", "Activer explain"),
        ("/tutor démontrer convergence", "Tuteur ponctuel"),
        ("/formule Stokes", "Chercher formule"),
        ("/resume séries entières", "Résumé de cours"),
        ("/cours convergence uniforme", "Mini-cours"),
        ("/corrige-exo mon exercice", "Corriger exercice"),
        ("/corrige-exam mon examen", "Corriger examen"),
        
        # Filtres rapides
        ("/exercice intégration par parties", "Filtre exercice"),
        ("/méthode résolution EDO", "Filtre méthode"),
        ("/théorie théorème de Cauchy", "Filtre théorie"),
        ("/cours séries de Fourier", "Filtre cours"),
        
        # Utilitaires
        ("/debug on", "Activer debug"),
        ("/debug off", "Désactiver debug"),
        ("/link on", "Activer auto-link"),
        ("/link off", "Désactiver auto-link"),
        ("/log save", "Sauvegarder logs"),
        ("/passport", "Afficher passport"),
        ("/blocks", "Liste tous les blocs"),
        ("/blocks 5", "Liste blocs chapitre 5"),
        ("/find-bloc théorème 5.7", "Chercher un bloc"),
    ]
    
    print(f"Nombre de commandes à tester: {len(commands_to_test)}\n")
    
    # Mock du facade et des composants
    with patch('src.application.adapters.legacy_assistant_adapter.get_di_container') as mock_container:
        # Mock DI Container
        mock_di = Mock()
        mock_di.get_retriever.return_value = Mock()
        mock_di.get_llm_provider.return_value = Mock()
        mock_di.get_router.return_value = Mock()
        mock_di.get_prompt_repository.return_value = Mock()
        mock_di.get_answer_question_use_case.return_value = Mock()
        mock_container.return_value = mock_di
        
        # Mock de l'assistant
        mock_assistant = Mock(spec=LegacyAssistantAdapter)
        mock_assistant.memory = Mock()
        mock_assistant.memory.chat_id = "test_123"
        mock_assistant.memory.state = {"pinned_meta": None, "last_top_meta": None}
        mock_assistant.memory.best_context_meta.return_value = None
        mock_assistant.memory.reset.return_value = None
        mock_assistant.memory.scope_show.return_value = {}
        mock_assistant.memory.scope_clear.return_value = None
        mock_assistant.memory.scope_set.return_value = None
        mock_assistant.ensure_ready.return_value = None
        mock_assistant.new_session.return_value = None
        mock_assistant.enable_logs.return_value = None
        mock_assistant.save_logs.return_value = None
        mock_assistant.engine = Mock()
        mock_assistant.engine._get_all_docs.return_value = []
        
        # Tester chaque commande
        results = []
        for cmd, description in commands_to_test:
            try:
                # Créer une instance du CLI avec l'assistant mocké
                with patch('src.ui.cli.app.get_assistant') as mock_get_assistant:
                    mock_get_assistant.return_value = mock_assistant
                    
                    cli = MathCLI()
                    
                    # Capturer stdout pour éviter le spam
                    old_stdout = sys.stdout
                    sys.stdout = StringIO()
                    
                    # Tester la commande
                    is_command = cli.handle_command(cmd)
                    
                    # Restaurer stdout
                    sys.stdout = old_stdout
                    
                    if is_command:
                        results.append((cmd, description, "✅ RECONNUE"))
                    else:
                        # Si handle_command retourne False, c'est une question normale
                        # Certaines commandes avec payload (ex: /exercice ...) sont des questions
                        if cmd.startswith(("/exercice ", "/méthode ", "/théorie ", "/cours ")):
                            results.append((cmd, description, "✅ FILTRE (question)"))
                        else:
                            results.append((cmd, description, "❌ NON RECONNUE"))
            
            except Exception as e:
                results.append((cmd, description, f"❌ ERREUR: {str(e)[:50]}"))
        
        # Afficher les résultats
        print("\nRÉSULTATS:\n")
        print(f"{'Commande':<40} {'Description':<30} {'Status':<30}")
        print("-" * 100)
        
        success_count = 0
        for cmd, desc, status in results:
            print(f"{cmd:<40} {desc:<30} {status:<30}")
            if "✅" in status:
                success_count += 1
        
        print("-" * 100)
        print(f"\nTotal: {success_count}/{len(commands_to_test)} commandes reconnues")
        
        if success_count == len(commands_to_test):
            print("\n🎉 SUCCÈS: Toutes les commandes sont reconnues !\n")
            return True
        else:
            print(f"\n⚠️  ATTENTION: {len(commands_to_test) - success_count} commandes non reconnues\n")
            return False


if __name__ == "__main__":
    success = test_all_commands_recognized()
    sys.exit(0 if success else 1)
