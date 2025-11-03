"""
Script complet pour analyser la base vectorielle et identifier les problèmes
"""

import os
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from collections import Counter

DB_DIR = "./db/chroma_db_math"
COLLECTION_NAME = "math_course"

print("=" * 80)
print("🔍 ANALYSE COMPLÈTE DE LA BASE VECTORIELLE")
print("=" * 80)

if not os.path.exists(DB_DIR):
    print(f"❌ Base vectorielle non trouvée: {DB_DIR}")
    exit(1)

# Charger la base
embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_DIR,
    embedding_function=embeddings,
)

total_docs = vector_store._collection.count()
print(f"\n📊 Total de documents: {total_docs:,}")

if total_docs == 0:
    print("⚠️  Base vide!")
    exit(0)

print(f"\n🔄 Récupération de TOUS les documents (peut prendre un moment)...")

# Récupérer TOUS les documents
all_results = vector_store._collection.get(
    limit=total_docs,
    include=["metadatas", "documents"]
)

if not all_results or not all_results.get("metadatas"):
    print("❌ Impossible de récupérer les métadonnées")
    exit(1)

metadatas = all_results["metadatas"]
documents = all_results.get("documents", [])

print(f"✅ {len(metadatas)} documents récupérés")

# Analyse complète
print("\n" + "=" * 80)
print("📈 STATISTIQUES COMPLÈTES")
print("=" * 80)

# 1. Types de contenu
types = [m.get("type", "inconnu") for m in metadatas if m]
type_counts = Counter(types)
print(f"\n📚 Distribution des types ({len(types)} docs):")
for doc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(types)) * 100
    bar = "█" * int(pct / 2)
    print(f"   {doc_type:15s}: {count:5d} ({pct:5.1f}%) {bar}")

# 2. Pages
pages = [m.get("page") for m in metadatas if m and m.get("page")]
if pages:
    unique_pages = sorted(set(pages))
    print(f"\n📄 Pages:")
    print(f"   Minimum: {min(pages)}")
    print(f"   Maximum: {max(pages)}")
    print(f"   Pages uniques: {len(unique_pages)}")
    print(f"   Pages couvertes: {unique_pages[:20]}{'...' if len(unique_pages) > 20 else ''}")
    
    # Distribution par page
    page_counts = Counter(pages)
    avg_chunks_per_page = sum(page_counts.values()) / len(page_counts)
    print(f"   Moyenne chunks/page: {avg_chunks_per_page:.1f}")

# 3. Chapitres
chapters = [m.get("chapter") for m in metadatas if m and m.get("chapter")]
if chapters:
    unique_chapters = sorted(set(chapters), key=lambda x: int(x) if x and x.isdigit() else 999)
    print(f"\n📖 Chapitres:")
    print(f"   Chapitres détectés: {len(unique_chapters)}")
    print(f"   Liste: {unique_chapters}")

# 4. Sections
sections = [m.get("section") for m in metadatas if m and m.get("section")]
if sections:
    unique_sections = sorted(set(sections))
    print(f"\n📑 Sections:")
    print(f"   Sections détectées: {len(unique_sections)}")
    print(f"   Exemples: {unique_sections[:20]}{'...' if len(unique_sections) > 20 else ''}")

# 5. Taille des documents
if documents:
    doc_lengths = [len(doc) for doc in documents if doc]
    avg_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0
    print(f"\n📏 Taille des chunks:")
    print(f"   Moyenne: {avg_length:.0f} caractères")
    print(f"   Min: {min(doc_lengths)}")
    print(f"   Max: {max(doc_lengths)}")

# 6. Chunk IDs
chunk_ids = [m.get("chunk_id") for m in metadatas if m and m.get("chunk_id") is not None]
if chunk_ids:
    print(f"\n🔢 Chunk IDs:")
    print(f"   Min ID: {min(chunk_ids)}")
    print(f"   Max ID: {max(chunk_ids)}")
    print(f"   IDs uniques: {len(set(chunk_ids))}")

print("\n" + "=" * 80)
print("🔍 PROBLÈMES POTENTIELS")
print("=" * 80)

problems = []

# Vérifier si pages < expected
if pages and max(pages) < 100:
    problems.append(f"⚠️  Seulement {max(pages)} pages détectées - le PDF devrait en avoir plus")

# Vérifier distribution
if len(type_counts) < 3:
    problems.append("⚠️  Peu de types différents détectés - classification peut-être trop stricte")

# Vérifier cohérence
if total_docs != len(metadatas):
    problems.append(f"⚠️  Incohérence: {total_docs} docs annoncés mais {len(metadatas)} métadonnées")

if problems:
    for p in problems:
        print(p)
else:
    print("✅ Aucun problème majeur détecté")

print("\n" + "=" * 80)
print("💡 RECOMMANDATIONS")
print("=" * 80)

if pages and max(pages) < 100:
    print("""
Le problème principal est que seulement quelques pages sont détectées.

Causes possibles:
1. PyPDFLoader n'arrive pas à extraire toutes les pages du PDF
2. Le PDF est protégé ou utilise un encodage spécial
3. Certaines pages sont des images sans texte extractible

Solutions:
1. Installer PyMuPDF: pip install pymupdf
2. Utiliser la version v2: python math_course_rag_v2.py
3. Vérifier le PDF avec: python diagnostic_extraction.py
4. Essayer d'autres extracteurs: pdfplumber, unstructured
""")
else:
    print("✅ La base vectorielle semble correctement construite")

print("=" * 80)
