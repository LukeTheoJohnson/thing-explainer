"""Rebuild wordlist.txt from the official xkcd words.js source.

Re-run only if words.js is updated upstream. Normalizes apostrophe variants
to a straight ASCII apostrophe, lowercases, dedupes, and sorts.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
APOSTROPHES = "’ʼ`"  # curly ', modifier letter ', grave `


def main() -> None:
    js = (HERE / "words.js").read_text(encoding="utf-8")
    m = re.search(r'"(.*)"', js, re.S)
    if not m:
        raise SystemExit("could not find quoted word string in words.js")

    norm = set()
    for raw in m.group(1).split("|"):
        w = raw.strip().lower()
        for ch in APOSTROPHES:
            w = w.replace(ch, "'")
        if w:
            norm.add(w)

    out = sorted(norm)
    (HERE / "wordlist.txt").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(out)} unique surface forms to wordlist.txt")


if __name__ == "__main__":
    main()
