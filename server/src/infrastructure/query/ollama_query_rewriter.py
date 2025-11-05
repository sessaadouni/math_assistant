"""
Implémentation du QueryRewriter utilisant Ollama pour la réécriture contextuelle.

Extrait de l'ancien assistant.py (lignes 81-150) avec améliorations SOLID.
"""

from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from src.application.interfaces.query_rewriter import IQueryRewriter
from src.config.settings import Settings


class OllamaQueryRewriter(IQueryRewriter):
    """
    Réécrit les questions de suivi en utilisant un LLM Ollama.
    
    Stratégie:
    ----------
    - Intègre la question précédente dans le prompt
    - Ajoute les métadonnées contextuelles (chapitre, type de bloc)
    - Utilise un modèle léger dédié à la réécriture
    - Conserve la question originale si pas de suivi ou si désactivé
    
    Configuration:
    --------------
    - settings.rag.rewrite_model: Modèle LLM à utiliser (ex: "llama3.2:latest")
    - settings.rag.enable_rewrite: Active/désactive la réécriture (default: True)
    - settings.rag.ollama_host: URL du serveur Ollama
    """
    
    # Template de prompt pour la réécriture (extrait de l'ancien assistant.py)
    REWRITE_PROMPT = """Tu es un assistant d'aide à l'étude.
L'étudiant pose une nouvelle question, potentiellement en lien avec la question précédente.

Question précédente : {last_question}
Nouvelle question : {new_question}
Contexte : {context_desc}

**Mission** : Reformule la nouvelle question pour qu'elle soit **auto-suffisante** (pas de pronoms vagues, pas de "ça", "elle", etc.). Intègre les éléments de la question précédente si nécessaire. Reste proche du sens original.

Reformulation auto-suffisante :"""

    def __init__(
        self,
        settings: Settings,
        llm: Optional[ChatOllama] = None
    ):
        """
        Initialise le service de réécriture.
        
        Parameters
        ----------
        settings : Settings
            Configuration globale (modèle, host, enable_rewrite)
        llm : Optional[ChatOllama]
            Instance LLM pré-configurée (pour testing/injection)
            Si None, crée une instance depuis settings.rag.rewrite_model
        """
        self.settings = settings
        self.enabled = getattr(settings.rag, 'enable_rewrite', True)
        
        # Utiliser l'instance injectée ou créer depuis config
        if llm is not None:
            self.llm = llm
        else:
            # Créer l'instance Ollama pour la réécriture
            model_name = getattr(settings.rag, 'rewrite_model', 'llama3.2:latest')
            base_url = getattr(settings.rag, 'ollama_host', 'http://localhost:11434')
            
            self.llm = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.3,  # Température basse pour réécriture stable
                num_predict=150,  # Limite de tokens (réécriture courte)
            )
        
        # Template de prompt compilé
        self.prompt_template = ChatPromptTemplate.from_template(self.REWRITE_PROMPT)
    
    def rewrite(
        self,
        new_question: str,
        last_question: Optional[str] = None,
        context_meta: Optional[Dict[str, Any]] = None,
        is_follow_up: bool = False
    ) -> str:
        """
        Réécrit une question en intégrant le contexte conversationnel.
        
        Stratégie:
        ----------
        1. Si réécriture désactivée → retourne new_question
        2. Si pas de suivi détecté → retourne new_question
        3. Si pas de question précédente → retourne new_question
        4. Sinon → reformule avec LLM en intégrant contexte
        
        Parameters
        ----------
        new_question : str
            La nouvelle question de l'utilisateur
        last_question : Optional[str]
            La question précédente dans la conversation
        context_meta : Optional[Dict[str, Any]]
            Métadonnées contextuelles (chapter, block_kind, block_id, type)
        is_follow_up : bool
            True si la nouvelle question est détectée comme question de suivi
            
        Returns
        -------
        str
            La question réécrite (ou originale si conditions non remplies)
            
        Examples
        --------
        >>> rewriter = OllamaQueryRewriter(settings)
        >>> result = rewriter.rewrite(
        ...     new_question="Et la différence avec la simple ?",
        ...     last_question="C'est quoi la convergence uniforme ?",
        ...     context_meta={"chapter": "5", "block_kind": "definition"},
        ...     is_follow_up=True
        ... )
        >>> print(result)
        "Quelle est la différence entre la convergence uniforme et la convergence simple ?"
        """
        # Cas 1: réécriture désactivée
        if not self.enabled:
            return new_question
        
        # Cas 2: pas de suivi détecté
        if not is_follow_up:
            return new_question
        
        # Cas 3: pas de question précédente
        if not last_question:
            return new_question
        
        # Cas 4: réécriture avec LLM
        try:
            # Formater la description du contexte
            context_desc = self._describe_meta(context_meta or {})
            
            # Préparer les variables du prompt
            prompt_vars = {
                "last_question": last_question,
                "new_question": new_question,
                "context_desc": context_desc
            }
            
            # Invoquer le LLM
            chain = self.prompt_template | self.llm
            response = chain.invoke(prompt_vars)
            
            # Extraire le contenu de la réponse
            rewritten = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # Fallback si réponse vide
            if not rewritten:
                return new_question
            
            return rewritten
            
        except Exception as e:
            # En cas d'erreur, retourner la question originale
            # (principe de robustesse: ne jamais bloquer l'utilisateur)
            print(f"[QueryRewriter] Erreur lors de la réécriture: {e}")
            return new_question
    
    def _describe_meta(self, meta: Dict[str, Any]) -> str:
        """
        Formate les métadonnées contextuelles pour le prompt.
        
        Extrait de l'ancien assistant.py (méthode describe_meta).
        
        Parameters
        ----------
        meta : Dict[str, Any]
            Métadonnées (chapter, block_kind, block_id, type)
            
        Returns
        -------
        str
            Description textuelle du contexte (ex: "Chapitre 5, Définition")
        
        Examples
        --------
        >>> rewriter._describe_meta({"chapter": "5", "block_kind": "definition"})
        "Chapitre 5, Définition"
        """
        if not meta:
            return "—"
        
        parts = []
        
        # Chapitre
        if "chapter" in meta:
            parts.append(f"Chapitre {meta['chapter']}")
        
        # Type de bloc (definition, theorem, example, etc.)
        if "block_kind" in meta:
            kind = meta["block_kind"]
            # Capitaliser la première lettre
            if kind:
                parts.append(kind.capitalize())
        
        # ID de bloc (si présent)
        if "block_id" in meta:
            parts.append(f"Bloc #{meta['block_id']}")
        
        # Type de document (si présent)
        if "type" in meta and meta["type"]:
            parts.append(f"Type: {meta['type']}")
        
        return ", ".join(parts) if parts else "—"
