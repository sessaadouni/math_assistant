# -*- coding: utf-8 -*-
"""
Logique métier de l'assistant mathématique (indépendante de l'UI).
- Orchestration avec routeur : rag_first / llm_first / llm_only / rag_to_llm
- Réécriture de requête contextuelle
- Mémoire de session (scope, pin, route override, last_top_meta)
- Fallback LLM (cloud → local) & base_url Ollama
- Runtime switchable: local | cloud | hybrid
- Debug trace détaillée (prompts, modèles, temps, stats RAG) + export ./logs/debug/
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, Tuple
import uuid, time, json, os
from rapidfuzz import fuzz

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from ..core.rag_engine import get_engine
from ..core.config import rag_config, ui_config
from .prompts import PROF_PROMPT
from .tasks import get_prompt
from src.utils import truncate_text, normalize_whitespace, normalize_query_for_retrieval
from src.utils.ollama import ensure_model_or_exit as ensure_model

# rich (optionnel)
try:
    from rich.console import Console
    from rich.table import Table
    RICH_OK = True
    console = Console()
except Exception:
    RICH_OK = False
    console = None


# --- Helpers ----------------------------------------------------------------

def _ollama_kwargs() -> Dict[str, Any]:
    kw = {}
    if rag_config.ollama_host:
        kw["base_url"] = rag_config.ollama_host
    if rag_config.ollama_api_key:
        kw["api_key"] = rag_config.ollama_api_key
    return kw


def _make_llm(model_name: str) -> OllamaLLM:
    return OllamaLLM(model=model_name, **_ollama_kwargs())


def _now_ms() -> int:
    return int(time.time() * 1000)


# --- Query Rewriter ---------------------------------------------------------

class QueryRewriter:
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
- Si la nouvelle question est une relance ou dépend du contexte, écris une requête condensée qui précise le chapitre et le bloc (s'ils sont fournis).
- Sinon, renvoie simplement la nouvelle question telle quelle.
- Sors uniquement la requête réécrite (une ligne).
"""
    )

    def __init__(self):
        self.enabled = rag_config.enable_rewrite
        self.model_name = rag_config.rewrite_model or rag_config.llm_model
        self.model = None
        if self.enabled:
            try:
                ensure_model(rag_config.ollama_host, self.model_name, rag_config.ollama_api_key)
                self.model = _make_llm(self.model_name)
            except SystemExit:
                self.enabled = False
                self.model = None
            except Exception:
                self.enabled = False
                self.model = None

    @staticmethod
    def describe_meta(meta: Optional[Dict[str, Any]]) -> str:
        if not meta:
            return "(aucun)"
        parts = []
        if meta.get("chapter"): parts.append(f"chapitre {meta['chapter']}")
        if meta.get("block_kind") and meta.get("block_id"):
            parts.append(f"{meta['block_kind']} {meta['block_id']}")
        elif meta.get("block_kind"):
            parts.append(str(meta["block_kind"]))
        if meta.get("type"): parts.append(f"type={meta['type']}")
        return ", ".join(parts) if parts else "(aucun)"

    def rewrite(
        self,
        new_q: str,
        last_q: Optional[str],
        context_meta: Optional[Dict[str, Any]],
        is_followup: bool,
        dbg: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.enabled or self.model is None:
            if dbg is not None:
                dbg["rewriter"] = {"enabled": False, "model": None, "output": new_q}
            return new_q
        if not is_followup and not context_meta:
            if dbg is not None:
                dbg["rewriter"] = {"enabled": True, "model": self.model_name, "output": new_q, "skipped": "no followup & no ctx"}
            return new_q
        try:
            ctx_str = self.describe_meta(context_meta)
            chain = self.REWRITE_PROMPT | self.model
            t0 = _now_ms()
            out = chain.invoke({"last_q": last_q or "(aucune)", "new_q": new_q, "ctx": ctx_str})
            dt = _now_ms() - t0
            rew = (out or "").strip() or new_q
            if dbg is not None:
                # on essaie d’obtenir un aperçu du prompt (optionnel)
                preview = None
                try:
                    preview = self.REWRITE_PROMPT.format(last_q=last_q or "(aucune)", new_q=new_q, ctx=ctx_str)
                except Exception:
                    pass
                dbg["rewriter"] = {
                    "enabled": True,
                    "model": self.model_name,
                    "input": {"last_q": last_q, "new_q": new_q, "ctx": ctx_str},
                    "prompt_preview": (preview[:1000] + " …") if isinstance(preview, str) and len(preview) > 1000 else preview,
                    "latency_ms": dt,
                    "output": rew,
                }
            return rew
        except Exception as e:
            if dbg is not None:
                dbg["rewriter"] = {"enabled": True, "model": self.model_name, "error": str(e), "output": new_q}
            return new_q


# --- Mémoire de session -----------------------------------------------------

class SessionMemory:
    def __init__(self):
        self.chat_id: str = uuid.uuid4().hex[:8]
        self.scope: Dict[str, Optional[str]] = {
            "chapter": None, "block_kind": None, "block_id": None, "type": None
        }
        self.state: Dict[str, Any] = {
            "last_question": None,
            "last_route": None,
            "last_top_meta": None,
            "pinned_meta": None,
            "last_decision": None,
            "route_override": None,  # "auto" | "rag" | "llm" | "hybrid"
        }
        self.log_buffer: List[dict] = []
        self.logs_enabled: bool = True

    def scope_show(self) -> str:
        items = [f"{k}={v}" for k, v in self.scope.items() if v]
        return "(aucun filtre)" if not items else ", ".join(items)

    def scope_set(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.scope:
                self.scope[k] = v

    def scope_clear(self):
        for k in self.scope:
            self.scope[k] = None

    def apply_scope(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(kwargs)
        if self.scope.get("chapter"): merged["chapter"] = self.scope["chapter"]
        if self.scope.get("block_kind"): merged["block_kind"] = self.scope["block_kind"]
        if self.scope.get("block_id"): merged["block_id"] = self.scope["block_id"]
        if self.scope.get("type"): merged["doc_type"] = self.scope["type"]
        return merged

    def reset(self, full: bool = True):
        self.state.update({
            "pinned_meta": None, "last_top_meta": None,
            "last_route": None, "last_question": None
        })
        if full:
            self.scope_clear()

    def start_new_session(self, *, reset_scope: bool = True, preserve_logs: bool = True):
        self.chat_id = uuid.uuid4().hex[:8]
        self.state.update({
            "last_question": None,
            "last_route": None,
            "last_top_meta": None,
            "pinned_meta": None,
            "last_decision": None,
        })
        if reset_scope:
            self.scope_clear()
        if not preserve_logs:
            self.log_buffer = []

    def enable_logs(self, enabled: bool = True):
        self.logs_enabled = enabled

    def add_log(self, entry: dict):
        if not self.logs_enabled:
            return
        entry["t"] = time.time()
        self.log_buffer.append(entry)

    @staticmethod
    def is_follow_up(new_q: str, last_q: Optional[str]) -> bool:
        if not last_q: return False
        t = new_q.strip().lower()
        prefixes = ("et ", "ok ", "peux", "refais", "reprends", "montre", "donne", "propose", "fais", "explique", "démonstre")
        pronouns = ("ça", "cela", "celle-ci", "celui-là", "celle-là")
        short = len(t.split()) <= 8
        if t.startswith(prefixes) or any(p in t for p in pronouns) or short:
            return True
        return fuzz.partial_ratio(new_q, last_q) >= 65

    def best_context_meta(self) -> Optional[dict]:
        if self.state.get("pinned_meta"): return self.state["pinned_meta"]
        if self.state.get("last_top_meta"): return self.state["last_top_meta"]
        if self.state.get("last_route"):
            r = self.state["last_route"]
            return {
                "chapter": r.get("chapter"),
                "block_kind": r.get("block_kind"),
                "block_id": r.get("block_id"),
                "type": None
            }
        return None

    def save_log(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            for row in self.log_buffer:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # override helpers
    def set_route_override(self, mode: Optional[str]):
        if mode in {None, "auto", "rag", "llm", "hybrid"}:
            self.state["route_override"] = mode or None

    def get_route_override(self) -> Optional[str]:
        return self.state.get("route_override")


# --- Routeur ---------------------------------------------------------------

from .router import decide_route  # gardé tel quel


# --- Assistant principal ----------------------------------------------------

class MathAssistant:
    def __init__(self):
        # Vérif modèles (primary + fallback optionnel)
        ensure_model(rag_config.ollama_host, rag_config.llm_model, rag_config.ollama_api_key)
        if rag_config.llm_local_fallback and rag_config.llm_local_fallback != rag_config.llm_model:
            try:
                ensure_model(rag_config.ollama_host, rag_config.llm_local_fallback, rag_config.ollama_api_key)
            except SystemExit:
                pass

        if rag_config.rewrite_model:
            try:
                ensure_model(rag_config.ollama_host, rag_config.rewrite_model, rag_config.ollama_api_key)
            except SystemExit:
                pass

        self.engine = get_engine()

        # Deux LLMs (primary → fallback)
        self.llm_primary = _make_llm(rag_config.llm_model)
        self.llm_fallback = _make_llm(rag_config.llm_local_fallback) if rag_config.llm_local_fallback else None

        # Prompts
        self.prof_prompt = PROF_PROMPT

        # Rewriter
        self.rewriter = QueryRewriter()

        # Mémoire
        self.memory = SessionMemory()

    # === Runtime controls ====================================================

    def set_route_override(self, mode: Optional[str]):
        """Override routeur (auto|rag|llm|hybrid)."""
        self.memory.set_route_override(mode)

    def set_runtime_mode(self, mode: str) -> Dict[str, Any]:
        """
        Bascule runtime: 'local' | 'cloud' | 'hybrid'
        Reconfigure hosts & modèles + rewriter (sans rebâtir la DB).
        """
        mode = (mode or "").lower().strip()
        if mode not in {"local", "cloud", "hybrid"}:
            raise ValueError("Mode invalide. Utilise: local | cloud | hybrid")

        # Applique la même logique que __post_init__ pour les dérivés
        if mode == "local":
            rag_config.ollama_host = rag_config.ollama_host_local
            rag_config.llm_model = rag_config.llm_model_local
            rag_config.llm_local_fallback = None
            rag_config.rewrite_model = rag_config.llm_rewriter_local if rag_config.use_rewriter else None
        elif mode == "cloud":
            if not rag_config.ollama_host_cloud:
                raise ValueError("Mode 'cloud' demandé mais OLLAMA_CLOUD_HOST non défini.")
            rag_config.ollama_host = rag_config.ollama_host_cloud
            rag_config.llm_model = rag_config.llm_model_cloud
            rag_config.llm_local_fallback = rag_config.llm_model_local
            rag_config.rewrite_model = rag_config.llm_rewriter_cloud if rag_config.use_rewriter else None
        else:  # hybrid
            rag_config.ollama_host = rag_config.ollama_host_cloud or rag_config.ollama_host_local
            rag_config.llm_model = rag_config.llm_model_cloud if rag_config.ollama_host_cloud else rag_config.llm_model_local
            rag_config.llm_local_fallback = rag_config.llm_model_local if rag_config.llm_model != rag_config.llm_model_local else None
            rag_config.rewrite_model = (rag_config.llm_rewriter_cloud or rag_config.llm_rewriter_local) if rag_config.use_rewriter else None

        # Recrée les clients
        ensure_model(rag_config.ollama_host, rag_config.llm_model, rag_config.ollama_api_key)
        self.llm_primary = _make_llm(rag_config.llm_model)
        self.llm_fallback = _make_llm(rag_config.llm_local_fallback) if rag_config.llm_local_fallback else None

        # Rewriter
        self.rewriter = QueryRewriter()

        return {
            "runtime": mode,
            "host": rag_config.ollama_host,
            "llm_primary": rag_config.llm_model,
            "llm_fallback": rag_config.llm_local_fallback,
            "rewriter_model": rag_config.rewrite_model,
        }

    def active_models(self) -> Dict[str, Any]:
        """Expose les modèles actifs (pour debug/UI)."""
        return {
            "host": rag_config.ollama_host,
            "runtime_default": getattr(rag_config, "runtime_default_mode", "hybrid"),
            "llm_primary": rag_config.llm_model,
            "llm_fallback": rag_config.llm_local_fallback,
            "rewriter_enabled": bool(rag_config.enable_rewrite),
            "rewriter_model": rag_config.rewrite_model,
        }

    # --- Invocation robuste (primary → fallback) ----------------------------

    def _invoke_with_fallback(
        self,
        prompt_tpl: ChatPromptTemplate,
        vars: Dict[str, Any],
        *,
        dbg: Optional[Dict[str, Any]] = None,
        step: str = "invoke"
    ) -> str:
        # Option: collecte un aperçu du prompt
        prompt_preview = None
        try:
            # ChatPromptTemplate: format(...) renvoie str dans langchain-core >=0.3
            prompt_preview = prompt_tpl.format(**vars)
        except Exception:
            try:
                # fallback: messages → string
                msgs = prompt_tpl.format_messages(**vars)
                prompt_preview = "\n".join(getattr(m, "content", str(m)) for m in msgs)
            except Exception:
                prompt_preview = None

        # primary
        model_used = getattr(self.llm_primary, "model", "primary")
        t0 = _now_ms()
        try:
            chain = (prompt_tpl | self.llm_primary)
            out = chain.invoke(vars)
            dt = _now_ms() - t0
            if dbg is not None:
                dbg.setdefault("llm_calls", []).append({
                    "step": step,
                    "model": model_used,
                    "fallback": False,
                    "latency_ms": dt,
                    "prompt_preview": (prompt_preview[:2000] + " …") if isinstance(prompt_preview, str) and len(prompt_preview) > 2000 else prompt_preview,
                    "vars_keys": list(vars.keys()),
                })
            return out
        except Exception as e_primary:
            if self.llm_fallback is None:
                if dbg is not None:
                    dbg.setdefault("llm_calls", []).append({
                        "step": step,
                        "model": model_used,
                        "fallback": False,
                        "error": str(e_primary),
                        "prompt_preview": None,
                        "vars_keys": list(vars.keys()),
                    })
                raise
            # fallback
            t1 = _now_ms()
            try:
                chain_fb = (prompt_tpl | self.llm_fallback)
                out_fb = chain_fb.invoke(vars)
                dt_fb = _now_ms() - t1
                if dbg is not None:
                    dbg.setdefault("llm_calls", []).append({
                        "step": step,
                        "model": getattr(self.llm_fallback, "model", "fallback"),
                        "fallback": True,
                        "latency_ms": dt_fb,
                        "prompt_preview": (prompt_preview[:2000] + " …") if isinstance(prompt_preview, str) and len(prompt_preview) > 2000 else prompt_preview,
                        "vars_keys": list(vars.keys()),
                        "primary_error": str(e_primary)[:500],
                    })
                return out_fb
            except Exception as e_fb:
                if dbg is not None:
                    dbg.setdefault("llm_calls", []).append({
                        "step": step,
                        "model": getattr(self.llm_fallback, "model", "fallback"),
                        "fallback": True,
                        "error": str(e_fb),
                        "primary_error": str(e_primary)[:500],
                        "prompt_preview": None,
                        "vars_keys": list(vars.keys()),
                    })
                # on remonte l'exception primaire pour diagnostic
                raise e_primary

    def _invoke_prof(self, *, context: str, question: str, dbg: Optional[Dict[str, Any]] = None) -> str:
        vars = {"context": context, "question": question}
        return self._invoke_with_fallback(self.prof_prompt, vars, dbg=dbg, step="prof_prompt")

    # -- Affichage sources (CLI éventuel) --
    @staticmethod
    def _print_sources(docs: List[Document]):
        if RICH_OK:
            table = Table(title="Sources trouvées", show_lines=True)
            table.add_column("#", style="bold")
            table.add_column("Bloc", style="magenta")
            table.add_column("Chap/Sec", style="cyan")
            table.add_column("Page", justify="right")
            table.add_column("Aperçu")
            for i, d in enumerate(docs, 1):
                blk = (f"{d.metadata.get('block_kind','') or ''} {d.metadata.get('block_id','') or ''}").strip()
                chapsec = f"{d.metadata.get('chapter','?')} / {d.metadata.get('section','?')}"
                page = str(d.metadata.get("page", "?"))
                prev = truncate_text((d.page_content or "").replace("\n", " "), max_length=120)
                table.add_row(str(i), blk or d.metadata.get("type", "?"), chapsec, page, prev)
            console.print(table)

    # -- Mise en forme contexte pour les prompts --
    @staticmethod
    def _format_context(docs: List[Document]) -> str:
        parts = []
        for d in docs:
            page = d.metadata.get("page", "?")
            block = " ".join(str(x) for x in [d.metadata.get("block_kind"), d.metadata.get("block_id")] if x).strip()
            tag = block if block else d.metadata.get("type", "cours")
            content = normalize_whitespace(d.page_content or "")
            parts.append(f"[{tag.upper()} - Page {page}]\n{content}")
        return "\n---\n".join(parts)

    @staticmethod
    def _top_meta(docs: List[Document]) -> Optional[dict]:
        if not docs: return None
        d = docs[0]
        return {
            "chapter": d.metadata.get("chapter"),
            "block_kind": d.metadata.get("block_kind"),
            "block_id": d.metadata.get("block_id"),
            "type": d.metadata.get("type"),
            "page": d.metadata.get("page"),
        }

    # -- Calcul des kwargs (scope + auto-link) --
    def _compute_filters(self, question: str, filter_type: Optional[str], auto_link: bool) -> Tuple[Dict[str, Any], bool]:
        chapter = block_id = block_kind = None
        follow = self.memory.is_follow_up(question, self.memory.state.get("last_question"))
        if auto_link and follow:
            ctx = self.memory.best_context_meta()
            if ctx:
                chapter = chapter or ctx.get("chapter")
                block_kind = block_kind or ctx.get("block_kind")
                block_id = block_id or ctx.get("block_id")
                if not filter_type and ctx.get("type"):
                    filter_type = ctx["type"]
        base = dict(doc_type=filter_type, chapter=chapter, block_kind=block_kind, block_id=block_id)
        final_kwargs = self.memory.apply_scope(base)
        return final_kwargs, follow

    # -- Orchestration complète --
    def route_and_execute(
        self,
        question: str,
        filter_type: Optional[str] = None,
        *,
        auto_link: bool = True,
        debug: bool = False,
        auto_pin_next: bool = False,
        allow_oot: bool = True,  # Autoriser hors-programme ?
    ) -> Dict[str, Any]:
        # Debug container pour ce tour
        dbg: Dict[str, Any] = {
            "ts": _now_ms(),
            "chat_id": self.memory.chat_id,
            "runtime": self.active_models(),
            "input_question": question,
            "auto_link": auto_link,
            "allow_oot": allow_oot,
        } if debug else {}

        filters, follow = self._compute_filters(question, filter_type, auto_link)
        if debug:
            dbg["filters"] = dict(filters)
            dbg["follow_up"] = bool(follow)

        ctx_meta = {
            "chapter": filters.get("chapter"),
            "block_kind": filters.get("block_kind"),
            "block_id": filters.get("block_id"),
            "type": filters.get("doc_type")
        }
        rewritten = self.rewriter.rewrite(
            question, self.memory.state.get("last_question"), ctx_meta, follow, dbg=dbg
        )
        if debug:
            dbg["rewritten_q"] = rewritten

        # Décision de route (auto)
        decision = decide_route(
            chat_id=self.memory.chat_id,
            raw_q=question,
            rewritten_q=rewritten,
            filters=filters,
            pinned_bias=bool(self.memory.state.get("pinned_meta")),
            last_decision=self.memory.state.get("last_decision"),
        )
        if debug:
            dbg["router"] = {
                "decision": decision.decision,
                "task": decision.task,
                "rag_conf": decision.rag_conf,
                "passport": decision.passport,
            }

        # appliquer override utilisateur
        override = self.memory.get_route_override()
        if override == "rag":
            decision.decision = "rag_first"; decision.reason = "override utilisateur (rag)"
        elif override == "llm":
            decision.decision = "llm_only"; decision.reason = "override utilisateur (llm)"
        elif override == "hybrid":
            decision.decision = "rag_to_llm"; decision.reason = "override utilisateur (hybrid)"
        self.memory.state["last_decision"] = decision.decision
        if debug and override:
            dbg.setdefault("router", {}).update({"override": override, "final_decision": decision.decision})

        # Exécution selon la route
        if decision.task and decision.decision != "rag_to_llm" and decision.task != "answer":
            payload = self.run_task(
                decision.task,
                question,
                filter_type=filter_type,
                auto_link=auto_link,
                debug=debug,
                auto_pin_next=auto_pin_next,
            )
            payload["passport"] = decision.passport
            top_meta = self._top_meta(payload.get("docs", []))
            payload["passport"]["top_meta"] = top_meta
            self.memory.state["last_decision"] = decision.decision
            if debug:
                payload["_debug"] = dbg
                self._dump_debug(payload["_debug"])
            return payload

        if decision.decision == "rag_first":
            payload = self._do_rag_answer(question, rewritten, filters, follow, allow_oot=allow_oot, dbg=dbg if debug else None)
        elif decision.decision == "rag_to_llm":
            payload = self._do_rag_then_llm(question, rewritten, filters, follow, task=decision.task, allow_oot=allow_oot, dbg=dbg if debug else None)
        elif decision.decision in {"llm_first", "llm_only"}:
            answer = self._invoke_with_fallback(
                ChatPromptTemplate.from_template(
                    "Explique en termes simples puis rigoureux : {q}. Donne 1 exemple en $$…$$ si pertinent."
                ),
                {"q": question},
                dbg=dbg if debug else None,
                step="llm_only"
            )
            payload = {
                "answer": answer, "docs": [], "final_kwargs": filters,
                "rewritten_q": rewritten, "hinted_q": rewritten,
                "top_meta": None, "follow_flag": follow
            }
        else:
            payload = {
                "answer": "(route inconnue)", "docs": [], "final_kwargs": filters,
                "rewritten_q": rewritten, "hinted_q": rewritten,
                "top_meta": None, "follow_flag": follow
            }

        # Mémoire + passeport
        self.memory.state["last_question"] = question
        top_meta = self._top_meta(payload.get("docs", []))
        if top_meta:
            self.memory.state["last_top_meta"] = top_meta
            if auto_pin_next:
                self.memory.state["pinned_meta"] = top_meta
        payload["passport"] = decision.passport
        payload["passport"]["top_meta"] = top_meta

        # Log
        self.memory.add_log({
            "q": question,
            **{k: (v if k != 'docs' else [d.metadata for d in v]) for k, v in payload.items()}
        })

        # Debug attach + dump
        if debug:
            payload["_debug"] = dbg
            self._dump_debug(payload["_debug"])

        return payload

    # -- Exécution des tâches --
    def run_task(
        self,
        task: str,
        question_or_payload: str,
        *,
        filter_type: Optional[str] = None,
        auto_link: bool = True,
        debug: bool = False,
        auto_pin_next: bool = False,
        **task_kwargs: Any,
    ) -> Dict[str, Any]:

        dbg: Dict[str, Any] = {"ts": _now_ms(), "task": task, "runtime": self.active_models()} if debug else {}

        prompt_tpl, default_doc_type = get_prompt(task)
        effective_doc_type = filter_type if filter_type is not None else default_doc_type

        filters, follow = self._compute_filters(question_or_payload, effective_doc_type, auto_link)
        if debug:
            dbg["filters"] = dict(filters); dbg["follow_up"] = bool(follow)

        ctx_meta = {
            "chapter":   filters.get("chapter"),
            "block_kind":filters.get("block_kind"),
            "block_id":  filters.get("block_id"),
            "type":      filters.get("doc_type"),
        }
        rewritten = self.rewriter.rewrite(
            new_q=question_or_payload,
            last_q=self.memory.state.get("last_question"),
            context_meta=ctx_meta,
            is_followup=follow,
            dbg=dbg if debug else None
        )

        hard_prefix = []
        if ctx_meta.get("chapter"): hard_prefix.append(f"chapitre {ctx_meta['chapter']}")
        if ctx_meta.get("block_kind") and ctx_meta.get("block_id"):
            hard_prefix.append(f"{str(ctx_meta['block_kind']).lower()} {ctx_meta['block_id']}")
        if ctx_meta.get("type"): hard_prefix.append(f"type {ctx_meta['type']}")
        hinted_q = rewritten if not hard_prefix else " | ".join(hard_prefix) + " — " + rewritten
        if debug:
            dbg["rewritten_q"] = rewritten; dbg["hinted_q"] = hinted_q

        # compat top_k/k
        try:
            retriever = self.engine.create_retriever(top_k=8, **filters)
        except TypeError:
            retriever = self.engine.create_retriever(k=8, **filters)
        docs: List[Document] = retriever.invoke(hinted_q)

        if filters.get("block_id"):
            bid   = str(filters["block_id"])
            bkind = (filters.get("block_kind") or "").lower()
            ch    = str(filters.get("chapter") or "")
            docs  = sorted(
                docs,
                key=lambda d: (
                    str(d.metadata.get("block_id")) == bid,
                    str(d.metadata.get("block_kind","")).lower() == bkind,
                    str(d.metadata.get("chapter")) == ch,
                ),
                reverse=True
            )[:8]

        context = self._format_context(docs)

        vars = {
            "context": context,
            "question": question_or_payload,
            "topic": question_or_payload,
            "notion": question_or_payload,
            "level": task_kwargs.get("level", "prépa/terminale+"),
            "chapters": task_kwargs.get("chapters", "—"),
            "duration": task_kwargs.get("duration", "2h"),
            "num_exercises": task_kwargs.get("num_exercises", 4),
            "total_points": task_kwargs.get("total_points", 20),
            "sheet_text": task_kwargs.get("sheet_text", ""),
            "query": task_kwargs.get("query", question_or_payload),
            "statement": task_kwargs.get("statement", question_or_payload),
            "student_answer": task_kwargs.get("student_answer", ""),
            "points": task_kwargs.get("points", 10),
            "num_questions": task_kwargs.get("num_questions", 12),
            "source": task_kwargs.get("source", "original"),
            "difficulty": task_kwargs.get("difficulty", "mixte"),
            "with_solutions": task_kwargs.get("with_solutions", True),
        }
        vars.update(task_kwargs)

        answer = self._invoke_with_fallback(prompt_tpl, vars, dbg=dbg if debug else None, step=f"task:{task}")

        self.memory.state["last_question"] = question_or_payload
        top_meta = self._top_meta(docs)
        if top_meta:
            self.memory.state["last_top_meta"] = top_meta
            if auto_pin_next:
                self.memory.state["pinned_meta"] = top_meta

        payload = {
            "task": task,
            "answer": answer,
            "docs": docs,
            "final_kwargs": filters,
            "rewritten_q": rewritten,
            "hinted_q": hinted_q,
            "top_meta": top_meta,
            "follow_flag": follow,
            "prompt_vars": vars,
        }
        self.memory.add_log({
            "q": question_or_payload,
            **{k: (v if k != "docs" else [d.metadata for d in v]) for k, v in payload.items()}
        })
        if debug:
            payload["_debug"] = dbg
            self._dump_debug(payload["_debug"])
        return payload

    def run_tasks(self, jobs: List[dict]) -> List[dict]:
        out = []
        for job in jobs:
            job = dict(job)
            task = job.pop("task")
            question_or_payload = job.pop("question_or_payload")
            out.append(self.run_task(task, question_or_payload, **job))
        return out

    def new_session(self, *, reset_scope: bool = True, preserve_logs: bool = True):
        self.memory.start_new_session(reset_scope=reset_scope, preserve_logs=preserve_logs)

    # -- RAG direct --
    def _do_rag_answer(
        self,
        question: str,
        rewritten: str,
        filters: Dict[str, Any],
        follow: bool,
        *,
        allow_oot: bool,
        dbg: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # compat top_k/k
        try:
            retriever = self.engine.create_retriever(top_k=8, **filters)
        except TypeError:
            retriever = self.engine.create_retriever(k=8, **filters)
        
        # Capture le where Chroma pour debug
        final_where = getattr(retriever, "_vector_where_debug", None)
        
        hinted_q = rewritten
        if any(w in question.lower() for w in ["énoncé", "enonce", "théorème", "theoreme", "page"]):
            hinted_q += " :: enonce theoreme page"

        # Normaliser LaTeX → Unicode pour meilleur retrieval
        hinted_q_normalized = normalize_query_for_retrieval(hinted_q)

        t0 = _now_ms()
        docs = retriever.invoke(hinted_q_normalized)
        tR = _now_ms() - t0

        # évaluer la qualité du contexte
        sim_max = 0.0
        try:
            if docs:
                sims = []
                for d in docs[:6]:
                    snippet = normalize_whitespace(d.page_content or "")[:700]
                    p = fuzz.partial_ratio(question, snippet)/100.0
                    t = fuzz.token_sort_ratio(question, snippet)/100.0
                    sims.append(0.6*p + 0.4*t)
                sim_max = max(sims) if sims else 0.0
        except Exception:
            pass

        if dbg is not None:
            dbg["retrieval"] = {
                "hinted_q": hinted_q,
                "docs_found": len(docs),
                "sim_max": sim_max,
                "latency_ms": tR,
                "filters": dict(filters),
                "bm25_only": getattr(self.engine, "_bm25_only", False),
                "use_reranker": bool(getattr(self.engine.config, "use_reranker", False)),
                "final_where": final_where,
            }
            dbg["top_docs_meta"] = [d.metadata for d in docs[:5]]

        # fallback autonome si contexte trop faible
        if not docs or sim_max < 0.25:
            if allow_oot:
                answer = self._invoke_with_fallback(
                    ChatPromptTemplate.from_template(
                        "Réponds de façon autonome et pédagogique à : {q}. "
                        "Commence simple, puis rigoureux. Donne un exemple en $$…$$ si pertinent. "
                        "Signale explicitement que tu réponds hors du livre."
                    ),
                    {"q": question},
                    dbg=dbg,
                    step="oot_autonome"
                )
            else:
                answer = "Contexte insuffisant pour répondre avec rigueur (hors programme désactivé)."
            return {
                "answer": answer, "docs": [], "final_kwargs": filters,
                "rewritten_q": rewritten, "hinted_q": hinted_q,
                "top_meta": None, "follow_flag": follow,
                "final_where": final_where
            }

        # Post-tri strict sur block_id (si demandé)
        if filters.get("block_id"):
            bid = str(filters["block_id"])
            bkind = normalize_whitespace(filters.get("block_kind") or "").lower()
            ch = str(filters.get("chapter") or "")
            docs = sorted(
                docs,
                key=lambda d: (
                    str(d.metadata.get("block_id")) == bid,
                    normalize_whitespace(d.metadata.get("block_kind") or "").lower() == bkind,
                    str(d.metadata.get("chapter")) == ch
                ),
                reverse=True
            )[:8]
        
        # Bonus sécurité: si docs vide après filtrage strict, relance recherche dégradée
        if not docs and filters.get("block_id"):
            if dbg is not None:
                dbg["fallback_search"] = "block_id trop strict, relance avec chapter seul"
            try:
                retriever_loose = self.engine.create_retriever(k=12, chapter=filters.get("chapter"))
            except TypeError:
                retriever_loose = self.engine.create_retriever(top_k=12, chapter=filters.get("chapter"))
            # Normaliser aussi la query pour le fallback
            fallback_query = normalize_query_for_retrieval(hinted_q)
            docs = retriever_loose.invoke(fallback_query)[:8]

        self._print_sources(docs)
        context = self._format_context(docs)
        
        # Ergonomie: si définition + question sur "preuve" → reformule
        top_meta_local = self._top_meta(docs)
        bk = normalize_whitespace((top_meta_local or {}).get("block_kind", "") or "").lower()
        q_adjusted = question
        if bk == "definition" and "preuve" in question.lower():
            q_adjusted = question.lower().replace("preuve", "commentaire, intuition et usages")
            if dbg is not None:
                dbg["question_adjusted"] = q_adjusted
        
        answer = self._invoke_prof(context=context, question=q_adjusted, dbg=dbg)
        return {
            "answer": answer, "docs": docs, "final_kwargs": filters,
            "rewritten_q": rewritten, "hinted_q": hinted_q,
            "top_meta": self._top_meta(docs), "follow_flag": follow,
            "final_where": final_where
        }

    # -- RAG puis LLM (exos/démos/extension) --
    def _do_rag_then_llm(
        self,
        question: str,
        rewritten: str,
        filters: Dict[str, Any],
        follow: bool,
        *,
        task: str,
        allow_oot: bool,
        dbg: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # compat top_k/k
        try:
            retriever = self.engine.create_retriever(top_k=8, **filters)
        except TypeError:
            retriever = self.engine.create_retriever(k=8, **filters)
        
        # Capture le where Chroma pour debug
        final_where = getattr(retriever, "_vector_where_debug", None)
        
        # Normaliser LaTeX → Unicode pour meilleur retrieval
        query_normalized = normalize_query_for_retrieval(rewritten or question)
        
        t0 = _now_ms()
        docs = retriever.invoke(query_normalized)
        tR = _now_ms() - t0

        if dbg is not None:
            dbg["retrieval"] = {
                "hinted_q": (rewritten or question),
                "docs_found": len(docs),
                "latency_ms": tR,
                "filters": dict(filters),
                "bm25_only": getattr(self.engine, "_bm25_only", False),
                "use_reranker": bool(getattr(self.engine.config, "use_reranker", False)),
                "final_where": final_where,
            }
            dbg["top_docs_meta"] = [d.metadata for d in docs[:5]]

        if not docs:
            answer = self._invoke_with_fallback(
                ChatPromptTemplate.from_template(
                    ("Formule une réponse autonome à : {q}. Ajoute un avertissement si suppositions."
                     if allow_oot else
                     "Contexte insuffisant (hors programme désactivé). Reformule la demande ou précise le chapitre.")
                ),
                {"q": question},
                dbg=dbg,
                step=f"rag_to_llm:oot_{'on' if allow_oot else 'off'}"
            )
            return {
                "answer": answer, "docs": [], "final_kwargs": filters,
                "rewritten_q": rewritten, "hinted_q": rewritten,
                "top_meta": None, "follow_flag": follow,
                "final_where": final_where
            }

        context = self._format_context(docs)
        prompt_tpl, _ = get_prompt(task)

        vars = {
            "context": context,
            "question": question,
            "topic": question,
            "notion": question,
            "level": "prépa/terminale+",
            "chapters": "—",
            "duration": "2h",
            "num_exercises": 4,
            "total_points": 20,
            "sheet_text": "",
            "query": question,
            "statement": question,
            "student_answer": "",
            "points": 10,
            "num_questions": 12,
            "source": "original",
            "difficulty": "mixte",
            "with_solutions": True,
        }

        answer = self._invoke_with_fallback(prompt_tpl, vars, dbg=dbg, step=f"rag_to_llm:{task}")
        self._print_sources(docs)
        return {
            "answer": answer, "docs": docs, "final_kwargs": filters,
            "rewritten_q": rewritten, "hinted_q": rewritten,
            "top_meta": self._top_meta(docs), "follow_flag": follow,
            "final_where": final_where
        }

    # -- API utilitaires --
    def ensure_ready(self):
        self.engine.build_or_load_store()

    def save_log(self, path: str):
        self.memory.save_log(path)

    def set_scope(self, **kwargs):
        self.memory.scope_set(**kwargs)

    def clear_scope(self):
        self.memory.scope_clear()

    # -- Debug dump util --
    def _dump_debug(self, dbg: Dict[str, Any]):
        if not dbg:
            return
        try:
            ui_config.debug_dir.mkdir(parents=True, exist_ok=True)
            ts = dbg.get("ts", _now_ms())
            fname = f"{self.memory.chat_id}_{ts}.json"
            fpath = ui_config.debug_dir / fname
            # tronquer les gros champs
            safe = json.loads(json.dumps(dbg, ensure_ascii=False))
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(safe, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# -- Instance globale et helpers module-level --

_assistant: Optional[MathAssistant] = None

def get_assistant() -> MathAssistant:
    """Singleton de l'assistant."""
    global _assistant
    if _assistant is None:
        _assistant = MathAssistant()
    return _assistant

def run_task(task: str, question_or_payload: str, **kwargs):
    return get_assistant().run_task(task, question_or_payload, **kwargs)

def run_tasks(jobs: List[dict]):
    return get_assistant().run_tasks(jobs)
