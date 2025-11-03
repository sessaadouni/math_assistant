# -*- coding: utf-8 -*-
"""
math_assistant_cli.py
CLI minimal basé sur math_assistant_lib.py (mêmes commandes qu’avant).
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import os, time

from lib.math_assistant_lib import (
    ensure_store_ready, retrieve_and_answer, LAST_STATE, SESSION_SCOPE,
    scope_show, scope_set, scope_clear, reset_state, best_context_meta,
    save_log_jsonl, new_chat_id, RICH_OK, console
)

AUTO_LINK = False
DEBUG = False
AUTO_PIN_NEXT = False
CHAT_ID = new_chat_id()

def main():
    ensure_store_ready()

    title = "🎓 ASSISTANT MATHÉMATIQUES – RAG v3.1 (CLI)"
    if RICH_OK:
        from rich.panel import Panel
        console.print(Panel.fit(f"[bold]{title}[/]"))
        console.print("Commandes:\n"
                      "  - tape ta question normalement\n"
                      "  - /exercice <q>   → filtre exercices\n"
                      "  - /méthode <q>    → filtre méthodes\n"
                      "  - /théorie <q>    → filtre théorie\n"
                      "  - /cours <q>      → tout le cours\n"
                      "  - /scope show|clear|set k=v ... (chapter, block_kind, block_id, type)\n"
                      "  - Raccourcis: /ch <num> | /bloc <kind> <id> | /type <t> | /reset\n"
                      "  - /new-chat      (nouveau chat isolé, AUTO_LINK=on + auto-pin du prochain contexte)\n"
                      "  - /link on|off   (activer/désactiver auto-link follow-up)\n"
                      "  - /pin | /unpin  (épingler/désépingler le contexte courant)\n"
                      "  - /forget        (oublier tout le contexte courant)\n"
                      "  - /log save      (sauvegarde du chat en JSONL)\n"
                      "  - /debug on|off  (afficher rewritten/hinted/kwargs)\n"
                      "  - q               → quitter")
    else:
        print(title)

    global AUTO_LINK, DEBUG, AUTO_PIN_NEXT, CHAT_ID

    while True:
        try:
            if RICH_OK:
                console.print("\n" + "─"*70)
                question = console.input("[bold cyan]💬 Ta question[/]: ").strip()
            else:
                print("\n" + "─"*70)
                question = input("💬 Ta question: ").strip()

            if not question:
                continue
            if question.lower() == "q":
                if RICH_OK: console.print("\n👋 Au revoir!")
                else: print("\n👋 Au revoir!")
                break

            # ----- debug -----
            if question.startswith("/debug"):
                parts = question.split()
                if len(parts) == 2 and parts[1].lower() in {"on","off"}:
                    DEBUG = (parts[1].lower() == "on")
                    (console.print if RICH_OK else print)(f"🐞 DEBUG = {DEBUG}")
                else:
                    (console.print if RICH_OK else print)("Usage: /debug on|off")
                continue

            # ----- link -----
            if question.startswith("/link"):
                parts = question.split()
                if len(parts) == 2 and parts[1].lower() in {"on","off"}:
                    AUTO_LINK = (parts[1].lower() == "on")
                    (console.print if RICH_OK else print)(f"🔗 AUTO_LINK = {AUTO_LINK}")
                else:
                    (console.print if RICH_OK else print)("Usage: /link on|off")
                continue

            # pin / unpin / forget
            if question == "/pin":
                LAST_STATE["pinned_meta"] = best_context_meta() or LAST_STATE.get("last_top_meta")
                (console.print if RICH_OK else print)(f"📌 Contexte épinglé: {LAST_STATE['pinned_meta'] or '(aucun)'}")
                continue

            if question == "/unpin":
                LAST_STATE["pinned_meta"] = None
                LAST_STATE["last_top_meta"] = None
                LAST_STATE["last_route"] = None
                LAST_STATE["last_question"] = None
                (console.print if RICH_OK else print)("📌 Contexte désépinglé et état mémorisé réinitialisé (plus aucun contexte actif).")
                continue

            if question == "/forget":
                reset_state(full=True)
                (console.print if RICH_OK else print)("🧹 Mémoire courte et portée nettoyées. Aucun contexte actif.")
                continue

            # new-chat
            if question == "/new-chat":
                reset_state(full=True)
                CHAT_ID = new_chat_id()
                AUTO_LINK = True
                AUTO_PIN_NEXT = True
                (console.print if RICH_OK else print)(
                    f"🆕 Nouveau chat lancé: [bold]{CHAT_ID}[/] — 🔗 AUTO_LINK=ON, 📌 auto-pin sur le prochain contexte."
                )
                continue

            # log
            if question.startswith("/log"):
                parts = question.split()
                if len(parts) == 2 and parts[1] == "save":
                    dirpath = f"./logs/{CHAT_ID}"
                    os.makedirs(dirpath, exist_ok=True)
                    ts = int(time.time())
                    path = f"{dirpath}/{ts}.jsonl"
                    save_log_jsonl(path)
                    (console.print if RICH_OK else print)(f"💾 Log sauvegardé: {path}")
                else:
                    (console.print if RICH_OK else print)("Usage: /log save")
                continue

            # scope
            if question.startswith("/scope"):
                parts = question.split()
                if len(parts) == 1 or parts[1] == "show":
                    (console.print if RICH_OK else print)(f"🔧 Portée: {scope_show()}")
                    continue
                if parts[1] == "clear":
                    scope_clear()
                    (console.print if RICH_OK else print)("✅ Portée réinitialisée")
                    continue
                if parts[1] == "set":
                    kvs: Dict[str, str] = {}
                    for token in parts[2:]:
                        if "=" in token:
                            k, v = token.split("=", 1)
                            k = k.strip().lower(); v = v.strip()
                            if k in {"chapter", "block_kind", "block_id", "type"}:
                                kvs[k] = v
                    scope_set(**kvs)
                    (console.print if RICH_OK else print)(f"✅ Portée mise à jour: {scope_show()}")
                    continue
                (console.print if RICH_OK else print)("❌ /scope <show|clear|set k=v ...>")
                continue

            # Raccourcis
            if question.startswith("/ch "):
                ch = question.split(" ", 1)[1].strip()
                scope_set(chapter=ch)
                (console.print if RICH_OK else print)(f"✅ chapter={ch}")
                continue

            if question.startswith("/bloc "):
                try:
                    _, rest = question.split(" ", 1)
                    kind, bid = rest.split(" ", 1)
                    kind_norm = (kind.lower().replace("é","e").replace("è","e").replace("ê","e"))
                    scope_set(block_kind=kind_norm, block_id=bid.strip())
                    (console.print if RICH_OK else print)(f"✅ bloc: {kind} {bid}")
                except Exception:
                    (console.print if RICH_OK else print)("❌ /bloc <theoreme|definition|proposition|corollaire> <id>")
                continue

            if question.startswith("/type "):
                t = question.split(" ", 1)[1].strip().lower()
                scope_set(type=t)
                (console.print if RICH_OK else print)(f"✅ type={t}")
                continue

            if question == "/reset":
                scope_clear()
                (console.print if RICH_OK else print)("✅ Portée réinitialisée")
                continue

            # Questions méta “de quoi on parlait ?”
            if question.lower().strip() in {
                "de quoi on parlait ?", "de quoi on parlait", "on parlait de quoi ?",
                "on parlait de quoi", "quel était le sujet ?", "quel etait le sujet ?",
                "c’etait quoi le sujet ?", "c'etait quoi le sujet ?", "on était sur quoi ?",
                "on etait sur quoi ?"
            }:
                if LAST_STATE.get("pinned_meta"):
                    (console.print if RICH_OK else print)(f"📌 Contexte épinglé: {LAST_STATE['pinned_meta']}")
                elif LAST_STATE.get("last_top_meta") or LAST_STATE.get("last_route") or LAST_STATE.get("last_question"):
                    (console.print if RICH_OK else print)(
                        "ℹ️ Plus rien n’est épinglé, mais j’ai encore un dernier contexte implicite en mémoire courte.\n"
                        "Utilise /unpin ou /forget pour tout effacer."
                    )
                else:
                    (console.print if RICH_OK else print)("🕳️ Aucun contexte actif. On ne parlait de rien.")
                continue

            # -----------------------------------
            # Filtres rapides
            # -----------------------------------
            filter_type = None
            if question.startswith("/"):
                parts = question.split(" ", 1)
                if len(parts) == 2:
                    cmd, payload = parts[0].lower(), parts[1]
                    if cmd == "/exercice":
                        filter_type = "exercice"; question = payload
                    elif cmd in {"/méthode", "/methode"}:
                        filter_type = "méthode"; question = payload
                    elif cmd in {"/théorie", "/theorie"}:
                        filter_type = "théorie"; question = payload
                    elif cmd == "/cours":
                        filter_type = None; question = payload
                    else:
                        (console.print if RICH_OK else print)(f"❌ Commande inconnue: {cmd}")
                        continue
                else:
                    (console.print if RICH_OK else print)("❌ Format: /commande <question>")
                    continue

            (console.print if RICH_OK else print)("\n🔍 Recherche en cours...")
            payload = retrieve_and_answer(
                question, filter_type,
                auto_link=AUTO_LINK, debug=DEBUG, auto_pin_next=AUTO_PIN_NEXT
            )
            AUTO_PIN_NEXT = False  # utilisé une fois, après /new-chat

            if RICH_OK:
                from rich.panel import Panel
                console.print(Panel.fit("[bold green]📝 Réponse[/]"))
                console.print(payload["answer"])
            else:
                print(payload["answer"])

        except Exception as e:
            if RICH_OK:
                from rich.panel import Panel
                console.print(Panel.fit(f"[bold red]❌ Erreur: {e}[/]"))
            else:
                print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
