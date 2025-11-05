#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests rapides Phase 3 - Infrastructure uniquement (sans LLM)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_solid_phase3 import (
    test_1_intent_detector,
    test_2_intent_router,
    test_3_hybrid_retriever,
    test_4_di_container_no_adapters,
    reset_container,
)


def run_fast_tests():
    """Execute les tests rapides (sans LLM ni performance)"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  TESTS RAPIDES PHASE 3 - INFRASTRUCTURE ONLY".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    tests = [
        ("Intent Detector", test_1_intent_detector),
        ("Intent Router", test_2_intent_router),
        ("Hybrid Retriever", test_3_hybrid_retriever),
        ("Suppression Adapters", test_4_di_container_no_adapters),
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
        print("█" + "  🎉 TOUS LES TESTS CORE PASSENT !".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█" + "  ✅ IntentDetector: OK".center(78) + "█")
        print("█" + "  ✅ IntentRouter: OK".center(78) + "█")
        print("█" + "  ✅ HybridRetriever: OK".center(78) + "█")
        print("█" + "  ✅ Adapters supprimés: OK".center(78) + "█")
    else:
        print("█" + f"  ⚠️  {failed} test(s) échoué(s)".center(78) + "█")
    
    print("█" + " "*78 + "█")
    print("█"*80)
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = run_fast_tests()
        sys.exit(0 if success else 1)
    finally:
        reset_container()
