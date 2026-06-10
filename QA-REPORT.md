# QA Report — course_redhat
Generated: 2026-06-10 (supersedes the 2026-03-25 report)

## Summary

Full structural and technical review of all 74 markdown files (73 chapters + README) and the 74 generated ODP slide decks. All issues found in this pass have been **fixed**; the repo is clean as of this report.

| Check | Scope | Result |
|---|---|---|
| Technical accuracy (RHEL 10) | All tracks, spot-checked in depth | ✅ Clean — all 5 issues from the 2026-03-25 report verified fixed |
| Broken file links | All `[...](*.md)` links | ✅ 0 broken |
| Broken intra-file anchors | 2,069 `[...](#...)` links | ✅ 0 broken (220 fixed in this pass) |
| Per-file TOC completeness | All H2 headings vs TOC entries | ✅ Complete (157 entries added, incl. `Further reading` / `Next step` in every chapter) |
| TOC links injected inside code fences | All fenced blocks | ✅ 0 (13 injected `[↑ Back to TOC]` lines removed from 5 files) |
| Orphaned `[↑ Back to TOC]` lines before the H1 title | All files | ✅ 0 (409 junk lines removed from 70 files) |
| Unlabelled code fences | All opening fences | ✅ 0 (2 fixed: `00-preface/02-labs.md`, `README.md`) |
| Mermaid literal `\n` in node labels | All `mermaid` blocks | ✅ 0 |
| Deprecated Mermaid `graph TD` | All `mermaid` blocks | ✅ 0 (all `flowchart`) |
| Footers / copyright | All course files | ✅ Uniform `© 2026 UncleJS — CC BY-NC-SA 4.0` |
| TODO / FIXME / placeholder markers | All files | ✅ 0 |
| Git hygiene (junk files, pycache, secrets) | Tracked files | ✅ Clean; `.gitignore` comprehensive |
| Slide decks freshness | 74 ODP decks | ✅ Regenerated 2026-06-10 from current chapter content |

## What was fixed in this pass (2026-06-10)

### 1. TOC tooling artifacts (worst finding)
The earlier automated TOC pass did not skip code fences or the pre-title region. Three symptom classes, all fixed:

- **Orphaned `[↑ Back to TOC](#toc)` lines before the H1** in 70 files (1–10 per file, 409 lines total) — rendered as dead-link junk above every chapter title.
- **`[↑ Back to TOC](#toc)` lines injected *inside* code fences** in 5 files: the lab/runbook template blocks in `00-preface/02-labs.md` and `05-rhca/perf/03-recovery-patterns.md`, and `virsh` output blocks in `90-labs/02-single-vm.md` (×2) and `90-labs/03-multi-vm.md` (the tool mistook command-output dashed separators for thematic breaks).
- **TOC entries pointing at headings that only exist inside code fences** (`Prerequisites`, `Estimated time`, `Recovery - <Scenario Name>`, `Steps`, `Post-recovery`, `Escalation`, …) — removed.

### 2. Broken intra-file anchors — 220 links across ~60 files
The TOC generator used a slugger that diverges from GitHub's: it collapsed the double hyphen GitHub produces for ` — ` (space-em-dash-space), parentheses, and quotes, and it stripped underscores. Every anchor was re-validated against the real GitHub slugging rules (lowercase; remove anything that is not a letter, number, space, hyphen, or underscore; spaces → hyphens; duplicates suffixed `-1`, `-2`). Examples fixed:

- `#pattern-8-disk-full-recovery` → `#pattern-8--disk-full-recovery`
- `#the-help-flag` → `#the---help-flag` (backticked `--help` in heading)
- `#pipes` → `#pipes--` (heading `Pipes — \`|\``)
- `#sshdconfig-drop-in-files` → `#sshd_config-drop-in-files` (underscores are kept by GitHub)

### 3. Missing TOC entries — 157 added across 72 files
Every chapter's `## Further reading` and `## Next step` are now in its TOC, plus other unlisted H2s (worked examples, lab steps, `Why This Matters in Production`, cheatsheet sections, …), inserted in document order.

### 4. Minor
- `README.md` track diagram and the `00-preface/02-labs.md` lab template fence now carry language tags (`text` / `markdown`).
- `05-rhca/networking/02-routing-method.md`: diagnostic hint now says "check firewalld (nftables backend)" instead of "iptables/firewalld".

### 5. Slides regenerated
All 74 ODP decks rebuilt with `python3 slides/generate_slides.py` from the post-fix chapter content (previous decks predated the 2×–3× chapter expansion). Total deck size 456K → 556K.

## Verified clean (no action needed)

- **Technical accuracy:** RHEL 10-native throughout — `dnf` (no `yum` in scenario text), firewalld-on-nftables, Quadlet as the container/systemd integration path with `podman generate systemd` explicitly marked removed in Podman 5.x, `pasta` rootless networking, `crun` runtime, `ansible-core` packaging, correct XFS cannot-shrink warnings with safe `lvreduce` ordering, sound SELinux workflow (`setenforce 0` and blind `audit2allow` explicitly discouraged), correct exam codes (EX200/EX294) with change disclaimer.
- **Corrections to earlier review claims** (so stale numbers don't resurface): the March report's "82 unlabelled code fences" and a later recount of "1155" both miscounted — closing fences were included; the true count was 2 opening fences, now 0. The "`<Scenario Name>` placeholder" flagged earlier is an intentional copy-paste runbook template inside a code fence, not unfinished authoring.

## How to re-verify

- Anchors + TOC completeness: `bun tools/md_audit.js .` — fence-aware GitHub-slugger audit over all `[...](#...)` links and H2 headings. Expected: 0 broken, 0 missing. Auto-fix with `bun tools/md_fix.js . --write`.
- Fence hygiene: `awk` scan for unlabelled opening fences and for `Back to TOC` lines inside fences or before the H1. Expected: 0 / 0 / 0.
- Slides: `python3 slides/generate_slides.py` regenerates 74 decks; the script removes stale decks itself.

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
