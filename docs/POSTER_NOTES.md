# ACC2026 Poster — Working Notes

**`posters/acc2026` is the poster being presented, and the only one generated.**
It is *From Batch to Bots*, retitled on 2026-08-19 — see
[its section below](#poster-acc2026--from-batch-to-bots).

An earlier poster is kept for reference at **`archive/acc2026-old/`**. It sits
outside `posters/`, so `poster.py` does not discover it: it is never checked,
built, or published. Its notes are retained below because the sourced facts and
the "deliberately off the poster" rules still apply.

The conference details, palette and content rules apply to both.

---

# Archived: `archive/acc2026-old/`

**Not generated.** Superseded by `posters/acc2026`; kept for its fact trail.

## Conference / authors

- **Conference:** ACC2026 — AnVIL Community Conference
- **Dates:** August 31 – September 1, 2026
- **Location:** Broad Institute, Cambridge, MA
- **Authors:** Enis Afgan · Keith Suderman · Michael Schatz (all Johns Hopkins University)
- **Contact shown:** none. **No email addresses anywhere** on the poster — removed from both header and footer at the user's request. The footer carries the repository URL and the funding acknowledgement.
- **Funding acknowledgement** (footer, right, 18pt): "Supported by the AnVIL Project (NHGRI Grant Nos. U24HG010262 and U24HG010263) and the Galaxy Project (NHGRI Grant No. U24HG006620)". Grant numbers are exactly as the user supplied them; NHGRI was added in front of each on request. The line break between the two projects is a hard `<br>` so the grant groups never split awkwardly across lines.

## Files

| File | Purpose |
|---|---|
| `archive/acc2026-old/poster.html` | The poster. Fixed 34in × 44in portrait, print-ready. Source of truth — edit this one. |
| `archive/acc2026-old/images/` | `anvil_logo.png`, `galaxy_logo.png`, `galaxy_logo_white.png`, `jhu_logo_trimmed.png`, `cost-time.png`, `ai-architecture.png` |
| `archive/acc2026-old/poster-flex.html` | **Generated.** Scales the whole poster to fit the browser window. |
| *(not built)* | **Generated.** Print-ready PDF, one page, MediaBox exactly 2448 × 3168 pt (34 × 44 in). |
| *(not built)* | **Generated.** Downscaled raster, for pull request review. |

Generated files are gitignored and rebuilt by `scripts/poster.py`; CI rebuilds
them on every push. Never edit or commit them.

`galaxy_logo_white.png` is no longer referenced (the Galaxy logo was removed from the header) but is kept in case the header changes back.

## Design

- **Size:** 34in × 44in **portrait** (as specified in `plan.md`), not the skill's default 48×36 landscape.
- **Palette:** AnVIL blue — primary `#0C5294`, accent `#4da6e8`, page background `#edf1f5`, card background white, tag background `#e0ecf7`, diagram background `#f0f4f8`.
- **Main logo:** AnVIL (subject is Galaxy *on AnVIL*). The AnVIL logo is dark blue on transparent, so in the header it sits on a **white pill**, at 1.9in and alone — the Galaxy logo was removed from the header.
- **Footer:** JHU left, Galaxy Project **centered**, text right. The footer is a `1fr auto 1fr` grid precisely so the Galaxy logo centres on the poster rather than on the remaining space. No AnVIL logo in the footer (it already leads the header).
- **Type:** Title 58pt · subtitle 27pt · authors 25pt · card h2 31pt · h3 23pt · body 21pt · tags/captions 17pt. These are ~10% smaller than the skill's defaults because the poster is 34in wide rather than 48in, and the content is dense.
- **Layout:** header / 3-column content / full-width AI band / footer.

## Content structure

| Column | Cards |
|---|---|
| 1 | Galaxy on AnVIL (intro) · Architecture (diagram) · Deployment: Then & Now |
| 2 | Maintenance, Simplified · Elastic Compute with Google Cloud Batch |
| 3 | Cost: Paying for Work, Not Uptime (chart) · Try It · Where This Is Going |
| full-width band | AI Co-Scientists: GalaxyAI, Orbit, and Where the Model Runs |

This maps to the three areas the plan asked for: (1) deployment + maintenance, (2) Batch cost/elasticity, (3) GalaxyAI and Orbit/Loom.

### Why the AI section is a full-width band

`images/ai-architecture.png` is 2210 × 858 px — a **2.58:1** aspect ratio. In a single 10.4in column its body labels render at about **9pt**, which is unreadable on a poster. The band gives the figure ~19.7in of width, putting the smallest labels near **18pt**.

The rule for resizing it: displayed label size ≈ `28px × (W_inches × 96 / 2210)`. Keep `W` at 15in or more, or the diagram stops being legible. The band grid is `1.55fr 1fr` (figure / text) — widening the text column shrinks the figure, so adjust both together.

The AI text and the "open question" paths were merged into this one band because the diagram already shows both destinations (in-cluster GPU with `no egress` vs. Gemini for Government behind `egress`), so the card and the figure were saying the same thing twice.

## Facts on the poster and where they came from

Sourced from session notes and code in `galaxy-k8s-boot`, `galaxy-k8s-boot-interactive-tools`, `galaxy-helm`, and `galaxy-dev`.

- **~6 min** launch-to-responding-Galaxy — `galaxy-k8s-boot/README.md`. ⚠️ The older GCC2026 poster in `galaxy-k8s-boot/gcc2026/` claims 15–20 min; that number is stale. Use ~6 min.
- **Versions:** RKE2 v1.36.2, Helm v4.2.2, Galaxy Helm chart 6.8.2, CloudNativePG, cert-manager, NGINX ingress, Debian 12 — `roles/galaxy_k8s_deployment/defaults/main.yml`.
- **e2-standard-4**, pre-built image with 15 pre-pulled container images and a configured CVMFS client — `roles/image_preparation/`.
- **Boot chain:** `launch_vm.sh` → cloud-init → `ansible-pull` → `playbook.yml` → role. No SSH.
- **Then/Now:** `.ignored/ARCHITECTURE_COMPARISON.md` (≈10 chained playbooks → 2 roles) and `.ignored/GCP_BATCH_NFS_FIX.md` (fragile ConfigMap patching replaced by a second `helm upgrade`).
- **Release automation:** galaxy-helm release → repository dispatch → auto-PR bumping the chart version — `PROJECT_STATUS_2026-05-12.md`.
- **Golden Batch VM image** published in `anvil-and-terra-development`, shared with `allAuthenticatedUsers`, image project decoupled from job project.
- **TPV routing**, local cap **1 core / 4 GB**; per-tool sizing MetaPhlAn 16/96, FastQC 16/64, fastp 8/32; `max_accepted_*` (reject) rather than `max_*` (clamp).
- **Machine-type selection** by memory-per-core ratio across n2 highcpu/standard/highmem, 2–128 vCPUs — `galaxy-dev/lib/galaxy/jobs/runners/util/gcp_batch/helpers.py`.
- **Per-job ceiling: 128 vCPUs / 512 GB.** Raised from "60 vCPUs and 240GB" on
  2026-08-20 at the authors' request. Consistent with the 2–128 vCPU range in
  the machine-selection code cited immediately above.
- **Cost numbers** read off `images/cost-time.png`: managed cluster ≈ $263/week; VM+Batch ≈ $107 typical (≈60% saving); low preset (3 runs) ≈ $57; high preset (25 runs) ≈ $211.
- **MCP: 44 tools** (`grep -c "@mcp.tool()" galaxy-dev/lib/galaxy/webapps/galaxy/api/mcp.py`), `enable_mcp_server` default false.
- **GalaxyAI** multi-agent system on pydantic-ai, 8 agent types — `galaxy-dev/doc/source/admin/ai_agents.md`.
- **Orbit/Loom** as interactive tool `interactive_tool_orbit`, Loom in `LOOM_MODE=remote`, via `galaxy-mcp` + in-cluster LiteLLM → Vertex Gemini. "list my histories" validated end to end — `galaxy-k8s-boot` `SESSION_NOTES.md` and `docs/orbit-interactive-tool-design.md`. Note: Orbit/Loom appear **only** in galaxy-k8s-boot, not in galaxy-helm or galaxy-dev.
- **Benchmarks** behind the "answer competitively" / "seven times faster" claims: `git show d3d57afb6f` in galaxy-dev (routing + error_analysis across gpt-oss-120b, Llama-4-Maverick, Llama-3.3-70B). Model names were deliberately left off the poster; add them if asked.

## Ad-like redesign (2026-08-16)

At the authors' request, the poster was rewritten to read more like an Apple
product-launch ad than a paper abstract: lead with the impact number, cut the
explanation. The expectation is that the authors talk through the "why" while
standing next to the poster, not that the poster explains itself unattended.

- Every card that had a paragraph-plus-bullet-list explanation was cut down to
  a big stat (`.metric`) or a couple of tags. Full sentences were removed
  wherever a number or a 2-3 word phrase said the same thing.
- Added `.metric.solo` (in the `.metrics` grid CSS): a full-width variant of
  the existing metric tile at a much bigger font (58pt vs. 36pt), for a single
  standout number rather than a paired row. Used for "No SSH", "2–128 vCPUs",
  "1 command", "44 tools", and (stacked, one per row) the two Maintenance
  stats.
- "Maintenance, Simplified" and "Elastic Compute" (column 2) lost their
  two `<h3>`-headed bullet lists (Terra team / Galaxy team, TPV routing
  steps) entirely — those were the most prose-heavy blocks on the poster.
  Elastic Compute's routing logic (≤1 core/4GB local vs. everything else to
  Batch) is now a two-box `.paths` diagram instead of a sentence, reusing the
  component already built for the AI band's self-hosted/hosted comparison.
- "Where This Is Going" (six bulleted, described roadmap items) became a bare
  tag row — the items are still all there, just as 2-4 word labels.
- Column heights were rebalanced and verified by rendering, not estimated.
- Numbers themselves are unchanged from the prior version; only their
  presentation changed. No new facts were introduced.

### Content restored to fill the page (same day)

The first pass of the redesign cut too much: it measured **33.26in of 44in**,
leaving nearly **11in of blank paper** — about a quarter of the board — and the
three columns ended at very different heights. It read as unfinished rather than
deliberately spare.

Content was restored until the page was full again, keeping the ad-like idiom
(big number first, short supporting line) rather than reverting to paragraphs:

| Card | Restored |
|---|---|
| Galaxy on AnVIL | Two intro sentences — what Galaxy is, and the VM/Batch split |
| Architecture | Session-critical work stays local; data disks survive redeploy |
| Deployment | The four-step "The VM provisions itself" boot chain; component versions on the tags |
| Maintenance | Both `<h3>` team lists (3 items each, trimmed); the pre-built image caption; the golden Batch image callout |
| Elastic Compute | TPV lead-in; the literal right-sizing explanation; the reference-data + job-ID callout |
| Cost | The chart's premise (managed cluster bills continuously); idle/headroom/scale consequences |
| Try It | One-line intro; repository names with what each one is |
| Where This Is Going | Six roadmap items back to described bullets from bare tags |
| AI band | The GalaxyAI router and MCP paragraphs; two bullets per model path; the full NIH policy sentence |

**Result: 42.66in of 44in — 1.34in of slack**, columns within ~0.5in of each
other. Nothing from "Deliberately off the poster" was reintroduced.

## Deliberately off the poster

The user asked to **remove all discussion of problems we had to resolve**, so the following are researched and available but intentionally not shown. Do not reintroduce them without asking:

- The "Engineering the long tail" section: the cross-project network fix (commit `e71a26bdb1`, qualifying network/subnet so Terra pet projects resolve) and the polling fix (~3,600 API calls/hr/job → ~30× reduction, `galaxy-dev/polling_interval.md`).
- The paragraph on interactive-tool infrastructure work: wildcard DNS zones, per-instance TLS, certificate persistence against Let's Encrypt rate limits, and keeping interactive sessions off Batch.
- The GalaxyAI model-portability bug (Gemini returning `tool_id` without `name`).
- The "removed an entire class of cross-project failures" phrasing in the Maintenance callout, and "could fail silently" in the Then box — both softened to describe the old design rather than its failures.

The **Then & Now** comparison was kept: it is the before/after improvement story `plan.md` explicitly asked for, and it now describes the old *design* rather than incidents.

---

# Shared tooling

## Regenerating derived files

```bash
python3 scripts/poster.py all                       # every poster
python3 scripts/poster.py all acc2026-architecture  # just one
python3 scripts/poster.py site                      # assemble site/ for Pages
python3 scripts/poster.py flex     # or individually
python3 scripts/poster.py pdf
python3 scripts/poster.py preview
```

`poster.py` reads the page size from the `@page` rule, so changing the poster's
dimensions there is enough — no size is hard-coded in the tooling. The `pdf`
target also fails if the output comes out as more than one page.

## Checking the layout after edits

The poster has a **fixed** 44in height, so added content silently overflows off
the bottom of the printed page while the HTML still looks fine in a browser.
After any content edit:

```bash
python3 scripts/poster.py check
```

It relaxes the body height to `auto`, lays the poster out in headless Chrome,
reads back `document.body.scrollHeight`, and exits non-zero above 44in. Takes
about 3 seconds. CI runs it on every pull request.

Current state: **43.62in of 44in**, so roughly **0.38in of slack**. (This
supersedes the older hand-measured "43.3in": the script counts the body's 0.35in
bottom padding, which the pixel-scanning method did not.)

⚠️ The measuring copy is written next to `poster.html` precisely so its relative
`images/` paths still resolve. A broken image collapses to a zero-height box and
the poster measures ~1in short — which is how the earlier manual method could
report a comfortable fit for a poster that overflowed.

⚠️ **CI measures about 0.2in shorter than macOS.** The poster asks for Helvetica
Neue, which Linux lacks, so CI falls through to Liberation Sans. Measured on the
same commit: **43.62in on macOS, 43.41in on the runner.** CI is the *optimistic*
side, so it can pass a poster that overflows when rendered on a Mac — treat the
local number as the real one and keep at least ~0.25in of slack in CI. Embedding
a self-hosted webfont would make the two agree exactly, at the cost of changing
the poster's typography.

Levers to fit, in order of least damage:
1. `.figure img { width: … }` on the cost chart (a full-width chart costs ~0.6in vs. 91%).
2. Rebalancing cards between columns — the AI band is fixed-height, so the three columns above it are what flexes.
3. Tightening prose.
4. Type sizes (already reduced ~10% from the skill defaults — reduce further only as a last resort).
5. The band's `1.55fr 1fr` split — see the legibility floor above before shrinking the figure.

---

# Poster: `acc2026` — *From Batch to Bots*

Created 2026-08-18 from `docs/abstract.txt` and `docs/presentation.pdf` (the
24-slide talk, August 2026). Renamed from `acc2026-architecture` to `acc2026` on
2026-08-19, when it became the only poster being presented.

## What it argues

The talk's spine, kept: the goal is to make the service **more usable and
therefore more used**, via three levers — quicker startup, lower cost, easier
updates. The poster reports measurements against each and is candid that
**startup has not improved yet**.

## The startup number

The archived poster claims **~6 min** launch-to-responding-Galaxy, sourced from
`galaxy-k8s-boot/README.md`. The August 2026 deck contradicts it:

- Slide 5: "Startup time — Before: ~15 min. Now: about the same 😔"
- Slide 6: measured deployment **16m 43s** (1003.09s across 20 Ansible tasks)
- Slide 7: **5–6 min is a target**, contingent on Galaxy 26.2's lazy toolbox loading

The authors chose the deck's figures. Since the archived poster is no longer
presented or generated, its stale ~6 min claim no longer needs correcting.

## Facts and where they came from

All from `docs/presentation.pdf` unless noted:

- **16m 43s / 1003.09s / 20 tasks**, `helm install galaxy` **674.09s = 67.2%**,
  job handler rollout **101.97s = 10.2%**, RKE2 startup **67.68s = 6.7%**,
  `galaxy-deps` **47.43s = 4.7%**, remaining 16 tasks **111.9s = 11.2%** — slide 6
- **Tool XML parsing 355s cold / 343s restart / 227s on t2d Tau AMD** — slide 7
- **Baseline compute cost $0.17/hr now vs $0.52+/hr before, ~65% lower** — slide 5
- **A month-plus upgrade involving three groups → mostly independent** — slide 9
- **Core tested features check out; next Terra Dev then Prod; target release
  announcement by ACC** — slide 10
- **GalaxyAI vs Orbit/Loom comparison table** — slide 20, reproduced verbatim
- **Loom brain → `galaxy-mcp` → Galaxy REST API, acting as the user** — slide 19
- **LiteLLM in-cluster, no API key for Vertex (ADC via the metadata server),
  deployed as config through `galaxy-k8s-boot`** — slide 17
- Researcher-facing benefits (tools, workflows, histories, provenance,
  reproducibility, collaboration) — `docs/abstract.txt`
- **Up to 60 vCPUs and 240GB memory per job** — per the authors, from GCP's
  own documentation on Batch job resource limits (not from the `galaxy-dev`
  machine-selection code cited above, which is where the earlier "2–128
  vCPUs" figure came from — that code path picks a machine type by
  memory-per-core ratio, but the 60 vCPU / 240GB ceiling is a GCP platform
  limit, a different fact).

## Figures

| Image | Source |
|---|---|
| `batch-service.png` | Cropped from slide 5 at 300 dpi |
| `phase-duration.png` | Cropped from slide 7 at 300 dpi, shown at 84% column width |
| `cost-time.png` | Reused from `acc2026` |
| `ai-architecture.png` | Reused from `acc2026` |

The slide 6 deployment-timing chart was **not** used as an image. At column
width its labels render around 8pt — below the 18pt floor this project set for
the AI diagram — and it is a dark dashboard on a light poster. It is redrawn as
native HTML bars (`.taskbars` / `.tb` in the poster's `<style>`), which are
legible at poster type sizes and on-brand. The numbers are identical.

## Deliberately off this poster

Consistent with the rule for `acc2026`: slide 10's "Data import & export to
Terra still has some issues" is a live problem and is **not** on the poster.
Slide 12's "is it allowed and/or feasible" framing is also omitted; the policy
question appears only as the NIH-guidance callout in the AI band.

## Current state

**42.88in of 44in — 1.12in of slack** measured on macOS. Columns balanced within
about half an inch. Levers used to fit it, in order: figure widths first
(`phase-duration.png` at 84%, `cost-time.png` at 90%), then prose tightening.

## Rewrite: *From Batch to Bots* (2026-08-19)

Retitled and rewritten at the authors' request. The brief: bigger type, far
fewer words, and a focus on **what changes for the user** rather than on
engineering detail.

**Title / subtitle.** "From Batch to Bots" over "Galaxy on AnVIL". The title
sets the arc the poster now follows — elastic Batch compute on the left, AI
assistance in the closing band, whose heading picks up the ellipsis
(*"… to Bots: Conversational Analysis"*).

**List items were reduced to their highlighted phrase.** Every
`.annotation-list` item that read *"**Key phrase** — trailing explanation"* lost
the trailing half. The `<strong>` was kept, so the checkmark lists now read as
short bold statements. This is faithful to the instruction; if the all-bold
weight ever looks heavy, dropping `<strong>` is a one-line change.

**The startup deep dive is gone.** The task-breakdown bars (`.taskbars` /
`.tb`) and `phase-duration.png` were removed, and the two cards they filled
collapsed into a single **~15 min** stat plus one line naming the tool panel as
the cause and Galaxy 26.2 lazy loading as the fix. This was a deliberate choice
between keeping the engineering credibility and making room for user-facing
content; the numbers survive in the "Facts" section above if they are ever
wanted back.

**The AI band lost its comparison table.** The GalaxyAI vs Orbit/Loom table
(*Where it runs / How it reaches Galaxy / Authentication / Scope / Model
backend*) and the three-step `galaxy-mcp` flow were cut as too technical for
the new brief. The two `.path-box` panels now carry the distinction in plain
terms. The `.cmp` table CSS is still in the `<style>` block, unused.

**Type scale.** Raised roughly 75% overall from the version this was forked
from — body 21pt → 37pt, card headings 31pt → 55pt, the solo metric number
58pt → 110pt. The footer is the one exception: it was pinned back by hand
(contact 22pt, acknowledgement 17pt) because scaling it with everything else
crowded the logos.

**Current state: 43.27in of 44in — 0.73in of slack.** Tighter than previous
versions, because the brief was to fill the page with large type. At this size
a single added list item can overflow, so run `check` after any edit.

**Column balance.** `Where It Stands` sits in column 2 under `Cheaper to Run`
purely for height balance — the three columns are otherwise within about half
an inch of each other.

## Content pass: intro copy, new "How it works" list, QR code (2026-08-19)

At the authors' request: title collapsed to one line ("From Batch to Bots:
Galaxy on AnVIL", `<h1>` alone, no separate `.subtitle`, font dropped from
126pt to 64pt to fit); `What You Get` renamed to `Galaxy on AnVIL` with its
bullet list replaced by one descriptive paragraph; a new card `How Galaxy on
AnVIL Works` added (6 dash-list items); `Elastic by Default` lost its
"Same data on or off the node" line and had its vCPU line replaced with "Up to
60 vCPUs and 240GB memory per job"; `Cheaper to Run`'s two list lines were
reworded ("Standby Galaxy is cheaper" / "Compute costs track the workload");
`Where It Stands` was removed outright (confirmed with the authors — nothing
took its place); `Fixes Reach You Sooner` gained a lead sentence about the new
upgrade process and reworded "Releases propagate themselves" to "Releases
managed via GitHub Actions"; `Try It` was replaced with a QR code
(`images/qrcode-galaxy-how-to.png`, 490x490) next to one sentence, in a new
`.qr-row` flex layout (image fixed at 1.9in) instead of stacking, to save
vertical space. All `.annotation-list` checkmarks became en dashes
(`\2013`), with `li` padding-left increased 0.3in &rarr; 0.4in for better
gap from the marker to the text.

**The "How it works" list could not fit as written.** The authors' original
text was six full sentences (label + explanation each, e.g. "Each user gets
an individual Galaxy instance — a private, customizable analysis
environment."). At this poster's 43pt body type that overflowed the page by
**18.6in** on its own — full sentences run 3-4 lines each at this size, which
is exactly why every other list on this poster is short bold phrases only.
Asked to choose, the authors picked a middle ground: bold label + a short
em-dash clause (e.g. "**Your own Galaxy** — a private, customizable
instance"), not the bare label the poster's existing lists use elsewhere.
This is a **deliberate exception** to the "every list item is just its bolded
phrase" rule described earlier in this file — don't silently reformat it back
to bare labels.

**Fitting the rest, in lever order:**
1. Columns were rebalanced twice (by card, not by rewording) once actual
   card heights were measured. Grouping at the time: col 1 = `Cheaper to Run`
   + `Elastic by Default` (the two cards with a `.figure` chart, so the next
   lever compounds on the same column); col 2 = `Galaxy on AnVIL` + `How
   Galaxy on AnVIL Works`; col 3 = `Fixes Reach You Sooner` + `Startup` +
   `Try It`. This is a pure height-balancing arrangement — expect it to move
   again if a future edit changes any card's length materially. (Superseded
   the same day — see below.)
2. `.figure img` width dropped from 100% to 50%, shrinking `cost-time.png`
   and `batch-service.png` (the only two `.figure` uses — the AI band figure
   is unaffected, it uses `.band-figure img` and stays at its legibility
   floor per the rule above).
3. `.card p, .card li` line-height 1.34 &rarr; 1.28, and `.card li`
   margin-bottom 0.06in &rarr; 0.04in — a small uniform tightening across
   every card and the AI band.
4. `.card` padding 0.3in &rarr; 0.26in, again uniform across every card.

None of the wording was shortened to make this fit — every content change
above is exactly what the authors asked for or approved.

**Current state at this point: 43.73in of 44in — 0.27in of slack**, measured
on macOS. This is tighter than most of this poster's history; the CI/macOS
gap noted above (CI reads ~0.2in shorter) means CI will likely show
~0.45-0.5in — don't let a green CI run read as more headroom than there
actually is on a Mac. Any future addition to this poster should re-run
`check` immediately and expect to need one of the levers above again.

## Layout rework for thematic flow (2026-08-19, same day)

The column order above put `Galaxy on AnVIL` and `How Galaxy on AnVIL Works`
side by side in the middle of the page rather than leading the poster, which
read oddly since together they're the natural opening pair. Reworked at the
authors' request:

- **Column 1 (top left, under the title) is now `Galaxy on AnVIL` directly
  followed by the renamed `Advantages` card** (was `How Galaxy on AnVIL
  Works`). `Cheaper to Run` and `Elastic by Default` moved to column 2 —
  this is a straight swap of column 1 and column 2's contents, so total
  column heights, and therefore the fit measurement, are unchanged (still
  43.73in / 0.27in slack). Column 3 (`Fixes Reach You Sooner`, `Startup`,
  `Try It`) is untouched.
- **`Advantages`'s em dashes became colons** (`&mdash;` &rarr; `:`), e.g.
  "**Your own Galaxy:** a private, customizable instance" — this only
  affects this one list, not the en-dash bullet markers used everywhere
  (those stay `\2013`, per the earlier "checkmarks to dashes" request).
- **`Advantages`'s "Connected to your data" line** now reads "from AnVIL,
  cloud, or local" (was "no cumbersome transfers").
- **`.tn-box ul` padding-left** (the "Then"/"Now" bullet lists in `Fixes
  Reach You Sooner`) increased 0.25in &rarr; 0.4in, so the bullets sit
  further from the box's left edge.

Every reference to "How Galaxy on AnVIL Works" earlier in this file (the
lever notes above, the overflow story) refers to what is now the
`Advantages` card — same content, renamed and relocated.

## Bigger chart figures, Elastic/Cheaper reorder (2026-08-19, same day)

The authors trimmed several other cards' prose in this pass (the `Galaxy on
AnVIL` intro paragraph, `Startup`, and the `Fixes Reach You Sooner`/`Then`
line), which freed 1.56in of slack — that headroom is what made the change
below possible.

- **`Elastic by Default` now comes before `Cheaper to Run`** (column 2,
  order swapped; still the same column, just Elastic on top, per the
  authors).
- **`.figure img` width raised from 50% to 60%** — `cost-time.png` and
  `batch-service.png` were unreadable at 50%, especially the chart's axis
  labels and legend. 65% overflows the page by 0.33in; 60% is the largest
  width that keeps a reasonable safety margin (0.30in of slack). This is
  the same lever documented above (the AI band figure is still unaffected —
  it uses `.band-figure img`, not `.figure img`).
- Fixed two typos introduced in the authors' text edit while rebuilding:
  a stray `&mdash,` (missing semicolon, in the `Startup` card's metric
  label) and "vresions" &rarr; "versions" in the same card's body text.

**Current state: 43.70in of 44in — 0.30in of slack**, measured on macOS.
Both figures are still native-resolution-limited (`cost-time.png` is only
621&times;420px), so they're now sharper-looking than before but not
perfectly crisp — that's a source-image ceiling, not a CSS one. If they need
to be larger still, the next options are: re-export the source charts at
higher resolution (no layout cost), or free more vertical room elsewhere in
`Elastic by Default` / `Cheaper to Run` specifically (their metrics tiles
and intro sentence are the only other content in that column).

## Unequal column widths + bigger figures still, header trim (2026-08-19, same day)

Widening `.figure img` alone had run into a real ceiling — 60% was already
close to the largest width the *equal* three-column grid could take. The
authors asked for the middle column to be widened at the two outer columns'
expense instead, to give the figures more room without more vertical cost.

- **Removed "ACC2026" from the header's `logo-right` box** (the `.conf` div
  and its now-unused CSS rule). This wasn't just cosmetic: the header lost a
  full 65pt line, and since `.content` sits in the body grid's `1fr` row,
  a shorter header directly gave the content area **1.17in** more room
  (0.30in &rarr; 1.47in slack) before any column-width change.
- **`.content` grid-template-columns changed from `1fr 1fr 1fr` to
  `0.95fr 1.1fr 0.95fr`** — column 2 (`Elastic by Default` / `Cheaper to
  Run`, the only cards with a `.figure` chart) is now wider; columns 1 and 3
  are narrower. This was tuned by measurement, not guessed: a more
  aggressive `0.8fr 1.4fr 0.8fr` was tried first and *lost* ground overall,
  because narrowing columns 1 and 3 that much made their text wrap onto
  many more lines — `Advantages` alone grew by 4.6in — which made column 1
  or 3 the new bottleneck instead of column 2. `0.95/1.1/0.95` is close to
  the narrowest split that doesn't trigger that penalty.
- **`.figure img` width raised from 60% to 73%** — found the same way as
  the 50%&rarr;60% change in the prior entry: bisect on measured overflow,
  not estimated. At this column width, 90% overflows by 2.04in; 73% lands
  at 0.35in of slack. Column 2 (with the two figures) is now the tallest of
  the three, which means this is the real ceiling for this lever at this
  column ratio — further growth has to come from a wider column 2 again, a
  higher-resolution source image, or less non-figure content in those two
  cards.

**Current state: 43.65in of 44in — 0.35in of slack**, measured on macOS.
Both chart images read clearly now at normal viewing distance (verified via
cropped preview renders) despite `cost-time.png`'s low native resolution
(621&times;420px) — a bigger blurry chart reads better on a printed poster
than a smaller one, up to a point neither figure has hit yet.

## Figure sources (2026-08-20)

`ai-architecture.png` had no source in this repository. It was authored as a
published Claude artifact on 2026-08-11
(`claude.ai/code/artifact/5f54f378-053d-47ce-a360-1cbdb827e14c`) and only the
rasterised PNG was ever committed, so the figure could not be edited or
re-rendered from the repo. A near-identical *older* version exists at
`galaxy-k8s-boot/gcc2026/galaxyai-architecture.html` (2026-07-21) — it predates
the Orbit/Loom tool-path band and is **not** what the poster used.

The source is now committed at `posters/acc2026/figures/ai-architecture.html`,
and `scripts/figures.py` renders `posters/<name>/figures/*.html` into
`posters/<name>/images/`.

### Why the renderer zooms the raster instead of widening the layout

The figure is a container-query design: type sizes are `clamp(min, Ncqw, max)`.
Past its ~1120px design width every size is pinned at its maximum, so laying it
out wider grows the boxes while the text stands still. `figures.py` therefore
renders at the design width and scales with `--force-device-scale-factor`,
which enlarges everything uniformly.

Two `<meta>` tags in a source drive it:

| Meta | Purpose |
|---|---|
| `render-width-in` | How wide the PNG sits on the poster. With `--dpi` this sets the pixel width — **measure it, don't guess** |
| `render-hide` | Selectors dropped before rendering |

For this figure `render-hide` drops `.head`, `.toolpath` and `.legend`, matching
the original crop: the poster's own heading covers the first, and the band text
covers the others. The full diagram is preserved in the source, so the tool path
(`Orbit brain → MCP gateway → galaxy-mcp → Galaxy REST API`) and the legend can
be brought back by editing one meta tag.

An earlier attempt cropped to the measured bounds of `.flow` instead. That is
fragile: the slide is vertically centred in the viewport, so the crop needs a
viewport tall enough to hold it, and the resulting ~60-megapixel screenshot got
clipped — the crop then landed on the wrong region and pulled the heading in.
Stripping the page down and letting the wanted part *be* the whole image needs
no coordinate arithmetic.

### Resolution

The figure is placed **19.71in wide** (measured, not assumed — the AI band grid
gives it that much). The old PNG was 2210px, i.e. **112 dpi as printed** —
acceptable on screen, soft on paper. It is now 5800px, **294 dpi**, for 467 KB.

Re-render after any edit to the source:

```bash
python3 scripts/figures.py            # every figure, 300 dpi
python3 scripts/figures.py --dpi 150  # lighter, for drafts
```

The swap is layout-neutral: the AI band's height is set by its **text** column,
not the figure, so both the old and new PNG measure the same overall height.

## "What's Next" replaces the Startup box (2026-08-20)

Requested changes, all in column 3 unless noted:

| Change | Note |
|---|---|
| `Fixes Reach You Sooner` → **Easier Updates** | Set in Title Case to match every other `<h2>`; the request wrote it lower-case |
| `Advantages` → **AnVIL Advantages** | column 1 |
| Dropped *"As the only no-code analysis solution on AnVIL,"* | column 1 — a superlative that would need defending |
| **Startup box removed** | its `~15 min` figure is gone from the poster entirely |
| **What's Next box added** | in the Startup box's slot, so `Try It` stays the closing call to action |

The Startup box's sentence moved into What's Next as its intro, minus its
closing clause: it read *"Building the tool panel dominates. Future versions
will target 5–6 min."*, and the new bullet *"Startup down to a ~6 min target"*
already carries the target. Keeping both would have stated it twice in adjacent
lines.

**Note that the poster no longer states current startup time anywhere.** The
`~15 min` measurement is only in the fact trail above. What's Next says where it
is going, not where it is — deliberate, but worth knowing if anyone asks at the
board.

Height is unchanged at **43.65in of 44in**: the tallest column is column 2
(`Cheaper to Run`), which none of this touched.

## Google Slides export (2026-08-20)

`scripts/extract_layout.py` + `scripts/to_slides.py` rebuild the poster as a
**native, editable** Google Slides deck, so collaborators can change it without
touching HTML.

```bash
python3 scripts/extract_layout.py > build/slides/layout.json
python3 scripts/to_slides.py <presentationId>
```

### The page-size trap

**The Slides API cannot create a 34×44in page.** `presentations.create` accepts
a `pageSize` and silently ignores it — requests for 34×44, 20×26 and 13.333×7.5
all came back as the default 10×5.625. `updatePageProperties` rejects a resize
outright. Page size is effectively read-only over the API.

Two ways around it, both verified:

1. **Copy a correctly-sized deck** (`drive files copy` preserves page size) —
   what we do, copying the reference deck the authors resized by hand.
2. **Import a PPTX**: `python-pptx` at 34×44 uploaded with
   `mimeType: application/vnd.google-apps.presentation` converts with the size
   intact and elements still native.

### How the rebuild works

Slides has no layout engine, so `extract_layout.py` asks Chrome where every
element actually landed (`getBoundingClientRect`, plus computed font size,
weight and colour) and emits JSON; `to_slides.py` turns that into Slides API
requests. Copying measured geometry beats hand-positioning ~65 blocks.

Two deliberate departures from a literal translation:

- **Consecutive bullets in a card become one text box** with real Slides
  bullets. Slides does not reflow between boxes, so one box per line means a
  collaborator adding a sentence silently overlaps what is beneath it.
- **Arial, not Helvetica Neue** — Slides does not have the latter, and the
  reference deck uses Arial.

### Things that bit, in order

| Symptom | Cause |
|---|---|
| `--json @file` rejected | `gws` has no `@file` form; pass JSON inline |
| `--upload` refused an absolute path | `gws` only uploads from under the working directory |
| `object ID (s001) length should not be less than 5` | Slides requires ≥ 5-character IDs |
| Text overflowing its card | Slides `lineSpacing: 100` already carries ~1.2 leading; CSS `line-height` must be divided by 1.2, not passed through |
| Logos invisible on the header bar | The CSS sits them on a white pill; the Slides build has to draw that rectangle |
| Path-box titles overlapping their bullets | Fixed offsets guessed at the title height — those titles wrap. Fixed by measuring `.p-title` and `ul` boxes too |

### What does not survive

Box shadows, the CSS `::before` dash bullets (Slides uses discs), and rounded
card corners — `ROUND_RECTANGLE` has a far larger radius than the CSS 0.12in, so
plain rectangles read closer. Images are pulled from the **GitHub Pages URLs**,
which is why `poster.py site` publishing `images/` matters: `createImage`
needs a publicly reachable URL.

## Direction of truth: HTML, not Slides (2026-08-20)

The authors' decision: **`posters/acc2026/poster.html` is authoritative.** The
Google Slides deck is a generated view for collaborators.

This matters because `to_slides.py` **clears the slide before rebuilding**, so a
regeneration silently destroys anything edited in Slides — which is exactly what
collaborators were given the deck to do. The two facts sit awkwardly together,
so the script now guards the gap:

- `posters/<name>/slides.json` holds the deck id and the Drive `version`
  recorded at the end of the last run.
- On each run the live version is fetched. If it has moved, the script refuses,
  naming who last modified the deck and when, and pointing at `poster.html`.
- `--force` overrides, and is the right call only once anything worth keeping
  has been ported back into the HTML.

**The workflow this implies:** collaborators edit or comment in Slides; those
changes are read, applied to `poster.html`, and the deck is regenerated from it.
The deck is never the place a change lands permanently.

## Resized to 36 × 48in (2026-08-21)

`@page` and the `body` rule now read 36in × 48in. Two things had to follow.

**Type scale +8%.** A wider page wraps less, so the same content on a 48in page
measured only 44.32in — 3.68in short. Scaling every size by 1.08 brings it to
**46.27in of 48in (1.73in slack)**.

The pt rounding quantizes hard at these sizes: 1.08 gives 46.27in, while 1.09
*and* 1.10 both give 47.71in (0.29in slack). There is nothing in between, so
this is a choice between ~1.7in of bottom margin and a margin too thin to
survive an edit. 1.08 is the safe one.

**The AI figure is wider.** The band now gives it **20.93in** (was 19.71in), so
`render-width-in` was updated and the figure re-rendered — 6160px, 294 dpi.
Re-measure this after any change to the band or the page size; a stale value
silently degrades print resolution.

### Resizing the Slides deck

The Slides API cannot resize a page — but **`drive files update` can replace an
existing presentation's contents with a PPTX while keeping the file ID**, and
therefore the URL. Build a correctly-sized PPTX with `python-pptx`, update the
file with it, then regenerate:

```bash
python3 -c "from pptx import Presentation; from pptx.util import Inches; \
p=Presentation(); p.slide_width,p.slide_height=Inches(36),Inches(48); \
p.slides.add_slide(p.slide_layouts[6]); p.save('build/slides/resize.pptx')"
gws drive files update --params '{"fileId":"<id>"}' \
  --upload build/slides/resize.pptx \
  --upload-content-type application/vnd.openxmlformats-officedocument.presentationml.presentation
python3 scripts/extract_layout.py > build/slides/layout.json
python3 scripts/to_slides.py --force
```

`--force` is required and correct here: replacing the file is itself an edit, so
the guard fires.

### Correction: the overwrite guard was measuring the wrong thing

The guard first shipped keyed to Drive's `version` field. **That does not
work.** Verified directly: 311 Slides API write requests left both `version` and
`modifiedTime` completely unchanged — they moved only when the file's bytes were
replaced via `files.update`. A guard on those fields would have sailed straight
through exactly the case it existed to catch.

It now hashes the deck's own contents — object IDs, element kinds, and text —
and compares that. Confirmed against a real edit: adding one shape changed the
fingerprint from `f0f5800228765423` to `1b90ccb23d96a86d` and the script
refused.

## Layout polish: wider diagrams, slack below the footer (2026-08-21)

Four changes, in the order they had to happen — the third unlocked the first.

**Empty space now falls below the footer.** The body grid was
`auto 1fr auto`, so the content row stretched and pinned the footer to the
bottom of the page, parking every spare inch *between* the AI band and the
footer. It is now `auto auto auto` with `align-content: start`, so the footer
follows the band directly and the remainder lands beneath it:

| | Before | After |
|---|---|---|
| Band → footer | 1.25in | **0.25in** (the grid gap) |
| Below footer | 0 | **0.63in** |

**Card swaps.** `Where It Stands` sits above `What's Next` in column 3; `Try It`
closes column 1.

**Diagrams widened 73% → 86%** (8.73in → **10.40in** in a 12.76in card). A
straight widen stalls at 82%, so two things bought the extra room:

- `cost-time.png` was trimmed of its dead margin (621×420 → 596×382). Besides
  enlarging the plotted area, this widens its aspect from 1.479 to 1.560, so the
  same displayed width costs less height.
- `.figure` padding cut from 0.12in to 0.05in.

### 86% is the ceiling, and why

88% overflows by 0.01in, 90% by 0.31in. Column 2 is now the tallest column
(33.26in), so every further percent pushes the whole page down. The obvious
sources of more room are already exhausted:

- **`batch-service.png` has zero trimmable margin** — measured, the content
  bounding box is the full 1720×991.
- **The band's height comes from its text column** (9.83in) not its figure
  (7.97in), so narrowing the figure column does nothing. Swept 1.55 / 1.40 /
  1.25 fr — the total did not move at all.

Going wider than 86% therefore needs a content decision, not a CSS one: drop
`Where It Stands` (~3in, gets to roughly 95–100%), cut the band text (the two
path panels and the NIH callout are what make it 9.83in), or reduce the type
scale ~4% — which reverses the direction the authors have asked for twice.

**Current state: 47.72in of 48in**, columns 33.21 / 33.26 / 29.66.

## The Google Slides export is dormant (2026-08-24)

The authors stopped using the Slides copy — it was not being used in practice.

**Nothing was deleted.** `scripts/extract_layout.py`, `scripts/to_slides.py`,
`posters/acc2026/slides.json` and the deck itself all remain, and the sections
above still describe how the export works and the Slides API limits it works
around. Both scripts now carry a DORMANT note in their docstrings, and
`CLAUDE.md` instructs future sessions not to run them.

**The deck will drift from the poster, and that is fine.** It is frozen at the
2026-08-24 layout. Do not treat regenerating it as part of finishing a poster
change; a stale deck is the expected state, not a bug.

**If it is ever resumed:** `slides.json` still holds the deck id and a
fingerprint that matches the live deck as of the freeze, so the overwrite guard
will behave correctly rather than firing spuriously on the first run back.
Re-read the sections above first — particularly that the Slides API cannot set a
page size, and that Drive's `version` and `modifiedTime` do not track Slides API
edits.
