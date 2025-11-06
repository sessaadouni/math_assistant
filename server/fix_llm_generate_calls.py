#!/usr/bin/env python3
"""
Script pour corriger tous les appels llm.generate() dans les use cases.

Change:
    self.llm.generate(prompt_template=..., variables=...)
To:
    formatted_prompt = prompt_template.format(**variables)
    self.llm.generate(prompt=formatted_prompt, temperature=0.1)
"""

import os
import re
from pathlib import Path

# Fichiers à corriger
USE_CASES_DIR = Path("src/application/use_cases")
FILES_TO_FIX = [
    "explain_theorem.py",
    "summarize_course.py",
    "exams_and_assessments.py",
    "sheets_and_exercises.py",
    "utilities.py",
    "generate_exercise.py",
]

def fix_llm_generate_call(file_path: Path):
    """Fix llm.generate() calls in a file."""
    print(f"📝 Traitement: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern: self.llm.generate(prompt_template=..., variables=...)
    # On cherche le bloc complet
    pattern = r'(\s+)(\w+_text) = self\.llm\.generate\(\s*prompt_template=(\w+),\s*variables=(\w+)\s*\)'
    
    def replacement(match):
        indent = match.group(1)
        var_name = match.group(2)
        template_var = match.group(3)
        variables_var = match.group(4)
        
        return f'''{indent}# Format prompt with variables
{indent}formatted_prompt = {template_var}.format(**{variables_var})
{indent}
{indent}# Generate text
{indent}{var_name} = self.llm.generate(
{indent}    prompt=formatted_prompt,
{indent}    temperature=0.1,
{indent})'''
    
    content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Corrigé !")
        return True
    else:
        print(f"  ⏭️  Rien à corriger")
        return False

def main():
    print("🔧 Correction des appels llm.generate() dans les use cases\n")
    
    fixed_count = 0
    for filename in FILES_TO_FIX:
        file_path = USE_CASES_DIR / filename
        if file_path.exists():
            if fix_llm_generate_call(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  Fichier non trouvé: {file_path}")
    
    print(f"\n✅ {fixed_count} fichier(s) corrigé(s)")

if __name__ == "__main__":
    main()
