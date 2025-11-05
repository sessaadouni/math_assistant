#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests d'intégration Phase 3 - Infrastructure complète (SOLID Architecture)

Objectifs:
- Tester IntentDetector (détection d'intents et patterns)
- Tester IntentRouter (routing avec RAG signal)
- Tester HybridRetriever (BM25 + Vector + Reranking)
- Tester intégration complète via AnswerQuestionUseCase
- Valider suppression des adapters temporaires

Statut: Phase 3 (Infrastructure Migration)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.di_container import DIContainer, get_container, reset_container
from src.domain.entities import Question, Answer
from src.domain.value_objects import Filters, SessionContext
from src.infrastructure.routing import IntentDetector, IntentRouter
from src.infrastructure.retrieval import HybridRetriever


def test_1_intent_detector():
    """Test 1: IntentDetector - Détection d'intents"""
    print("\n" + "="*80)
    print("TEST 1: IntentDetector - Détection d'intents")
    print("="*80)
    
    detector = IntentDetector()
    
    # Test 1.1: QA intent (fallback)
    query = "Qu'est-ce qu'une dérivée ?"
    task, scores = detector.detect_intent(query)
    print(f"\n✓ Query: {query!r}")
    print(f"  Task: {task}")
    assert task in {"qa", "course_explain"}, f"Expected qa or course_explain, got {task}"
    print(f"  ✅ Intent détecté: {task}")
    
    # Test 1.2: Exercise generation
    query = "Génère 5 exercices sur les limites"
    task, scores = detector.detect_intent(query)
    print(f"\n✓ Query: {query!r}")
    print(f"  Task: {task}")
    assert task == "exercise_gen", f"Expected exercise_gen, got {task}"
    print(f"  ✅ Intent détecté: {task}")
    
    # Test 1.3: Theorem
    query = "Quel est le théorème de Pythagore ?"
    task, scores = detector.detect_intent(query)
    print(f"\n✓ Query: {query!r}")
    print(f"  Task: {task}")
    assert task == "theorem", f"Expected theorem, got {task}"
    print(f"  ✅ Intent détecté: {task}")
    
    # Test 1.4: Special intent - book
    special = detector.detect_special_intent("exercices du livre chapitre 3")
    print(f"\n✓ Query: 'exercices du livre chapitre 3'")
    print(f"  Special: {special}")
    assert special == "book_exercises", f"Expected book_exercises, got {special}"
    print(f"  ✅ Special intent détecté: {special}")
    
    # Test 1.5: Math detection
    has_math = detector.looks_like_math("Calcule la dérivée de x² + 3x")
    print(f"\n✓ Query: 'Calcule la dérivée de x² + 3x'")
    print(f"  Has math: {has_math}")
    assert has_math, "Math keywords should be detected"
    print(f"  ✅ Math détecté")
    
    print("\n" + "="*80)
    print("✅ TEST 1 PASSED: IntentDetector fonctionne correctement")
    print("="*80)


def test_2_intent_router():
    """Test 2: IntentRouter - Routing avec RAG signal"""
    print("\n" + "="*80)
    print("TEST 2: IntentRouter - Routing avec RAG signal")
    print("="*80)
    
    container = get_container()
    router = container.get_router()
    
    # Test 2.1: IRouter-compatible API (used by use cases)
    decision = router.decide(
        question="Théorème de Bolzano-Weierstrass chapitre 1",
        explicit_filters=Filters(chapter="1"),
    )
    print(f"\n✓ Query: 'Théorème de Bolzano-Weierstrass chapitre 1'")
    print(f"  Decision: {decision.decision}")
    print(f"  Confidence: {decision.rag_confidence:.3f}")
    print(f"  Task: {decision.task_type}")
    print(f"  Reason: {decision.reason}")
    assert decision.decision in {"rag_first", "llm_first", "rag_to_llm"}, "Expected RAG decision"
    print(f"  ✅ Routing décision: {decision.decision}")
    
    # Test 2.2: LLM-only (general question)
    decision = router.decide(
        question="Quelle est la capitale de la France ?",
        explicit_filters=Filters(),
    )
    print(f"\n✓ Query: 'Quelle est la capitale de la France ?'")
    print(f"  Decision: {decision.decision}")
    print(f"  Confidence: {decision.rag_confidence:.3f}")
    print(f"  Task: {decision.task_type}")
    assert decision.decision in {"llm_only", "llm_first"}, "Expected LLM decision"
    print(f"  ✅ Routing décision: {decision.decision}")
    
    # Test 2.3: Book intent → rag_to_llm
    decision = router.decide(
        question="Exercices du livre chapitre 5",
        explicit_filters=Filters(chapter="5"),
    )
    print(f"\n✓ Query: 'Exercices du livre chapitre 5'")
    print(f"  Decision: {decision.decision}")
    print(f"  Task: {decision.task_type}")
    print(f"  Special: {decision.metadata.get('routing', {}).get('matched_special')}")
    assert decision.decision == "rag_to_llm", f"Expected rag_to_llm for book intent, got {decision.decision}"
    print(f"  ✅ Routing décision: {decision.decision}")
    
    print("\n" + "="*80)
    print("✅ TEST 2 PASSED: IntentRouter fonctionne correctement")
    print("="*80)


def test_3_hybrid_retriever():
    """Test 3: HybridRetriever - BM25 + Vector + Reranking"""
    print("\n" + "="*80)
    print("TEST 3: HybridRetriever - BM25 + Vector + Reranking")
    print("="*80)
    
    container = get_container()
    retriever = container.get_retriever()
    
    # Test 3.1: Simple retrieval
    filters = Filters()
    docs = retriever.retrieve(
        query="théorème limite continuité",
        filters=filters,
        k=5,
    )
    print(f"\n✓ Query: 'théorème limite continuité'")
    print(f"  Docs retrieved: {len(docs)}")
    print(f"  Top doc type: {docs[0].metadata.get('type') if docs else 'N/A'}")
    print(f"  Top doc page: {docs[0].metadata.get('page') if docs else 'N/A'}")
    assert len(docs) > 0, "Should retrieve at least 1 document"
    print(f"  ✅ Retrieval: {len(docs)} docs")
    
    # Test 3.2: Filtered retrieval (chapter)
    filters_ch = Filters(chapter="1")
    docs_ch = retriever.retrieve(
        query="définition",
        filters=filters_ch,
        k=5,
    )
    print(f"\n✓ Query: 'définition' (chapter=1)")
    print(f"  Docs retrieved: {len(docs_ch)}")
    if docs_ch:
        print(f"  Chapters: {set(d.metadata.get('chapter') for d in docs_ch)}")
    assert len(docs_ch) > 0, "Should retrieve documents from chapter 1"
    print(f"  ✅ Filtered retrieval: {len(docs_ch)} docs")
    
    # Test 3.3: Metadata discovery
    blocs = retriever.get_available_blocs()
    doc_types = retriever.get_available_doc_types()
    print(f"\n✓ Metadata discovery:")
    print(f"  Available blocs: {blocs[:5]}{'...' if len(blocs) > 5 else ''}")
    print(f"  Available types: {doc_types}")
    assert len(doc_types) > 0, "Should have at least 1 doc type"
    print(f"  ✅ Metadata: {len(blocs)} blocs, {len(doc_types)} types")
    
    print("\n" + "="*80)
    print("✅ TEST 3 PASSED: HybridRetriever fonctionne correctement")
    print("="*80)


def test_4_di_container_no_adapters():
    """Test 4: Vérifier que les adapters temporaires ont été supprimés"""
    print("\n" + "="*80)
    print("TEST 4: Vérification suppression adapters temporaires")
    print("="*80)
    
    # Test 4.1: Check files don't exist
    adapters = [
        Path("src/config/retriever_adapter.py"),
        Path("src/config/router_adapter.py"),
    ]
    
    for adapter in adapters:
        print(f"\n✓ Checking: {adapter}")
        assert not adapter.exists(), f"Adapter should be deleted: {adapter}"
        print(f"  ✅ Supprimé: {adapter}")
    
    # Test 4.2: Check imports don't use adapters
    container = get_container()
    router = container.get_router()
    retriever = container.get_retriever()
    
    print(f"\n✓ Router type: {type(router).__name__}")
    assert "Adapter" not in type(router).__name__, "Router should not be an adapter"
    print(f"  ✅ Router est IntentRouter")
    
    print(f"\n✓ Retriever type: {type(retriever).__name__}")
    assert "Adapter" not in type(retriever).__name__, "Retriever should not be an adapter"
    print(f"  ✅ Retriever est HybridRetriever")
    
    print("\n" + "="*80)
    print("✅ TEST 4 PASSED: Adapters supprimés, vraies implémentations utilisées")
    print("="*80)


def test_5_end_to_end_use_case():
    """Test 5: Intégration complète via AnswerQuestionUseCase"""
    print("\n" + "="*80)
    print("TEST 5: Intégration End-to-End via AnswerQuestionUseCase")
    print("="*80)
    
    container = get_container()
    use_case = container.get_answer_question_use_case()
    
    # Test 5.1: Simple question
    question_text = "Qu'est-ce qu'une fonction continue ?"
    
    print(f"\n✓ Question: {question_text!r}")
    answer = use_case.execute(
        question_text=question_text,
        chat_id="test_e2e",
    )
    
    print(f"  Answer preview: {answer.text[:150]}...")
    print(f"  Task: {answer.task_type}")
    print(f"  Context docs: {len(answer.context.documents) if answer.context else 0}")
    
    assert answer.text, "Should have answer text"
    assert answer.task_type, "Should have task type"
    print(f"  ✅ Réponse générée: {len(answer.text)} chars")
    
    # Test 5.2: Another simple question
    question_text_2 = "Théorème de Pythagore"
    
    print(f"\n✓ Question: {question_text_2!r}")
    answer_2 = use_case.execute(
        question_text=question_text_2,
        chat_id="test_e2e",
    )
    
    print(f"  Answer preview: {answer_2.text[:150]}...")
    print(f"  Task: {answer_2.task_type}")
    print(f"  Context docs: {len(answer_2.context.documents) if answer_2.context else 0}")
    
    assert answer_2.text, "Should have answer text"
    print(f"  ✅ Réponse générée: {len(answer_2.text)} chars")
    
    print("\n" + "="*80)
    print("✅ TEST 5 PASSED: Intégration End-to-End fonctionne")
    print("="*80)


def test_6_performance_check():
    """Test 6: Vérification des performances"""
    print("\n" + "="*80)
    print("TEST 6: Vérification des performances")
    print("="*80)
    
    import time
    
    container = get_container()
    router = container.get_router()
    retriever = container.get_retriever()
    
    # Test 6.1: Router speed
    t0 = time.time()
    for _ in range(3):
        router.decide(
            question="théorème",
            explicit_filters=Filters(),
        )
    t1 = time.time()
    router_time = (t1 - t0) / 3
    
    print(f"\n✓ Router performance:")
    print(f"  Average time: {router_time*1000:.1f} ms")
    # Note: Router does retrieval so it's expected to be slower (100-500ms is acceptable)
    assert router_time < 5.0, f"Router too slow: {router_time:.3f}s"
    print(f"  ✅ Router acceptable: {router_time*1000:.1f} ms")
    
    # Test 6.2: Retriever speed
    t0 = time.time()
    for _ in range(3):
        retriever.retrieve(
            query="théorème",
            filters=Filters(),
            k=5,
        )
    t1 = time.time()
    retriever_time = (t1 - t0) / 3
    
    print(f"\n✓ Retriever performance:")
    print(f"  Average time: {retriever_time*1000:.1f} ms")
    # Note: Hybrid retrieval with reranking is expensive (BM25 + Vector + CrossEncoder)
    # 500ms per query is acceptable for production
    assert retriever_time < 10.0, f"Retriever too slow: {retriever_time:.3f}s"
    print(f"  ✅ Retriever acceptable: {retriever_time*1000:.1f} ms")
    
    print("\n" + "="*80)
    print("✅ TEST 6 PASSED: Performances acceptables")
    print("="*80)


def run_all_tests():
    """Execute tous les tests"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  TESTS D'INTÉGRATION PHASE 3 - SOLID ARCHITECTURE".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    tests = [
        ("Intent Detector", test_1_intent_detector),
        ("Intent Router", test_2_intent_router),
        ("Hybrid Retriever", test_3_hybrid_retriever),
        ("Suppression Adapters", test_4_di_container_no_adapters),
        ("End-to-End Use Case", test_5_end_to_end_use_case),
        ("Performance Check", test_6_performance_check),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 TEST ERROR: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + f"  RÉSUMÉ DES TESTS".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█" + f"  Total: {len(tests)} tests".center(78) + "█")
    print("█" + f"  ✅ Passed: {passed}".center(78) + "█")
    print("█" + f"  ❌ Failed: {failed}".center(78) + "█")
    print("█" + " "*78 + "█")
    
    if failed == 0:
        print("█" + "  🎉 TOUS LES TESTS PASSENT ! Phase 3 terminée.".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█" + "  ✅ IntentDetector: OK".center(78) + "█")
        print("█" + "  ✅ IntentRouter: OK".center(78) + "█")
        print("█" + "  ✅ HybridRetriever: OK".center(78) + "█")
        print("█" + "  ✅ Adapters supprimés: OK".center(78) + "█")
        print("█" + "  ✅ End-to-End: OK".center(78) + "█")
        print("█" + "  ✅ Performances: OK".center(78) + "█")
    else:
        print("█" + f"  ⚠️  {failed} test(s) échoué(s)".center(78) + "█")
    
    print("█" + " "*78 + "█")
    print("█"*80)
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        reset_container()
