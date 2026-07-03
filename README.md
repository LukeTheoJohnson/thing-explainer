# thing-explainer

You don't want an answer that makes you feel small. You want the easy, true one.

This work is a small thing on your computer that reads what you write. Every word you
write has to be one of the ten hundred words that people use most. If you use a
big word, it stops and points at the word to change. It will not tell you that
you are done until every word is one of the ten hundred.

*(Every word up to here is one of the ten hundred — these first lines pass their
own check.)* It is the same game as Randall Munroe's
[*Thing Explainer*](https://en.wikipedia.org/wiki/Thing_Explainer) book, but with
a hard law so a machine can play it for real.

## Why?

I really like this ten hundred words idea. When I am trying to learn something new
myself, or tell others. There is a fine line to walk. You can say the heart of the
thing with no big hard words. On the other side, you can cut away so much it is not
quite true any more. I like to push myself to say things in an easy way, even in
fields full of deep, hard ideas. I would push other people to do the same: start
as easy as you can, and only add the hard parts when they really do help you see
the thing more clearly. When you want to say something hard, and you find an easy
way to say it: you really know the thing.

## Get it

Three ways to use it: a `thing-explainer` you run by name, a part you can pull
into your own Python, and [a way to use it in Claude Code](SKILL.md).

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

(See how `engine` is fine: it really is one of the ten hundred. The words come
from Munroe's own set, not made up.)

## Use it in your own Python

```python
from thing_explainer import check

issues = check("The molecule moves.")
fails = [i for i in issues if i["kind"] == "FAIL"]
if fails:
    print("banned:", ", ".join(i["word"] for i in fails))
```

Each word it stops on comes back with a few parts:
`{"kind", "word", "line", "col", "context"}`. `kind` is `FAIL` (a word you can
not use) or `WARN` (looks like a name). You can also give it your own set of
words to check.

The way to work goes round and round: write, check, change only the words it
points at, then go again, until it says `PASS` and gives back `0`. You are not
allowed to say you are done until it says so.

## How it keeps the law

- Every word has to be in [`wordlist.txt`](src/thing_explainer/wordlist.txt)
  (about 3,600 word forms: the main words and the same words with `-s`, `-ing`,
  `-ed`, and `-er` on the end).
- **FAIL**: a word you can not use. You have to change it.
- **WARN**: a word with a big first letter part way through a line that is not in
  the ten hundred. It is taken to be a name or a place (Jupiter, Anna) and let
  through, but still shown to you.
- It gives back `1` if some word is wrong, `0` if all is well. So you can drop it
  into a run that goes round and round, or a step that has to pass before the rest
  of your work can go on.

## A few that pass

All three pass; every word in them is one of the ten hundred, checked against
Munroe's own set.

> **A flying machine** *(this is a plane; but the word "plane" is not one of the ten hundred!)*
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

## What each part is

| Part | What it is |
|------|------------|
| `src/thing_explainer/checker.py` | The part that does the checking. Run it; go by the number it gives back. |
| `src/thing_explainer/wordlist.txt` | The words you can use. The one true set. Do not change it by hand. |
| `src/thing_explainer/words.js` | The words as they come from xkcd.com/simplewriter (where they are from). |
| `src/thing_explainer/build_wordlist.py` | Builds `wordlist.txt` from `words.js` again if the words up there change. |
| `tests/test_checker.py` | All the checks that lock in how every part of the law works. |
| `SKILL.md` | How to use it in Claude Code: the write, check, change way of working. |

```bash
pip install -e ".[dev]"
python -m pytest                 # run all the checks
```

## Big thank you

Everything good here is **[Randall Munroe](https://xkcd.com/)**'s: the man behind
[xkcd](https://xkcd.com/), who once made machines that move on their own, at NASA.

- **[*Up Goer Five*](https://xkcd.com/1133/)** (xkcd #1133, 2012): the drawing of
  the Saturn V (a very big space car), with every part named using only the ten
  hundred most used words. "The only flying space car we sent to another world"
  and all.
- **[*Thing Explainer: Complicated Stuff in Simple Words*](https://en.wikipedia.org/wiki/Thing_Explainer)**
  (Houghton Mifflin Harcourt, 2015). The book that ran with it: the human body, a
  wash machine, the table of all the bits the world is made of, all in the same
  ten hundred words.
- **[Simple Writer](https://xkcd.com/simplewriter/)**: Munroe's own little thing,
  in your computer, that points out any word not in the ten hundred. This one is
  more or less that same thing but harder: it gives a hard number back, so a run
  that writes can not say it passed when it did not.

If you like this, **buy the book**. It is beautiful, and it is the real thing.

**About the words:** [`wordlist.txt`](src/thing_explainer/wordlist.txt) is made
from [`words.js`](src/thing_explainer/words.js), the very same words that come
with xkcd's Simple Writer. That set is Munroe's work, not mine, and is here only
to make the thing run; see [LICENSE](LICENSE) for the note on where it is from.
What I wrote here is MIT; the words in the set are Munroe's to give. Please keep
this thank you in anything you build on top of it.
