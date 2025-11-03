#!/bin/bash
# Script pour lancer le backend sans watcher les fichiers du client

cd "$(dirname "$0")"
uvicorn server:app --reload --reload-exclude 'client/*' --reload-exclude 'chroma_db*' --reload-exclude '__pycache__'
