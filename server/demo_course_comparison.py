#!/usr/bin/env python3
"""
Exemple comparatif: Mini-cours vs Cours complet

Ce script montre concrètement la différence entre:
- explain_course (mini-cours, 10-15min)
- build_course (cours exhaustif, double piste)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.application.facades.math_assistant_facade import MathAssistantFacade


def demo():
    """Démonstration des deux types de cours."""
    
    print("\n" + "=" * 80)
    print("🎓 DÉMONSTRATION: Mini-cours vs Cours complet")
    print("=" * 80)
    
    assistant = MathAssistantFacade()
    topic = "convergence uniforme"
    
    print(f"\n📌 Sujet: {topic}")
    print(f"📌 Niveau: prépa")
    
    # ========================================================================
    # MINI-COURS
    # ========================================================================
    print("\n" + "─" * 80)
    print("📚 1. MINI-COURS (explain_course)")
    print("─" * 80)
    print("\n🎯 Objectif: Explication rapide et pédagogique (10-15min)")
    print("✓ Intuition avant rigueur")
    print("✓ FAQ intégrée")
    print("✓ Formules essentielles")
    print("\n⏳ Génération en cours...")
    
    mini = assistant.explain_course(
        topic=topic,
        level="prépa",
        chapter="5"
    )
    
    print(f"\n✅ Généré !")
    print(f"   - Longueur: {len(mini['answer']):,} caractères")
    print(f"   - Sources: {len(mini['sources'])} documents")
    print(f"\n📄 Aperçu (500 premiers caractères):")
    print("─" * 80)
    print(mini['answer'][:500])
    print("...")
    print("─" * 80)
    
    # ========================================================================
    # COURS COMPLET
    # ========================================================================
    print("\n" + "─" * 80)
    print("📖 2. COURS COMPLET (build_course)")
    print("─" * 80)
    print("\n🎯 Objectif: Traitement exhaustif et rigoureux")
    print("✓ Double piste: CPGE-preuve + Appli-ingénieur")
    print("✓ Preuves (esquisses) + méthodes détaillées")
    print("✓ Exercices corrigés pas à pas")
    print("✓ Contre-exemples et pièges")
    print("\n⏳ Génération en cours (plus long)...")
    
    complet = assistant.build_course(
        topic=topic,
        level="prépa",
        chapter="5"
    )
    
    print(f"\n✅ Généré !")
    print(f"   - Longueur: {len(complet['answer']):,} caractères")
    print(f"   - Sources: {len(complet['sources'])} documents")
    print(f"\n📄 Aperçu (500 premiers caractères):")
    print("─" * 80)
    print(complet['answer'][:500])
    print("...")
    print("─" * 80)
    
    # ========================================================================
    # COMPARAISON
    # ========================================================================
    print("\n" + "=" * 80)
    print("📊 COMPARAISON")
    print("=" * 80)
    
    ratio = len(complet['answer']) / len(mini['answer']) if len(mini['answer']) > 0 else 0
    
    print(f"""
┌─────────────────────────┬──────────────────┬──────────────────┐
│ Métrique                │ Mini-cours       │ Cours complet    │
├─────────────────────────┼──────────────────┼──────────────────┤
│ Longueur (caractères)   │ {len(mini['answer']):>15,} │ {len(complet['answer']):>15,} │
│ Ratio                   │              1.0x │ {ratio:>14.1f}x │
│ Sources utilisées       │ {len(mini['sources']):>16} │ {len(complet['sources']):>16} │
│ Temps de lecture estimé │         10-15min │         30-45min │
└─────────────────────────┴──────────────────┴──────────────────┘
    """)
    
    print("\n🎓 Cas d'usage recommandés:")
    print("\nMini-cours (explain_course):")
    print("  • Découverte rapide d'une notion")
    print("  • Révision express avant un DS")
    print("  • Besoin de clarification pédagogique")
    print("  • Vue d'ensemble avant approfondissement")
    
    print("\nCours complet (build_course):")
    print("  • Apprentissage approfondi et rigoureux")
    print("  • Préparation examen/concours")
    print("  • Besoin de preuves et justifications")
    print("  • Travail sur exercices variés")
    print("  • Construction solide des fondations")
    
    print("\n" + "=" * 80)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
