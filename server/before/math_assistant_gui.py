# -*- coding: utf-8 -*-
"""
math_assistant_gui.py
GUI PySide6 pour l'assistant RAG de maths :
- PySide6 + QtWebEngine (KaTeX) pour LaTeX (fallback QTextBrowser)
- Style moderne et cohérent
"""

from __future__ import annotations
from typing import Optional, List
import os, sys, time, json

from PySide6 import QtCore, QtGui, QtWidgets
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_OK = True
except Exception:
    WEBENGINE_OK = False

from lib.math_assistant_lib import (
    ensure_store_ready, retrieve_and_answer, LAST_STATE, SESSION_SCOPE,
    scope_show, scope_set, scope_clear, reset_state, best_context_meta,
    save_log_jsonl
)

KATEX_HTML_TPL = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous"></script>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin: 0; padding: 16px 20px; font-family: system-ui, -apple-system, "Segoe UI", Inter, Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
         background: #0b0f14; color: #e6edf3; line-height: 1.6; }}
  .bubble {{ background: #0f1720; border: 1px solid #1f2a37; border-radius: 14px; padding: 16px 18px; box-shadow: 0 10px 30px rgba(0,0,0,.35); }}
  h1,h2,h3 {{ color: #cbd5e1; }}
  code, pre {{ background: #0b1220; border: 1px solid #192233; border-radius: 10px; padding: 2px 6px; }}
  .katex {{ font-size: 1.1em; }}
  .katex-display {{ margin: 1em 0; }}
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
        throwOnError: false
    }});
}});
</script>
</head>
<body><div class="bubble">{html}</div></body></html>"""

# Styles globaux améliorés
GLOBAL_STYLE = """
QMainWindow {
    background-color: #0b0f14;
}

QWidget {
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #0f1720;
    border-right: 1px solid #1f2a37;
}

/* Labels */
QLabel {
    color: #e6edf3;
    padding: 2px;
}

QLabel#title {
    font-size: 18px;
    font-weight: 600;
    color: #cbd5e1;
    padding: 8px 0;
}

/* Line Edits */
QLineEdit {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    selection-background-color: #1f6feb;
}

QLineEdit:focus {
    border: 1px solid #388bfd;
    outline: none;
}

QLineEdit:hover {
    border-color: #484f58;
}

/* Combo Box */
QComboBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #484f58;
}

QComboBox:focus {
    border: 1px solid #388bfd;
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

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
    color: #e6edf3;
    padding: 4px;
}

/* Buttons */
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
}

QPushButton:disabled {
    background-color: #161b22;
    color: #6e7681;
    border-color: #21262d;
}

/* Primary Button (Send) */
QPushButton#btnSend {
    background-color: #238636;
    border-color: #2ea043;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#btnSend:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}

QPushButton#btnSend:pressed {
    background-color: #1f7a2f;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #e6edf3;
    padding: 4px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #30363d;
    background-color: #161b22;
}

QCheckBox::indicator:hover {
    border-color: #484f58;
    background-color: #21262d;
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

/* Table Widget */
QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #e6edf3;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #21262d;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    border: none;
    border-bottom: 1px solid #21262d;
    padding: 8px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
}

/* Text Browser */
QTextBrowser {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 12px;
    color: #e6edf3;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #0d1117;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #484f58;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #21262d;
}

/* Separators */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #21262d;
}
"""

def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def md_to_html_light(md: str) -> str:
    lines = md.splitlines()
    out = []
    in_code = False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            out.append("<pre><code>" if in_code else "</code></pre>")
            continue
        if in_code:
            out.append(html_escape(ln)); continue
        if ln.startswith("### "): out.append(f"<h3>{html_escape(ln[4:])}</h3>"); continue
        if ln.startswith("## "):  out.append(f"<h2>{html_escape(ln[3:])}</h2>"); continue
        if ln.startswith("# "):   out.append(f"<h1>{html_escape(ln[2:])}</h1>"); continue
        if ln.startswith("- "):   out.append(f"<li>{html_escape(ln[2:])}</li>"); continue
        if ln.strip() == "":
            out.append("<br/>"); continue
        out.append(f"<p>{html_escape(ln)}</p>")
    if any(l.startswith("- ") for l in lines):
        html = "\n".join(out).replace("<li>", "<ul><li>", 1).replace("</li>", "</li></ul>", 1)
        return html
    return "\n".join(out)

class ChatWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant Math – RAG v3.1 (GUI, PySide6 + KaTeX)")
        self.resize(1200, 800)
        
        # Appliquer le style global
        self.setStyleSheet(GLOBAL_STYLE)

        self.auto_link = True
        self.debug = False
        self.auto_pin_next = False

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ----- Sidebar -----
        side = QtWidgets.QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(330)
        s = QtWidgets.QVBoxLayout(side)
        s.setContentsMargins(16, 16, 16, 16)
        s.setSpacing(12)

        title = QtWidgets.QLabel("Outils & Portée")
        title.setObjectName("title")
        s.addWidget(title)

        # Section Portée
        scope_label = QtWidgets.QLabel("Définir la portée")
        scope_label.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: 600; margin-top: 8px;")
        s.addWidget(scope_label)

        self.in_chapter = QtWidgets.QLineEdit(placeholderText="Chapitre (ex: 21)")
        self.in_block_kind = QtWidgets.QLineEdit(placeholderText="Block kind (théorème/définition/...)")
        self.in_block_id = QtWidgets.QLineEdit(placeholderText="Block id (ex: 21.52)")
        self.in_type = QtWidgets.QComboBox()
        self.in_type.addItems(["", "exercice", "méthode", "théorie", "cours"])
        
        for w in [self.in_chapter, self.in_block_kind, self.in_block_id, self.in_type]:
            s.addWidget(w)

        btn_apply = QtWidgets.QPushButton("Appliquer la portée")
        btn_apply.clicked.connect(self.apply_scope)
        btn_clear = QtWidgets.QPushButton("Réinitialiser la portée")
        btn_clear.clicked.connect(self.clear_scope)
        s.addWidget(btn_apply)
        s.addWidget(btn_clear)

        # Section Options
        options_label = QtWidgets.QLabel("Options")
        options_label.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: 600; margin-top: 12px;")
        s.addWidget(options_label)

        self.chk_link = QtWidgets.QCheckBox("Auto-link (follow-up)")
        self.chk_link.setChecked(True)
        self.chk_debug = QtWidgets.QCheckBox("Mode debug")
        self.chk_debug.setChecked(False)
        s.addWidget(self.chk_link)
        s.addWidget(self.chk_debug)

        # Section Actions
        actions_label = QtWidgets.QLabel("Actions rapides")
        actions_label.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: 600; margin-top: 12px;")
        s.addWidget(actions_label)

        row_btns = QtWidgets.QHBoxLayout()
        row_btns.setSpacing(8)
        btn_pin = QtWidgets.QPushButton("📌 Pin")
        btn_pin.clicked.connect(self.do_pin)
        btn_unpin = QtWidgets.QPushButton("Unpin")
        btn_unpin.clicked.connect(self.do_unpin)
        row_btns.addWidget(btn_pin)
        row_btns.addWidget(btn_unpin)
        s.addLayout(row_btns)

        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)
        btn_newchat = QtWidgets.QPushButton("🆕 New chat")
        btn_newchat.clicked.connect(self.do_new_chat)
        btn_forget = QtWidgets.QPushButton("🧹 Forget")
        btn_forget.clicked.connect(self.do_forget)
        row2.addWidget(btn_newchat)
        row2.addWidget(btn_forget)
        s.addLayout(row2)

        btn_log = QtWidgets.QPushButton("💾 Sauver log (JSONL)")
        btn_log.clicked.connect(self.save_log)
        s.addWidget(btn_log)
        
        s.addStretch(1)

        # ----- Centre -----
        center = QtWidgets.QWidget()
        c = QtWidgets.QVBoxLayout(center)
        c.setContentsMargins(16, 16, 16, 16)
        c.setSpacing(12)

        if WEBENGINE_OK:
            self.view = QWebEngineView()
        else:
            self.view = QtWidgets.QTextBrowser()
            self.view.setOpenExternalLinks(True)
        c.addWidget(self.view, 4)

        # Section Sources
        sources_label = QtWidgets.QLabel("Sources utilisées")
        sources_label.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: 600;")
        c.addWidget(sources_label)

        self.sources = QtWidgets.QTableWidget(0, 5)
        self.sources.setHorizontalHeaderLabels(["#", "Bloc", "Chap/Sec", "Page", "Aperçu"])
        self.sources.horizontalHeader().setStretchLastSection(True)
        self.sources.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.sources.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sources.verticalHeader().setVisible(False)
        c.addWidget(self.sources, 2)

        # Input box
        input_box = QtWidgets.QHBoxLayout()
        input_box.setSpacing(8)
        self.in_question = QtWidgets.QLineEdit(placeholderText="Pose ta question…")
        self.in_question.returnPressed.connect(self.on_send)
        
        self.cmb_filter = QtWidgets.QComboBox()
        self.cmb_filter.addItems(["(aucun filtre)", "exercice", "méthode", "théorie", "cours"])
        self.cmb_filter.setFixedWidth(140)
        
        btn_send = QtWidgets.QPushButton("Envoyer ↵")
        btn_send.setObjectName("btnSend")
        btn_send.clicked.connect(self.on_send)
        btn_send.setFixedWidth(100)
        
        input_box.addWidget(self.in_question, 1)
        input_box.addWidget(self.cmb_filter)
        input_box.addWidget(btn_send)
        c.addLayout(input_box)

        main_layout.addWidget(side)
        main_layout.addWidget(center, 1)

        self.status = self.statusBar()
        self.status.showMessage("Préparation du store…")
        ensure_store_ready()
        self.status.showMessage("Prêt.")

    # ===== Actions =====
    def apply_scope(self):
        kv = {}
        if self.in_chapter.text().strip():
            kv["chapter"] = self.in_chapter.text().strip()
        if self.in_block_kind.text().strip():
            kv["block_kind"] = self.in_block_kind.text().strip().lower()
        if self.in_block_id.text().strip():
            kv["block_id"] = self.in_block_id.text().strip()
        t = self.in_type.currentText().strip()
        if t:
            kv["type"] = t
        scope_set(**kv)
        self.status.showMessage(f"Portée appliquée: {scope_show()}", 3000)

    def clear_scope(self):
        scope_clear()
        self.in_chapter.clear()
        self.in_block_kind.clear()
        self.in_block_id.clear()
        self.in_type.setCurrentIndex(0)
        self.status.showMessage("Portée réinitialisée.", 3000)

    def do_pin(self):
        meta = LAST_STATE.get("pinned_meta") or LAST_STATE.get("last_top_meta")
        if not meta:
            meta = {"info": "(aucun contexte détecté encore)"}
        LAST_STATE["pinned_meta"] = meta
        self.status.showMessage(f"Contexte épinglé: {meta}", 4000)

    def do_unpin(self):
        LAST_STATE["pinned_meta"] = None
        LAST_STATE["last_top_meta"] = None
        LAST_STATE["last_route"] = None
        LAST_STATE["last_question"] = None
        self.status.showMessage("Contexte désépinglé et mémoire courte réinitialisée.", 4000)

    def do_forget(self):
        reset_state(full=True)
        self.status.showMessage("Mémoire courte et portée nettoyées. Aucun contexte actif.", 4000)

    def do_new_chat(self):
        reset_state(full=True)
        self.chk_link.setChecked(True)
        self.auto_pin_next = True
        self.status.showMessage("Nouveau chat isolé (auto-link ON, auto-pin au prochain contexte).", 4000)

    def save_log(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Sauver log JSONL", "./logs/session.jsonl", "JSON Lines (*.jsonl)"
        )
        if not path:
            return
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        save_log_jsonl(path)
        self.status.showMessage(f"Log sauvegardé: {path}", 4000)

    def on_send(self):
        q = self.in_question.text().strip()
        if not q:
            return

        filt = self.cmb_filter.currentText()
        filt = None if filt in {"(aucun filtre)", "cours"} else filt

        self.auto_link = self.chk_link.isChecked()
        self.debug = self.chk_debug.isChecked()

        self.status.showMessage("Recherche en cours…")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        try:
            payload = retrieve_and_answer(
                q, filt,
                auto_link=self.auto_link,
                debug=self.debug,
                auto_pin_next=self.auto_pin_next
            )
            self.auto_pin_next = False
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if self.debug:
            dbg = f"[DEBUG] rewritten_q={payload['rewritten_q']} | hinted_q={payload['hinted_q']} | kwargs={payload['final_kwargs']}"
            self.status.showMessage(dbg, 8000)
        else:
            self.status.showMessage("Réponse générée.", 2000)

        self.render_answer(payload["answer"])
        self.populate_sources(payload["docs"])
        self.in_question.clear()
        self.in_question.setFocus()

    def render_answer(self, answer_md: str):
        if WEBENGINE_OK:
            html = md_to_html_light(answer_md)
            self.view.setHtml(KATEX_HTML_TPL.format(html=html))
        else:
            if isinstance(self.view, QtWidgets.QTextBrowser):
                self.view.setPlainText(answer_md)

    def populate_sources(self, docs: List):
        self.sources.setRowCount(0)
        for i, d in enumerate(docs, start=1):
            blk = ("{} {}".format(
                d.metadata.get("block_kind", "") or "",
                d.metadata.get("block_id", "") or ""
            )).strip()
            chapsec = f"{d.metadata.get('chapter','?')} / {d.metadata.get('section','?')}"
            page = str(d.metadata.get("page", "?"))
            prev = (d.page_content[:140].replace("\n", " ") + "…") if getattr(d, "page_content", "") else ""
            
            row = self.sources.rowCount()
            self.sources.insertRow(row)
            self.sources.setItem(row, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.sources.setItem(row, 1, QtWidgets.QTableWidgetItem(blk if blk else d.metadata.get("type", "?")))
            self.sources.setItem(row, 2, QtWidgets.QTableWidgetItem(chapsec))
            self.sources.setItem(row, 3, QtWidgets.QTableWidgetItem(page))
            
            item_prev = QtWidgets.QTableWidgetItem(prev)
            item_prev.setToolTip(prev)
            self.sources.setItem(row, 4, item_prev)
        
        self.sources.resizeColumnsToContents()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Assistant Math – RAG v3.1")
    w = ChatWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()