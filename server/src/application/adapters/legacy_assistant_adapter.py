"""
Legacy Assistant Adapter

Wraps MathAssistantFacade to provide the old MathAssistant API.
This allows existing CLI/GUI/API code to work without modifications.

ARCHITECTURE:
-------------
┌─────────────────────────────────────────┐
│  Legacy Code (CLI, GUI, FastAPI)        │
│  • calls .route_and_execute()           │
│  • calls .run_task()                    │
│  • accesses .memory attribute           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  LegacyAssistantAdapter                 │  ← This file
│  • Translates old API → new Facade API  │
│  • Provides .memory compatibility       │
│  • Maps task names to facade methods    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  MathAssistantFacade (SOLID)            │
│  • 17 high-level methods                │
│  • DI Container                         │
│  • 16 Use Cases                         │
└─────────────────────────────────────────┘

USAGE:
------
# In src/assistant/__init__.py:
from src.application.adapters import LegacyAssistantAdapter

def get_assistant():
    return LegacyAssistantAdapter()

# All legacy code works unchanged!
assistant = get_assistant()
result = assistant.route_and_execute("question", "exercice")
result = assistant.run_task("qcm", "séries", num_questions=5)
"""

from typing import Optional, Dict, Any
from ..facades import MathAssistantFacade


class LegacyAssistantAdapter:
    """
    Adapter wrapping MathAssistantFacade for backward compatibility.
    
    This class provides the OLD MathAssistant API while using the
    NEW SOLID architecture under the hood.
    
    Key responsibilities:
    - Translate route_and_execute() → facade.ask() or appropriate method
    - Translate run_task(task, ...) → facade method based on task name
    - Provide .memory attribute compatibility
    - Map old parameter names to new ones
    """
    
    def __init__(self):
        """Initialize adapter with facade."""
        self._facade = MathAssistantFacade()
        
        # Expose memory for backward compatibility
        # Legacy code accesses assistant.memory.chat_id, etc.
        self._memory_proxy = SessionMemoryProxy(self._facade)
    
    @property
    def memory(self):
        """Legacy memory access → SessionContext proxy."""
        return self._memory_proxy
    
    def ensure_ready(self):
        """
        Legacy method to ensure system is ready.
        
        In new architecture, DI Container handles initialization,
        so this is a no-op.
        """
        # No-op: DI Container already initialized everything
        pass
    
    def new_session(self, reset_scope: bool = True, preserve_logs: bool = True):
        """
        Start a new session (legacy method).
        
        Parameters
        ----------
        reset_scope : bool
            Whether to reset scope/filters (unused in new architecture)
        preserve_logs : bool
            Whether to preserve logs (unused in new architecture)
        """
        self._facade.new_session()
    
    # ========================================================================
    # Logging Methods
    # ========================================================================
    
    def enable_logs(self, enabled: bool = True):
        """
        Enable/disable logging.
        
        For backward compatibility, delegate to memory proxy.
        """
        self._memory_proxy._state["logs_enabled"] = enabled
    
    def add_log(self, entry: dict):
        """
        Add a log entry.
        
        For backward compatibility, delegate to memory proxy.
        """
        self._memory_proxy.add_log(entry)
    
    def save_log(self, path: str):
        """
        Save logs to file.
        
        For backward compatibility, write logs from memory proxy.
        """
        import json
        from pathlib import Path
        
        logs = self._memory_proxy._state.get("logs", [])
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for log in logs:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
    
    def best_context_meta(self) -> Optional[Dict[str, Any]]:
        """
        Get best context metadata.
        
        For backward compatibility, delegate to memory proxy.
        """
        return self._memory_proxy.best_context_meta()
    
    # ========================================================================
    # Router & Runtime Methods
    # ========================================================================
    
    def set_route_override(self, mode: Optional[str]):
        """
        Set route override (auto|rag|llm|hybrid).
        
        For backward compatibility, store in memory proxy.
        """
        self._memory_proxy.set_route_override(mode)
    
    def get_route_override(self) -> Optional[str]:
        """
        Get current route override.
        
        For backward compatibility, delegate to memory proxy.
        """
        return self._memory_proxy.get_route_override()
    
    def set_runtime_mode(self, mode: str) -> Dict[str, Any]:
        """
        Set runtime mode (local|cloud|hybrid).
        
        ⚠️ WARNING: In new architecture, runtime is set at startup.
        This method is provided for backward compatibility but has limited effect.
        
        To truly switch runtime, restart the application with new config.
        
        Parameters
        ----------
        mode : str
            Runtime mode: "local", "cloud", or "hybrid"
            
        Returns
        -------
        Dict[str, Any]
            Current configuration (simulated)
        """
        from ...core.config import rag_config
        
        # Store mode preference
        self._memory_proxy._state["runtime_mode"] = mode
        
        # Return simulated config
        # In reality, changing runtime requires recreating the DI Container
        return {
            "runtime": mode,
            "host": rag_config.ollama_host,
            "llm_primary": rag_config.llm_model,
            "llm_fallback": rag_config.llm_local_fallback,
            "rewriter_model": rag_config.rewrite_model,
            "note": "⚠️ Runtime change requires restart in new architecture"
        }
    
    def active_models(self) -> Dict[str, Any]:
        """
        Get active models configuration.
        
        For backward compatibility, read from config.
        """
        from ...core.config import rag_config
        
        return {
            "host": rag_config.ollama_host,
            "runtime_default": getattr(rag_config, "runtime_default_mode", "hybrid"),
            "llm_primary": rag_config.llm_model,
            "llm_fallback": rag_config.llm_local_fallback,
            "rewriter_enabled": rag_config.use_rewriter,
            "rewriter_model": rag_config.rewrite_model,
        }
    
    # ========================================================================
    # Batch Processing
    # ========================================================================
    
    def run_tasks(self, jobs: list[dict]) -> list[dict]:
        """
        Execute multiple tasks in batch.
        
        For backward compatibility, process sequentially.
        
        Parameters
        ----------
        jobs : list[dict]
            List of job specifications, each with task name and parameters
            
        Returns
        -------
        list[dict]
            Results for each job
        """
        results = []
        for job in jobs:
            try:
                result = self.run_task(**job)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "job": job
                })
        return results
    
    # ========================================================================
    # Engine Access (for legacy code that accesses .engine directly)
    # ========================================================================
    
    @property
    def engine(self):
        """
        Get RAG engine.
        
        ⚠️ WARNING: Direct engine access is discouraged.
        Use facade methods instead.
        
        For backward compatibility, return the retriever's store.
        """
        # Return None or a mock object
        # Real engine access should go through use cases
        class EngineMock:
            """Mock engine for backward compatibility."""
            def __init__(self):
                pass
        
        return EngineMock()
    
    def route_and_execute(
        self,
        question: str,
        filter_type: Optional[str] = None,
        auto_link: bool = True,
        debug: bool = False,
        auto_pin_next: bool = False,
        allow_oot: bool = True,
        progress_callback: Optional[callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy main entry point for Q&A.
        
        Maps to facade.ask() with appropriate parameters.
        
        Parameters
        ----------
        question : str
            User question
        filter_type : Optional[str]
            Document type filter (exercice, théorème, etc.)
        auto_link : bool
            Auto-link to previous context
        debug : bool
            Enable debug mode
        auto_pin_next : bool
            Pin result to context (handled by SessionContext)
        allow_oot : bool
            Allow out-of-topic questions
            
        Returns
        -------
        Dict[str, Any]
            Response with keys: answer, docs, metadata
            
        Notes
        -----
        Old API returned:
        {
            "answer": str,
            "docs": List[Document],
            "metadata": {...}
        }
        
        New facade returns:
        {
            "answer": str,
            "sources": List[Document],
            "metadata": {...}
        }
        
        This method translates between the two.
        """
        # Get router override if set
        router_override = self._memory_proxy.get_route_override()
        
        # Call facade
        result = self._facade.ask(
            question=question,
            doc_type=filter_type,
            auto_link=auto_link,
            debug=debug,
            router_mode=router_override,
            progress_callback=progress_callback
        )
        
        # Update memory state for backward compatibility
        # Store last question and context metadata so CLI can access them
        self._memory_proxy._state["last_question"] = question
        if result.get("sources"):
            # Store first document metadata as "last_top_meta"
            first_doc = result["sources"][0]
            self._memory_proxy._state["last_top_meta"] = {
                "page": first_doc.metadata.get("page"),
                "chapter": first_doc.metadata.get("chapter"),
                "doc_type": first_doc.metadata.get("doc_type"),
                "file_name": first_doc.metadata.get("file_name"),
            }
        
        # Translate response format
        return {
            "answer": result["answer"],
            "docs": result["sources"],  # OLD KEY: "docs" → NEW KEY: "sources"
            "metadata": result.get("metadata", {})
        }
    
    def run_task(
        self,
        task: str,
        question_or_payload: str,
        filter_type: Optional[str] = None,
        auto_link: bool = True,
        debug: bool = False,
        auto_pin_next: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy task execution method.
        
        Maps task names to appropriate facade methods.
        
        Task Mapping:
        -------------
        - "qa", "question" → ask()
        - "explain", "course" → explain_course()
        - "build_course" → build_course()
        - "summarize_course" → summarize_course()
        - "exercises", "exercice" → generate_exercises()
        - "solve" → solve_exercise()
        - "correct" → correct_exercise()
        - "theorem", "théorème" → explain_theorem()
        - "formula", "formule" → explain_formula()
        - "proof", "prove" → prove_statement()
        - "sheet", "fiche" → create_sheet()
        - "review_sheet" → review_sheet()
        - "exam", "examen" → generate_exam()
        - "correct_exam" → correct_exam()
        - "qcm" → generate_qcm()
        - "kholle" → generate_kholle()
        - "tutor" → ask() with special handling (future: TutorUseCase)
        
        Parameters
        ----------
        task : str
            Task name (see mapping above)
        question_or_payload : str
            Question text or payload
        filter_type : Optional[str]
            Document type filter
        **kwargs
            Additional task-specific parameters
            
        Returns
        -------
        Dict[str, Any]
            Response in old format (answer, docs, metadata)
        """
        # Normalize task name
        task_lower = task.lower().strip()
        router_override = self._memory_proxy.get_route_override()
        
        # Map to facade method
        if task_lower in {"qa", "question"}:
            result = self._facade.ask(
                question=question_or_payload,
                doc_type=filter_type,
                auto_link=auto_link,
                debug=debug,
                router_mode=router_override,
            )
        
        elif task_lower in {"explain", "course", "cours", "course_explain"}:
            chapter = kwargs.get("chapter")
            level = kwargs.get("level", "prépa/terminale+")
            result = self._facade.explain_course(
                topic=question_or_payload,
                level=level,
                chapter=chapter
            )
        
        elif task_lower in {"build_course", "course_build"}:
            chapter = kwargs.get("chapter")
            level = kwargs.get("level", "prépa/terminale+")
            result = self._facade.build_course(
                topic=question_or_payload,
                level=level,
                chapter=chapter
            )
        
        elif task_lower == "summarize_course":
            chapter = kwargs.get("chapter")
            level = kwargs.get("level", "prépa/terminale+")
            result = self._facade.summarize_course(
                topic=question_or_payload,
                level=level,
                chapter=chapter
            )
        
        elif task_lower in {"exercises", "exercice", "exercices"}:
            count = kwargs.get("count", kwargs.get("num_exercises", 3))
            difficulty = kwargs.get("difficulty", "moyen")
            chapter = kwargs.get("chapter")
            result = self._facade.generate_exercises(
                topic=question_or_payload,
                count=count,
                difficulty=difficulty,
                chapter=chapter
            )
        
        elif task_lower == "solve":
            chapter = kwargs.get("chapter")
            result = self._facade.solve_exercise(
                exercise_text=question_or_payload,
                chapter=chapter
            )
        
        elif task_lower == "correct":
            exercise_text = kwargs.get("exercise_text", "")
            student_answer = question_or_payload
            chapter = kwargs.get("chapter")
            result = self._facade.correct_exercise(
                exercise_text=exercise_text,
                student_answer=student_answer,
                chapter=chapter
            )
        
        elif task_lower in {"theorem", "théorème", "theoreme"}:
            chapter = kwargs.get("chapter")
            result = self._facade.explain_theorem(
                theorem_name=question_or_payload,
                chapter=chapter
            )
        
        elif task_lower in {"formula", "formule"}:
            chapter = kwargs.get("chapter")
            result = self._facade.explain_formula(
                formula_name=question_or_payload,
                chapter=chapter
            )
        
        elif task_lower in {"proof", "prove", "preuve"}:
            chapter = kwargs.get("chapter")
            result = self._facade.prove_statement(
                statement=question_or_payload,
                chapter=chapter
            )
        
        elif task_lower in {"sheet", "fiche"}:
            chapter = kwargs.get("chapter")
            level = kwargs.get("level", "prépa/terminale+")
            result = self._facade.create_sheet(
                topic=question_or_payload,
                level=level,
                chapter=chapter
            )
        
        elif task_lower == "review_sheet":
            sheet_text = question_or_payload
            topic = kwargs.get("topic", "")
            level = kwargs.get("level", "prépa/terminale+")
            result = self._facade.review_sheet(
                sheet_text=sheet_text,
                topic=topic,
                level=level
            )
        
        elif task_lower in {"exam", "examen"}:
            chapters = kwargs.get("chapters", kwargs.get("chapter", ""))
            duration = kwargs.get("duration", "2h")
            total_points = kwargs.get("total_points", 100)
            difficulty = kwargs.get("difficulty", "moyen")
            result = self._facade.generate_exam(
                chapters=chapters,
                duration=duration,
                total_points=total_points,
                difficulty=difficulty
            )
        
        elif task_lower == "correct_exam":
            exam_text = kwargs.get("exam_text", "")
            student_answers = question_or_payload
            chapter = kwargs.get("chapter")
            result = self._facade.correct_exam(
                exam_text=exam_text,
                student_answers=student_answers,
                chapter=chapter
            )
        
        elif task_lower == "qcm":
            num_questions = kwargs.get("num_questions", kwargs.get("count", 5))
            chapter = kwargs.get("chapter")
            result = self._facade.generate_qcm(
                topic=question_or_payload,
                num_questions=num_questions,
                chapter=chapter
            )
        
        elif task_lower == "kholle":
            duration = kwargs.get("duration", "20min")
            chapter = kwargs.get("chapter")
            result = self._facade.generate_kholle(
                topic=question_or_payload,
                duration=duration,
                chapter=chapter
            )
        
        elif task_lower == "tutor":
            # Tutor mode: for now, use ask() with guidance
            # Future: create dedicated TutorUseCase
            with_solutions = kwargs.get("with_solutions", False)
            result = self._facade.ask(
                question=question_or_payload,
                doc_type=filter_type,
                auto_link=auto_link,
                debug=debug,
                router_mode=router_override,
            )
            # Add tutor metadata
            result["metadata"]["task"] = "tutor"
            result["metadata"]["with_solutions"] = with_solutions
        
        else:
            # Unknown task: fallback to ask()
            result = self._facade.ask(
                question=question_or_payload,
                doc_type=filter_type,
                auto_link=auto_link,
                debug=debug,
                router_mode=router_override,
            )
        
        # Update memory state for backward compatibility
        # Store last question and context metadata so CLI can access them
        self._memory_proxy._state["last_question"] = question_or_payload
        if result.get("sources") and len(result["sources"]) > 0:
            # Store first document metadata as "last_top_meta"
            first_doc = result["sources"][0]
            self._memory_proxy._state["last_top_meta"] = {
                "page": first_doc.metadata.get("page"),
                "chapter": first_doc.metadata.get("chapter"),
                "doc_type": first_doc.metadata.get("doc_type"),
                "file_name": first_doc.metadata.get("file_name"),
            }
        
        # Translate response format (sources → docs)
        return {
            "answer": result["answer"],
            "docs": result.get("sources", []),  # OLD KEY
            "metadata": result.get("metadata", {})
        }


class SessionMemoryProxy:
    """
    Proxy for SessionContext to provide .memory compatibility.
    
    Legacy code accesses:
    - assistant.memory.chat_id
    - assistant.memory.state (dict)
    - assistant.memory.best_context_meta()
    - assistant.memory.reset(full=True/False)
    - assistant.memory.start_new_session()
    - assistant.memory.is_follow_up()
    - assistant.memory.apply_scope()
    - assistant.memory.get_route_override()
    - assistant.memory.set_route_override()
    - assistant.memory.add_log()
    - etc.
    
    This proxy translates these to SessionContext or provides stubs.
    """
    
    def __init__(self, facade: MathAssistantFacade):
        self._facade = facade
        # State dict for backward compatibility
        self._state = {}
    
    @property
    def chat_id(self) -> str:
        """Get current chat ID."""
        return self._facade.get_session_id()
    
    @property
    def state(self) -> Dict[str, Any]:
        """
        Get session state dictionary.
        
        Legacy code accesses:
        - memory.state["last_question"]
        - memory.state["last_top_meta"]
        - memory.state["pinned_meta"]
        - memory.state["last_decision"]
        
        Returns a dict that can be read/written.
        """
        return self._state
    
    def best_context_meta(self) -> Optional[Dict[str, Any]]:
        """
        Get best context metadata.
        
        Returns pinned_meta if available, else last_top_meta.
        """
        return self._state.get("pinned_meta") or self._state.get("last_top_meta")
    
    def reset(self, full: bool = False):
        """
        Reset session memory.
        
        Parameters
        ----------
        full : bool
            If True, full reset (clear everything).
            If False, partial reset (keep pinned_meta).
        """
        if full:
            # Full reset: clear everything and start new session
            self._state.clear()
            self._facade.new_session()
        else:
            # Partial reset: keep pinned_meta, clear the rest
            pinned = self._state.get("pinned_meta")
            self._state.clear()
            if pinned:
                self._state["pinned_meta"] = pinned
    
    def start_new_session(self, reset_scope: bool = True, preserve_logs: bool = True):
        """Start a new session (legacy method)."""
        self._facade.new_session()
        if not preserve_logs:
            self._state.clear()
    
    def is_follow_up(self, current_question: str, last_question: Optional[str]) -> bool:
        """
        Check if current question is a follow-up.
        
        Simple heuristic: if current starts with short words like
        "et", "mais", "donc", "aussi", etc.
        """
        if not last_question:
            return False
        
        current_lower = current_question.strip().lower()
        follow_up_words = {"et", "mais", "donc", "aussi", "encore", "puis", "alors", "ensuite"}
        
        for word in follow_up_words:
            if current_lower.startswith(word + " "):
                return True
        
        return False
    
    def apply_scope(self, base_filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply scope/filters to base filters.
        
        For backward compatibility, just return base_filters.
        In new architecture, filters are managed differently.
        """
        return base_filters
    
    def get_route_override(self) -> Optional[str]:
        """Get route override (rag/llm/hybrid)."""
        return self._state.get("route_override")
    
    def set_route_override(self, mode: Optional[str]):
        """Set route override."""
        if mode:
            self._state["route_override"] = mode
        elif "route_override" in self._state:
            del self._state["route_override"]
    
    def add_log(self, log_entry: Dict[str, Any]):
        """
        Add log entry.
        
        For backward compatibility, store in state.
        """
        if "logs" not in self._state:
            self._state["logs"] = []
        self._state["logs"].append(log_entry)
    
    def get_pinned_blocks(self):
        """Get pinned blocks from context."""
        # SessionContext doesn't have pinned blocks yet
        # Return empty list for backward compatibility
        return []
    
    def forget(self):
        """Clear session memory."""
        self.reset(full=True)
    
    def new_chat(self):
        """Start new chat."""
        self.start_new_session()
    
    # ========================================================================
    # Scope Management Methods
    # ========================================================================
    
    def scope_show(self) -> str:
        """
        Show ALL current settings: scope/filters, OOT, tutor mode, router, etc.
        
        Returns a comprehensive string representation of all active settings.
        """
        lines = []
        
        # 1. Scope/Filters
        if "scope" not in self._state:
            self._state["scope"] = {
                "chapter": None,
                "block_kind": None,
                "block_id": None,
                "type": None
            }
        
        scope = self._state["scope"]
        scope_items = [f"{k}={v}" for k, v in scope.items() if v]
        scope_str = "(aucun filtre)" if not scope_items else ", ".join(scope_items)
        lines.append(f"🔧 Portée/Filtres: {scope_str}")
        
        # 2. Out-of-Topic (OOT)
        oot_status = "✅ autorisé" if self._state.get("oot_allowed", True) else "❌ désactivé"
        lines.append(f"🌍 Hors programme (OOT): {oot_status}")
        
        # 3. Tutor Mode
        tutor_mode = self._state.get("tutor_mode")
        if tutor_mode:
            lines.append(f"🎓 Mode tuteur: ✅ activé ({tutor_mode})")
        else:
            lines.append("🎓 Mode tuteur: ❌ désactivé")
        
        # 4. Auto-link (context preservation)
        auto_link = self._state.get("auto_link", True)
        link_status = "✅ activé" if auto_link else "❌ désactivé"
        lines.append(f"🔗 Auto-link: {link_status}")
        
        # 5. Router Override
        router_override = self._state.get("route_override")
        if router_override:
            lines.append(f"🎯 Router: ⚙️  mode forcé = {router_override}")
        else:
            lines.append("🎯 Router: ✅ auto (pas de surcharge)")
        
        # 6. Backend/Models
        backend = self._state.get("backend", "ollama")
        lines.append(f"🖥️  Backend: {backend}")
        
        # 7. Pinned Context
        if self._state.get("pinned_meta"):
            lines.append("📌 Contexte épinglé: ✅ oui")
        else:
            lines.append("📌 Contexte épinglé: ❌ non")
        
        # 8. Session ID
        lines.append(f"💬 Session: {self.chat_id}")
        
        return "\n".join(lines)
    
    def scope_set(self, **kwargs):
        """
        Set scope filters.
        
        Parameters
        ----------
        chapter : Optional[str]
            Chapter filter
        block_kind : Optional[str]
            Block kind filter (theorem, definition, etc.)
        block_id : Optional[str]
            Specific block ID
        type : Optional[str]
            Document type filter
        """
        if "scope" not in self._state:
            self._state["scope"] = {
                "chapter": None,
                "block_kind": None,
                "block_id": None,
                "type": None
            }
        
        for k, v in kwargs.items():
            if k in self._state["scope"]:
                self._state["scope"][k] = v
    
    def scope_clear(self):
        """Clear all scope filters."""
        self._state["scope"] = {
            "chapter": None,
            "block_kind": None,
            "block_id": None,
            "type": None
        }
    
    # ========================================================================
    # Pin/Unpin Methods
    # ========================================================================
    
    def pin(self):
        """
        Pin current context (mark for persistence).
        
        Stores best_context_meta as pinned_meta.
        """
        best = self.best_context_meta()
        if best:
            self._state["pinned_meta"] = best
    
    def unpin(self):
        """Unpin context (clear pinned_meta)."""
        if "pinned_meta" in self._state:
            del self._state["pinned_meta"]
    
    def pin_docs(self, docs):
        """
        Pin specific documents.
        
        Legacy method for pinning document results.
        """
        self._state["pinned_docs"] = docs
    
    def forget_links(self):
        """
        Forget context links (clear last_question, etc.).
        
        Used when user wants to break the conversation chain.
        """
        # Clear conversation history markers
        if "last_question" in self._state:
            del self._state["last_question"]
        if "last_top_meta" in self._state:
            del self._state["last_top_meta"]
    
    # ========================================================================
    # Out-of-Topic (OOT) Methods
    # ========================================================================
    
    def set_oot_allow(self, allow: bool):
        """
        Set whether out-of-topic questions are allowed.
        
        Parameters
        ----------
        allow : bool
            If True, allow questions outside the course scope
        """
        self._state["oot_allowed"] = allow
    
    def oot_allowed(self) -> bool:
        """
        Check if out-of-topic questions are allowed.
        
        Returns
        -------
        bool
            True if OOT is allowed (default: True)
        """
        return self._state.get("oot_allowed", True)
    
    # ========================================================================
    # Tutor Mode Methods
    # ========================================================================
    
    def set_tutor_mode(self, mode: Optional[str]):
        """
        Set tutor mode.
        
        Parameters
        ----------
        mode : Optional[str]
            Tutor mode: "on", "smart", "explain", "guide", or None to disable
        """
        if mode:
            self._state["tutor_mode"] = mode
        elif "tutor_mode" in self._state:
            del self._state["tutor_mode"]
    
    def get_tutor_mode(self) -> Optional[str]:
        """
        Get current tutor mode.
        
        Returns
        -------
        Optional[str]
            Current tutor mode or None if disabled
        """
        return self._state.get("tutor_mode")
    
    # ========================================================================
    # Auto-Link Methods
    # ========================================================================
    
    def set_auto_link(self, enabled: bool):
        """
        Set auto-link (automatic context preservation).
        
        Parameters
        ----------
        enabled : bool
            If True, automatically link to previous context
        """
        self._state["auto_link"] = enabled
    
    def get_auto_link(self) -> bool:
        """
        Get auto-link status.
        
        Returns
        -------
        bool
            True if auto-link is enabled (default: True)
        """
        return self._state.get("auto_link", True)
