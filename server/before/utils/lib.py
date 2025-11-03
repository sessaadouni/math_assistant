# lib.py

import json
import difflib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def build_url(host: str, path: str) -> str:
  """
  Construit une URL complète en combinant l'hôte et le chemin.
  """
  return host.rstrip('/') + '/' + path.lstrip('/')
  
def add_authorization_header(headers: dict, host: str, api_key: str | None) -> dict:
  """
  Ajoute le header d'autorisation si l'hôte est le Cloud Ollama et qu'une clé API est fournie.
  """
  if host.startswith('https://ollama.com') and api_key: headers['Authorization'] = 'Bearer ' + api_key
  return headers


def list_models(host: str, api_key: str | None = None, timeout: int = 10) -> list[str]:
  """
  Retourne la liste des modèles visibles par l'hôte Ollama (local ou Cloud).
  - Local: http://localhost:11434/api/tags
  - Cloud: https://ollama.com/api/tags (header Authorization requis)
  """
  url = build_url(host, '/api/tags')
  headers = add_authorization_header({}, host, api_key)

  req = Request(url, headers=headers, method='GET')
  try:
    with urlopen(req, timeout=timeout) as resp: data = json.load(resp)
  except HTTPError as e: raise RuntimeError(f"Echec /api/tags ({e.code}): {e.reason}") from e
  except URLError as e: raise RuntimeError(f"Echec /api/tags: {e.reason}") from e

  out: list[str] = []
  for m in data.get('models', []):
    # L'API renvoie généralement 'name'; certains wrappers utilisent 'model'
    name = m.get('name') or m.get('model')
    if name: out.append(name)
  return out


def verify_model_exists(host: str, model: str, api_key: str | None = None) -> tuple[bool, set[str]]:
  """
  Vérifie si un modèle existe sur l'hôte Ollama.
  Retourne un tuple (existe: bool, ensemble_des_modèles: set[str])
  """
  models = set(list_models(host, api_key))
  return (model in models, models)


def ensure_model_or_exit(host: str, model: str, api_key: str | None = None) -> None:
  """
  Vérifie que le modèle existe, sinon affiche des suggestions et quitte le programme.
  """
  ok, models = verify_model_exists(host, model, api_key)
  if ok: return
  # Suggestions proches (levenshtein approximée via difflib)
  suggestions = difflib.get_close_matches(model, list(models), n=5, cutoff=0.4)
  msg = [
    f"Le modèle '{model}' n'est pas disponible sur {host}.",
    "Modèles détectés (extraits):"
  ]
  for m in sorted(list(models))[:15]: msg.append(f"  - {m}")
  if suggestions: msg.append("\nAs-tu voulu dire : " + ", ".join(suggestions))
  raise SystemExit("\n".join(msg))


def load_prompt(prompt_file: str) -> str:
  """
  Charge le contenu d'un fichier de prompt.
  """
  with open(prompt_file, 'r', encoding='utf-8') as f: return f.read()
