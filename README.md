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
- Highlighted blocks like this:

> **⚠️ Do NOT do this**
> A pattern you should avoid, with a short explanation and the correct alternative.
>

> **💡 Pro tip**
> Useful shortcut or context that helps you understand the "why".
>

Full details in [Conventions](00-preface/conventions.md).

---

## Objective map

Every chapter is mapped to RHCSA / RHCE / RHCA-style skill domains in the
[Objective Map](98-reference/objective-map.md) appendix.

> **Note:** This guide does not promise exam coverage. It teaches the real-world
> skills that those certifications measure.
