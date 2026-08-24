#!/usr/bin/env python3
"""Measure the rendered poster and emit a layout description as JSON.

DORMANT as of 2026-08-24: this exists to feed to_slides.py, and the Google
Slides copy is no longer maintained. Kept in case it is wanted again.

Slides has no layout engine -- every element is absolutely positioned -- so the
only way to reproduce the poster faithfully is to ask the browser where things
actually ended up and copy those coordinates.

Usage:  python3 scripts/extract_layout.py [poster] > layout.json
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import poster as P

JS = r"""
<script>
window.addEventListener('load', function () {
  var px2in = function (v) { return v / 96; };
  var out = { page: {}, blocks: [] };
  var b = document.body.getBoundingClientRect();
  out.page = { w: px2in(b.width), h: px2in(b.height) };

  function rect(el) {
    var r = el.getBoundingClientRect();
    return { x: px2in(r.left), y: px2in(r.top), w: px2in(r.width), h: px2in(r.height) };
  }
  function css(el) {
    var s = getComputedStyle(el);
    return {
      size: parseFloat(s.fontSize) * 0.75,          // px -> pt
      weight: parseInt(s.fontWeight, 10) || 400,
      color: s.color,
      align: s.textAlign,
      lh: parseFloat(s.lineHeight) / parseFloat(s.fontSize) || 1.3
    };
  }
  // runs: keep bold/colour spans so emphasis survives the trip
  function runs(el) {
    var out = [];
    (function walk(node, bold, color) {
      for (var i = 0; i < node.childNodes.length; i++) {
        var n = node.childNodes[i];
        if (n.nodeType === 3) {
          var t = n.textContent.replace(/\s+/g, ' ');
          if (t.trim()) out.push({ t: t, b: bold, c: color });
        } else if (n.nodeType === 1) {
          var s = getComputedStyle(n);
          walk(n, bold || parseInt(s.fontWeight, 10) >= 600,
                  s.color !== color ? s.color : color);
        }
      }
    })(el, css(el).weight >= 600, css(el).color);
    return out;
  }
  function push(type, el, extra) {
    var o = { type: type, box: rect(el), style: css(el) };
    for (var k in (extra || {})) o[k] = extra[k];
    out.blocks.push(o);
  }

  document.querySelectorAll('.card').forEach(function (card) {
    push('card', card, { band: card.classList.contains('band') });
    card.querySelectorAll(':scope > h2').forEach(function (h) {
      push('heading', h, { runs: runs(h) });
    });
    // everything that carries content, in document order
    card.querySelectorAll('p, li, .caption, .metric, .tn-box, img, .path-box, .callout, .tag')
        .forEach(function (el) {
      if (el.matches('.metric .num, .metric .lbl')) return;
      if (el.tagName === 'IMG') { push('image', el, { src: el.getAttribute('src') }); return; }
      if (el.classList.contains('metric')) {
        var n = el.querySelector('.num'), l = el.querySelector('.lbl');
        push('metric', el, {
          num: n ? n.textContent.trim() : '', numStyle: n ? css(n) : null,
          lbl: l ? l.textContent.trim() : '', lblStyle: l ? css(l) : null
        });
        return;
      }
      if (el.classList.contains('tn-box')) {
        var lab = el.querySelector('.tn-label');
        var li0 = el.querySelector('li');
        push('tnbox', el, {
          label: lab ? lab.textContent.trim() : '',
          labelStyle: lab ? css(lab) : null, labelBox: lab ? rect(lab) : null,
          itemStyle: li0 ? css(li0) : null,
          itemsBox: el.querySelector('ul') ? rect(el.querySelector('ul')) : null,
          items: Array.prototype.map.call(el.querySelectorAll('li'), function (li) {
            return li.textContent.trim(); }),
          now: el.classList.contains('now')
        });
        return;
      }
      if (el.classList.contains('path-box')) {
        var t = el.querySelector('.p-title');
        var pli = el.querySelector('li');
        push('pathbox', el, {
          title: t ? t.textContent.trim() : '',
          labelStyle: t ? css(t) : null, labelBox: t ? rect(t) : null,
          itemStyle: pli ? css(pli) : null,
          itemsBox: el.querySelector('ul') ? rect(el.querySelector('ul')) : null,
          items: Array.prototype.map.call(el.querySelectorAll('li'), function (li) {
            return li.textContent.trim(); }),
          accent: el.classList.contains('accent')
        });
        return;
      }
      if (el.closest('.tn-box, .path-box, .metric')) return;
      var kind = el.tagName === 'LI' ? 'bullet'
               : el.classList.contains('caption') ? 'caption'
               : el.classList.contains('tag') ? 'tag'
               : el.classList.contains('callout') ? 'callout' : 'para';
      push(kind, el, { runs: runs(el) });
    });
  });
  // header / footer live outside .content and have no .card wrapper
  ['.header', '.footer'].forEach(function (sel) {
    var region = document.querySelector(sel);
    if (!region) return;
    push(sel === '.header' ? 'header' : 'footer', region, {});
    region.querySelectorAll('img').forEach(function (im) {
      push('image', im, { src: im.getAttribute('src'), chrome: true });
    });
    region.querySelectorAll('h1, .subtitle, .authors, .affiliations, .conf, .conf-name, .conf-sub, .contact a, .ack')
      .forEach(function (el) {
        push('chrome-text', el, { runs: runs(el), cls: el.className || el.tagName.toLowerCase() });
      });
  });

  document.title = 'LAYOUT:' + encodeURIComponent(JSON.stringify(out));
});
</script>
"""

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else None
    d = P.discover(name)[0]
    src = (d / "poster.html").resolve()
    probe = src.with_name(".layout.html")
    probe.write_text(src.read_text(encoding="utf-8").replace("</body>", JS + "</body>", 1),
                     encoding="utf-8")
    try:
        def ready(p):
            m = re.search(r"LAYOUT:(\S+?)</title>", p.read_bytes().decode("utf-8", "replace"))
            return m.group(1) if m else None
        raw = P.run_chrome("--dump-dom", "--window-size=3264,4400", probe.as_uri(), ready=ready)
    finally:
        probe.unlink(missing_ok=True)
    from urllib.parse import unquote
    print(json.dumps(json.loads(unquote(raw)), indent=1))


if __name__ == "__main__":
    main()
