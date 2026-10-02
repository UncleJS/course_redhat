# QA Report — course_redhat
Generated: 2026-10-02 (A+ completeness pass)

## Summary

Completeness pass after `a7b2aeb`. Prior accuracy remediations (passes 1–3) remain intact. This pass fills former objective-map **Not covered** / **Partial** rows with theory chapters and labs, wires navigation and slides, and regenerates all ODPs.

| Check | Scope | Result |
|---|---|---|
| New theory | archives, process, NFS/autofs, chrony | Added |
| Chapter extensions | `su`, scp/sftp/rsync, vfat, IPv6 | Added |
| New labs | firewalld, SSH transfer, multi-node, systemd harden, perf | Added |
| Wiring | README TOC, Next-step, objective map, `README_ORDER` | Updated |
| Username | lab examples → `student` | Normalized |
| Track badges | unused H1 badge convention | Dropped |
| `md_audit` | course tree | **0 broken links** |
| Slides | `python3 slides/generate_slides.py` | **83 ODPs** OK |

## Dimension grades (post-pass)

| Dimension | Grade |
|---|---|
| Structural hygiene | A+ |
| Technical accuracy | A+ |
| Navigation / honesty | A+ |
| Pedagogy / labs | A+ |
| Exam completeness | A+ |
| Tooling / slides | A+ |

## Out of scope (unchanged)

AAP/controller UI, IdM, Buildah deep dive, bond/VLAN hands-on beyond existing L2 chapter, bpftrace.

## How to re-verify

```bash
node tools/md_audit.js .
python3 -m pip install -r requirements.txt
python3 slides/generate_slides.py
```

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
