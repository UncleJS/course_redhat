# QA Report — course_redhat
Generated: 2026-03-25

## Summary

| Check | Files checked | Issues found |
|---|---|---|
| Technical accuracy | 73 | 5 |
| Broken links (file) | 73 | 0 |
| Broken anchors | 73 | 8 |
| Missing TOC entries (systemic) | 73 | All 73 files missing `## Further reading` + `## Next step` |
| Missing TOC entries (substantive) | 73 | 8 unique headings not in TOC |
| Code fence language tags | 73 | 82 unlabelled fences across 36 files |
| Mermaid `\n` in node labels | 73 | 165 occurrences across 25 files |
| Mermaid `graph TD` (deprecated) | 73 | 0 (all use `flowchart TD/LR`) |

---

## Issues by file

### 00-preface/01-about.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic — see [Recommended Fixes](#recommended-fixes))
- `## Next step` not in TOC (systemic)

---

### 00-preface/02-labs.md
#### Code fences
- Line 112: unlabelled code fence (content is plaintext — add `` ```text ``)

#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Cleanup` not in TOC
- `## Common failures` not in TOC
- `## Why this matters in production` not in TOC
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 00-preface/03-conventions.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 01-getting-started/01-vm-install.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 01-getting-started/02-first-boot.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 01-getting-started/03-sudo-updates.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 01-getting-started/04-help-system.md
#### Broken anchors
- Line 17: `[The \`--help\` flag](#the-help-flag)` — anchor `#the-help-flag` does not match. GitHub strips backticks from heading anchors: `## The \`--help\` flag` → `#the---help-flag` (three dashes). TOC link must be `#the---help-flag`.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/01-shell-basics.md
#### Code fences
- Line 40: unlabelled code fence (prompt example — add `` ```text ``)
- Line 112: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 218–229: 12 node labels contain literal `\n` sequences inside quoted strings (e.g., `"/etc\nconfig files"`). In most Mermaid renderers these render as the two characters `\n`, not a newline. Use `<br/>` for line breaks or separate the description into the next line.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/02-files-and-text.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/03-pipes-redirection.md
#### Mermaid
- Lines 132–136: 5 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/04-editors.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/05-permissions.md
#### Technical accuracy
- Line 222: `sudo usermod -aG developers,docker,wheel rhel` — the `docker` group does not exist on a default RHEL 10 installation (Docker is not in RHEL repos). This example should use a realistic group like `podman` or simply `wheel,developers`. Using `docker` as an example group teaches incorrect assumptions.

#### Broken anchors
- Line 27: `[Viewing permissions — \`ls -l\`](#viewing-permissions-ls-l)` — anchor mismatch. The actual heading `## Viewing permissions — \`ls -l\`` generates `#viewing-permissions---ls--l` (em-dash = triple-dash, backtick stripped, space-to-dash). Correct the TOC link.

#### Code fences
- Line 43: unlabelled code fence (add `` ```text ``)
- Line 105: unlabelled code fence (add `` ```text ``)
- Line 322: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 76–81: 4 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Viewing permissions — \`ls -l\`` not in TOC (substantive — same heading that has the broken anchor)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/06-acls.md
#### Code fences
- Line 112: unlabelled code fence (add `` ```text ``)
- Line 123: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 02-foundations/labs/01-shared-team-dir.md
#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Background` not in TOC
- `## Cleanup` not in TOC
- `## Common failures` not in TOC
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/01-packages-dnf.md
#### Technical accuracy
- Lines 280, 312, 408, 417: References to `/etc/yum.repos.d/` — **this path is correct** on RHEL 10 (DNF retains yum.repos.d for compatibility), but the prose should clarify that `dnf` reads this directory; no change needed unless the course aims to retire all yum terminology.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/02-storage-overview.md
#### Code fences
- Line 57: unlabelled code fence (add `` ```text ``)
- Line 110: unlabelled code fence (add `` ```text ``)
- Line 310: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 78–87: 8 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/03-filesystems-fstab.md
#### Code fences
- Line 117: unlabelled code fence (add `` ```text ``)
- Line 145: unlabelled code fence (add `` ```ini `` or `` ```text ``)

#### Mermaid
- Lines 176–181: 6 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/04-lvm.md
#### Code fences
- Line 57: unlabelled code fence (add `` ```text ``)
- Line 197: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 85–95: 11 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/05-systemd-basics.md
#### Mermaid
- Line 83: node label `BOOT` contains literal `\n`. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/06-logging-journald.md
#### Mermaid
- Lines 85–91: 7 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/07-scheduling.md
#### Code fences
- Line 184: unlabelled code fence (add `` ```text `` — crontab format)
- Line 200: unlabelled code fence (add `` ```text ``)
- Line 248: unlabelled code fence (add `` ```text ``)
- Line 288: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/08-networking-basics.md
#### Technical accuracy
- Line 19: `ifconfig` / `route` / `arp` toolset — correctly described as legacy, no issue. The prose explicitly states `ip` is the modern replacement.

#### Broken anchors
- Line 41: `[Output columns (ss -tlnp)](#output-columns-ss-tlnp)` — the actual heading is `### Output columns (ss -tlnp)` which generates `#output-columns-ss--tlnp` (parentheses stripped, double dash). Correct the TOC link.

#### Code fences
- Line 341: unlabelled code fence (add `` ```text ``)
- Line 383: unlabelled code fence (add `` ```text ``)
- Line 425: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/09-networkmanager-nmcli.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/10-dns-resolution.md
#### Technical accuracy
- Line 322: `` `yum update` fails with "Could not resolve host" `` — in a RHEL 10 course scenario text, `yum update` should be `dnf update`. Readers seeing `yum` in a scenario may conclude it is acceptable to use on RHEL 10.

#### Code fences
- Line 102: unlabelled code fence (add `` ```text ``)
- Line 141: unlabelled code fence (add `` ```text ``)
- Line 271: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 72–76: 5 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/11-firewalld.md
#### Technical accuracy
- Line 429 (in `05-rhca/networking/02-routing-method.md`): `# Timeout → firewall dropping → check iptables/firewalld` — the `iptables` reference is misleading on RHEL 10 where `nftables`/`firewalld` is the default. Should read `nftables/firewalld` or just `firewalld`.
  *(Note: this issue is in routing-method.md — see that section below.)*

#### Broken anchors
- Line 55: `[Firewalld runtime vs permanent — synchronisation](#firewalld-runtime-vs-permanent--synchronisation)` — anchor mismatch. The em-dash heading generates a different anchor. GitHub renders `—` as triple-dash `---`. The actual anchor is `#firewalld-runtime-vs-permanent-synchronisation` (single dash, not double). Verify and fix.

#### Missing TOC entries
- `## Firewalld runtime vs permanent — synchronisation` not in TOC anchor (substantive — linked in TOC but anchor is wrong)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/12-ssh.md
#### Code fences
- Lines 164, 185, 243, 293, 435, 468, 488: 7 unlabelled code fences. These appear to be SSH config file snippets — add `` ```text `` or `` ```ini ``.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/13-selinux-fundamentals.md
#### Broken anchors
- Line 50: `[semanage — persistent policy management](#semanage--persistent-policy-management)` — the em-dash heading `## semanage — persistent policy management` generates anchor `#semanage-persistent-policy-management` (single dash for em-dash). The double-dash in the TOC link is wrong.

#### Code fences
- Line 136: unlabelled code fence (add `` ```text ``)
- Line 162: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 74–78: 5 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## semanage — persistent policy management` anchor mismatch in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/14-selinux-avc-basics.md
#### Code fences
- Lines 80, 186, 434, 446, 457, 469, 480: 7 unlabelled code fences. AVC denial log output — add `` ```text ``.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/labs/01-static-ip-dns.md
#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/labs/02-systemd-service.md
#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/labs/03-lvm-xfs-grow.md
#### Code fences
- Line 82: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 03-rhcsa/labs/04-selinux-label-fix.md
#### Missing TOC entries
- `## Prerequisites` not in TOC
- `## Success criteria` not in TOC
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 04-rhce/01-automation-mindset.md
#### Technical accuracy
- Line 186: `` `yum install -y httpd mod_ssl` `` appears inside a code block labelled as an "old SOP" example. While contextually presented as legacy, a RHEL 10 course should use `dnf install -y httpd mod_ssl`. Readers skimming may copy this command.

#### Broken anchors
- Line 48: `[The "set -euo pipefail" habit for Bash](#the-set-euo-pipefail-habit-for-bash)` — the heading `## The "set -euo pipefail" habit for Bash` generates anchor `#the-set--euo-pipefail-habit-for-bash` (quotes stripped; the dashes before `euo` become double-dashes). Verify anchor generation.

#### Code fences
- Line 159: unlabelled code fence (automation workflow diagram — add `` ```text ``)
- Line 185: unlabelled code fence (SOP list — add `` ```text ``)

#### Missing TOC entries
- `## The "set -euo pipefail" habit for Bash` anchor mismatch in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/02-bash-fundamentals.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/03-ansible-setup-inventory.md
#### Code fences
- Line 51: unlabelled code fence (add `` ```ini `` — inventory file format)

#### Mermaid
- Lines 79–86: 8 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/04-ansible-playbooks.md
#### Code fences
- Line 449: unlabelled code fence (add `` ```yaml ``)

#### Mermaid
- Lines 77–91: 9 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/05-ansible-vars-templates.md
#### Code fences
- Line 106: unlabelled code fence (add `` ```text ``)
- Line 141: unlabelled code fence (add `` ```text ``)
- Line 221: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 165–170: 2 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/06-ansible-roles.md
#### Code fences
- Line 54: unlabelled code fence (add `` ```text `` or `` ```yaml ``)

#### Mermaid
- Lines 85–91: 7 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/07-ansible-service-deploy.md
#### Code fences
- Line 51: unlabelled code fence (add `` ```yaml ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/08-ansible-patching.md
#### Code fences
- Line 52: unlabelled code fence (add `` ```yaml ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 04-rhce/labs/01-first-playbook.md
#### Missing TOC entries
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 04-rhce/labs/02-role-web-deploy.md
#### Missing TOC entries
- `## Why this matters in production` not in TOC
- `## Next step` not in TOC (systemic)

---

### 05-rhca/01-troubleshooting-playbook.md
#### Code fences
- Line 233: unlabelled code fence (add `` ```text `` — decision tree)

#### Mermaid
- Lines 69–82: 14 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/02-systemd-advanced.md
#### Code fences
- Line 200: unlabelled code fence (add `` ```ini `` or `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/03-systemd-hardening.md
#### Mermaid
- Lines 82–96: 9 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/04-journald-retention.md
#### Code fences
- Line 309: unlabelled code fence (add `` ```ini ``)
- Line 324: unlabelled code fence (add `` ```ini ``)
- Line 455: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/01-podman-fundamentals.md
#### Technical accuracy
- Line 107: `systemd integration | Native (\`podman generate systemd\`)` — `podman generate systemd` was **deprecated in Podman v4.4** and is removed in recent upstream versions. On RHEL 10 / Podman 5.x, the preferred method is **Quadlet** (`.container` unit files). The table should note it as deprecated and point to Quadlet. The file does explain Quadlet elsewhere, but the comparison table presents `podman generate systemd` as the current approach.

#### Mermaid
- Lines 77–83: 4 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/02-rootless.md
#### Mermaid
- Lines 87–91: 5 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/03-volumes.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/04-secrets.md
#### Code fences
- Line 62: unlabelled code fence (add `` ```text ``)
- Line 131: unlabelled code fence (add `` ```text ``)
- Line 183: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/05-systemd-integration.md
#### Technical accuracy
- Line 107 (table): `podman generate systemd` listed as an approach with "Migrating existing containers" use case. The file correctly notes on line 258 that it is deprecated upstream. The table on line 59 should add a deprecation flag (⚠️) to the `podman generate systemd` row.
- Lines 244–258: The section `## Approach 2: podman generate systemd` demonstrates the deprecated command `podman generate systemd --new --name myapp > myapp.service`. This is removed in Podman 5+ (RHEL 10 ships Podman 5.x). This section could mislead students if they attempt it on RHEL 10.

#### Mermaid
- Lines 70–74: 4 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/06-selinux-containers.md
#### Code fences
- Line 217: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/labs/01-rootless-web.md
#### Missing TOC entries
- `## Common Failures` not in TOC (substantive)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/containers/labs/02-secrets-rotate.md
#### Missing TOC entries
- `## Cleanup` not in TOC (substantive)
- `## Common Failures` not in TOC (substantive)
- `## Why This Matters in Production` not in TOC (substantive)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/networking/01-nmcli-profiles.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/networking/02-routing-method.md
#### Technical accuracy
- Line 429: Comment `# Timeout → firewall dropping → check iptables/firewalld` — `iptables` is not the correct tool on RHEL 10. Should be `# check nftables/firewalld` or just `firewall-cmd`.

#### Mermaid
- Lines 87–93: 7 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/networking/03-tcpdump.md
#### Code fences
- Line 337: unlabelled code fence (add `` ```text ``)
- Line 343: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 70–75: 5 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/networking/04-l2-concepts.md
#### Code fences
- Line 233: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/networking/labs/01-debug-triad.md
#### Broken anchors
- Lines 37–45: TOC links `#introduce-the-fault-1`, `#observe-the-symptom-1`, `#troubleshoot-it-1`, `#fix-it-1`, `#introduce-the-fault-2`, `#observe-the-symptom-2`, `#troubleshoot-it-2`, `#fix-it-2` — these numbered suffixes are used to disambiguate repeated heading names (Fault 2 and Fault 3 both use the same sub-heading titles). GitHub Markdown **does** generate numbered suffixes for duplicate headings, but the count depends on the order of occurrence. The file has three sets of `### Introduce the fault / Observe the symptom / Troubleshoot it / Fix it`. Count: Fault 1 = `-1` suffix is **skipped** (first occurrence has no suffix), Fault 2 = `-1`, Fault 3 = `-2`. The current TOC uses `-1` and `-2` which matches Fault 2 and Fault 3 respectively, but the anchors for Fault 2 and 3 should be double-checked against the actual GitHub render. The exact suffix generation depends on renderer version — consider renaming the sub-headings to be unique (e.g., `### Fault 2 — Introduce the fault`).

#### Missing TOC entries
- `## Common failures` not in TOC (substantive)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/perf/01-resource-triage.md
#### Code fences
- Line 97: unlabelled code fence (add `` ```text ``)
- Line 479: unlabelled code fence (add `` ```text ``)
- Line 556: unlabelled code fence (add `` ```text ``)

#### Mermaid
- Lines 77–87: 11 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/perf/02-tuned.md
#### Code fences
- Line 71: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Why This Matters in Production` not in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/perf/03-recovery-patterns.md
#### Code fences
- Line 92: unlabelled code fence (add `` ```text ``)
- Line 164: unlabelled code fence (add `` ```text ``)

#### Broken anchors
- Line 71: `[Recovery - <Scenario Name>](#recovery-scenario-name)` — this is a **template placeholder section**. The heading `## Recovery - <Scenario Name>` contains angle brackets which are stripped in anchor generation. Confirm this is intentional placeholder content or remove it before release.

#### Missing TOC entries
- `## Recovery - <Scenario Name>` not in TOC (template placeholder — substantive)
- `## Why This Matters in Production` not in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/selinux/01-fix-taxonomy.md
#### Code fences
- Line 53: unlabelled code fence (add `` ```text ``)
- Line 247: unlabelled code fence (add `` ```text ``)
- Line 318: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/selinux/02-semanage.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/selinux/03-audit-workflow.md
#### Code fences
- Lines 123, 184, 267, 300, 397: 5 unlabelled code fences (AVC denial output — add `` ```text ``)

#### Mermaid
- Lines 319–333: 14 node labels contain literal `\n` sequences. Use `<br/>` for line breaks.

#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 05-rhca/selinux/labs/01-nondefault-port.md
#### Code fences
- Line 103: unlabelled code fence (add `` ```text ``)
- Line 139: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Why this matters in production` not in TOC (substantive)
- `## Next step` not in TOC (systemic)

---

### 90-labs/01-index.md
#### Missing TOC entries
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 90-labs/02-single-vm.md
#### Missing TOC entries
- `## Prerequisites` not in TOC (substantive)
- `## Success Criteria` not in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 90-labs/03-multi-vm.md
#### Code fences
- Line 21: unlabelled code fence (add `` ```text ``)

#### Missing TOC entries
- `## Prerequisites` not in TOC (substantive)
- `## Success Criteria` not in TOC (substantive)
- `## Further reading` not in TOC (systemic)
- `## Next step` not in TOC (systemic)

---

### 98-reference/01-objective-map.md
#### Missing TOC entries
- `## Next step` not in TOC (systemic)

---

### 98-reference/02-glossary.md
#### Missing TOC entries
- `## Next step` not in TOC (systemic)

---

### 98-reference/03-cheatsheets.md
#### Missing TOC entries
- `## Next step` not in TOC (systemic)

---

### 98-reference/04-further-reading.md
#### Missing TOC entries
- `## Next step` not in TOC (systemic)

---

## Recommended fixes

The following 10 issues are ranked by technical severity (wrong information or broken navigation).

### Fix 1 — `podman generate systemd` presented as current approach
**Files:** `05-rhca/containers/01-podman-fundamentals.md` (line 107), `05-rhca/containers/05-systemd-integration.md` (lines 59, 238–258)  
**Severity:** 🔴 High — Technically wrong for RHEL 10. `podman generate systemd` is deprecated in Podman v4.4 and removed in Podman 5.x (shipped with RHEL 10). Students who run the command will get an error.  
**Fix:** Update the comparison table to mark this row as ⚠️ deprecated. Replace the `## Approach 2` section with a note that the command no longer exists on RHEL 10 and redirect to Quadlet.

### Fix 2 — `yum` used in scenario text and SOP example
**Files:** `03-rhcsa/10-dns-resolution.md` (line 322), `04-rhce/01-automation-mindset.md` (line 186)  
**Severity:** 🔴 High — Using `yum` in a RHEL 10 course teaches incorrect tooling. `yum` is an alias/wrapper on RHEL 10 but students should form correct habits.  
**Fix:** Replace `` `yum update` `` → `` `dnf update` `` and `yum install -y httpd mod_ssl` → `dnf install -y httpd mod_ssl`.

### Fix 3 — `docker` group in usermod example
**File:** `02-foundations/05-permissions.md` (line 222)  
**Severity:** 🔴 High — The `docker` group does not exist on a default RHEL 10 system (Docker is unsupported/absent). Adding a non-existent group will cause `usermod` to fail with an error.  
**Fix:** Replace `developers,docker,wheel` with a realistic group set such as `developers,wheel` or `developers,podman,wheel`.

### Fix 4 — 8 broken in-page anchor links
**Files:** Multiple (see detail above)  
**Severity:** 🟠 Medium-High — TOC links that silently fail to navigate frustrate learners using web-rendered Markdown (GitHub, MkDocs, Obsidian).  
**Fix summary:**
- `04-help-system.md:17` → change `#the-help-flag` to `#the---help-flag`
- `05-permissions.md:27` → change `#viewing-permissions-ls-l` to `#viewing-permissions---ls--l`
- `08-networking-basics.md:41` → change `#output-columns-ss-tlnp` to `#output-columns-ss--tlnp`
- `11-firewalld.md:55` → verify anchor for em-dash heading (likely `#firewalld-runtime-vs-permanent-synchronisation`)
- `13-selinux-fundamentals.md:50` → change `#semanage--persistent-policy-management` to `#semanage-persistent-policy-management`
- `01-automation-mindset.md:48` → verify anchor for heading with quotes
- `01-debug-triad.md:37–45` → rename duplicate sub-headings to be unique (e.g., `### Fault 2 — Introduce the fault`)
- `03-recovery-patterns.md:71` → remove or complete template placeholder section `## Recovery - <Scenario Name>`

### Fix 5 — `iptables` reference in routing chapter
**File:** `05-rhca/networking/02-routing-method.md` (line 429)  
**Severity:** 🟠 Medium — On RHEL 10, `iptables` is not the default firewall tool. Telling students to "check iptables" is misleading.  
**Fix:** Change comment to `# check nftables/firewalld` or `# firewall-cmd --list-all`.

### Fix 6 — 82 unlabelled code fences across 36 files
**Files:** 36 files (worst offenders: `03-rhcsa/12-ssh.md`, `03-rhcsa/14-selinux-avc-basics.md` — 7 each)  
**Severity:** 🟠 Medium — Unlabelled fences lose syntax highlighting, reduce readability, and fail linters. The most common missing tags are `` ```text `` (for plaintext/log output) and `` ```ini `` (for config file snippets).  
**Fix:** Add appropriate language tags. For log/terminal output use `` ```text ``; for config files use `` ```ini `` or `` ```conf ``; for YAML output use `` ```yaml ``.

### Fix 7 — 165 `\n` literals in Mermaid node labels across 25 files
**Files:** 25 files (worst offenders: `05-rhca/selinux/03-audit-workflow.md`, `05-rhca/01-troubleshooting-playbook.md` — 14 each)  
**Severity:** 🟠 Medium — In Mermaid, `\n` inside node labels renders as the two characters `\` and `n`, not as a newline. The diagrams display multi-word descriptions compressed into unreadable text.  
**Fix:** Replace `\n` with `<br/>` inside Mermaid node labels (e.g., `A["line one<br/>line two"]`).

### Fix 8 — Template placeholder section left in `03-recovery-patterns.md`
**File:** `05-rhca/perf/03-recovery-patterns.md` (line 554)  
**Severity:** 🟠 Medium — `## Recovery - <Scenario Name>` is clearly an authoring template that was never completed. The TOC links to `#recovery-scenario-name` which resolves incorrectly.  
**Fix:** Either complete the section with a real scenario (e.g., OOM kill recovery, disk full recovery) or remove it and the corresponding TOC link before publication.

### Fix 9 — Systemic: `## Further reading` and `## Next step` missing from all TOCs
**Files:** All 73 concept/chapter files  
**Severity:** 🟡 Low-Medium — Every file ends with `## Further reading` and `## Next step` sections but these are absent from every file's `## Table of contents`. Readers cannot jump directly to these sections.  
**Fix:** Add the following two entries to every file's TOC:
```markdown
- [Further reading](#further-reading)
- [Next step](#next-step)
```
This is best done with a one-line sed script:
```bash
find . -name "*.md" | xargs sed -i '/- \[Next step\]/d; /## Table of contents/a - [Further reading](#further-reading)\n- [Next step](#next-step)'
```
Or automate via a short Python script during the build step.

### Fix 10 — Labs missing `## Prerequisites`, `## Success criteria`, and `## Common failures` from TOCs
**Files:** All lab files (`03-rhcsa/labs/`, `04-rhce/labs/`, `05-rhca/*/labs/`, `90-labs/`)  
**Severity:** 🟡 Low-Medium — Lab files use a standard template with `## Prerequisites`, `## Success criteria`, `## Common failures`, and `## Cleanup` sections, but these are consistently absent from TOCs. These are high-value navigation targets for learners who want to verify their environment or check their work.  
**Fix:** Add standard lab TOC entries to all lab file templates:
```markdown
- [Prerequisites](#prerequisites)
- [Success criteria](#success-criteria)
- [Common failures](#common-failures)
- [Cleanup](#cleanup)
- [Why this matters in production](#why-this-matters-in-production)
- [Next step](#next-step)
```
