# Oblong Traders — Website

Single-page marketing site for **Oblong Traders Pvt. Ltd.**, positioning the company as an end-to-end partner across product development, manufacturing, global sourcing, export and strategic consulting.

It is a static site with no build step and no dependencies: just HTML, CSS and vanilla JS.

```
index.html          page markup (14 sections)
css/styles.css      design tokens + all styles (responsive, reduced-motion)
js/main.js          interactions (reveals, sticky lifecycle, capabilities, process, nav)
assets/logo.svg     logo (brand mark + wordmark)
assets/logo-mark.svg  brand mark only
assets/favicon.svg
assets/img/         placeholder material studies + world dot map
tools/generate_materials.py   regenerates the placeholder imagery (numpy + Pillow)
```

## Run locally

```bash
npx serve .        # or: python3 -m http.server 8080
```

## Before launch: replace the placeholders

| What | Where | Notes |
|---|---|---|
| **Photography** | `assets/img/*.jpg` | Procedurally generated *material studies* (leather, watch dial, ceramic, jewelry, metal, felt, packaging, steel, linen). Replace them with real product photography under the same filenames, ideally 1600×1200 or larger. |
| **Case studies** | `#work` section | Clearly labelled placeholders. No client names, figures or results have been invented. |
| **Contact details & socials** | Footer `#contact-details` | `[Email address]` is still a placeholder, and social links currently point to `#`. Phone and office address are filled in. |
| **Privacy / Terms** | Footer | Links point to `#`. |

The world map in the sourcing section is an **illustrative** dot map with abstract routes, and its caption says so. It does not mark any offices, factories or markets. If you later confirm specific markets, add them there.

## Design system (summary)

- **Colour:** Brand Orange `#F58220` (fills, lines, CTAs), `--orange-ink #DC6A0B` (large accent text on light), `--orange-text #B4560A` (small accent text on light, AA). Charcoal `#292929`, Graphite `#181818`, Warm White `#FAFAF8`, Soft Gray `#F2F2F0`. The palette stays mostly neutral, with orange as a restrained accent.
- **Type:** Plus Jakarta Sans for headlines and Inter for body text (Google Fonts), with system fallbacks. Headlines use weight 700 with tight negative tracking. Orange is reserved for single key phrases.
- **UI:** pill-shaped buttons (fully rounded), 2px radius elsewhere, 1px borders, numbered editorial rows instead of cards, and a fill-sweep hover on buttons.
- **Motion:** masked headline reveals, clip-path image reveals, a scroll-driven lifecycle line, a sticky process counter, subtle parallax and a page-load curtain. All of it is disabled under `prefers-reduced-motion`.
