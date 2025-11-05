# -*- coding: utf-8 -*-
"""
src/ui/cli/app.py
Application CLI pour l'assistant mathématique
"""

from __future__ import annotations
from typing import Optional
import os
import json
import time

from src.assistant import get_assistant
from src.core.config import ui_config, rag_config
from .styles import console, CLIFormatter


class MathCLI:
    """Interface CLI pour l'assistant mathématique"""

    def __init__(self):
        self.assistant = get_assistant()
        self.formatter = CLIFormatter()

        # Options
        self.auto_link = getattr(ui_config, "cli_auto_link", True)
        self.debug = getattr(ui_config, "cli_debug", False)
        self.auto_pin_next = False
        self.allow_oot = getattr(ui_config, "cli_allow_oot", True)  # Hors programme autorisé ?
        self.chat_id = self.assistant.memory.chat_id
        
        # Mode tuteur persistant
        self.tutor_mode = False  # Mode tuteur activé/désactivé
        self.tutor_strict = False  # True=strict (tout en guidage), False=smart (intelligent)
        self.tutor_explain = False  # Mode explanation/compréhension activé

        # Cache du dernier passport et du dernier debug record
        self._last_passport: Optional[dict] = None
        self._last_debug: Optional[dict] = None
    
    def _sync_state_to_memory(self):
        """Synchronize CLI state to assistant.memory for comprehensive /show display."""
        # Sync OOT
        self.assistant.memory.set_oot_allow(self.allow_oot)
        
        # Sync tutor mode
        if self.tutor_mode:
            mode = "strict" if self.tutor_strict else "smart"
            self.assistant.memory.set_tutor_mode(mode)
        else:
            self.assistant.memory.set_tutor_mode(None)
        
        # Sync auto-link
        self.assistant.memory.set_auto_link(self.auto_link)
        
        # Store backend (for display purposes)
        self.assistant.memory.state["backend"] = rag_config.runtime_default_mode

    def run(self):
        """Boucle principale"""
        self.assistant.ensure_ready()

        # Bandeau d'accueil simplifié
        self.formatter.title("🎓 ASSISTANT MATHÉMATIQUES – RAG v3.1")
        # Afficher seulement l'info essentielle au démarrage
        console.print(f"[cyan]⚡ Backend:[/] [bold]{rag_config.runtime_default_mode}[/]  |  [cyan]🤖 LLM:[/] [bold]{rag_config.llm_model}[/]")
        console.print(f"[dim]💡 Utilise /show pour voir tous les paramètres, /help pour les commandes[/]\n")
        self.formatter.command_help()

        while True:
            try:
                self.formatter.separator()
                
                # Get router mode
                router_mode = self.assistant.memory.get_route_override() or "auto"
                
                question = self.formatter.prompt(
                    tutor_mode=self.tutor_mode,
                    tutor_strict=self.tutor_strict,
                    tutor_explain=self.tutor_explain,
                    allow_oot=self.allow_oot,
                    router_mode=router_mode,
                    backend=rag_config.runtime_default_mode
                )

                if not question:
                    continue

                if question.lower() == "q":
                    self.formatter.goodbye()
                    break

                # Traitement de la commande/question
                if not self.handle_command(question):
                    self.handle_question(question)

            except KeyboardInterrupt:
                self.formatter.goodbye()
                break

            except Exception as e:
                self.formatter.error(str(e))

    # --------------------------------------------------------------------- #
    #                      COMMANDES SPÉCIALES (/...)                       #
    # --------------------------------------------------------------------- #
    def handle_command(self, command: str) -> bool:
        """
        Traite les commandes spéciales

        Returns:
            True si c'était une commande, False sinon
        """
        cmd = command.strip()

        # ----- Aide -----
        if cmd.lower() in {"/help", "/aide", "/?"}:
            self.formatter.command_help()
            self.formatter.info("\n🔍 Nouvelles commandes:")
            self.formatter.info("  /blocks [chapitre]  - Liste les blocs d'un chapitre")
            self.formatter.info("  /find-bloc <query>  - Cherche un bloc par ID ou titre")
            return True

        # ----- Manuel détaillé -----
        if cmd.lower().startswith("/man "):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 2:
                self.formatter.command_manual(parts[1])
            else:
                self.formatter.warning("Usage: /man <commande>")
            return True

        # ----- Alias /show -> /scope show -----
        if cmd.lower() == "/show":
            # Synchronize CLI state with assistant.memory before showing
            self._sync_state_to_memory()
            self.formatter.scope_status(self.assistant.memory.scope_show())
            return True

        # ----- Liste des blocs d'un chapitre -----
        if cmd.startswith("/blocks"):
            parts = cmd.split()
            ch = parts[1] if len(parts) > 1 else None
            
            all_docs = self.assistant.engine._get_all_docs()
            rows = []
            
            for d in all_docs:
                if ch and str(d.metadata.get("chapter")) != str(ch):
                    continue
                
                bk = (d.metadata.get("block_kind") or "").lower()
                bid = d.metadata.get("block_id")
                
                if bk and bid:
                    rows.append((
                        str(d.metadata.get("chapter")),
                        bk,
                        str(bid),
                        d.metadata.get("title") or ""
                    ))
            
            if not rows:
                self.formatter.info("Aucun bloc trouvé.")
                return True
            
            # Tableau Rich
            from rich.table import Table
            t = Table(title=f"Blocs chapitre {ch}" if ch else "Tous les blocs", show_lines=True)
            t.add_column("Ch.", style="cyan", justify="center")
            t.add_column("Type", style="magenta")
            t.add_column("ID", style="bold yellow")
            t.add_column("Titre", style="white")
            
            # Tri: chapitre (numérique) > type > id
            for r in sorted(rows, key=lambda x: (
                int(x[0]) if x[0].isdigit() else 999,
                x[1],
                x[2]
            )):
                t.add_row(*r)
            
            console.print(t)
            self.formatter.info(f"\n💡 Utilise: /ch {ch or '<N>'} puis /bloc <type> <id>")
            return True

        # ----- Recherche de bloc par ID ou titre -----
        if cmd.startswith("/find-bloc "):
            q = cmd.split(" ", 1)[1].strip().lower()
            
            all_docs = self.assistant.engine._get_all_docs()
            hits = []
            
            for d in all_docs:
                bk = (d.metadata.get("block_kind") or "").lower()
                bid = str(d.metadata.get("block_id") or "").lower()
                title = (d.metadata.get("title") or "").lower()
                
                # Recherche dans ID ou titre
                if q in bid or q in title:
                    hits.append((
                        d.metadata.get("chapter"),
                        bk,
                        bid,
                        d.metadata.get("page"),
                        d.metadata.get("title") or ""
                    ))
            
            if not hits:
                self.formatter.info(f"Aucun bloc correspondant à '{q}'.")
                return True
            
            from rich.table import Table
            t = Table(title=f"Résultats pour '{q}'", show_lines=True)
            t.add_column("Ch.", style="cyan", justify="center")
            t.add_column("Type", style="magenta")
            t.add_column("ID", style="bold yellow")
            t.add_column("Page", style="green", justify="right")
            t.add_column("Titre", style="white")
            
            for h in hits[:40]:  # Limite 40 résultats
                t.add_row(
                    str(h[0]),
                    h[1],
                    h[2],
                    str(h[3] or "?"),
                    h[4]
                )
            
            console.print(t)
            self.formatter.info(f"\n💡 Pour cibler: /ch <N> puis /bloc <type> <id>")
            return True

        # ----- Debug on/off -----
        if cmd.startswith("/debug"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].lower() in {"on", "off"}:
                self.debug = (parts[1].lower() == "on")
                self.formatter.success(f"Mode debug: {'activé' if self.debug else 'désactivé'}")
            else:
                self.formatter.warning("Usage: /debug on|off")
            return True

        # ----- Auto-link on/off -----
        if cmd.startswith("/link"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].lower() in {"on", "off"}:
                self.auto_link = (parts[1].lower() == "on")
                self.formatter.success(f"Auto-link: {'activé' if self.auto_link else 'désactivé'}")
            else:
                self.formatter.warning("Usage: /link on|off")
            return True

        # ----- Hors programme on/off -----
        if cmd.startswith("/oot"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].lower() in {"on", "off"}:
                self.allow_oot = (parts[1].lower() == "on")
                # Synchronize with assistant.memory
                self.assistant.memory.set_oot_allow(self.allow_oot)
                self.formatter.success(f"Hors programme: {'autorisé' if self.allow_oot else 'désactivé (RAG strict)'}")
            else:
                self.formatter.warning("Usage: /oot on|off")
            return True

        # ----- Router override: auto|rag|llm|hybrid -----
        if cmd.startswith("/router") or cmd.startswith("/route"):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 1 or parts[1].strip().lower() in {"show", "status"}:
                mode = self.assistant.memory.get_route_override() or "auto"
                self.formatter.router_status(mode, self.allow_oot)
                return True

            mode = parts[1].strip().lower()
            alias = {"auto": "auto", "rag": "rag", "llm": "llm", "hybrid": "hybrid"}
            if mode in alias:
                self.assistant.set_route_override(alias[mode])
                self.formatter.success(f"🧭 Routeur forcé: {alias[mode]}")
            else:
                self.formatter.warning("Usage: /router <auto|rag|llm|hybrid>  (ou '/router show')")
            return True

        # ----- Backend/runtime (local|cloud|hybrid) -----
        if cmd.startswith("/backend") or cmd.startswith("/runtime"):
            parts = cmd.split(maxsplit=1)
            if len(parts) == 1 or parts[1].strip().lower() in {"show", "status"}:
                self.formatter.backend_status({
                    "runtime": rag_config.runtime_default_mode,
                    "ollama_host": rag_config.ollama_host,
                    "llm_primary": rag_config.llm_model,
                    "llm_fallback": rag_config.llm_local_fallback,
                    "rewrite_model": rag_config.rewrite_model,
                    "embed_primary": rag_config.embed_model_primary,
                    "embed_alt": rag_config.embed_model_alt,
                    "reranker": rag_config.reranker_model if rag_config.use_reranker else "(désactivé)",
                })
                return True

            mode = parts[1].strip().lower()
            if mode not in {"local", "cloud", "hybrid"}:
                self.formatter.warning("Usage: /backend <local|cloud|hybrid>  (ou '/backend show')")
                return True

            # Change backend mode directly
            rag_config.runtime_default_mode = mode
            self.formatter.success(f"✅ Backend changé: {mode.upper()}")
            self.formatter.info(f"⚠️  Note: Certains modèles peuvent nécessiter un redémarrage pour être rechargés.")
            return True

        # ----- Afficher/Sauver le dernier passport de routage -----
        if cmd in {"/passport", "/decision"} or cmd.startswith("/passport"):
            if not self._last_passport:
                self.formatter.info("Aucun passport disponible (pose une question d'abord).")
                return True

            # /passport save  ou  /passport json
            parts = cmd.split()
            if len(parts) == 2 and parts[1] in {"save", "json"}:
                dirpath = ui_config.debug_dir / self.chat_id
                dirpath.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                path = dirpath / f"passport_{ts}.json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self._last_passport, f, ensure_ascii=False, indent=2)
                self.formatter.success(f"Passport enregistré: {path}")
            else:
                self.formatter.passport(self._last_passport)
                # Si le passport contient poids/penalties → affichage détaillé
                self.formatter.debug_passport(self._last_passport)
            return True

        # ----- Modèles actifs / env utiles -----
        if cmd in {"/models", "/model"}:
            self.formatter.models_table({
                "runtime": rag_config.runtime_default_mode,
                "ollama_host": rag_config.ollama_host,
                "llm_primary": rag_config.llm_model,
                "llm_fallback": rag_config.llm_local_fallback,
                "rewrite_model": rag_config.rewrite_model,
                "embed_primary": rag_config.embed_model_primary,
                "embed_alt": rag_config.embed_model_alt,
                "reranker": rag_config.reranker_model if rag_config.use_reranker else "(désactivé)",
            })
            return True

        if cmd in {"/where", "/paths"}:
            self.formatter.paths({
                "log_dir": str(ui_config.log_dir / self.chat_id),
                "debug_dir": str(ui_config.debug_dir / self.chat_id),
                "db_dir": str(rag_config.db_dir),
                "pdf_path": str(rag_config.pdf_path),
            })
            return True

        # ----- Pin / Unpin -----
        if cmd == "/pin" or cmd.startswith("/pin "):
            meta = self.assistant.memory.best_context_meta()
            if not meta:
                meta = self.assistant.memory.state.get("last_top_meta") or {"info": "(aucun contexte)"}
            self.assistant.memory.state["pinned_meta"] = meta
            self.formatter.success(f"Contexte épinglé: {meta}")
            return True

        if cmd == "/unpin" or cmd.startswith("/unpin "):
            self.assistant.memory.reset(full=False)
            self.formatter.success("Contexte désépinglé et mémoire courte réinitialisée")
            return True

        # ----- Forget -----
        if cmd == "/forget":
            self.assistant.memory.reset(full=True)
            self.tutor_mode = False
            self.tutor_strict = False
            self.tutor_explain = False
            self.formatter.success("Mémoire courte et portée nettoyées • Mode tuteur désactivé")
            return True

        # ----- New chat -----
        if cmd.startswith("/new-chat"):
            parts = cmd.split(maxsplit=1)
            chat_name = parts[1].strip() if len(parts) > 1 else None
            
            self.assistant.new_session(reset_scope=True, preserve_logs=True)
            self.chat_id = self.assistant.memory.chat_id
            self.auto_link = True
            self.auto_pin_next = True
            self.tutor_mode = False
            self.tutor_strict = False
            self.tutor_explain = False
            self._last_passport = None
            self._last_debug = None
            
            chat_display = f"[cyan]{chat_name}[/]" if chat_name else self.chat_id
            self.formatter.success(
                f"Nouveau chat: {chat_display} | Auto-link activé | Auto-pin au prochain contexte | Mode tuteur désactivé"
            )
            return True

        # ----- Raccourcis de tâches -----
        if cmd.startswith("/qcm "):
            notion = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("qcm", notion)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/exam "):
            ch = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("exam_gen", f"Exam chapters {ch}", chapters=ch)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/fiche "):
            notion = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("sheet_create", notion)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/kholle "):
            notion = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("kholle", notion)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/tutor"):
            parts = cmd.split()
            if len(parts) == 1:
                # /tutor seul → afficher le status
                mode_str = "activé" if self.tutor_mode else "désactivé"
                if self.tutor_mode:
                    if self.tutor_strict:
                        type_str = "strict (tout en guidage)"
                    else:
                        type_str = "smart (détection auto)"
                    status = f"Mode tuteur: {mode_str} • Type: {type_str}"
                else:
                    status = f"Mode tuteur: {mode_str}"
                
                explain_str = "activé" if self.tutor_explain else "désactivé"
                status += f" • Mode explain: {explain_str}"
                self.formatter.info(status)
                return True
            
            arg = parts[1].lower()
            
            # /tutor on [strict|smart]
            if arg == "on":
                self.tutor_mode = True
                # Déterminer le type (strict ou smart)
                if len(parts) >= 3 and parts[2].lower() == "strict":
                    self.tutor_strict = True
                    self.assistant.memory.set_tutor_mode("strict")
                    self.formatter.success("🎓 Mode tuteur activé (strict) - Toutes les réponses en guidage pédagogique")
                else:
                    self.tutor_strict = False
                    self.assistant.memory.set_tutor_mode("smart")
                    self.formatter.success("🎓 Mode tuteur activé (smart) - Détection auto : exercices → guidage, théorie → normal")
                return True
            
            # /tutor off
            if arg == "off":
                self.tutor_mode = False
                self.tutor_strict = False
                self.assistant.memory.set_tutor_mode(None)
                self.formatter.success("Mode tuteur désactivé")
                return True
            
            # /tutor explain [on|off|<question>]
            if arg == "explain":
                if len(parts) >= 3:
                    sub_arg = parts[2].lower()
                    # Check if it's on/off command
                    if sub_arg == "on":
                        self.tutor_explain = True
                        self.formatter.success("🧠 Mode explain activé - Guidage socratique pour la compréhension de cours/théorèmes")
                        return True
                    elif sub_arg == "off":
                        self.tutor_explain = False
                        self.formatter.success("Mode explain désactivé")
                        return True
                    else:
                        # /tutor explain <question> → mode ponctuel explanation
                        st = cmd.split(" ", 2)[2].strip()
                        payload = self.assistant.run_task("tutor", st, with_solutions=False)
                        self._capture_backend_debug(payload)
                        self.formatter.info("🧠 Mode explain - Guidage socratique")
                        self.formatter.sources_table(payload["docs"])
                        self.formatter.answer(payload["answer"])
                        return True
                else:
                    # /tutor explain sans argument → afficher usage
                    self.formatter.warning("Usage: /tutor explain on|off ou /tutor explain <question>")
                    return True
            
            # /tutor <question> → mode ponctuel (comme avant)
            if len(parts) >= 2:
                st = cmd.split(" ", 1)[1].strip()
                if st.lower() not in {"on", "off", "strict", "smart", "explain"}:
                    payload = self.assistant.run_task("tutor", st, with_solutions=False)
                    self._capture_backend_debug(payload)
                    self.formatter.sources_table(payload["docs"])
                    self.formatter.answer(payload["answer"])
                    return True
            
            self.formatter.warning("Usage: /tutor [on|off] [strict|smart] | /tutor explain [on|off] | /tutor <question>")
            return True

        if cmd.startswith("/formule "):
            q = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("formula", q)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/resume "):
            q = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("course_summary", q)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/cours "):
            q = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("course_build", q)
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/corrige-exo "):
            st = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("exercise_correct", "Correction exercice", statement=st, student_answer="")
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        if cmd.startswith("/corrige-exam "):
            st = cmd.split(" ", 1)[1].strip()
            payload = self.assistant.run_task("exam_correct", "Correction examen", statement=st, student_answer="")
            self._capture_backend_debug(payload)
            self.formatter.sources_table(payload["docs"])
            self.formatter.answer(payload["answer"])
            return True

        # ----- Log -----
        if cmd.startswith("/log"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1] == "save":
                dirpath = ui_config.log_dir / self.chat_id
                dirpath.mkdir(parents=True, exist_ok=True)
                ts = int(time.time())
                path = dirpath / f"{ts}.jsonl"
                self.assistant.memory.save_log(str(path))
                self.formatter.success(f"Log sauvegardé: {path}")
            else:
                self.formatter.warning("Usage: /log save")
            return True

        # ----- Scope -----
        if cmd.startswith("/scope"):
            parts = cmd.split()
            if len(parts) == 1 or parts[1] == "show":
                self.formatter.scope_status(self.assistant.memory.scope_show())
                return True

            if parts[1] == "clear":
                self.assistant.memory.scope_clear()
                self.formatter.success("Portée réinitialisée")
                return True

            if parts[1] == "set":
                kvs = {}
                for token in parts[2:]:
                    if "=" in token:
                        k, v = token.split("=", 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k in {"chapter", "block_kind", "block_id", "type"}:
                            kvs[k] = v
                self.assistant.memory.scope_set(**kvs)
                self.formatter.success(f"Portée mise à jour: {self.assistant.memory.scope_show()}")
                return True

            self.formatter.warning("Usage: /scope <show|clear|set k=v ...>")
            return True

        # ----- Raccourcis scope -----
        if cmd.startswith("/ch "):
            ch = cmd.split(" ", 1)[1].strip()
            self.assistant.memory.scope_set(chapter=ch)
            self.formatter.success(f"Chapitre défini: {ch}")
            self.formatter.info("💡 Utilise /blocks pour voir les blocs disponibles")
            return True

        if cmd.startswith("/bloc "):
            try:
                _, rest = cmd.split(" ", 1)
                parts = rest.split()
                if len(parts) < 2:
                    self.formatter.warning("Usage: /bloc <type> <id>")
                    self.formatter.info("Exemples: /bloc theoreme 3.7 | /bloc definition 3.2")
                    return True
                
                kind = parts[0].strip()
                bid = parts[1].strip()
                
                # Normalisation sans accents
                from src.utils import normalize_whitespace
                kind_norm = normalize_whitespace(kind).lower()
                kind_norm = (
                    kind_norm
                    .replace("é", "e").replace("è", "e").replace("ê", "e")
                    .replace("à", "a").replace("ô", "o").replace("û", "u")
                )
                
                self.assistant.memory.scope_set(block_kind=kind_norm, block_id=bid)
                self.formatter.success(f"Bloc défini: {kind_norm} {bid}")
                self.formatter.info("💡 Vérifie avec /show ou /scope show")
            except Exception as e:
                self.formatter.warning("Usage: /bloc <théorème|définition|proposition|corollaire> <id>")
                self.formatter.info(f"Erreur: {e}")
            return True

        if cmd.startswith("/type "):
            t = cmd.split(" ", 1)[1].strip().lower()
            self.assistant.memory.scope_set(type=t)
            self.formatter.success(f"Type défini: {t}")
            return True

        if cmd == "/reset":
            self.assistant.memory.scope_clear()
            self.formatter.success("Portée réinitialisée")
            return True

        # ----- Questions méta -----
        meta_questions = {
            "de quoi on parlait ?", "de quoi on parlait", "on parlait de quoi ?",
            "on parlait de quoi", "quel était le sujet ?", "quel etait le sujet ?",
            "c'etait quoi le sujet", "c'était quoi le sujet", "on était sur quoi",
            "on etait sur quoi"
        }

        if cmd.lower().strip() in meta_questions:
            if self.assistant.memory.state.get("pinned_meta"):
                self.formatter.info(f"Contexte épinglé: {self.assistant.memory.state['pinned_meta']}")
            elif any([
                self.assistant.memory.state.get("last_top_meta"),
                self.assistant.memory.state.get("last_route"),
                self.assistant.memory.state.get("last_question")
            ]):
                self.formatter.info(
                    "Dernier contexte implicite en mémoire courte. "
                    "Utilise /unpin ou /forget pour effacer."
                )
            else:
                self.formatter.info("Aucun contexte actif")
            return True

        # Si ça commence par / mais n'est pas une commande reconnue
        if cmd.startswith("/"):
            return False  # On laisse passer pour gestion des filtres

        return False

    # --------------------------------------------------------------------- #
    #                        FLUX QUESTION → RÉPONSE                        #
    # --------------------------------------------------------------------- #
    def handle_question(self, question: str):
        """Traite une question standard ou avec filtre"""
        filter_type = None

        # Filtres rapides
        if question.startswith("/"):
            parts = question.split(" ", 1)
            if len(parts) == 2:
                cmd, payload = parts[0].lower(), parts[1]

                if cmd == "/exercice":
                    filter_type = "exercice"
                    question = payload
                elif cmd in {"/méthode", "/methode"}:
                    filter_type = "méthode"
                    question = payload
                elif cmd in {"/théorie", "/theorie"}:
                    filter_type = "théorie"
                    question = payload
                elif cmd == "/cours":
                    filter_type = None
                    question = payload
                else:
                    self.formatter.warning(f"Commande inconnue: {cmd}")
                    return
            else:
                self.formatter.warning("Format: /commande <question>")
                return

        # Ne pas afficher "Recherche en cours" ici, on va afficher les étapes en temps réel
        
        # Callback pour afficher les étapes en temps réel
        def progress_callback(step: str, detail: str = ""):
            self.formatter.processing_step(step, detail)

        # Si mode tuteur ou explain activé, intercepter selon le mode
        if self.tutor_mode or self.tutor_explain:
            should_tutor = False
            is_comprehension = False
            q_lower = question.lower()
            
            # Détection des 3 catégories
            # 1. Questions de compréhension (explain/socratique)
            comprehension_keywords = [
                "explique", "expliquer", "comprendre", "comment ça marche",
                "pourquoi", "qu'est-ce que", "quelle est la différence",
                "intuition", "idée derrière", "comprends pas", "pas clair",
                "comment fonctionne", "c'est quoi", "quel est le sens",
                "à quoi ça sert", "interprétation", "signification"
            ]
            
            # 2. Exercices/Démonstrations/Preuves
            exercice_keywords = [
                # Verbes d'action
                "démontrer", "montrer", "prouver", "établir", "justifier",
                "calculer", "résoudre", "déterminer", "trouver", "vérifier",
                # Contexte exercice
                "exercice", "problème", "soit", "on considère", "en déduire",
                # Démonstrations
                "démonstration de", "preuve de", "démonstration du théorème",
                "prouver le théorème", "montrer que le théorème"
            ]
            
            # 3. Questions théoriques pures (rappels)
            theory_keywords = [
                "définition de", "formule de", "énoncé du théorème",
                "rappel de", "quelle est la formule", "liste les propriétés",
                "donne la définition", "rappelle la formule"
            ]
            
            # Analyse de la question
            is_comprehension = any(kw in q_lower for kw in comprehension_keywords)
            is_theory_pure = any(kw in q_lower for kw in theory_keywords)
            is_exercise = any(kw in q_lower for kw in exercice_keywords)
            
            # Forcer tuteur si filter_type est "exercice"
            if filter_type == "exercice":
                is_exercise = True
            
            # Logique de décision selon les modes
            if self.tutor_strict:
                # Mode strict: TOUT en guidage
                should_tutor = True
                tutor_type = "strict"
            elif self.tutor_mode:
                # Mode smart: exercices/démos en guidage, théorie pure normale
                if is_theory_pure and not is_exercise:
                    should_tutor = False  # Réponse normale pour rappels
                elif is_exercise:
                    should_tutor = True
                    tutor_type = "exercice"
                elif is_comprehension and self.tutor_explain:
                    should_tutor = True
                    tutor_type = "explain"
                else:
                    should_tutor = is_exercise
                    tutor_type = "smart"
            elif self.tutor_explain:
                # Mode explain seul: compréhension uniquement
                if is_comprehension:
                    should_tutor = True
                    tutor_type = "explain"
                else:
                    should_tutor = False
            
            if should_tutor:
                # Utiliser la tâche tuteur
                payload = self.assistant.run_task(
                    "tutor",
                    question,
                    filter_type=filter_type,
                    auto_link=self.auto_link,
                    debug=self.debug,
                    auto_pin_next=self.auto_pin_next,
                    with_solutions=False
                )
                self.auto_pin_next = False
                self._capture_backend_debug(payload)
                
                # Afficher un indicateur selon le type
                if tutor_type == "explain" or is_comprehension:
                    self.formatter.info("🧠 Mode tuteur - Guidage socratique (compréhension)")
                elif tutor_type == "strict":
                    self.formatter.info("🎓 Mode tuteur - Guidage pédagogique (strict)")
                else:
                    self.formatter.info("🎓 Mode tuteur - Guidage pédagogique (exercice/démo)")
            else:
                # Mode smart: question théorique → réponse normale
                payload = self.assistant.route_and_execute(
                    question,
                    filter_type,
                    auto_link=self.auto_link,
                    debug=self.debug,
                    auto_pin_next=self.auto_pin_next,
                    allow_oot=self.allow_oot,
                    progress_callback=progress_callback,
                )
                self.auto_pin_next = False
                self._capture_backend_debug(payload)
        else:
            # Mode normal
            payload = self.assistant.route_and_execute(
                question,
                filter_type,
                auto_link=self.auto_link,
                debug=self.debug,
                auto_pin_next=self.auto_pin_next,
                allow_oot=self.allow_oot,
                progress_callback=progress_callback,
            )
            self.auto_pin_next = False
            self._capture_backend_debug(payload)

        # Affichage debug (requête, kwargs, passport, trace LLM)
        if self.debug:
            # Combiner final_kwargs avec final_where pour debug_info
            debug_kwargs = dict(payload.get("final_kwargs", {}))
            debug_kwargs["final_where"] = payload.get("final_where")
            self.formatter.debug_info(
                payload.get("rewritten_q"),
                payload.get("hinted_q"),
                debug_kwargs
            )
            if payload.get("passport"):
                self.formatter.debug_passport(payload["passport"])
            if payload.get("debug_record"):
                self.formatter.debug_trace(payload["debug_record"])

        # Affichage sources
        self.formatter.sources_table(payload["docs"])

        # Affichage réponse
        self.formatter.answer(payload["answer"])

    # --------------------------------------------------------------------- #
    #                              Utils internes                           #
    # --------------------------------------------------------------------- #
    def _capture_backend_debug(self, payload: dict):
        """Capture passport + debug_record si fournis, et propose /passport."""
        self._last_passport = payload.get("passport")
        self._last_debug = payload.get("debug_record")


def main():
    """Point d'entrée du CLI"""
    try:
        cli = MathCLI()
        cli.run()
    except KeyboardInterrupt:
        CLIFormatter.goodbye()
    except Exception as e:
        CLIFormatter.error(f"Erreur fatale: {e}")
        raise


if __name__ == "__main__":
    main()
