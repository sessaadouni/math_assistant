# -*- coding: utf-8 -*-
"""
src/ui/gui/__init__.py
Package GUI pour l'assistant RAG de maths
"""

from .app import main, MainWindow
from .widgets import (
    AnswerViewer,
    SourcesTable,
    ScopeWidget,
    OptionsWidget,
    ActionsWidget,
    QueryInputWidget,
    SectionLabel,
)
from .styles import GLOBAL_STYLE, KATEX_HTML_TEMPLATE, ICONS

__all__ = [
    # Main app
    'main',
    'MainWindow',
    # Widgets
    'AnswerViewer',
    'SourcesTable',
    'ScopeWidget',
    'OptionsWidget',
    'ActionsWidget',
    'QueryInputWidget',
    'SectionLabel',
    # Styles
    'GLOBAL_STYLE',
    'KATEX_HTML_TEMPLATE',
    'ICONS',
]