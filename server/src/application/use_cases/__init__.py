"""
Application Layer - Use Cases

Business logic orchestration using domain entities and infrastructure services.
"""

# Q&A Use Cases
from .answer_question import AnswerQuestionUseCase

# Course Use Cases
from .explain_course import ExplainCourseUseCase
from .build_course import BuildCourseUseCase
from .summarize_course import SummarizeCourseUseCase

# Exercise Use Cases
from .generate_exercise import GenerateExerciseUseCase
from .sheets_and_exercises import (
    CreateSheetUseCase,
    ReviewSheetUseCase,
    SolveExerciseUseCase,
    CorrectExerciseUseCase,
)

# Exam Use Cases
from .exams_and_assessments import (
    GenerateExamUseCase,
    CorrectExamUseCase,
    GenerateQCMUseCase,
    GenerateKholleUseCase,
)

# Utility Use Cases
from .explain_theorem import ExplainTheoremUseCase
from .utilities import (
    ExplainFormulaUseCase,
    ProveStatementUseCase,
)

__all__ = [
    # Q&A
    "AnswerQuestionUseCase",
    # Course
    "ExplainCourseUseCase",
    "BuildCourseUseCase",
    "SummarizeCourseUseCase",
    # Sheets
    "CreateSheetUseCase",
    "ReviewSheetUseCase",
    # Exercises
    "GenerateExerciseUseCase",
    "SolveExerciseUseCase",
    "CorrectExerciseUseCase",
    # Exams
    "GenerateExamUseCase",
    "CorrectExamUseCase",
    "GenerateQCMUseCase",
    "GenerateKholleUseCase",
    # Utilities
    "ExplainTheoremUseCase",
    "ExplainFormulaUseCase",
    "ProveStatementUseCase",
]
