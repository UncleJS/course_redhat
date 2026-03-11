
[↑ Back to TOC](#toc)

# Storage Overview — lsblk, blkid, mounts
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

Before managing storage, you need to understand what devices exist, how they
are partitioned, and what is currently mounted.

---
<a name="toc"></a>

## Table of contents

- [Block device hierarchy](#block-device-hierarchy)
- [List block devices — `lsblk`](#list-block-devices-lsblk)
- [Identify filesystems — `blkid`](#identify-filesystems-blkid)
- [View current mounts](#view-current-mounts)
- [Partition tools](#partition-tools)
  - [`fdisk` (MBR and GPT, interactive)](#fdisk-mbr-and-gpt-interactive)
  - [`gdisk` (GPT only)](#gdisk-gpt-only)
  - [`parted` (scriptable, GPT-aware)](#parted-scriptable-gpt-aware)
- [Creating a filesystem](#creating-a-filesystem)
- [Mounting a filesystem](#mounting-a-filesystem)
  - [Persistent mount via `/etc/fstab`](#persistent-mount-via-etcfstab)
- [Swap](#swap)


## Block device hierarchy

```
Physical disk (e.g., /dev/vda)
  └── Partition (e.g., /dev/vda1, /dev/vda2)
        └── Filesystem (e.g., XFS, ext4)
              └── Mount point (e.g., /, /boot, /home)
```

On RHEL VMs you typically see:
- `/dev/vda` — KVM/QEMU virtual disk
- `/dev/sda` — SCSI/SATA disk (bare metal or VMware)
- `/dev/nvme0n1` — NVMe disk (modern bare metal)


[↑ Back to TOC](#toc)

---

## List block devices — `lsblk`

```bash
lsblk
```

Example output:

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vda    252:0    0   20G  0 disk
├─vda1 252:1    0    1G  0 part /boot
├─vda2 252:2    0    2G  0 part [SWAP]
└─vda3 252:3    0   17G  0 part /
```

```bash
# Show filesystem type and UUID
lsblk -f

# Show size in bytes
lsblk -b
```


[↑ Back to TOC](#toc)

---

## Identify filesystems — `blkid`

```bash
sudo blkid
```

Output shows UUID, type, and label for each partition. UUIDs are what `/etc/fstab`
uses to identify devices reliably (device names like `/dev/vda1` can change).

```bash
# Show info for a specific device
sudo blkid /dev/vda1
```


[↑ Back to TOC](#toc)

---

## View current mounts

```bash
# All currently mounted filesystems
mount | column -t

# Only real filesystems (not virtual)
mount | grep -v " (tmpfs\|sysfs\|proc\|devtmpfs\|cgroup)"

# Disk usage per mount
df -h

# Inode usage (if disk is "full" but df looks OK)
df -ih
```


[↑ Back to TOC](#toc)

---

## Partition tools

### `fdisk` (MBR and GPT, interactive)

```bash
sudo fdisk /dev/vdb      # interactive mode — type m for help
sudo fdisk -l            # list all partition tables
sudo fdisk -l /dev/vda   # list one disk
```

### `gdisk` (GPT only)

```bash
sudo gdisk /dev/vdb
```

### `parted` (scriptable, GPT-aware)

```bash
sudo parted /dev/vdb print
sudo parted /dev/vdb mklabel gpt
sudo parted /dev/vdb mkpart primary xfs 1MiB 100%
```


[↑ Back to TOC](#toc)

---

## Creating a filesystem

```bash
# XFS (default on RHEL)
sudo mkfs.xfs /dev/vdb1

# XFS with a label
sudo mkfs.xfs -L mydata /dev/vdb1

# ext4 (legacy, occasionally needed)
sudo mkfs.ext4 /dev/vdb1
```


[↑ Back to TOC](#toc)

---

## Mounting a filesystem

```bash
# Create mount point
sudo mkdir -p /mnt/data

# Mount temporarily
sudo mount /dev/vdb1 /mnt/data

# Mount by UUID
sudo mount UUID="<uuid-from-blkid>" /mnt/data

# Unmount
sudo umount /mnt/data
```

### Persistent mount via `/etc/fstab`

```bash
sudo blkid /dev/vdb1   # get UUID
sudo vim /etc/fstab
```

Add a line:

```
UUID=<your-uuid>  /mnt/data  xfs  defaults  0 0
```

Test without rebooting:

```bash
sudo mount -a
```

> **🚨 Always test fstab before rebooting**
> A bad fstab entry can prevent the system from booting. Always run
> `sudo mount -a` after editing fstab to catch errors immediately.
>


[↑ Back to TOC](#toc)

---

## Swap

```bash
# Check current swap
swapon --show

# Create a swap partition
sudo mkswap /dev/vdb2
sudo swapon /dev/vdb2

# Add to fstab for persistence
UUID=<swap-uuid>  swap  swap  defaults  0 0
```


[↑ Back to TOC](#toc)

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Managing storage devices](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/managing_storage_devices/index) | Official storage overview, device naming, partitioning |
| [`lsblk` man page](https://man7.org/linux/man-pages/man8/lsblk.8.html) | Full option reference |
| [`blkid` man page](https://man7.org/linux/man-pages/man8/blkid.8.html) | Block device attribute querying |

---


[↑ Back to TOC](#toc)

## Next step

→ [Filesystems and fstab](03-filesystems-fstab.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
