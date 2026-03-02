# Red Hat Enterprise Linux 10 — Beginner to RHCA

> **Note:** This guide does not promise exam coverage. It teaches the real-world
> skills that those certifications measure.

Welcome. This guide takes you from your very first login on a RHEL 10 system
all the way through the skills expected of a Red Hat Certified Architect (RHCA)
on the **RHEL infrastructure** track — with hands-on labs every step of the way.

[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

---
<a name="toc"></a>

## Table of contents

- [Who this guide is for](#who-this-guide-is-for)
- [How the guide is structured](#how-the-guide-is-structured)
- [Full table of contents](#full-table-of-contents)
  - [Preface](#preface)
  - [Getting Started (Onramp)](#getting-started-onramp)
  - [Linux Foundations (Onramp)](#linux-foundations-onramp)
  - [RHEL Administration (RHCSA Track)](#rhel-administration-rhcsa-track)
  - [Automation (RHCE Track)](#automation-rhce-track)
  - [Advanced Infrastructure (RHCA Track)](#advanced-infrastructure-rhca-track)
  - [Lab Environments](#lab-environments)
  - [Reference](#reference)
- [Lab environment](#lab-environment)
- [Conventions at a glance](#conventions-at-a-glance)
- [License](#license)


## Who this guide is for

| You are … | Start here |
|---|---|
| Completely new to Linux | [Install a RHEL 10 Lab VM](01-getting-started/01-vm-install.md) |
| Comfortable with Linux basics, learning RHEL admin | [Packages and Repos](03-rhcsa/01-packages-dnf.md) |
| Preparing for RHCE or wanting automation skills | [Automation Mindset](04-rhce/01-automation-mindset.md) |
| Going deep on RHEL infrastructure / RHCA | [Troubleshooting Playbook](05-rhca/01-troubleshooting-playbook.md) |


[↑ Back to TOC](#toc)

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


[↑ Back to TOC](#toc)

---

## Full table of contents

### Preface

- [About This Guide](00-preface/01-about.md)
- [Lab Workflow (Snapshots, Safety)](00-preface/02-labs.md)
- [Conventions (Prompts, Paths, Editors)](00-preface/03-conventions.md)

### Getting Started (Onramp)

- [Install a RHEL 10 Lab VM](01-getting-started/01-vm-install.md)
- [First Boot Checklist](01-getting-started/02-first-boot.md)
- [Accounts, sudo, and Updates](01-getting-started/03-sudo-updates.md)
- [Getting Help (man, --help, apropos)](01-getting-started/04-help-system.md)

### Linux Foundations (Onramp)

- [Shell Basics (pwd, ls, cd)](02-foundations/01-shell-basics.md)
- [Files and Text (cp, mv, rm, less)](02-foundations/02-files-and-text.md)
- [Pipes and Redirection](02-foundations/03-pipes-redirection.md)
- [Editing Files (nano + vim intro)](02-foundations/04-editors.md)
- [Users, Groups, Permissions](02-foundations/05-permissions.md)
- [ACLs (When and How)](02-foundations/06-acls.md)
- [Lab — Shared Team Directory](02-foundations/labs/01-shared-team-dir.md)

### RHEL Administration (RHCSA Track)

- [Packages and Repos (dnf)](03-rhcsa/01-packages-dnf.md)
- [Storage Overview (lsblk, blkid, mounts)](03-rhcsa/02-storage-overview.md)
- [Filesystems and fstab (XFS)](03-rhcsa/03-filesystems-fstab.md)
- [LVM (Create, Extend, Reduce Safely)](03-rhcsa/04-lvm.md)
- [systemd Essentials](03-rhcsa/05-systemd-basics.md)
- [Logs and journalctl](03-rhcsa/06-logging-journald.md)
- [Scheduling (timers + cron)](03-rhcsa/07-scheduling.md)
- [Networking Basics (ip, ss)](03-rhcsa/08-networking-basics.md)
- [NetworkManager (nmcli)](03-rhcsa/09-networkmanager-nmcli.md)
- [DNS and Name Resolution](03-rhcsa/10-dns-resolution.md)
- [Firewalling (firewalld)](03-rhcsa/11-firewalld.md)
- [SSH (Keys, Server Basics)](03-rhcsa/12-ssh.md)
- [SELinux Fundamentals (Contexts, Booleans)](03-rhcsa/13-selinux-fundamentals.md)
- [SELinux Troubleshooting (AVCs)](03-rhcsa/14-selinux-avc-basics.md)
- [Lab — Static IP + DNS Validation](03-rhcsa/labs/01-static-ip-dns.md)
- [Lab — Create a systemd Service](03-rhcsa/labs/02-systemd-service.md)
- [Lab — LVM + XFS Grow](03-rhcsa/labs/03-lvm-xfs-grow.md)
- [Lab — Fix a SELinux Label Issue](03-rhcsa/labs/04-selinux-label-fix.md)

### Automation (RHCE Track)

- [Automation Mindset (Idempotence)](04-rhce/01-automation-mindset.md)
- [Bash Scripting Fundamentals](04-rhce/02-bash-fundamentals.md)
- [Ansible Setup and Inventory](04-rhce/03-ansible-setup-inventory.md)
- [Ansible Playbooks (Tasks, Handlers)](04-rhce/04-ansible-playbooks.md)
- [Variables, Templates, and Files](04-rhce/05-ansible-vars-templates.md)
- [Roles and Collections](04-rhce/06-ansible-roles.md)
- [Deploy a Service with Ansible (Firewall + SELinux)](04-rhce/07-ansible-service-deploy.md)
- [Patch Workflow + Reporting](04-rhce/08-ansible-patching.md)
- [Lab — Write Your First Playbook](04-rhce/labs/01-first-playbook.md)
- [Lab — Role-Based Web Service Deploy](04-rhce/labs/02-role-web-deploy.md)

### Advanced Infrastructure (RHCA Track)

- [Troubleshooting Playbook (First 10 Minutes)](05-rhca/01-troubleshooting-playbook.md)
- [Advanced systemd (Dependencies, Drop-ins)](05-rhca/02-systemd-advanced.md)
- [systemd Hardening (Service Sandboxing)](05-rhca/03-systemd-hardening.md)
- [Journald Retention and Forwarding](05-rhca/04-journald-retention.md)

**SELinux Deep Dive**
- [Fix Taxonomy (Label vs Boolean vs Port vs Policy)](05-rhca/selinux/01-fix-taxonomy.md)
- [semanage (fcontext, port, boolean)](05-rhca/selinux/02-semanage.md)
- [Audit Workflow (ausearch, audit2why cautions)](05-rhca/selinux/03-audit-workflow.md)
- [Lab — Non-Default Port (Correct SELinux Fix)](05-rhca/selinux/labs/01-nondefault-port.md)

**Networking Deep Dive**
- [nmcli Profiles at Scale](05-rhca/networking/01-nmcli-profiles.md)
- [Routing + Troubleshooting Method](05-rhca/networking/02-routing-method.md)
- [tcpdump Guided Debugging](05-rhca/networking/03-tcpdump.md)
- [VLAN, Bridge, Bond Concepts](05-rhca/networking/04-l2-concepts.md)
- [Lab — Debug DNS vs Routing vs Firewall](05-rhca/networking/labs/01-debug-triad.md)

**Containers with Podman**
- [Container Fundamentals (RHEL view)](05-rhca/containers/01-podman-fundamentals.md)
- [Rootless Podman (Storage, Networking)](05-rhca/containers/02-rootless.md)
- [Volumes and Persistent Data](05-rhca/containers/03-volumes.md)
- [Podman Secrets (Create, Use, Rotate)](05-rhca/containers/04-secrets.md)
- [systemd-Managed Containers (Quadlet)](05-rhca/containers/05-systemd-integration.md)
- [Container SELinux Gotchas (Volumes, Labels)](05-rhca/containers/06-selinux-containers.md)
- [Lab — Run Rootless Web App + Persistent Data](05-rhca/containers/labs/01-rootless-web.md)
- [Lab — Inject + Rotate a Podman Secret](05-rhca/containers/labs/02-secrets-rotate.md)

**Performance and Resilience**
- [Resource Triage (CPU, Mem, Disk, IO)](05-rhca/perf/01-resource-triage.md)
- [tuned Basics](05-rhca/perf/02-tuned.md)
- [Recovery Patterns](05-rhca/perf/03-recovery-patterns.md)

### Lab Environments

- [Lab Environments Overview](90-labs/01-index.md)
- [Single-VM Labs](90-labs/02-single-vm.md)
- [Multi-VM Labs (Optional)](90-labs/03-multi-vm.md)

### Reference

- [Exam Objective Map](98-reference/01-objective-map.md)
- [Glossary](98-reference/02-glossary.md)
- [Command Cheatsheets](98-reference/03-cheatsheets.md)
- [Further Reading (Official Docs)](98-reference/04-further-reading.md)


[↑ Back to TOC](#toc)

---

## Lab environment

All labs target a **single fresh RHEL 10 VM** unless explicitly marked
`(Multi-VM)`. Every lab tells you exactly:

- what packages to install first
- the step-by-step commands with expected results
- how to verify success
- how to clean up and reset

Read the [Lab Workflow](00-preface/02-labs.md) page before starting your first lab.


[↑ Back to TOC](#toc)

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

Full details in [Conventions](00-preface/03-conventions.md).


## License

This project is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

https://creativecommons.org/licenses/by-nc-sa/4.0/

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
