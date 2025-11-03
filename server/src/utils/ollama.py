# -*- coding: utf-8 -*-
"""
src/utils/ollama.py
Utilitaires pour interagir avec Ollama (local et cloud)
"""

from __future__ import annotations
import json
import difflib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from typing import Optional, List, Dict, Any, Tuple


def build_url(host: str, path: str) -> str:
    """
    Construit une URL complète en combinant l'hôte et le chemin.
    
    Args:
        host: URL de base (ex: http://localhost:11434)
        path: Chemin de l'endpoint (ex: /api/tags)
    
    Returns:
        URL complète
    """
    return host.rstrip('/') + '/' + path.lstrip('/')


def add_authorization_header(headers: Dict[str, str], host: str, api_key: Optional[str]) -> Dict[str, str]:
    """
    Ajoute le header d'autorisation si l'hôte est le Cloud Ollama et qu'une clé API est fournie.
    
    Args:
        headers: Dictionnaire de headers existants
        host: URL de l'hôte Ollama
        api_key: Clé API optionnelle
    
    Returns:
        Headers mis à jour
    """
    if host.startswith('https://ollama.com') and api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    return headers


def list_models(host: str, api_key: Optional[str] = None, timeout: int = 10) -> List[str]:
    """
    Retourne la liste des modèles visibles par l'hôte Ollama (local ou Cloud).
    
    Endpoints:
        - Local: http://localhost:11434/api/tags
        - Cloud: https://ollama.com/api/tags (header Authorization requis)
    
    Args:
        host: URL de l'hôte Ollama
        api_key: Clé API pour Cloud Ollama (optionnel)
        timeout: Timeout en secondes pour la requête
    
    Returns:
        Liste des noms de modèles disponibles
    
    Raises:
        RuntimeError: En cas d'échec de la requête
    """
    url = build_url(host, '/api/tags')
    headers = add_authorization_header({}, host, api_key)

    req = Request(url, headers=headers, method='GET')
    
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except HTTPError as e:
        raise RuntimeError(f"Échec de /api/tags (code {e.code}): {e.reason}") from e
    except URLError as e:
        raise RuntimeError(f"Échec de /api/tags: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Réponse JSON invalide de /api/tags: {e}") from e

    out: List[str] = []
    for m in data.get('models', []):
        # L'API renvoie généralement 'name'; certains wrappers utilisent 'model'
        name = m.get('name') or m.get('model')
        if name:
            out.append(name)
    
    return out


def verify_model_exists(host: str, model: str, api_key: Optional[str] = None) -> Tuple[bool, set[str]]:
    """
    Vérifie si un modèle existe sur l'hôte Ollama.
    
    Args:
        host: URL de l'hôte Ollama
        model: Nom du modèle à vérifier
        api_key: Clé API optionnelle
    
    Returns:
        Tuple (existe: bool, ensemble_des_modèles: set[str])
    """
    try:
        models = set(list_models(host, api_key))
        return (model in models, models)
    except RuntimeError:
        # Si l'API n'est pas accessible, on suppose que le modèle n'existe pas
        return (False, set())


def ensure_model_or_exit(host: str, model: str, api_key: Optional[str] = None) -> None:
    """
    Vérifie que le modèle existe, sinon affiche des suggestions et quitte le programme.
    
    Args:
        host: URL de l'hôte Ollama
        model: Nom du modèle requis
        api_key: Clé API optionnelle
    
    Raises:
        SystemExit: Si le modèle n'est pas disponible
    """
    ok, models = verify_model_exists(host, model, api_key)
    
    if ok:
        return
    
    # Suggestions proches (Levenshtein approximée via difflib)
    suggestions = difflib.get_close_matches(model, list(models), n=5, cutoff=0.4)
    
    msg = [
        f"❌ Le modèle '{model}' n'est pas disponible sur {host}.",
        "",
        "📋 Modèles détectés (extrait):"
    ]
    
    # Afficher les 15 premiers modèles triés
    for m in sorted(list(models))[:15]:
        msg.append(f"   • {m}")
    
    if len(models) > 15:
        msg.append(f"   ... et {len(models) - 15} autres")
    
    if suggestions:
        msg.append("")
        msg.append("💡 Suggestions (modèles similaires):")
        for s in suggestions:
            msg.append(f"   • {s}")
    
    msg.append("")
    msg.append("🔧 Pour télécharger un modèle:")
    msg.append(f"   ollama pull {model}")
    
    raise SystemExit("\n".join(msg))


def load_prompt(prompt_file: str) -> str:
    """
    Charge le contenu d'un fichier de prompt.
    
    Args:
        prompt_file: Chemin vers le fichier de prompt
    
    Returns:
        Contenu du fichier
    
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        IOError: En cas d'erreur de lecture
    """
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier de prompt introuvable: {prompt_file}")
    except Exception as e:
        raise IOError(f"Erreur lors de la lecture du prompt: {e}") from e


def check_ollama_health(host: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Vérifie la santé de l'instance Ollama.
    
    Args:
        host: URL de l'hôte Ollama
        timeout: Timeout en secondes
    
    Returns:
        Dictionnaire avec status et informations
        {
            "healthy": bool,
            "version": str | None,
            "models_count": int,
            "error": str | None
        }
    """
    result = {
        "healthy": False,
        "version": None,
        "models_count": 0,
        "error": None
    }
    
    try:
        # Tenter de lister les modèles comme test de santé
        models = list_models(host, timeout=timeout)
        result["healthy"] = True
        result["models_count"] = len(models)
        
        # Optionnel: récupérer la version (si endpoint disponible)
        try:
            version_url = build_url(host, '/api/version')
            req = Request(version_url, method='GET')
            with urlopen(req, timeout=timeout) as resp:
                version_data = json.load(resp)
                result["version"] = version_data.get("version")
        except Exception:
            # Version endpoint peut ne pas exister sur toutes les versions
            pass
            
    except RuntimeError as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = f"Erreur inattendue: {e}"
    
    return result


def format_model_info(model_name: str, detailed: bool = False) -> str:
    """
    Formate les informations d'un modèle pour affichage.
    
    Args:
        model_name: Nom du modèle (ex: "llama2:7b")
        detailed: Si True, parse et affiche les détails
    
    Returns:
        Chaîne formatée
    """
    if not detailed:
        return model_name
    
    # Parser le nom du modèle (format: name:tag ou name)
    parts = model_name.split(':')
    base_name = parts[0]
    tag = parts[1] if len(parts) > 1 else "latest"
    
    # Extraire la taille si présente dans le tag (ex: "7b", "13b")
    size = None
    if any(c.isdigit() for c in tag):
        import re
        size_match = re.search(r'(\d+(?:\.\d+)?[bkm])', tag.lower())
        if size_match:
            size = size_match.group(1).upper()
    
    info_parts = [f"📦 {base_name}"]
    if tag != "latest":
        info_parts.append(f"[tag: {tag}]")
    if size:
        info_parts.append(f"[{size}]")
    
    return " ".join(info_parts)


def get_model_families(models: List[str]) -> Dict[str, List[str]]:
    """
    Regroupe les modèles par famille (nom de base).
    
    Args:
        models: Liste de noms de modèles
    
    Returns:
        Dictionnaire {famille: [tags]}
        Ex: {"llama2": ["7b", "13b", "70b"], ...}
    """
    families: Dict[str, List[str]] = {}
    
    for model in models:
        parts = model.split(':')
        base_name = parts[0]
        tag = parts[1] if len(parts) > 1 else "latest"
        
        if base_name not in families:
            families[base_name] = []
        families[base_name].append(tag)
    
    return families


# Alias pour compatibilité avec l'ancien lib.py
ensure_model = ensure_model_or_exit