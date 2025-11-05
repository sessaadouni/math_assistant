"""
Base Prompt Classes

Defines abstract base classes and utilities for prompt templates.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate


class BasePrompt(ABC):
    """
    Abstract base class for all prompts.
    
    Each prompt subclass represents a specific task template.
    """
    
    def __init__(self, template: ChatPromptTemplate):
        """
        Initialize prompt with template.
        
        Args:
            template: LangChain ChatPromptTemplate
        """
        self._template = template
    
    @property
    def template(self) -> ChatPromptTemplate:
        """Get the template"""
        return self._template
    
    @abstractmethod
    def get_task_name(self) -> str:
        """
        Get the task name for this prompt.
        
        Returns:
            Task name (e.g., "qa", "course_build", etc.)
        """
        pass
    
    @abstractmethod
    def get_default_doc_type(self) -> str:
        """
        Get default document type filter for this prompt.
        
        Returns:
            Document type ("cours", "td", "exam", etc.)
        """
        pass
    
    def format(self, **kwargs) -> str:
        """
        Format the prompt with variables.
        
        Args:
            **kwargs: Template variables
            
        Returns:
            Formatted prompt string
        """
        return self._template.format(**kwargs)
    
    def get_required_variables(self) -> list[str]:
        """
        Get list of required variables for this prompt.
        
        Returns:
            List of variable names
        """
        return list(self._template.input_variables)
    
    def validate_variables(self, **kwargs) -> bool:
        """
        Validate that all required variables are provided.
        
        Args:
            **kwargs: Variables to validate
            
        Returns:
            True if valid, False otherwise
        """
        required = set(self.get_required_variables())
        provided = set(kwargs.keys())
        return required.issubset(provided)


class QAPrompt(BasePrompt):
    """Base class for Q&A prompts"""
    
    def get_default_doc_type(self) -> str:
        return "cours"


class CoursePrompt(BasePrompt):
    """Base class for course-related prompts"""
    
    def get_default_doc_type(self) -> str:
        return "cours"


class ExercisePrompt(BasePrompt):
    """Base class for exercise-related prompts"""
    
    def get_default_doc_type(self) -> str:
        return "td"


class ExamPrompt(BasePrompt):
    """Base class for exam-related prompts"""
    
    def get_default_doc_type(self) -> str:
        return "exam"


class UtilityPrompt(BasePrompt):
    """Base class for utility prompts (formula, theorem, proof)"""
    
    def get_default_doc_type(self) -> str:
        return "cours"
