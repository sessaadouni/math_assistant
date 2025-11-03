# -*- coding: utf-8 -*-
"""
src/core/rag_engine.py
Moteur RAG refactorisé avec architecture modulaire
"""

from __future__ import annotations
import re
from typing import List, Optional, Dict, Any, Tuple
from collections import Counter, defaultdict
import os
import unicodedata

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever

from .config import rag_config
from src.utils import clean_text, normalize_whitespace, truncate_text

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import track
    RICH_OK = True
    console = Console()
except Exception:
    RICH_OK = False
    console = None


# ---------------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    """Normalise accents/casse/espaces pour comparer des métadonnées ou filtres."""
    s = "" if s is None else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.strip().lower().split())


# ---------------------------------------------------------------------------
# Extraction / enrichissement structurel
# ---------------------------------------------------------------------------

class DocumentStructureExtractor:
    """Extraction et enrichissement de la structure des documents"""

    BLOCK_RE = re.compile(
        r"^(THEOREME|THÉORÈME|PROPOSITION|DEFINITION|DÉFINITION|COROLLAIRE|REMARQUE|APPLICATION)\s+(\d+(?:\.\d+)*)\s*(?:[–-]\s*)?(.*)",
        re.IGNORECASE
    )
    SECTION_RE = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)\s+(.+)")
    CHAP_RE = re.compile(r"^\s*(?:chapitre\s+)?(\d+)[\s\.:]+([A-ZÉÈÊÂÎÔÛÇ].*)", re.IGNORECASE)
    CHAP_TITLE_RE = re.compile(r"^\s*(\d+)\s+(.+)$")

    TYPE_KEYWORDS = [
        ("exercice", ["exercice", "problème", "corrigé", "application", "ex."]),
        ("méthode", ["méthode", "technique", "procédure", "astuce", "remarque"]),
        ("théorie", ["théorème", "définition", "propriété", "lemme", "corollaire"]),
        ("sommaire", ["sommaire", "table des matières", "index"]),
        ("exemple", ["exemple", "illustration", "cas particulier"]),
        ("démonstration", ["démonstration", "preuve", "montrons que"]),
    ]

    @classmethod
    def detect_type(cls, text: str) -> str:
        t = text.lower()
        for label, kws in cls.TYPE_KEYWORDS:
            if any(k in t for k in kws):
                return label
        return "cours"

    @classmethod
    def extract_structure(cls, text: str) -> Dict[str, Any]:
        lines = [l for l in text.splitlines() if l.strip()]
        chapter = section = title = None

        # Détection chapitre
        for l in lines[:12]:
            mc = cls.CHAP_TITLE_RE.match(l.strip())
            if mc and len(mc.group(1)) <= 3:
                chapter = mc.group(1)
                if not title:
                    title = mc.group(2).strip()
                break

        if not chapter:
            for l in lines[:10]:
                m = cls.CHAP_RE.match(l.strip())
                if m:
                    chapter = m.group(1)
                    title = title or m.group(2).strip()
                    break

        # Détection section
        for l in lines[:20]:
            ms = cls.SECTION_RE.match(l.strip())
            if ms:
                section = ms.group(1)
                if not title:
                    title = ms.group(2).strip()
                break

        return {"chapter": chapter, "section": section, "title": title}

    @classmethod
    def detect_block(cls, lines: List[str]) -> Dict[str, Any]:
        for ln in list(lines)[:16]:
            m = cls.BLOCK_RE.match(_norm(ln))
            if m:
                kind, num, title = m.group(1).lower(), m.group(2), (m.group(3) or "").strip()
                return {"block_kind": kind, "block_id": num, "block_title": title or None}
        return {}

    @classmethod
    def enrich_document(cls, doc: Document) -> Document:
        doc.page_content = clean_text(doc.page_content)

        structure = cls.extract_structure(doc.page_content)
        doc.metadata.update(structure)

        block = cls.detect_block(doc.page_content.splitlines())
        doc.metadata.update(block)

        doc.metadata["type"] = cls.detect_type(doc.page_content)
        if "block_kind" in doc.metadata:
            if doc.metadata.get("block_kind") in {"théorème", "proposition", "définition", "corollaire"}:
                doc.metadata["type"] = "théorie"
        
        # Normalisation block_kind sans accents pour uniformité
        for k in ("type","chapter","block_kind","block_id"):
            if k in doc.metadata and doc.metadata[k] is not None:
                doc.metadata[k] = _norm(doc.metadata[k])

        MATH_SIGNS = "=+-*/^×·⋅÷±∓≠≤≥≪≫≡≢≈≃≅∝∫∑∏∮√∂∇∆∞∈∉∀∃∄∅∪∩⊂⊆⊃⊇⊄⊅⊕⊗→⇒⇔↦←⇐↔∘⟂∥∠∴∵°′″ℕℤℚℝℂℙαβγδεζηθικλμνξπρστφχψωΓΔΘΛΞΠΣΦΨΩ"
        doc.metadata["length"] = len(doc.page_content)
        doc.metadata["has_math"] = any(c in doc.page_content for c in MATH_SIGNS)

        return doc


# ---------------------------------------------------------------------------
# Chargement PDF
# ---------------------------------------------------------------------------

class PDFLoader:
    """Chargement intelligent de PDF avec fallback"""

    @staticmethod
    def load_with_pymupdf(pdf_path: str) -> List[Document]:
        try:
            import fitz
        except ImportError:
            return PDFLoader.load_with_pypdf(pdf_path)

        if RICH_OK:
            console.print(Panel.fit("[bold cyan]Extraction avec PyMuPDF[/]"))
        else:
            print("📖 Extraction avec PyMuPDF...")

        doc = fitz.open(pdf_path)
        pages: List[Document] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text() or ""
            pages.append(Document(
                page_content=text,
                metadata={"page": page_num + 1, "source": str(pdf_path), "is_empty": not text.strip()}
            ))

        doc.close()

        if RICH_OK:
            console.print(f"✅ {len(pages)} pages extraites")
        else:
            print(f"✅ {len(pages)} pages extraites")

        return pages

    @staticmethod
    def load_with_pypdf(pdf_path: str) -> List[Document]:
        from langchain_community.document_loaders import PyPDFLoader

        if RICH_OK:
            console.print(Panel.fit("[bold cyan]Extraction avec PyPDFLoader[/]"))
        else:
            print("📖 Extraction avec PyPDFLoader...")

        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        if RICH_OK:
            console.print(f"✅ {len(pages)} pages extraites")
        else:
            print(f"✅ {len(pages)} pages extraites")

        return pages

    @classmethod
    def load(cls, pdf_path: str) -> List[Document]:
        try:
            import fitz  # noqa
            return cls.load_with_pymupdf(pdf_path)
        except ImportError:
            return cls.load_with_pypdf(pdf_path)


# ---------------------------------------------------------------------------
# Découpage hiérarchique
# ---------------------------------------------------------------------------

class DocumentSplitter:
    """Découpage hiérarchique et intelligent des documents"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\nTHÉORÈME", "\nDÉFINITION", "\nPROPOSITION", "\nCOROLLAIRE",
                "\n\n", "\n", ". ", " ", ""
            ],
            length_function=len,
        )

    def split_by_sections(self, pages: List[Document]) -> List[Document]:
        big_texts: List[Tuple[int, str]] = [
            (p.metadata.get("page", i+1), p.page_content)
            for i, p in enumerate(pages)
        ]

        merged = ""
        for pg, txt in big_texts:
            merged += f"\n<<<PAGE {pg}>>>\n" + txt

        block_starts = [0]
        for m in re.finditer(
            r"\n(?:THÉORÈME|PROPOSITION|DÉFINITION|COROLLAIRE|REMARQUE|APPLICATION)\s+\d",
            merged, re.IGNORECASE
        ):
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

            page_hits = [int(m.group(1)) for m in re.finditer(r"<<<PAGE (\d+)>>>", chunk_txt)]
            if page_hits:
                page_start, page_end = min(page_hits), max(page_hits)
                chunk_txt = re.sub(r"<<<PAGE \d+>>>", "", chunk_txt)
            else:
                page_start = page_end = None

            d = Document(
                page_content=chunk_txt,
                metadata={
                    "page": page_end,                    # compat
                    "page_start": page_start,
                    "page_end": page_end,
                    "source": str(rag_config.pdf_path)
                }
            )
            DocumentStructureExtractor.enrich_document(d)
            section_docs.append(d)

        return section_docs if section_docs else pages

    def split_documents(self, pages: List[Document]) -> List[Document]:
        if RICH_OK:
            console.print(Panel.fit("[bold magenta]Découpage hiérarchique (sections/blocs)[/]"))

        section_docs = self.split_by_sections(pages)

        if RICH_OK:
            console.print(f"📄 Segments hiérarchiques: [bold]{len(section_docs)}[/]")
            console.print(Panel.fit("[bold magenta]Découpage en chunks[/]"))

        chunks = self.splitter.split_documents(section_docs)

        for i, c in enumerate(chunks):
            c.metadata["chunk_id"] = i
            DocumentStructureExtractor.enrich_document(c)

        if RICH_OK:
            console.print(f"✅ {len(chunks)} chunks créés")
            self._print_distribution(chunks)
        else:
            print(f"✅ {len(chunks)} chunks créés")

        return chunks

    @staticmethod
    def _print_distribution(chunks: List[Document]):
        type_counts = Counter(
            c.metadata.get("block_kind", c.metadata.get("type", "?"))
            for c in chunks
        )

        tab = Table(title="Distribution des blocs")
        tab.add_column("Bloc/Type")
        tab.add_column("Count", justify="right")

        for k, v in sorted(type_counts.items(), key=lambda x: -x[1]):
            tab.add_row(str(k), str(v))

        console.print(tab)


# ---------------------------------------------------------------------------
# Retriever hybride (BM25 + Vectoriel + Reranker)
# ---------------------------------------------------------------------------

def _map_reranker_name(name: str) -> str:
    """
    Accepte des alias 'ollama-like' et retourne un ID HuggingFace valide pour SentenceTransformers.
    """
    n = (name or "").strip()
    # Tolérer des suffixes ':latest'
    n = n.split(":")[0]
    # Mappings fréquents
    if n.endswith("bge-reranker-v2-m3") or "bge-reranker-v2-m3" in n:
        return "BAAI/bge-reranker-v2-m3"
    if "jina-reranker" in n:
        return "jinaai/jina-reranker-v2-base-multilingual"
    if n.lower() in {"bge-small-en-v1.5", "bge-base-en-v1.5"}:
        return f"BAAI/{n}"
    # Par défaut, on renvoie tel quel (si déjà HF)
    return n


class HybridRetriever:
    """Retriever hybride BM25 + Vectoriel avec reranking"""

    def __init__(
        self,
        store: Optional[Chroma],
        all_docs: List[Document],
        k: int = 8,
        filters: Optional[Dict[str, Any]] = None,
        use_reranker: bool = True
    ):
        self.store = store
        self.all_docs = all_docs
        self.k = max(k, 8)
        self.filters = filters or {}
        self.use_reranker = use_reranker and rag_config.use_reranker

        # ------------------------- BM25 (optionnel) -------------------------
        bm25_needed = (self.store is None) or bool(getattr(rag_config, "use_bm25_with_vector", False))
        if bm25_needed and self.all_docs:
            bm_docs_source = self._apply_filters(self.all_docs)
            bm_docs_norm = [Document(page_content=strip_accents(d.page_content), metadata=d.metadata) for d in bm_docs_source]
            self._bm25_enabled = len(bm_docs_norm) > 0
            self.bm25 = BM25Retriever.from_documents(bm_docs_norm, k=self.k * 2) if self._bm25_enabled else None

        # ------------------------- Vector (Chroma) --------------------------
        # ------------------------- Vector (Chroma) - FILTRE SOUPLE --------------------------
        # Stratégie: filtre minimal côté vecteur (chapitre OU type OU block_kind)
        # puis post-tri strict sur block_id pour éviter rappel trop faible
        
        def _as_str(v): return str(v) if v is not None else None

        vector_filter = None
        if self.store is not None and self.filters:
            # Priorité: chapitre > type > block_kind
            # On N'INCLUT PAS block_id dans le where (trop restrictif)
            if self.filters.get("chapter"):
                vector_filter = {"chapter": {"$eq": _as_str(self.filters["chapter"])}}
            elif self.filters.get("type"):
                vector_filter = {"type": {"$eq": _norm(self.filters["type"])}}
            elif self.filters.get("block_kind"):
                # block_kind seul (normalisé sans accents)
                vector_filter = {"block_kind": {"$eq": _norm(self.filters["block_kind"])}}

        kwargs = {"k": self.k * 2}
        if vector_filter:
            # IMPORTANT: passer 'filter', pas 'where', sinon conflit interne
            kwargs["filter"] = vector_filter

        self.vector = self.store.as_retriever(search_kwargs=kwargs) if self.store is not None else None
        self._vector_where_debug = vector_filter  # utile pour affichage debug/CLI

        # ------------------------- Reranker ---------------------------------
        self._cross = None
        self._rr_maxlen = 256
        self._rr_batch = 16
        if self.use_reranker:
            self._init_reranker()



    def _init_reranker(self):
        try:
            from sentence_transformers import CrossEncoder  # noqa
            hf_id = _map_reranker_name(rag_config.reranker_model)

            # Device/batch/seq_len contrôlables par env pour s'adapter au PC
            device = os.getenv("RERANKER_DEVICE", None)      # "cpu" | "cuda" | "mps" | None
            self._cross = CrossEncoder(hf_id, device=device)

            self._rr_maxlen = int(os.getenv("RERANK_MAX_LEN", "256"))
            self._rr_batch  = int(os.getenv("RERANK_BATCH", "16"))
        except Exception:
            self._cross = None
            self.use_reranker = False

    def _apply_filters(self, docs: List[Document]) -> List[Document]:
        if not self.filters:
            return docs

        out = []
        # Comparaison insensible aux accents/majuscules
        wanted = {k: _norm(v) for k, v in self.filters.items() if v is not None}
        for d in docs:
            ok = True
            for k, v in wanted.items():
                if _norm(d.metadata.get(k)) != v:
                    ok = False
                    break
            if ok:
                out.append(d)
        return out

    def _fast_path_docs(self) -> List[Document]:
        if not self.filters:
            return []

        wanted = {}
        for k in ("chapter", "block_kind", "block_id", "type"):
            v = self.filters.get(k)
            if v is not None:
                wanted[k] = _norm(v)

        out = []
        for d in self.all_docs:
            ok = True
            for k, v in wanted.items():
                if _norm(d.metadata.get(k)) != v:
                    ok = False
                    break
            if ok:
                out.append(d)

        return out[: max(self.k, 10)]

    def invoke(self, query: str) -> List[Document]:
        fast = self._fast_path_docs() if self.all_docs else []
        bm_docs = self.bm25.invoke(query) if self.bm25 else []
        vec_docs = self.vector.invoke(query) if self.vector else []

        # Fusion
        rank = defaultdict(float)
        idx_map = {}

        def push(list_docs, w=1.0, k0=60):
            for r, d in enumerate(list_docs):
                did = id(d)
                idx_map[did] = d
                rank[did] += w * (1.0 / (k0 + r + 1))

        push(fast, 2.0)
        push(bm_docs, 1.0)
        push(vec_docs, 1.0)

        merged = sorted(idx_map.values(), key=lambda d: rank[id(d)], reverse=True)
        candidates = merged[: max(self.k * 2, 12)]

        # Reranking CrossEncoder
        if self.use_reranker and self._cross and candidates:
            try:
                # Tronquage raisonnable (texte) et batching pour limiter la charge
                def _approx_clip(s, ntok):  # ~4 chars/token
                    return s[: ntok * 4]
                pairs = [(query, _approx_clip(d.page_content, self._rr_maxlen)) for d in candidates]
                scores = []
                for i in range(0, len(pairs), self._rr_batch):
                    sub = pairs[i:i + self._rr_batch]
                    scores.extend(self._cross.predict(sub, show_progress_bar=False))
                candidates = [d for d, s in sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)]
            except Exception:
                pass

        return candidates[: self.k]


# ---------------------------------------------------------------------------
# RAG Engine
# ---------------------------------------------------------------------------

class RAGEngine:
    """Moteur RAG principal"""

    def __init__(self):
        self.config = rag_config
        self._store: Optional[Chroma] = None
        self._all_docs: Optional[List[Document]] = None
        self._bm25_only: bool = False  # si embeddings indisponibles

    # --- Embeddings (lazy) ---------------------------------------------------

    def _init_embeddings(self) -> Optional[OllamaEmbeddings]:
        """
        Essaie d'initialiser l'embedding primaire, puis l'alternative.
        Retourne None si impossible → mode BM25-only.
        """
        base_kwargs = {}
        if self.config.ollama_host:
            base_kwargs["base_url"] = self.config.ollama_host
        if self.config.ollama_api_key:
            base_kwargs["api_key"] = self.config.ollama_api_key

        tried = []

        for name in [self.config.embed_model_primary, self.config.embed_model_alt]:
            if not name:
                continue
            try:
                emb = OllamaEmbeddings(model=name, **base_kwargs)
                # Ping simple pour forcer l'initialisation (optionnel / robuste)
                _ = emb.embed_query("ping")
                if RICH_OK:
                    console.print(f"✅ Embeddings: [bold]{name}[/]")
                else:
                    print(f"✅ Embeddings: {name}")
                return emb
            except Exception as e:
                tried.append((name, str(e)))
                continue

        if RICH_OK:
            console.print(Panel.fit("[bold red]Aucun model d'embedding disponible → BM25-only[/]"))
            for n, err in tried:
                console.print(f"  - {n}: {err[:120]}…")
        else:
            print("❌ Embeddings indisponibles → BM25-only")

        return None

    @property
    def store(self) -> Optional[Chroma]:
        """Lazy loading du store (peut être None en BM25-only)."""
        if self._store is None and not self._bm25_only:
            self._store = self.build_or_load_store()
        return self._store

    # --- Construction / chargement ------------------------------------------

    def build_or_load_store(self, force_rebuild: bool = False) -> Optional[Chroma]:
        """Construction ou chargement du vector store (ou bascule BM25-only)."""
        self.config.db_dir.mkdir(parents=True, exist_ok=True)

        # Embeddings
        embeddings = self._init_embeddings()
        if embeddings is None:
            # BM25-only : on prépare _all_docs et on sort
            pages = PDFLoader.load(str(self.config.pdf_path))
            splitter = DocumentSplitter(
                chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
            )
            self._all_docs = splitter.split_documents(pages)
            self._bm25_only = True
            return None

        # Vector store
        if force_rebuild and self.config.db_dir.exists():
            import shutil
            if RICH_OK:
                console.print(Panel.fit("[bold red]Suppression de l'ancienne base[/]"))
            shutil.rmtree(self.config.db_dir)
            self.config.db_dir.mkdir(parents=True, exist_ok=True)

        vector_store = Chroma(
            collection_name=self.config.collection_name,
            persist_directory=str(self.config.db_dir),
            embedding_function=embeddings,
        )

        if vector_store._collection.count() == 0:
            if RICH_OK:
                console.print(Panel.fit("[bold cyan]INDEXATION DU COURS DE MATHÉMATIQUES[/]"))

            docs = self._load_and_split()

            if RICH_OK:
                console.print(Panel.fit(f"[bold]Ajout à la base vectorielle ({len(docs)} chunks)[/]"))

            batch_size = 100
            rng = range(0, len(docs), batch_size)
            iterator = track(rng, description="Vectorisation...") if RICH_OK else rng

            for i in iterator:
                vector_store.add_documents(docs[i:i+batch_size])

            if RICH_OK:
                console.print(Panel.fit("[bold green]✅ Indexation terminée[/]"))
        else:
            msg = f"🔎 Base vectorielle chargée ({vector_store._collection.count()} documents)"
            console.print(msg) if RICH_OK else print(msg)

        return vector_store

    # --- Utils internes ------------------------------------------------------

    def _load_and_split(self) -> List[Document]:
        pages = PDFLoader.load(str(self.config.pdf_path))
        splitter = DocumentSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )
        return splitter.split_documents(pages)

    def _get_all_docs(self) -> List[Document]:
        """
        Récupère tous les documents (depuis le store si dispo, sinon depuis le split BM25-only).
        """
        if self._all_docs is not None:
            return self._all_docs

        if self._bm25_only:
            # déjà construit dans build_or_load_store
            return self._all_docs or []

        # Vector store → on recharge depuis la collection
        store = self.store
        assert store is not None, "Store attendu ici"
        results = store._collection.get(include=["metadatas", "documents"])
        self._all_docs = []
        for txt, meta in zip(results.get("documents", []), results.get("metadatas", [])):
            self._all_docs.append(Document(page_content=txt, metadata=meta or {}))
        return self._all_docs

    # --- API publique --------------------------------------------------------

    def create_retriever(
        self,
        k: int = 8,
        doc_type: Optional[str] = None,
        chapter: Optional[str] = None,
        block_kind: Optional[str] = None,
        block_id: Optional[str] = None,
        **kwargs
    ) -> HybridRetriever:
        """Crée un retriever avec filtres (supporte BM25-only)."""
        # Blindage au cas où "k" fuit dans kwargs depuis un dict
        if "k" in kwargs:
            kwargs.pop("k", None)

        filters: Dict[str, Any] = {}
        if doc_type:
            filters["type"] = doc_type
        if chapter:
            filters["chapter"] = chapter
        if block_kind:
            filters["block_kind"] = block_kind
        if block_id:
            filters["block_id"] = block_id

        # BM25 requis ? (ex: pas d'embeddings OU volonté explicite via config)
        bm25_needed = (self.store is None) or bool(getattr(rag_config, "use_bm25_with_vector", False))
        all_docs: List[Document] = self._get_all_docs() if bm25_needed else []

        return HybridRetriever(
            store=self.store,           # peut être None (BM25-only)
            all_docs=all_docs,          # [] si on coupe BM25 pour perf
            k=k,
            filters=filters,
            use_reranker=self.config.use_reranker
        )

    def self_check(self) -> str:
        lines = []
        bar = "=" * 80
        lines.append(bar)
        lines.append("🔍 RAG SELF-CHECK v3.1 - Système de cours de mathématiques")
        lines.append(bar)

        if self.config.pdf_path.exists():
            size_mb = self.config.pdf_path.stat().st_size / (1024 * 1024)
            lines.append(f"✅ PDF: {self.config.pdf_path}")
            lines.append(f"   Taille: {size_mb:.2f} MB")
        else:
            lines.append(f"❌ PDF non trouvé: {self.config.pdf_path}")
            return "\n".join(lines)

        if not self.config.db_dir.exists():
            lines.append(f"⚠️  Base vectorielle non créée")
            lines.append(f"   Lancez: python -m src.core.rag_engine")
            return "\n".join(lines)

        try:
            store = self.store
            if store is None:
                lines.append("⚠️ Mode BM25-only (embeddings indisponibles)")
                count = len(self._get_all_docs())
                lines.append(f"✅ Chunks (BM25): {count:,}")
            else:
                count = store._collection.count()
                lines.append(f"✅ Base vectorielle: {self.config.db_dir}")
                lines.append(f"✅ Documents indexés: {count:,}")

            sample_size = min(count, 250) if store is not None else min(len(self._get_all_docs()), 250)
            metas = []
            if store is not None:
                results = store._collection.get(limit=sample_size, include=["metadatas"])
                metas = results.get("metadatas", []) if results else []
            else:
                metas = [d.metadata for d in self._get_all_docs()[:sample_size]]

            types = [m.get("type", "?") for m in metas if m]
            tc = Counter(types)
            lines.append(f"\n📊 Distribution des types (échantillon {len(types)}):")
            for k_, v in sorted(tc.items(), key=lambda x: -x[1]):
                pct = (v / max(1, len(types))) * 100
                lines.append(f"   {k_:15s}: {v:4d} ({pct:4.1f}%)")

            pages = [m.get("page") for m in metas if m and m.get("page")]
            if pages:
                lines.append(f"\n📄 Pages: {min(pages)} → {max(pages)} ({len(set(pages))} uniques)")

            chapters = [m.get("chapter") for m in metas if m and m.get("chapter")]
            if chapters:
                uniq = sorted(set(chapters), key=lambda x: int(x) if str(x).isdigit() else 999)
                lines.append(f"📚 Chapitres: {uniq[:12]}{'...' if len(uniq) > 12 else ''}")

            lines.append(f"\n🧪 Test de recherche:")
            retr = self.create_retriever(k=3)
            res = retr.invoke("théorème démonstration")
            lines.append(f"   Query: 'théorème démonstration' → {len(res)} résultats")

            if res:
                d0 = res[0]
                prev = truncate_text(d0.page_content.replace("\n", " "), max_length=120)
                lines.append(f"   Top: type={d0.metadata.get('type')} page={d0.metadata.get('page')} ap={prev}")

            lines.append("\n" + bar)
            lines.append("✅ Système opérationnel")
            lines.append(bar)

        except Exception as e:
            import traceback
            lines.append(f"\n❌ Erreur: {e}")
            lines.append(traceback.format_exc())

        return "\n".join(lines)


# Instance globale
_engine = None

def get_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine


# Fonctions de compatibilité
def build_or_load_store(force_rebuild: bool = False) -> Optional[Chroma]:
    return get_engine().build_or_load_store(force_rebuild)

def create_retriever(**kwargs) -> HybridRetriever:
    return get_engine().create_retriever(**kwargs)

def rag_self_check() -> str:
    return get_engine().self_check()


if __name__ == "__main__":
    if RICH_OK:
        console.print(Panel.fit("[bold]Self-check[/]"))
    print(rag_self_check())
