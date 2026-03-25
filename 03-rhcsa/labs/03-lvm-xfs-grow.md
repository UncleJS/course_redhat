
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

- [Background](#background)
- [Steps](#steps)
  - [1 — Confirm the second disk is present](#1-confirm-the-second-disk-is-present)
  - [2 — Initialise the PV and create VG](#2-initialise-the-pv-and-create-vg)
  - [3 — Create a 4 GB LV](#3-create-a-4-gb-lv)
  - [4 — Format with XFS and mount](#4-format-with-xfs-and-mount)
  - [5 — Write test data](#5-write-test-data)
  - [6 — Add to fstab for persistent mount](#6-add-to-fstab-for-persistent-mount)
  - [7 — Extend the LV and grow the filesystem](#7-extend-the-lv-and-grow-the-filesystem)
  - [8 — Reboot and verify persistence](#8-reboot-and-verify-persistence)
- [Cleanup](#cleanup)
- [Troubleshooting guide](#troubleshooting-guide)
- [Extension tasks](#extension-tasks)


## Prerequisites

- Completed [Storage Overview](../02-storage-overview.md), [Filesystems and fstab](../03-filesystems-fstab.md), and [LVM](../04-lvm.md)
- A second virtual disk attached to your VM (e.g., `/dev/vdb`)
- VM snapshot taken

---


[↑ Back to TOC](#toc)

## Background

Disk space exhaustion is one of the most common and most preventable
production incidents. A full filesystem causes application writes to fail,
logs to stop rotating, and services to crash. The traditional response —
adding a new disk and migrating data — requires downtime. LVM eliminates
this: you can add capacity to a running filesystem in minutes, without
unmounting, without stopping services, and without moving data.

LVM (Logical Volume Manager) inserts a layer of abstraction between physical
storage and filesystems. Physical disks or partitions become **Physical
Volumes (PVs)**. One or more PVs are pooled into a **Volume Group (VG)**.
From the VG's pooled space, you carve out **Logical Volumes (LVs)** — the
actual block devices you format and mount. The power of this model is that
you can add a new PV to an existing VG and immediately use that space to
extend an existing LV, all while the filesystem is mounted and in use.

XFS is the default filesystem on RHEL 10. It supports online growth —
`xfs_growfs` expands a mounted filesystem to fill newly allocated block
device space — but does not support shrinking. This asymmetry is a key
fact for both the RHCSA exam and production planning: size LVM volumes
conservatively and grow on demand rather than attempting to reclaim space
by shrinking.

### The LVM stack

```text
Physical disks:    /dev/vdb         /dev/vdc
                      |                |
Physical Volumes:  pvcreate /dev/vdb   pvcreate /dev/vdc
                      \               /
Volume Group:       vgcreate labvg /dev/vdb /dev/vdc
                              |
Logical Volumes:    lvcreate -L 4G -n lablv labvg
                              |
Filesystem:         mkfs.xfs /dev/labvg/lablv
                              |
Mount:              mount /dev/labvg/lablv /mnt/labdata
```

The three LVM reporting commands map directly to these layers:

| Command | What it shows |
|---|---|
| `pvs` or `pvdisplay` | Physical volumes and which VG they belong to |
| `vgs` or `vgdisplay` | Volume groups: total size, free space, number of PVs/LVs |
| `lvs` or `lvdisplay` | Logical volumes: size, VG, device path, filesystem type |

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

> **Hint:** On KVM/QEMU VMs, the second disk is typically `/dev/vdb`. On
> VMware it may be `/dev/sdb`. On cloud instances it could be `/dev/xvdb`
> or `/dev/nvme1n1`. Always confirm the device name from `lsblk` before
> running any destructive commands.


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

> **Hint:** `pvcreate` writes LVM metadata to the first sector of the disk.
> If the disk already has a filesystem or partition table, `pvcreate` will
> prompt for confirmation (or fail with `--force` not set). If you are
> working on the wrong disk, stop immediately — this is destructive.


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

> **Hint:** `-L 4G` allocates exactly 4 GiB. Use `-l 50%FREE` to allocate
> 50% of available VG space. The LV device path will be
> `/dev/labvg/lablv` (symlink) or equivalently `/dev/mapper/labvg-lablv`.
> Both refer to the same device.


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

> **Hint:** `mkfs.xfs` will fail if the device already has a filesystem.
> Use `sudo wipefs -a /dev/labvg/lablv` to clear any existing signatures
> before re-formatting. This is safe to do on a freshly created LV.


[↑ Back to TOC](#toc)

---

### 5 — Write test data

```bash
sudo bash -c 'for i in {1..5}; do echo "file-$i" > /mnt/labdata/file-$i.txt; done'
ls /mnt/labdata/
```

> **Hint:** This test data serves a critical purpose: after extending the
> filesystem in step 7, you will verify these files still exist. This
> confirms that the grow operation did not corrupt data. Always write test
> data before any storage operation that modifies layout.


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

> **Hint:** Always test `mount -a` immediately after editing `/etc/fstab`.
> A typo in `fstab` can prevent the system from booting. If `mount -a`
> fails, fix the `fstab` entry before rebooting. For extra safety on
> production systems, use the filesystem's UUID instead of device path:
> `sudo blkid /dev/labvg/lablv` to find the UUID, then use
> `UUID=<uuid>  /mnt/labdata  xfs  defaults  0 0`.


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

> **Hint:** `lvextend` alone resizes the block device but not the filesystem.
> You must run `xfs_growfs` (for XFS) or `resize2fs` (for ext4) to expand
> the filesystem into the new space. A common mistake is forgetting the
> second step and then wondering why `df` still shows the old size.
> You can combine both steps with `lvextend -r -L +2G /dev/labvg/lablv`
> (`-r` automatically runs the appropriate resize tool).


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

## Troubleshooting guide

| Symptom | Likely cause | Fix |
|---|---|---|
| `pvcreate` fails with "existing signature" | Disk has a partition table or filesystem | `sudo wipefs -a /dev/vdb` (destructive — confirm right disk first) |
| `mount -a` fails | fstab entry has typo | `sudo mount -a` shows the error; fix the fstab line |
| Filesystem size unchanged after `lvextend` | Forgot `xfs_growfs` | `sudo xfs_growfs /mnt/labdata` |
| Files gone after reboot | fstab entry missing or wrong | Re-add `/dev/labvg/lablv /mnt/labdata xfs defaults 0 0` |
| `lvextend` says "insufficient free space" | VG has no room | `sudo vgs` — check `VFree`; add another PV if needed |
| `lsblk` shows LV but `df` doesn't show mount | Filesystem not mounted | `sudo mount /dev/labvg/lablv /mnt/labdata` |
| `mkfs.xfs` fails with "device busy" | LV already mounted | `sudo umount /mnt/labdata` first |
| System doesn't boot after fstab edit | Bad fstab entry | Boot to rescue mode (`rd.break` on kernel line); fix `/etc/fstab` |

---


[↑ Back to TOC](#toc)

## Why this matters in production

Running out of disk space on a server is one of the most common (and
preventable) issues. LVM lets you extend storage on demand — adding a new
disk to a VG and extending an LV — without downtime and without losing data.
This is a fundamental skill for any RHEL admin.

### LVM quick-reference commands

Keep these commands in mind when diagnosing LVM issues on any system:

```bash
# Display all PVs with detail
sudo pvdisplay
sudo pvs -o +pv_uuid   # include UUID

# Display all VGs
sudo vgdisplay
sudo vgs

# Display all LVs
sudo lvdisplay
sudo lvs -o +lv_path   # include device path

# Show full mapping: PV → VG → LV → mount
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID

# Check filesystem usage
df -hT   # -T shows filesystem type
```

### fstab entry best practices

The `/etc/fstab` entry for an LVM volume can use three different identifiers:

| Identifier | Example | Persistence |
|---|---|---|
| Device path | `/dev/labvg/lablv` | Stable within same VG/LV name |
| Device mapper path | `/dev/mapper/labvg-lablv` | Same as above, different notation |
| UUID | `UUID=<uuid>` | Stable even if VG/LV renamed |

For exam purposes, the device path (`/dev/labvg/lablv`) is the most readable
and is fully acceptable. For production, UUIDs are preferred — they survive VG
renames and disk reorders.

Always test `fstab` entries immediately:

```bash
# Safe test: unmount and remount via fstab
sudo umount /mnt/labdata
sudo mount -a
# If this fails, fix fstab BEFORE rebooting
```

If you accidentally introduce a bad `fstab` entry and reboot, the system will
enter emergency mode. Recovery:

1. Boot to emergency mode (enter root password at prompt)
2. Remount root filesystem read-write: `mount -o remount,rw /`
3. Edit `/etc/fstab` to fix the bad entry
4. Reboot

### Common exam mistakes on LVM tasks

| Mistake | Consequence | Prevention |
|---|---|---|
| Running `lvextend` but not `xfs_growfs` | Block device resized but filesystem unchanged; `df` still shows old size | Always run `xfs_growfs` (or use `lvextend -r`) after `lvextend` |
| Forgetting to update `/etc/fstab` | Filesystem not mounted after reboot | Always test `mount -a` after adding fstab entry |
| Using wrong device name in `pvcreate` | Destroys data on wrong disk | Confirm device with `lsblk` before any destructive command |
| Using `resize2fs` on XFS | Command fails (`resize2fs` is for ext4 only) | XFS: use `xfs_growfs`; ext4: use `resize2fs`; confirm type with `df -T` |
| Specifying LV path wrong in `lvextend` | "device not found" error | Use either `/dev/labvg/lablv` or `/dev/mapper/labvg-lablv` |
| Not running `systemctl daemon-reload` after fstab change | No immediate effect (but matters for systemd-managed mounts) | Run `daemon-reload` if using systemd mount units |

### Capacity planning with LVM

LVM is most powerful when used with headroom in mind. A practical production
pattern is to provision LVs at 60–70% of expected need, leaving VG free space
for emergency extension. Monitor with:

```bash
# Check VG free space
sudo vgs --units g -o vg_name,vg_size,vg_free

# Alert threshold: when VFree < 10% of VSize
# Automate with a cron/timer job that emails when VFree drops below threshold
```

Thin provisioning is an advanced LVM feature that allows overcommitting storage:
LVs appear larger than the actual physical space allocated. Thin pools allocate
physical blocks on write, not at LV creation. This is useful in test/dev
environments but requires careful monitoring in production to prevent the thin
pool from filling up.

### XFS vs ext4 on RHEL 10

RHEL 10 defaults to XFS. Understand the key differences:

| Feature | XFS | ext4 |
|---|---|---|
| Online grow | Yes (`xfs_growfs`) | Yes (`resize2fs`) |
| Online shrink | No | Yes (`resize2fs`) |
| Max filesystem size | 1 EiB | 1 EiB |
| Best for | Large files, high throughput | General purpose |
| Repair tool | `xfs_repair` | `e2fsck` |
| Default on RHEL 10 | Yes | No |

For the exam: XFS is always the right choice unless the question specifies ext4.
The repair command for XFS is `xfs_repair` (not `fsck.xfs`). Always unmount
before running `xfs_repair`.

### Full verification checklist after LVM grow

Use this sequence to confirm the entire LVM stack is correct after completing the lab:

```bash
# 1. Physical volume visible and assigned to VG
sudo pvs
# Expected: /dev/vdb labvg <size>

# 2. Volume group has expected size and free space
sudo vgs
# Expected: labvg <total-size> <free-space>

# 3. Logical volume at expected size
sudo lvs
# Expected: lablv labvg <size>

# 4. Filesystem at expected size (after xfs_growfs)
df -hT /mnt/labdata
# Expected: ~6G (or extended size), type xfs

# 5. Data integrity: test files present
ls /mnt/labdata/
# Expected: file-1.txt through file-5.txt

# 6. fstab entry present and correct
grep labdata /etc/fstab
# Expected: /dev/labvg/lablv /mnt/labdata xfs defaults 0 0

# 7. fstab entry works (umount and remount)
sudo umount /mnt/labdata && sudo mount -a && df -h /mnt/labdata
# Expected: filesystem remounts without error

# 8. Persistence: boot check
# (After reboot) df -h /mnt/labdata should show mounted XFS filesystem
```

---


[↑ Back to TOC](#toc)

## Extension tasks

**Extension 1 — Extend using a second physical disk**

Simulate adding storage capacity by adding a second virtual disk (`/dev/vdc`)
to your VM. Add it as a new PV to `labvg`, then use that space to extend
`lablv` by another 3 GB. This exercises the multi-disk VG scenario common
in production.

```bash
sudo pvcreate /dev/vdc
sudo vgextend labvg /dev/vdc
sudo pvs   # verify new PV in labvg
sudo lvextend -L +3G /dev/labvg/lablv
sudo xfs_growfs /mnt/labdata
df -h /mnt/labdata   # should now show ~9 GB
```

**Extension 2 — Snapshot and rollback**

Create an LVM snapshot of `lablv`, make a destructive change to the data,
then restore from the snapshot. This demonstrates LVM's snapshot capability —
widely used for consistent backups and safe upgrades.

```bash
# Create snapshot (1 GB COW space)
sudo lvcreate -L 1G -s -n lablv_snap /dev/labvg/lablv

# Delete some test files
sudo rm /mnt/labdata/file-*.txt
ls /mnt/labdata/   # files gone

# Restore: unmount, merge snapshot, reboot
sudo umount /mnt/labdata
sudo lvconvert --merge /dev/labvg/lablv_snap
sudo mount /mnt/labdata   # after lvconvert triggers restore on next activation
ls /mnt/labdata/   # files restored
```

**Extension 3 — Use UUID in fstab instead of device path**

Device paths can change if disks are added in a different order. UUIDs are
stable. Update your `fstab` entry to use the filesystem UUID.

```bash
sudo blkid /dev/labvg/lablv
# Note the UUID value

sudo vim /etc/fstab
# Replace: /dev/labvg/lablv  /mnt/labdata  xfs  defaults  0 0
# With:    UUID=<your-uuid>  /mnt/labdata  xfs  defaults  0 0

sudo umount /mnt/labdata
sudo mount -a
df -h /mnt/labdata   # verify it still mounts correctly
```

---


[↑ Back to TOC](#toc)

## Next step

→ [Lab — Fix a SELinux Label Issue](04-selinux-label-fix.md)

[↑ Back to TOC](#toc)

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
