# Presentation tools

How the slide deck `IronPass-Presentation.pptx` in the repo root is built.

1. `assets.mjs` makes the pictures: backgrounds, icon tiles (Lucide and Simple Icons), framed screenshots (from `shots.json`) and the diagrams. It needs Playwright, `lucide-static` and `simple-icons` from npm.
2. `build_deck.py` places the pictures and the text with python-pptx. Only text boxes, plain shapes, pictures and one table are used, so the file opens in Google Slides.

```bash
node assets.mjs <repo-root> <build-dir>
python build_deck.py <build-dir> IronPass-Presentation.pptx "90+" "3m 37s"
```

Fonts (all from Google Fonts): Unbounded for titles, DM Sans for text, JetBrains Mono for code.
