# -*- coding: utf-8 -*-
"""
scripts/gen_sft_qa.py
Génère des paires Q/A depuis les blocs "théorème/définition/proposition/corollaire".
Sortie: JSONL {"instruction","input","output","meta":{...}}
"""

import os, json, re
import pathlib
from langchain_chroma import Chroma

DB_DIR   = pathlib.Path(os.environ.get("MATH_DB_DIR", "./db/chroma_db_math_v3_1")).resolve()
COLLECTION = os.environ.get("MATH_COLLECTION", "math_course_v3_1")
OUT_PATH = pathlib.Path(os.environ.get("SFT_QA_OUT", "./data/sft_qa.jsonl")).resolve()

def clean(txt: str) -> str:
    # Nettoyage léger (évite d’éjecter les maths)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()

def main():
    store = Chroma(collection_name=COLLECTION, persist_directory=DB_DIR, embedding_function=None)
    rows = store._collection.get(include=["metadatas","documents"])

    count = 0
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for txt, meta in zip(rows.get("documents", []), rows.get("metadatas", [])):
            meta = meta or {}
            kind = (meta.get("block_kind") or "").lower()
            if kind not in {"théorème","définition","proposition","corollaire"}:
                continue
            title = meta.get("block_title") or meta.get("title") or ""
            bid   = meta.get("block_id") or "?"
            chapter = meta.get("chapter") or "?"

            instruction = f"Explique clairement le {kind} {bid} ({title}) du chapitre {chapter}."
            inp = ""  # on peut mettre “extrait brut” si tu veux du closed-book ≠ strict
            out = clean(txt)

            payload = {
                "instruction": instruction,
                "input": inp,
                "output": out,
                "meta": {"chapter": chapter, "block_id": bid, "block_kind": kind, "title": title}
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ Écrit: {OUT_PATH} ({count} items)")

if __name__ == "__main__":
    main()
