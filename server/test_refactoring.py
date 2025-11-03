#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier le refactoring avec les nouvelles librairies
"""

print("🔍 Test du refactoring avec ollama.py et text_processing.py\n")

# Test 1: Import des utilitaires
print("1️⃣  Test des imports...")
try:
    from src.utils import (
        markdown_to_html, 
        truncate_text, 
        clean_text, 
        normalize_whitespace,
        extract_latex_formulas,
        format_inline_markdown
    )
    print("   ✅ Imports src.utils OK")
except Exception as e:
    print(f"   ❌ Erreur imports src.utils: {e}")
    exit(1)

# Test 2: Import widgets
print("\n2️⃣  Test import widgets...")
try:
    from src.ui.gui import widgets
    print("   ✅ Import widgets OK")
except Exception as e:
    print(f"   ❌ Erreur import widgets: {e}")
    exit(1)

# Test 3: Import rag_engine
print("\n3️⃣  Test import rag_engine...")
try:
    from src.core import rag_engine
    print("   ✅ Import rag_engine OK")
except Exception as e:
    print(f"   ❌ Erreur import rag_engine: {e}")
    exit(1)

# Test 4: Import assistant
print("\n4️⃣  Test import assistant...")
try:
    from src.assistant import assistant
    print("   ✅ Import assistant OK")
except Exception as e:
    print(f"   ❌ Erreur import assistant: {e}")
    exit(1)

# Test 5: Fonctionnalités de text_processing
print("\n5️⃣  Test fonctionnalités text_processing...")
try:
    # Test clean_text
    dirty = "Hello    world  \n\n\n\n  test"
    cleaned = clean_text(dirty)
    assert cleaned == "Hello world\n\ntest"
    print("   ✅ clean_text fonctionne")
    
    # Test truncate_text
    long_text = "Ceci est un texte très long qui devrait être tronqué"
    truncated = truncate_text(long_text, max_length=20)
    assert len(truncated) <= 22  # 20 + "…"
    print("   ✅ truncate_text fonctionne")
    
    # Test markdown_to_html
    md = "# Titre\n\nParagraphe avec **gras** et *italique*."
    html = markdown_to_html(md, preserve_latex=False)
    assert "<h1>" in html
    assert "<strong>" in html
    assert "<em>" in html
    print("   ✅ markdown_to_html fonctionne")
    
    # Test extract_latex_formulas
    latex_text = "Formule inline: $x^2$ et display: $$\\int_0^1 f(x) dx$$"
    formulas = extract_latex_formulas(latex_text)
    assert len(formulas) == 2
    print("   ✅ extract_latex_formulas fonctionne")
    
except Exception as e:
    print(f"   ❌ Erreur dans les tests: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 6: Markdown avec LaTeX preservation dans widgets
print("\n6️⃣  Test markdown avec préservation LaTeX (widgets)...")
try:
    from src.ui.gui.widgets import markdown_to_html_with_latex
    
    md_with_latex = """
# Formule de Leibniz

La formule est:

$$
\\int_a^b f(x) dx = F(b) - F(a)
$$

Et inline: $f'(x) = \\frac{df}{dx}$

**Important** avec *italique*.
"""
    html = markdown_to_html_with_latex(md_with_latex)
    # Vérifier que les délimiteurs LaTeX sont préservés
    assert "$$" in html, "Les délimiteurs $$ doivent être présents"
    assert "$f'(x)" in html or "$f(" in html, "Le LaTeX inline doit être présent"
    assert "<strong>" in html, "Le gras doit être converti"
    assert "<em>" in html, "L'italique doit être converti"
    print("   ✅ Préservation LaTeX fonctionne (widgets)")
except Exception as e:
    print(f"   ❌ Erreur préservation LaTeX: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
print("="*60)
print("\n📝 Résumé des améliorations:")
print("   • widgets.py utilise maintenant markdown_to_html de text_processing.py")
print("   • widgets.py utilise truncate_text pour les aperçus")
print("   • rag_engine.py utilise clean_text, normalize_whitespace et truncate_text")
print("   • assistant.py utilise truncate_text et normalize_whitespace")
print("   • Préservation LaTeX améliorée avec preserve_latex=True")
print("\n🎉 Le refactoring est complet et fonctionnel!")
