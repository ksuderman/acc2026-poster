# ACC2026 Poster — Galaxy on AnVIL

Working notes for the poster in this directory. Read this first to resume work.

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
| `poster/poster.html` | The poster. Fixed 34in × 44in portrait, print-ready. Source of truth — edit this one. |
| `poster/images/` | `anvil_logo.png`, `galaxy_logo.png`, `galaxy_logo_white.png`, `jhu_logo_trimmed.png`, `cost-time.png`, `ai-architecture.png` |
| `poster/poster-flex.html` | **Generated.** Scales the whole poster to fit the browser window. |
| `build/poster.pdf` | **Generated.** Print-ready PDF, one page, MediaBox exactly 2448 × 3168 pt (34 × 44 in). |
| `build/poster-preview.png` | **Generated.** Downscaled raster, for pull request review. |

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

## Deliberately off the poster

The user asked to **remove all discussion of problems we had to resolve**, so the following are researched and available but intentionally not shown. Do not reintroduce them without asking:

- The "Engineering the long tail" section: the cross-project network fix (commit `e71a26bdb1`, qualifying network/subnet so Terra pet projects resolve) and the polling fix (~3,600 API calls/hr/job → ~30× reduction, `galaxy-dev/polling_interval.md`).
- The paragraph on interactive-tool infrastructure work: wildcard DNS zones, per-instance TLS, certificate persistence against Let's Encrypt rate limits, and keeping interactive sessions off Batch.
- The GalaxyAI model-portability bug (Gemini returning `tool_id` without `name`).
- The "removed an entire class of cross-project failures" phrasing in the Maintenance callout, and "could fail silently" in the Then box — both softened to describe the old design rather than its failures.

The **Then & Now** comparison was kept: it is the before/after improvement story `plan.md` explicitly asked for, and it now describes the old *design* rather than incidents.

## Regenerating derived files

```bash
python3 scripts/poster.py all      # flex viewer + PDF + PNG preview
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

⚠️ Font rendering differs between macOS and the Linux CI runner: the poster asks
for Helvetica Neue, which Linux lacks, so CI measures against metric-compatible
Liberation Sans. The numbers are close but not identical. Reproduce a marginal
CI failure locally before reworking the layout. Embedding a self-hosted webfont
would make the two agree exactly, at the cost of changing the typography.

Levers to fit, in order of least damage:
1. `.figure img { width: … }` on the cost chart (a full-width chart costs ~0.6in vs. 91%).
2. Rebalancing cards between columns — the AI band is fixed-height, so the three columns above it are what flexes.
3. Tightening prose.
4. Type sizes (already reduced ~10% from the skill defaults — reduce further only as a last resort).
5. The band's `1.55fr 1fr` split — see the legibility floor above before shrinking the figure.
