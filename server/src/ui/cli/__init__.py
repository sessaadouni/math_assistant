# -*- coding: utf-8 -*-
"""
src/ui/cli/__init__.py
Package CLI pour l'assistant RAG de maths
"""

from .app import main
from .styles import (
    GITHUB_DARK_THEME,
    console,
    CLIFormatter,
)

__all__ = [
    'main',
    'GITHUB_DARK_THEME',
    'console',
    'CLIFormatter',
]