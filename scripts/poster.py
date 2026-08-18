#!/usr/bin/env python3
"""Build and check the ACC2026 poster.

Subcommands:
  check    measure the laid-out poster and fail if it exceeds the page height
  flex     generate build/poster-flex.html (scales the poster to the window)
  pdf      generate build/poster.pdf (print-ready, one page)
  preview  generate build/poster-preview.png (downscaled, for PR review)
  all      flex + pdf + preview

Everything is derived from poster/poster.html, which is the only file to edit
by hand. Page size is read from its @page rule, so changing the poster
dimensions there is enough -- no size is hard-coded here.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path

DPI = 96
ROOT = Path(__file__).resolve().parent.parent
POSTERS = ROOT / "posters"
BUILD = ROOT / "build"


def discover(name=None):
    """Return the poster directories to act on.

    With no name, every poster under posters/ is returned, so `check` in CI
    covers all of them without needing a list kept in step with the tree.
    """
    if not POSTERS.is_dir():
        sys.exit(f"Missing {POSTERS.relative_to(ROOT)}/")
    found = sorted(d for d in POSTERS.iterdir() if (d / "poster.html").is_file())
    if not found:
        sys.exit(f"No posters found under {POSTERS.relative_to(ROOT)}/")
    if name is None:
        return found
    picked = [d for d in found if d.name == name]
    if not picked:
        sys.exit(f"No poster named {name!r}. Available: "
                 + ", ".join(d.name for d in found))
    return picked

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome-stable",
    "google-chrome",
    "chromium-browser",
    "chromium",
]


def find_chrome():
    """Locate a Chrome/Chromium binary, honouring $CHROME."""
    override = os.environ.get("CHROME")
    if override:
        if Path(override).is_file() and os.access(override, os.X_OK):
            return override
        sys.exit(f"CHROME is set to {override!r}, which is not an executable file")
    for candidate in CHROME_CANDIDATES:
        found = candidate if Path(candidate).is_file() else shutil.which(candidate)
        if found and os.access(found, os.X_OK):
            return found
    sys.exit(
        "No Chrome or Chromium found. Install Google Chrome, or point $CHROME at a binary."
    )


BASE_FLAGS = [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    # Headless Chrome otherwise blocks on background services at startup, which
    # is slow with a fresh profile and hangs outright without network access.
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-sync",
    "--disable-client-side-phishing-detection",
]


def run_chrome(*args, ready, timeout=180):
    """Run headless Chrome until `ready` reports that its output has landed.

    Chrome reliably produces the artifact and then fails to exit, sitting in
    shutdown for minutes. So rather than wait on the process, poll for the
    output and stop Chrome as soon as it appears.

    `ready` is called with the path holding Chrome's stdout and returns None
    while the output is still pending, or the result once it is complete.
    """
    profile = tempfile.mkdtemp(prefix="poster-chrome-")
    stdout_path = Path(profile) / "stdout"
    cmd = [find_chrome(), *BASE_FLAGS, f"--user-data-dir={profile}", *args]
    with open(stdout_path, "wb") as sink:
        proc = subprocess.Popen(cmd, stdout=sink, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + timeout
        while time.time() < deadline:
            result = ready(stdout_path)
            if result is not None:
                return result
            if proc.poll() is not None:
                # Chrome exited on its own; the output is as complete as it gets.
                result = ready(stdout_path)
                if result is not None:
                    return result
                sys.exit(f"Chrome exited {proc.returncode} without producing output")
            time.sleep(0.25)
        sys.exit(f"Chrome produced no output within {timeout}s")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def settled_file(path, _seen={}):
    """Report a file as ready once it exists and its size has stopped growing."""
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        return None
    size = path.stat().st_size
    if _seen.get(path) == size:
        return path
    _seen[path] = size
    return None


def read_source(src):
    if not src.is_file():
        sys.exit(f"Missing {src.relative_to(ROOT)}")
    return src.read_text(encoding="utf-8")


def page_size(html):
    """Return the (width, height) in inches declared by the @page rule."""
    match = re.search(
        r"@page\s*\{[^}]*size:\s*([\d.]+)in\s+([\d.]+)in", html, re.IGNORECASE
    )
    if not match:
        sys.exit("Could not find an '@page { size: Win Hin }' rule in poster.html")
    return float(match.group(1)), float(match.group(2))


def body_rule(html):
    """Return the `body { ... }` block that sets the poster's fixed size."""
    match = re.search(r"\n  body \{.*?\n  \}", html, re.DOTALL)
    if not match:
        sys.exit("Could not find the top-level 'body { ... }' rule in poster.html")
    return match


# --------------------------------------------------------------------------
# check
# --------------------------------------------------------------------------

def cmd_check(args, src):
    """Lay the poster out with an unconstrained height and measure the result.

    The poster's height is fixed, so content that no longer fits is simply
    clipped off the bottom of the page and the HTML still looks fine in a
    browser. Relaxing the height to `auto` makes the overflow measurable.

    The measuring copy is written next to poster.html so that its relative
    `images/` references still resolve; a broken image collapses to a
    zero-height box and makes the poster measure short.
    """
    html = read_source(src)
    width_in, height_in = page_size(html)
    limit_px = round(height_in * DPI)

    rule = body_rule(html)
    relaxed, count = re.subn(
        r"height:\s*[\d.]+in", "height: auto", rule.group(0), count=1
    )
    if count != 1:
        sys.exit("The body rule has no fixed 'height: <N>in' to relax")
    probe = (
        "<script>window.addEventListener('load', function () {"
        "document.title = 'MEASURED_PX:' + document.body.scrollHeight;"
        "});</script>\n"
    )
    measured_html = (
        html[: rule.start()] + relaxed + html[rule.end():]
    ).replace("</body>", probe + "</body>", 1)

    probe_file = src.with_name(".measure.html")
    probe_file.write_text(measured_html, encoding="utf-8")

    def measured(stdout_path):
        match = re.search(r"MEASURED_PX:(\d+)", stdout_path.read_bytes().decode(
            "utf-8", "replace"))
        return int(match.group(1)) if match else None

    try:
        # --dump-dom prints the DOM once the load event fires, which is exactly
        # when the probe has recorded the height.
        actual_px = run_chrome(
            "--dump-dom",
            f"--window-size={round(width_in * DPI)},{limit_px}",
            probe_file.as_uri(),
            ready=measured,
        )
    finally:
        probe_file.unlink(missing_ok=True)

    actual_in = actual_px / DPI
    slack_in = height_in - actual_in

    print(f"{src.parent.name}: content height: {actual_in:.2f}in of "
          f"{height_in:g}in ({slack_in:+.2f}in slack)")
    if actual_px > limit_px:
        sys.exit(
            f"FAIL: {src.parent.name} overflows its {height_in:g}in page by "
            f"{-slack_in:.2f}in. Content past the bottom edge is silently "
            f"dropped when the PDF is printed. See docs/POSTER_NOTES.md for "
            f"the levers to reclaim space, least damaging first."
        )
    if slack_in < 0.15:
        print(f"warning: only {slack_in:.2f}in of slack left", file=sys.stderr)


# --------------------------------------------------------------------------
# flex
# --------------------------------------------------------------------------

FLEX_CSS = """  /* ── Flex viewer: scales the fixed {w:g}x{h:g}in poster to fit the window ── */
  html, body {{ margin: 0; background: #dfe5ec; width: 100%; overflow: auto; }}
  #stage {{ transform-origin: top left; margin: 0 auto; }}
  #stage .poster {{ box-shadow: 0 0.1in 0.5in rgba(0,0,0,0.25); }}
"""

FLEX_JS = """
<script>
(function () {{
  var DPI = {dpi}, W = {w:g} * DPI, H = {h:g} * DPI;
  var stage = document.getElementById('stage');
  function fit() {{
    var pad = 24;
    var s = Math.min((window.innerWidth - pad) / W, (window.innerHeight - pad) / H);
    stage.style.transform = 'scale(' + s + ')';
    stage.style.width = W + 'px';
    stage.style.height = H + 'px';
    document.body.style.height = (H * s + pad) + 'px';
    stage.style.marginLeft = Math.max(0, (window.innerWidth - W * s) / 2) + 'px';
    stage.style.marginTop = (pad / 2) + 'px';
  }}
  window.addEventListener('resize', fit);
  window.addEventListener('load', fit);
  fit();
}})();
</script>
"""


def cmd_flex(args, src):
    """Wrap the poster in a stage that scales it down to the browser window."""
    html = read_source(src)
    width_in, height_in = page_size(html)

    # The poster's own styling lives on `body`; move it onto `.poster` so the
    # wrapper divs can own the page background and the scaling transform.
    rule = body_rule(html)
    html = html[: rule.start()] + rule.group(0).replace(
        "\n  body {", "\n  .poster {", 1
    ) + html[rule.end():]

    css = FLEX_CSS.format(w=width_in, h=height_in)
    html = re.sub(r"(@page \{[^}]*\}\n)", r"\1" + css, html, count=1)
    html = re.sub(
        r"<title>(.*?)</title>", r"<title>\1 (fit to window)</title>", html, count=1
    )
    html = html.replace("<body>", '<body>\n<div id="stage"><div class="poster">', 1)
    js = FLEX_JS.format(dpi=DPI, w=width_in, h=height_in)
    html = html.replace("</body>", "</div></div>\n" + js + "\n</body>", 1)

    # Written into poster/ so its relative images/ paths keep working.
    out = src.with_name("poster-flex.html")
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# pdf / preview
# --------------------------------------------------------------------------

def cmd_pdf(args, src):
    outdir = BUILD / src.parent.name
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "poster.pdf"
    out.unlink(missing_ok=True)
    run_chrome(
        "--no-pdf-header-footer",
        f"--print-to-pdf={out}",
        src.as_uri(),
        ready=lambda _: settled_file(out),
    )
    pages = len(re.findall(rb"/Type\s*/Page[^s]", out.read_bytes()))
    if pages != 1:
        sys.exit(f"FAIL: {out.name} came out as {pages} pages; the poster must "
                 f"print as one. Run 'poster.py check' to see the overflow.")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB, 1 page)")


def cmd_preview(args, src):
    html = read_source(src)
    width_in, height_in = page_size(html)
    outdir = BUILD / src.parent.name
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "poster-preview.png"
    out.unlink(missing_ok=True)
    run_chrome(
        f"--screenshot={out}",
        f"--window-size={round(width_in * DPI)},{round(height_in * DPI)}",
        f"--force-device-scale-factor={args.scale}",
        "--default-background-color=FFFFFFFF",
        src.as_uri(),
        ready=lambda _: settled_file(out),
    )
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


SITE_INDEX = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ACC2026 Posters &mdash; Galaxy on AnVIL</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: #edf1f5; color: #2c2c2c; padding: 3rem 1.5rem;
  }}
  .wrap {{ max-width: 60rem; margin: 0 auto; }}
  h1 {{ color: #0C5294; font-size: 2rem; margin-bottom: 0.4rem; }}
  .sub {{ color: #6b6b6b; margin-bottom: 2.5rem; }}
  .grid {{ display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)); }}
  .card {{
    background: white; border-top: 5px solid #0C5294; border-radius: 0.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 1.2rem; display: flex; flex-direction: column;
  }}
  .card h2 {{ font-size: 1.1rem; color: #0C5294; margin-bottom: 0.7rem; }}
  .card img {{ width: 100%; border: 1px solid #c8d6e5; margin-bottom: 0.9rem; }}
  .links {{ margin-top: auto; display: flex; gap: 0.6rem; flex-wrap: wrap; }}
  .links a {{
    background: #0C5294; color: white; text-decoration: none;
    padding: 0.45rem 0.9rem; border-radius: 0.25rem; font-size: 0.9rem;
  }}
  .links a.alt {{ background: #e0ecf7; color: #0a3d6e; }}
</style></head><body><div class="wrap">
<h1>ACC2026 Posters</h1>
<div class="sub">Galaxy on AnVIL &mdash; AnVIL Community Conference, Broad Institute, August 31 &ndash; September 1 2026</div>
<div class="grid">{cards}</div>
</div></body></html>
"""

SITE_CARD = """  <div class="card">
    <h2>{title}</h2>
    <img src="{name}/poster-preview.png" alt="Preview of {title}">
    <div class="links">
      <a href="{name}/">View</a>
      <a class="alt" href="{name}/poster.pdf">PDF</a>
    </div>
  </div>
"""


def cmd_site(args, posters):
    """Assemble the GitHub Pages site: one landing page, one folder per poster."""
    site = ROOT / "site"
    shutil.rmtree(site, ignore_errors=True)
    site.mkdir()
    cards = []
    for d in posters:
        src = d / "poster.html"
        flex = d / "poster-flex.html"
        built = BUILD / d.name
        for needed in (flex, built / "poster.pdf", built / "poster-preview.png"):
            if not needed.is_file():
                sys.exit(f"Missing {needed.relative_to(ROOT)} - run 'poster.py all' first")
        out = site / d.name
        out.mkdir()
        shutil.copy(flex, out / "index.html")
        shutil.copytree(d / "images", out / "images")
        shutil.copy(built / "poster.pdf", out / "poster.pdf")
        shutil.copy(built / "poster-preview.png", out / "poster-preview.png")
        match = re.search(r"<title>(.*?)</title>", src.read_text(encoding="utf-8"))
        title = match.group(1).replace(" - ACC2026 Poster", "") if match else d.name
        cards.append(SITE_CARD.format(name=d.name, title=title))
    (site / "index.html").write_text(SITE_INDEX.format(cards="".join(cards)),
                                     encoding="utf-8")
    print(f"wrote site/ with {len(posters)} poster(s)")


def cmd_all(args, src):
    cmd_flex(args, src)
    cmd_pdf(args, src)
    cmd_preview(args, src)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    parsers = {
        "check": sub.add_parser("check", help="fail if a poster overflows its page height"),
        "flex": sub.add_parser("flex", help="generate <poster>/poster-flex.html"),
        "pdf": sub.add_parser("pdf", help="generate build/<poster>/poster.pdf"),
    }
    for name in ("preview", "all"):
        parsers[name] = sub.add_parser(name, help=f"generate {name} output")
        parsers[name].add_argument("--scale", type=float, default=0.35,
                                   help="preview scale factor (default: 0.35)")
    for p in parsers.values():
        p.add_argument("poster", nargs="?",
                       help="poster directory name under posters/ "
                            "(default: every poster)")
    parsers["site"] = sub.add_parser("site", help="assemble site/ for GitHub Pages")
    parsers["site"].add_argument("poster", nargs="?", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.command == "site":
        cmd_site(args, discover(args.poster))
        return
    for poster_dir in discover(args.poster):
        globals()[f"cmd_{args.command}"](args, poster_dir / "poster.html")


if __name__ == "__main__":
    main()
