# LVM — Create, Extend, Reduce Safely

**Logical Volume Management (LVM)** adds a flexible abstraction layer between
physical storage and filesystems. It lets you resize, snapshot, and reorganise
storage without downtime.

---

## LVM concepts

```
Physical disk(s)
    └── Physical Volume (PV)   [pvcreate]
          └── Volume Group (VG) [vgcreate]
                ├── Logical Volume (LV) [lvcreate]
                └── Logical Volume (LV)
                      └── Filesystem (mkfs.xfs)
                            └── Mount point
```

| Term | Description |
|---|---|
| **PV** (Physical Volume) | A disk or partition initialised for LVM |
| **VG** (Volume Group) | A pool of storage from one or more PVs |
| **LV** (Logical Volume) | A slice of a VG; behaves like a partition |
| **PE** (Physical Extent) | Smallest allocation unit (default 4 MiB) |

---

## Create an LVM setup from scratch

Assumes a raw extra disk `/dev/vdb` (adjust to your device).

### 1 — Initialise the PV

```bash
sudo pvcreate /dev/vdb
```

> **✅ Verify**
> ```bash
> sudo pvs
> ```
> Look for `/dev/vdb` in the output.
>

### 2 — Create a VG

```bash
sudo vgcreate datavg /dev/vdb
```

> **✅ Verify**
> ```bash
> sudo vgs
> ```
> Look for: `datavg` with free space shown.
>

### 3 — Create an LV

```bash
# Create a 5 GB logical volume named 'datalv'
sudo lvcreate -L 5G -n datalv datavg

# Or use 100% of free space
sudo lvcreate -l 100%FREE -n datalv datavg
```

> **✅ Verify**
> ```bash
> sudo lvs
> ```
> Look for: `datalv` in `datavg` with size `5.00g`.
>

### 4 — Format and mount

```bash
sudo mkfs.xfs /dev/datavg/datalv
sudo mkdir -p /mnt/data
sudo mount /dev/datavg/datalv /mnt/data
```

### 5 — Add to fstab

```bash
sudo blkid /dev/datavg/datalv
```

Add to `/etc/fstab`:

```
/dev/datavg/datalv  /mnt/data  xfs  defaults  0 0
```

(LVM device paths are stable — using the `/dev/VG/LV` path is fine for LVM.)

---

## Extend an LV (online, no downtime)

```bash
# Extend LV by 2 GB
sudo lvextend -L +2G /dev/datavg/datalv

# Grow XFS filesystem to fill (online)
sudo xfs_growfs /mnt/data
```

Or extend and grow in one command:

```bash
sudo lvextend -L +2G -r /dev/datavg/datalv
```

(`-r` = resize filesystem automatically after extending)

---

## Reduce an LV (ext4 only — not XFS)

> **⚠️ XFS cannot be shrunk**
> Reduction only works with ext4. For XFS, create a new LV at the right size.
>

```bash
# ext4 only — unmount first
sudo umount /mnt/data
sudo e2fsck -f /dev/datavg/datalv
sudo resize2fs /dev/datavg/datalv 4G
sudo lvreduce -L 4G /dev/datavg/datalv
sudo mount /dev/datavg/datalv /mnt/data
```

---

## Add a new PV to an existing VG

When a VG runs low on space:

```bash
sudo pvcreate /dev/vdc
sudo vgextend datavg /dev/vdc
sudo vgs   # confirm new free space
```

---

## LVM snapshot (basics)

```bash
# Create a read-only snapshot of datalv (2G COW space)
sudo lvcreate -L 2G -s -n datalv-snap /dev/datavg/datalv

# Mount the snapshot read-only
sudo mount -o ro /dev/datavg/datalv-snap /mnt/snap

# Remove when done
sudo umount /mnt/snap
sudo lvremove /dev/datavg/datalv-snap
```

---

## LVM status commands

```bash
sudo pvs          # physical volumes (brief)
sudo pvdisplay    # physical volumes (detailed)

sudo vgs          # volume groups (brief)
sudo vgdisplay    # volume groups (detailed)

sudo lvs          # logical volumes (brief)
sudo lvdisplay    # logical volumes (detailed)
```

---

## Further reading

| Resource | Notes |
|---|---|
| [RHEL 10 — Configuring and managing logical volumes](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/10/html/configuring_and_managing_logical_volumes/index) | Official LVM guide including thin provisioning and snapshots |
| [LVM2 resource page](https://sourceware.org/lvm2/) | Upstream LVM2 project and man pages |
| [`lvmconfig` man page](https://man7.org/linux/man-pages/man8/lvmconfig.8.html) | LVM configuration file reference |

---

## Next step

→ [systemd Essentials](systemd-basics.md)
