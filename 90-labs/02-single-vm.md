
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Single-VM Lab Setup
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

## Overview

A single RHEL 10 VM covers 95% of the labs in this guide. This page walks through creating it with KVM/QEMU, performing a minimal installation, and configuring the baseline student environment.

**Estimated time:** 30–45 minutes  
**What you get:** A fully registered, SSH-accessible RHEL 10 VM ready for all Track A–D labs.


[↑ Back to TOC](#toc)

---
<a name="toc"></a>

## Table of contents

- [Overview](#overview)
- [Step 1 — Install KVM and virt-install (Host)](#step-1-install-kvm-and-virt-install-host)
- [Step 2 — Create the VM](#step-2-create-the-vm)
- [Step 3 — RHEL 10 Installation (Anaconda)](#step-3-rhel-10-installation-anaconda)
  - [Installation Destination](#installation-destination)
  - [Software Selection](#software-selection)
  - [Network and Host Name](#network-and-host-name)
  - [Root Password](#root-password)
- [Step 4 — First Boot](#step-4-first-boot)
  - [Confirm SSH access](#confirm-ssh-access)
  - [Register the system](#register-the-system)
- [Step 5 — Baseline Configuration](#step-5-baseline-configuration)
- [Step 6 — SSH Key Setup (Recommended)](#step-6-ssh-key-setup-recommended)
- [Step 7 — Snapshot the VM (Strongly Recommended)](#step-7-snapshot-the-vm-strongly-recommended)
- [Disk Layout for Storage Labs](#disk-layout-for-storage-labs)
- [Quick Reference — VM Management](#quick-reference-vm-management)
- [Troubleshooting](#troubleshooting)


## Prerequisites

- A Linux workstation with KVM and `libvirt` installed
- At least 8 GB RAM available on the host (4 GB for the VM, rest for the host)
- 40 GB free disk space
- RHEL 10 ISO downloaded

---


[↑ Back to TOC](#toc)

## Step 1 — Install KVM and virt-install (Host)

```bash
# On the KVM host (Fedora/RHEL)
$ sudo dnf install -y qemu-kvm libvirt virt-install virt-manager

$ sudo systemctl enable --now libvirtd

# Verify KVM is functional
$ sudo virsh list --all
 Id   Name   State

[↑ Back to TOC](#toc)

--------------------
```

---

## Step 2 — Create the VM

```bash
$ sudo virt-install \
  --name rhel10-lab \
  --memory 4096 \
  --vcpus 4 \
  --disk size=40,format=qcow2,bus=virtio \
  --cdrom /path/to/rhel-10.x-x86_64-dvd.iso \
  --os-variant rhel10.0 \
  --network network=default,model=virtio \
  --graphics vnc \
  --noautoconsole
```

Open the VM console:

```bash
$ virt-manager &
# or
$ sudo virsh console rhel10-lab
```


[↑ Back to TOC](#toc)

---

## Step 3 — RHEL 10 Installation (Anaconda)

Follow the graphical installer with these settings:

### Installation Destination

- Select `/dev/vda` (40 GB virtio disk)
- Partitioning: **Automatic** (for initial setup)
- Or custom:

| Mount point | Size | Filesystem |
|---|---|---|
| `/boot` | 1 GB | xfs |
| `/boot/efi` | 600 MB | vfat (if UEFI) |
| `swap` | 4 GB | swap |
| `/` | remainder | xfs |

### Software Selection

Choose **Minimal Install** — we install packages on-demand throughout the guide.

### Network and Host Name

- Hostname: `rhel10.lab.local`
- Enable the Ethernet interface (it will get a DHCP address initially)

### Root Password

Set a strong root password. Then also create a user account:

- Username: `student`
- Check "Make this user administrator" (adds to `wheel` group)


[↑ Back to TOC](#toc)

---

## Step 4 — First Boot

After reboot, log in as `student` via the console or SSH.

### Confirm SSH access

```bash
# From the KVM host, get the VM's IP
$ sudo virsh domifaddr rhel10-lab
 Name       MAC address          Protocol     Address

[↑ Back to TOC](#toc)

-------------------------------------------------------------------------------
 vnet0      52:54:00:xx:xx:xx    ipv4         192.168.122.10/24

# SSH in
$ ssh student@192.168.122.10
```

### Register the system

```bash
$ sudo subscription-manager register --username <rhn-username> --password <rhn-password>
$ sudo subscription-manager attach --auto
$ sudo dnf update -y
```

> If you have a Developer Subscription, use the same credentials. Alternatively, configure a local Satellite or DNF mirror.


[↑ Back to TOC](#toc)

---

## Step 5 — Baseline Configuration

```bash
# Set hostname persistently
$ sudo hostnamectl set-hostname rhel10.lab.local

# Verify sudo works
$ sudo whoami
root

# Install commonly needed tools (used across labs)
$ sudo dnf install -y \
    bash-completion \
    bind-utils \
    tcpdump \
    net-tools \
    lsof \
    strace \
    vim \
    tmux \
    git \
    python3 \
    podman

# Enable and start firewalld (should already be active)
$ sudo systemctl enable --now firewalld
$ sudo firewall-cmd --state
running
```


[↑ Back to TOC](#toc)

---

## Step 6 — SSH Key Setup (Recommended)

Generate an SSH key pair on your workstation and copy the public key to the lab VM for passwordless access:

```bash
# On your workstation
$ ssh-keygen -t ed25519 -C "rhca-lab"

$ ssh-copy-id student@192.168.122.10
```


[↑ Back to TOC](#toc)

---

## Step 7 — Snapshot the VM (Strongly Recommended)

Take a snapshot before starting any lab so you can roll back quickly:

```bash
$ sudo virsh snapshot-create-as rhel10-lab \
    --name "baseline" \
    --description "Clean RHEL 10 install, student user, tools installed"

# List snapshots
$ sudo virsh snapshot-list rhel10-lab

# Restore to snapshot
$ sudo virsh snapshot-revert rhel10-lab baseline
```


[↑ Back to TOC](#toc)

---

## Disk Layout for Storage Labs

LVM and filesystem labs (Chapters 03-rhcsa) need extra disk space. Add a second virtual disk:

```bash
# Attach a second 10 GB disk to the running VM
$ sudo virsh attach-disk rhel10-lab \
    /var/lib/libvirt/images/rhel10-lab-extra.qcow2 \
    vdb \
    --driver qemu \
    --subdriver qcow2 \
    --persistent

# Create the image file first if it doesn't exist
$ sudo qemu-img create -f qcow2 \
    /var/lib/libvirt/images/rhel10-lab-extra.qcow2 10G

# Inside the VM, confirm the new disk
$ lsblk
NAME   MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
vda    252:0    0  40G  0 disk
...
vdb    252:16   0  10G  0 disk   ← second disk for storage labs
```


[↑ Back to TOC](#toc)

---

## Quick Reference — VM Management

```bash
# Start VM
$ sudo virsh start rhel10-lab

# Graceful shutdown
$ sudo virsh shutdown rhel10-lab

# Force off
$ sudo virsh destroy rhel10-lab

# Delete VM and its disk (irreversible)
$ sudo virsh undefine rhel10-lab --remove-all-storage

# Get console (use Ctrl+] to detach)
$ sudo virsh console rhel10-lab
```


[↑ Back to TOC](#toc)

---

## Success Criteria

Before moving on to Chapter 1:

- [ ] `ssh student@<vm-ip>` works without a password (key auth)
- [ ] `sudo dnf update -y` completes without errors
- [ ] `podman --version` returns a version string
- [ ] A baseline snapshot named `baseline` exists
- [ ] `lsblk` shows `/dev/vdb` (second disk attached)

---


[↑ Back to TOC](#toc)

## Troubleshooting

| Problem | Fix |
|---|---|
| No IP address on `ens3` | `sudo nmcli connection up ens3`; check if DHCP server on the `default` libvirt network is running |
| `subscription-manager` fails | Check network connectivity; verify RHN credentials; try `--force` |
| SSH connection refused | Confirm `sshd` is running: `sudo systemctl start sshd` |
| Disk not visible as `/dev/vda` | Different hypervisor uses `/dev/sda` — update disk references in labs accordingly |
| `virt-install` fails with `No space left` | Free up disk space on the host in `/var/lib/libvirt/images/` |


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [`virt-install` man page](https://linux.die.net/man/1/virt-install) | Full CLI reference for scripted VM creation |
| [`virsh` man page](https://libvirt.org/manpages/virsh.html) | VM lifecycle management: start, stop, snapshot, console |
| [RHEL 10 — Installation Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/interactively_installing_rhel_from_installation_media/index) | Official RHEL installation walkthrough |

---


[↑ Back to TOC](#toc)

## Next step

→ [Multi-VM Lab Setup](03-multi-vm.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
