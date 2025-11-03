#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/run_gui.py
Point d'entrée GUI simplifié
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.ui.gui.app import main

if __name__ == "__main__":
    main()