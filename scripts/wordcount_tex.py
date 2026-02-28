#!/usr/bin/env python3
"""
Approximate word count for paper/main.tex + paper/references.bib and update
the \\PaperWordCount macro in paper/main.tex.

This is an approximation intended for conference compliance checks.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = REPO_ROOT / "paper" / "main.tex"
BIB_PATH = REPO_ROOT / "paper" / "references.bib"


def _strip_tex(text: str) -> str:
    # Remove comments
    text = re.sub(r"(?m)^%.*$", "", text)
    # Remove LaTeX commands (keep their brace contents by stripping the command name only)
    text = re.sub(r"\\[a-zA-Z@]+\\*?(\\[[^\\]]*\\])?", " ", text)
    # Remove braces and other markup
    text = text.replace("{", " ").replace("}", " ")
    # Remove math blocks (very rough)
    text = re.sub(r"\\\((.*?)\\\)", " ", text, flags=re.DOTALL)
    text = re.sub(r"\\\[(.*?)\\\]", " ", text, flags=re.DOTALL)
    # Collapse whitespace
    text = re.sub(r"\\s+", " ", text)
    return text.strip()


def _strip_bib(text: str) -> str:
    # Keep only field values (roughly).
    text = re.sub(r"(?m)^%.*$", "", text)
    # Remove entry headers like @article{key,
    text = re.sub(r"@\\w+\\s*\\{[^,]+,", " ", text)
    # Remove field names like title =
    text = re.sub(r"(?m)^\\s*\\w+\\s*=\\s*", " ", text)
    # Remove braces/quotes/commas
    text = text.replace("{", " ").replace("}", " ").replace("\"", " ").replace(",", " ")
    text = re.sub(r"\\s+", " ", text)
    return text.strip()


def _count_words(text: str) -> int:
    words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text)
    return len(words)


def main() -> int:
    tex_text = TEX_PATH.read_text(encoding="utf-8") if TEX_PATH.exists() else ""
    bib_text = BIB_PATH.read_text(encoding="utf-8") if BIB_PATH.exists() else ""

    tex_wc = _count_words(_strip_tex(tex_text))
    bib_wc = _count_words(_strip_bib(bib_text))
    total = tex_wc + bib_wc

    updated = re.sub(
        r"\\newcommand\{\\PaperWordCount\}\{[^}]*\}",
        rf"\\newcommand{{\\PaperWordCount}}{{{total}}}",
        tex_text,
    )
    TEX_PATH.write_text(updated, encoding="utf-8")

    print(f"TeX words: {tex_wc}")
    print(f"Bib words: {bib_wc}")
    print(f"Total (approx): {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
