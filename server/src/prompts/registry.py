"""
PromptRegistry - Factory for prompt templates

This registry provides centralized access to all prompt templates
following the Factory and Registry patterns.
"""

from typing import Dict, Optional
from .base import BasePrompt


class PromptRegistry:
    """
    Registry for prompt templates.
    
    This class implements the Factory pattern to provide
    centralized access to all prompt templates.
    
    Usage:
        registry = PromptRegistry()
        prompt = registry.get("qa")
        formatted = prompt.format(question="...", context="...")
    """
    
    def __init__(self):
        self._prompts: Dict[str, BasePrompt] = {}
        self._default_task = "qa"
    
    def register(self, task: str, prompt: BasePrompt) -> None:
        """
        Register a prompt for a task.
        
        Args:
            task: Task identifier (e.g., "qa", "course_build")
            prompt: Prompt instance
        """
        self._prompts[task] = prompt
    
    def get(self, task: str) -> BasePrompt:
        """
        Get prompt for a task.
        
        Args:
            task: Task identifier
            
        Returns:
            Prompt instance
            
        Raises:
            KeyError: If task not found and no default available
        """
        if task in self._prompts:
            return self._prompts[task]
        
        # Fallback to default
        if self._default_task in self._prompts:
            return self._prompts[self._default_task]
        
        raise KeyError(f"No prompt registered for task '{task}' and no default available")
    
    def get_with_doc_type(self, task: str) -> tuple[BasePrompt, str]:
        """
        Get prompt and its default document type.
        
        Args:
            task: Task identifier
            
        Returns:
            Tuple of (prompt, default_doc_type)
        """
        prompt = self.get(task)
        doc_type = prompt.get_default_doc_type()
        return prompt, doc_type
    
    def has(self, task: str) -> bool:
        """
        Check if task is registered.
        
        Args:
            task: Task identifier
            
        Returns:
            True if registered
        """
        return task in self._prompts
    
    def list_tasks(self) -> list[str]:
        """
        List all registered tasks.
        
        Returns:
            List of task identifiers
        """
        return list(self._prompts.keys())
    
    def set_default_task(self, task: str) -> None:
        """
        Set default task for fallback.
        
        Args:
            task: Task identifier
        """
        if task not in self._prompts:
            raise KeyError(f"Cannot set default to unregistered task '{task}'")
        self._default_task = task


# Global registry instance
_default_registry: Optional[PromptRegistry] = None


def get_default_registry() -> PromptRegistry:
    """
    Get the default global prompt registry.
    
    This function creates and populates the registry on first call.
    
    Returns:
        Default PromptRegistry instance
    """
    global _default_registry
    
    if _default_registry is None:
        _default_registry = PromptRegistry()
        _populate_registry(_default_registry)
    
    return _default_registry


def _populate_registry(registry: PromptRegistry) -> None:
    """
    Populate registry with all available prompts.
    
    This function imports and registers all prompt implementations.
    
    Args:
        registry: Registry to populate
    """
    # Import all prompt modules
    from .qa import ProfessorPrompt, TutorPrompt
    from .course import (
        CourseBuildPrompt,
        CourseExplainPrompt,
        CourseSummaryPrompt,
        SheetCreatePrompt,
        SheetReviewPrompt,
    )
    from .exercises import (
        ExerciseGeneratorPrompt,
        ExerciseSolverPrompt,
        ExerciseCorrectorPrompt,
    )
    from .exams import (
        ExamGeneratorPrompt,
        ExamCorrectorPrompt,
        QCMPrompt,
        KhollePrompt,
    )
    from .utilities import (
        FormulaPrompt,
        TheoremPrompt,
        ProofPrompt,
    )
    
    # Register Q&A prompts
    registry.register("qa", ProfessorPrompt())
    registry.register("tutor", TutorPrompt())
    
    # Register course prompts
    registry.register("course_build", CourseBuildPrompt())
    registry.register("course_explain", CourseExplainPrompt())
    registry.register("course_summary", CourseSummaryPrompt())
    registry.register("sheet_create", SheetCreatePrompt())
    registry.register("sheet_review", SheetReviewPrompt())
    
    # Register exercise prompts
    registry.register("exercise_gen", ExerciseGeneratorPrompt())
    registry.register("solver", ExerciseSolverPrompt())
    registry.register("exo_corrector", ExerciseCorrectorPrompt())
    
    # Register exam prompts
    registry.register("exam", ExamGeneratorPrompt())
    registry.register("exam_corrector", ExamCorrectorPrompt())
    registry.register("qcm", QCMPrompt())
    registry.register("kholle", KhollePrompt())
    
    # Register utility prompts
    registry.register("formula", FormulaPrompt())
    registry.register("theorem", TheoremPrompt())
    registry.register("proof", ProofPrompt())
    
    # Set default
    registry.set_default_task("qa")


def reset_registry() -> None:
    """
    Reset the global registry.
    
    Useful for testing.
    """
    global _default_registry
    _default_registry = None
