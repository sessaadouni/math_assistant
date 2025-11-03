#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_cli.py
Point d'entrée CLI simplifié
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.ui.cli.app import main

if __name__ == "__main__":
    main()