"""
Interface pour les services de réécriture de requêtes.

La réécriture contextuelle améliore la qualité du retrieval en
reformulant les questions utilisateur avec le contexte conversationnel.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IQueryRewriter(ABC):
    """
    Interface pour la réécriture contextuelle de requêtes.
    
    Principe:
    ---------
    Reformule les questions de suivi en intégrant le contexte de la
    conversation (question précédente, métadonnées, scope) pour obtenir
    des requêtes auto-suffisantes qui fonctionnent mieux avec le retrieval.
    
    Exemple:
    --------
    Q1: "C'est quoi la convergence uniforme ?"
    Q2: "Quelle est la différence avec la convergence simple ?"
    
    → Réécriture: "Quelle est la différence entre la convergence uniforme
       et la convergence simple en analyse ?"
    """
    
    @abstractmethod
    def rewrite(
        self,
        new_question: str,
        last_question: Optional[str] = None,
        context_meta: Optional[Dict[str, Any]] = None,
        is_follow_up: bool = False
    ) -> str:
        """
        Réécrit une question en intégrant le contexte conversationnel.
        
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
            La question réécrite (auto-suffisante pour le retrieval)
            
        Notes
        -----
        - Si is_follow_up=False ou last_question=None: retourne new_question telle quelle
        - Si is_follow_up=True: reformule en intégrant le contexte
        - La réécriture peut être désactivée via configuration
        """
        pass
