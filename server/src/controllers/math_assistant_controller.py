# -*- coding: utf-8 -*-
"""
src/controllers/math_assistant_controller.py
Contrôleur FastAPI pour l'assistant mathématique (orchestration + tasks)
"""
from __future__ import annotations
from typing import Dict, Any, Optional, List, AsyncIterator
import asyncio
import math

from fastapi import APIRouter, Request, HTTPException, Body, Query
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from src.core.rag_engine import get_engine
from src.core.config import rag_config
from src.assistant import get_assistant

router = APIRouter()

# ========= Models =========

class TaskJob(BaseModel):
    task: str = Field(..., description="Nom de tâche (qa, sheet_create, qcm, exam_gen, tutor, ...)")
    question_or_payload: str = Field(..., description="Sujet / question / énoncé")
    filter_type: Optional[str] = Field(None, description="Filtre doc (exercice|méthode|théorie|cours)")
    auto_link: bool = True
    auto_pin_next: bool = False
    # Tous les kwargs spécifiques (level, duration, num_questions, etc.)
    extras: Dict[str, Any] = Field(default_factory=dict)

class TasksBatchRequest(BaseModel):
    jobs: List[TaskJob]

class SheetReviewRequest(BaseModel):
    sheet_text: str

class GradeRequest(BaseModel):
    statement: str
    student_answer: str
    kind: Optional[str] = Field(None, description="exercise|exam (par défaut: exam)")

# ========= Utils =========

def _chunk_stream(s: str, chunk_size: int = 800) -> AsyncIterator[str]:
    async def _agen():
        if not s:
            return
        for i in range(0, len(s), chunk_size):
            yield s[i:i+chunk_size]
            await asyncio.sleep(0)
    return _agen()

async def sse_from_text(text: str):
    async for chunk in _chunk_stream(text):
        yield {"data": chunk}

def _normalize_filter(t: Optional[str]) -> Optional[str]:
    if not t: return None
    t = t.strip().lower()
    return t if t in {"exercice", "méthode", "methode", "théorie", "theorie", "cours"} else None

# ========= Health & diag =========

@router.get("/health")
async def health():
    return {
        "ok": True,
        "version": "3.2.0",
        "model": rag_config.llm_model,
        "embed_model": rag_config.embed_model,
        "reranker_enabled": rag_config.use_reranker
    }

@router.get("/rag_check")
async def rag_check():
    engine = get_engine()
    return {"status": engine.self_check()}

# ========= Orchestration (chat) =========

@router.get("/chat")
async def chat(
    question: str = Query(..., min_length=2, max_length=5000),
    doc_type: Optional[str] = Query(None),
    auto_link: bool = Query(True),
    debug: bool = Query(False),
    auto_pin_next: bool = Query(False),
):
    """
    Orchestration Q&A avec routeur (rag_first / llm_first / rag_to_llm / llm_only).
    """
    assistant = get_assistant()
    filter_type = _normalize_filter(doc_type)

    payload = assistant.route_and_execute(
        question=question,
        filter_type=filter_type,
        auto_link=auto_link,
        debug=debug,
        auto_pin_next=auto_pin_next,
    )

    return EventSourceResponse(
        sse_from_text(payload["answer"]),
        media_type="text/event-stream"
    )

# ========= Tâche générique =========

@router.post("/task")
async def task(job: TaskJob):
    assistant = get_assistant()
    payload = assistant.run_task(
        task=job.task,
        question_or_payload=job.question_or_payload,
        filter_type=_normalize_filter(job.filter_type),
        auto_link=job.auto_link,
        auto_pin_next=job.auto_pin_next,
        **(job.extras or {})
    )
    return EventSourceResponse(
        sse_from_text(payload["answer"]),
        media_type="text/event-stream"
    )

@router.post("/tasks")
async def tasks_batch(batch: TasksBatchRequest):
    assistant = get_assistant()
    jobs = []
    for j in batch.jobs:
        jobs.append({
            "task": j.task,
            "question_or_payload": j.question_or_payload,
            "filter_type": _normalize_filter(j.filter_type),
            "auto_link": j.auto_link,
            "auto_pin_next": j.auto_pin_next,
            **(j.extras or {})
        })
    results = assistant.run_tasks(jobs)
    # On renvoie non-stream (liste d'objets)
    return results

# ========= Alias conviviaux (compat) =========

@router.get("/sheet")
async def sheet(topic: str, level: str = "Prépa", chapter: Optional[str] = None):
    assistant = get_assistant()
    if chapter:
        assistant.set_scope(chapter=chapter)
    payload = assistant.run_task(
        task="sheet_create",
        question_or_payload=topic,
        level=level
    )
    return EventSourceResponse(sse_from_text(payload["answer"]), media_type="text/event-stream")

@router.post("/sheet_review")
async def sheet_review(payload: SheetReviewRequest):
    assistant = get_assistant()
    out = assistant.run_task(
        task="sheet_review",
        question_or_payload="Relecture fiche",
        sheet_text=payload.sheet_text
    )
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")

@router.get("/formula")
async def formula(query: str):
    assistant = get_assistant()
    out = assistant.run_task(task="formula", question_or_payload=query)
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")

@router.get("/exam")
async def exam(chapters: str, duration: str = "3h", level: str = "Prépa"):
    assistant = get_assistant()
    out = assistant.run_task(
        task="exam_gen",
        question_or_payload=f"Exam on chapters: {chapters}",
        chapters=chapters,
        duration=duration,
        level=level
    )
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")

@router.get("/course")
async def course(notion: str, level: str = "Prépa", chapter: Optional[str] = None):
    assistant = get_assistant()
    if chapter:
        assistant.set_scope(chapter=chapter)
    out = assistant.run_task(
        task="course_build",
        question_or_payload=notion,
        level=level
    )
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")

@router.post("/grade")
async def grade(payload: GradeRequest):
    assistant = get_assistant()
    task_name = "exam_correct" if (payload.kind or "exam") == "exam" else "exercise_correct"
    out = assistant.run_task(
        task=task_name,
        question_or_payload="Correction",
        statement=payload.statement,
        student_answer=payload.student_answer,
    )
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")

@router.get("/tutor")
async def tutor(statement: str):
    """Mode Learn & Study : guider pas à pas sans donner la solution."""
    assistant = get_assistant()
    out = assistant.run_task(
        task="tutor",
        question_or_payload=statement,
        with_solutions=False  # sécurité : on n'imprime pas la solution
    )
    return EventSourceResponse(sse_from_text(out["answer"]), media_type="text/event-stream")
