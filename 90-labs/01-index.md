# Lab Environments

## Overview

The labs in this guide are designed for hands-on practice in a safe, isolated environment. This section describes the two supported configurations:

| Configuration | Best For |
|---|---|
| [Single-VM](02-single-vm.md) | Working through all chapters sequentially; most exercises |
| [Multi-VM](03-multi-vm.md) | Ansible labs, networking labs, replication, multi-node scenarios |


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [What You Need](#what-you-need)
  - [Hardware or Cloud Instance](#hardware-or-cloud-instance)
- [RHEL 10 Installation Media](#rhel-10-installation-media)
- [Lab VM Conventions](#lab-vm-conventions)
- [Quick-Start Checklist](#quick-start-checklist)


## What You Need

### Hardware or Cloud Instance

| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 vCPUs | 4 vCPUs |
| RAM | 2 GB | 4 GB |
| Disk | 20 GB | 40 GB |
| Network | 1 NIC | 1 NIC + optional 2nd |

A KVM/QEMU hypervisor on Linux is the assumed environment. VirtualBox, VMware Workstation, or a cloud provider (AWS, GCP, Azure) also work — adapt disk device names (`/dev/vda` → `/dev/sda` or `/dev/nvme0n1`) as needed.


[↑ Back to TOC](#toc)

---

## RHEL 10 Installation Media

Download from the Red Hat Customer Portal (subscription required) or use a free developer account:

- Developer subscription: [https://developers.redhat.com](https://developers.redhat.com)
- ISO: Red Hat Enterprise Linux 10.x DVD ISO


[↑ Back to TOC](#toc)

---

## Lab VM Conventions

Throughout the labs:

| Convention | Value |
|---|---|
| Primary disk | `/dev/vda` |
| Network interface | `ens3` |
| Non-root user | `student` |
| Hostname (single VM) | `rhel10.lab.local` |
| Hostname (multi-VM controller) | `controller.lab.local` |
| Hostname (multi-VM managed nodes) | `node1.lab.local`, `node2.lab.local` |


[↑ Back to TOC](#toc)

---

## Quick-Start Checklist

Before starting Chapter 1:

- [ ] RHEL 10 installed and boots successfully
- [ ] `student` user created with `sudo` access
- [ ] System registered (`subscription-manager register`) or connected to a local mirror
- [ ] SSH key-based login working from your workstation to the VM
- [ ] Internet or local mirror accessible for `dnf`

See [Single-VM Setup](02-single-vm.md) for the detailed walkthrough.


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring and managing virtualization](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_virtualization/index) | Official KVM/QEMU setup and VM management |
| [Red Hat Developer — Free RHEL download](https://developers.redhat.com/products/rhel/download) | No-cost RHEL 10 for lab use |
| [virt-manager project](https://virt-manager.org/) | GUI front-end for libvirt useful for lab management |

---

## Next step

→ [Single-VM Lab Setup](02-single-vm.md)
---

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0
