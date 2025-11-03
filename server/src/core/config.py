# -*- coding: utf-8 -*-
"""
src/core/config.py
Configuration centralisée pour le système RAG (compat rétro avec l'assistant actuel)
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RAGConfig:
    """Configuration du système RAG"""
    
    use_bm25_with_vector: bool = field(default_factory=lambda: os.getenv("USE_BM25_WITH_VECTOR", "0") not in {"0","false","False"})

    # --- Chemins ---
    pdf_path: Path = field(default_factory=lambda: Path(os.getenv("MATH_PDF_PATH", "./model/livre_2011.pdf")))
    db_dir: Path = field(default_factory=lambda: Path(os.getenv("MATH_DB_DIR", "./db/chroma_db_math_v3_1")))
    collection_name: str = field(default_factory=lambda: os.getenv("MATH_COLLECTION_NAME", "math_course_v3_1"))

    # --- Chunking ---
    chunk_size: int = field(default_factory=lambda: int(os.getenv("MATH_CHUNK_SIZE", "1000")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("MATH_CHUNK_OVERLAP", "150")))

    # --- Ollama endpoints ---
    ollama_host_local: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434")))
    ollama_host_cloud: Optional[str] = field(default_factory=lambda: os.getenv("OLLAMA_CLOUD_HOST") or None)
    ollama_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OLLAMA_API_KEY") or None)

    # --- Modèles LLM primaires (déclaratifs) ---
    llm_model_local: str = field(default_factory=lambda: os.getenv("MATH_LLM_LOCAL", "qwen2.5:7b-math"))
    llm_model_cloud: str = field(default_factory=lambda: os.getenv("MATH_LLM_CLOUD", "deepseek-v3.1:671b-cloud"))

    # --- Rewriter ---
    use_rewriter: bool = field(default_factory=lambda: os.getenv("MATH_USE_REWRITER", "1") not in {"0", "false", "False"})
    llm_rewriter_local: str = field(default_factory=lambda: os.getenv("MATH_LLM_REWRITER_LOCAL", "gemma3:4b"))
    llm_rewriter_cloud: str = field(default_factory=lambda: os.getenv("MATH_LLM_REWRITER_CLOUD", "glm-4.6:cloud"))

    # --- Embeddings ---
    embed_model_primary: str = field(default_factory=lambda: os.getenv("EMBED_PRIMARY_MODEL_NAME", "bge-m3:latest"))
    embed_model_alt: str = field(default_factory=lambda: os.getenv("EMBED_ALT_MODEL_NAME", "mxbai-embed-large:latest"))

    # --- Reranker ---
    use_reranker: bool = field(default_factory=lambda: os.getenv("MATH_USE_RERANKER", "1") not in {"0", "false", "False"})
    reranker_model: str = field(default_factory=lambda: os.getenv("MATH_RERANKER_MODEL", "bge-reranker-v2-m3:latest"))

    # --- Routeur — seuils ---
    router_threshold_rag_first: float = field(default_factory=lambda: float(os.getenv("ROUTER_RAG_FIRST", "0.55")))
    router_threshold_llm_first: float = field(default_factory=lambda: float(os.getenv("ROUTER_LLM_FIRST", "0.35")))
    
    # --- Routeur — poids & pénalités (NOUVEAU) ---
    # Poids des signaux (seront renormalisés pour sum=1.0)
    router_w_sim:    float = field(default_factory=lambda: float(os.getenv("ROUTER_W_SIM",    "0.65")))
    router_w_struct: float = field(default_factory=lambda: float(os.getenv("ROUTER_W_STRUCT", "0.20")))
    router_w_kw:     float = field(default_factory=lambda: float(os.getenv("ROUTER_W_KW",     "0.075")))
    router_w_pin:    float = field(default_factory=lambda: float(os.getenv("ROUTER_W_PIN",    "0.075")))
    # Pénalités si contexte faible
    router_weak_penalty:        float = field(default_factory=lambda: float(os.getenv("ROUTER_WEAK_PENALTY",        "0.20")))
    router_weak_penalty_focus:  float = field(default_factory=lambda: float(os.getenv("ROUTER_WEAK_PENALTY_FOCUS",  "0.10")))

    # --- Runtime ---
    # local | cloud | hybrid  (hybrid = cloud en primaire + local en fallback)
    runtime_default_mode: str = field(default_factory=lambda: os.getenv("RUNTIME_MODE", "hybrid"))

    # --- Champs dérivés (compat avec le code existant) ---
    # *Ces champs sont remplis en __post_init__ selon le runtime_default_mode*
    ollama_host: str = ""                 # utilisé par l'assistant actuel
    llm_model: str = ""                   # modèle primaire
    llm_local_fallback: Optional[str] = None
    enable_rewrite: bool = False
    rewrite_model: Optional[str] = None

    def __post_init__(self):
        # Chemins
        self.pdf_path = self.pdf_path.resolve()
        self.db_dir = self.db_dir.resolve()
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF introuvable: {self.pdf_path}")

        # Runtime resolution
        mode = (self.runtime_default_mode or "hybrid").lower()
        if mode not in {"local", "cloud", "hybrid"}:
            mode = "hybrid"

        # Host actif
        if mode == "local":
            self.ollama_host = self.ollama_host_local
        elif mode == "cloud":
            if not self.ollama_host_cloud:
                raise ValueError("Mode 'cloud' sélectionné mais OLLAMA_CLOUD_HOST non défini.")
            self.ollama_host = self.ollama_host_cloud
        else:  # hybrid
            # primaire = cloud si dispo, sinon local
            self.ollama_host = self.ollama_host_cloud or self.ollama_host_local

        # LLM primaire + fallback (compat assistant actuel)
        if mode == "local":
            self.llm_model = self.llm_model_local
            self.llm_local_fallback = None
        elif mode == "cloud":
            self.llm_model = self.llm_model_cloud
            # en cloud pur, on peut mettre le local en secours si souhaité :
            self.llm_local_fallback = self.llm_model_local
        else:  # hybrid
            self.llm_model = self.llm_model_cloud if self.ollama_host_cloud else self.llm_model_local
            self.llm_local_fallback = self.llm_model_local if self.llm_model != self.llm_model_local else None

        # Rewriter (compat : enable_rewrite + rewrite_model)
        self.enable_rewrite = bool(self.use_rewriter)
        if self.use_rewriter:
            if mode == "local":
                self.rewrite_model = self.llm_rewriter_local
            elif mode == "cloud":
                self.rewrite_model = self.llm_rewriter_cloud
            else:  # hybrid
                self.rewrite_model = self.llm_rewriter_cloud or self.llm_rewriter_local
        else:
            self.rewrite_model = None
            
        # Normalisation des poids (sum=1.0, protection valeurs <=0)
        ws = [max(0.0, self.router_w_sim), max(0.0, self.router_w_struct),
              max(0.0, self.router_w_kw),  max(0.0, self.router_w_pin)]
        s = sum(ws) or 1.0
        self.router_w_sim, self.router_w_struct, self.router_w_kw, self.router_w_pin = [w/s for w in ws]


@dataclass
class UIConfig:
    """Configuration interface utilisateur"""

    # CLI
    cli_rich_enabled: bool = True
    cli_auto_link: bool = False
    cli_debug: bool = False
    cli_allow_oot: bool = True

    # GUI
    gui_width: int = 1200
    gui_height: int = 800
    gui_sidebar_width: int = 330
    gui_dark_theme: bool = True

    # Logs
    log_dir: Path = field(default_factory=lambda: Path("./logs/chat_logs/"))
    debug_dir: Path = field(default_factory=lambda: Path("./logs/debug/"))

    def __post_init__(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir.mkdir(parents=True, exist_ok=True)


# Instances globales
rag_config = RAGConfig()
ui_config = UIConfig()
