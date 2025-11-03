# -*- coding: utf-8 -*-
"""
model/math_course_rag.py
RAG cours de maths — indexation hiérarchique + hybrid retrieval maison
+ routage canonique (Leibniz barycentre, etc.) + console rich + garde-fou "math only"
+ fast-path sur bloc ciblé quand disponible.
"""

from __future__ import annotations
import os
import re
import pathlib
from collections import Counter, defaultdict
from typing import List, Optional, Dict, Any, Iterable, Tuple

from dotenv import load_dotenv
load_dotenv()

# LangChain & vecteurs
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings

# Lexical retriever
from langchain_community.retrievers import BM25Retriever

# Console riche (fallback si absent)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    from rich.traceback import install as rich_traceback
    RICH_OK = True
    console = Console()
    rich_traceback(show_locals=False)
except Exception:
    RICH_OK = False
    console = None

# ==============================================================================
# Config
# ==============================================================================
PDF_PATH = pathlib.Path(os.environ.get("MATH_PDF_PATH", "./model/livre_2011.pdf")).resolve()
DB_DIR   = pathlib.Path(os.environ.get("MATH_DB_DIR", "./db/chroma_db_math_v3_1")).resolve()
COLLECTION_NAME = "math_course_v3_1"

CHUNK_SIZE = int(os.environ.get("MATH_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.environ.get("MATH_CHUNK_OVERLAP", "150"))
EMBED_MODEL = os.environ.get("EMBED_MODEL_NAME", "mxbai-embed-large:latest")

# Reranker optionnel activable/désactivable par env
USE_RERANKER = os.environ.get("MATH_USE_RERANKER", "1") not in {"0", "false", "False"}
RERANKER_MODEL = os.environ.get("MATH_RERANKER_MODEL", "BAAI/bge-reranker-base")

embeddings = OllamaEmbeddings(model=EMBED_MODEL)

# ==============================================================================
# Heuristiques de structure + désambiguïsation
# ==============================================================================
TYPE_KEYWORDS = [
    ("exercice", ["exercice", "exercices", "problème", "corrigé", "application", "entraînement", "ex."]),
    ("méthode",  ["méthode", "technique", "procédure", "comment faire", "astuce", "remarque"]),
    ("théorie",  ["théorème", "définition", "propriété", "lemme", "corollaire", "proposition"]),
    ("sommaire", ["sommaire", "table des matières", "chapitre", "index"]),
    ("exemple",  ["exemple", "illustration", "cas particulier"]),
    ("démonstration", ["démonstration", "preuve", "montrons que"]),
]

BLOCK_RE = re.compile(
    r"^(THÉORÈME|PROPOSITION|DÉFINITION|COROLLAIRE|REMARQUE|APPLICATION)\s+(\d+(?:\.\d+)*)\s*(?:[–-]\s*)?(.*)",
    re.IGNORECASE
)
SECTION_RE = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)\s+(.+)")
CHAP_RE    = re.compile(r"^\s*(?:chapitre\s+)?(\d+)[\s\.:]+([A-ZÉÈÊÂÎÔÛÇ].*)", re.IGNORECASE)
CHAP_TITLE_RE = re.compile(r"^\s*(\d+)\s+(.+)$")

# Routage — ajoute tes cas
CANON = {
    "fonction de leibniz (barycentre)": {
        "aliases": [
            "fonction de leibniz pour le barycentre",
            "fonction de leibniz barycentre", "leibniz barycentre",
            "formule de leibniz barycentre", "barycentre leibniz"
        ],
        "must_have": ["barycentre"],
        "chapter": "28",
        "block_kind": "théorème",
        "block_id": "28.7",
    },
    "formule de leibniz (dérivées)": {
        "aliases": ["formule de leibniz", "leibniz dérivée", "leibniz produit dérivée",
                    "leibniz n-ième dérivée", "formule de leibniz analyse"],
        "must_have": ["dériv"],
        "chapter": "12",
    },
}

def canonical_route(q: str) -> Optional[dict]:
    t = q.lower()
    for _, meta in CANON.items():
        if any(a in t for a in meta["aliases"]):
            if all(w in t for w in meta.get("must_have", [])):
                return meta
    return None

# ==============================================================================
# Garde-fou "math only"
# ==============================================================================
# MATH_WHITELIST_PATTERNS = [
#     r"\b(théor(è|e)me|définition|lemme|corollaire|proposition|preuve|démonstration)\b",
#     r"\b(alg(è|e)bre|analyse|g(é|e)om(é|e)trie|arithm(é|e)tique|probabilit(é|e)s?|statistiques?)\b",
#     r"\b(int(é|e)grale?s?|d(é|e)riv(é|e)e?s?|limite?s?|s(é|e)rie?s?)\b",
#     r"\b(matrice?s?|vecteur?s?|espace?s? vectoriel?s?)\b",
#     r"\b(barycentre|affine|euclidien|norme|scalaire|leibniz)\b",   # ← ajouté “leibniz”
#     r"[+\-*/=<>^]|∑|∏|√|≤|≥|≠|∈|∀|∃|→|⇒|↦|⊂|⊆|⊃|⊇|≈|≃|≅|⟂"
# ]

# def is_math_query(q: str) -> bool:
#     t = q.lower()
#     if len(t) < 3:
#         return False
#     for pat in MATH_WHITELIST_PATTERNS:
#         if re.search(pat, t):
#             return True
#     return False

# ==============================================================================
# Extraction PDF
# ==============================================================================
def load_pdf_with_pymupdf(pdf_path: str) -> List[Document]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("⚠️  PyMuPDF non installé. Installez: pip install pymupdf")
        return load_pdf_with_pypdf(pdf_path)

    _p = Panel.fit("[bold cyan]Extraction avec PyMuPDF[/]") if RICH_OK else None
    console.print(_p) if RICH_OK else print("📖 Extraction avec PyMuPDF...")
    doc = fitz.open(pdf_path)
    pages: List[Document] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append(Document(
                page_content=text,
                metadata={"page": page_num + 1, "source": str(pdf_path)}
            ))
    doc.close()
    if RICH_OK: console.print(f"✅ {len(pages)} pages extraites")
    else: print(f"✅ {len(pages)} pages extraites")
    return pages

def load_pdf_with_pypdf(pdf_path: str) -> List[Document]:
    from langchain_community.document_loaders import PyPDFLoader
    _p = Panel.fit("[bold cyan]Extraction avec PyPDFLoader[/]") if RICH_OK else None
    console.print(_p) if RICH_OK else print("📖 Extraction avec PyPDFLoader...")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    if RICH_OK: console.print(f"✅ {len(pages)} pages extraites")
    else: print(f"✅ {len(pages)} pages extraites")
    return pages

def load_pdf_smart(pdf_path: str) -> List[Document]:
    try:
        import fitz  # noqa
        return load_pdf_with_pymupdf(pdf_path)
    except ImportError:
        return load_pdf_with_pypdf(pdf_path)

# ==============================================================================
# Structuration & enrichissement
# ==============================================================================
def detect_type(text: str) -> str:
    t = text.lower()
    for label, kws in TYPE_KEYWORDS:
        if any(k in t for k in kws):
            return label
    return "cours"

def extract_structure(text: str) -> Dict[str, Any]:
    lines = [l for l in text.splitlines() if l.strip()]

    chapter = None
    section = None
    title = None

    for l in lines[:12]:
        mc = CHAP_TITLE_RE.match(l.strip())
        if mc and len(mc.group(1)) <= 3:
            chapter = mc.group(1)
            if not title:
                title = mc.group(2).strip()
            break

    if not chapter:
        for l in lines[:10]:
            m = CHAP_RE.match(l.strip())
            if m:
                chapter = m.group(1)
                title = title or m.group(2).strip()
                break

    for l in lines[:20]:
        ms = SECTION_RE.match(l.strip())
        if ms:
            section = ms.group(1)
            if not title:
                title = ms.group(2).strip()
            break

    return {"chapter": chapter, "section": section, "title": title}

def detect_block_kind_title(lines: Iterable[str]) -> Dict[str, Any]:
    for ln in list(lines)[:16]:
        m = BLOCK_RE.match(ln.strip())
        if m:
            kind, num, title = m.group(1).lower(), m.group(2), m.group(3).strip()
            return {"block_kind": kind, "block_id": num, "block_title": title or None}
    return {}

def enrich_document(doc: Document) -> Document:
    structure = extract_structure(doc.page_content)
    doc.metadata.update(structure)

    block = detect_block_kind_title(doc.page_content.splitlines())
    doc.metadata.update(block)

    doc.metadata["type"] = detect_type(doc.page_content)
    if "block_kind" in doc.metadata:
        if doc.metadata["block_kind"] in {"théorème", "proposition", "définition", "corollaire"}:
            doc.metadata["type"] = "théorie"

    MATH_SIGNS = "∫∑∏√≤≥≠∈∀∃→⇒↦⊂⊆⊃⊇≈≃≅⟂"
    doc.metadata["length"] = len(doc.page_content)
    doc.metadata["has_math"] = any(c in doc.page_content for c in MATH_SIGNS)
    return doc

def split_by_sections(pages: List[Document]) -> List[Document]:
    big_texts: List[Tuple[int, str]] = [(p.metadata.get("page", i+1), p.page_content) for i, p in enumerate(pages)]
    merged = ""
    page_map = []
    idx = 0
    for pg, txt in big_texts:
        merged += f"\n<<<PAGE {pg}>>>\n" + txt
        page_map.append((idx, pg))
        idx = len(merged)

    block_starts = [0]
    for m in re.finditer(r"\n(?:THÉORÈME|PROPOSITION|DÉFINITION|COROLLAIRE|REMARQUE|APPLICATION)\s+\d", merged, re.IGNORECASE):
        block_starts.append(m.start())
    for m in re.finditer(r"\n\d+\.\d+(?:\.\d+)?\s+", merged):
        block_starts.append(m.start())

    block_starts = sorted(set(block_starts))
    section_docs: List[Document] = []
    for i, start in enumerate(block_starts):
        end = block_starts[i+1] if i+1 < len(block_starts) else len(merged)
        chunk_txt = merged[start:end].strip()
        if not chunk_txt:
            continue

        page_matches = list(re.finditer(r"<<<PAGE (\d+)>>>", chunk_txt))
        if page_matches:
            page_no = int(page_matches[-1].group(1))
            chunk_txt = re.sub(r"<<<PAGE \d+>>>", "", chunk_txt)
        else:
            page_no = None

        d = Document(page_content=chunk_txt, metadata={"page": page_no, "source": str(PDF_PATH)})
        enrich_document(d)
        section_docs.append(d)

    return section_docs if section_docs else pages

def load_and_split(pdf_path: str) -> List[Document]:
    pages = load_pdf_smart(pdf_path)
    if RICH_OK: console.print(Panel.fit("[bold magenta]Découpage hiérarchique (sections/blocs)[/]"))
    section_docs = split_by_sections(pages)
    if RICH_OK: console.print(f"📄 Segments hiérarchiques: [bold]{len(section_docs)}[/]")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\nTHÉORÈME", "\nDÉFINITION", "\nPROPOSITION", "\nCOROLLAIRE",
            "\n\n", "\n", ". ", " ", ""
        ],
        length_function=len,
    )

    if RICH_OK: console.print(Panel.fit("[bold magenta]Découpage en chunks[/]"))
    chunks = splitter.split_documents(section_docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i
        enrich_document(c)

    if RICH_OK:
        console.print(f"✅ {len(chunks)} chunks créés")
        type_counts = Counter(c.metadata.get("block_kind", c.metadata.get("type", "?")) for c in chunks)
        tab = Table(title="Distribution des blocs (sur chunks)")
        tab.add_column("Bloc/Type"); tab.add_column("Count", justify="right")
        for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
            tab.add_row(str(k), str(v))
        console.print(tab)
    else:
        print(f"✅ {len(chunks)} chunks créés")

    return chunks

# ==============================================================================
# Store & retrievers
# ==============================================================================
def build_or_load_store(force_rebuild: bool = False) -> Chroma:
    os.makedirs(DB_DIR, exist_ok=True)
    if force_rebuild and os.path.exists(DB_DIR):
        import shutil
        if RICH_OK: console.print(Panel.fit("[bold red]Suppression de l'ancienne base[/]"))
        shutil.rmtree(DB_DIR)
        os.makedirs(DB_DIR, exist_ok=True)

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIR,
        embedding_function=embeddings,
    )

    if vector_store._collection.count() == 0:
        if RICH_OK: console.print(Panel.fit("[bold cyan]INDEXATION DU COURS DE MATHÉMATIQUES[/]"))
        docs = load_and_split(str(PDF_PATH))
        if RICH_OK: console.print(Panel.fit(f"[bold]Ajout à la base vectorielle ({len(docs)} chunks)[/]"))
        batch_size = 100
        rng = range(0, len(docs), batch_size)
        iterator = track(rng, description="Vectorisation...") if RICH_OK else rng
        for i in iterator:
            vector_store.add_documents(docs[i:i+batch_size])
        if RICH_OK: console.print(Panel.fit("[bold green]✅ Indexation terminée[/]"))
    else:
        msg = f"🔎 Base vectorielle chargée ({vector_store._collection.count()} documents)"
        console.print(msg) if RICH_OK else print(msg)

    return vector_store

def _materialize_all_docs(store: Chroma) -> List[Document]:
    results = store._collection.get(include=["metadatas", "documents"])
    docs: List[Document] = []
    for txt, meta in zip(results.get("documents", []), results.get("metadatas", [])):
        docs.append(Document(page_content=txt, metadata=meta or {}))
    return docs

# --- Reranker optionnel (CrossEncoder) ---
_CROSS = None
def _maybe_init_reranker() -> bool:
    global _CROSS
    if _CROSS is not None:
        return True
    if not USE_RERANKER:
        return False
    try:
        from sentence_transformers import CrossEncoder  # noqa
        _CROSS = CrossEncoder(RERANKER_MODEL)
        return True
    except Exception:
        _CROSS = None
        return False

class SimpleHybridRetriever:
    """
    Hybride maison BM25 + Vectoriel.
    - Fusion par score de rang.
    - Rerank cross-encoder optionnel (sentence-transformers).
    - Fast-path: si filters très précis, on précharge ces docs d’abord.
    """
    def __init__(self, store: Chroma, all_docs: List[Document],
                 k: int = 8, filters: Optional[Dict[str, Any]] = None):
        self.store = store
        self.all_docs = all_docs
        self.k = max(k, 8)
        self.filters = filters or {}
        self.use_reranker = _maybe_init_reranker()

        # --- BM25: corpus après filtrage Python ---
        bm_docs_source = self._apply_filters(self.all_docs)
        self._bm25_enabled = len(bm_docs_source) > 0
        if self._bm25_enabled:
            # passe k ici (API récente)
            self.bm25 = BM25Retriever.from_documents(bm_docs_source, k=self.k * 2)
        else:
            self.bm25 = None

        # --- Vectoriel: ne PAS passer plusieurs clés à Chroma (sinon erreur) ---
        vector_filter = None
        if self.filters:
            # On préfère ne passer qu’UNE clé (chapter si dispo), le reste se fait en Python
            if "chapter" in self.filters:
                vector_filter = {"chapter": self.filters["chapter"]}
            elif "type" in self.filters and not any(k in self.filters for k in ("block_kind", "block_id")):
                vector_filter = {"type": self.filters["type"]}
            # sinon: pas de filter côté Chroma

        kwargs = {"k": self.k * 2}
        if vector_filter:
            kwargs["filter"] = vector_filter
        self.vector = store.as_retriever(search_kwargs=kwargs)

    def _apply_filters(self, docs: List[Document]) -> List[Document]:
        if not self.filters:
            return docs
        out = []
        for d in docs:
            ok = True
            for k, v in self.filters.items():
                if d.metadata.get(k) != v:
                    ok = False; break
            if ok: out.append(d)
        return out

    def _fast_path_docs(self) -> List[Document]:
        if not self.filters:
            return []
        wanted = {}
        for k in ("chapter", "block_kind", "block_id", "type"):
            v = self.filters.get(k)
            if v is not None:
                wanted[k] = str(v)

        out = []
        for d in self.all_docs:
            ok = True
            for k, v in wanted.items():
                if str(d.metadata.get(k)) != v:
                    ok = False
                    break
            if ok:
                out.append(d)
        return out[: max(self.k, 10)]


    def invoke(self, query: str) -> List[Document]:
        fast = self._fast_path_docs()
        bm_docs = self.bm25.invoke(query) if self.bm25 else []   # <- ICI
        vec_docs = self.vector.invoke(query)

        from collections import defaultdict
        rank = defaultdict(float); idx_map = {}
        def push(list_docs, w=1.0):
            for r, d in enumerate(list_docs):
                did = id(d); idx_map[did] = d; rank[did] += w * (1.0 / (r+1))
        push(fast, 2.0)
        push(bm_docs, 1.0)
        push(vec_docs, 1.0)

        merged = sorted(idx_map.values(), key=lambda d: rank[id(d)], reverse=True)
        candidates = merged[: max(self.k * 2, 12)]

        if self.use_reranker and candidates:
            try:
                pairs = [(query, d.page_content[:2000]) for d in candidates]
                scores = _CROSS.predict(pairs)
                candidates = [d for d, s in sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)]
            except Exception:
                pass
        return candidates[: self.k]


def build_hybrid_retriever(store: Chroma, k: int = 8, filters: Optional[Dict[str, Any]] = None) -> SimpleHybridRetriever:
    all_docs = _materialize_all_docs(store)
    return SimpleHybridRetriever(store, all_docs, k=k, filters=filters)

def create_retriever(
    k: int = 8,
    doc_type: Optional[str] = None,
    chapter: Optional[str] = None,
    mmr: bool = False,
    block_kind: Optional[str] = None,
    block_id: Optional[str] = None,
    **kwargs
) -> SimpleHybridRetriever:
    store = build_or_load_store()
    filters: Dict[str, Any] = {}
    if doc_type:   filters["type"] = doc_type
    if chapter:    filters["chapter"] = chapter
    if block_kind: filters["block_kind"] = block_kind
    if block_id:   filters["block_id"] = block_id
    return build_hybrid_retriever(store, k=k, filters=filters)

# ==============================================================================
# Outils console
# ==============================================================================
def print_sources(docs: List[Document]) -> None:
    if RICH_OK:
        table = Table(title="Sources trouvées", show_lines=True)
        table.add_column("#", style="bold")
        table.add_column("Bloc", style="magenta")
        table.add_column("Chap/Sec", style="cyan")
        table.add_column("Page", justify="right")
        table.add_column("Aperçu")
        for i, d in enumerate(docs, 1):
            blk = ("{} {}".format(d.metadata.get("block_kind", "") or "", d.metadata.get("block_id", "") or "")).strip()
            chapsec = f"{d.metadata.get('chapter','?')} / {d.metadata.get('section','?')}"
            page = str(d.metadata.get("page", "?"))
            prev = (d.page_content[:120].replace("\n", " ") + "...") if d.page_content else ""
            table.add_row(str(i), blk or d.metadata.get("type", "?"), chapsec, page, prev)
        console.print(table)
    else:
        print("\n📖 Sources trouvées:")
        for i, d in enumerate(docs, 1):
            blk = ("{} {}".format(d.metadata.get("block_kind", "") or "", d.metadata.get("block_id", "") or "")).strip()
            chapsec = f"{d.metadata.get('chapter','?')} / {d.metadata.get('section','?')}"
            page = str(d.metadata.get("page", "?"))
            prev = (d.page_content[:120].replace("\n", " ") + "...") if d.page_content else ""
            print(f"  {i}. [{blk or d.metadata.get('type','?')}] Chap/Sec {chapsec} | Page {page}: {prev}")

# ==============================================================================
# Self-check
# ==============================================================================
def rag_self_check() -> str:
    lines = []
    bar = "=" * 80
    lines.append(bar)
    lines.append("🔍 RAG SELF-CHECK v3.1 - Système de cours de mathématiques")
    lines.append(bar)

    if os.path.exists(PDF_PATH):
        size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)
        lines.append(f"✅ PDF: {PDF_PATH}")
        lines.append(f"   Taille: {size_mb:.2f} MB")
    else:
        lines.append(f"❌ PDF non trouvé: {PDF_PATH}")
        return "\n".join(lines)

    if not os.path.exists(DB_DIR):
        lines.append(f"⚠️  Base vectorielle non créée")
        lines.append(f"   Lancez: python -c \"import model.math_course_rag_v3_1 as r; r.build_or_load_store()\"")
        return "\n".join(lines)

    try:
        store = build_or_load_store()
        count = store._collection.count()
        lines.append(f"✅ Base vectorielle: {DB_DIR}")
        lines.append(f"✅ Documents indexés: {count:,}")

        if count > 0:
            sample_size = min(count, 250)
            results = store._collection.get(limit=sample_size, include=["metadatas"])
            metas = results.get("metadatas", []) if results else []
            types = [m.get("type", "?") for m in metas if m]
            tc = Counter(types)
            lines.append(f"\n📊 Distribution des types (échantillon {len(types)}):")
            for k, v in sorted(tc.items(), key=lambda x: -x[1]):
                pct = (v / max(1, len(types))) * 100
                lines.append(f"   {k:15s}: {v:4d} ({pct:4.1f}%)")

            pages = [m.get("page") for m in metas if m and m.get("page")]
            if pages:
                lines.append(f"\n📄 Pages: {min(pages)} → {max(pages)} ({len(set(pages))} uniques)")

            chapters = [m.get("chapter") for m in metas if m and m.get("chapter")]
            if chapters:
                uniq = sorted(set(chapters), key=lambda x: int(x) if str(x).isdigit() else 999)
                lines.append(f"📚 Chapitres: {uniq[:12]}{'...' if len(uniq) > 12 else ''}")

            has_math = [m.get("has_math") for m in metas if m]
            mcount = sum(1 for x in has_math if x)
            lines.append(f"🔢 Contenu mathématique: {mcount}/{len(has_math)} chunks ({100*mcount/max(1,len(has_math)):.1f}%)")

            lines.append(f"\n🧪 Test de recherche:")
            retr = create_retriever(k=3)
            res = retr.invoke("théorème démonstration")
            lines.append(f"   Query: 'théorème démonstration' → {len(res)} résultats")
            if res:
                d0 = res[0]
                prev = d0.page_content[:120].replace("\n", " ")
                lines.append(f"   Top: type={d0.metadata.get('type')} page={d0.metadata.get('page')} ap={prev}...")
        lines.append("\n" + bar)
        lines.append("✅ Système opérationnel")
        lines.append(bar)
    except Exception as e:
        import traceback
        lines.append(f"\n❌ Erreur: {e}")
        lines.append(traceback.format_exc())

    return "\n".join(lines)

if __name__ == "__main__":
    if RICH_OK:
        console.print(Panel.fit("[bold]Self-check[/]"))
        console.print(rag_self_check())
    else:
        print(rag_self_check())
