#!/usr/bin/env python3
"""
Test de diagnostic pour /cours qui ne génère pas de contenu
"""

import sys
sys.path.insert(0, "/home/se/test_ollama_rag/server")

print("=" * 80)
print("DIAGNOSTIC: Problème /cours retourne 'À la prochaine fois !'")
print("=" * 80)

# Test 1: Vérifier le prompt course_build
print("\n1️⃣ Vérification du prompt course_build")
print("-" * 80)
try:
    from src.prompts.registry import PromptRegistry
    registry = PromptRegistry()
    
    course_build = registry.get("course_build")
    template = course_build.template.messages[0].prompt.template
    
    print(f"✅ Prompt course_build chargé")
    print(f"   Longueur: {len(template)} caractères")
    print(f"   Variables: {course_build.template.input_variables}")
    
    # Vérifier que le template contient bien du contenu structuré
    if "Structure OBLIGATOIRE" in template:
        print("✅ Template contient 'Structure OBLIGATOIRE'")
    else:
        print("❌ Template ne contient pas 'Structure OBLIGATOIRE'")
    
    if "double piste" in template.lower():
        print("✅ Template mentionne 'double piste'")
    else:
        print("❌ Template ne mentionne pas 'double piste'")
        
except Exception as e:
    print(f"❌ Erreur lors du chargement du prompt: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Simuler un appel run_task
print("\n2️⃣ Simulation d'un appel run_task('course_build')")
print("-" * 80)
try:
    from src.assistant import get_assistant
    
    assistant = get_assistant()
    
    print("✅ Assistant chargé")
    print(f"   LLM: {assistant.engine.config.llm_model}")
    print(f"   Backend: {assistant.engine.config.runtime_default_mode}")
    
    # Test avec une notion simple
    print("\n   Test: Génération cours sur 'dérivées'")
    payload = assistant.run_task("course_build", "dérivées", level="L3", debug=True)
    
    answer = payload.get("answer", "")
    print(f"\n   Réponse reçue:")
    print(f"   - Longueur: {len(answer)} caractères")
    print(f"   - Premières 200 car: {answer[:200]}")
    print(f"   - Dernières 100 car: {answer[-100:]}")
    
    if len(answer) < 500:
        print(f"\n❌ PROBLÈME: Réponse trop courte ({len(answer)} car)")
        print(f"   Contenu complet:\n{answer}")
    else:
        print(f"✅ Réponse semble correcte ({len(answer)} caractères)")
    
    # Vérifier la structure attendue
    sections_attendues = ["Introduction", "Définitions", "Propriétés", "Méthodes", "Exemples"]
    sections_trouvees = [s for s in sections_attendues if s in answer]
    print(f"\n   Sections trouvées: {sections_trouvees}")
    
    if len(sections_trouvees) < 3:
        print(f"❌ Peu de sections structurées trouvées")
    else:
        print(f"✅ Structure correcte détectée")
    
    # Afficher le debug si disponible
    if "debug" in payload:
        dbg = payload["debug"]
        print(f"\n   Debug info:")
        print(f"   - Task: {dbg.get('task')}")
        print(f"   - Runtime: {dbg.get('runtime')}")
        print(f"   - Rewritten query: {dbg.get('rewritten_q')}")
        
except Exception as e:
    print(f"❌ Erreur lors de l'appel run_task: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIN DU DIAGNOSTIC")
print("=" * 80)
