#!/usr/bin/env python3
"""
Test rapide des prompts enrichis course_build et course_explain
"""

import sys
from src.assistant.prompts import COURSE_BUILD_PROMPT, COURSE_EXPLAIN_PROMPT

def test_prompts():
    print("🧪 Test des prompts enrichis\n")
    print("=" * 70)
    
    # Test 1: COURSE_BUILD_PROMPT
    print("\n📖 1. COURSE_BUILD_PROMPT (cours complet)")
    print("-" * 70)
    
    build_template = COURSE_BUILD_PROMPT.messages[0].prompt.template
    
    # Vérifications
    checks_build = {
        "Double piste (🔬 + ⚙️)": "🔬" in build_template and "⚙️" in build_template,
        "9 sections": "**9)" in build_template,
        "30-45min": "30-45min" in build_template,
        "COURS COMPLET": "COURS COMPLET" in build_template,
        "Exercices (5-6)": "5-6 exercices" in build_template or "Exercices d'application" in build_template,
        "Mini-révision": "Mini-révision" in build_template or "révision interactive" in build_template,
    }
    
    print(f"Longueur: {len(build_template)} caractères")
    print("\nVérifications:")
    for check, result in checks_build.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # Test 2: COURSE_EXPLAIN_PROMPT
    print("\n\n📚 2. COURSE_EXPLAIN_PROMPT (mini-cours)")
    print("-" * 70)
    
    explain_template = COURSE_EXPLAIN_PROMPT.messages[0].prompt.template
    
    checks_explain = {
        "MINI-COURS": "MINI-COURS" in explain_template,
        "10-15min": "10-15min" in explain_template,
        "7 sections": "**7)" in explain_template,
        "FAQ": "FAQ" in explain_template,
        "L'essentiel en 3 phrases": "L'essentiel en 3 phrases" in explain_template or "essentiel" in explain_template.lower(),
    }
    
    print(f"Longueur: {len(explain_template)} caractères")
    print("\nVérifications:")
    for check, result in checks_explain.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # Test 3: Ratio
    print("\n\n📊 3. Comparaison")
    print("-" * 70)
    ratio = len(build_template) / len(explain_template)
    print(f"Ratio longueur (build/explain): {ratio:.2f}x")
    print(f"  → Build: {len(build_template)} chars")
    print(f"  → Explain: {len(explain_template)} chars")
    
    # Test 4: Variables attendues
    print("\n\n🔍 4. Variables dans les templates")
    print("-" * 70)
    
    vars_build = [v for v in ["{notion}", "{level}", "{context}"] if v in build_template]
    vars_explain = [v for v in ["{topic}", "{level}", "{context}"] if v in explain_template]
    
    print(f"COURSE_BUILD_PROMPT: {', '.join(vars_build)}")
    print(f"COURSE_EXPLAIN_PROMPT: {', '.join(vars_explain)}")
    
    # Résumé
    print("\n\n" + "=" * 70)
    all_checks = list(checks_build.values()) + list(checks_explain.values())
    success_rate = sum(all_checks) / len(all_checks) * 100
    
    if success_rate == 100:
        print("✅ Tous les tests passent ! Les prompts sont bien enrichis.")
        return 0
    else:
        print(f"⚠️  {success_rate:.0f}% des vérifications passent.")
        return 1

if __name__ == "__main__":
    sys.exit(test_prompts())
