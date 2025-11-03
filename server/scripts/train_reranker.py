# -*- coding: utf-8 -*-
"""
scripts/train_reranker.py
Fine-tuning d'un CrossEncoder (sentence-transformers) sur paires positives/négatives.
Entrée: data/reranker_pairs.jsonl
Sortie: dossier modèle (ex: ./models/reranker-local)
"""

import os, json
from typing import List, Dict
from tqdm import tqdm
from datasets import Dataset
from sentence_transformers import InputExample, losses, CrossEncoder
from torch.utils.data import DataLoader

PAIRS_PATH = os.environ.get("RERANKER_PAIRS_IN", "./data/reranker_pairs.jsonl")
MODEL_IN   = os.environ.get("RERANKER_MODEL_IN", "BAAI/bge-reranker-base")
MODEL_OUT  = os.environ.get("RERANKER_MODEL_OUT", "./models/reranker-local")
EPOCHS     = int(os.environ.get("RERANKER_EPOCHS", "1"))
BATCH      = int(os.environ.get("RERANKER_BATCH", "8"))

def load_pairs(path: str):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def build_examples(items: List[Dict]) -> List[InputExample]:
    exs = []
    # Stratégie simple: (q,pos)->label 1.0 et (q,neg)->0.0
    for it in items:
        q, pos, neg = it["query"], it["positive"], it["negative"]
        exs.append(InputExample(texts=[q, pos], label=1.0))
        exs.append(InputExample(texts=[q, neg], label=0.0))
    return exs

def main():
    items = load_pairs(PAIRS_PATH)
    examples = build_examples(items)

    train_loader = DataLoader(examples, shuffle=True, batch_size=BATCH)
    model = CrossEncoder(MODEL_IN, num_labels=1)
    loss = losses.BinaryCrossEntropyLoss(model)

    model.fit(train_dataloader=train_loader, epochs=EPOCHS, warmup_steps=50, show_progress_bar=True)
    os.makedirs(MODEL_OUT, exist_ok=True)
    model.save(MODEL_OUT)
    print(f"✅ Modèle sauvegardé: {MODEL_OUT}")

if __name__ == "__main__":
    main()
