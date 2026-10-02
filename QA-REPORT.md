# QA Report — course_redhat
Generated: 2026-10-02 (supersedes the 2026-06-10 report)

## Summary

Deep review + remediation pass (Oct 2026). June structural QA still holds; Critical/High accuracy, navigation, reference honesty, and tooling issues from that review are addressed in-repo.

| Check | Scope | Result |
|---|---|---|
| Technical accuracy (RHEL 10) | Critical/High from deep review | Fixed — timers, AppStream modules, Jinja render host, reboot detect, hardlink example, CVE `cves:` |
| License consistency | About + LICENSE + footers | Fixed — About is CC BY-NC-SA 4.0 |
| Next-step chains | RHCSA / RHCE / RHCA / 90-labs | Fixed — labs in chain; RHCA order matches README |
| Objective map honesty | Gaps marked **Not covered** | Updated |
| Ansible cheatsheet / glossary | Reference | Added |
| Username convention | Labs + Ansible | Normalized to `student` |
| `.gitignore` vs chapter names | `*secret*` / `*password*` | Narrowed |
| Slide H3 export | `generate_slides.py` | H2+H3 now become slides |
| Tooling docs | `requirements.txt`, `tools/README.md` | Added; audit scripts use `node` shebang |
| Broken intra-file anchors / TOC | Prior June audit | Still expected clean — re-run `node tools/md_audit.js .` |

## Fixed in this pass (2026-10-02)

### Accuracy / legal
- `03-rhcsa/07-scheduling.md` — `OnCalendar` defaults to **local** time; timezone as **suffix** or `Timezone=`
- `03-rhcsa/01-packages-dnf.md` — AppStream is a normal repo on RHEL 10; modularity removed
- `04-rhce/05-ansible-vars-templates.md` — Jinja rendered on **control node**
- `04-rhce/08-ansible-patching.md` — `needs-restarting -r`; CVE example uses `cves:`
- `00-preface/01-about.md` — CC BY-NC-SA 4.0; labs promise corrected
- `02-foundations/02-files-and-text.md` — hard links stay on one filesystem (avoid `/tmp`)

### Navigation
- RHCSA: chapter 14 → labs 01→02→03→04 → RHCE
- RHCE: playbooks → lab 01 → vars → roles → lab 02 → service deploy → patching → RHCA
- RHCA: SELinux lab → networking 01… → networking lab → containers → secrets lab → perf → 90-labs → objective map

### Reference / consistency
- Objective map marks tar/NFS/automount/scp/`su` gaps; adds Automation Mindset row
- Ansible section in cheatsheets; glossary: bond, idempotence, Jinja2, VLAN
- `student` username in Ansible + rootless examples; conventions updated

### Tooling
- `.gitignore` no longer matches `*secrets*` chapter paths
- Slides include H3 content; docstring matches flat `NNN-slug.odp` output
- `requirements.txt`, `tools/README.md`, Node shebang on audit scripts
- `AGENTS.md` rewritten for this repo (context-mode optional)

## How to re-verify

```bash
node tools/md_audit.js .                 # expect 0 broken / 0 missing TOC
pip install -r requirements.txt
python3 slides/generate_slides.py        # regenerates 74 ODP decks
```

## Still open (medium / coverage — not blocking)

- Content gaps: tar, `su`, scp/sftp, NFS/autofs, vfat, deeper chrony/IPv6, multi-node RHCE lab
- Slide decks truncate long sections; regenerate after large chapter edits
- Prefatory “prerequisites on every chapter” / track badges still not fully realized

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
