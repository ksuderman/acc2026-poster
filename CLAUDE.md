# CLAUDE.md

Instructions for Claude Code working in this repository, whether run locally or
from GitHub Actions.

## What this repository is

The conference poster for **ACC2026** (AnVIL Community Conference, August 31 –
September 1 2026, Broad Institute, Cambridge MA), titled *Galaxy on AnVIL*.
Authors: Enis Afgan, Keith Suderman, Michael Schatz — all Johns Hopkins
University.

**Read `docs/POSTER_NOTES.md` before making any change.** It records every
design decision, where each fact on the poster came from, and — importantly —
what has been deliberately left off. It is the single most useful file here.

## The one rule that matters

`poster/poster.html` is a **fixed 34in × 44in page**. Content that no longer
fits does not wrap, scroll, or warn — it is silently clipped off the bottom
when the PDF is printed, and the HTML still looks fine in a browser. There is
currently about **0.4in of slack**.

So, after any change to poster content or styling:

```bash
python3 scripts/poster.py check
```

This is not optional and it is not slow (about 3 seconds). Never report a
content change as complete without running it.

The check needs headless Chrome. It is available in GitHub Actions, and the
workflow allowlists this exact command — if it appears blocked, say so rather
than pushing an unverified layout.

If it fails, `docs/POSTER_NOTES.md` lists the levers for reclaiming space in
order of least damage. Prefer those in order; shrinking the type is a last
resort, since it has already been reduced ~10% from the design-system defaults.

## Files

| Path | Role |
|---|---|
| `poster/poster.html` | **The poster. The only file to edit by hand.** |
| `poster/images/` | Images the poster references |
| `docs/POSTER_NOTES.md` | Design decisions, sourced facts, what's deliberately omitted |
| `docs/plan.md` | The original brief |
| `docs/abstract.txt` | The submitted abstract |
| `scripts/poster.py` | Check and build tooling |
| `.claude/skills/poster/` | The poster design system, as a skill |
| `build/`, `poster/poster-flex.html` | Generated — never edit, never commit |

`poster-flex.html`, `poster.pdf` and `poster-preview.png` are **derived**.
Regenerate them with `python3 scripts/poster.py all`; do not hand-edit them and
do not commit them. CI rebuilds them on every push and publishes the flex
viewer to GitHub Pages.

## Content rules

These come from explicit decisions by the authors. Do not undo them without
being asked:

- **No email addresses anywhere on the poster** — removed from both the header
  and the footer on request.
- **No discussion of problems that had to be resolved.** Several sections about
  bugs, failures and fixes were deliberately cut. `docs/POSTER_NOTES.md` lists
  them under "Deliberately off the poster" — that section is a record of what
  *not* to reintroduce, not a to-do list.
- **Grant numbers are exact** as supplied: NHGRI U24HG010262, U24HG010263,
  U24HG006620.
- **AnVIL palette**, not the Galaxy palette — the subject is Galaxy *on* AnVIL.
  Primary `#0C5294`, accent `#4da6e8`, page background `#edf1f5`.
- Facts on the poster are sourced from real code and session notes, catalogued
  in `docs/POSTER_NOTES.md`. If you change a number, say where the new one came
  from. Note in particular that the "~6 min" launch time supersedes the stale
  15–20 min figure in the older GCC2026 poster.

## Working style here

- Keep the poster a single self-contained HTML file with inline `<style>`. No
  external stylesheets, no CDN links, no build step beyond `scripts/poster.py`.
- Reference images with relative `images/...` paths.
- Update `docs/POSTER_NOTES.md` when you make a design decision worth
  remembering. It is what lets the next session resume without re-deriving
  everything.
- Font rendering differs between macOS and the Linux CI runner: the poster asks
  for Helvetica Neue, which Linux lacks, so CI measures ~0.2in shorter (43.41in
  vs 43.62in on the same commit). CI is the optimistic side, so a passing CI run
  does not prove the poster fits on a Mac. When running in Actions, treat
  anything under ~0.25in of reported slack as too tight.
