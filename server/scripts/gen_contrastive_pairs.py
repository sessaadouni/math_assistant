# -*- coding: utf-8 -*-
"""
scripts/gen_contrastive_pairs.py
Génère des paires (query, positive, negative) pour fine-tuning du cross-encoder.
Sortie: JSONL avec champs: {"query","positive","negative","meta":{...}}
"""

import os, json, random
from collections import defaultdict
from langchain_chroma import Chroma

DB_DIR = os.environ.get("MATH_DB_DIR", "./db/chroma_db_math_v3_1")
COLLECTION = os.environ.get("MATH_COLLECTION", "math_course_v3_1")
OUT_PATH = os.environ.get("RERANKER_PAIRS_OUT", "./data/reranker_pairs.jsonl")

random.seed(42)

def main():
    store = Chroma(collection_name=COLLECTION, persist_directory=DB_DIR, embedding_function=None)
    rows = store._collection.get(include=["metadatas","documents"])

    docs = []
    for txt, meta in zip(rows.get("documents", []), rows.get("metadatas", [])):
        meta = meta or {}
        docs.append({"text": txt, "meta": meta})

    # Regroupe par chapitre et par "mot-clé" grossier depuis le titre de bloc
    by_chapter = defaultdict(list)
    for d in docs:
        ch = d["meta"].get("chapter","?")
        by_chapter[ch].append(d)

    def make_query(meta):
        # ex: "Énonce le théorème 28.7 (fonction de Leibniz, barycentre)."
        kind = meta.get("block_kind")
        bid  = meta.get("block_id")
        bttl = meta.get("block_title") or meta.get("title") or ""
        if kind and bid:
            return f"Énonce le {kind} {bid} ({bttl}).".strip()
        # fallback
        if meta.get("title"):
            return f"Explique: {meta['title']}"
        return "Explique le résultat associé."

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for d in docs:
            meta = d["meta"]
            kind = (meta.get("block_kind") or "").lower()
            if kind not in {"théorème","définition","proposition","corollaire"}:
                continue
            q = make_query(meta)
            pos = d["text"]

            # hard negatives: même chapitre ≠ block_id OU autre chapitre mais titre proche
            c = meta.get("chapter")
            candidates = [x for x in by_chapter.get(c, []) if x["meta"].get("block_id") != meta.get("block_id")]
            if not candidates:
                # fallback autres chapitres
                all_others = [x for x in docs if x is not d]
                candidates = random.sample(all_others, k=min(10, len(all_others)))

            neg = random.choice(candidates)["text"]
            f.write(json.dumps({"query": q, "positive": pos, "negative": neg, "meta": meta}, ensure_ascii=False) + "\n")

    print(f"✅ Écrit: {OUT_PATH}")

if __name__ == "__main__":
    main()
