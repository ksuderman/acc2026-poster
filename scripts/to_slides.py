#!/usr/bin/env python3
"""Build a Google Slides poster from an extracted layout.

Reads the JSON that extract_layout.py produces and emits Slides API requests
that reproduce it as native, editable page elements.

The HTML poster is authoritative. This deck is a generated view of it, and
regenerating CLEARS THE SLIDE FIRST -- any edit made in Slides is destroyed. To
protect against that, the deck's Drive `version` is recorded in
`posters/<name>/slides.json` after each run; if it has moved since, the script
refuses to run without --force.

Two deliberate departures from a literal translation:

* Consecutive bullets in a card become ONE text box with real Slides bullets,
  not one box per line. Slides does not reflow between boxes, so a collaborator
  adding a sentence to a one-line box silently overlaps whatever sits beneath
  it. One box per list keeps editing predictable.
* Fonts are Arial rather than Helvetica Neue, which Slides does not have. The
  reference deck uses Arial too, and it is metrically close.

Usage:  python3 scripts/to_slides.py [poster] [--force]
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

EMU = 914400
FONT = "Arial"
IMG_BASE = "https://ksuderman.github.io/acc2026-poster/"
# Slides insets text inside a box; nudge geometry so glyphs land where CSS put them.
INSET_X, INSET_Y = 0.1, 0.05


def emu(inches):
    return int(round(inches * EMU))


def color(css):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", css or "")
    if not m:
        return {"red": 0, "green": 0, "blue": 0}
    r, g, b = (int(v) / 255 for v in m.groups())
    return {"red": r, "green": g, "blue": b}


def hexc(h):
    h = h.lstrip("#")
    return {k: int(h[i:i + 2], 16) / 255 for k, i in (("red", 0), ("green", 2), ("blue", 4))}


class Deck:
    def __init__(self, pid, slide_id):
        self.pid, self.slide = pid, slide_id
        self.reqs, self.n = [], 0

    def _id(self, prefix):
        self.n += 1
        return f"{prefix}_{self.n:04d}"   # Slides requires >= 5 chars

    def box(self, b, dx=0, dy=0, dw=0, dh=0):
        return {"size": {"width": {"magnitude": emu(b["w"] + dw), "unit": "EMU"},
                         "height": {"magnitude": emu(b["h"] + dh), "unit": "EMU"}},
                "transform": {"scaleX": 1, "scaleY": 1,
                              "translateX": emu(b["x"] + dx), "translateY": emu(b["y"] + dy),
                              "unit": "EMU"}}

    def shape(self, kind, b, fill=None, outline=None, radius=None):
        oid = self._id("s")
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": kind,
                                          "elementProperties": {"pageObjectId": self.slide, **self.box(b)}}})
        props, fields = {}, []
        if fill is not None:
            props["shapeBackgroundFill"] = {"solidFill": {"color": {"rgbColor": fill}}}
            fields.append("shapeBackgroundFill")
        else:
            props["shapeBackgroundFill"] = {"propertyState": "NOT_RENDERED"}
            fields.append("shapeBackgroundFill")
        if outline:
            props["outline"] = {"outlineFill": {"solidFill": {"color": {"rgbColor": outline[0]}}},
                                "weight": {"magnitude": emu(outline[1]), "unit": "EMU"},
                                "dashStyle": "SOLID"}
            fields.append("outline")
        else:
            props["outline"] = {"propertyState": "NOT_RENDERED"}
            fields.append("outline")
        self.reqs.append({"updateShapeProperties": {"objectId": oid, "shapeProperties": props,
                                                    "fields": ",".join(fields)}})
        return oid

    def text(self, b, runs, style, align=None, bullets=False, valign="TOP"):
        """runs: list of {t, b(old), c(olor)} or list of such lists (one per paragraph)."""
        paras = runs if runs and isinstance(runs[0], list) else [runs]
        oid = self._id("t")
        self.reqs.append({"createShape": {"objectId": oid, "shapeType": "TEXT_BOX",
                                          "elementProperties": {"pageObjectId": self.slide,
                                                                **self.box(b, dx=-INSET_X, dy=-INSET_Y,
                                                                           dw=2 * INSET_X, dh=2 * INSET_Y)}}})
        text, spans = "", []
        for i, para in enumerate(paras):
            if i:
                text += "\n"
            for r in para:
                start = len(text)
                text += r["t"]
                spans.append((start, len(text), r))
        if not text.strip():
            return None
        self.reqs.append({"insertText": {"objectId": oid, "text": text}})
        self.reqs.append({"updateTextStyle": {
            "objectId": oid, "textRange": {"type": "ALL"},
            "style": {"fontFamily": FONT,
                      "fontSize": {"magnitude": style["size"], "unit": "PT"},
                      "foregroundColor": {"opaqueColor": {"rgbColor": color(style["color"])}},
                      "bold": style["weight"] >= 600},
            "fields": "fontFamily,fontSize,foregroundColor,bold"}})
        for a, z, r in spans:
            if z <= a:
                continue
            st, fl = {}, []
            if r.get("b"):
                st["bold"] = True; fl.append("bold")
            if r.get("c"):
                st["foregroundColor"] = {"opaqueColor": {"rgbColor": color(r["c"])}}
                fl.append("foregroundColor")
            if fl:
                self.reqs.append({"updateTextStyle": {
                    "objectId": oid, "textRange": {"type": "FIXED_RANGE", "startIndex": a, "endIndex": z},
                    "style": st, "fields": ",".join(fl)}})
        para_style, pf = {"lineSpacing": max(85, round(style.get("lh", 1.3) * 100 / 1.2)), "spaceBelow": {"magnitude": 0, "unit": "PT"}}, ["lineSpacing", "spaceBelow"]
        if align and align in ("CENTER", "END"):
            para_style["alignment"] = align; pf.append("alignment")
        self.reqs.append({"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                                   "style": para_style, "fields": ",".join(pf)}})
        if bullets:
            self.reqs.append({"createParagraphBullets": {
                "objectId": oid, "textRange": {"type": "ALL"},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        if valign != "TOP":
            self.reqs.append({"updateShapeProperties": {
                "objectId": oid, "shapeProperties": {"contentAlignment": valign},
                "fields": "contentAlignment"}})
        return oid

    def image(self, b, src):
        oid = self._id("i")
        url = IMG_BASE + src.replace("images/", "images/")
        self.reqs.append({"createImage": {"objectId": oid, "url": url,
                                          "elementProperties": {"pageObjectId": self.slide, **self.box(b)}}})
        return oid

    def flush(self, chunk=60):
        sent = 0
        while self.reqs:
            batch, self.reqs = self.reqs[:chunk], self.reqs[chunk:]
            body = json.dumps({"requests": batch}, separators=(",", ":"))
            r = subprocess.run(["gws", "slides", "presentations", "batchUpdate",
                                "--params", json.dumps({"presentationId": self.pid}),
                                "--json", body], capture_output=True, text=True)
            if '"error"' in r.stdout or r.returncode != 0:
                print(r.stdout[:1500] or r.stderr[:1500], file=sys.stderr)
                sys.exit(f"batch failed after {sent} requests")
            sent += len(batch)
        return sent


ACCENT = hexc("#0C5294")
LINE   = hexc("#c8d6e5")
TINT   = hexc("#f0f4f8")
NOWBG  = hexc("#e0ecf7")
WHITE  = hexc("#ffffff")


def build(deck, layout):
    blocks = layout["blocks"]
    cards = [b for b in blocks if b["type"] == "card"]

    def in_card(b, c):
        bb, cb = b["box"], c["box"]
        return (bb["x"] >= cb["x"] - .05 and bb["y"] >= cb["y"] - .05
                and bb["x"] + bb["w"] <= cb["x"] + cb["w"] + .05
                and bb["y"] + bb["h"] <= cb["y"] + cb["h"] + .05)

    # ---- backgrounds, painted first so everything else lands on top ----
    for b in blocks:
        if b["type"] in ("header", "footer"):
            deck.shape("RECTANGLE", b["box"], fill=ACCENT)
    for c in cards:
        deck.shape("RECTANGLE", c["box"], fill=WHITE, outline=(LINE, 0.012))
        deck.shape("RECTANGLE", {**c["box"], "h": 0.07}, fill=ACCENT)
    for b in blocks:
        t = b["type"]
        if t == "metric":
            deck.shape("RECTANGLE", b["box"], fill=TINT, outline=(LINE, 0.008))
        elif t == "tnbox":
            deck.shape("RECTANGLE", b["box"], fill=NOWBG if b.get("now") else TINT,
                       outline=(LINE, 0.008))
        elif t == "pathbox":
            deck.shape("RECTANGLE", b["box"], fill=TINT,
                       outline=(ACCENT if b.get("accent") else LINE, 0.01))
        elif t == "callout":
            deck.shape("RECTANGLE", b["box"], fill=NOWBG)

    # ---- images ----
    for b in blocks:
        if b["type"] != "image":
            continue
        if b.get("chrome"):
            # logos are dark on transparent; the CSS sits them on a white pill
            pad = 0.12
            deck.shape("RECTANGLE", {"x": b["box"]["x"] - pad, "y": b["box"]["y"] - pad,
                                     "w": b["box"]["w"] + 2 * pad, "h": b["box"]["h"] + 2 * pad},
                       fill=WHITE)
        deck.image(b["box"], b["src"])

    # ---- text ----
    for b in blocks:
        t = b["type"]
        if t in ("heading", "para", "caption", "callout", "chrome-text"):
            deck.text(b["box"], b.get("runs", []), b["style"],
                      align={"center": "CENTER", "right": "END"}.get(b["style"].get("align")))
        elif t == "metric":
            num_b = {**b["box"], "h": b["box"]["h"] * 0.62}
            lbl_b = {**b["box"], "y": b["box"]["y"] + b["box"]["h"] * 0.62,
                     "h": b["box"]["h"] * 0.38}
            if b.get("num"):
                deck.text(num_b, [{"t": b["num"], "b": True, "c": None}],
                          b.get("numStyle") or b["style"], align="CENTER")
            if b.get("lbl"):
                deck.text(lbl_b, [{"t": b["lbl"], "b": False, "c": None}],
                          b.get("lblStyle") or b["style"], align="CENTER")
        elif t in ("tnbox", "pathbox"):
            head = b.get("label") or b.get("title") or ""
            # use the measured boxes: these titles wrap, so a fixed offset collides
            hb = b.get("labelBox") or {**b["box"], "x": b["box"]["x"] + .12,
                                       "w": b["box"]["w"] - .24,
                                       "y": b["box"]["y"] + .10, "h": .5}
            if head:
                deck.text(hb, [{"t": head, "b": True, "c": None}],
                          b.get("labelStyle") or b["style"])
            items = b.get("items") or []
            if items:
                ib = b.get("itemsBox") or {**b["box"], "x": b["box"]["x"] + .12,
                                           "w": b["box"]["w"] - .24,
                                           "y": b["box"]["y"] + .62, "h": b["box"]["h"] - .72}
                deck.text(ib, [[{"t": it, "b": False, "c": None}] for it in items],
                          b.get("itemStyle") or b["style"], bullets=True)

    # bullets: one text box per run of them inside a card, so edits reflow
    for c in cards:
        runs, cur = [], []
        for b in blocks:
            if b["type"] != "bullet" or not in_card(b, c):
                continue
            if cur and b["box"]["y"] - (cur[-1]["box"]["y"] + cur[-1]["box"]["h"]) > 0.6:
                runs.append(cur); cur = []
            cur.append(b)
        if cur:
            runs.append(cur)
        for group in runs:
            x = min(g["box"]["x"] for g in group)
            y = min(g["box"]["y"] for g in group)
            w = max(g["box"]["x"] + g["box"]["w"] for g in group) - x
            h = max(g["box"]["y"] + g["box"]["h"] for g in group) - y
            deck.text({"x": x, "y": y, "w": w, "h": h},
                      [g.get("runs", []) for g in group], group[0]["style"], bullets=True)


def drive_meta(pid):
    r = subprocess.run(["gws", "drive", "files", "get", "--params",
                        json.dumps({"fileId": pid,
                                    "fields": "id,name,modifiedTime,version,"
                                              "lastModifyingUser(displayName)"}),
                        "--format", "json"], capture_output=True, text=True)
    return json.loads(r.stdout)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv
    name = args[0] if args else None

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import poster as P
    d = P.discover(name)[0]
    state_path = d / "slides.json"
    if not state_path.is_file():
        sys.exit(f"No {state_path.relative_to(P.ROOT)} -- create it with the "
                 f'deck id, e.g. {{"presentationId": "..."}}')
    state = json.loads(state_path.read_text())
    pid = state["presentationId"]

    meta = drive_meta(pid)
    seen, now = state.get("version"), meta.get("version")
    if seen and now and seen != now and not force:
        sys.exit(
            f"Refusing to overwrite: '{meta.get('name')}' is at Drive version "
            f"{now}, but {state_path.name} recorded {seen}.\n"
            f"Someone edited the deck since it was last generated "
            f"(last modified {meta.get('modifiedTime')} by "
            f"{meta.get('lastModifyingUser', {}).get('displayName', '?')}).\n"
            f"The HTML poster is authoritative, so regenerating DISCARDS those "
            f"edits.\nPort anything worth keeping back into "
            f"{(d / 'poster.html').relative_to(P.ROOT)} first, then re-run with "
            f"--force."
        )

    layout_path = P.ROOT / "build" / "slides" / "layout.json"
    if not layout_path.is_file():
        sys.exit(f"No {layout_path.relative_to(P.ROOT)} -- run "
                 f"'python3 scripts/extract_layout.py > {layout_path.relative_to(P.ROOT)}' first")
    layout = json.load(open(layout_path))

    pres = json.loads(subprocess.run(
        ["gws", "slides", "presentations", "get", "--params",
         json.dumps({"presentationId": pid}), "--format", "json"],
        capture_output=True, text=True).stdout)
    slide = pres["slides"][0]
    deck = Deck(pid, slide["objectId"])
    for el in slide.get("pageElements", []):
        deck.reqs.append({"deleteObject": {"objectId": el["objectId"]}})
    print("clearing", len(deck.reqs), "existing elements")
    deck.flush()
    build(deck, layout)
    print("sending", len(deck.reqs), "requests")
    deck.flush()

    after = drive_meta(pid)
    state["version"] = after.get("version")
    state["generatedAt"] = after.get("modifiedTime")
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(f"recorded Drive version {state['version']} in "
          f"{state_path.relative_to(P.ROOT)}")
    print(f"done -- https://docs.google.com/presentation/d/{pid}/edit")


if __name__ == "__main__":
    main()
