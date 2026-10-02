# QA Report — course_redhat
Generated: 2026-10-02 (deep-review pass 3)

## Summary

Third deep-review pass after `f602dcc`. Prior remediations remain verified. This pass clears a new High accuracy cluster (recovery `/sysroot`, TuneD `profiles/` paths, invented Ansible `cves:`, L2 VLAN duplicate) plus Medium firewall/SELinux/permissions nits.

| Check | Scope | Result |
|---|---|---|
| Recovery emergency vs `/sysroot` | `05-rhca/perf/03-recovery-patterns.md` | Fixed |
| Root `xfs_repair` guidance | same | Fixed — rescue media; `-d` last resort |
| TuneD profile paths | `02-tuned.md`, cheatsheet | Fixed — `/…/tuned/profiles/` |
| Ansible `cves:` on `dnf` | `04-rhce/08-ansible-patching.md` | Fixed — `dnf update --cve` via command |
| L2 bond+VLAN+bridge | `04-l2-concepts.md` | Fixed — one VLAN conn + diagram |
| Sticky / fake boolean / `--direct` / rich priority / immediate / chcon MCS | various | Fixed |

## Still open (content expansion — not blocking)

- Chapters: tar/gzip, `su`, scp/sftp, NFS/autofs, chrony.conf, `kill`/`nice`
- Practice: multi-node RHCE lab; RHCSA firewall/SSH labs; RHCA core/perf labs

## How to re-verify

```bash
node tools/md_audit.js .
python3 -m pip install -r requirements.txt
python3 slides/generate_slides.py
```

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
