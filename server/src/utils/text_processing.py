# -*- coding: utf-8 -*-
"""
src/utils/text_processing.py
Utilitaires pour le traitement de texte, LaTeX, Markdown
"""

from __future__ import annotations
import re
from typing import List, Tuple, Optional, Dict, Any
from html import escape as html_escape_builtin


def clean_text(text: str) -> str:
    """
    Nettoie un texte en normalisant les espaces et sauts de ligne.
    
    Args:
        text: Texte brut
    
    Returns:
        Texte nettoyé
    """
    # Remplacer les multiples espaces par un seul
    text = re.sub(r' +', ' ', text)
    # Remplacer les multiples sauts de ligne par maximum 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Supprimer les espaces en début/fin de ligne
    text = '\n'.join(line.strip() for line in text.splitlines())
    return text.strip()


def extract_latex_formulas(text: str) -> List[Tuple[str, str, int, int]]:
    """
    Extrait les formules LaTeX d'un texte.
    
    Args:
        text: Texte contenant du LaTeX
    
    Returns:
        Liste de tuples (type, formula, start_pos, end_pos)
        où type est 'display' ($$...$$) ou 'inline' ($...$)
    """
    formulas = []
    
    # Display math: $$...$$
    for match in re.finditer(r'\$\$(.*?)\$\$', text, re.DOTALL):
        formulas.append(('display', match.group(1).strip(), match.start(), match.end()))
    
    # Inline math: $...$
    for match in re.finditer(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', text):
        formulas.append(('inline', match.group(1).strip(), match.start(), match.end()))
    
    # LaTeX delimiters: \[...\] et \(...\)
    for match in re.finditer(r'\\\[(.*?)\\\]', text, re.DOTALL):
        formulas.append(('display', match.group(1).strip(), match.start(), match.end()))
    
    for match in re.finditer(r'\\\((.*?)\\\)', text):
        formulas.append(('inline', match.group(1).strip(), match.start(), match.end()))
    
    # Trier par position
    return sorted(formulas, key=lambda x: x[2])


def escape_latex_in_text(text: str, placeholder: str = "LATEX_FORMULA_{}") -> Tuple[str, Dict[str, str]]:
    """
    Remplace les formules LaTeX par des placeholders pour traitement séparé.
    
    Args:
        text: Texte avec LaTeX
        placeholder: Template de placeholder
    
    Returns:
        Tuple (texte_avec_placeholders, dict_placeholders)
    """
    formulas = extract_latex_formulas(text)
    replacements = {}
    
    # Remplacer de la fin vers le début pour conserver les positions
    for i, (ftype, formula, start, end) in enumerate(reversed(formulas)):
        key = placeholder.format(len(formulas) - i - 1)
        replacements[key] = (ftype, formula)
        text = text[:start] + key + text[end:]
    
    return text, replacements


def restore_latex_formulas(text: str, replacements: Dict[str, Tuple[str, str]]) -> str:
    """
    Restaure les formules LaTeX depuis les placeholders.
    
    Args:
        text: Texte avec placeholders
        replacements: Dict des placeholders
    
    Returns:
        Texte avec LaTeX restauré
    """
    for placeholder, (ftype, formula) in replacements.items():
        if ftype == 'display':
            text = text.replace(placeholder, f"$${formula}$$")
        else:
            text = text.replace(placeholder, f"${formula}$")
    return text


def markdown_to_html(markdown: str, preserve_latex: bool = True) -> str:
    """
    Convertit du Markdown en HTML (conversion légère).
    Préserve le LaTeX si demandé.
    
    Args:
        markdown: Texte Markdown
        preserve_latex: Si True, préserve les formules LaTeX
    
    Returns:
        HTML généré
    """
    if preserve_latex:
        # Temporairement remplacer le LaTeX
        text, latex_map = escape_latex_in_text(markdown)
    else:
        text = markdown
        latex_map = {}
    
    lines = text.splitlines()
    html_lines = []
    in_code_block = False
    in_list = False
    code_lang = ""
    
    for line in lines:
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                code_lang = stripped[3:].strip()
                lang_class = f' class="language-{code_lang}"' if code_lang else ''
                html_lines.append(f'<pre><code{lang_class}>')
                in_code_block = True
            continue
        
        if in_code_block:
            html_lines.append(html_escape_builtin(line))
            continue
        
        # Headers
        if stripped.startswith('# '):
            html_lines.append(f'<h1>{html_escape_builtin(stripped[2:])}</h1>')
        elif stripped.startswith('## '):
            html_lines.append(f'<h2>{html_escape_builtin(stripped[3:])}</h2>')
        elif stripped.startswith('### '):
            html_lines.append(f'<h3>{html_escape_builtin(stripped[4:])}</h3>')
        elif stripped.startswith('#### '):
            html_lines.append(f'<h4>{html_escape_builtin(stripped[5:])}</h4>')
        
        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{html_escape_builtin(stripped[2:])}</li>')
        
        elif stripped.startswith(tuple(f'{i}. ' for i in range(1, 10))):
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
            content = re.sub(r'^\d+\.\s+', '', stripped)
            html_lines.append(f'<li>{html_escape_builtin(content)}</li>')
        
        # Blockquotes
        elif stripped.startswith('> '):
            content = stripped[2:]
            html_lines.append(f'<blockquote>{html_escape_builtin(content)}</blockquote>')
        
        # Horizontal rule
        elif stripped in ('---', '***', '___'):
            if in_list:
                html_lines.append('</ul>' if html_lines[-2].startswith('<ul>') else '</ol>')
                in_list = False
            html_lines.append('<hr>')
        
        # Empty line
        elif not stripped:
            if in_list:
                html_lines.append('</ul>' if '<ul>' in '\n'.join(html_lines[-5:]) else '</ol>')
                in_list = False
            html_lines.append('<br>')
        
        # Paragraph
        else:
            if in_list:
                html_lines.append('</ul>' if '<ul>' in '\n'.join(html_lines[-5:]) else '</ol>')
                in_list = False
            
            # Inline formatting
            formatted = format_inline_markdown(stripped)
            html_lines.append(f'<p>{formatted}</p>')
    
    # Close any open tags
    if in_code_block:
        html_lines.append('</code></pre>')
    if in_list:
        html_lines.append('</ul>')
    
    html = '\n'.join(html_lines)
    
    # Restaurer le LaTeX
    if preserve_latex:
        html = restore_latex_formulas(html, latex_map)
    
    return html


def format_inline_markdown(text: str) -> str:
    """
    Formate les éléments inline Markdown (gras, italique, code, liens).
    
    Args:
        text: Texte avec Markdown inline
    
    Returns:
        HTML avec formatage inline
    """
    # Code inline
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Bold
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
    
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    return html_escape_builtin(text).replace('&lt;', '<').replace('&gt;', '>')


def wrap_latex_display(formula: str) -> str:
    """
    Entoure une formule LaTeX de délimiteurs display.
    
    Args:
        formula: Formule LaTeX
    
    Returns:
        Formule entourée de $$...$$ si pas déjà présent
    """
    formula = formula.strip()
    if formula.startswith('$$') and formula.endswith('$$'):
        return formula
    if formula.startswith('$') and formula.endswith('$'):
        return f"${formula}$"
    return f"$${formula}$$"


def wrap_latex_inline(formula: str) -> str:
    """
    Entoure une formule LaTeX de délimiteurs inline.
    
    Args:
        formula: Formule LaTeX
    
    Returns:
        Formule entourée de $...$ si pas déjà présent
    """
    formula = formula.strip()
    if formula.startswith('$') and formula.endswith('$'):
        # Enlever les doubles $$ si présents
        if formula.startswith('$$'):
            formula = formula[2:-2]
        else:
            return formula
    return f"${formula}$"


def extract_citations(text: str) -> List[Tuple[str, int]]:
    """
    Extrait les citations de page du type [p.X] ou [page X].
    
    Args:
        text: Texte contenant des citations
    
    Returns:
        Liste de tuples (citation_complète, numéro_page)
    """
    citations = []
    
    # Pattern [p.123] ou [p. 123]
    for match in re.finditer(r'\[p\.?\s*(\d+)\]', text, re.IGNORECASE):
        citations.append((match.group(0), int(match.group(1))))
    
    # Pattern [page 123]
    for match in re.finditer(r'\[page\s+(\d+)\]', text, re.IGNORECASE):
        citations.append((match.group(0), int(match.group(1))))
    
    return citations


def truncate_text(text: str, max_length: int = 200, suffix: str = "…") -> str:
    """
    Tronque un texte intelligemment (à la fin d'un mot).
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter si tronqué
    
    Returns:
        Texte tronqué
    """
    if len(text) <= max_length:
        return text
    
    # Tronquer à max_length puis trouver le dernier espace
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # Au moins 80% de la longueur cible
        truncated = truncated[:last_space]
    
    return truncated.rstrip('.,;:!?') + suffix


def normalize_whitespace(text: str) -> str:
    """
    Normalise les espaces (utile pour la comparaison de textes).
    
    Args:
        text: Texte à normaliser
    
    Returns:
        Texte normalisé
    """
    # Remplacer tous les types d'espaces par des espaces normaux
    text = re.sub(r'[\s\u00a0\u2000-\u200b]+', ' ', text)
    # Supprimer les espaces en début/fin
    return text.strip()


def detect_language(text: str) -> str:
    """
    Détecte la langue d'un texte (français/anglais de base).
    
    Args:
        text: Texte à analyser
    
    Returns:
        Code langue ('fr', 'en', 'unknown')
    """
    text_lower = text.lower()
    
    # Mots français fréquents
    fr_words = ['le', 'la', 'les', 'de', 'et', 'un', 'une', 'des', 'est', 'dans']
    # Mots anglais fréquents
    en_words = ['the', 'is', 'and', 'of', 'a', 'in', 'to', 'that', 'it', 'for']
    
    fr_count = sum(1 for w in fr_words if f' {w} ' in f' {text_lower} ')
    en_count = sum(1 for w in en_words if f' {w} ' in f' {text_lower} ')
    
    if fr_count > en_count:
        return 'fr'
    elif en_count > fr_count:
        return 'en'
    else:
        return 'unknown'


def split_into_sentences(text: str) -> List[str]:
    """
    Découpe un texte en phrases (heuristique simple).
    
    Args:
        text: Texte à découper
    
    Returns:
        Liste de phrases
    """
    # Remplacer les abréviations courantes pour éviter les faux positifs
    text = re.sub(r'\bM\.', 'M§', text)
    text = re.sub(r'\bMme\.', 'Mme§', text)
    text = re.sub(r'\bDr\.', 'Dr§', text)
    text = re.sub(r'\bp\.', 'p§', text)  # page
    text = re.sub(r'\bvol\.', 'vol§', text)
    
    # Découper sur . ! ? suivi d'espace et majuscule
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÉÈÊÀÂ])', text)
    
    # Restaurer les abréviations
    sentences = [s.replace('§', '.') for s in sentences]
    
    return [s.strip() for s in sentences if s.strip()]


def highlight_keywords(text: str, keywords: List[str], tag: str = 'mark') -> str:
    """
    Surligne des mots-clés dans un texte HTML.
    
    Args:
        text: Texte (peut contenir du HTML)
        keywords: Liste de mots-clés à surligner
        tag: Tag HTML à utiliser (default: 'mark')
    
    Returns:
        Texte avec mots-clés surlignés
    """
    for kw in keywords:
        # Échapper le mot-clé pour regex
        pattern = re.escape(kw)
        # Surligner (case insensitive)
        text = re.sub(
            f'({pattern})',
            f'<{tag}>\\1</{tag}>',
            text,
            flags=re.IGNORECASE
        )
    return text


# Alias pour compatibilité
html_escape = html_escape_builtin
md_to_html_light = markdown_to_html