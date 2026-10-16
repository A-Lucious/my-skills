# Reusable Asset Source Index

**English** | [简体中文](README.zh-CN.md)

[Source URL index](INDEX.md) · [Source and license records](THIRD_PARTY_LICENSES.md) · [Machine-readable index](index.json)

This directory records 9 sources across styles. It stores links, authors, licenses and known upstream file hashes. Asset files, archives and preview images are obtained only when needed.

Browse previews on the publisher's website and confirm the selected file's current license. Download only selected files and notices into the target project's `Test Workspace/asset-cache/`. Before downloading, prune disposable files as needed to keep the shared cache within **50 MiB**. This is a workflow budget, not an automatic download or cleanup service. If only an archive is available, check its size against the budget, extract the selected files, and immediately remove the archive and unused contents. Use an individual-file source when a pack exceeds the budget.

Place working copies and provenance in `Test Workspace/<task-id>/references/`. Adapt assets through Aseprite MCP. After delivery, remove disposable cache and unused references; retain adopted files, required attribution and final outputs. Downloads and previews must stay outside this index directory and Git history. Do not crawl full catalogues automatically.

Most listed packs use CC0; Game-icons primarily uses CC BY 3.0 with some CC0 icons. Preserve the selected icon's author credit, source and license link, and identify modifications. Verify per-file licensing before use; see the [license records](THIRD_PARTY_LICENSES.md).
