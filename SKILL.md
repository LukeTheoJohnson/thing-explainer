---
name: thing-explainer
description: Explain any topic using only the "ten hundred" most common English words (xkcd Simple Writer / Randall Munroe's Thing Explainer style). Use when the user asks to explain something in simple words, "like I'm five", in plain/basic English, with no jargon, or explicitly names Thing Explainer / Up Goer Five / ten hundred words. The 1000-word limit is a HARD constraint enforced by the thing-explainer checker, not a vibe.
---

# Thing Explainer

Explain a thing using only simple, common words, the way Randall Munroe's
*Thing Explainer* book and the [Up Goer Five](https://xkcd.com/1133/) comic do.
The catch is the rule is **hard**: only words on the allowed list are permitted,
and a script checks it. You cannot talk your way past the checker.

## The one rule you cannot break

Every word must be in `wordlist.txt` (≈3,600 surface forms: the ~1000 base
words plus their plurals and -ing/-ed/-er endings). This is the official xkcd
Simple Writer list. "Thousand" itself isn't allowed, so people write "ten
hundred". That is the spirit: if a word feels fancy, it is probably banned.

Do **not** decide by feel whether your text passes. The model (you) is bad at
self-policing a closed vocabulary; you will let "system", "process", "energy"
slip through. Only the checker decides.

Install it once with `pip install thing-explainer`, which gives you the
`thing-explainer` command used below.

## Workflow: always loop through the checker

1. **Draft** the explanation in the Thing Explainer voice (see below).
2. **Check it:**
   ```bash
   thing-explainer draft.txt
   # or:  echo "your text" | thing-explainer
   ```
3. **Read the report.** Each `FAIL` line gives the banned word, its line:col,
   and context. The `FIX:` line lists every word you must replace.
4. **Rewrite only the flagged words:** swap each banned word for a small-word
   phrase ("car that flies up" not "rocket", "very small bits" not "molecules").
   Don't rewrite passing text.
5. **Repeat** until the checker prints `PASS` and exits 0. Then you are done.

Never present an explanation as finished until `thing-explainer` has returned
exit code 0 on the final text. If you claim it passed, you must have run it.

## FAIL vs WARN

- **FAIL**: a banned word. Must be replaced. Includes a banned word
  capitalized at the start of a sentence (e.g. "Molecules are small.").
- **WARN**: a capitalized word mid-sentence that isn't on the list. Treated as
  a likely name or place (Jupiter, Mars, Anna) and **allowed**. Glance at each
  warning to make sure it really is a name and not a banned word you happened to
  capitalize. Warnings do not fail the check.
- Pure numbers are ignored; `5` won't be flagged. Spelling them out ("five") is
  a style choice, not a rule.

## Writing voice

- Short sentences. Plain, friendly, a little playful.
- Describe what a thing *does* using small words instead of naming it with a big
  word. "The part that keeps the air going round" beats "the ventilation system".
- It is fine (expected, even) for explanations to get long and a bit funny.
  That trade of more words for smaller words is the whole point.
- Don't smuggle in a banned word by sticking small words around it.

## Files

| File | What it is |
|------|------------|
| `SKILL.md` | This file. |
| `thing-explainer` | The checker / enforcement command (`pip install thing-explainer`). Run it; trust its exit code. |
| `src/thing_explainer/wordlist.txt` | The allowed words. The source of truth. Do not hand-edit. |
| `src/thing_explainer/words.js` | Raw upstream list from xkcd.com/simplewriter (provenance). |
| `src/thing_explainer/build_wordlist.py` | Rebuilds `wordlist.txt` from `words.js` if upstream updates. |

## Credit

The whole idea, and the word list, are **Randall Munroe's**, from
[*Up Goer Five*](https://xkcd.com/1133/) (xkcd #1133),
the book [*Thing Explainer*](https://en.wikipedia.org/wiki/Thing_Explainer)
(2015), and his [Simple Writer](https://xkcd.com/simplewriter/) tool. This skill
just enforces his game with a hard exit code. If you like it, buy the book.
