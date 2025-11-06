#!/usr/bin/env python3
"""
Test script for improved course prompts.

Tests the difference between:
- course_explain (mini-course, 10-15min read)
- course_build (complete course, CPGE + Engineering tracks)
"""

import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent))

from src.application.facades.math_assistant_facade import MathAssistantFacade


def test_mini_course():
    """Test mini-course (course_explain)."""
    print("=" * 80)
    print("TEST 1: Mini-cours (course_explain) - Lecture rapide 10-15min")
    print("=" * 80)
    
    assistant = MathAssistantFacade()
    
    # Test on a simple topic
    result = assistant.explain_course(
        topic="séries de Fourier",
        level="prépa/terminale+",
        chapter="8"
    )
    
    print("\n📚 MINI-COURS (explain_course):")
    print("-" * 80)
    print(result["answer"][:500])  # First 500 chars
    print("\n... (truncated)\n")
    print(f"✓ Longueur totale: {len(result['answer'])} caractères")
    print(f"✓ Sources: {len(result['sources'])} documents")
    print()


def test_complete_course():
    """Test complete course (course_build)."""
    print("=" * 80)
    print("TEST 2: Cours complet (course_build) - Exhaustif avec double piste")
    print("=" * 80)
    
    assistant = MathAssistantFacade()
    
    # Test on same topic
    result = assistant.build_course(
        topic="séries de Fourier",
        level="prépa/terminale+",
        chapter="8"
    )
    
    print("\n📖 COURS COMPLET (build_course):")
    print("-" * 80)
    print(result["answer"][:500])  # First 500 chars
    print("\n... (truncated)\n")
    print(f"✓ Longueur totale: {len(result['answer'])} caractères")
    print(f"✓ Sources: {len(result['sources'])} documents")
    print()


def test_comparison():
    """Compare both approaches."""
    print("=" * 80)
    print("TEST 3: Comparaison des deux approches")
    print("=" * 80)
    
    assistant = MathAssistantFacade()
    
    topic = "convergence uniforme"
    
    print(f"\n📊 Comparaison sur: {topic}\n")
    
    # Mini-cours
    mini = assistant.explain_course(topic=topic, level="prépa")
    print(f"Mini-cours (explain):")
    print(f"  - Longueur: {len(mini['answer'])} chars")
    print(f"  - Sources: {len(mini['sources'])} docs")
    print(f"  - Objectif: Explication rapide et pédagogique\n")
    
    # Cours complet
    complet = assistant.build_course(topic=topic, level="prépa")
    print(f"Cours complet (build):")
    print(f"  - Longueur: {len(complet['answer'])} chars")
    print(f"  - Sources: {len(complet['sources'])} docs")
    print(f"  - Objectif: Traitement exhaustif CPGE + Ingé\n")
    
    ratio = len(complet['answer']) / len(mini['answer']) if len(mini['answer']) > 0 else 0
    print(f"📈 Ratio de longueur (complet/mini): {ratio:.1f}x")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🧪 TEST DES PROMPTS DE COURS AMÉLIORÉS")
    print("=" * 80)
    print()
    
    try:
        test_mini_course()
        test_complete_course()
        test_comparison()
        
        print("=" * 80)
        print("✅ TOUS LES TESTS TERMINÉS")
        print("=" * 80)
        print()
        print("RÉSUMÉ:")
        print("  - course_explain → Mini-cours pédagogique (10-15min)")
        print("  - course_build   → Cours complet exhaustif (double piste)")
        print()
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
