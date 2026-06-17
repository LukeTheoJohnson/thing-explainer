"""Thing Explainer: enforce the xkcd "ten hundred" word limit in code.

Public API:

    from thing_explainer import check, load_wordlist

    issues = check("The molecule moves.")   # -> [{'kind': 'FAIL', 'word': 'molecule', ...}]
    if not any(i["kind"] == "FAIL" for i in issues):
        print("clean")

The 1,000-word limit is a hard rule, not a vibe: every word must appear in the
packaged wordlist (Randall Munroe's Simple Writer list). See the project README.
"""
from __future__ import annotations

from .checker import check, load_wordlist, main, normalize

__all__ = ["check", "load_wordlist", "normalize", "main", "__version__"]

__version__ = "0.1.0"
