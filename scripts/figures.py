#!/usr/bin/env python3
"""Render figure sources to print-resolution PNGs.

Each `posters/<name>/figures/<figure>.html` is rendered to
`posters/<name>/images/<figure>.png`.

The sources are container-query designs whose type sizes are `clamp()`ed with a
maximum, so widening the layout past the design width makes the text stop
growing while the boxes keep going. Instead the page is laid out at its design
width and the *raster* is scaled up, which enlarges everything uniformly.

Two optional `<meta>` tags in a source control the render:

    <meta name="render-hide" content=".head, .legend">  drop these from the render
    <meta name="render-width-in" content="19.71">   printed width, in inches

`render-width-in` is how wide the PNG will be placed on the poster; with
`--dpi` it sets the pixel width. Measure it rather than guess -- see
docs/POSTER_NOTES.md.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import poster as P  # noqa: E402  (shared Chrome plumbing)

ROOT = P.ROOT
DESIGN_WIDTH = 1120  # the .slide max-width these sources are designed at


def meta(html, name, default=None):
    m = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"', html)
    return m.group(1) if m else default


def trim(im, margin=0, tol=6):
    """Trim uniform background from the edges, then re-add a small margin.

    A flex container that has grown to fill its row leaves dead space above and
    below the boxes it holds; cropping to the element's own bounds would bake
    that into the figure and make it needlessly tall on the page.
    """
    from PIL import Image, ImageChops
    bg = Image.new("RGB", im.size, im.convert("RGB").getpixel((0, 0)))
    diff = ImageChops.difference(im.convert("RGB"), bg).convert("L")
    box = diff.point(lambda v: 255 if v > tol else 0).getbbox()
    if box is None:
        return im
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - margin), max(0, y0 - margin),
                    min(im.width, x1 + margin), min(im.height, y1 + margin)))


def render(src, dpi, out_dir):
    html = src.read_text(encoding="utf-8")
    hide = meta(html, "render-hide", "")
    width_in = float(meta(html, "render-width-in", "10"))

    # Raster zoom: lay out at the design width, scale the pixels. Widening the
    # layout instead would hit the clamp() maximums on every type size.
    scale = round(width_in * dpi / DESIGN_WIDTH, 4)

    # Rather than screenshot the page and crop by measured coordinates -- which
    # needs a viewport tall enough to hold a centred slide, and a raster large
    # enough to survive it -- strip the page down to just the wanted part and
    # let it be the whole image.
    reset = f"""
<style id="figure-render-reset">
  html, body {{ margin: 0 !important; padding: 0 !important;
                display: block !important; min-height: 0 !important;
                background: #fff !important; }}
  .slide {{ width: {DESIGN_WIDTH}px !important; aspect-ratio: auto !important;
            border: 0 !important; border-radius: 0 !important;
            box-shadow: none !important; overflow: visible !important; }}
  {hide + " { display: none !important; }" if hide else ""}
</style>
"""
    tmp = src.with_name("." + src.stem + "-render.html")
    tmp.write_text(html.replace("</head>", reset + "</head>", 1), encoding="utf-8")

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (src.stem + ".png")
    shot = src.with_name("." + src.stem + "-shot.png")
    shot.unlink(missing_ok=True)
    try:
        P.run_chrome(
            f"--screenshot={shot}",
            f"--window-size={DESIGN_WIDTH},{DESIGN_WIDTH}",
            f"--force-device-scale-factor={scale}",
            "--default-background-color=FFFFFFFF",
            tmp.as_uri(),
            ready=lambda _: P.settled_file(shot),
        )
        from PIL import Image
        im = trim(Image.open(shot), margin=round(6 * scale))
        im.save(out)
    finally:
        shot.unlink(missing_ok=True)
        tmp.unlink(missing_ok=True)

    print(f"wrote {out.relative_to(ROOT)} ({im.width}x{im.height}, "
          f"{im.width / width_in:.0f} dpi at {width_in}in wide)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("poster", nargs="?", help="poster name (default: all)")
    ap.add_argument("--dpi", type=int, default=300,
                    help="target print resolution (default: 300)")
    args = ap.parse_args()

    found = False
    for d in P.discover(args.poster):
        for src in sorted((d / "figures").glob("*.html")):
            found = True
            render(src, args.dpi, d / "images")
    if not found:
        sys.exit("No figure sources found under posters/*/figures/")


if __name__ == "__main__":
    main()
