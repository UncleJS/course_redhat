# Red Hat Enterprise Linux 10 — Beginner to RHCA

> **Note:** This guide does not promise exam coverage. It teaches the real-world
> skills that those certifications measure.

Welcome. This guide takes you from your very first login on a RHEL 10 system
all the way through the skills expected of a Red Hat Certified Architect (RHCA)
on the **RHEL infrastructure** track — with hands-on labs every step of the way.

---

## Who this guide is for

| You are … | Start here |
|---|---|
| Completely new to Linux | [Install a RHEL 10 Lab VM](01-getting-started/vm-install.md) |
| Comfortable with Linux basics, learning RHEL admin | [Packages and Repos](03-rhcsa/packages-dnf.md) |
| Preparing for RHCE or wanting automation skills | [Automation Mindset](04-rhce/automation-mindset.md) |
| Going deep on RHEL infrastructure / RHCA | [Troubleshooting Playbook](05-rhca/troubleshooting-playbook.md) |

---

## How the guide is structured

The guide is split into four progressive tracks:

```
Onramp  →  RHCSA  →  RHCE  →  RHCA
```

You can read start-to-finish or jump directly to any chapter. Each chapter is
self-contained and lists its prerequisites up front.

| Track | Covers |
|---|---|
| **Onramp** | Terminal, files, permissions, editors, help system |
| **RHCSA** | Storage, users, systemd, networking, firewall, SSH, SELinux |
| **RHCE** | Bash, Ansible, roles, patching workflows |
| **RHCA** | SELinux deep dive, advanced systemd, networking, Podman ops, performance |

---

## Full table of contents

### Preface

- [About This Guide](00-preface/about.md)
- [Lab Workflow (Snapshots, Safety)](00-preface/labs.md)
- [Conventions (Prompts, Paths, Editors)](00-preface/conventions.md)

### Getting Started (Onramp)

- [Install a RHEL 10 Lab VM](01-getting-started/vm-install.md)
- [First Boot Checklist](01-getting-started/first-boot.md)
- [Accounts, sudo, and Updates](01-getting-started/sudo-updates.md)
- [Getting Help (man, --help, apropos)](01-getting-started/help-system.md)

### Linux Foundations (Onramp)

- [Shell Basics (pwd, ls, cd)](02-foundations/shell-basics.md)
- [Files and Text (cp, mv, rm, less)](02-foundations/files-and-text.md)
- [Pipes and Redirection](02-foundations/pipes-redirection.md)
- [Editing Files (nano + vim intro)](02-foundations/editors.md)
- [Users, Groups, Permissions](02-foundations/permissions.md)
- [ACLs (When and How)](02-foundations/acls.md)
- [Lab — Shared Team Directory](02-foundations/labs/shared-team-dir.md)

### RHEL Administration (RHCSA Track)

- [Packages and Repos (dnf)](03-rhcsa/packages-dnf.md)
- [Storage Overview (lsblk, blkid, mounts)](03-rhcsa/storage-overview.md)
- [Filesystems and fstab (XFS)](03-rhcsa/filesystems-fstab.md)
- [LVM (Create, Extend, Reduce Safely)](03-rhcsa/lvm.md)
- [systemd Essentials](03-rhcsa/systemd-basics.md)
- [Logs and journalctl](03-rhcsa/logging-journald.md)
- [Scheduling (timers + cron)](03-rhcsa/scheduling.md)
- [Networking Basics (ip, ss)](03-rhcsa/networking-basics.md)
- [NetworkManager (nmcli)](03-rhcsa/networkmanager-nmcli.md)
- [DNS and Name Resolution](03-rhcsa/dns-resolution.md)
- [Firewalling (firewalld)](03-rhcsa/firewalld.md)
- [SSH (Keys, Server Basics)](03-rhcsa/ssh.md)
- [SELinux Fundamentals (Contexts, Booleans)](03-rhcsa/selinux-fundamentals.md)
- [SELinux Troubleshooting (AVCs)](03-rhcsa/selinux-avc-basics.md)
- [Lab — Static IP + DNS Validation](03-rhcsa/labs/static-ip-dns.md)
- [Lab — Create a systemd Service](03-rhcsa/labs/systemd-service.md)
- [Lab — LVM + XFS Grow](03-rhcsa/labs/lvm-xfs-grow.md)
- [Lab — Fix a SELinux Label Issue](03-rhcsa/labs/selinux-label-fix.md)

### Automation (RHCE Track)

- [Automation Mindset (Idempotence)](04-rhce/automation-mindset.md)
- [Bash Scripting Fundamentals](04-rhce/bash-fundamentals.md)
- [Ansible Setup and Inventory](04-rhce/ansible-setup-inventory.md)
- [Ansible Playbooks (Tasks, Handlers)](04-rhce/ansible-playbooks.md)
- [Variables, Templates, and Files](04-rhce/ansible-vars-templates.md)
- [Roles and Collections](04-rhce/ansible-roles.md)
- [Deploy a Service with Ansible (Firewall + SELinux)](04-rhce/ansible-service-deploy.md)
- [Patch Workflow + Reporting](04-rhce/ansible-patching.md)
- [Lab — Write Your First Playbook](04-rhce/labs/first-playbook.md)
- [Lab — Role-Based Web Service Deploy](04-rhce/labs/role-web-deploy.md)

### Advanced Infrastructure (RHCA Track)

- [Troubleshooting Playbook (First 10 Minutes)](05-rhca/troubleshooting-playbook.md)
- [Advanced systemd (Dependencies, Drop-ins)](05-rhca/systemd-advanced.md)
- [systemd Hardening (Service Sandboxing)](05-rhca/systemd-hardening.md)
- [Journald Retention and Forwarding](05-rhca/journald-retention.md)

**SELinux Deep Dive**
- [Fix Taxonomy (Label vs Boolean vs Port vs Policy)](05-rhca/selinux/fix-taxonomy.md)
- [semanage (fcontext, port, boolean)](05-rhca/selinux/semanage.md)
- [Audit Workflow (ausearch, audit2why cautions)](05-rhca/selinux/audit-workflow.md)
- [Lab — Non-Default Port (Correct SELinux Fix)](05-rhca/selinux/labs/nondefault-port.md)

**Networking Deep Dive**
- [nmcli Profiles at Scale](05-rhca/networking/nmcli-profiles.md)
- [Routing + Troubleshooting Method](05-rhca/networking/routing-method.md)
- [tcpdump Guided Debugging](05-rhca/networking/tcpdump.md)
- [VLAN, Bridge, Bond Concepts](05-rhca/networking/l2-concepts.md)
- [Lab — Debug DNS vs Routing vs Firewall](05-rhca/networking/labs/debug-triad.md)

**Containers with Podman**
- [Container Fundamentals (RHEL view)](05-rhca/containers/podman-fundamentals.md)
- [Rootless Podman (Storage, Networking)](05-rhca/containers/rootless.md)
- [Volumes and Persistent Data](05-rhca/containers/volumes.md)
- [Podman Secrets (Create, Use, Rotate)](05-rhca/containers/secrets.md)
- [systemd-Managed Containers (Quadlet)](05-rhca/containers/systemd-integration.md)
- [Container SELinux Gotchas (Volumes, Labels)](05-rhca/containers/selinux-containers.md)
- [Lab — Run Rootless Web App + Persistent Data](05-rhca/containers/labs/rootless-web.md)
- [Lab — Inject + Rotate a Podman Secret](05-rhca/containers/labs/secrets-rotate.md)

**Performance and Resilience**
- [Resource Triage (CPU, Mem, Disk, IO)](05-rhca/perf/resource-triage.md)
- [tuned Basics](05-rhca/perf/tuned.md)
- [Recovery Patterns](05-rhca/perf/recovery-patterns.md)

### Lab Environments

- [Lab Environments Overview](90-labs/index.md)
- [Single-VM Labs](90-labs/single-vm.md)
- [Multi-VM Labs (Optional)](90-labs/multi-vm.md)

### Reference

- [Exam Objective Map](98-reference/objective-map.md)
- [Glossary](98-reference/glossary.md)
- [Command Cheatsheets](98-reference/cheatsheets.md)
- [Further Reading (Official Docs)](98-reference/further-reading.md)

---

## Lab environment

All labs target a **single fresh RHEL 10 VM** unless explicitly marked
`(Multi-VM)`. Every lab tells you exactly:

- what packages to install first
- the step-by-step commands with expected results
- how to verify success
- how to clean up and reset

Read the [Lab Workflow](00-preface/labs.md) page before starting your first lab.

---

## Conventions at a glance

- `$` — command runs as a regular user
- `#` — command runs as root (prefer `sudo` unless told otherwise)
- `sudo command` — escalate a single command (safe default)

> **⚠️ Do NOT do this**
> A pattern you should avoid, with a short explanation and the correct alternative.
>

> **💡 Pro tip**
> Useful shortcut or context that helps you understand the "why".
>

Full details in [Conventions](00-preface/conventions.md).
