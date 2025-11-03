# -*- coding: utf-8 -*-
"""
src/ui/gui/app.py
Application GUI principale pour l'assistant RAG de maths (Architecture MVC)
"""

from __future__ import annotations
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

# Import des styles
from .styles import GLOBAL_STYLE, ICONS

# Import des widgets
from .widgets import (
    AnswerViewer,
    SourcesTable,
    ScopeWidget,
    OptionsWidget,
    ActionsWidget,
    QueryInputWidget,
    SectionLabel,
)

# Import de l'assistant
from src.assistant import get_assistant


class MainWindow(QtWidgets.QMainWindow):
    """Fenêtre principale de l'application GUI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialiser l'assistant
        self.assistant = get_assistant()
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"{ICONS['search']} Assistant Math – RAG v3.1")
        self.resize(1280, 900)
        
        # Appliquer le style global
        self.setStyleSheet(GLOBAL_STYLE)
        
        # État de l'application
        self.auto_pin_next = False
        
        # Construire l'interface
        self._setup_ui()
        
        # Initialiser le store en arrière-plan
        self._init_store()
        
    def _setup_ui(self):
        """Construire l'interface utilisateur"""
        
        # Widget central
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        # Layout principal horizontal
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== SIDEBAR (gauche) =====
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # ===== ZONE CENTRALE =====
        center = self._create_center_area()
        main_layout.addWidget(center, 1)  # stretch = 1
        
        # ===== STATUS BAR =====
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Initialisation...")
        
    def _create_sidebar(self) -> QtWidgets.QFrame:
        """Créer la barre latérale (sidebar)"""
        
        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(340)
        
        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Titre
        title = QtWidgets.QLabel(f"{ICONS['scope']} Configuration & Outils")
        title.setObjectName("title")
        layout.addWidget(title)
        
        # Section Portée
        layout.addWidget(SectionLabel(f"{ICONS['scope']} Définir la portée"))
        self.scope_widget = ScopeWidget()
        self.scope_widget.scope_applied.connect(self._on_scope_applied)
        self.scope_widget.scope_cleared.connect(self._on_scope_cleared)
        layout.addWidget(self.scope_widget)
        
        # Section Options
        layout.addWidget(SectionLabel(f"{ICONS['options']} Options"))
        self.options_widget = OptionsWidget()
        layout.addWidget(self.options_widget)
        
        # Section Actions rapides
        layout.addWidget(SectionLabel(f"{ICONS['actions']} Actions rapides"))
        self.actions_widget = ActionsWidget()
        self.actions_widget.pin_clicked.connect(self._on_pin)
        self.actions_widget.unpin_clicked.connect(self._on_unpin)
        self.actions_widget.new_chat_clicked.connect(self._on_new_chat)
        self.actions_widget.forget_clicked.connect(self._on_forget)
        self.actions_widget.save_log_clicked.connect(self._on_save_log)
        layout.addWidget(self.actions_widget)
        
        # Spacer pour pousser tout vers le haut
        layout.addStretch(1)
        
        return sidebar
    
    def _create_center_area(self) -> QtWidgets.QWidget:
        """Créer la zone centrale (viewer + sources + input)"""
        
        center = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(center)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Viewer de réponse (avec KaTeX)
        self.answer_viewer = AnswerViewer()
        layout.addWidget(self.answer_viewer, 4)  # stretch = 4
        
        # Section Sources
        layout.addWidget(SectionLabel(f"{ICONS['sources']} Sources utilisées"))
        self.sources_table = SourcesTable()
        layout.addWidget(self.sources_table, 2)  # stretch = 2
        
        # Input de question
        self.query_input = QueryInputWidget()
        self.query_input.send_clicked.connect(self._on_send)
        layout.addLayout(self.query_input)
        
        return center
    
    def _init_store(self):
        """Initialiser le store RAG en arrière-plan"""
        self.status_bar.showMessage("Préparation du store RAG...")
        
        try:
            self.assistant.ensure_ready()
            self.status_bar.showMessage("✓ Store RAG prêt", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"⚠ Erreur store: {e}", 5000)
            QtWidgets.QMessageBox.warning(
                self,
                "Erreur d'initialisation",
                f"Impossible d'initialiser le store RAG:\n{e}\n\n"
                "L'application peut ne pas fonctionner correctement."
            )
    
    # ===== SLOTS (gestionnaires d'événements) =====
    
    def _on_scope_applied(self, scope_info: str):
        """Quand une portée est appliquée"""
        self.status_bar.showMessage(f"✓ Portée appliquée: {scope_info}", 4000)
    
    def _on_scope_cleared(self):
        """Quand la portée est réinitialisée"""
        self.assistant.memory.scope_clear()
        self.status_bar.showMessage("✓ Portée réinitialisée", 3000)
    
    def _on_pin(self):
        """Épingler le contexte actuel"""
        try:
            # Épingler le meilleur contexte disponible
            best_meta = self.assistant.memory.best_context_meta()
            if best_meta:
                self.assistant.memory.state["pinned_meta"] = best_meta
                info = f"chap={best_meta.get('chapter')}, bloc={best_meta.get('block_kind')} {best_meta.get('block_id')}"
                self.status_bar.showMessage(f"📌 Contexte épinglé: {info}", 4000)
            else:
                self.status_bar.showMessage("⚠ Aucun contexte à épingler", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"⚠ Erreur pin: {e}", 3000)
    
    def _on_unpin(self):
        """Désépingler le contexte"""
        self.assistant.memory.state["pinned_meta"] = None
        self.status_bar.showMessage("📍 Contexte désépinglé", 3000)
    
    def _on_new_chat(self):
        """Démarrer un nouveau chat isolé"""
        self.assistant.memory.reset(full=True)
        self.options_widget.set_auto_link(True)
        self.auto_pin_next = True
        self.answer_viewer.clear()
        self.sources_table.clear()
        self.status_bar.showMessage(
            "🆕 Nouveau chat (auto-link ON, auto-pin au prochain contexte)",
            4000
        )
    
    def _on_forget(self):
        """Oublier la mémoire courte"""
        self.assistant.memory.reset(full=True)
        self.status_bar.showMessage("🧹 Mémoire courte nettoyée", 3000)
    
    def _on_save_log(self):
        """Sauvegarder le log de conversation"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le log JSONL",
            str(Path.cwd() / "logs" / "session.jsonl"),
            "JSON Lines (*.jsonl);;Tous les fichiers (*)"
        )
        
        if not path:
            return
        
        try:
            self.assistant.memory.save_log(path)
            self.status_bar.showMessage(f"💾 Log sauvegardé: {path}", 4000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder le log:\n{e}"
            )
    
    def _on_send(self):
        """Envoyer la question à l'assistant"""
        
        # Récupérer la question
        question = self.query_input.get_question()
        if not question:
            return

        type_filter = self.query_input.get_type_filter()
        auto_link = self.options_widget.get_auto_link()
        debug = self.options_widget.get_debug()

        # Portée éventuelle
        scope = self.scope_widget.get_scope()
        if scope:
            self.assistant.memory.scope_set(**scope)

        self.status_bar.showMessage("🔍 Recherche en cours...")
        self.answer_viewer.show_loading()
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))

        try:
            text = question.strip()
            payload = None

            # --- Détection de "slash commands" (mêmes que CLI) ---
            def _show(p):
                self.answer_viewer.set_answer(p['answer'])
                self.sources_table.set_sources(p['docs'])

            if text.startswith("/qcm "):
                p = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("qcm", p)

            elif text.startswith("/exam "):
                ch = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("exam_gen", f"Exam chapters {ch}", chapters=ch)

            elif text.startswith("/fiche "):
                notion = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("sheet_create", notion)

            elif text.startswith("/kholle "):
                notion = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("kholle", notion)

            elif text.startswith("/tutor "):
                st = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("tutor", st, with_solutions=False)

            elif text.startswith("/formule "):
                q = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("formula", q)

            elif text.startswith("/resume "):
                q = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("course_summary", q)

            elif text.startswith("/cours "):
                q = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("course_build", q)

            elif text.startswith("/corrige-exo "):
                st = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("exercise_correct", "Correction exercice", statement=st, student_answer="")

            elif text.startswith("/corrige-exam "):
                st = text.split(" ", 1)[1].strip()
                payload = self.assistant.run_task("exam_correct", "Correction examen", statement=st, student_answer="")

            else:
                # Orchestration standard
                payload = self.assistant.route_and_execute(
                    question=text,
                    filter_type=type_filter,
                    auto_link=auto_link,
                    debug=debug,
                    auto_pin_next=self.auto_pin_next
                )

            self.auto_pin_next = False
            _show(payload)

            if debug:
                self.status_bar.showMessage(
                    f"[DEBUG] rewritten={payload.get('rewritten_q')} | hinted={payload.get('hinted_q')} | kwargs={payload.get('final_kwargs')}",
                    8000
                )
            else:
                self.status_bar.showMessage("✓ Réponse générée", 2000)

            self.query_input.clear()
            self.query_input.focus()

        except Exception as e:
            err = f"Erreur: {e}"
            self.answer_viewer.show_error(err)
            self.status_bar.showMessage(f"✗ {err}", 5000)
            QtWidgets.QMessageBox.critical(self, "Erreur de traitement", f"Une erreur est survenue:\n\n{e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        """Événement de fermeture de la fenêtre"""
        
        # Demander confirmation si conversation en cours
        if len(self.assistant.memory.log_buffer) > 0:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirmation de fermeture",
                "Voulez-vous sauvegarder la conversation avant de quitter ?",
                QtWidgets.QMessageBox.StandardButton.Yes |
                QtWidgets.QMessageBox.StandardButton.No |
                QtWidgets.QMessageBox.StandardButton.Cancel
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self._on_save_log()
        
        event.accept()


def main():
    """Point d'entrée de l'application GUI"""
    
    # Créer l'application Qt
    app = QtWidgets.QApplication(sys.argv)
    
    # Configuration de l'application
    app.setApplicationName("Assistant Math RAG v3.1")
    app.setOrganizationName("MathRAG")
    app.setApplicationVersion("3.1.0")
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()