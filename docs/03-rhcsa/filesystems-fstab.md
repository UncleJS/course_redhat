# Filesystems and fstab

This chapter covers XFS filesystem management and persistent mounts via
`/etc/fstab` — the foundation of storage configuration on RHEL.

---

## XFS — RHEL's default filesystem

XFS is a high-performance 64-bit journaling filesystem. It is the default
on RHEL and the best choice for most workloads.

| Feature | Value |
|---|---|
| Max filesystem size | 8 EiB |
| Max file size | 8 EiB |
| Journal | Metadata only (fast recovery) |
| Growing | Supported online (no unmount needed) |
| Shrinking | **Not supported** — size wisely |

!!! warning "XFS cannot be shrunk"
    Plan your XFS partition sizes with room to grow. Once created, an XFS
    filesystem can only be extended, not reduced.

---

## Create and mount XFS

```bash
# Partition (if starting from a raw disk)
sudo parted /dev/vdb mklabel gpt
sudo parted /dev/vdb mkpart primary xfs 1MiB 100%
sudo partprobe /dev/vdb    # inform kernel of new partition table

# Format
sudo mkfs.xfs /dev/vdb1

# Mount point
sudo mkdir -p /mnt/data

# Temporary mount (lost on reboot)
sudo mount /dev/vdb1 /mnt/data

# Verify
df -h /mnt/data
```

---

## `/etc/fstab` — persistent mounts

`/etc/fstab` defines what gets mounted at boot.

### Format

```
<device>  <mountpoint>  <fstype>  <options>  <dump>  <pass>
```

| Field | Value | Notes |
|---|---|---|
| device | `UUID=...` | Prefer UUID over device name |
| mountpoint | `/mnt/data` | Must exist before mounting |
| fstype | `xfs` | Filesystem type |
| options | `defaults` | Common mount options |
| dump | `0` | `0` = do not back up with dump |
| pass | `0` | `0` = no fsck at boot (XFS handles its own recovery) |

### Add an entry

```bash
# Get the UUID
sudo blkid /dev/vdb1
```

```bash
sudo vim /etc/fstab
```

```
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  /mnt/data  xfs  defaults  0 0
```

### Test immediately (do not wait for reboot)

```bash
sudo mount -a
```

!!! success "Verify"
    ```bash
    df -h /mnt/data
    ```
    Look for: `/mnt/data` with the expected size

---

## Common mount options

| Option | Meaning |
|---|---|
| `defaults` | rw, suid, exec, auto, nouser, async |
| `noexec` | Prevent executing binaries from this mount |
| `nosuid` | Ignore SUID/SGID bits |
| `noatime` | Don't update access time (performance gain) |
| `ro` | Read-only |
| `_netdev` | Wait for network before mounting (NFS, iSCSI) |

---

## Growing an XFS filesystem

XFS supports online growth (filesystem stays mounted):

```bash
# First, grow the underlying partition or LV (see LVM chapter)
# Then grow the filesystem to fill the new space:
sudo xfs_growfs /mnt/data
```

---

## XFS tools

```bash
# View filesystem info
sudo xfs_info /mnt/data

# Repair (must be unmounted)
sudo xfs_repair /dev/vdb1

# Dump/restore (for backup)
sudo xfsdump -l 0 -f /backup/data.dump /mnt/data
sudo xfsrestore -f /backup/data.dump /mnt/restore
```

---

## Diagnosing full filesystems

```bash
# Check disk usage
df -h

# Find large files
sudo du -sh /var/* | sort -rh | head -20

# Find files consuming inodes
df -ih
```

---

## Next step

→ [LVM](lvm.md)
