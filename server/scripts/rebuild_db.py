#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/rebuild_db.py
Script pour reconstruire la base vectorielle
"""

import sys
import argparse
from pathlib import Path

# Ajouter le répertoire racine au path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.core.rag_engine import get_engine
from src.core.config import rag_config

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    console = Console()
    RICH_OK = True
except ImportError:
    RICH_OK = False
    console = None


def main():
    parser = argparse.ArgumentParser(
        description="Reconstruit la base vectorielle du système RAG"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force la reconstruction sans demander confirmation"
    )
    parser.add_argument(
        "--check-only",
        "-c",
        action="store_true",
        help="Vérifie l'état sans reconstruire"
    )
    
    args = parser.parse_args()
    
    if RICH_OK:
        console.print(Panel.fit(
            "[bold cyan]🔧 Gestion de la base vectorielle[/]",
            border_style="cyan"
        ))
    else:
        print("=" * 60)
        print("🔧 Gestion de la base vectorielle")
        print("=" * 60)
    
    # Afficher la configuration
    if RICH_OK:
        console.print(f"\n[bold]Configuration:[/]")
        console.print(f"  PDF: [cyan]{rag_config.pdf_path}[/]")
        console.print(f"  DB:  [cyan]{rag_config.db_dir}[/]")
        console.print(f"  Embeddings: [yellow]{rag_config.embed_model}[/]")
        console.print(f"  Chunk size: [green]{rag_config.chunk_size}[/]")
        console.print(f"  Overlap: [green]{rag_config.chunk_overlap}[/]")
    else:
        print("\nConfiguration:")
        print(f"  PDF: {rag_config.pdf_path}")
        print(f"  DB:  {rag_config.db_dir}")
        print(f"  Embeddings: {rag_config.embed_model}")
        print(f"  Chunk size: {rag_config.chunk_size}")
        print(f"  Overlap: {rag_config.chunk_overlap}")
    
    # Mode check-only
    if args.check_only:
        if RICH_OK:
            console.print("\n[bold]Vérification du système...[/]")
        else:
            print("\nVérification du système...")
        
        engine = get_engine()
        result = engine.self_check()
        
        if RICH_OK:
            console.print(result)
        else:
            print(result)
        
        return
    
    # Vérifier si la DB existe
    db_exists = rag_config.db_dir.exists()
    
    if db_exists:
        if RICH_OK:
            console.print(f"\n[yellow]⚠️  La base vectorielle existe déjà[/]")
            console.print(f"   Emplacement: {rag_config.db_dir}")
        else:
            print(f"\n⚠️  La base vectorielle existe déjà")
            print(f"   Emplacement: {rag_config.db_dir}")
        
        if not args.force:
            if RICH_OK:
                if not Confirm.ask("Voulez-vous la reconstruire ?", default=False):
                    console.print("\n[dim]Opération annulée[/]")
                    return
            else:
                response = input("\nVoulez-vous la reconstruire ? (y/N): ").strip().lower()
                if response not in {"y", "yes", "o", "oui"}:
                    print("\nOpération annulée")
                    return
    
    # Reconstruction
    if RICH_OK:
        console.print("\n[bold green]🔨 Reconstruction de la base...[/]")
    else:
        print("\n🔨 Reconstruction de la base...")
    
    try:
        engine = get_engine()
        engine.build_or_load_store(force_rebuild=True)
        
        if RICH_OK:
            console.print(Panel.fit(
                "[bold green]✅ Base reconstruite avec succès ![/]",
                border_style="green"
            ))
        else:
            print("\n" + "=" * 60)
            print("✅ Base reconstruite avec succès !")
            print("=" * 60)
        
        # Vérification finale
        if RICH_OK:
            console.print("\n[bold]Vérification finale...[/]")
        else:
            print("\nVérification finale...")
        
        result = engine.self_check()
        
        if RICH_OK:
            console.print(result)
        else:
            print(result)
    
    except Exception as e:
        if RICH_OK:
            console.print(Panel.fit(
                f"[bold red]❌ Erreur: {e}[/]",
                border_style="red"
            ))
        else:
            print(f"\n❌ Erreur: {e}")
        
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()