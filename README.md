# Galaxy on AnVIL — ACC2026 Poster

Conference poster for the **AnVIL Community Conference 2026** (August 31 –
September 1 2026, Broad Institute, Cambridge MA).

*A self-provisioning deployment, elastic compute on Google Cloud Batch, and the
road to AI co-scientists* — Enis Afgan, Keith Suderman, Michael Schatz, Johns
Hopkins University.

The poster is one self-contained HTML file, 34in × 44in portrait, printed to
PDF through headless Chrome.

## Looking at it

The current poster is published from `main` to GitHub Pages — a scaling viewer
that fits the poster to your browser window, no download needed. Every pull
request also attaches a PDF and a PNG preview as build artifacts, under the
run's **Summary → Artifacts**.

## Working on it locally

Requires Python 3 and Google Chrome. Nothing to install.

```bash
python3 scripts/poster.py check     # does it still fit the page?  (~3s)
python3 scripts/poster.py all       # flex viewer + PDF + PNG preview
python3 scripts/poster.py --help    # individual targets
```

`poster/poster.html` is the only file you edit by hand. Open it directly in a
browser to work on it, or run `poster.py flex` and open
`poster/poster-flex.html` to see the whole thing scaled to your window.

Set `CHROME=/path/to/chrome` if Chrome is somewhere unusual.

### The page height is a hard limit

The poster is a fixed 34in × 44in page. Content that no longer fits does not
wrap or warn — **it is silently clipped off the bottom of the printed PDF**,
while the HTML still looks fine in a browser. There is roughly 0.4in of slack
at the moment.

So run `python3 scripts/poster.py check` after any content change. CI runs it
on every pull request and fails the build on overflow.

`docs/POSTER_NOTES.md` lists the ways to reclaim space, least damaging first.

One caveat: the poster asks for Helvetica Neue, which the Linux CI runner does
not have, so CI falls through to Liberation Sans and measures about **0.2in
shorter** than macOS does (43.41in vs 43.62in on the same commit). CI is the
optimistic side, so a green build is not by itself proof the poster fits when
rendered on a Mac. Keep a little slack, and trust your local number.

## Contributing

1. Read `docs/POSTER_NOTES.md`. It records every design decision, where each
   fact on the poster came from, and what has been deliberately left off —
   including several sections the authors removed on purpose.
2. Branch, edit `poster/poster.html`, run the check, open a pull request.
3. CI checks the fit, builds a preview, and reviews the change against the
   documented content rules.

Do not commit generated files — `build/` and `poster/poster-flex.html` are
rebuilt by CI and are gitignored.

### Working with Claude

The repository is set up for [Claude Code GitHub
Actions](https://code.claude.com/docs/en/github-actions). Mention `@claude` in
an issue or pull request comment to have it make a change, for example:

```
@claude the cost card is running long — tighten it and keep the poster under 44in
@claude add a sentence about spot instances to "Where This Is Going"
```

Claude reads `CLAUDE.md` and `docs/POSTER_NOTES.md` first, and can run the fit
check itself before pushing. It only responds to users with **write access** to
this repository.

`.claude/skills/poster/` holds the poster design system — palettes, type scale,
component styles, and the logo library — as a skill available both to `@claude`
and to Claude Code running locally.

## Layout

```
poster/poster.html      the poster — the only hand-edited file
poster/images/          images it references
docs/POSTER_NOTES.md    design decisions, sourced facts, what's omitted
docs/plan.md            the original brief
docs/abstract.txt       the submitted abstract
scripts/poster.py       check and build tooling
.claude/skills/poster/  the poster design system, as a skill
CLAUDE.md               instructions for Claude Code
```
