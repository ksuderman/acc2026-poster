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
   card heights were measured. Final grouping: col 1 = `Cheaper to Run` +
   `Elastic by Default` (the two cards with a `.figure` chart, so the next
   lever compounds on the same column); col 2 = `Galaxy on AnVIL` + `How
   Galaxy on AnVIL Works`; col 3 = `Fixes Reach You Sooner` + `Startup` +
   `Try It`. This is a pure height-balancing arrangement — expect it to move
   again if a future edit changes any card's length materially.
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

**Current state: 43.73in of 44in — 0.27in of slack**, measured on macOS. This
is tighter than most of this poster's history; the CI/macOS gap noted above
(CI reads ~0.2in shorter) means CI will likely show ~0.45-0.5in — don't let a
green CI run read as more headroom than there actually is on a Mac. Any
future addition to this poster should re-run `check` immediately and expect
to need one of the levers above again.
