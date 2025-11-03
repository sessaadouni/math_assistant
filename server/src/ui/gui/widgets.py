# -*- coding: utf-8 -*-
"""
src/ui/gui/widgets.py
Widgets réutilisables pour l'interface GUI
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
import re

from PySide6 import QtCore, QtGui, QtWidgets

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

from .styles import KATEX_HTML_TEMPLATE, ICONS

# Import des utilitaires de traitement de texte
from src.utils import truncate_text, clean_text, extract_latex_formulas, escape_latex_in_text, restore_latex_formulas


# ===== HELPER FUNCTIONS =====

def markdown_to_html_with_latex(markdown: str) -> str:
    """
    Convertit Markdown en HTML en préservant parfaitement le LaTeX pour KaTeX.
    Version optimisée pour l'affichage avec KaTeX auto-render.
    """
    # Étape 1: Extraire et remplacer temporairement le LaTeX
    text, latex_replacements = escape_latex_in_text(markdown, placeholder="§§§LATEX{}§§§")

    lines = text.splitlines()
    html_lines = []
    in_code_block = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                html_lines.append('<pre><code>')
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line)  # Pas d'échappement dans les code blocks
            continue

        # Headers
        if stripped.startswith('### '):
            content = format_inline_markdown(stripped[4:])
            html_lines.append(f'<h3>{content}</h3>')
        elif stripped.startswith('## '):
            content = format_inline_markdown(stripped[3:])
            html_lines.append(f'<h2>{content}</h2>')
        elif stripped.startswith('# '):
            content = format_inline_markdown(stripped[2:])
            html_lines.append(f'<h1>{content}</h1>')

        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = format_inline_markdown(stripped[2:])
            html_lines.append(f'<li>{content}</li>')

        # Empty lines
        elif not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<br>')

        # Paragraphs
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = format_inline_markdown(line)
            html_lines.append(f'<p>{content}</p>')

    # Close any open tags
    if in_code_block:
        html_lines.append('</code></pre>')
    if in_list:
        html_lines.append('</ul>')

    html = '\n'.join(html_lines)

    # Étape 2: Restaurer le LaTeX
    html = restore_latex_formulas(html, latex_replacements)

    return html


def format_inline_markdown(text: str) -> str:
    """Formate les éléments inline Markdown (gras, italique, code, liens)"""
    # Bold: **text** ou __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)

    # Italic: *text* ou _text_ (mais pas ** ou __)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)

    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    # Links: [text](url)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)

    return text


# ===== WIDGETS =====

class SectionLabel(QtWidgets.QLabel):
    """Label pour les titres de section dans la sidebar"""

    def __init__(self, text: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("section_label")


class AnswerViewer(QtWidgets.QWidget):
    """Widget pour afficher les réponses de l'assistant (avec KaTeX si possible)"""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Utiliser WebEngine si disponible, sinon TextBrowser
        if WEBENGINE_AVAILABLE:
            self.view = QWebEngineView()
            self._use_katex = True
        else:
            self.view = QtWidgets.QTextBrowser()
            self.view.setOpenExternalLinks(True)
            self._use_katex = False

        layout.addWidget(self.view)

        self._last_markdown: str = ""
        self._last_html: str = ""

        # Message de bienvenue
        self.show_welcome()

    def show_welcome(self):
        """Afficher un message de bienvenue"""
        welcome_md = """# 🎓 Bienvenue dans l'Assistant Math RAG v3.1

Posez vos questions sur les mathématiques et je vous aiderai en m'appuyant sur le manuel de référence.

**Fonctionnalités :**
- 🔍 Recherche sémantique avancée dans le PDF
- 📚 Citations des sources utilisées
- 🎯 Filtrage par type de contenu (exercice, théorie, méthode...)
- 📌 Mémorisation du contexte pour des conversations suivies

**Pour commencer :**
1. Tapez votre question dans la zone de texte en bas
2. Optionnel : définissez une portée (chapitre, type...) dans la sidebar
3. Cliquez sur "Envoyer" ou appuyez sur Entrée

Exemple : *"Comment résoudre une équation du second degré ?"*
"""
        self.set_answer(welcome_md)

    def show_loading(self):
        """Afficher un message de chargement"""
        loading_md = "# 🔄 Recherche en cours...\n\nVeuillez patienter."
        self.set_answer(loading_md)

    def show_error(self, error_msg: str):
        """Afficher un message d'erreur"""
        error_md = f"# ❌ Erreur\n\n{error_msg}"
        self.set_answer(error_md)

    def set_answer(self, markdown: str):
        """Afficher une réponse en Markdown"""
        self._last_markdown = markdown or ""
        if self._use_katex:
            html_body = markdown_to_html_with_latex(markdown)
            full_html = KATEX_HTML_TEMPLATE.format(html=html_body)
            self._last_html = full_html
            self.view.setHtml(full_html)
        else:
            self._last_html = ""
            if isinstance(self.view, QtWidgets.QTextBrowser):
                self.view.setMarkdown(markdown)

    def clear(self):
        """Effacer le contenu"""
        self.show_welcome()

    # --- utilitaires export/copie ---
    def last_markdown(self) -> str:
        return self._last_markdown

    def last_html(self) -> str:
        return self._last_html

    def copy_markdown_to_clipboard(self):
        QtWidgets.QApplication.clipboard().setText(self._last_markdown or "")

    def copy_html_to_clipboard(self):
        QtWidgets.QApplication.clipboard().setText(self._last_html or "")

    def export_html(self, path: str):
        html = self._last_html or KATEX_HTML_TEMPLATE.format(html=markdown_to_html_with_latex(self._last_markdown))
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)


class AnswerToolbar(QtWidgets.QFrame):
    """Barre d'outils au-dessus de la réponse (copie, export, clear)"""

    def __init__(self, viewer: AnswerViewer, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        self.viewer = viewer

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 6, 6)
        layout.setSpacing(8)

        self.copy_md_btn = QtWidgets.QPushButton("Copier MD")
        self.copy_html_btn = QtWidgets.QPushButton("Copier HTML")
        self.export_html_btn = QtWidgets.QPushButton("Exporter HTML")
        self.clear_btn = QtWidgets.QPushButton("Effacer")

        for b in (self.copy_md_btn, self.copy_html_btn, self.export_html_btn, self.clear_btn):
            b.setProperty("isChip", True)

        layout.addWidget(self.copy_md_btn)
        layout.addWidget(self.copy_html_btn)
        layout.addWidget(self.export_html_btn)
        layout.addStretch(1)
        layout.addWidget(self.clear_btn)

        # actions
        self.copy_md_btn.clicked.connect(self.viewer.copy_markdown_to_clipboard)
        self.copy_html_btn.clicked.connect(self.viewer.copy_html_to_clipboard)
        self.export_html_btn.clicked.connect(self._choose_export)
        self.clear_btn.clicked.connect(self.viewer.clear)

    def _choose_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exporter la réponse en HTML", "reponse.html", "HTML (*.html);;Tous les fichiers (*)"
        )
        if path:
            self.viewer.export_html(path)


class QuickTaskBar(QtWidgets.QFrame):
    """Barre de chips pour insérer des slash-commands rapidement"""

    insert_text = QtCore.Signal(str)  # émet le texte à insérer dans l’input

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)

        chips = [
            (f"{ICONS['fiche']} Fiche", "/fiche "),
            (f"{ICONS['qcm']} QCM", "/qcm "),
            (f"{ICONS['exam']} Examen", "/exam "),
            (f"{ICONS['tutor']} Tutor", "/tutor "),
            (f"{ICONS['formula']} Formule", "/formule "),
            (f"{ICONS['summary']} Résumé", "/resume "),
            (f"{ICONS['course']} Cours", "/cours "),
        ]

        for label, payload in chips:
            btn = QtWidgets.QPushButton(label)
            btn.setProperty("isChip", True)
            btn.clicked.connect(lambda _, p=payload: self.insert_text.emit(p))
            layout.addWidget(btn)

        layout.addStretch(1)


class SourcesTable(QtWidgets.QTableWidget):
    """Tableau pour afficher les sources utilisées"""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(0, 5, parent)

        # Configuration des colonnes
        self.setHorizontalHeaderLabels([
            "#", "Bloc", "Chap/Sec", "Page", "Aperçu"
        ])

        # Styles
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.verticalHeader().setVisible(False)

        # Largeurs des colonnes
        self.setColumnWidth(0, 40)   # #
        self.setColumnWidth(1, 180)  # Bloc
        self.setColumnWidth(2, 100)  # Chap/Sec
        self.setColumnWidth(3, 60)   # Page

    def set_sources(self, documents: List[Any]):
        """Afficher les sources"""
        self.setRowCount(0)

        for i, doc in enumerate(documents, start=1):
            self._add_source_row(i, doc)

        self.resizeColumnsToContents()

    def _add_source_row(self, index: int, doc: Any):
        """Ajouter une ligne pour une source"""
        row = self.rowCount()
        self.insertRow(row)

        # Extraire les métadonnées
        meta = getattr(doc, 'metadata', {})

        # Colonne #
        self.setItem(row, 0, QtWidgets.QTableWidgetItem(str(index)))

        # Colonne Bloc
        block_kind = meta.get('block_kind', '')
        block_id = meta.get('block_id', '')
        block_text = f"{block_kind} {block_id}".strip()
        if not block_text:
            block_text = meta.get('type', '?')
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(block_text))

        # Colonne Chap/Sec
        chapter = meta.get('chapter', '?')
        section = meta.get('section', '?')
        chapsec = f"{chapter} / {section}"
        self.setItem(row, 2, QtWidgets.QTableWidgetItem(chapsec))

        # Colonne Page
        page = str(meta.get('page', '?'))
        self.setItem(row, 3, QtWidgets.QTableWidgetItem(page))

        # Colonne Aperçu
        content = getattr(doc, 'page_content', '')
        preview = truncate_text(content.replace('\n', ' '), max_length=140) if content else ''
        preview_item = QtWidgets.QTableWidgetItem(preview)
        preview_item.setToolTip(truncate_text(content, max_length=500))
        self.setItem(row, 4, preview_item)

    def clear(self):
        """Effacer toutes les sources"""
        self.setRowCount(0)


class ScopeWidget(QtWidgets.QWidget):
    """Widget pour définir la portée de recherche"""

    scope_applied = QtCore.Signal(str)  # Signal émis avec info de portée
    scope_cleared = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Champs de saisie
        self.chapter_input = QtWidgets.QLineEdit()
        self.chapter_input.setPlaceholderText("Chapitre (ex: 21)")

        self.block_kind_input = QtWidgets.QLineEdit()
        self.block_kind_input.setPlaceholderText("Block kind (théorème/définition...)")

        self.block_id_input = QtWidgets.QLineEdit()
        self.block_id_input.setPlaceholderText("Block id (ex: 21.52)")

        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems([
            "(aucun type)",
            "exercice",
            "méthode",
            "théorie",
            "cours"
        ])

        layout.addWidget(self.chapter_input)
        layout.addWidget(self.block_kind_input)
        layout.addWidget(self.block_id_input)
        layout.addWidget(self.type_combo)

        # Boutons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(8)

        self.apply_btn = QtWidgets.QPushButton("Appliquer")
        self.apply_btn.clicked.connect(self._apply)

        self.clear_btn = QtWidgets.QPushButton("Réinitialiser")
        self.clear_btn.clicked.connect(self._clear)

        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

    def _apply(self):
        """Appliquer la portée"""
        scope = self.get_scope()
        if not scope:
            return

        scope_str = ", ".join(f"{k}={v}" for k, v in scope.items())
        self.scope_applied.emit(scope_str)

    def _clear(self):
        """Réinitialiser la portée"""
        self.chapter_input.clear()
        self.block_kind_input.clear()
        self.block_id_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.scope_cleared.emit()

    def get_scope(self) -> Dict[str, str]:
        """Récupérer la portée définie"""
        scope = {}

        chapter = self.chapter_input.text().strip()
        if chapter:
            scope['chapter'] = chapter

        block_kind = self.block_kind_input.text().strip()
        if block_kind:
            scope['block_kind'] = block_kind.lower()

        block_id = self.block_id_input.text().strip()
        if block_id:
            scope['block_id'] = block_id

        type_text = self.type_combo.currentText()
        if type_text and type_text != "(aucun type)":
            scope['type'] = type_text

        return scope


class OptionsWidget(QtWidgets.QWidget):
    """Widget pour les options de l'assistant"""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.auto_link_checkbox = QtWidgets.QCheckBox("Auto-link (follow-up)")
        self.auto_link_checkbox.setChecked(True)
        self.auto_link_checkbox.setToolTip(
            "Lier automatiquement les questions suivantes au contexte précédent"
        )

        self.debug_checkbox = QtWidgets.QCheckBox("Mode debug")
        self.debug_checkbox.setChecked(False)
        self.debug_checkbox.setToolTip(
            "Afficher les informations de débogage dans la barre de statut"
        )

        layout.addWidget(self.auto_link_checkbox)
        layout.addWidget(self.debug_checkbox)

    def get_auto_link(self) -> bool:
        """Récupérer l'état de auto-link"""
        return self.auto_link_checkbox.isChecked()

    def set_auto_link(self, enabled: bool):
        """Définir l'état de auto-link"""
        self.auto_link_checkbox.setChecked(enabled)

    def get_debug(self) -> bool:
        """Récupérer l'état du mode debug"""
        return self.debug_checkbox.isChecked()


class ActionsWidget(QtWidgets.QWidget):
    """Widget pour les actions rapides"""

    pin_clicked = QtCore.Signal()
    unpin_clicked = QtCore.Signal()
    new_chat_clicked = QtCore.Signal()
    forget_clicked = QtCore.Signal()
    save_log_clicked = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Ligne 1 : Pin / Unpin
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(8)

        self.pin_btn = QtWidgets.QPushButton(f"{ICONS['pin']} Pin")
        self.pin_btn.setToolTip("Épingler le contexte actuel")
        self.pin_btn.clicked.connect(self.pin_clicked.emit)

        self.unpin_btn = QtWidgets.QPushButton(f"{ICONS['unpin']} Unpin")
        self.unpin_btn.setToolTip("Désépingler le contexte")
        self.unpin_btn.clicked.connect(self.unpin_clicked.emit)

        row1.addWidget(self.pin_btn)
        row1.addWidget(self.unpin_btn)

        # Ligne 2 : New chat / Forget
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)

        self.new_chat_btn = QtWidgets.QPushButton(f"{ICONS['new_chat']} New chat")
        self.new_chat_btn.setToolTip("Démarrer un nouveau chat isolé")
        self.new_chat_btn.clicked.connect(self.new_chat_clicked.emit)

        self.forget_btn = QtWidgets.QPushButton(f"{ICONS['forget']} Forget")
        self.forget_btn.setToolTip("Oublier la mémoire courte")
        self.forget_btn.clicked.connect(self.forget_clicked.emit)

        row2.addWidget(self.new_chat_btn)
        row2.addWidget(self.forget_btn)

        # Ligne 3 : Save log
        self.save_log_btn = QtWidgets.QPushButton(f"{ICONS['save']} Sauver log (JSONL)")
        self.save_log_btn.setToolTip("Sauvegarder la conversation dans un fichier JSONL")
        self.save_log_btn.clicked.connect(self.save_log_clicked.emit)

        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.save_log_btn)


class QueryInputWidget(QtWidgets.QHBoxLayout):
    """Widget pour l'entrée de question (input + filtre + bouton)"""

    send_clicked = QtCore.Signal()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        self.setSpacing(8)

        # Input de question
        self.question_input = QtWidgets.QLineEdit()
        self.question_input.setPlaceholderText("Pose ta question…")
        self.question_input.returnPressed.connect(self.send_clicked.emit)

        # Filtre de type
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems([
            "(aucun filtre)",
            "exercice",
            "méthode",
            "théorie",
            "cours"
        ])
        self.filter_combo.setFixedWidth(140)
        self.filter_combo.setToolTip("Filtrer par type de contenu")

        # Bouton Envoyer
        self.send_btn = QtWidgets.QPushButton(f"{ICONS['send']} Envoyer")
        self.send_btn.setObjectName("btnSend")
        self.send_btn.setFixedWidth(110)
        self.send_btn.clicked.connect(self.send_clicked.emit)

        # Ajouter les widgets
        self.addWidget(self.question_input, 1)  # stretch = 1
        self.addWidget(self.filter_combo)
        self.addWidget(self.send_btn)

    def get_question(self) -> str:
        """Récupérer la question saisie"""
        return self.question_input.text().strip()

    def get_type_filter(self) -> Optional[str]:
        """Récupérer le filtre de type sélectionné"""
        filter_text = self.filter_combo.currentText()
        if filter_text in {"(aucun filtre)", "cours"}:
            return None
        return filter_text

    def clear(self):
        """Effacer l'input"""
        self.question_input.clear()

    def focus(self):
        """Donner le focus à l'input"""
        self.question_input.setFocus()


class TaskTabs(QtWidgets.QTabWidget):
    """Onglet Tâches avec formulaires prêts"""

    taskRequested = QtCore.Signal(str, dict)  # (task_name, kwargs)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.setMovable(False)

        self._add_tab_fiche()
        self._add_tab_qcm()
        self._add_tab_exam()
        self._add_tab_tutor()
        self._add_tab_formule()
        self._add_tab_resume()
        self._add_tab_cours()

    # --- helpers ---
    def _line(self, placeholder=""):
        le = QtWidgets.QLineEdit()
        le.setPlaceholderText(placeholder)
        return le

    def _form_tab(self):
        w = QtWidgets.QWidget()
        lay = QtWidgets.QFormLayout(w)
        lay.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)
        return w, lay

    def _submit_btn(self, text="Générer"):
        b = QtWidgets.QPushButton(text)
        b.setObjectName("btnSend")
        return b

    # --- tabs ---
    def _add_tab_fiche(self):
        w, lay = self._form_tab()
        topic = self._line("Notion (ex: Série entière)")
        level = self._line("Niveau (Prépa, Licence...)")
        gen = self._submit_btn("Générer la fiche")
        gen.clicked.connect(lambda: self.taskRequested.emit("sheet_create", {"question_or_payload": topic.text().strip(), "level": level.text().strip() or "Prépa"}))
        lay.addRow("Sujet :", topic)
        lay.addRow("Niveau :", level)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['fiche']} Fiche")

    def _add_tab_qcm(self):
        w, lay = self._form_tab()
        notion = self._line("Notion ciblée")
        gen = self._submit_btn("Générer le QCM")
        gen.clicked.connect(lambda: self.taskRequested.emit("qcm", {"question_or_payload": notion.text().strip()}))
        lay.addRow("Notion :", notion)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['qcm']} QCM")

    def _add_tab_exam(self):
        w, lay = self._form_tab()
        chapters = self._line("Chapitres (ex: 1,5,7)")
        duration = self._line("Durée (ex: 3h)")
        level = self._line("Niveau (ex: Prépa)")
        gen = self._submit_btn("Générer le sujet")

        def _emit():
            self.taskRequested.emit("exam_gen", {
                "question_or_payload": f"Exam chapters {chapters.text().strip()}",
                "chapters": chapters.text().strip(),
                "duration": duration.text().strip() or "3h",
                "level": level.text().strip() or "Prépa"
            })
        gen.clicked.connect(_emit)
        lay.addRow("Chapitres :", chapters)
        lay.addRow("Durée :", duration)
        lay.addRow("Niveau :", level)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['exam']} Examen")

    def _add_tab_tutor(self):
        w, lay = self._form_tab()
        stmt = QtWidgets.QPlainTextEdit()
        stmt.setPlaceholderText("Énoncé à guider (pas à pas, sans solution)")
        gen = self._submit_btn("Démarrer le tutor")
        gen.clicked.connect(lambda: self.taskRequested.emit("tutor", {"question_or_payload": stmt.toPlainText().strip(), "with_solutions": False}))
        lay.addRow("Énoncé :", stmt)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['tutor']} Tutor")

    def _add_tab_formule(self):
        w, lay = self._form_tab()
        q = self._line("Description (ex: dérivée produit, transformée de Laplace...)")
        gen = self._submit_btn("Rechercher la formule")
        gen.clicked.connect(lambda: self.taskRequested.emit("formula", {"question_or_payload": q.text().strip()}))
        lay.addRow("Recherche :", q)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['formula']} Formule")

    def _add_tab_resume(self):
        w, lay = self._form_tab()
        q = self._line("Notion / partie de cours")
        gen = self._submit_btn("Générer le résumé")
        gen.clicked.connect(lambda: self.taskRequested.emit("course_summary", {"question_or_payload": q.text().strip()}))
        lay.addRow("Sujet :", q)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['summary']} Résumé")

    def _add_tab_cours(self):
        w, lay = self._form_tab()
        q = self._line("Notion (ex: Séries, EV, DL...)")
        level = self._line("Niveau (Prépa, Licence...)")
        gen = self._submit_btn("Générer le mini-cours")
        gen.clicked.connect(lambda: self.taskRequested.emit("course_build", {"question_or_payload": q.text().strip(), "level": level.text().strip() or "Prépa"}))
        lay.addRow("Notion :", q)
        lay.addRow("Niveau :", level)
        lay.addRow("", gen)
        self.addTab(w, f"{ICONS['course']} Cours")


class CommandPalette(QtWidgets.QFrame):
    """
    Palette de commandes (Ctrl+K) :
    - recherche sur une liste de commandes
    - insertTextRequested: insère du texte dans l'input (/commands)
    - gotoTabRequested: navigue vers un onglet
    - triggerRequested: déclenche une action de la fenêtre principale
    """

    insertTextRequested = QtCore.Signal(str)
    gotoTabRequested = QtCore.Signal(str)
    triggerRequested = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setObjectName("palette_overlay")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        # Overlay plein écran (dans la fenêtre)
        self.setGeometry(self.parentWidget().rect())

        # Box centrale
        self.box = QtWidgets.QFrame(self)
        self.box.setObjectName("palette_box")
        self.box.setFixedWidth(720)

        v = QtWidgets.QVBoxLayout(self.box)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)

        self.input = QtWidgets.QLineEdit()
        self.input.setObjectName("palette_input")
        self.input.setPlaceholderText(f"{ICONS['palette']} Rechercher une commande… (Esc pour fermer)")
        self.list = QtWidgets.QListWidget()
        self.list.setObjectName("palette_list")

        v.addWidget(self.input)
        v.addWidget(self.list)

        # Données commandes
        self._commands = self._build_commands()
        self._filtered = self._commands[:]
        self._refresh_list()

        # Connexions
        self.input.textChanged.connect(self._on_search)
        self.list.itemActivated.connect(self._on_activate)
        self.list.itemClicked.connect(self._on_activate)

    def show_palette(self):
        self._center_box()
        self._reset_search()
        self.show()
        self.raise_()
        self.input.setFocus()

    def hide_palette(self):
        self.hide()
        # focus sur l'input question si présent
        parent = self.parentWidget()
        if parent and hasattr(parent, "query_input"):
            try:
                parent.query_input.focus()
            except Exception:
                pass

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.setGeometry(self.parentWidget().rect())
        self._center_box()

    def _center_box(self):
        if not self.parentWidget():
            return
        pw = self.parentWidget().width()
        ph = self.parentWidget().height()
        bw = self.box.width()
        bh = 400
        self.box.setFixedHeight(bh)
        self.box.move(int((pw - bw) / 2), int((ph - bh) / 2))

    def _reset_search(self):
        self.input.clear()
        self._filtered = self._commands[:]
        self._refresh_list()

    # --- commandes disponibles ---
    def _build_commands(self) -> List[Dict[str, str]]:
        return [
            # Navigation onglets
            {"id": "goto_response", "label": "Aller à : Réponse", "hint": "Onglet principal"},
            {"id": "goto_sources", "label": "Aller à : Sources", "hint": "Onglet sources"},
            {"id": "goto_tasks", "label": "Aller à : Tâches", "hint": "Formulaires de génération"},
            # Actions
            {"id": "new_chat", "label": "Nouveau chat", "hint": "Réinitialise contexte et mémoire courte"},
            {"id": "pin", "label": "Épingler le contexte", "hint": "Conserver le meilleur contexte"},
            {"id": "unpin", "label": "Désépingler le contexte", "hint": "Oublier l’épinglage courant"},
            {"id": "forget", "label": "Oublier mémoire courte", "hint": "Reset conversation"},
            {"id": "save_log", "label": "Sauver log (JSONL)", "hint": "Exporter la session"},
            {"id": "toggle_auto_link", "label": "Basculer Auto-link", "hint": "Lier les questions de suivi"},
            {"id": "toggle_debug", "label": "Basculer Debug", "hint": "Afficher info debug"},
            {"id": "focus_input", "label": "Focus sur l’input", "hint": "Curseur dans la zone de question"},
            # Slash commands (insertion)
            {"id": "insert_/fiche", "label": "Insérer : /fiche ", "hint": "Générer fiche"},
            {"id": "insert_/qcm", "label": "Insérer : /qcm ", "hint": "Générer QCM"},
            {"id": "insert_/exam", "label": "Insérer : /exam ", "hint": "Générer examen"},
            {"id": "insert_/tutor", "label": "Insérer : /tutor ", "hint": "Guidage pas à pas"},
            {"id": "insert_/formule", "label": "Insérer : /formule ", "hint": "Rechercher une formule"},
            {"id": "insert_/resume", "label": "Insérer : /resume ", "hint": "Générer un résumé"},
            {"id": "insert_/cours", "label": "Insérer : /cours ", "hint": "Générer un mini-cours"},
        ]

    def _refresh_list(self):
        self.list.clear()
        for cmd in self._filtered:
            item = QtWidgets.QListWidgetItem(f"{cmd['label']}  ·  {cmd['hint']}")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, cmd["id"])
            self.list.addItem(item)
        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _on_search(self, text: str):
        q = (text or "").strip().lower()
        if not q:
            self._filtered = self._commands[:]
            self._refresh_list()
            return
        # filtre simple (substring sur label/hint)
        res = []
        for c in self._commands:
            hay = f"{c['label']} {c['hint']}".lower()
            if all(tok in hay for tok in q.split()):
                res.append(c)
        self._filtered = res
        self._refresh_list()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        # Échappe/ferme
        if event.key() in (QtCore.Qt.Key.Key_Escape,):
            self.hide_palette()
            event.accept()
            return
        # Entrée valide la sélection
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            self._activate_current()
            event.accept()
            return
        super().keyPressEvent(event)

    def _activate_current(self):
        item = self.list.currentItem()
        if item:
            self._on_activate(item)

    def _on_activate(self, item: QtWidgets.QListWidgetItem):
        cmd_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if cmd_id.startswith("insert_/"):
            # insérer une slash command
            text = cmd_id.replace("insert_", "") + " "
            self.insertTextRequested.emit(text)
            self.hide_palette()
            return
        if cmd_id.startswith("goto_"):
            # naviguer vers onglet
            target = cmd_id.split("_", 1)[1]
            self.gotoTabRequested.emit(target)
            self.hide_palette()
            return
        # déclencher action
        self.triggerRequested.emit(cmd_id)
        self.hide_palette()
