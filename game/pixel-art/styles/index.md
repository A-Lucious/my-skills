# Pixel Style Library

All styles share [COMMON.md](COMMON.md), while independently defining proportions, outlines, materials, default lighting, and fixed palettes.

| ID | Visual Direction | Specs & References |
|---|---|---|
| `parchment-fantasy` (Default) | Parchment dark fantasy, semi-realistic proportions, selective outlines, and material color blocking | [STYLE.md](parchment-fantasy/STYLE.md) · [palette.json](parchment-fantasy/palette.json) · [Reference Library](parchment-fantasy/reference-library/INDEX.md) |

To add a reusable style, invoke `$pixel-art create-style` and follow the [style creation interview](../commands/create-style.md). New style directories follow the Parchment Fantasy layout: `STYLE.md`, a locked `palette.json`, `PIXEL-SHADER.md`, `REFERENCE-STUDY.md`, and `reference-library/INDEX.md`, plus an independent `pixel_shader.py` for styles supporting 3D production. Legacy palette snapshots are needed only when that style has its own history.

Each library entry links its own documents and states any draft or unvalidated scope. New styles declare their relationship with COMMON and pass the palette check. Reference indexes record actual sources or explicitly state that none were supplied; discrepancies between references and written specifications remain alongside calibration records. Adding a style does not change the default.
