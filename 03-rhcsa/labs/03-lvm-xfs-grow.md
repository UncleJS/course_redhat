
[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)


[↑ Back to TOC](#toc)

# Lab: LVM + XFS Grow
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![RHEL](https://img.shields.io/badge/RHEL-10-red)](https://www.redhat.com)

**Track:** RHCSA
**Estimated time:** 35 minutes
**Topology:** Single VM (requires an extra unpartitioned disk — add a 10 GB virtual disk to your VM)

---
<a name="toc"></a>

## Table of contents

- [Steps](#steps)
  - [1 — Confirm the second disk is present](#1-confirm-the-second-disk-is-present)
  - [2 — Initialise the PV and create VG](#2-initialise-the-pv-and-create-vg)
  - [3 — Create a 4 GB LV](#3-create-a-4-gb-lv)
  - [4 — Format with XFS and mount](#4-format-with-xfs-and-mount)
  - [5 — Write test data](#5-write-test-data)
  - [6 — Add to fstab for persistent mount](#6-add-to-fstab-for-persistent-mount)
  - [7 — Extend the LV and grow the filesystem](#7-extend-the-lv-and-grow-the-filesystem)
  - [8 — Reboot and verify persistence](#8-reboot-and-verify-persistence)


## Prerequisites

- Completed [Storage Overview](../02-storage-overview.md), [Filesystems and fstab](../03-filesystems-fstab.md), and [LVM](../04-lvm.md)
- A second virtual disk attached to your VM (e.g., `/dev/vdb`)
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Success criteria

- An LVM volume group `labvg` created on `/dev/vdb`
- A logical volume `lablv` formatted with XFS, mounted at `/mnt/labdata`
- Data written, filesystem extended, data verified intact
- Mount persists across reboot

---


[↑ Back to TOC](#toc)

## Steps

### 1 — Confirm the second disk is present

```bash
lsblk
```

Look for: a disk without partitions (e.g., `vdb 10G`). If you don't see it,
add a virtual disk to your VM and reboot.


[↑ Back to TOC](#toc)

---

### 2 — Initialise the PV and create VG

```bash
sudo pvcreate /dev/vdb
sudo vgcreate labvg /dev/vdb
```

> **✅ Verify**
> ```bash
> sudo vgs
> ```
> Look for: `labvg` with ~10 GB free.
>


[↑ Back to TOC](#toc)

---

### 3 — Create a 4 GB LV

```bash
sudo lvcreate -L 4G -n lablv labvg
```

> **✅ Verify**
> ```bash
> sudo lvs
> ```
> Look for: `lablv` in `labvg` with size `4.00g`.
>


[↑ Back to TOC](#toc)

---

### 4 — Format with XFS and mount

```bash
sudo mkfs.xfs /dev/labvg/lablv
sudo mkdir -p /mnt/labdata
sudo mount /dev/labvg/lablv /mnt/labdata
```

> **✅ Verify**
> ```bash
> df -h /mnt/labdata
> ```
> Look for: ~4 GB filesystem mounted on `/mnt/labdata`.
>


[↑ Back to TOC](#toc)

---

### 5 — Write test data

```bash
sudo bash -c 'for i in {1..5}; do echo "file-$i" > /mnt/labdata/file-$i.txt; done'
ls /mnt/labdata/
```


[↑ Back to TOC](#toc)

---

### 6 — Add to fstab for persistent mount

```bash
echo "/dev/labvg/lablv  /mnt/labdata  xfs  defaults  0 0" | sudo tee -a /etc/fstab
```

Test:

```bash
sudo umount /mnt/labdata
sudo mount -a
```

> **✅ Verify**
> ```bash
> df -h /mnt/labdata
> ls /mnt/labdata/
> ```
> Filesystem remounted and files still present.
>


[↑ Back to TOC](#toc)

---

### 7 — Extend the LV and grow the filesystem

```bash
# Extend LV by 2 GB
sudo lvextend -L +2G /dev/labvg/lablv

# Grow filesystem online (no unmount needed for XFS)
sudo xfs_growfs /mnt/labdata
```

> **✅ Verify**
> ```bash
> df -h /mnt/labdata
> ```
> Look for: filesystem now ~6 GB.
>

```bash
ls /mnt/labdata/
```

All 5 test files still present.


[↑ Back to TOC](#toc)

---

### 8 — Reboot and verify persistence

```bash
sudo reboot
```

After login:

```bash
df -h /mnt/labdata
ls /mnt/labdata/
```

Both should show the mounted filesystem and test files.


[↑ Back to TOC](#toc)

---

## Cleanup

```bash
# Remove fstab entry first
sudo vim /etc/fstab   # delete the /mnt/labdata line
sudo umount /mnt/labdata
sudo lvremove /dev/labvg/lablv
sudo vgremove labvg
sudo pvremove /dev/vdb
sudo rmdir /mnt/labdata
```

---


[↑ Back to TOC](#toc)

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `pvcreate` fails | Disk already has partition table | `sudo wipefs -a /dev/vdb` (destructive — confirm right disk) |
| `mount -a` fails | fstab entry has typo | `sudo mount -a` shows the error; fix fstab |
| Filesystem size unchanged after `lvextend` | Forgot `xfs_growfs` | Run `sudo xfs_growfs /mnt/labdata` |
| Files gone after reboot | fstab entry missing | Re-add `/dev/labvg/lablv /mnt/labdata xfs defaults 0 0` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Running out of disk space on a server is one of the most common (and
preventable) issues. LVM lets you extend storage on demand — adding a new
disk to a VG and extending an LV — without downtime and without losing data.
This is a fundamental skill for any RHEL admin.

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — Fix a SELinux Label Issue](04-selinux-label-fix.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
