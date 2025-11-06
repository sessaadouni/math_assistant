#!/usr/bin/env python3
"""
Affichage des prompts pour inspection.

Ce script affiche les prompts réels qui seront envoyés au LLM.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.prompts.course import CourseBuildPrompt, CourseExplainPrompt


def show_prompts():
    """Affiche les prompts pour inspection."""
    
    print("\n" + "=" * 80)
    print("🔍 INSPECTION DES PROMPTS DE COURS")
    print("=" * 80)
    
    # Variables d'exemple
    example_vars = {
        "topic": "convergence uniforme",
        "level": "prépa",
        "context": "[Doc 1 – p.42, ch.5]\nDéfinition: Une suite de fonctions...\n\n[Doc 2 – p.43, ch.5]\nThéorème: Si une suite converge uniformément..."
    }
    
    # ========================================================================
    # MINI-COURS
    # ========================================================================
    print("\n" + "─" * 80)
    print("📚 1. PROMPT MINI-COURS (explain_course)")
    print("─" * 80)
    
    explain_prompt = CourseExplainPrompt()
    print("\n🏷️  Task:", explain_prompt.get_task_name())
    print("📄 Type:", explain_prompt.__class__.__name__)
    print("\n" + "─" * 80)
    print("TEMPLATE:")
    print("─" * 80)
    
    # Récupérer le template
    template_str = explain_prompt.template.messages[0].prompt.template
    print(template_str)
    
    print("\n" + "─" * 80)
    print("EXEMPLE FORMATÉ (avec variables):")
    print("─" * 80)
    formatted = template_str.format(**example_vars)
    print(formatted[:800])
    print("\n... (tronqué pour lisibilité)")
    
    # ========================================================================
    # COURS COMPLET
    # ========================================================================
    print("\n\n" + "─" * 80)
    print("📖 2. PROMPT COURS COMPLET (build_course)")
    print("─" * 80)
    
    build_prompt = CourseBuildPrompt()
    print("\n🏷️  Task:", build_prompt.get_task_name())
    print("📄 Type:", build_prompt.__class__.__name__)
    print("\n" + "─" * 80)
    print("TEMPLATE:")
    print("─" * 80)
    
    # Récupérer le template
    template_str = build_prompt.template.messages[0].prompt.template
    print(template_str)
    
    print("\n" + "─" * 80)
    print("EXEMPLE FORMATÉ (avec variables):")
    print("─" * 80)
    formatted = template_str.format(**example_vars)
    print(formatted[:800])
    print("\n... (tronqué pour lisibilité)")
    
    # ========================================================================
    # COMPARAISON
    # ========================================================================
    print("\n\n" + "=" * 80)
    print("📊 COMPARAISON DES TEMPLATES")
    print("=" * 80)
    
    explain_template = CourseExplainPrompt().template.messages[0].prompt.template
    build_template = CourseBuildPrompt().template.messages[0].prompt.template
    
    print(f"""
┌───────────────────────────┬──────────────────┬──────────────────┐
│ Métrique                  │ Mini-cours       │ Cours complet    │
├───────────────────────────┼──────────────────┼──────────────────┤
│ Longueur template (chars) │ {len(explain_template):>16} │ {len(build_template):>16} │
│ Ratio                     │              1.0x │ {len(build_template)/len(explain_template):>14.1f}x │
│ Structure                 │       7 sections │       9 sections │
│ Double piste (CPGE/Ingé)  │              Non │              Oui │
│ Exercices détaillés       │              Non │              Oui │
│ Contre-exemples           │              Non │              Oui │
└───────────────────────────┴──────────────────┴──────────────────┘
    """)
    
    print("\n🔑 Points clés:")
    
    print("\n📚 Mini-cours (explain_course):")
    print("  • Template plus court et direct")
    print("  • Focus sur la pédagogie et l'accessibilité")
    print("  • FAQ intégrée")
    print("  • 7 sections structurées")
    
    print("\n📖 Cours complet (build_course):")
    print("  • Template enrichi et détaillé")
    print("  • Double piste: CPGE-preuve + Appli-ingénieur")
    print("  • Preuves (esquisses) + méthodes")
    print("  • 9 sections avec exercices détaillés")
    print("  • Contre-exemples obligatoires")
    print("  • Mini-révision interactive")
    
    print("\n" + "=" * 80)
    print("✅ INSPECTION TERMINÉE")
    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        show_prompts()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
