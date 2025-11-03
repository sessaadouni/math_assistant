"""
Script de diagnostic pour vérifier l'extraction du PDF
"""
from langchain_community.document_loaders import PyPDFLoader
import os

PDF_PATH = "./livre_2011.pdf"

print("=" * 80)
print("🔍 DIAGNOSTIC D'EXTRACTION PDF")
print("=" * 80)

# Vérifier le fichier
if os.path.exists(PDF_PATH):
    size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
    print(f"✅ PDF: {PDF_PATH}")
    print(f"   Taille: {size_mb:.2f} MB")
else:
    print(f"❌ PDF non trouvé: {PDF_PATH}")
    exit(1)

print("\n📖 Extraction avec PyPDFLoader...")
loader = PyPDFLoader(PDF_PATH)
pages = loader.load()

print(f"✅ Pages extraites: {len(pages)}")
print(f"\n📊 Statistiques:")
print(f"   - Nombre total de pages: {len(pages)}")

# Analyser le contenu
total_chars = sum(len(p.page_content) for p in pages)
avg_chars = total_chars / len(pages) if pages else 0
print(f"   - Caractères totaux: {total_chars:,}")
print(f"   - Moyenne par page: {avg_chars:.0f} chars")

# Vérifier quelques pages
print(f"\n📄 Échantillon de pages:")
sample_indices = [0, len(pages)//4, len(pages)//2, 3*len(pages)//4, len(pages)-1]
for idx in sample_indices:
    if idx < len(pages):
        page = pages[idx]
        content_preview = page.page_content[:100].replace("\n", " ")
        print(f"\n   Page {idx+1}:")
        print(f"      Métadonnées: {page.metadata}")
        print(f"      Longueur: {len(page.page_content)} chars")
        print(f"      Aperçu: {content_preview}...")

# Vérifier les métadonnées de pages
print(f"\n🔍 Analyse des numéros de page dans les métadonnées:")
page_numbers = []
for p in pages:
    if 'page' in p.metadata:
        page_numbers.append(p.metadata['page'])

if page_numbers:
    print(f"   - Min: {min(page_numbers)}")
    print(f"   - Max: {max(page_numbers)}")
    print(f"   - Unique: {len(set(page_numbers))}")
else:
    print("   ⚠️  Aucun numéro de page dans les métadonnées")

print("\n" + "=" * 80)
