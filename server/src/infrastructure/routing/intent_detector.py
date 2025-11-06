# -*- coding: utf-8 -*-
"""
Intent Detection for Math RAG Assistant (SOLID Architecture).

This module handles intent classification and special task detection.
Migrated from src/assistant/router.py to follow SOLID principles.
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import re
import unicodedata

from rapidfuzz import fuzz


# -------------------------
# Regex/Keywords (ASCII normalized)
# -------------------------

# Out-of-syllabus / extension patterns
OUT_OF_SYLLABUS_KW = (
    r"\bhors(\s|-)?programmes?\b",
    r"\benhors\b.*\bprogrammes?\b",
    r"\ben\s+dehors\s+du\s+programme\b",
    r"\bextra(\s|-)?programmes?\b",
    r"\b(out|off)\s+syllabus\b",
    r"\bau(\s|-)?del[àa]\b",
    r"\bau(\s|-)?del[àa]\s+du\s+cours\b",
    r"\bapprofondissements?\b",
    r"\bextension\s+du\s+cours\b",
    r"\bsuite\s+du\s+cours\b",
    r"\bniveau\s+(avanc[ée]|\+|sup[ée]rieur)\b",
    r"\bpreuve\s+alternative\b",
    r"\bpreuve\s+(hors(\s|-)?programme|non\s+au\s+programme)\b",
    r"\bnon\s+au\s+programme\b",
)

# Book/document-related patterns
BOOK_KW = (
    r"\blivre\b", r"\bmanuel\b", r"\bouvrage\b", r"\bpdf\b",
    r"\bchapitre[s]?\b", r"\bsection[s]?\b", r"\bpage[s]?\b",
    r"\benonce[s]?\b", r"\btheoreme[s]?\b", r"\bdefinition[s]?\b",
    r"\bproposition[s]?\b", r"\bcorollaire[s]?\b",
    r"\bexercice[s]?\b", r"\bsommaire\b", r"\btable\s+des\s+matieres\b",
)

# Math keywords (content signal)
MATH_KW = (
    r"\bderiv[ee]e?s?\b", r"\bintegrale?s?\b", r"\blimite?s?\b",
    r"\bserie?s?\b", r"\bsuite?s?\b", r"\bprobabilit[ee]s?\b",
    r"\bmatrice[s]?\b", r"\bdeterminant\b", r"\bvaleurs?\s*propres?\b",
    r"\btheoreme[s]?\b", r"\bdefinition[s]?\b", r"\bcorollaire[s]?\b", r"\blemme[s]?\b",
    r"\bfonction[s]?\b", r"\bcontinuite\b", r"\bconvergence\b",
    r"\bgradient\b", r"\bvectoriel(le)?\b", r"\banal(?:yse|ytique)\b",
    r"\b(d[ée]riv[ée]s?|int[ée]grales?|limites?)\b",
    r"\bmatric(?:e|es)\b|\bendomorphisme\b|\bpolyn[oô]me\b",
    r"[=+\-*/^×·⋅÷±∓]",  # Arithmetic operators
    r"[=≠≤≥≪≫≡≢≈≃≅∝]",  # Relations
    r"[∫∑∏∮√∂∇∆∞]",  # Calculus operators
    r"[∈∉∀∃∄∅∪∩⊂⊆⊃⊇⊄⊅⊕⊗]",  # Set theory
    r"[→⇒⇔↦←⇐↔∘]",  # Arrows
    r"[⟂∥∠∴∵°′″]",  # Geometry
    r"[ℕℤℚℝℂℙ]",  # Number sets
    r"[αβγδεζηθικλμνξπρστφχψω]",  # Greek lowercase
    r"[ΓΔΘΛΞΠΣΦΨΩ]",  # Greek uppercase
)

# Intent patterns (priority order: highest to lowest)
INTENT_PATTERNS: List[Tuple[str, Tuple[str, ...]]] = [
    ("qcm", (
        r"\bqcm\b",
        r"\bquiz{1,2}\b",
        r"\bmcq\b",
        r"\b(vrai|faux)\b",
        r"\bchoix\s+multiple[s]?\b",
        r"\bquestions?\s+[àa]\s+choix\b",
        r"\btest\b",
    )),
    ("kholle", (
        r"\bkh[ôo]lle\b",
        r"\bcolle\b",
        r"\boral(?:\s+court)?\b",
        r"\binterro\s+orale\b",
    )),
    ("exam_gen", (
        r"\b(examen|partiel|concours|[ée]preuve)\b",
        r"\bsujet\s+(d['e]\s*)?(examen|partiel|concours)\b",
        r"\bdevoir\s+surveill[ée]\b",
        r"\bD\.?S\.?\b",
        r"\bbar[èe]me\b",
        r"\bnotation\b",
    )),
    ("exercise_gen", (
        r"\b(g[ée]n[ée]r(?:e|ez|er))\b.*\b(exos?|exercices?|probl[èe]mes?)\b",
        r"\b(cr[ée]e?|compose|fabrique|propose)\b.*\b(exos?|exercices?)\b",
        r"\b(exos?|exercices?)\s+originaux\b",
        r"\bentrainement\b|\bentraînement\b",
    )),
    ("solve", (
        r"\br[ée]souds?\b|\br[ée]soudre\b",
        r"\bsolution\b.*\b(exo|exercice|probl[èe]me)\b",
        r"\b(calcul(e|er|ez)|d[ée]termine[rz]?|trouve[rz]?|r[ée]solve[rz]?)\b",
        r"\bint[ée]gr(e|er|ez)\b|\bd[ée]riv(e|er|ez)\b|\blimite\b",
        r"\b(diagonalise[rz]?|r[ée]duis[ez]?|factorise[rz]?)\b",
        r"\b(r[ée]soudre|solution)\s+(ce|cet|cette)\b",
    )),
    ("tutor", (
        r"\baide\s*-\s?moi\b.*\bpas\s*[àa]\s*pas\b",
        r"\baide\b.*\bpas\s*[àa]\s*pas\b",
        r"\bguid[ea]\b|\bguidage\b|\baccompagnement\b",
        r"\bindices?\b|\bpistes?\b|\bsuggestions?\b",
        r"\b(ne|n[''])\s*me\s*(donne|donnes)\s*pas\s*(la|de)\s*(r[ée]ponse|solution)\b",
        r"\bsans\s*(donner|divulguer)\s*(la|de)\s*(r[ée]ponse|solution)\b",
        r"\bjuste\s*des\s*indices\b",
        r"\bpose[-\s]*moi\s*des\s*questions\b|\bm['']interroger\b",
        r"\b(m[ée]thode|approche)\s+socratique\b|\bsocratic\b",
        r"\bpas\s*la\s*solution\b",
        r"\bplan\s+d['e]\s*attaque\b|\b[ée]tapes?\s+cl[ée]s?\b",
    )),
    ("exercise_correct", (
        r"\bcorrige\b.*\b(exo|exercice|probl[èe]me)\b",
        r"\bfeedback\b.*\b(exo|exercice)\b",
        r"\b(analy[s|z]e|[ée]value)\b.*\b(exo|exercice)\b",
    )),
    ("exam_correct", (
        r"\bcorrige\b.*\b(examen|[ée]preuve|partiel|concours|D\.?S\.?)\b",
        r"\b(note|notation)\b.*\b(/?\s*20|sur\s*20)\b",
        r"\bm[ée]tris\b.*\bbar[èe]me\b|\bbar[èe]mise\b",
    )),
    ("course_summary", (
        r"\br[ée]sum[ée]\b",
        r"\bsynth[èe]se\b",
        r"\br[ée]cap(itulatif)?\b|\ben\s+bref\b|\baper[çc]u\b",
    )),
    ("sheet_create", (
        r"\bfiche[s]?\b",
        r"\bfiche\s+de\s+r[ée]vision\b",
        r"\baide-?m[ée]moire\b|\bm[ée]mo\b|\bcheat\s*sheet\b",
        r"\bfiche\s+synth[èe]se\b",
    )),
    ("sheet_review", (
        r"\b(v[ée]rifie|relis|am[ée]liore|critique|audit)\b.*\bfiche\b",
        r"\breview\b.*\bfiche\b",
        r"\b[ée]value\b.*\bfiche\b",
    )),
    ("course_build", (
        r"\b(fais|construis|r[ée]dige|[ée]cris)\b.*\bcours\b",
        r"\bcours\s+complet\b|\bmini-?cours\b|\ble[çc]on\b|\bchapitre\s+complet\b",
        r"\bplan\s+de\s+cours\b",
    )),
    ("course_explain", (
        r"\bm['']explique\b|\bexplique\b.*\b(cours|notion|chapitre)\b",
        r"\brends?\s*(cela|ceci|[çc]a)?\s*(intuitif|clair)\b",
        r"\bELI5\b|\bexplique\s+simplement\b",
        r"\b(p[ée]dagogie|p[ée]dagogique)\b",
    )),
    ("formula", (
        r"\bformule[s]?\b|\bformulaire\b",
        r"\b[ée]quation[s]?\b",
        r"\bidentit[ée]s?\b|\bd[ée]veloppements?\b|\brelation[s]?\b",
        r"\bloi[s]?\b",
    )),
    ("theorem", (
        r"\bth[ée]or[èe]me[s]?\b",
        r"\bpropri[ée]t[ée]s?\b|\bcorollaire[s]?\b|\blemme[s]?\b|\baxiome[s]?\b|\bprincipe[s]?\b",
    )),
    ("proof", (
        r"\bpreuve[s]?\b|\bd[ée]monstration[s]?\b",
        r"\b(d[ée]montre|prouve|montre|justifie|[ée]tablis?)\s+que\b",
        r"\bargumente\b|\braisonne\b",
    )),
    ("qa", (r".*",)),  # Fallback
]


# -------------------------
# Intent Detector
# -------------------------

class IntentDetector:
    """
    Detects user intent and task type from normalized query text.
    
    Responsibilities:
    - Pattern matching for 17 task types
    - Special intent detection (book/out-of-syllabus)
    - Math content signal detection
    - Intent scoring with fuzzy matching fallback
    """
    
    def __init__(self) -> None:
        self._intent_patterns = INTENT_PATTERNS
        self._intent_order = [task for task, _ in INTENT_PATTERNS]
        
    @staticmethod
    def _strip_accents(text: str) -> str:
        """Remove accents from text (é → e, à → a, etc.)."""
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text: strip accents, lowercase, collapse whitespace."""
        text = IntentDetector._strip_accents(text or "")
        text = text.lower()
        return " ".join(text.split())
    
    @staticmethod
    def _regex_hit(patterns: Tuple[str, ...], text: str) -> bool:
        """Check if any regex pattern matches the normalized text."""
        return any(re.search(pattern, text) for pattern in patterns)
    
    def detect_intent(self, query: str) -> Tuple[str, Dict[str, float]]:
        """
        Score each intent and return best match.
        
        Args:
            query: User query text (will be normalized)
            
        Returns:
            Tuple of (best_task, scores_dict)
            
        Scoring logic:
        - Exact regex match: +1.0 per pattern
        - Fuzzy match fallback: +0.5 * similarity (if no exact match)
        - Best task: highest score, then earliest in priority order
        """
        normalized = self._normalize(query)
        scores: Dict[str, float] = {}
        
        for task, patterns in self._intent_patterns:
            # Count exact regex matches
            exact_matches = sum(1.0 for p in patterns if re.search(p, normalized))
            
            # Fuzzy fallback for non-"qa" tasks with no exact match
            fuzzy_sim = 0.0
            if exact_matches == 0 and task != "qa":
                try:
                    # Clean patterns for fuzzy matching (remove regex special chars)
                    pattern_texts = [p.replace("\\b", "") for p in patterns]
                    fuzzy_sim = max(
                        fuzz.partial_ratio(normalized, pt) / 100.0 
                        for pt in pattern_texts
                    )
                except (ValueError, ZeroDivisionError):
                    fuzzy_sim = 0.0
            
            scores[task] = exact_matches + 0.5 * fuzzy_sim
        
        # Select best: highest score, then earliest in priority order
        best_task = max(
            scores.items(), 
            key=lambda kv: (kv[1], -self._intent_order.index(kv[0]))
        )[0]
        
        return best_task, scores
    
    def detect_special_intent(self, query: str) -> Optional[str]:
        """
        Detect special book/out-of-syllabus intents.
        
        Args:
            query: User query text (will be normalized)
            
        Returns:
            One of: "book_exercises", "book_demo", "course_extension", or None
            
        Logic:
        - book + exercice → "book_exercises"
        - out-of-syllabus + démonstration → "book_demo"
        - book OR out-of-syllabus → "course_extension"
        """
        normalized = self._normalize(query)
        
        has_book = self._regex_hit(BOOK_KW, normalized)
        has_out_of_syllabus = self._regex_hit(OUT_OF_SYLLABUS_KW, normalized)
        
        # Priority 1: Book exercises
        if has_book and re.search(r"\b(exo|exercice|exercices|exos)\b", normalized):
            return "book_exercises"
        
        # Priority 2: Out-of-syllabus proofs
        if has_out_of_syllabus and re.search(r"\b(preuve|demonstration)\b", normalized):
            return "book_demo"
        
        # Priority 3: General extension
        if has_book or has_out_of_syllabus:
            return "course_extension"
        
        return None
    
    def looks_like_math(self, query: str) -> bool:
        """
        Check if query contains math-related keywords or symbols.
        
        Args:
            query: User query text (will be normalized)
            
        Returns:
            True if math content is detected
        """
        normalized = self._normalize(query)
        return self._regex_hit(MATH_KW, normalized)
    
    def has_anaphoric_reference(self, query: str) -> bool:
        """
        Detect anaphoric references that indicate the query refers to previous context.
        
        Examples:
        - "donne moi des exo pour m'entrainer dessus" → True (dessus)
        - "explique moi ça" → True (ça)
        - "peux tu approfondir ce sujet" → True (ce sujet)
        - "qu'est-ce que la dérivée?" → False (no reference)
        
        Args:
            query: User query text (will be normalized)
            
        Returns:
            True if anaphoric reference is detected
        """
        normalized = self._normalize(query)
        
        # Anaphoric patterns (pronouns/references to previous context)
        anaphoric_patterns = (
            r"\bdessus\b",           # "dessus", "là-dessus"
            r"\bla-dessus\b",
            r"\b(ca|cela)\b",        # "ça", "cela"
            r"\bce\s+(sujet|theme|point|concept)\b",  # "ce sujet", "ce thème"
            r"\bcette\s+(notion|question|partie)\b",  # "cette notion"
            r"\bceci\b",             # "ceci"
            r"\bcette\s+(?:partie|section)\b",
            r"\bde\s+ce\s+(?:que|dont)\b",  # "de ce que", "de ce dont"
            r"\b(?:a|en)\s+ce\s+propos\b",  # "à ce propos", "en ce propos"
            r"\b(?:par|pour)\s+rapport\s+[aà]\s+(?:ca|cela)\b",  # "par rapport à ça"
            r"\bplus\s+sur\s+(?:ca|cela|ce\s+sujet)\b",  # "plus sur ça"
            r"\bapprofondir\s+(?:ca|cela|ce\s+sujet)\b",  # "approfondir ça"
            r"\b(d[' ]?autres?|autres?)\s+(?:exos?|exercices?|questions?|exemples?)\b",  # "d'autres exos"
            r"\bencore\s+(?:des?\s+)?(?:exos?|exercices?|questions?|exemples?)\b",       # "encore des exos"
            r"\b(ajoute|rajoute|propose)\s+(?:moi\s+)?(?:d[' ]?)?autres?\b",             # "rajoute moi d'autres"
            r"\bcontinue(?:\s+(?:sur|avec))?\b",                                        # "continue (sur/avec)"
            r"\bplus\s+d[' ]?(?:exos?|exercices?|détails?)\b",                          # "plus d'exos"
        )
        
        return any(re.search(pattern, normalized) for pattern in anaphoric_patterns)
