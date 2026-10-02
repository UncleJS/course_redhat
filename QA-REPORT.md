# QA Report — course_redhat
Generated: 2026-10-02 (post-remediation pass 2)

## Summary

Second deep-review pass after `d3e0c35`. Prior Critical/High remediations remain verified. This pass clears leftover High accuracy (XFS fstab `pass`) and objective-map honesty (process/chrony/IPv6), plus Medium nits and meta soften.

| Check | Scope | Result |
|---|---|---|
| Prior Critical remediations | Timers, modules, Jinja, reboot, license, hardlink, nav, student, gitignore, H3 slides | Still verified |
| XFS fstab `pass` / `fsck.xfs` | `03-rhcsa/03-filesystems-fstab.md` | Fixed — no-op stub wording |
| Objective map process / time / IPv6 | `98-reference/01-objective-map.md` | Fixed — Partial / Not covered honesty |
| LVM RO snapshot + merge lab | `04-lvm.md`, LVM grow lab | Fixed — `-pr` + deactivate caveat |
| chown / `--preserve-root` | `02-foundations/05-permissions.md` | Fixed |
| `apt-get` contrast | `04-rhce/01-automation-mindset.md` | Fixed → `dnf` |
| About EX294 URL | `00-preface/01-about.md` | Fixed (version-agnostic) |
| README overclaims | prerequisites / labs-every-step | Softened; Next-step vs TOC note |
| Slide decks | 74 ODP | Regenerate in this pass |

## Still open (content expansion — not blocking)

- Chapters still missing for exam shape: tar/gzip, `su`, scp/sftp, NFS, autofs, vfat depth, chrony.conf, `nice`/`kill` teaching
- Practice: multi-node RHCE lab; RHCA core/perf labs; more RHCSA firewall/SSH labs
- Chapter-level Prerequisites blocks / track badges still unused (README no longer promises them)

## How to re-verify

```bash
node tools/md_audit.js .
pip install -r requirements.txt
python3 slides/generate_slides.py
```

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
