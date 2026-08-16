---
name: poster
description: Create or edit an academic conference poster using the JHU/AnVIL/Galaxy design system. Use when adding, restyling or restructuring poster content in this repository.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Academic poster design system

The poster is a single self-contained HTML file: all CSS inline in a `<style>`
block, no external stylesheets, images referenced from a relative `images/`
directory.

In this repository the poster already exists at `poster/poster.html` — edit it
in place. Read `docs/POSTER_NOTES.md` first for the decisions already made, and
`CLAUDE.md` for the content rules and the mandatory fit check.

To start a *new* poster: ask for the conference name, dates, location, authors
and affiliations (assume nothing), then copy the logos you need from
`.claude/skills/poster/assets/images/` into the poster's `images/` directory.
`.claude/skills/poster/assets/reference-poster.html` is a fully worked example —
read it when you need the exact implementation of an element, but do not copy
its content.

## Available logos

In `.claude/skills/poster/assets/images/`:

- `anvil_logo.png` — AnVIL (dark blue on transparent; needs a white pill on dark backgrounds)
- `galaxy_logo.png` — Galaxy Project, colour, for light backgrounds
- `galaxy_logo_white.png` — Galaxy Project, white, for dark backgrounds
- `jhu_logo_trimmed.png` — Johns Hopkins University
- `psu_logo.png` — Penn State University
- `freiburg_logo_trimmed.png` — University of Freiburg

Include only the university logos matching the authors' affiliations. Choose
the main logo — Galaxy Project or AnVIL — by the poster's subject, and take the
colour palette from that choice. Ask if the subject is ambiguous.

## Colour palette — AnVIL

```
Primary blue (header/footer bg, card borders, headings): #0C5294
Accent blue (links, conf text, highlights):              #4da6e8
Dark text:                                               #2c2c2c
Dark gray (secondary text, tool names):                  #4a4a4a
Warm gray (labels, captions):                            #6b6b6b
Page background:                                         #edf1f5
Card background:                                         white
Highlight text:                                          #0C5294
Tag background (blue-tinted):                            #e0ecf7
Tag text (blue-tinted):                                  #0a3d6e
Tag background (neutral):                                #e8e8e4
Diagram/workflow box background:                         #f0f4f8
Workflow box border:                                     #b0c4d8
Card heading border / table cell border:                 #c8d6e5
Table header background:                                 #0C5294
Table even row background:                               #f5f8fb
Compare box background / border / accent:                #f0f4f8 / #b0c4d8 / #4da6e8
Arch box — Galaxy:                                       #0C5294 bg, white text
Arch box — GCP:                                          #4da6e8 bg, white text
Arch box — Pulsar:                                       #6b6b6b bg, white text
Arch box — NFS/storage:                                  #e0ecf7 bg, #0a3d6e text, #0C5294 border
Step number circles:                                     #0C5294 bg, white text
Workflow arrows:                                         #0C5294
Header/footer border accent:                             #4da6e8
```

## Colour palette — Galaxy

```
Near-black (header/footer bg):      #2c2c2c
Gold accent (borders, highlights):  #c9b613
Dark gray (logo text, headings):    #4a4a4a
Warm gray (secondary text):         #6b6b6b
Page background:                    #f0f0ec
Card background:                    white
Highlight text:                     #a89a10
Tag background (gold-tinted):       #f5f3e0
Tag text (gold-tinted):             #5a5210
Tag background (neutral):           #e8e8e4
Workflow box background:            #faf8ec
Workflow box border:                #e0ddb0
Card bottom border:                 #e0ddd0
```

## Typography

Font stack: `'Helvetica Neue', Helvetica, Arial, sans-serif`.

Sizes below are for a 48in-wide poster. Scale them down for a narrower page —
this poster is 34in wide and dense, so it runs about 10% smaller throughout
(title 58pt, subtitle 27pt, authors 25pt, h2 31pt, h3 23pt, body 21pt,
tags/captions 17pt).

- Title: 66pt bold
- Subtitle: 30pt light, opacity 0.85
- Authors: 26pt medium
- Affiliations: 20–22pt, opacity 0.7
- Card headings (h2): 36pt
- Card body: 24pt, line-height 1.45
- Tags/badges: 20pt medium
- Footer: 22pt

## Page layout

- `@page { size: <W>in <H>in; margin: 0; }` — 48in × 36in landscape by default;
  this poster is 34in × 44in portrait.
- Body: CSS Grid, `grid-template-rows: auto 1fr auto` (header, content, footer).
- Content area: 3-column grid by default. Cards span columns with
  `grid-column: 1 / 3`, or run full width as a band.

## Header

Dark background, white text, 3-column grid: logo-left | centred title area |
conference details right. Accent bottom border (8px). Logo height ~1.5in, on a
white pill (`background: white; padding: 0.14in 0.26in; border-radius: 0.12in`)
when the logo is dark on transparent.

## Cards

White background, `border-radius: 0.12in`, accent top border (6px),
`box-shadow: 0 2px 8px rgba(0,0,0,0.06)`, padding 0.4in, heading with a bottom
border.

## Special elements

**Checkmark lists**

```css
.annotation-list { list-style: none; padding-left: 0; }
.annotation-list li { padding-left: 0.3in; position: relative; }
.annotation-list li::before {
  content: "\2713"; position: absolute; left: 0; font-weight: 700;
}
```

**Tags** — flexbox wrap, 0.08in gap, tinted or neutral background per palette.

**Workflow boxes** — tinted background with a border, numbered steps in 0.4in
round circles, accent-coloured arrows at 28pt bold.

**Architecture diagrams** — tinted background; box styles per palette above.

## Footer

Dark background, white text, accent top border. University logos on white pill
backgrounds. Use a `1fr auto 1fr` grid if a logo needs to be centred on the
*poster* rather than on the space left over.

## Before you finish

1. Run `python3 scripts/poster.py check`. The page height is fixed, so
   overflow is silently clipped rather than reported. This is mandatory.
2. Update `docs/POSTER_NOTES.md` with any decision worth remembering.
3. Do not commit generated files (`build/`, `poster/poster-flex.html`).
