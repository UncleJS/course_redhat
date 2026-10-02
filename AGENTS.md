# Agent notes — course_redhat

This is a **markdown-only** RHEL 10 training repo (chapters, labs, reference, ODP slides). Prefer small, accurate content edits over drive-by rewrites.

## Tooling

- Audit anchors/TOCs: `node tools/md_audit.js .` (see [tools/README.md](tools/README.md))
- Regenerate slides: `pip install -r requirements.txt && python3 slides/generate_slides.py`
- Lab VM username in examples: **`student`** (see [90-labs/01-index.md](90-labs/01-index.md))

## Context-mode MCP (optional)

If the **context-mode** MCP server is installed and connected in this session, prefer its sandbox tools (`ctx_batch_execute`, `ctx_execute`, `ctx_fetch_and_index`, `ctx_search`) for large command output and web fetches so the context window is not flooded.

If those tools are **not** available, use normal Shell / Grep / Read / WebFetch. Do not fail the task waiting for context-mode.

## Content conventions

- Keep chapter chrome: badges, `#toc`, TOC, Further reading, Next step, CC BY-NC-SA footer
- Prefer `sudo` over interactive root shells in examples
- RHEL 10: no DNF module streams; Quadlet for containers; `needs-restarting -r` for reboot detection
- Do not invent exam coverage — align [98-reference/01-objective-map.md](98-reference/01-objective-map.md) with what chapters actually teach
