# -*- coding: utf-8 -*-
"""
Routeur décisionnel pour l'assistant Maths (IA → IA).
- Décide: "rag_first" | "llm_first" | "llm_only" | "rag_to_llm"
- Détecte les intentions liées au livre/hors-programme ET les tâches pédagogiques:
  qa | course_build | course_explain | course_summary | sheet_create | sheet_review
  formula | theorem | proof | exercise_gen | exam_gen | solve | tutor
  exercise_correct | exam_correct | qcm | kholle
- Construit un "context passport" riche (scores, motifs, raisons).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
import uuid, re, time, unicodedata
from rapidfuzz import fuzz

from langchain_core.documents import Document

from ..core.rag_engine import get_engine
from ..core.config import rag_config
from src.utils import normalize_whitespace, normalize_query_for_retrieval

# -------------------------
# Helpers
# -------------------------
def _strip_accents(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

def _norm(s: str) -> str:
    s = _strip_accents(s or "")
    s = s.lower()
    return " ".join(s.split())

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def _regex_hit(patterns: Tuple[str, ...], s: str) -> bool:
    """Vrai si au moins un pattern regex matche la chaîne normalisée."""
    return any(re.search(p, s) for p in patterns)

# -------------------------
# Regex/keywords (ASCII, car normalisé)
# -------------------------

# --- Hors programme / extension ---
OUT_OF_SYLLABUS_KW = (
    r"\bhors(\s|-)?programmes?\b",
    r"\benhors\b.*\bprogrammes?\b",
    r"\ben\s+dehors\s+du\s+programme\b",
    r"\bextra(\s|-)?programmes?\b",
    r"\b(out|off)\s+syllabus\b",
    r"\bau(\s|-)?del[àa]\b",
    r"\bau(\s|-)?del[àa]\s+du\s+cours\b",
    r"\bapprofondissements?\b",
    r"\bextension\s+du\s+cours\b",
    r"\bsuite\s+du\s+cours\b",
    r"\bniveau\s+(avanc[ée]|\+|sup[ée]rieur)\b",
    r"\bpreuve\s+alternative\b",
    r"\bpreuve\s+(hors(\s|-)?programme|non\s+au\s+programme)\b",
    r"\bnon\s+au\s+programme\b",
)

BOOK_KW = (
    r"\blivre\b", r"\bmanuel\b", r"\bouvrage\b", r"\bpdf\b",
    r"\bchapitre[s]?\b", r"\bsection[s]?\b", r"\bpage[s]?\b",
    r"\benonce[s]?\b", r"\btheoreme[s]?\b", r"\bdefinition[s]?\b",
    r"\bproposition[s]?\b", r"\bcorollaire[s]?\b",
    r"\bexercice[s]?\b", r"\bsommaire\b", r"\btable\s+des\s+matieres\b",
)

# --- Signal "ça parle de maths"
MATH_KW = (
    r"\bderiv[ee]e?s?\b", r"\bintegrale?s?\b", r"\blimite?s?\b",
    r"\bserie?s?\b", r"\bsuite?s?\b", r"\bprobabilit[ee]s?\b",
    r"\bmatrice[s]?\b", r"\bdeterminant\b", r"\bvaleurs?\s*propres?\b",
    r"\btheoreme[s]?\b", r"\bdefinition[s]?\b", r"\bcorollaire[s]?\b", r"\blemme[s]?\b",
    r"\bfonction[s]?\b", r"\bcontinuite\b", r"\bconvergence\b",
    r"\bgradient\b", r"\bvectoriel(le)?\b", r"\banal(?:yse|ytique)\b",
    r"\b(d[ée]riv[ée]s?|int[ée]grales?|limites?)\b",
    r"\bmatric(?:e|es)\b|\bendomorphisme\b|\bpolyn[oô]me\b",
    r"[=+\-*/^×·⋅÷±∓]",  # Opérateurs arithmétiques de base
    r"[=≠≤≥≪≫≡≢≈≃≅∝]",  # Relations et équivalences
    r"[∫∑∏∮√∂∇∆∞]",  # Opérateurs calcul/analyse
    r"[∈∉∀∃∄∅∪∩⊂⊆⊃⊇⊄⊅⊕⊗]",  # Ensembles et logique
    r"[→⇒⇔↦←⇐↔∘]",  # Flèches et composition
    r"[⟂∥∠∴∵°′″]",  # Géométrie
    r"[ℕℤℚℝℂℙ]",  # Ensembles de nombres
    r"[αβγδεζηθικλμνξπρστφχψω]",  # Lettres grecques minuscules
    r"[ΓΔΘΛΞΠΣΦΨΩ]",  # Lettres grecques majuscules
)

# --- Intents → task (priorité décroissante) ---
INTENT_PATTERNS: List[Tuple[str, Tuple[str, ...]]] = [
    ("qcm", (
        r"\bqcm\b",
        r"\bquiz{1,2}\b",
        r"\bmcq\b",
        r"\b(vrai|faux)\b",
        r"\bchoix\s+multiple[s]?\b",
        r"\bquestions?\s+[àa]\s+choix\b",
        r"\btest\b",
    )),
    ("kholle", (
        r"\bkh[ôo]lle\b",
        r"\bcolle\b",
        r"\boral(?:\s+court)?\b",
        r"\binterro\s+orale\b",
    )),
    ("exam_gen", (
        r"\b(examen|partiel|concours|[ée]preuve)\b",
        r"\bsujet\s+(d['e]\s*)?(examen|partiel|concours)\b",
        r"\bdevoir\s+surveill[ée]\b",
        r"\bD\.?S\.?\b",
        r"\bbar[èe]me\b",
        r"\bnotation\b",
    )),
    ("exercise_gen", (
        r"\b(g[ée]n[ée]r(?:e|ez|er))\b.*\b(exos?|exercices?|probl[èe]mes?)\b",
        r"\b(cr[ée]e?|compose|fabrique|propose)\b.*\b(exos?|exercices?)\b",
        r"\b(exos?|exercices?)\s+originaux\b",
        r"\bentrainement\b|\bentraînement\b",
    )),
    ("solve", (
        r"\br[ée]souds?\b|\br[ée]soudre\b",
        r"\bsolution\b.*\b(exo|exercice|probl[èe]me)\b",
        r"\b(calcul(e|er|ez)|d[ée]termine[rz]?|trouve[rz]?|r[ée]solve[rz]?)\b",
        r"\bint[ée]gr(e|er|ez)\b|\bd[ée]riv(e|er|ez)\b|\blimite\b",
        r"\b(diagonalise[rz]?|r[ée]duis[ez]?|factorise[rz]?)\b",
        r"\b(r[ée]soudre|solution)\s+(ce|cet|cette)\b",
    )),
    ("tutor", (
        r"\baide\s*-\s?moi\b.*\bpas\s*[àa]\s*pas\b",
        r"\baide\b.*\bpas\s*[àa]\s*pas\b",
        r"\bguid[ea]\b|\bguidage\b|\baccompagnement\b",
        r"\bindices?\b|\bpistes?\b|\bsuggestions?\b",
        r"\b(ne|n['’])\s*me\s*(donne|donnes)\s*pas\s*(la|de)\s*(r[ée]ponse|solution)\b",
        r"\bsans\s*(donner|divulguer)\s*(la|de)\s*(r[ée]ponse|solution)\b",
        r"\bjuste\s*des\s*indices\b",
        r"\bpose[-\s]*moi\s*des\s*questions\b|\bm[’']interroger\b",
        r"\b(m[ée]thode|approche)\s+socratique\b|\bsocratic\b",
        r"\bpas\s*la\s*solution\b",
        r"\bplan\s+d['e]\s*attaque\b|\b[ée]tapes?\s+cl[ée]s?\b",
    )),
    ("exercise_correct", (
        r"\bcorrige\b.*\b(exo|exercice|probl[èe]me)\b",
        r"\bfeedback\b.*\b(exo|exercice)\b",
        r"\b(analy[s|z]e|[ée]value)\b.*\b(exo|exercice)\b",
    )),
    ("exam_correct", (
        r"\bcorrige\b.*\b(examen|[ée]preuve|partiel|concours|D\.?S\.?)\b",
        r"\b(note|notation)\b.*\b(/?\s*20|sur\s*20)\b",
        r"\bm[ée]tris\b.*\bbar[èe]me\b|\bbar[èe]mise\b",
    )),
    ("course_summary", (
        r"\br[ée]sum[ée]\b",
        r"\bsynth[èe]se\b",
        r"\br[ée]cap(itulatif)?\b|\ben\s+bref\b|\baper[çc]u\b",
    )),
    ("sheet_create", (
        r"\bfiche[s]?\b",
        r"\bfiche\s+de\s+r[ée]vision\b",
        r"\baide-?m[ée]moire\b|\bm[ée]mo\b|\bcheat\s*sheet\b",
        r"\bfiche\s+synth[èe]se\b",
    )),
    ("sheet_review", (
        r"\b(v[ée]rifie|relis|am[ée]liore|critique|audit)\b.*\bfiche\b",
        r"\breview\b.*\bfiche\b",
        r"\b[ée]value\b.*\bfiche\b",
    )),
    ("course_build", (
        r"\b(fais|construis|r[ée]dige|[ée]cris)\b.*\bcours\b",
        r"\bcours\s+complet\b|\bmini-?cours\b|\ble[çc]on\b|\bchapitre\s+complet\b",
        r"\bplan\s+de\s+cours\b",
    )),
    ("course_explain", (
        r"\bm['’]explique\b|\bexplique\b.*\b(cours|notion|chapitre)\b",
        r"\brends?\s*(cela|ceci|[çc]a)?\s*(intuitif|clair)\b",
        r"\bELI5\b|\bexplique\s+simplement\b",
        r"\b(p[ée]dagogie|p[ée]dagogique)\b",
    )),
    ("formula", (
        r"\bformule[s]?\b|\bformulaire\b",
        r"\b[ée]quation[s]?\b",
        r"\bidentit[ée]s?\b|\bd[ée]veloppements?\b|\brelation[s]?\b",
        r"\bloi[s]?\b",
    )),
    ("theorem", (
        r"\bth[ée]or[èe]me[s]?\b",
        r"\bpropri[ée]t[ée]s?\b|\bcorollaire[s]?\b|\blemme[s]?\b|\baxiome[s]?\b|\bprincipe[s]?\b",
    )),
    ("proof", (
        r"\bpreuve[s]?\b|\bd[ée]monstration[s]?\b",
        r"\b(d[ée]montre|prouve|montre|justifie|[ée]tablis?)\s+que\b",
        r"\bargumente\b|\braisonne\b",
    )),
    ("qa", (r".*",)),
]

# -------------------------
# Dataclass
# -------------------------
@dataclass
class RouterDecision:
    decision: str                 # rag_first | llm_first | llm_only | rag_to_llm
    rag_conf: float               # 0..1
    reason: str
    task: str                     # task key pour tasks.get_prompt()
    filters: Dict[str, Any]
    passport: Dict[str, Any]

# -------------------------
# Intent helpers
# -------------------------
def _intent_from_text(q_norm: str) -> Tuple[str, Dict[str, float]]:
    """Score chaque intent; retourne (best_task, scores)."""
    scores: Dict[str, float] = {}
    order = [t for t, _ in INTENT_PATTERNS]
    for task, pats in INTENT_PATTERNS:
        raw = sum(1.0 for p in pats if re.search(p, q_norm))
        if raw == 0 and task != "qa":
            try:
                sim = max(fuzz.partial_ratio(q_norm, p.replace("\\b", "")) for p in pats) / 100.0
            except ValueError:
                sim = 0.0
        else:
            sim = 0.0
        scores[task] = raw + 0.5 * sim
    best = max(scores.items(), key=lambda kv: (kv[1], -order.index(kv[0])))[0]
    return best, scores

def _book_intent(q_norm: str) -> Optional[str]:
    """Intent spécial livre/hors-programme."""
    has_book = _regex_hit(BOOK_KW, q_norm)
    has_out  = _regex_hit(OUT_OF_SYLLABUS_KW, q_norm)
    if has_book and re.search(r"\b(exo|exercice|exercices|exos)\b", q_norm):
        return "book_exercises"
    if has_out and re.search(r"\b(preuve|demonstration)\b", q_norm):
        return "book_demo"
    if has_book or has_out:
        return "course_extension"
    return None

# -------------------------
# RAG signal
# -------------------------
def _quick_rag_signal(query: str, filters: Dict[str, Any]) -> Tuple[float, float, List[Document], Dict[str, Any]]:
    """
    Aperçu RAG (rapide).
    Renvoie sim_fuzzy (0..1), struct_bonus (0..0.2), docs, stats.
    stats contient: {k, hits, sim_max, struct_hits, latency_ms, bm25_only, use_reranker, use_bm25_with_vector}
    """
    engine = get_engine()
    filt_cnt = sum(1 for k in ("chapter","block_kind","block_id","type","doc_type") if filters.get(k))
    k = 5 + (0 if filt_cnt >= 2 else 3)

    # Normaliser LaTeX → Unicode pour meilleur retrieval
    query_normalized = normalize_query_for_retrieval(query)

    t0 = time.time()
    try:
        # robustesse inter-versions: tenter top_k puis k
        try:
            retr = engine.create_retriever(top_k=k, **filters)
        except TypeError:
            retr = engine.create_retriever(k=k, **filters)
        docs = retr.invoke(query_normalized)
    except Exception as e:
        dt = int((time.time() - t0) * 1000)
        return 0.0, 0.0, [], {
            "k": k, "hits": 0, "sim_max": 0.0, "struct_hits": 0,
            "latency_ms": dt, "error": str(e),
            "bm25_only": getattr(engine, "_bm25_only", False),
            "use_reranker": bool(getattr(engine.config, "use_reranker", False)),
            "use_bm25_with_vector": bool(getattr(engine.config, "use_bm25_with_vector", False)),
        }

    dt = int((time.time() - t0) * 1000)
    if not docs:
        return 0.0, 0.0, [], {
            "k": k, "hits": 0, "sim_max": 0.0, "struct_hits": 0,
            "latency_ms": dt,
            "bm25_only": getattr(engine, "_bm25_only", False),
            "use_reranker": bool(getattr(engine.config, "use_reranker", False)),
            "use_bm25_with_vector": bool(getattr(engine.config, "use_bm25_with_vector", False)),
        }

    sims = []
    for d in docs:
        snippet = normalize_whitespace(d.page_content or "")[:700]
        p = fuzz.partial_ratio(query, snippet) / 100.0
        t = fuzz.token_sort_ratio(query, snippet) / 100.0
        sims.append(0.6 * p + 0.4 * t)
    sim_max = max(sims) if sims else 0.0

    # bonus structurel si filtres concordent
    hits = 0
    for d in docs:
        if filters.get("chapter") and str(d.metadata.get("chapter")) == str(filters["chapter"]): hits += 1
        if filters.get("block_kind") and str(d.metadata.get("block_kind")).lower() == str(filters["block_kind"]).lower(): hits += 1
        if filters.get("block_id") and str(d.metadata.get("block_id")) == str(filters["block_id"]): hits += 1
    struct_bonus = 0.2 if hits >= 2 else (0.1 if hits == 1 else 0.0)

    stats = {
        "k": k,
        "hits": len(docs),
        "sim_max": sim_max,
        "struct_hits": hits,
        "latency_ms": dt,
        "bm25_only": getattr(engine, "_bm25_only", False),
        "use_reranker": bool(getattr(engine.config, "use_reranker", False)),
        "use_bm25_with_vector": bool(getattr(engine.config, "use_bm25_with_vector", False)),
    }
    return sim_max, struct_bonus, docs, stats

def _looks_like_math(q_norm: str) -> bool:
    return _regex_hit(MATH_KW, q_norm)

def _threshold(name: str, default: float) -> float:
    return float(getattr(rag_config, name, default))

# -------------------------
# Passport builder
# -------------------------
def build_passport(
    chat_id: str,
    raw_q: str,
    rewritten_q: str,
    filters: Dict[str, Any],
    decision: str,
    rag_conf: float,
    task: str,
    *,
    intent_scores: Dict[str, float],
    rag_stats: Dict[str, Any],
    reason: str,
    matched_special: Optional[str],
) -> Dict[str, Any]:
    return {
        "chat_id": chat_id,
        "turn_id": uuid.uuid4().hex[:8],
        "user_query_raw": raw_q,
        "user_query_rewritten": rewritten_q,
        "filters": {k: v for k, v in filters.items() if v},
        "routing": {
            "decision": decision,
            "rag_conf": round(float(rag_conf), 3),
            "thresholds": {
                "rag_first": _threshold("router_threshold_rag_first", 0.55),
                "llm_first": _threshold("router_threshold_llm_first", 0.35),
            },
            "weights": {"sim": 0.65, "struct": 0.20, "kw": 0.075, "pin": 0.075},
            "rag_stats": rag_stats,
            "reason": reason,
            "matched_special": matched_special,
        },
        "task": task,
        "intent_scores": {k: round(v, 3) for k, v in intent_scores.items()},
        "safety": {"math_only": True},
        "ts": int(time.time()),
    }

# -------------------------
# Core
# -------------------------
# (imports & helpers identiques)
# ...

def decide_route(
    *,
    chat_id: str,
    raw_q: str,
    rewritten_q: str,
    filters: Dict[str, Any],
    pinned_bias: bool = False,
    last_decision: Optional[str] = None,
) -> RouterDecision:
    q_norm  = _norm(raw_q)
    rew_norm= _norm(rewritten_q or raw_q)

    task_main, scores = _intent_from_text(q_norm)
    special_task = _book_intent(q_norm)
    task = special_task or task_main

    sim, struct_bonus, _docs, rag_stats = _quick_rag_signal(rew_norm, filters)

    # --- Signaux discrets (0/1) pour kw/pin ; synergy pin ~ +0.025 (par défaut)
    kw_signal = 1.0 if _looks_like_math(q_norm) else 0.0
    pin_signal = 0.0
    if pinned_bias:
        pin_signal = 1.0
        if last_decision in {"rag_first", "rag_to_llm"} and rag_config.router_w_pin > 0:
            # conserver l'esprit de +0.025 : on convertit en "gain relatif" sur le poids pin
            pin_signal += (0.025 / rag_config.router_w_pin)

    # --- Combinaison pondérée (poids renormalisés côté config)
    base = (
        rag_config.router_w_sim    * float(sim) +
        rag_config.router_w_struct * float(struct_bonus) +
        rag_config.router_w_kw     * float(kw_signal) +
        rag_config.router_w_pin    * float(pin_signal)
    )

    # --- Pénalités si contexte faible
    weak_ctx = (rag_stats.get("hits", 0) < 3) or (rag_stats.get("sim_max", 0.0) < 0.25)
    if weak_ctx:
        base -= rag_config.router_weak_penalty
    rag_conf = _clamp(base)
    if weak_ctx and (filters.get("chapter") or filters.get("block_id") or filters.get("block_kind")):
        rag_conf = _clamp(rag_conf - rag_config.router_weak_penalty_focus)

    t_rag = _threshold("router_threshold_rag_first", 0.55)
    t_llm = _threshold("router_threshold_llm_first", 0.35)

    if task in {"book_exercises", "book_demo", "course_extension"}:
        decision = "rag_to_llm"
        reason = "intent livre/hors programme détecté"
    else:
        if rag_conf >= t_rag and not weak_ctx:
            decision, reason = "rag_first", "signal RAG fort"
        elif rag_conf >= t_llm:
            decision, reason = "llm_first", "signal RAG moyen"
        else:
            decision, reason = "llm_only", "signal RAG faible"

    passport = build_passport(
        chat_id, raw_q, rewritten_q or raw_q, filters, decision, rag_conf, task,
        intent_scores=scores, rag_stats={
            **rag_stats,
            "weights": {
                "sim": rag_config.router_w_sim,
                "struct": rag_config.router_w_struct,
                "kw": rag_config.router_w_kw,
                "pin": rag_config.router_w_pin,
            },
            "signals": {
                "sim": float(sim),
                "struct": float(struct_bonus),
                "kw_signal": float(kw_signal),
                "pin_signal": float(pin_signal),
                "weak_ctx": bool(weak_ctx),
            },
            "penalties": {
                "weak_penalty": rag_config.router_weak_penalty,
                "weak_penalty_focus": rag_config.router_weak_penalty_focus,
            },
        },
        reason=reason, matched_special=special_task
    )

    return RouterDecision(
        decision=decision,
        rag_conf=rag_conf,
        reason=reason,
        task=task,
        filters=filters,
        passport=passport,
    )
