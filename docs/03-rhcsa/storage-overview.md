# Storage Overview — lsblk, blkid, mounts

Before managing storage, you need to understand what devices exist, how they
are partitioned, and what is currently mounted.

---

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

!!! danger "Always test fstab before rebooting"
    A bad fstab entry can prevent the system from booting. Always run
    `sudo mount -a` after editing fstab to catch errors immediately.

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

---

## Next step

→ [Filesystems and fstab](filesystems-fstab.md)
