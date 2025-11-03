# -*- coding: utf-8 -*-
"""
server.py
Serveur FastAPI pour l'assistant mathématique RAG
"""
import os
import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.controllers.math_assistant_controller import router
from src.core.config import rag_config

load_dotenv()

app = FastAPI(
    title="Math RAG Teacher API",
    description="API pour l'assistant mathématique avec RAG",
    version="3.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5173", "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers (basics)
@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp: Response = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    # CSP light (SSE friendly)
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; media-src 'self'; connect-src 'self' http://localhost:* http://127.0.0.1:*; frame-ancestors 'none';"
    )
    return resp

app.include_router(router, prefix="/api", tags=["Math Assistant"])

@app.get("/")
async def root():
    return {
        "name": "Math RAG Teacher API",
        "version": "3.2.0",
        "docs": "/docs",
        "health": "/api/health",
        "model": rag_config.llm_model,
        "embed_model": rag_config.embed_model
    }

@app.on_event("startup")
async def startup_event():
    print("🚀 Démarrage du serveur Math RAG Teacher")
    print(f"📚 Modèle LLM: {rag_config.llm_model}")
    print(f"🔢 Modèle d'embeddings: {rag_config.embed_model}")
    print(f"📁 Base vectorielle: {rag_config.db_dir}")
    if rag_config.use_reranker:
        print(f"🎯 Reranker activé: {rag_config.reranker_model}")
    # Pré-chargement
    from src.core.rag_engine import get_engine
    engine = get_engine()
    engine.build_or_load_store()
    print("✅ Moteur RAG initialisé")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Arrêt du serveur Math RAG Teacher")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "true").lower() == "true"
    uvicorn.run("server:app", host=host, port=port, reload=reload, log_level="info")
