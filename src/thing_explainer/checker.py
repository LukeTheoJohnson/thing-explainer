#!/usr/bin/env python3
"""Thing Explainer word checker.

Enforces the hard constraint: text may only use words from the xkcd Simple
Writer "ten hundred" list (wordlist.txt, ~3.6k surface forms incl. inflections).

This is the enforcement layer. The writing model drafts; this script decides
whether the draft passes. Do not trust prose claims that text is "simple" --
run it through here.

Usage:
    thing-explainer text.md            # check a file
    echo "some words" | thing-explainer   # check stdin
    thing-explainer --quiet text.md    # exit code only, no report

Exit codes:
    0  clean (no banned words; warnings allowed)
    1  one or more FAIL words (must be rewritten)
    2  usage / file error

Rules:
    PASS  token (lowercased, apostrophes normalized) is in the wordlist
    FAIL  token not in list -- including a banned word capitalized at the
          start of a sentence (e.g. "Molecules are small.")
    WARN  capitalized token mid-sentence that isn't in the list -- treated as a
          likely proper noun (name/place), allowed but surfaced for review
    skip  pure numbers/symbols are ignored (digit-vs-spelled is a style choice)
"""
from __future__ import annotations

import argparse
import re
import sys
from functools import lru_cache
from importlib import resources
from pathlib import Path

APOSTROPHES = "’ʼ`"

# A token is letters with optional internal apostrophes (don't, hasn't).
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’ʼ`][A-Za-z]+)*")
SENTENCE_END = re.compile(r"[.!?:;]['\"’”)]*\s*$|\n\s*$")
# Opening punctuation a sentence's first word can hide behind: quotes, brackets,
# the inverted marks used in Spanish, and an em dash. Stripped from the text
# *before* a word so a banned word at a true sentence start (He said: "Molecules
# …) is still seen as sentence-initial and FAILs instead of passing as a name.
OPENING = "\"'“‘”’([{¿¡—–-"


@lru_cache(maxsize=1)
def load_wordlist() -> frozenset[str]:
    """The allowed surface forms, read from the packaged wordlist.txt.

    Uses importlib.resources so it resolves whether the package is run from a
    source checkout or installed into site-packages. Cached: the list never
    changes within a process.
    """
    text = resources.files("thing_explainer").joinpath("wordlist.txt").read_text(
        encoding="utf-8"
    )
    return frozenset(w.strip() for w in text.splitlines() if w.strip())


def normalize(token: str) -> str:
    t = token.lower()
    for ch in APOSTROPHES:
        t = t.replace(ch, "'")
    return t


def check(text: str, words: frozenset[str] | set[str] | None = None) -> list[dict]:
    """Return a list of issues. Each: {kind, word, line, col, context}.

    `words` defaults to the packaged ten-hundred list; pass your own set to
    check against a different vocabulary.
    """
    if words is None:
        words = load_wordlist()
    issues: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in TOKEN_RE.finditer(line):
            token = m.group(0)
            norm = normalize(token)
            if norm in words:
                continue
            # Banned. Decide FAIL vs WARN.
            # Look past any opening quote/bracket the word hides behind, so a
            # banned word that truly starts a sentence can't pass as a name.
            preceding = line[: m.start()].rstrip().rstrip(OPENING).rstrip()
            sentence_initial = preceding == "" or bool(SENTENCE_END.search(preceding))
            is_cap = token[0].isupper()
            kind = "WARN" if (is_cap and not sentence_initial) else "FAIL"
            issues.append(
                {
                    "kind": kind,
                    "word": token,
                    "line": lineno,
                    "col": m.start() + 1,
                    "context": line.strip()[:80],
                }
            )
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="Check text against the ten-hundred wordlist.")
    ap.add_argument("file", nargs="?", help="file to check (default: stdin)")
    ap.add_argument("--quiet", action="store_true", help="exit code only, no report")
    args = ap.parse_args()

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"file not found: {p}", file=sys.stderr)
            return 2
        text = p.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    words = load_wordlist()
    issues = check(text, words)
    fails = [i for i in issues if i["kind"] == "FAIL"]
    warns = [i for i in issues if i["kind"] == "WARN"]

    if not args.quiet:
        if not issues:
            print("PASS: every word is in the ten hundred.")
        else:
            for i in issues:
                print(f"  {i['kind']}  L{i['line']}:C{i['col']}  {i['word']!r}  | {i['context']}")
            uniq_fail = sorted({i["word"].lower() for i in fails})
            print()
            print(f"{len(fails)} banned word(s) to fix, {len(warns)} warning(s) (likely names).")
            if uniq_fail:
                print("FIX: " + ", ".join(uniq_fail))

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
