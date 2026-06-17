"""Test suite for the Thing Explainer checker.

Goal: lock down every behavior that the enforcement guarantee depends on, so a
future wordlist refresh or checker edit can't silently weaken the rule. Grouped
by concern: classification (FAIL/WARN/skip), tokenizing, the public API, the
packaged wordlist itself, and the CLI end to end.

Run: python -m pytest
"""
from __future__ import annotations

import subprocess
import sys

import pytest

from thing_explainer import check, load_wordlist, normalize
from thing_explainer.checker import TOKEN_RE

WORDS = load_wordlist()


def kinds(text: str) -> list[tuple[str, str]]:
    """(kind, word) pairs, the part of each issue we assert on most."""
    return [(i["kind"], i["word"]) for i in check(text, WORDS)]


# ── classification: the four core behaviors (the original regression set) ─────
def test_clean_text_passes():
    assert check("The big sky car goes up so we can look at the world.", WORDS) == []


def test_banned_common_words_fail():
    issues = kinds("The molecule moves to process the data.")
    assert ("FAIL", "molecule") in issues
    assert ("FAIL", "process") in issues
    assert ("FAIL", "data") in issues


def test_real_list_word_passes():
    # "system" is genuinely in Munroe's list; must not be flagged.
    assert kinds("The system works.") == []


def test_proper_noun_midsentence_warns_not_fails():
    assert kinds("We can see Jupiter in the sky at night.") == [("WARN", "Jupiter")]


def test_banned_word_capitalized_at_sentence_start_fails():
    # Must not escape enforcement via the proper-noun rule.
    assert kinds("Molecules are very small.") == [("FAIL", "Molecules")]


def test_contraction_with_curly_apostrophe_passes():
    # don't / don’t both normalize into the list.
    assert check("We don't fall and we don’t stop.", WORDS) == []


def test_pure_numbers_ignored():
    assert check("We have 5 of them.", WORDS) == []


# ── FAIL vs WARN boundary: the proper-noun escape hatch must stay narrow ──────
def test_banned_word_after_period_is_fail_not_warn():
    # New sentence => sentence-initial => a banned cap word is a FAIL.
    assert kinds("We go home. Molecules are small.") == [("FAIL", "Molecules")]


def test_banned_word_after_question_mark_is_fail():
    assert kinds("Are you ok? Energy is high.") == [("FAIL", "Energy")]


def test_banned_word_after_colon_is_fail():
    assert kinds("Here it is: Energy is high.") == [("FAIL", "Energy")]


def test_proper_noun_after_comma_warns():
    # Comma does not start a new sentence, so a cap non-list word is a name.
    assert kinds("We saw the sky, Anna, and the sea.") == [("WARN", "Anna")]


def test_lowercase_banned_word_is_always_fail():
    # No capital => cannot be a proper noun => FAIL wherever it sits.
    assert kinds("we like jupiter at night") == [("FAIL", "jupiter")]


@pytest.mark.parametrize("opener", ["(", '"', "“", "'", "‘", "["])
def test_sentence_initial_through_opening_punctuation(opener):
    # A banned cap word at the true start of a sentence, behind a quote/bracket,
    # must FAIL; it can't slip through as a likely name just because a quote
    # sits in front of it.
    assert kinds(f"He said: {opener}Molecules are small.") == [("FAIL", "Molecules")]


def test_banned_word_behind_opening_quote_at_line_start_fails():
    # A line that opens with a quote then a banned cap word is sentence-initial.
    assert kinds('"Molecules are small," he said.') == [("FAIL", "Molecules")]


def test_midsentence_name_behind_quote_still_warns():
    # The fix must not over-correct: a name in quotes mid-sentence (not at a
    # sentence start) is still a likely name, so it stays a WARN.
    assert kinds('We flew to "Jupiter" last year.') == [("WARN", "Jupiter")]


def test_name_opening_a_quoted_sentence_fails_like_any_sentence_start():
    # Consistent with "Molecules are small.": at a true sentence start the
    # checker can't tell a name from a banned word, so it errs toward FAIL.
    # (Lowercase or rephrase to silence; this is intended strictness.)
    assert kinds('She said: "Jupiter is far away."') == [("FAIL", "Jupiter")]


# ── tokenizing ────────────────────────────────────────────────────────────────
def test_hyphenated_words_split_into_separate_tokens():
    # "ten-hundred" tokenizes as two words; both are on the list.
    assert check("ten-hundred", WORDS) == []


def test_internal_apostrophe_kept_as_one_token():
    assert [m.group(0) for m in TOKEN_RE.finditer("don't")] == ["don't"]


def test_line_and_column_are_one_based_and_accurate():
    issues = check("ok ok\nthe molecule", WORDS)
    assert len(issues) == 1
    assert issues[0]["line"] == 2
    assert issues[0]["col"] == 5  # 1-based index of 'molecule' on line 2


def test_context_is_the_trimmed_line():
    issues = check("   the molecule moves   ", WORDS)
    assert issues[0]["context"] == "the molecule moves"


def test_empty_text_has_no_issues():
    assert check("", WORDS) == []
    assert check("\n\n   \n", WORDS) == []


# ── normalize() ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Don't", "don't"),
        ("don’t", "don't"),  # curly apostrophe
        ("donʼt", "don't"),  # modifier-letter apostrophe
        ("don`t", "don't"),  # grave
        ("HELLO", "hello"),
    ],
)
def test_normalize_lowercases_and_unifies_apostrophes(raw, expected):
    assert normalize(raw) == expected


# ── public API surface ────────────────────────────────────────────────────────
def test_check_defaults_to_packaged_wordlist():
    # Calling check() with no word set must use the bundled list, not error.
    assert check("The molecule moves.")  # non-empty -> something was flagged
    assert check("we go up") == []


def test_check_accepts_a_custom_vocabulary():
    issues = check("cat dog", words=frozenset({"cat"}))
    assert [(i["kind"], i["word"]) for i in issues] == [("FAIL", "dog")]


def test_load_wordlist_is_cached_same_object():
    # lru_cache means repeated loads return the identical frozenset.
    assert load_wordlist() is load_wordlist()


def test_issue_dict_has_the_documented_shape():
    issue = check("The molecule moves.")[0]
    assert set(issue) == {"kind", "word", "line", "col", "context"}


# ── the packaged wordlist itself (catches a broken build / refresh) ───────────
def test_wordlist_is_substantial():
    # ~3,600 surface forms. If a build ships an empty/half list, fail loudly.
    assert len(WORDS) > 3000


def test_wordlist_entries_are_normalized():
    # Every entry should already be lowercase with straight apostrophes,
    # otherwise normalize() at check time can never match them.
    bad = [w for w in WORDS if w != normalize(w)]
    assert bad == []


def test_known_anchor_words_present_and_absent():
    # A few load-bearing assertions about the actual list content.
    for w in ("the", "water", "system", "sky", "car"):
        assert w in WORDS, f"expected {w!r} in the ten hundred"
    for w in ("molecule", "energy", "data", "process", "thousand"):
        assert w not in WORDS, f"did not expect {w!r} in the ten hundred"


# ── CLI: exit codes and report, the contract scripts/CI depend on ─────────────
def run_cli(args, stdin=""):
    return subprocess.run(
        [sys.executable, "-m", "thing_explainer.checker", *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_cli_clean_text_exits_zero(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text("we go up to the sky", encoding="utf-8")
    r = run_cli([str(f)])
    assert r.returncode == 0
    assert "PASS" in r.stdout


def test_cli_banned_text_exits_one(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("the molecule moves", encoding="utf-8")
    r = run_cli([str(f)])
    assert r.returncode == 1
    assert "molecule" in r.stdout
    assert "FIX:" in r.stdout


def test_cli_warnings_only_still_exit_zero(tmp_path):
    # A lone proper noun is a WARN, not a FAIL -> clean exit.
    f = tmp_path / "warn.txt"
    f.write_text("we can see Jupiter at night", encoding="utf-8")
    r = run_cli([str(f)])
    assert r.returncode == 0


def test_cli_reads_stdin():
    r = run_cli([], stdin="the molecule moves")
    assert r.returncode == 1
    assert "molecule" in r.stdout


def test_cli_quiet_suppresses_report_but_keeps_exit_code():
    r = run_cli(["--quiet"], stdin="the molecule moves")
    assert r.returncode == 1
    assert r.stdout.strip() == ""


def test_cli_missing_file_exits_two():
    r = run_cli(["does_not_exist_12345.txt"])
    assert r.returncode == 2
