
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab Workflow — Snapshots and Safety
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Golden rule

> **Take a VM snapshot before every lab.** If something goes wrong, revert
> and start over. Snapshots are free and save enormous time.


[↑ Back to TOC](#toc)

## Recommended VM setup

| Tool | Notes |
|---|---|
| **GNOME Boxes** | Easiest snapshot UX on Linux desktop |
| **VirtualBox** | Free; snapshots via Machine → Take Snapshot |
| **libvirt / virt-manager** | Best for advanced setups; CLI snapshots with `virsh snapshot-create-as` |
| **VMware Workstation / Fusion** | Commercial; excellent snapshot support |

### Take a snapshot before each lab

**virt-manager (GUI)**

Right-click the VM → **Manage Snapshots** → **+**

**virsh (CLI)**

```bash
virsh snapshot-create-as --domain rhel10-lab \
  --name "before-lab-$(date +%Y%m%d)" \
  --description "clean state"
```

**VirtualBox (CLI)**

```bash
VBoxManage snapshot "rhel10-lab" take "before-lab-$(date +%Y%m%d)"
```

### Restore a snapshot

**virsh (CLI)**

```bash
virsh snapshot-revert --domain rhel10-lab --snapshotname "before-lab-20260223"
```

**VirtualBox (CLI)**

```bash
VBoxManage snapshot "rhel10-lab" restore "before-lab-20260223"
```



[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Golden rule](#golden-rule)
- [Recommended VM setup](#recommended-vm-setup)
  - [Take a snapshot before each lab](#take-a-snapshot-before-each-lab)
  - [Restore a snapshot](#restore-a-snapshot)
- [Lab page anatomy](#lab-page-anatomy)
- [Estimated time](#estimated-time)
- [Steps  (numbered, with Verify checkpoints inline)](#steps-numbered-with-verify-checkpoints-inline)
- [Verify checkpoints](#verify-checkpoints)
- [Safety conventions](#safety-conventions)
- [Single-VM vs Multi-VM labs](#single-vm-vs-multi-vm-labs)


## Lab page anatomy

Every lab in this guide has the same structure:

```

[↑ Back to TOC](#toc)

## Prerequisites

[↑ Back to TOC](#toc)

## Estimated time

[↑ Back to TOC](#toc)

## Success criteria

[↑ Back to TOC](#toc)

## Steps  (numbered, with Verify checkpoints inline)

[↑ Back to TOC](#toc)

## Cleanup

[↑ Back to TOC](#toc)

## Common failures

[↑ Back to TOC](#toc)

## Why this matters in production
```

Read the **Success criteria** section first — it tells you exactly what "done"
looks like before you start typing.

---


[↑ Back to TOC](#toc)

## Verify checkpoints

Labs use **verify** blocks to confirm state at key points:

> **✅ Verify**
> ```bash
> systemctl is-active myservice
> ```
> Expected: `active`
>

If a verify step fails, stop and read the **Common failures** section for that
lab before proceeding.


[↑ Back to TOC](#toc)

---

## Safety conventions

- Every destructive-ish command (anything touching disks, firewall rules, or
  SELinux mode) is marked with a warning admonition.
- Labs do **not** ask you to run `setenforce 0` as a fix — if you see that in a
  tutorial elsewhere, treat it as a red flag.
- Labs do **not** ask you to disable `firewalld` — they show you the correct
  rule to add.
- Cleanup steps are mandatory, not optional. Run them before your next lab.


[↑ Back to TOC](#toc)

---

## Single-VM vs Multi-VM labs

| Label | Topology |
|---|---|
| *(no label)* | Single VM only |
| `(Multi-VM)` | Needs 2–3 VMs; instructions provided |

Multi-VM labs are always optional. The same skill is demonstrated in a
single-VM variant where possible.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [KVM/libvirt Snapshot Management](https://libvirt.org/formatsnapshot.html) | Snapshot XML format and `virsh snapshot-*` commands |
| [RHEL 10 — Configuring and using virtualization](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_virtualization/index) | Official guide to KVM/QEMU on RHEL |
| [virt-manager project](https://virt-manager.org/) | GUI for libvirt; useful for snapshot management |

---


[↑ Back to TOC](#toc)

## Next step

→ [Conventions (Prompts, Paths, Editors)](03-conventions.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
