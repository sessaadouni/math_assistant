#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la normalisation des block_kind
"""

import sys
from pathlib import Path

# Ajoute le dossier parent au path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.core.rag_engine import get_engine, _norm

def test_normalization():
    """Teste la normalisation des accents"""
    
    print("=" * 80)
    print("🧪 TEST DE NORMALISATION")
    print("=" * 80)
    
    # Test normalisation de base
    test_cases = [
        ("théorème", "theoreme"),
        ("Théorème", "theoreme"),
        ("THÉORÈME", "theoreme"),
        ("définition", "definition"),
        ("Définition", "definition"),
        ("proposition", "proposition"),
        ("corollaire", "corollaire"),
    ]
    
    print("\n1️⃣ Tests de normalisation _norm():")
    all_ok = True
    for input_val, expected in test_cases:
        result = _norm(input_val)
        ok = result == expected
        all_ok &= ok
        status = "✅" if ok else "❌"
        print(f"  {status} _norm('{input_val}') = '{result}' (attendu: '{expected}')")
    
    print(f"\n{'✅ Tous les tests passent!' if all_ok else '❌ Certains tests échouent'}")
    
    return all_ok


def analyze_blocks():
    """Analyse les blocs dans la DB"""
    
    print("\n" + "=" * 80)
    print("📊 ANALYSE DES BLOCS DANS LA BASE")
    print("=" * 80)
    
    try:
        engine = get_engine()
        all_docs = engine._get_all_docs()
        
        print(f"\n📚 Total documents: {len(all_docs)}")
        
        # Statistiques par type de bloc
        block_kinds = {}
        chapters = set()
        blocks_by_chapter = {}
        
        for doc in all_docs:
            bk = doc.metadata.get("block_kind")
            ch = doc.metadata.get("chapter")
            bid = doc.metadata.get("block_id")
            
            if bk:
                block_kinds[bk] = block_kinds.get(bk, 0) + 1
            
            if ch:
                chapters.add(ch)
                if ch not in blocks_by_chapter:
                    blocks_by_chapter[ch] = []
                if bk and bid:
                    blocks_by_chapter[ch].append((bk, bid))
        
        print("\n📊 Distribution des types de blocs:")
        for bk, count in sorted(block_kinds.items(), key=lambda x: -x[1]):
            print(f"  • {bk:20s}: {count:4d} docs")
        
        print(f"\n📚 Chapitres trouvés: {len(chapters)}")
        print(f"  {sorted(chapters, key=lambda x: int(x) if str(x).isdigit() else 999)}")
        
        # Exemples de blocs par chapitre
        print("\n📋 Exemples de blocs par chapitre:")
        for ch in sorted(list(chapters)[:5], key=lambda x: int(x) if str(x).isdigit() else 999):
            blocks = blocks_by_chapter.get(ch, [])
            print(f"\n  Chapitre {ch}: {len(blocks)} blocs")
            # Affiche les 5 premiers
            for bk, bid in sorted(set(blocks))[:5]:
                print(f"    - {bk} {bid}")
            if len(blocks) > 5:
                print(f"    ... et {len(blocks) - 5} autres")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retrieval():
    """Teste le retrieval avec différents filtres"""
    
    print("\n" + "=" * 80)
    print("🔍 TEST DE RETRIEVAL AVEC FILTRES")
    print("=" * 80)
    
    try:
        engine = get_engine()
        
        # Test 1: Chapitre seul
        print("\n1️⃣ Test: chapter=3")
        retriever = engine.create_retriever(k=5, chapter="3")
        docs = retriever.invoke("base orthogonale")
        print(f"  Résultats: {len(docs)} documents")
        for i, doc in enumerate(docs[:3], 1):
            ch = doc.metadata.get("chapter")
            bk = doc.metadata.get("block_kind")
            bid = doc.metadata.get("block_id")
            print(f"  {i}. Ch.{ch} | {bk} {bid}")
        
        # Test 2: Chapitre + block_kind
        print("\n2️⃣ Test: chapter=3, block_kind=definition")
        retriever = engine.create_retriever(k=5, chapter="3", block_kind="definition")
        docs = retriever.invoke("base orthogonale")
        print(f"  Résultats: {len(docs)} documents")
        for i, doc in enumerate(docs[:3], 1):
            ch = doc.metadata.get("chapter")
            bk = doc.metadata.get("block_kind")
            bid = doc.metadata.get("block_id")
            print(f"  {i}. Ch.{ch} | {bk} {bid}")
        
        # Test 3: Chapitre + block_kind + block_id (strict)
        print("\n3️⃣ Test: chapter=3, block_kind=definition, block_id=3.7")
        retriever = engine.create_retriever(k=5, chapter="3", block_kind="definition", block_id="3.7")
        docs = retriever.invoke("base orthogonale")
        print(f"  Résultats: {len(docs)} documents")
        for i, doc in enumerate(docs[:3], 1):
            ch = doc.metadata.get("chapter")
            bk = doc.metadata.get("block_kind")
            bid = doc.metadata.get("block_id")
            print(f"  {i}. Ch.{ch} | {bk} {bid}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Démarrage des tests de normalisation et retrieval\n")
    
    # Test 1: Normalisation
    norm_ok = test_normalization()
    
    # Test 2: Analyse blocs
    analyze_ok = analyze_blocks()
    
    # Test 3: Retrieval
    retrieval_ok = test_retrieval()
    
    # Résumé
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    print(f"  {'✅' if norm_ok else '❌'} Normalisation")
    print(f"  {'✅' if analyze_ok else '❌'} Analyse blocs")
    print(f"  {'✅' if retrieval_ok else '❌'} Retrieval")
    print()
    
    sys.exit(0 if all([norm_ok, analyze_ok, retrieval_ok]) else 1)
