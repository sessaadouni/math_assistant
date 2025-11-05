"""
MathAssistant Facade - Unified API for all math assistant operations

This facade provides a single entry point to all math assistant use cases,
maintaining backward compatibility while using clean SOLID architecture.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ...domain.entities import Question, Answer
from ...domain.value_objects import Filters, SessionContext
from ...config.di_container import DIContainer


class MathAssistantFacade:
    """
    Facade for the Math Assistant system.
    
    This class provides a unified, simple API for all math assistant operations.
    It orchestrates all use cases and maintains session state.
    
    Architecture:
    -------------
    - Delegates to specialized use cases (SOLID Single Responsibility)
    - Uses dependency injection for all services
    - Maintains session context for conversational flow
    - Provides backward-compatible API
    
    Usage:
    ------
    >>> assistant = MathAssistantFacade()
    >>> response = assistant.ask("C'est quoi la convergence uniforme ?", chapter="5")
    >>> print(response["answer"])
    
    >>> exercises = assistant.generate_exercises("séries de Fourier", count=3)
    >>> print(exercises["answer"])
    """
    
    def __init__(self, container: Optional[DIContainer] = None):
        """
        Initialize the Math Assistant Facade.
        
        Parameters
        ----------
        container : Optional[DIContainer]
            Dependency injection container (creates default if None)
        """
        self.container = container or DIContainer()
        
        # Get session store from container
        self._session_store = self.container.get_session_store()
        
        # Default chat_id
        self._chat_id = "default"
        
        # Cache use cases for performance
        self._use_cases: Dict[str, Any] = {}
    
    @property
    def session_context(self):
        """
        Get current session context from SessionStore.
        
        This ensures we always use the up-to-date context that
        includes conversation history updated by use cases.
        """
        return self._session_store.get_context(self._chat_id)
    
    # ========================================================================
    # Q&A - Main entry point
    # ========================================================================
    
    def ask(
        self,
        question: str,
        chapter: Optional[str] = None,
        block_kind: Optional[str] = None,
        block_id: Optional[str] = None,
        doc_type: Optional[str] = None,
        auto_link: bool = True,
        debug: bool = False,
        router_mode: Optional[str] = None,
        progress_callback: Optional[callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main Q&A entry point - ask any question.
        
        Parameters
        ----------
        question : str
            The question to ask
        chapter : Optional[str]
            Filter by chapter
        block_kind : Optional[str]
            Filter by block kind (theorem, definition, etc.)
        block_id : Optional[str]
            Filter by specific block ID
        doc_type : Optional[str]
            Filter by document type
        auto_link : bool
            Whether to link to previous context (default: True)
        debug : bool
            Enable debug mode (default: False)
            
        Returns
        -------
        Dict[str, Any]
            Response with keys: answer (str), sources (List), metadata (Dict)
        
        Examples
        --------
        >>> assistant = MathAssistantFacade()
        >>> result = assistant.ask("Qu'est-ce qu'une série de Fourier ?", chapter="8")
        >>> print(result["answer"])
        """
        use_case = self._get_use_case("answer_question")
        
        # Build filters
        filters = Filters(
            chapter=chapter,
            block_kind=block_kind,
            block_id=block_id,
            type=doc_type
        ) if any([chapter, block_kind, block_id, doc_type]) else None
        
        # Execute use case
        # NOTE: AnswerQuestionUseCase uses direct parameters, not a Request dataclass
        answer = use_case.execute(
            question_text=question,
            chat_id=self.session_context.chat_id,
            filters=filters,
            auto_link=auto_link,
            debug=debug,
            force_router_mode=router_mode,
            progress_callback=progress_callback
        )
        
        # Return as dict for backward compatibility
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Course Operations
    # ========================================================================
    
    def explain_course(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a pedagogical explanation of a course topic.
        
        Parameters
        ----------
        topic : str
            The topic to explain
        level : str
            Education level (default: "prépa/terminale+")
        chapter : Optional[str]
            Filter by chapter
            
        Returns
        -------
        Dict[str, Any]
            Explanation with examples, FAQ, and references
        """
        use_case = self._get_use_case("explain_course")
        
        from ..use_cases.explain_course import ExplainCourseRequest
        request = ExplainCourseRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def build_course(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build complete course content on a topic."""
        use_case = self._get_use_case("build_course")
        
        from ..use_cases.build_course import BuildCourseRequest
        request = BuildCourseRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def summarize_course(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a concise course summary with key points."""
        use_case = self._get_use_case("summarize_course")
        
        from ..use_cases.summarize_course import SummarizeCourseRequest
        request = SummarizeCourseRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Sheet Operations
    # ========================================================================
    
    def create_sheet(
        self,
        topic: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a revision sheet."""
        use_case = self._get_use_case("create_sheet")
        
        from ..use_cases.sheets_and_exercises import CreateSheetRequest
        request = CreateSheetRequest(
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def review_sheet(
        self,
        sheet_text: str,
        topic: str,
        level: str = "prépa/terminale+",
        **kwargs
    ) -> Dict[str, Any]:
        """Review a student's revision sheet."""
        use_case = self._get_use_case("review_sheet")
        
        from ..use_cases.sheets_and_exercises import ReviewSheetRequest
        request = ReviewSheetRequest(
            sheet_text=sheet_text,
            topic=topic,
            level=level,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Exercise Operations
    # ========================================================================
    
    def generate_exercises(
        self,
        topic: str,
        count: int = 4,
        level: str = "prépa/terminale+",
        difficulty: str = "mixte",
        with_solutions: bool = True,
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate exercises on a topic.
        
        Parameters
        ----------
        topic : str
            Topic for exercises
        count : int
            Number of exercises (default: 4)
        level : str
            Education level
        difficulty : str
            "facile", "moyen", "difficile", or "mixte"
        with_solutions : bool
            Include solutions (default: True)
        chapter : Optional[str]
            Filter by chapter
            
        Returns
        -------
        Dict[str, Any]
            Generated exercises
        """
        use_case = self._get_use_case("generate_exercise")
        
        from ..use_cases.generate_exercise import GenerateExerciseRequest
        request = GenerateExerciseRequest(
            topic=topic,
            count=count,
            level=level,
            difficulty=difficulty,
            with_solutions=with_solutions,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def solve_exercise(
        self,
        statement: str,
        topic: Optional[str] = None,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Solve an exercise step by step."""
        use_case = self._get_use_case("solve_exercise")
        
        from ..use_cases.sheets_and_exercises import SolveExerciseRequest
        request = SolveExerciseRequest(
            statement=statement,
            topic=topic,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def correct_exercise(
        self,
        statement: str,
        student_answer: str,
        points: int = 10,
        level: str = "prépa/terminale+",
        **kwargs
    ) -> Dict[str, Any]:
        """Correct a student's exercise answer."""
        use_case = self._get_use_case("correct_exercise")
        
        from ..use_cases.sheets_and_exercises import CorrectExerciseRequest
        request = CorrectExerciseRequest(
            statement=statement,
            student_answer=student_answer,
            points=points,
            level=level,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Exam Operations
    # ========================================================================
    
    def generate_exam(
        self,
        chapters: str,
        duration: str = "2h",
        total_points: int = 20,
        level: str = "prépa",
        difficulty: str = "mixte",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a complete exam."""
        use_case = self._get_use_case("generate_exam")
        
        from ..use_cases.exams_and_assessments import GenerateExamRequest
        request = GenerateExamRequest(
            chapters=chapters,
            duration=duration,
            total_points=total_points,
            level=level,
            difficulty=difficulty,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def correct_exam(
        self,
        student_answer: str,
        exam_statement: str,
        points: int = 20,
        level: str = "prépa",
        **kwargs
    ) -> Dict[str, Any]:
        """Correct an exam with detailed grading."""
        use_case = self._get_use_case("correct_exam")
        
        from ..use_cases.exams_and_assessments import CorrectExamRequest
        request = CorrectExamRequest(
            student_answer=student_answer,
            exam_statement=exam_statement,
            points=points,
            level=level,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def generate_qcm(
        self,
        topic: str,
        num_questions: int = 12,
        level: str = "prépa",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a QCM (multiple choice quiz)."""
        use_case = self._get_use_case("generate_qcm")
        
        from ..use_cases.exams_and_assessments import GenerateQCMRequest
        request = GenerateQCMRequest(
            topic=topic,
            num_questions=num_questions,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def generate_kholle(
        self,
        topic: str,
        duration: str = "20min",
        level: str = "prépa",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a kholle (oral exam)."""
        use_case = self._get_use_case("generate_kholle")
        
        from ..use_cases.exams_and_assessments import GenerateKholleRequest
        request = GenerateKholleRequest(
            topic=topic,
            duration=duration,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Utility Operations
    # ========================================================================
    
    def explain_theorem(
        self,
        theorem_name: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Explain a mathematical theorem.
        
        Parameters
        ----------
        theorem_name : str
            Name of the theorem
        level : str
            Education level
        chapter : Optional[str]
            Filter by chapter
            
        Returns
        -------
        Dict[str, Any]
            Detailed theorem explanation with examples
        """
        use_case = self._get_use_case("explain_theorem")
        
        from ..use_cases.explain_theorem import ExplainTheoremRequest
        request = ExplainTheoremRequest(
            theorem_name=theorem_name,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def explain_formula(
        self,
        query: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Explain a mathematical formula."""
        use_case = self._get_use_case("explain_formula")
        
        from ..use_cases.utilities import ExplainFormulaRequest
        request = ExplainFormulaRequest(
            query=query,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    def prove_statement(
        self,
        statement: str,
        level: str = "prépa/terminale+",
        chapter: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Provide a rigorous mathematical proof."""
        use_case = self._get_use_case("prove_statement")
        
        from ..use_cases.utilities import ProveStatementRequest
        request = ProveStatementRequest(
            statement=statement,
            level=level,
            filters=Filters(chapter=chapter) if chapter else None,
            session_context=self.session_context
        )
        
        answer = use_case.execute(request)
        return self._answer_to_dict(answer)
    
    # ========================================================================
    # Generic Task Execution (backward compatibility)
    # ========================================================================
    
    def run_task(
        self,
        task: str,
        question_or_payload: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a task by name (backward compatible API).
        
        This method provides backward compatibility with the old assistant API.
        It routes to the appropriate specialized method based on task name.
        
        Parameters
        ----------
        task : str
            Task name (qa, course_explain, exercise_gen, etc.)
        question_or_payload : str
            Question or main payload
        **kwargs
            Additional task-specific parameters
            
        Returns
        -------
        Dict[str, Any]
            Task result
            
        Examples
        --------
        >>> assistant = MathAssistantFacade()
        >>> result = assistant.run_task("qa", "Qu'est-ce qu'une limite ?", chapter="1")
        >>> result = assistant.run_task("exercise_gen", "intégrales", count=3)
        """
        # Map task names to methods
        task_mapping = {
            "qa": self.ask,
            "tutor": self.ask,
            "course_explain": lambda q, **kw: self.explain_course(q, **kw),
            "course_build": lambda q, **kw: self.build_course(q, **kw),
            "course_summary": lambda q, **kw: self.summarize_course(q, **kw),
            "sheet_create": lambda q, **kw: self.create_sheet(q, **kw),
            "sheet_review": lambda q, **kw: self.review_sheet(kwargs.get("sheet_text", ""), q, **kw),
            "exercise_gen": lambda q, **kw: self.generate_exercises(q, **kw),
            "solver": lambda q, **kw: self.solve_exercise(q, **kw),
            "exo_corrector": lambda q, **kw: self.correct_exercise(q, kwargs.get("student_answer", ""), **kw),
            "exam": lambda q, **kw: self.generate_exam(q, **kw),
            "exam_corrector": lambda q, **kw: self.correct_exam(kwargs.get("student_answer", ""), q, **kw),
            "qcm": lambda q, **kw: self.generate_qcm(q, **kw),
            "kholle": lambda q, **kw: self.generate_kholle(q, **kw),
            "theorem": lambda q, **kw: self.explain_theorem(q, **kw),
            "formula": lambda q, **kw: self.explain_formula(q, **kw),
            "proof": lambda q, **kw: self.prove_statement(q, **kw),
        }
        
        if task not in task_mapping:
            return {
                "answer": f"Tâche inconnue : {task}",
                "sources": [],
                "metadata": {"error": "unknown_task", "task": task}
            }
        
        return task_mapping[task](question_or_payload, **kwargs)
    
    # ========================================================================
    # Internal Helpers
    # ========================================================================
    
    def _get_use_case(self, name: str) -> Any:
        """Get or create use case instance (with caching)."""
        if name not in self._use_cases:
            getter_name = f"get_{name}_use_case"
            getter = getattr(self.container, getter_name)
            self._use_cases[name] = getter()
        return self._use_cases[name]
    
    def _answer_to_dict(self, answer: Answer) -> Dict[str, Any]:
        """Convert Answer entity to dictionary."""
        # Build metadata from Answer attributes
        metadata = {
            "answer_id": answer.id,
            "question_id": answer.question_id,
            "chat_id": answer.chat_id,
            "created_at": answer.created_at.isoformat() if answer.created_at else None,
        }
        
        # Add optional metadata
        if answer.task_type:
            metadata["task"] = answer.task_type
        if answer.model_used:
            metadata["model_used"] = answer.model_used
        if answer.execution_time:
            metadata["execution_time"] = answer.execution_time
        if answer.context:
            metadata["num_sources"] = len(answer.context.sources)
            metadata["retrieval_time"] = getattr(answer.context, "retrieval_time", None)
        
        # Return DOCUMENTS (not Source objects) for backward compatibility
        # Legacy code expects Document objects with .to_source() method
        documents = answer.context.documents if answer.context else []
        
        return {
            "answer": answer.text,
            "sources": documents,  # Return Document objects, not Source objects
            "metadata": metadata
        }
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def new_session(self, session_id: Optional[str] = None):
        """
        Start a new session.
        
        Parameters
        ----------
        session_id : Optional[str]
            Session ID (uses "default" if None)
        """
        new_id = session_id or "default"
        
        # Clear old session if exists
        if self._session_store.exists(self._chat_id):
            self._session_store.clear_context(self._chat_id)
        
        # Set new chat_id
        self._chat_id = new_id
        
        # Get or create new context (SessionStore will create if not exists)
        _ = self._session_store.get_context(self._chat_id)
    
    def get_session_id(self) -> str:
        """Get current session ID."""
        return self._chat_id


# ============================================================================
# Global singleton instance
# ============================================================================

_global_assistant: Optional[MathAssistantFacade] = None


def get_assistant() -> MathAssistantFacade:
    """
    Get global MathAssistant instance (singleton pattern).
    
    This provides backward compatibility with the old API.
    
    Returns
    -------
    MathAssistantFacade
        Global assistant instance
        
    Examples
    --------
    >>> from src.application.facades import get_assistant
    >>> assistant = get_assistant()
    >>> result = assistant.ask("Qu'est-ce qu'une dérivée ?")
    """
    global _global_assistant
    if _global_assistant is None:
        _global_assistant = MathAssistantFacade()
    return _global_assistant


def reset_assistant():
    """Reset global assistant (useful for testing)."""
    global _global_assistant
    _global_assistant = None
