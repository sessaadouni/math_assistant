#!/usr/bin/env python3
"""
Diagnostic simple: comparer les différentes méthodes d'extraction PDF
"""

import os
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = "./livre_2011.pdf"

print("=" * 80)
print("🔍 DIAGNOSTIC EXTRACTION PDF")
print("=" * 80)

if not os.path.exists(PDF_PATH):
    print(f"❌ PDF non trouvé: {PDF_PATH}")
    exit(1)

size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
print(f"📁 Fichier: {PDF_PATH} ({size_mb:.2f} MB)\n")

# Test 1: PyPDFLoader
print("📖 Méthode 1: PyPDFLoader (LangChain)")
print("-" * 80)
try:
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    print(f"✅ Pages extraites: {len(pages)}")
    
    if pages:
        # Stats
        total_chars = sum(len(p.page_content) for p in pages)
        avg_chars = total_chars / len(pages)
        print(f"   Caractères totaux: {total_chars:,}")
        print(f"   Moyenne/page: {avg_chars:.0f} chars")
        
        # Échantillon
        print(f"\n   Échantillon page 1:")
        print(f"   Métadonnées: {pages[0].metadata}")
        print(f"   Longueur: {len(pages[0].page_content)} chars")
        preview = pages[0].page_content[:200].replace("\n", " ")
        print(f"   Aperçu: {preview}...")
        
        if len(pages) > 1:
            print(f"\n   Échantillon page {len(pages)//2}:")
            mid = len(pages)//2
            print(f"   Métadonnées: {pages[mid].metadata}")
            print(f"   Longueur: {len(pages[mid].page_content)} chars")
            preview = pages[mid].page_content[:200].replace("\n", " ")
            print(f"   Aperçu: {preview}...")
        
        if len(pages) > 2:
            print(f"\n   Échantillon dernière page ({len(pages)}):")
            print(f"   Métadonnées: {pages[-1].metadata}")
            print(f"   Longueur: {len(pages[-1].page_content)} chars")
            preview = pages[-1].page_content[:200].replace("\n", " ")
            print(f"   Aperçu: {preview}...")
            
except Exception as e:
    print(f"❌ Erreur: {e}")

print()

# Test 2: PyMuPDF si disponible
print("📖 Méthode 2: PyMuPDF (fitz)")
print("-" * 80)
try:
    import fitz
    doc = fitz.open(PDF_PATH)
    print(f"✅ Pages dans le PDF: {len(doc)}")
    print(f"   Métadonnées PDF: {doc.metadata}")
    
    # Tester extraction première page
    if len(doc) > 0:
        page = doc[0]
        text = page.get_text()
        print(f"\n   Page 1:")
        print(f"   Longueur: {len(text)} chars")
        preview = text[:200].replace("\n", " ")
        print(f"   Aperçu: {preview}...")
    
    doc.close()
    
except ImportError:
    print("⚠️  PyMuPDF non installé")
    print("   Installation: pip install pymupdf")
except Exception as e:
    print(f"❌ Erreur: {e}")

print()
print("=" * 80)
print("📌 RECOMMANDATIONS")
print("=" * 80)

if len(pages) < 100:
    print("⚠️  Extraction incomplète détectée!")
    print()
    print("Solutions possibles:")
    print("1. Installer PyMuPDF: pip install pymupdf")
    print("2. Vérifier que le PDF n'est pas corrompu ou protégé")
    print("3. Essayer un autre loader: pdfplumber, unstructured")
    print()
else:
    print("✅ L'extraction semble correcte")

print("=" * 80)
