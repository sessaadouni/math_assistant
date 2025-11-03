# -*- coding: utf-8 -*-
"""
src/ui/gui/styles.py
Styles Qt modernes pour l'interface GUI (GitHub Dark inspired)
"""

# Style global de l'application (GitHub Dark theme)
GLOBAL_STYLE = """
QMainWindow {
    background-color: #0d1117;
}

QWidget {
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* ===== Sidebar ===== */
QFrame#sidebar {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

/* ===== Labels ===== */
QLabel {
    color: #e6edf3;
    padding: 2px;
}

QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    padding: 12px 0;
}

QLabel#section_label {
    color: #8b949e;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 16px;
    margin-bottom: 8px;
}

/* ===== Line Edits ===== */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border: 1px solid #388bfd;
    outline: none;
    background-color: #010409;
}
QLineEdit:hover {
    border-color: #484f58;
}
QLineEdit:disabled {
    background-color: #161b22;
    color: #6e7681;
    border-color: #21262d;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    min-height: 20px;
}
QComboBox:hover {
    border-color: #484f58;
    background-color: #161b22;
}
QComboBox:focus {
    border: 1px solid #388bfd;
    background-color: #010409;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b949e;
    margin-right: 8px;
}
QComboBox::down-arrow:hover {
    border-top-color: #e6edf3;
}
QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    color: #e6edf3;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 4px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #21262d;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    color: #e6edf3;
    font-weight: 500;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #484f58;
}
QPushButton:pressed {
    background-color: #161b22;
    transform: translateY(1px);
}
QPushButton:disabled {
    background-color: #161b22;
    color: #6e7681;
    border-color: #21262d;
}

/* Primary Button (Bouton Envoyer) */
QPushButton#btnSend {
    background-color: #238636;
    border-color: #2ea043;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#btnSend:hover {
    background-color: #2ea043;
    border-color: #3fb950;
    box-shadow: 0 0 0 3px rgba(35, 134, 54, 0.15);
}
QPushButton#btnSend:pressed {
    background-color: #1f7a2f;
}
QPushButton#btnSend:disabled {
    background-color: #161b22;
    border-color: #21262d;
    color: #6e7681;
}

/* Danger Button */
QPushButton#btnDanger {
    background-color: #da3633;
    border-color: #f85149;
    color: #ffffff;
}
QPushButton#btnDanger:hover {
    background-color: #f85149;
    border-color: #ff7b72;
}

/* ===== Checkboxes ===== */
QCheckBox {
    spacing: 8px;
    color: #e6edf3;
    padding: 6px 4px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #30363d;
    background-color: #0d1117;
}
QCheckBox::indicator:hover {
    border-color: #484f58;
    background-color: #161b22;
}
QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
    image: none;
}
QCheckBox::indicator:checked:hover {
    background-color: #388bfd;
    border-color: #388bfd;
}
QCheckBox:disabled {
    color: #6e7681;
}
QCheckBox::indicator:disabled {
    background-color: #161b22;
    border-color: #21262d;
}

/* ===== Table Widget ===== */
QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #e6edf3;
}
QTableWidget::item {
    padding: 10px 12px;
    border-bottom: 1px solid #21262d;
}
QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}
QTableWidget::item:hover {
    background-color: #161b22;
}
QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    border: none;
    border-bottom: 2px solid #30363d;
    padding: 10px 12px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}
QHeaderView::section:hover {
    background-color: #21262d;
}

/* ===== Text Browser ===== */
QTextBrowser {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px;
    color: #e6edf3;
    line-height: 1.6;
}

/* ===== Tabs ===== */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px;
    background: #0d1117;
}
QTabBar::tab {
    background: #161b22;
    border: 1px solid #30363d;
    padding: 8px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    color: #8b949e;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #0d1117;
    color: #e6edf3;
    border-bottom-color: #0d1117;
}
QTabBar::tab:hover {
    color: #e6edf3;
}

/* ===== Toolbar (AnswerToolbar & QuickTaskBar) ===== */
QFrame#toolbar {
    background-color: transparent;
}
QFrame#toolbar QPushButton[isChip="true"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 999px;
    padding: 6px 12px;
    font-weight: 600;
}
QFrame#toolbar QPushButton[isChip="true"]:hover {
    background: #21262d;
}

/* ===== Command Palette ===== */
QFrame#palette_overlay {
    background: rgba(0,0,0,0.45);
}
QFrame#palette_box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 12px;
}
QLineEdit#palette_input {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 10px 12px;
    color: #e6edf3;
    font-size: 14px;
}
QListWidget#palette_list {
    background-color: #0d1117;
    border: none;
    color: #e6edf3;
}
QListWidget#palette_list::item {
    padding: 10px 8px;
    border-radius: 6px;
}
QListWidget#palette_list::item:selected {
    background: #161b22;
}

/* ===== Scrollbars ===== */
QScrollBar:vertical {
    background-color: #0d1117;
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}
QScrollBar::handle:vertical:pressed {
    background-color: #6e7681;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 14px;
    border-radius: 7px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}
QScrollBar::handle:horizontal:hover { background-color: #484f58; }
QScrollBar::handle:horizontal:pressed { background-color: #6e7681; }
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal { width: 0px; }
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal { background: none; }

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
    padding: 6px 12px;
}
QStatusBar::item { border: none; }

/* ===== Separators ===== */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #30363d;
}

/* ===== Tooltips ===== */
QToolTip {
    background-color: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #161b22;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding: 4px;
}
QMenuBar::item {
    padding: 6px 12px;
    border-radius: 6px;
}
QMenuBar::item:selected { background-color: #21262d; }
QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

/* ===== Splitter ===== */
QSplitter::handle { background-color: #30363d; }
QSplitter::handle:hover { background-color: #484f58; }
QSplitter::handle:pressed { background-color: #6e7681; }
"""

# Template HTML pour KaTeX (rendu LaTeX)
KATEX_HTML_TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" 
          integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" 
          crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" 
            integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" 
            crossorigin="anonymous"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" 
            integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" 
            crossorigin="anonymous"></script>
    <style>
        :root {{ color-scheme: dark; }}
        body {{ 
            margin: 0; padding: 20px 24px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0d1117; color: #e6edf3; line-height: 1.7; font-size: 14px;
        }}
        .bubble {{ 
            background: #161b22; border: 1px solid #30363d; border-radius: 12px; 
            padding: 20px 24px; box-shadow: 0 8px 24px rgba(0,0,0,.4); max-width: 100%;
        }}
        h1, h2, h3 {{ color: #ffffff; margin-top: 24px; margin-bottom: 12px; font-weight: 600; }}
        h1 {{ font-size: 28px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
        h2 {{ font-size: 22px; }} h3 {{ font-size: 18px; }}
        p {{ margin: 12px 0; }}
        code {{ background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 2px 6px; 
               font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; 
               font-size: 13px; color: #f0883e; }}
        pre {{ background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; overflow-x: auto; margin: 16px 0; }}
        pre code {{ background: none; border: none; padding: 0; color: #e6edf3; }}
        .katex {{ font-size: 1.6em; }}
        .katex-display {{ margin: 20px 0; overflow-x: auto; overflow-y: hidden; font-size: 1.8em; }}
        strong, b {{ color: #ffffff; font-weight: 600; }}
        em, i {{ color: #79c0ff; font-style: italic; }}
        hr {{ border: none; border-top: 1px solid #30363d; margin: 24px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #161b22; font-weight: 600; }}
        ul, ol {{ margin: 12px 0; padding-left: 28px; }} li {{ margin: 6px 0; }}
        a {{ color: #58a6ff; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
        blockquote {{ border-left: 4px solid #30363d; margin: 16px 0; padding-left: 16px; color: #8b949e; }}
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '$', right: '$', display: false}},
                    {{left: '\\\\[', right: '\\\\]', display: true}},
                    {{left: '\\\\(', right: '\\\\)', display: false}}
                ],
                throwOnError: false,
                trust: true
            }});
        }});
    </script>
</head>
<body>
    <div class="bubble">{html}</div>
</body>
</html>"""

# Icônes Unicode
ICONS = {
    'pin': '📌',
    'unpin': '📍',
    'new_chat': '🆕',
    'forget': '🧹',
    'save': '💾',
    'send': '📤',
    'scope': '🎯',
    'options': '⚙️',
    'actions': '⚡',
    'sources': '📚',
    'search': '🔍',
    # Ajouts pour tabs / chips / palette
    'fiche': '🗂️',
    'qcm': '📝',
    'exam': '🧪',
    'tutor': '🧭',
    'formula': '∑',
    'summary': '🧾',
    'course': '📘',
    'palette': '⌘',
}
