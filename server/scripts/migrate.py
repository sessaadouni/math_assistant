#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/migrate.py
Script de migration automatique de l'ancien code vers la nouvelle structure
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple

# Couleurs pour le terminal
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def print_step(msg: str):
    print(f"{Colors.CYAN}▶{Colors.RESET} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def check_file_exists(path: Path) -> bool:
    """Vérifier si un fichier existe"""
    return path.exists() and path.is_file()

def check_dir_exists(path: Path) -> bool:
    """Vérifier si un dossier existe"""
    return path.exists() and path.is_dir()

def create_dir(path: Path):
    """Créer un dossier s'il n'existe pas"""
    path.mkdir(parents=True, exist_ok=True)

def copy_file_if_missing(src: Path, dst: Path, description: str):
    """Copier un fichier si la destination n'existe pas"""
    if dst.exists():
        print_info(f"{description} existe déjà : {dst}")
        return False
    
    if not src.exists():
        print_error(f"{description} source introuvable : {src}")
        return False
    
    create_dir(dst.parent)
    shutil.copy2(src, dst)
    print_success(f"{description} copié : {dst}")
    return True

def create_init_files(base_path: Path) -> List[Path]:
    """Créer tous les fichiers __init__.py nécessaires"""
    init_files = [
        base_path / "src" / "__init__.py",
        base_path / "src" / "core" / "__init__.py",
        base_path / "src" / "assistant" / "__init__.py",
        base_path / "src" / "controllers" / "__init__.py",
        base_path / "src" / "utils" / "__init__.py",
        base_path / "src" / "ui" / "__init__.py",
        base_path / "src" / "ui" / "cli" / "__init__.py",
        base_path / "src" / "ui" / "gui" / "__init__.py",
    ]
    
    created = []
    for init_file in init_files:
        if not init_file.exists():
            create_dir(init_file.parent)
            init_file.write_text('# -*- coding: utf-8 -*-\n')
            created.append(init_file)
    
    return created

def make_executable(path: Path):
    """Rendre un fichier exécutable"""
    if path.exists():
        os.chmod(path, 0o755)
        return True
    return False

def main():
    """Fonction principale de migration"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  Migration Math RAG v3.1{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # Déterminer le répertoire racine
    script_path = Path(__file__).resolve()
    root = script_path.parent.parent
    
    print_info(f"Répertoire racine : {root}\n")
    
    # ===== Étape 1 : Vérifier la structure =====
    print_step("Étape 1/6 : Vérification de la structure existante")
    
    required_dirs = {
        "before": root / "before",
        "src": root / "src",
        "scripts": root / "scripts",
        "model": root / "model",
    }
    
    missing_dirs = []
    for name, path in required_dirs.items():
        if check_dir_exists(path):
            print_success(f"Dossier '{name}' trouvé")
        else:
            print_error(f"Dossier '{name}' manquant : {path}")
            missing_dirs.append(name)
    
    if missing_dirs:
        print_error(f"\nDossiers manquants : {', '.join(missing_dirs)}")
        print_info("Veuillez créer ces dossiers avant de relancer la migration.")
        return 1
    
    print()
    
    # ===== Étape 2 : Copier les fichiers essentiels =====
    print_step("Étape 2/6 : Copie des fichiers essentiels")
    
    # Copier prompts.py
    prompts_src = root / "before" / "prompts.py"
    prompts_dst = root / "src" / "assistant" / "prompts.py"
    copy_file_if_missing(prompts_src, prompts_dst, "Fichier prompts.py")
    
    # Vérifier le PDF
    pdf_path = root / "model" / "livre_2011.pdf"
    if check_file_exists(pdf_path):
        print_success(f"PDF trouvé : {pdf_path}")
    else:
        print_error(f"PDF manquant : {pdf_path}")
        print_warning("Le système RAG ne pourra pas fonctionner sans le PDF.")
    
    print()
    
    # ===== Étape 3 : Créer les __init__.py =====
    print_step("Étape 3/6 : Création des fichiers __init__.py")
    
    created_inits = create_init_files(root)
    if created_inits:
        for init_file in created_inits:
            print_success(f"__init__.py créé : {init_file.relative_to(root)}")
    else:
        print_info("Tous les __init__.py existent déjà")
    
    print()
    
    # ===== Étape 4 : Rendre les scripts exécutables =====
    print_step("Étape 4/6 : Configuration des permissions")
    
    executable_files = [
        root / "start_all.sh",
        root / "start_backend.sh",
        root / "scripts" / "run_cli.py",
        root / "scripts" / "run_gui.py",
        root / "scripts" / "diagnostic.py",
        root / "scripts" / "rebuild_db.py",
    ]
    
    for exe_file in executable_files:
        if make_executable(exe_file):
            print_success(f"Permissions configurées : {exe_file.name}")
        else:
            print_warning(f"Fichier non trouvé : {exe_file.name}")
    
    print()
    
    # ===== Étape 5 : Créer .env si nécessaire =====
    print_step("Étape 5/6 : Configuration de l'environnement")
    
    env_example = root / ".env.example"
    env_file = root / ".env"
    
    if env_file.exists():
        print_info(f"Fichier .env existe déjà")
    elif env_example.exists():
        answer = input(f"{Colors.YELLOW}?{Colors.RESET} Créer .env depuis .env.example? (o/N) : ").strip().lower()
        if answer in ['o', 'oui', 'y', 'yes']:
            shutil.copy2(env_example, env_file)
            print_success(f"Fichier .env créé")
            print_warning("N'oubliez pas d'éditer .env avec vos propres valeurs!")
        else:
            print_info("Création de .env ignorée")
    else:
        print_warning("Fichier .env.example introuvable")
        print_info("Vous devrez créer .env manuellement")
    
    print()
    
    # ===== Étape 6 : Vérifier les imports =====
    print_step("Étape 6/6 : Vérification des imports")
    
    test_imports = [
        ("Configuration", "from src.core.config import rag_config, ui_config"),
        ("RAG Engine", "from src.core.rag_engine import RAGEngine"),
        ("Assistant", "from src.assistant.assistant import MathAssistant"),
        ("Contrôleur", "from src.controllers.math_assistant_controller import MathAssistantController"),
    ]
    
    all_ok = True
    for name, import_stmt in test_imports:
        try:
            exec(import_stmt)
            print_success(f"Import {name} OK")
        except Exception as e:
            print_error(f"Import {name} échoué : {e}")
            all_ok = False
    
    print()
    
    # ===== Résumé =====
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}  Résumé de la migration{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    if all_ok:
        print_success("Migration réussie ! ✨")
        print()
        print_info("Prochaines étapes :")
        print(f"  1. Éditer {Colors.CYAN}.env{Colors.RESET} avec vos valeurs")
        print(f"  2. Lancer {Colors.CYAN}python scripts/diagnostic.py{Colors.RESET}")
        print(f"  3. Tester le CLI : {Colors.CYAN}python scripts/run_cli.py{Colors.RESET}")
        print(f"  4. Tester le GUI : {Colors.CYAN}python scripts/run_gui.py{Colors.RESET}")
        print()
        return 0
    else:
        print_error("Migration incomplète")
        print()
        print_info("Actions recommandées :")
        print(f"  1. Vérifier que tous les fichiers sont en place")
        print(f"  2. Installer les dépendances : {Colors.CYAN}uv pip install -e .{Colors.RESET}")
        print(f"  3. Relancer la migration : {Colors.CYAN}python scripts/migrate.py{Colors.RESET}")
        print()
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Migration interrompue{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Erreur fatale : {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)