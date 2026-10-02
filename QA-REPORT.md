# QA Report — course_redhat
Generated: 2026-10-02 (A+ honesty pass)

## Summary

Honesty pass after `7555a13`. Completeness wiring from the prior pass remains intact. This pass corrects High RHEL-10 accuracy bugs introduced or left in new material, closes Partial skills, places core RHCSA howtos on the RHCSA track, and fixes map/username/lab honesty so claimed grades match the tree.

| Check | Scope | Result |
|---|---|---|
| autofs `/misc` duplication | `03-rhcsa/16-nfs-automount.md` | Fixed — `/shares` + `auto.shares`; hard mounts |
| `ipv6.method ignore` as disable | `03-rhcsa/09-networkmanager-nmcli.md` | Fixed — `disabled` + ignore vs disabled note |
| sshd `Match` drop-in footgun | `03-rhcsa/12-ssh.md` | Fixed — Include-at-top, `Match all`, first-wins |
| chrony timesyncd / `-a` | `03-rhcsa/17-time-chrony.md` | Fixed |
| sudo `-i` vs `su -` rationale | `01-getting-started/03-sudo-updates.md` | Fixed |
| firewalld `immediate` | labs/05 | Fixed |
| archives zip / SELinux extract | `02-foundations/07-archives.md` | Fixed |
| ext4 + groupmod/del | fstab / permissions | Fixed |
| RHCSA-track howtos | systemd, journald, map dual links | Fixed |
| Map honesty | patching lab, SSH keys lab, not-covered footer | Fixed |
| Username / Track / Multi-VM IP | student; RHCA; `192.168.100.x` | Fixed |
| Thin labs | +verify / limit / runtime test / tuned restore | Thickened |
| `md_audit` | course tree | **0 broken / 0 missing TOC** |
| Slides | regenerate | **83 ODPs** OK |

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

Kickstart, Stratis, VDO, Cockpit UI, AAP/controller UI, IdM, Buildah deep dive, bpftrace, full NFS server Multi-VM lab — listed on the objective map footer.

## How to re-verify

```bash
node tools/md_audit.js .
python3 -m pip install -r requirements.txt
python3 slides/generate_slides.py
```

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
