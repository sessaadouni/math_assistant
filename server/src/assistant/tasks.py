# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .prompts import (
    PROF_PROMPT, COURSE_BUILD_PROMPT, COURSE_EXPLAIN_PROMPT, COURSE_SUMMARY_PROMPT,
    SHEET_CREATE_PROMPT, SHEET_REVIEW_PROMPT, FORMULA_PROMPT, THEOREM_PROMPT, PROOF_PROMPT,
    EXERCISE_GEN_PROMPT, EXAM_PROMPT, SOLVER_PROMPT, TUTOR_PROMPT, EXO_CORRECTOR_PROMPT,
    EXAM_CORRECTOR_PROMPT, QCM_PROMPT, KHOLLE_PROMPT
)

# Tâches disponibles (tu peux étendre)
TASKS = {
    "qa":                 {"prompt": PROF_PROMPT,            "default_doc_type": None},
    "course_build":       {"prompt": COURSE_BUILD_PROMPT,    "default_doc_type": "cours"},
    "course_explain":     {"prompt": COURSE_EXPLAIN_PROMPT,  "default_doc_type": "cours"},
    "course_summary":     {"prompt": COURSE_SUMMARY_PROMPT,  "default_doc_type": "cours"},
    "sheet_create":       {"prompt": SHEET_CREATE_PROMPT,    "default_doc_type": "cours"},
    "sheet_review":       {"prompt": SHEET_REVIEW_PROMPT,    "default_doc_type": "cours"},
    "formula":            {"prompt": FORMULA_PROMPT,         "default_doc_type": "théorie"},
    "theorem":            {"prompt": THEOREM_PROMPT,         "default_doc_type": "théorie"},
    "proof":              {"prompt": PROOF_PROMPT,           "default_doc_type": "théorie"},
    "exercise_gen":       {"prompt": EXERCISE_GEN_PROMPT,    "default_doc_type": None},
    "exam_gen":           {"prompt": EXAM_PROMPT,            "default_doc_type": None},
    "solve":              {"prompt": SOLVER_PROMPT,          "default_doc_type": None},
    "tutor":              {"prompt": TUTOR_PROMPT,           "default_doc_type": None},
    "exercise_correct":   {"prompt": EXO_CORRECTOR_PROMPT,   "default_doc_type": None},
    "exam_correct":       {"prompt": EXAM_CORRECTOR_PROMPT,  "default_doc_type": None},
    "qcm":                {"prompt": QCM_PROMPT,             "default_doc_type": "cours"},
    "kholle":             {"prompt": KHOLLE_PROMPT,          "default_doc_type": "cours"},
}

def get_prompt(task: str):
    meta = TASKS.get(task) or TASKS["qa"]
    return meta["prompt"], meta["default_doc_type"]
