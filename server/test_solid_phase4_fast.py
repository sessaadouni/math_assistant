"""
Tests rapides pour Phase 4 - QueryRewriter extraction

Ces tests valident l'extraction du QueryRewriter en service SOLID sans LLM.
"""

import sys
import os
from pathlib import Path

# Add server to path
server_dir = Path(__file__).parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))


def test_query_rewriter_interface():
    """Test 1: Vérifier que l'interface IQueryRewriter est bien définie"""
    from src.application.interfaces.query_rewriter import IQueryRewriter
    from abc import ABC
    
    # L'interface doit être une ABC
    assert issubclass(IQueryRewriter, ABC), "IQueryRewriter doit hériter de ABC"
    
    # Vérifier la signature de la méthode abstraite
    assert hasattr(IQueryRewriter, 'rewrite'), "IQueryRewriter doit avoir une méthode rewrite()"
    
    # Vérifier qu'on ne peut pas instancier directement
    try:
        _ = IQueryRewriter()
        assert False, "Ne devrait pas pouvoir instancier IQueryRewriter directement"
    except TypeError:
        pass  # Comportement attendu
    
    print("✓ Test 1 passed: IQueryRewriter interface correctly defined")


def test_ollama_query_rewriter_implementation():
    """Test 2: Vérifier l'implémentation OllamaQueryRewriter"""
    from src.infrastructure.query.ollama_query_rewriter import OllamaQueryRewriter
    from src.application.interfaces.query_rewriter import IQueryRewriter
    from src.config.settings import Settings, rag_config, ui_config
    
    # OllamaQueryRewriter doit implémenter IQueryRewriter
    assert issubclass(OllamaQueryRewriter, IQueryRewriter), \
        "OllamaQueryRewriter doit implémenter IQueryRewriter"
    
    # Créer une instance avec settings
    settings = Settings(rag_config, ui_config)
    
    # Mock LLM pour éviter les appels réseau
    class MockLLM:
        def invoke(self, prompt):
            class MockResponse:
                content = "Question reformulée de test"
            return MockResponse()
    
    rewriter = OllamaQueryRewriter(settings=settings, llm=MockLLM())
    
    # Vérifier les attributs
    assert hasattr(rewriter, 'settings'), "Doit avoir attribut settings"
    assert hasattr(rewriter, 'llm'), "Doit avoir attribut llm"
    assert hasattr(rewriter, 'prompt_template'), "Doit avoir attribut prompt_template"
    
    print("✓ Test 2 passed: OllamaQueryRewriter correctly implements interface")


def test_query_rewriter_no_rewrite_cases():
    """Test 3: Vérifier les cas où la réécriture est désactivée ou inutile"""
    from src.infrastructure.query.ollama_query_rewriter import OllamaQueryRewriter
    from src.config.settings import Settings, rag_config, ui_config
    
    settings = Settings(rag_config, ui_config)
    
    # Mock LLM qui ne devrait jamais être appelé
    class MockLLM:
        def invoke(self, prompt):
            raise AssertionError("LLM ne devrait pas être appelé dans ces cas")
    
    rewriter = OllamaQueryRewriter(settings=settings, llm=MockLLM())
    
    question = "Quelle est la différence ?"
    
    # Cas 1: is_follow_up=False → pas de réécriture
    result = rewriter.rewrite(
        new_question=question,
        last_question="Question précédente",
        is_follow_up=False
    )
    assert result == question, "Cas 1: Devrait retourner la question originale"
    
    # Cas 2: last_question=None → pas de réécriture
    result = rewriter.rewrite(
        new_question=question,
        last_question=None,
        is_follow_up=True
    )
    assert result == question, "Cas 2: Devrait retourner la question originale"
    
    # Cas 3: réécriture désactivée
    rewriter.enabled = False
    result = rewriter.rewrite(
        new_question=question,
        last_question="Question précédente",
        is_follow_up=True
    )
    assert result == question, "Cas 3: Devrait retourner la question originale"
    
    print("✓ Test 3 passed: No-rewrite cases correctly handled")


def test_query_rewriter_with_rewrite():
    """Test 4: Vérifier la logique de réécriture et robustesse"""
    from src.infrastructure.query.ollama_query_rewriter import OllamaQueryRewriter
    from src.config.settings import Settings, rag_config, ui_config
    
    settings = Settings(rag_config, ui_config)
    
    # Test sans LLM réel: vérifier que la logique de décision fonctionne
    # On passe llm=None, ce qui causera une erreur si appelé
    rewriter = OllamaQueryRewriter(settings=settings, llm=None)
    rewriter.enabled = True
    
    original_question = "Et la différence avec la simple ?"
    
    # Cas 1: Vérifier le fallback gracieux en cas d'erreur
    # (llm=None causera une erreur, qui devrait être catchée)
    result = rewriter.rewrite(
        new_question=original_question,
        last_question="C'est quoi la convergence uniforme ?",
        context_meta={"chapter": "5", "block_kind": "definition"},
        is_follow_up=True
    )
    
    # En cas d'erreur (llm=None), devrait retourner la question originale
    assert result == original_question, \
        "En cas d'erreur LLM, devrait retourner la question originale (robustesse)"
    
    # Cas 2: Vérifier que la logique de branchement fonctionne
    # Si enabled=False, ne devrait jamais tenter d'appeler le LLM
    rewriter.enabled = False
    result2 = rewriter.rewrite(
        new_question="Une autre question",
        last_question="Question précédente",
        is_follow_up=True
    )
    assert result2 == "Une autre question", "Si disabled, devrait retourner l'originale"
    
    # Cas 3: Vérifier l'intégration dans la méthode rewrite
    # La méthode _describe_meta devrait être appelée pour formater le contexte
    rewriter.enabled = True
    meta = {"chapter": "5", "block_kind": "definition"}
    context_desc = rewriter._describe_meta(meta)
    assert context_desc != "—", "Les métadonnées devraient être formatées"
    assert "Chapitre 5" in context_desc, "Devrait inclure le numéro de chapitre"
    
    print("✓ Test 4 passed: Rewrite logic and error handling verified")


def test_describe_meta_formatting():
    """Test 5: Vérifier le formatage des métadonnées contextuelles"""
    from src.infrastructure.query.ollama_query_rewriter import OllamaQueryRewriter
    from src.config.settings import Settings, rag_config, ui_config
    
    settings = Settings(rag_config, ui_config)
    rewriter = OllamaQueryRewriter(settings=settings, llm=None)
    
    # Cas 1: métadonnées vides
    result = rewriter._describe_meta({})
    assert result == "—", "Métadonnées vides devraient retourner '—'"
    
    # Cas 2: seulement chapitre
    result = rewriter._describe_meta({"chapter": "5"})
    assert "Chapitre 5" in result, "Devrait contenir 'Chapitre 5'"
    
    # Cas 3: chapitre + block_kind
    result = rewriter._describe_meta({"chapter": "5", "block_kind": "definition"})
    assert "Chapitre 5" in result, "Devrait contenir 'Chapitre 5'"
    assert "Definition" in result, "Devrait contenir 'Definition' (capitalisé)"
    
    # Cas 4: métadonnées complètes
    result = rewriter._describe_meta({
        "chapter": "5",
        "block_kind": "theorem",
        "block_id": "42",
        "type": "cours"
    })
    assert "Chapitre 5" in result, "Devrait contenir 'Chapitre 5'"
    assert "Theorem" in result, "Devrait contenir 'Theorem'"
    assert "Bloc #42" in result, "Devrait contenir 'Bloc #42'"
    assert "Type: cours" in result, "Devrait contenir 'Type: cours'"
    
    print("✓ Test 5 passed: Metadata formatting correctly handled")


def test_di_container_integration():
    """Test 6: Vérifier l'intégration dans le DI Container"""
    from src.config.di_container import DIContainer
    from src.application.interfaces.query_rewriter import IQueryRewriter
    
    container = DIContainer()
    
    # Obtenir le query rewriter
    rewriter = container.get_query_rewriter()
    
    # Vérifier que c'est bien une implémentation de IQueryRewriter
    assert isinstance(rewriter, IQueryRewriter), \
        "get_query_rewriter() devrait retourner une instance de IQueryRewriter"
    
    # Vérifier le singleton
    rewriter2 = container.get_query_rewriter()
    assert rewriter is rewriter2, "Devrait retourner la même instance (singleton)"
    
    print("✓ Test 6 passed: DI Container integration working")


def test_all_use_cases_available():
    """Test 7: Vérifier que TOUS les use cases sont disponibles dans le DI Container"""
    from src.config.di_container import DIContainer
    from src.application.use_cases import (
        # Q&A
        AnswerQuestionUseCase,
        # Course
        ExplainCourseUseCase,
        BuildCourseUseCase,
        SummarizeCourseUseCase,
        # Sheets & Exercises
        CreateSheetUseCase,
        ReviewSheetUseCase,
        GenerateExerciseUseCase,
        SolveExerciseUseCase,
        CorrectExerciseUseCase,
        # Exams
        GenerateExamUseCase,
        CorrectExamUseCase,
        GenerateQCMUseCase,
        GenerateKholleUseCase,
        # Utilities
        ExplainTheoremUseCase,
        ExplainFormulaUseCase,
        ProveStatementUseCase,
    )
    
    container = DIContainer()
    
    # Tester chaque use case
    use_cases_to_test = [
        ("answer_question", container.get_answer_question_use_case, AnswerQuestionUseCase),
        ("explain_course", container.get_explain_course_use_case, ExplainCourseUseCase),
        ("build_course", container.get_build_course_use_case, BuildCourseUseCase),
        ("summarize_course", container.get_summarize_course_use_case, SummarizeCourseUseCase),
        ("create_sheet", container.get_create_sheet_use_case, CreateSheetUseCase),
        ("review_sheet", container.get_review_sheet_use_case, ReviewSheetUseCase),
        ("generate_exercise", container.get_generate_exercise_use_case, GenerateExerciseUseCase),
        ("solve_exercise", container.get_solve_exercise_use_case, SolveExerciseUseCase),
        ("correct_exercise", container.get_correct_exercise_use_case, CorrectExerciseUseCase),
        ("generate_exam", container.get_generate_exam_use_case, GenerateExamUseCase),
        ("correct_exam", container.get_correct_exam_use_case, CorrectExamUseCase),
        ("generate_qcm", container.get_generate_qcm_use_case, GenerateQCMUseCase),
        ("generate_kholle", container.get_generate_kholle_use_case, GenerateKholleUseCase),
        ("explain_theorem", container.get_explain_theorem_use_case, ExplainTheoremUseCase),
        ("explain_formula", container.get_explain_formula_use_case, ExplainFormulaUseCase),
        ("prove_statement", container.get_prove_statement_use_case, ProveStatementUseCase),
    ]
    
    for name, getter, expected_type in use_cases_to_test:
        use_case = getter()
        assert use_case is not None, f"{name} use case devrait être disponible"
        assert isinstance(use_case, expected_type), f"{name}: type incorrect"
        
        # Vérifier singleton
        use_case2 = getter()
        assert use_case is use_case2, f"{name}: devrait retourner la même instance (singleton)"
    
    print(f"✓ Test 7 passed: ALL {len(use_cases_to_test)} use cases correctly registered in DI Container")


def test_math_assistant_facade():
    """Test 8: Vérifier que le MathAssistantFacade fonctionne correctement"""
    from src.application.facades import MathAssistantFacade, get_assistant
    
    # Test 8a: Création du facade
    assistant = MathAssistantFacade()
    assert assistant is not None, "MathAssistantFacade devrait être créé"
    assert assistant.container is not None, "Le DI Container devrait être initialisé"
    
    # Test 8b: Vérifier que le container a bien créé les dépendances
    # Ces appels ne doivent pas lever d'exception
    try:
        retriever = assistant.container.get_retriever()
        llm = assistant.container.get_llm_provider()
        router = assistant.container.get_router()
        prompts = assistant.container.get_prompt_registry()
        assert retriever is not None, "Retriever devrait être disponible"
        assert llm is not None, "LLM devrait être disponible"
        assert router is not None, "Router devrait être disponible"
        assert prompts is not None, "Prompts devrait être disponible"
    except Exception as e:
        assert False, f"Le DI Container devrait créer les dépendances : {e}"
    
    # Test 8c: Vérifier le singleton global
    assistant1 = get_assistant()
    assistant2 = get_assistant()
    assert assistant1 is assistant2, "get_assistant() devrait retourner la même instance"
    
    # Test 8d: Vérifier que les méthodes existent
    methods_to_check = [
        'ask', 'explain_course', 'build_course', 'summarize_course',
        'create_sheet', 'review_sheet', 'generate_exercises', 
        'solve_exercise', 'correct_exercise', 'generate_exam',
        'correct_exam', 'generate_qcm', 'generate_kholle',
        'explain_theorem', 'explain_formula', 'prove_statement',
        'run_task'  # backward compatibility
    ]
    
    for method_name in methods_to_check:
        assert hasattr(assistant, method_name), f"Méthode {method_name} devrait exister"
        assert callable(getattr(assistant, method_name)), f"{method_name} devrait être callable"
    
    print("✓ Test 8 passed: MathAssistantFacade correctly initialized with DI Container")


def test_math_assistant_facade():
    """Test 8: Vérifier que le MathAssistantFacade fonctionne"""
    from src.application.facades import MathAssistantFacade, get_assistant
    
    # Test 8a: Instanciation directe
    assistant = MathAssistantFacade()
    assert assistant is not None, "MathAssistantFacade devrait être instanciable"
    assert hasattr(assistant, 'ask'), "Devrait avoir une méthode ask()"
    assert hasattr(assistant, 'generate_exercises'), "Devrait avoir generate_exercises()"
    assert hasattr(assistant, 'explain_theorem'), "Devrait avoir explain_theorem()"
    assert hasattr(assistant, 'run_task'), "Devrait avoir run_task() pour rétrocompatibilité"
    
    # Test 8b: Singleton global
    global_assistant = get_assistant()
    assert global_assistant is not None, "get_assistant() devrait retourner une instance"
    assert isinstance(global_assistant, MathAssistantFacade), "Type incorrect"
    
    # Vérifier singleton
    global_assistant2 = get_assistant()
    assert global_assistant is global_assistant2, "Devrait retourner la même instance (singleton)"
    
    # Test 8c: Vérifier les méthodes clés
    methods_to_check = [
        'ask', 'explain_course', 'build_course', 'summarize_course',
        'create_sheet', 'review_sheet', 'generate_exercises', 'solve_exercise',
        'correct_exercise', 'generate_exam', 'correct_exam', 'generate_qcm',
        'generate_kholle', 'explain_theorem', 'explain_formula', 'prove_statement',
        'run_task', 'new_session', 'get_session_id'
    ]
    
    for method_name in methods_to_check:
        assert hasattr(assistant, method_name), f"Devrait avoir la méthode {method_name}()"
        assert callable(getattr(assistant, method_name)), f"{method_name} devrait être callable"
    
    print(f"✓ Test 8 passed: MathAssistantFacade with {len(methods_to_check)} methods operational")


def run_all_tests():
    """Exécute tous les tests Phase 4"""
    print("\n" + "="*60)
    print("Phase 4 Fast Tests - Complete SOLID Architecture")
    print("="*60 + "\n")
    
    tests = [
        test_query_rewriter_interface,
        test_ollama_query_rewriter_implementation,
        test_query_rewriter_no_rewrite_cases,
        test_query_rewriter_with_rewrite,
        test_describe_meta_formatting,
        test_di_container_integration,
        test_all_use_cases_available,
        test_math_assistant_facade,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} FAILED:")
            print(f"  {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
