# thing-explainer

You don't want a dumb explanation, just the simple version

Explain anything using only the **ten hundred** most common English words, the
way Randall Munroe's [*Thing Explainer*](https://en.wikipedia.org/wiki/Thing_Explainer)
book does. This project provides a lightweight function for the 1,000-word limit with enforcing loops. A checker reads the text and refuses to pass it until every single word is
on the allowed list.

# Why?

I've often found myself trying to capture this **ten hundred** concept when asking for explanations or learning new concepts. People refer to this idea sometimes as "Explain like I'm five" but there's a balance between getting the 80:20 rule right and explaining the core without jargon or frills, and genuinely oversimplyiifying. 

## Install

Three options for using it: a `thing-explainer` command line tool, an importable
Python library, and a [Claude Code skill](SKILL.md).

```bash
pip install thing-explainer
```

## Try it

```bash
echo "The engine converts fuel into motion." | thing-explainer
```
```
  FAIL  L1:C12  'converts'  | The engine converts fuel into motion.
  FAIL  L1:C21  'fuel'  | The engine converts fuel into motion.
  FAIL  L1:C31  'motion'  | The engine converts fuel into motion.

3 banned word(s) to fix, 0 warning(s) (likely names).
FIX: converts, fuel, motion
```

(Note that `engine` passes: it really is one of the ten hundred. The list is
Munroe's actual one, not a guess.)

## Use it as a library

```python
from thing_explainer import check

issues = check("The molecule moves.")
fails = [i for i in issues if i["kind"] == "FAIL"]
if fails:
    print("banned:", ", ".join(i["word"] for i in fails))
```

Each issue is a dict: `{"kind", "word", "line", "col", "context"}`, where
`kind` is `FAIL` (banned word) or `WARN` (likely a name). Pass your own word set
as the second argument to check against a different vocabulary.

The workflow is a loop: **draft → check → fix only the flagged words → repeat**
until the checker prints `PASS` and exits `0`. You are not allowed to call it
done until the script says so.

## How the rule is enforced

- Every word must appear in [`wordlist.txt`](src/thing_explainer/wordlist.txt) (~3,600 surface forms:
  the ~1,000 base words plus their plurals and `-ing`/`-ed`/`-er` endings).
- **FAIL**: a banned word. Must be rewritten.
- **WARN**: a capitalised word mid-sentence that isn't on the list. Treated as
  a likely name or place (Jupiter, Anna) and allowed, but surfaced for review.
- Exit code is `1` if it fails, `0` if clean. So you can drop it into a
  loop or a CI gate.

## Examples

All three pass the checker; every word is verified against Munroe's list.

> **A flying machine** *(a plane; "plane" itself is banned!)*
> A flying machine is a big metal bird that carries people through the sky. It
> has long flat arms on each side. When it runs fast along the ground, air
> rushes over those arms and pushes the whole thing up. Once it is high up, it
> keeps going fast so it does not drop. At the front, spinning parts pull it
> along. To come down, it slows and points its nose at the ground a little until
> its feet touch and roll to a stop.

> **A computer**
> A computer is a box that does what you tell it, very fast. Inside is a tiny
> part that thinks by doing lots of small bits of adding, one after another,
> faster than you could ever count. It keeps things it needs to remember in
> another part, like a wall of little boxes. When you press keys or move your
> hand, the box reads that and changes what you see on the light screen. It only
> knows two things, on and off, but by putting many of those together it can
> show words, sounds, and moving pictures.

> **Rain**
> Rain starts in the big water below. When the sun warms it, some of the water
> turns into a thing you can not see and goes up into the sky. Up high it is
> cold, so all those bits come together and turn back into tiny drops. Lots and
> lots of drops make the grey clouds you see. When the drops get too big and
> heavy to stay up, they fall back down on us as rain.

## Files

| File | What it is |
|------|------------|
| `src/thing_explainer/checker.py` | The checker. Run it; trust its exit code. |
| `src/thing_explainer/wordlist.txt` | The allowed words. Source of truth. Don't hand-edit. |
| `src/thing_explainer/words.js` | Raw upstream list from xkcd.com/simplewriter (provenance). |
| `src/thing_explainer/build_wordlist.py` | Rebuilds `wordlist.txt` from `words.js` if upstream changes. |
| `tests/test_checker.py` | The test suite locking in every enforcement behaviour. |
| `SKILL.md` | Claude Code skill: the draft → check → fix loop. |

```bash
pip install -e ".[dev]"
python -m pytest                 # the full suite
```

## Credit & thanks

Everything good about this idea belongs to **[Randall Munroe](https://xkcd.com/)**:
cartoonist behind [xkcd](https://xkcd.com/), former NASA roboticist.

- **[*Up Goer Five*](https://xkcd.com/1133/)** (xkcd #1133, 2012): the blueprint
  of the Saturn V rocket, labelled using only the ten hundred most used words.
  "The only flying space car we sent to another world" and all.
- **[*Thing Explainer: Complicated Stuff in Simple Words*](https://en.wikipedia.org/wiki/Thing_Explainer)**
  (Houghton Mifflin Harcourt, 2015). The book that ran with it: the human body,
  a washing machine, the periodic table (the "pieces everything is made of"),
  all in the same thousand words.
- **[Simple Writer](https://xkcd.com/simplewriter/)**: Munroe's own in-browser
  tool that flags any word outside the list. This project is, more or less, that
  tool grown a spine: a hard exit code so an automated writing loop can't fib
  about whether it passed.

If you enjoy this, **buy the book**. It's beautiful, and it's the real thing.

**On the word list:** [`wordlist.txt`](src/thing_explainer/wordlist.txt) is built
from [`words.js`](src/thing_explainer/words.js), the exact vocabulary shipped with
xkcd's Simple Writer. That list is Munroe's work, not mine, and is included here
only to make the checker runnable; see [LICENSE](LICENSE) for the provenance
note. The code in this repo is MIT; the word list's terms are Munroe's. Please
keep this credit intact in anything you build on top of it.
