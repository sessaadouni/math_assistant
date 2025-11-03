# -*- coding: utf-8 -*-
"""
lib/math_assistant_lib.py
Lib commune (CLI/GUI) pour l’assistant RAG de maths :
- Initialise LLM/prompt/chain
- Portée (scope), mémoire courte (pin/unpin/auto-link), query rewrite
- Retrieval + réponse
- Logging JSONL
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
import os, json, time, uuid
from rapidfuzz import fuzz

# ----- Dépendances LangChain/Ollama -----
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# ----- Votre backend RAG existant -----
from model.math_course_rag_v3_1 import (
    create_retriever, build_or_load_store, canonical_route,
    print_sources, console, RICH_OK
)

# ======================================================================
# LLM & Prompt de réponse
# ======================================================================

MODEL_NAME = os.environ.get("MATH_LLM_NAME", "deepseek-v3.1:671b-cloud")
model = OllamaLLM(model=MODEL_NAME)

template = """Tu es un assistant pédagogique en mathématiques.

[Contexte du cours]
{context}

[Question]
{question}

Règles:
- Réponds en français, clair et structuré.
- Cite les définitions/théorèmes/propositions utilisés (avec identifiant si dispo).
- Utilise du LaTeX inline si utile (ex: $\\sum_i a_i$).
- Si c'est un exercice, guide par étapes sans tout divulguer d'un coup.
- Indique les pages du cours quand disponibles (métadonnées).
Réponse:"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# ======================================================================
# Query Rewriter (optionnel)
# ======================================================================

REWRITE_ENABLED = os.environ.get("MATH_REWRITE", "1") not in {"0", "false", "False"}
REWRITE_MODEL_NAME = os.environ.get("MATH_REWRITE_LLM_NAME", "gemma3:12b").strip()
rewrite_model: Optional[OllamaLLM] = None
if REWRITE_ENABLED:
    try:
        rewrite_model = OllamaLLM(model=REWRITE_MODEL_NAME) if REWRITE_MODEL_NAME else model
    except Exception:
        REWRITE_ENABLED = False
        rewrite_model = None

REWRITE_PROMPT = ChatPromptTemplate.from_template(
    """Tu reformules des questions courtes d'étudiants en requêtes auto-suffisantes pour la recherche de contexte.
Si on te donne un CONTEXTE (chapitre, type de bloc, identifiant), intègre-le explicitement.
Garde une longueur raisonnable et des mots-clés concrets. Pas de politesse.

[DERNIÈRE QUESTION]
{last_q}

[NOUVELLE QUESTION]
{new_q}

[CONTEXTE]
{ctx}

Consigne:
- Si la nouvelle question est une relance ou dépend du contexte, écris une requête condensée qui précise le chapitre et le bloc (s’ils sont fournis).
- Sinon, renvoie simplement la nouvelle question telle quelle.
- Sors uniquement la requête réécrite (une ligne).
"""
)

def describe_meta(meta: Optional[Dict[str, Any]]) -> str:
    if not meta: return "(aucun)"
    parts = []
    if meta.get("chapter"): parts.append(f"chapitre {meta['chapter']}")
    if meta.get("block_kind") and meta.get("block_id"):
        parts.append(f"{meta['block_kind']} {meta['block_id']}")
    elif meta.get("block_kind"):
        parts.append(str(meta["block_kind"]))
    if meta.get("type"): parts.append(f"type={meta['type']}")
    return ", ".join(parts) if parts else "(aucun)"

def rewrite_query_if_needed(
    new_q: str,
    last_q: Optional[str],
    context_meta: Optional[Dict[str, Any]],
    is_followup_flag: bool
) -> str:
    if not REWRITE_ENABLED or rewrite_model is None:
        return new_q
    if not is_followup_flag and not context_meta:
        return new_q
    try:
        ctx_str = describe_meta(context_meta)
        rp = REWRITE_PROMPT | rewrite_model
        out = rp.invoke({"last_q": last_q or "(aucune)", "new_q": new_q, "ctx": ctx_str})
        rewritten = (out or "").strip()
        return rewritten or new_q
    except Exception:
        return new_q

# ======================================================================
# Portée de session (scope) & mémoire courte
# ======================================================================

SESSION_SCOPE: Dict[str, Optional[str]] = {
    "chapter": None,
    "block_kind": None,
    "block_id": None,
    "type": None,  # doc_type: exercice/méthode/théorie/cours
}

def scope_show() -> str:
    items = [f"{k}={v}" for k, v in SESSION_SCOPE.items() if v]
    return "(aucun filtre)" if not items else ", ".join(items)

def scope_set(**kwargs: Any) -> None:
    for k, v in kwargs.items():
        if k in SESSION_SCOPE:
            SESSION_SCOPE[k] = v

def scope_clear() -> None:
    for k in SESSION_SCOPE:
        SESSION_SCOPE[k] = None

def apply_scope_to_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(kwargs)
    if SESSION_SCOPE.get("chapter"):
        merged["chapter"] = SESSION_SCOPE["chapter"]
    if SESSION_SCOPE.get("block_kind"):
        merged["block_kind"] = SESSION_SCOPE["block_kind"]
    if SESSION_SCOPE.get("block_id"):
        merged["block_id"] = SESSION_SCOPE["block_id"]
    if SESSION_SCOPE.get("type"):
        merged["doc_type"] = SESSION_SCOPE["type"]
    return merged

# mémoire courte
LAST_STATE: Dict[str, Any] = {
    "last_question": None,
    "last_route": None,
    "last_top_meta": None,
    "pinned_meta": None,
}

LOG_BUFFER: List[dict] = []

def reset_state(full: bool = True) -> None:
    LAST_STATE["pinned_meta"] = None
    LAST_STATE["last_top_meta"] = None
    LAST_STATE["last_route"] = None
    LAST_STATE["last_question"] = None
    if full:
        scope_clear()

def best_context_meta() -> Optional[dict]:
    if LAST_STATE.get("pinned_meta"):
        return LAST_STATE["pinned_meta"]
    if LAST_STATE.get("last_top_meta"):
        return LAST_STATE["last_top_meta"]
    if LAST_STATE.get("last_route"):
        return {
            "chapter": LAST_STATE["last_route"].get("chapter"),
            "block_kind": LAST_STATE["last_route"].get("block_kind"),
            "block_id": LAST_STATE["last_route"].get("block_id"),
            "type": None,
        }
    return None

def meta_from_docs(docs: List[Document]) -> Optional[dict]:
    if not docs: return None
    d = docs[0]
    return {
        "chapter": d.metadata.get("chapter"),
        "block_kind": d.metadata.get("block_kind"),
        "block_id": d.metadata.get("block_id"),
        "type": d.metadata.get("type"),
        "page": d.metadata.get("page"),
    }

def is_follow_up(new_q: str, last_q: Optional[str]) -> bool:
    if not last_q: return False
    t = new_q.strip().lower()
    prefixes = (
        "et ", "ok ", "d’accord", "daccord", "peux", "peux-tu", "peux tu",
        "refais", "refaire", "reprends", "reprend", "montre", "donne", "propose",
        "fais", "fais-moi", "fais moi", "explique", "démontre", "demonstre",
        "la preuve", "la démonstration", "la demonstration", "un exemple", "un exo",
        "peux tu m'en faire", "peux tu m en faire", "peux-tu m'en faire"
    )
    pronouns = ("ça", "cela", "celle-ci", "celle ci", "celui-là", "celui la", "celle-là")
    short = len(t.split()) <= 8
    if t.startswith(prefixes) or any(p in t for p in pronouns) or short:
        return True
    return fuzz.partial_ratio(new_q, last_q) >= 65

# ======================================================================
# Retrieval + réponse
# ======================================================================

def format_context(docs: List[Document]) -> str:
    parts = []
    for d in docs:
        page = d.metadata.get("page", "?")
        block = " ".join(str(x) for x in [d.metadata.get("block_kind"), d.metadata.get("block_id")] if x).strip()
        tag  = block if block else d.metadata.get("type", "cours")
        parts.append(f"[{tag.upper()} - Page {page}]\n{d.page_content}")
    return "\n---\n".join(parts)

def compute_final_kwargs(question: str, filter_type: Optional[str], auto_link: bool) -> Tuple[Dict[str, Any], bool]:
    route = canonical_route(question)
    LAST_STATE["last_route"] = route

    chapter = block_id = block_kind = None
    if route:
        chapter    = route.get("chapter")
        block_id   = route.get("block_id")
        block_kind = route.get("block_kind")

    follow_flag = is_follow_up(question, LAST_STATE.get("last_question"))
    if auto_link and not route:
        if follow_flag:
            ctx = best_context_meta()
            if ctx:
                chapter    = chapter    or ctx.get("chapter")
                block_kind = block_kind or ctx.get("block_kind")
                block_id   = block_id   or ctx.get("block_id")
                if not filter_type and ctx.get("type"):
                    filter_type = ctx["type"]

    base_kwargs = dict(
        k=8,
        doc_type=filter_type,
        chapter=chapter,
        block_kind=block_kind,
        block_id=block_id,
    )
    final_kwargs = apply_scope_to_kwargs(base_kwargs)
    return final_kwargs, follow_flag

def retrieve_and_answer(
    question: str,
    filter_type: Optional[str] = None,
    *,
    auto_link: bool = True,
    debug: bool = False,
    auto_pin_next: bool = False
) -> Dict[str, Any]:
    """
    Retourne un dict avec:
      answer (str), docs (List[Document]), final_kwargs (dict),
      rewritten_q (str), hinted_q (str), top_meta (dict|None), follow_flag (bool)
    """
    final_kwargs, follow_flag = compute_final_kwargs(question, filter_type, auto_link)

    context_meta = {
        "chapter": final_kwargs.get("chapter"),
        "block_kind": final_kwargs.get("block_kind"),
        "block_id": final_kwargs.get("block_id"),
        "type": final_kwargs.get("doc_type"),
    }
    rewritten_q = rewrite_query_if_needed(
        new_q=question,
        last_q=LAST_STATE.get("last_question"),
        context_meta=context_meta,
        is_followup_flag=follow_flag
    )

    hard_prefix = []
    if context_meta.get("chapter"):
        hard_prefix.append(f"chapitre {context_meta['chapter']}")
    if context_meta.get("block_kind") and context_meta.get("block_id"):
        hard_prefix.append(f"{str(context_meta['block_kind']).lower()} {context_meta['block_id']}")
    if context_meta.get("type"):
        hard_prefix.append(f"type {context_meta['type']}")

    hinted_q = rewritten_q if not hard_prefix else " | ".join(hard_prefix) + " — " + rewritten_q

    t = question.lower()
    if any(w in t for w in ["énoncé", "enonce", "page", "théorème", "theoreme"]):
        extras = []
        if context_meta.get("block_id"): extras.append(f"énoncé exact {context_meta['block_id']}")
        if context_meta.get("chapter"):  extras.append(f"chapitre {context_meta['chapter']}")
        extras.append("théorème énoncé page")
        hinted_q = hinted_q + " :: " + " ".join(extras)

    retriever = create_retriever(**final_kwargs)
    docs: List[Document] = retriever.invoke(hinted_q)

    if not docs:
        answer = "Je n’ai rien trouvé dans le cours pour cette requête. Essaie de reformuler ou de préciser le chapitre/section."
        payload = {
            "answer": answer,
            "docs": [],
            "final_kwargs": final_kwargs,
            "rewritten_q": rewritten_q,
            "hinted_q": hinted_q,
            "top_meta": None,
            "follow_flag": follow_flag
        }
        LOG_BUFFER.append({"t": time.time(), "q": question, **payload})
        return payload

    # boost si block connu
    if final_kwargs.get("block_id"):
        bid = str(final_kwargs["block_id"])
        bkind = str(final_kwargs.get("block_kind") or "")
        ch = str(final_kwargs.get("chapter") or "")
        docs = sorted(
            docs,
            key=lambda d: (
                str(d.metadata.get("block_id")) == bid,
                str(d.metadata.get("block_kind","")).lower() == bkind.lower(),
                str(d.metadata.get("chapter")) == ch,
            ),
            reverse=True
        )[:8]

    print_sources(docs)
    context = format_context(docs)
    answer = chain.invoke({"context": context, "question": question})

    LAST_STATE["last_question"] = question
    top_meta = meta_from_docs(docs)
    if top_meta:
        LAST_STATE["last_top_meta"] = top_meta
        if auto_pin_next:
            LAST_STATE["pinned_meta"] = top_meta

    payload = {
        "answer": answer,
        "docs": docs,
        "final_kwargs": final_kwargs,
        "rewritten_q": rewritten_q,
        "hinted_q": hinted_q,
        "top_meta": top_meta,
        "follow_flag": follow_flag
    }
    LOG_BUFFER.append({"t": time.time(), "q": question, **payload})
    return payload

# ======================================================================
# Divers
# ======================================================================

def ensure_store_ready() -> None:
    build_or_load_store()

def new_chat_id() -> str:
    return uuid.uuid4().hex[:8]

def save_log_jsonl(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in LOG_BUFFER:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
